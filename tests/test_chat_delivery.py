import json
from pathlib import Path
import queue
import sys
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import ChatClient, PetWindow
import pet_runtime
import sts2_bridge


class Response:
    def __init__(self, lines):
        self.lines = lines

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        return iter(self.lines)


class ChatDeliveryTests(unittest.TestCase):
    def test_cancelled_chunk_callback_does_not_get_swallowed(self):
        line = b'data: {"choices":[{"delta":{"content":"hello"}}]}\n'

        def chunk(_):
            raise pet_runtime.TurnCancelled()

        with patch('main.urllib.request.urlopen', return_value=Response([line])):
            with self.assertRaises(pet_runtime.TurnCancelled):
                ChatClient({}).chat_stream([], 'hi', on_chunk=chunk)

    def test_chat_settings_apply_to_stream_request(self):
        client = ChatClient({'context_budget': 1000, 'max_reply_tokens': 700})
        with patch('main.urllib.request.urlopen', return_value=Response([])) as request:
            client.chat_stream([], 'hi')
        body = json.loads(request.call_args.args[0].data)
        self.assertEqual(body['max_tokens'], 700)
        self.assertEqual(body['messages'][-1]['content'], 'hi')

    def test_strategy_summary_request_does_not_offer_game_tools(self):
        response = Response([])
        response.read = lambda: json.dumps({'choices': [{'message': {
            'content': '这回合优先防守，把剩余费用用于进攻。'}}]}).encode('utf-8')
        with patch('main.urllib.request.urlopen', return_value=response) as request:
            result = ChatClient({}).complete([{'role': 'user', 'content': '总结回合策略'}], tools=None)
        body = json.loads(request.call_args.args[0].data)
        self.assertNotIn('tools', body)
        self.assertNotIn('tool_choice', body)
        self.assertIn('优先防守', result['content'])

    def window(self, client):
        window = SimpleNamespace(
            chat_client=client, _speech_generation=3,
            voice_tts_done=threading.Event(),
            voice_chat_cfg={'tts_enabled': True},
            _tts_client=SimpleNamespace(ready=lambda: True),
            _tts_queue=queue.Queue(), _soullink_usable=lambda: False,
            _tts_text=lambda text: text)
        return window

    def test_fallback_reply_queues_both_complete_sentence_and_tail(self):
        def unavailable(*args, **kwargs):
            raise OSError('stream unavailable')

        reply = 'This is a sufficiently long sentence. Remaining tail'
        window = self.window(SimpleNamespace(chat_stream=unavailable, chat=lambda *a, **k: reply))
        result, spoken = PetWindow._stream_chat(window, [], 'hi', None, 'hi')
        self.assertTrue(spoken)
        self.assertEqual(result, reply)
        queued = list(window._tts_queue.queue)
        self.assertEqual(''.join(item[1] for item in queued).replace(' ', ''), reply.replace(' ', ''))
        self.assertTrue(all(item[0] == 3 for item in queued))

    def test_stale_tts_generation_never_synthesizes(self):
        window = self.window(SimpleNamespace())
        window._tts_client.synthesize = lambda text: self.fail('stale speech synthesized')
        PetWindow._speak_voice(window, 'old speech', generation=2)

    def test_voice_turn_is_saved_before_interrupted_playback(self):
        recorded, microphones = [], []

        def interrupted(_):
            raise pet_runtime.TurnCancelled()

        window = SimpleNamespace(
            mc_cfg={'enabled': False}, _is_screen_look_request=lambda text: False,
            _mc_context_note=lambda: None,
            _sts2_context_note=lambda: None,
            memory=SimpleNamespace(dialogue_context=lambda text: ([], None),
                                   record_turn=lambda *a, **k: recorded.append((a, k))),
            voice_recognizer=SimpleNamespace(set_microphone=microphones.append),
            voice_tts_done=threading.Event(), chat_client=SimpleNamespace(),
            _stream_chat=lambda *args: ('reply', True), _wait_for_speech=interrupted)
        with patch('main._voice_chat_diag'):
            with self.assertRaises(pet_runtime.TurnCancelled):
                PetWindow._voice_turn_worker(window, 'hello')
        self.assertEqual(recorded[0][0], ('hello', 'reply'))
        self.assertEqual(recorded[0][1]['source'], 'voice')
        self.assertEqual(microphones, [False, True])


class SpeechCompletionTests(unittest.TestCase):
    def window(self):
        window = SimpleNamespace(
            _speech_generation=3, voice_tts_done=threading.Event(),
            diagnostics=Mock(), soullink_js=Mock(),
            voice_chat_cfg={'tts_enabled': True}, _tts_client=Mock(),
            soullink_runner=Mock(), soullink_event=Mock(),
            chat_reply=Mock(), _tts_text=lambda text: text,
            _speak_voice=Mock(), _soullink_usable=lambda: True)
        window.soullink_runner.classify.return_value = {'emotion': 'neutral'}
        window._wait_for_speech = lambda sent: PetWindow._wait_for_speech(window, sent)
        return window

    def test_browser_failure_is_not_speech_completion(self):
        window = self.window()
        window.soullink_js.emit.side_effect = lambda _: PetWindow._on_tts_result(window, 3, 'TTS HTTP 500')
        with self.assertRaises(RuntimeError):
            window._wait_for_speech(True)
        window.diagnostics.event.assert_called()

    def test_stale_browser_completion_cannot_release_current_speech(self):
        window = self.window()
        PetWindow._on_tts_result(window, 2, '')
        self.assertFalse(window.voice_tts_done.is_set())
        PetWindow._on_tts_result(window, 3, '')
        self.assertTrue(window.voice_tts_done.is_set())

    def test_browser_failure_falls_back_to_standalone_speech(self):
        window = self.window()
        window._wait_for_speech = Mock(side_effect=RuntimeError('TTS failed'))
        PetWindow._emit_speech(window, '旁白', require_audio=True)
        window._speak_voice.assert_called_once_with('旁白', 3)
        window.chat_reply.emit.assert_not_called()

    def test_all_speech_paths_failing_blocks_game_action(self):
        window = self.window()
        window._wait_for_speech = Mock(side_effect=RuntimeError('TTS failed'))
        window._speak_voice.side_effect = RuntimeError('Audio failed')
        with self.assertRaises(sts2_bridge.Sts2Error):
            PetWindow._emit_speech(window, '旁白', require_audio=True)
        window.chat_reply.emit.assert_not_called()

    def test_speech_failure_can_still_show_text_for_normal_chat(self):
        window = self.window()
        window._wait_for_speech = Mock(side_effect=RuntimeError('TTS failed'))
        window._speak_voice.side_effect = RuntimeError('Audio failed')
        PetWindow._emit_speech(window, '旁白')
        window.chat_reply.emit.assert_called_once_with('旁白')

    def test_emotion_classifier_failure_does_not_disable_speech(self):
        window = self.window()
        window.soullink_runner.classify.side_effect = RuntimeError('Classifier unavailable')
        window._wait_for_speech = Mock()
        PetWindow._emit_speech(window, '旁白', require_audio=True)
        payload = json.loads(window.soullink_event.emit.call_args.args[0])
        self.assertIsNone(payload['intent'])
        self.assertEqual(payload['speak_text'], '旁白')
        window._wait_for_speech.assert_called_once_with(True)


if __name__ == '__main__':
    unittest.main()
