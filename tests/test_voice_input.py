import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import LocalVoiceRecognizer, PetWindow


class Recorder:
    def __init__(self, audio):
        self.audio = np.asarray(audio, dtype=np.float32)
        self.is_recording = True
        self.calls = []

    def stop(self):
        self.calls.append('stop')
        self.is_recording = False

    def wait_audio(self):
        self.calls.append('wait_audio')

    def transcribe(self):
        self.calls.append('transcribe')
        return ' recognized text '

    def set_microphone(self, enabled):
        self.calls.append(('microphone', enabled))

    def abort(self):
        raise AssertionError('abort waits forever without a text() caller')

    def text(self):
        raise AssertionError('text() would wait for another recording')


class Signal:
    def __init__(self):
        self.values = []
        self.done = threading.Event()

    def emit(self, value):
        self.values.append(value)
        if 'setVoiceBusy(false' in value:
            self.done.set()


class VoiceInputTests(unittest.TestCase):
    def recognizer(self, audio):
        recognizer = LocalVoiceRecognizer({})
        recognizer._recorder = Recorder(audio)
        recognizer._recording = True
        return recognizer

    def test_cancel_manual_recording_without_waiting_for_text(self):
        recognizer = self.recognizer([0.1])
        recognizer.abort()
        self.assertFalse(recognizer._recording)
        self.assertEqual(recognizer._recorder.calls,
                         ['stop', 'wait_audio', ('microphone', False)])
        recognizer.abort()
        self.assertEqual(recognizer._recorder.calls.count('stop'), 1)

    def test_empty_recording_returns_instead_of_rearming_vad(self):
        recognizer = self.recognizer([])
        self.assertEqual(recognizer.stop_and_transcribe(), '')
        self.assertTrue(recognizer.error())
        self.assertEqual(recognizer._recorder.calls, ['stop', 'wait_audio'])

    def test_transcribes_only_the_finished_recording(self):
        recognizer = self.recognizer([0.1])
        recognizer._error = 'previous error'
        self.assertEqual(recognizer.stop_and_transcribe(), 'recognized text')
        self.assertEqual(recognizer.error(), '')
        self.assertEqual(recognizer._recorder.calls,
                         ['stop', 'wait_audio', 'transcribe'])

    def window(self, recognizer):
        return SimpleNamespace(
            voice_busy=False, voice_recording=False, voice_pending_abort=False,
            voice_token=0, voice_recognizer=recognizer, _ptt_down=False,
            voice_ui=Signal(), voice_status=Signal(),
            voice_text=Signal(), voice_send=Signal(),
            _run_js=lambda text: None, _notify=lambda text: None)

    def test_start_exception_restores_button_for_retry(self):
        def fail():
            raise RuntimeError('device unavailable')

        window = self.window(SimpleNamespace(needs_model=fail))
        PetWindow._voice_start(window)
        self.assertTrue(window.voice_ui.done.wait(2))
        self.assertFalse(window.voice_busy)
        self.assertFalse(window.voice_recording)
        self.assertIn('device unavailable', window.voice_status.values[0])

    def test_release_during_initialization_cancels_and_restores_button(self):
        entered = threading.Event()
        release = threading.Event()
        aborted = threading.Event()

        def start():
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test initialization timed out')
            return True

        window = self.window(SimpleNamespace(
            needs_model=lambda: False, start=start, abort=aborted.set))
        PetWindow._voice_start(window)
        self.assertTrue(entered.wait(2))
        window.voice_pending_abort = True
        release.set()
        self.assertTrue(window.voice_ui.done.wait(2))
        self.assertTrue(aborted.is_set())
        self.assertFalse(window.voice_busy)
        self.assertFalse(window.voice_recording)

    def test_transcription_exception_restores_button(self):
        def fail():
            raise RuntimeError('transcription failed')

        window = self.window(SimpleNamespace(stop_and_transcribe=fail))
        window.voice_recording = True
        PetWindow._voice_stop_and_send(window)
        self.assertTrue(window.voice_ui.done.wait(2))
        self.assertFalse(window.voice_busy)
        self.assertFalse(window.voice_recording)
        self.assertEqual(window.voice_send.values, [])
        self.assertIn('transcription failed', window.voice_status.values[0])


if __name__ == '__main__':
    unittest.main()
