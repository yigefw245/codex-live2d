from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import sys
import ssl
import threading
import urllib.error
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sts2_bridge as sts
import pet_runtime
from main import PetWindow


def combat():
    return {'state_type': 'monster', 'battle': {'is_play_phase': True, 'turn': 'player', 'round': 1,
            'enemies': [{'entity_id': 'ENEMY_0', 'hp': 30, 'block': 0}]},
            'player': {'hp': 60, 'max_hp': 80, 'gold': 99,
                       'hand': [{'index': 0, 'name': 'Strike', 'can_play': True,
                                 'target_type': 'Self'}]},
            'run': {'act': 1, 'floor': 2}}


def decision(name='combat_play_card', args=None):
    return {'content': 'Prefer attacking.', 'tool_calls': [{'function': {
        'name': name, 'arguments': json.dumps(args if args is not None else
        {'card_index': 0, 'target': 'ENEMY_0'})}}]}


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.server.reads.append(self.path)
                self.reply(self.server.state, self.server.get_status)

            def do_POST(self):
                self.server.posts.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                self.reply(self.server.outcome, self.server.post_status)

            def reply(self, body, code=200):
                raw = json.dumps(body).encode('utf-8')
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def setUp(self):
        self.server.state, self.server.get_status = combat(), 200
        self.server.posts, self.server.reads = [], []
        self.server.outcome = {'status': 'ok', 'message': 'Played card'}
        self.server.post_status = 200
        self.client = sts.Sts2Client(self.server.server_port)
        self.stop = threading.Event()

    def test_real_http_routes_and_card_target(self):
        state = self.client.state()
        self.client.act('combat_play_card', {'card_index': 0, 'target': 'ENEMY_0'}, state, self.stop)
        self.assertEqual(self.server.posts, [('/api/v1/singleplayer',
            {'action': 'play_card', 'card_index': 0, 'target': 'ENEMY_0'})])
        self.assertEqual(self.server.reads, ['/api/v1/singleplayer?format=json'] * 2)

    def test_parameter_aliases_match_http_contract(self):
        cases = [('rewards', 'rewards_claim', 'reward_index', 'claim_reward'),
                 ('map', 'map_choose_node', 'node_index', 'choose_map_node'),
                 ('event', 'event_choose_option', 'option_index', 'choose_event_option'),
                 ('card_select', 'deck_select_card', 'card_index', 'select_card'),
                 ('shop', 'shop_purchase', 'item_index', 'shop_purchase')]
        for screen, name, param, action in cases:
            with self.subTest(name=name):
                self.server.state = {'state_type': screen}
                self.client.act(name, {param: 2}, self.server.state, self.stop)
                self.assertEqual(self.server.posts[-1][1], {'action': action, 'index': 2})

    def test_changed_state_never_posts_old_indices(self):
        expected = combat()
        self.server.state['player']['hand'] = []
        with self.assertRaises(sts.StaleState):
            self.client.act('combat_play_card', {'card_index': 0}, expected, self.stop)
        self.assertEqual(self.server.posts, [])

    def test_state_changed_during_speech_never_posts(self):
        brain = sts.Sts2Brain(self.client, Mock(return_value=decision()), sts.DEFAULTS)
        spoken = []

        def speak(text, stop):
            spoken.append(text)
            self.assertEqual(self.server.posts, [])
            self.server.state = combat()
            self.server.state['player']['hand'] = []

        result = brain.step(self.stop, before_action=speak)
        self.assertEqual(result.status, 'waiting')
        self.assertEqual(len(spoken), 1)
        self.assertEqual(self.server.posts, [])

    def test_skipped_reward_cleanup_uses_real_http_contract_without_reopening(self):
        rewards = {'state_type': 'rewards', 'run': {'act': 1, 'floor': 2},
                   'rewards': {'items': [{'index': 0, 'type': 'card'}], 'can_proceed': True}}
        self.server.state = rewards
        llm = Mock(return_value=decision('rewards_claim', {'reward_index': 0}))
        brain = sts.Sts2Brain(self.client, llm, sts.DEFAULTS)
        self.assertEqual(brain.step(self.stop).action, 'rewards_claim')
        self.server.state = {'state_type': 'card_reward', 'run': {'act': 1, 'floor': 2},
                             'card_reward': {'can_skip': True, 'cards': []}}
        llm.return_value = decision('rewards_skip_card', {})
        self.assertEqual(brain.step(self.stop).action, 'rewards_skip_card')
        self.server.state = rewards
        llm.reset_mock()
        self.assertEqual(brain.step(self.stop).action, 'proceed_to_map')
        llm.assert_not_called()
        self.assertEqual([body['action'] for _, body in self.server.posts],
                         ['claim_reward', 'skip_card_reward', 'proceed'])

    def test_cleanup_does_not_proceed_when_state_changes_during_final_recheck(self):
        rewards = {'state_type': 'rewards', 'run': {'act': 1, 'floor': 2},
                   'rewards': {'items': [{'index': 0, 'type': 'card'}], 'can_proceed': True}}
        llm = Mock(return_value=decision('rewards_skip_card', {}))
        brain = sts.Sts2Brain(self.client, llm, sts.DEFAULTS)
        self.server.state = {'state_type': 'card_reward', 'run': {'act': 1, 'floor': 2},
                             'card_reward': {'can_skip': True}}
        brain.step(self.stop)
        self.server.posts.clear()
        self.server.state = rewards
        original_state = self.client.state
        def changed_after_read():
            snapshot = original_state()
            self.server.state = dict(rewards, player={'hp': 10})
            return snapshot
        self.client.state = changed_after_read
        self.assertEqual(brain.step(self.stop).status, 'waiting')
        self.assertEqual(self.server.posts, [])

    def test_pause_prevents_mutation(self):
        self.stop.set()
        with self.assertRaises(sts.Sts2Cancelled):
            self.client.act('combat_end_turn', {}, combat(), self.stop)
        self.assertEqual(self.server.posts, [])

    def test_multiplayer_conflict_is_not_bypassed(self):
        self.server.get_status = 409
        with self.assertRaises(sts.Sts2Error):
            self.client.state()
        self.assertEqual(self.server.posts, [])

    def test_game_errors_are_not_retried(self):
        self.server.outcome = {'status': 'error', 'message': 'not enough energy'}
        with self.assertRaises(sts.Sts2GameError) as raised:
            self.client.act('combat_play_card', {'card_index': 0}, combat(), self.stop)
        self.assertIn('energy', raised.exception.diagnostic_data['server_error'])
        self.assertNotIn('energy', str(raised.exception))
        self.assertEqual(len(self.server.posts), 1)

    def test_missing_combat_api_explains_version_mismatch(self):
        self.server.get_status = 500
        self.server.state = {
            'error': "Method not found: 'CombatManager.get_IsPlayPhase()'.",
            'exception_type': 'System.MissingMethodException',
            'stack_trace': 'at STS2_MCP.McpMod.BuildBattleState',
        }
        with self.assertRaisesRegex(sts.Sts2HttpError, '版本不兼容') as raised:
            self.client.state()
        data = raised.exception.diagnostic_data
        self.assertEqual(data['http_status'], 500)
        self.assertEqual(data['method'], 'GET')
        self.assertIn('get_IsPlayPhase', data['server_error'])
        self.assertIn('BuildBattleState', data['stack_trace'])
        self.assertEqual(len(self.server.reads), 1)
        self.assertEqual(self.server.posts, [])

    def test_post_http500_keeps_reason_and_never_retries(self):
        self.server.post_status = 500
        self.server.outcome = {'error': 'Action failed: invalid target'}
        with self.assertRaises(sts.Sts2HttpError) as raised:
            self.client.act('combat_play_card', {'card_index': 0}, combat(), self.stop)
        self.assertNotIn('target', str(raised.exception))
        self.assertIn('invalid target', raised.exception.diagnostic_data['server_error'])
        self.assertEqual(raised.exception.diagnostic_data['method'], 'POST')
        self.assertEqual(len(self.server.posts), 1)

    def test_plaintext_http_error_is_bounded(self):
        from io import BytesIO
        from urllib.error import HTTPError
        self.client._http = Mock()
        self.client._http.open.side_effect = HTTPError(
            self.client.base, 502, 'Bad gateway', {}, BytesIO(b'oops ' * 20000))
        with self.assertRaises(sts.Sts2HttpError) as raised:
            self.client.state()
        self.assertLess(len(str(raised.exception)), 350)
        self.assertLessEqual(len(raised.exception.diagnostic_data['server_error']), 500)
        self.assertEqual(raised.exception.diagnostic_data['http_status'], 502)

    def test_unsafe_tools_and_invalid_arguments_are_rejected(self):
        for name, args in [('delete_profile', {'profile_id': 1}),
                           ('menu_select', {'option': 'abandon'}),
                           ('combat_play_card', {'card_index': True}),
                           ('combat_play_card', {'card_index': -1}),
                           ('combat_play_card', {'card_index': 0, 'extra': 'oops'}),
                           ('combat_play_card', {})]:
            with self.subTest(name=name, args=args), self.assertRaises(sts.Sts2Error):
                self.client.act(name, args, combat(), self.stop)
        self.assertEqual(self.server.posts, [])

    def test_wrong_screen_cannot_execute_card_play(self):
        self.server.state = {'state_type': 'map'}
        with self.assertRaises(sts.Sts2Error):
            self.client.act('combat_play_card', {'card_index': 0}, self.server.state, self.stop)
        self.assertEqual(self.server.posts, [])


class BrainTests(unittest.TestCase):
    def setUp(self):
        self.stop = threading.Event()
        self.client = Mock()
        self.client.state.return_value = combat()
        self.client.act.return_value = {'status': 'ok', 'message': 'Played card'}
        self.llm = Mock(return_value=decision())
        self.brain = sts.Sts2Brain(self.client, self.llm, sts.DEFAULTS)

    def test_one_decision_executes_one_action(self):
        result = self.brain.step(self.stop, 'play conservatively')
        self.assertEqual(result.status, 'acted')
        self.assertIn('这回合', result.narration)
        self.assertNotIn('Played card', result.narration)
        self.client.act.assert_called_once()
        self.assertIn('play conservatively', self.llm.call_args.args[0][0]['content'])

    def test_no_tools_can_start_reset_or_delete_runs(self):
        for screen in ('menu', 'game_over', 'overlay', 'unknown'):
            self.assertEqual(sts.tools_for({'state_type': screen}), [])
        self.assertFalse({'menu_select', 'delete_profile', 'switch_profile'} & set(sts.SPECS))

    def test_existing_text_tool_compatibility_is_reused(self):
        self.llm.return_value = {'tool_calls': [], 'content':
            '<invoke name="combat_play_card"><parameter name="card_index">0</parameter>'
            '<parameter name="target">ENEMY_0</parameter></invoke>Play the card.'}
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'acted')
        self.assertNotIn('invoke', result.narration)
        self.client.act.assert_called_once_with('combat_play_card',
            {'card_index': 0, 'target': 'ENEMY_0'}, combat(), self.stop)

    def test_structured_text_decision_avoids_repair_request(self):
        plan = '这波先稳住防守，剩余费用找输出机会，不贪伤害。'
        self.llm.return_value = {'content': json.dumps({
            'narration': plan, 'action': {'name': 'combat_play_card',
                                        'arguments': {'card_index': 0}}}, ensure_ascii=False)}
        result = self.brain.step(self.stop, before_action=Mock())
        self.assertEqual(result.narration, plan)
        self.llm.assert_called_once()
        self.client.act.assert_called_once_with('combat_play_card', {'card_index': 0}, combat(), self.stop)

    def test_structured_text_decision_still_requires_valid_live_action(self):
        for name, args in [('delete_profile', {}), ('combat_play_card', {'card_index': 99}),
                           ('combat_play_card', {'card_index': '0'}),
                           ('map_choose_node', {'node_index': 0})]:
            value = {'content': json.dumps({'action': {'name': name, 'arguments': args}})}
            self.assertEqual(sts.decision_candidates(value, combat())[0], [])

    def test_model_request_is_short_and_uses_remaining_deadline(self):
        with patch('sts2_bridge.time.monotonic', return_value=100):
            self.brain._decide([], [], self.stop, 105)
        self.assertEqual(self.llm.call_args.kwargs['max_tokens'], 256)
        self.assertEqual(self.llm.call_args.kwargs['timeout'], 5)

    def test_transient_chat_connection_failure_retries_once_before_action(self):
        self.llm.side_effect = [urllib.error.URLError(ConnectionRefusedError(10061, 'refused')), decision()]
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'acted')
        self.assertEqual(self.llm.call_count, 2)
        self.client.act.assert_called_once()

    def test_persistent_chat_disconnect_pauses_without_fallback_action(self):
        self.llm.side_effect = urllib.error.URLError(ConnectionRefusedError(10061, 'secret URL'))
        with self.assertRaises(sts.Sts2ModelError) as raised:
            self.brain.step(self.stop)
        self.assertEqual(self.llm.call_count, 2)
        self.assertIn('聊天服务连接中断', str(raised.exception))
        self.assertIn('游戏已暂停', str(raised.exception))
        self.assertNotIn('secret', str(raised.exception))
        self.assertNotIn('secret', str(raised.exception.diagnostic_data))
        self.client.act.assert_not_called()

    def test_chat_failure_during_action_repair_never_uses_fallback(self):
        self.llm.side_effect = [{}, urllib.error.URLError('offline'), urllib.error.URLError('offline')]
        with self.assertRaises(sts.Sts2ModelError):
            self.brain.step(self.stop)
        self.assertEqual(self.llm.call_count, 3)
        self.client.act.assert_not_called()

    def test_chat_http_errors_are_not_retried(self):
        for code in (400, 401, 429, 500):
            self.llm.reset_mock()
            self.llm.side_effect = urllib.error.HTTPError('secret URL', code, 'error', {}, None)
            with self.assertRaises(sts.Sts2ModelError) as raised:
                self.brain.step(self.stop)
            self.assertEqual(raised.exception.diagnostic_data['http_status'], code)
            self.llm.assert_called_once()
        self.client.act.assert_not_called()

    def test_certificate_error_is_not_retried_or_bypassed(self):
        self.llm.side_effect = urllib.error.URLError(ssl.SSLCertVerificationError('untrusted'))
        with self.assertRaises(sts.Sts2ModelError):
            self.brain.step(self.stop)
        self.llm.assert_called_once()
        self.client.act.assert_not_called()

    def test_pause_during_network_retry_never_sends_late_request_or_action(self):
        def disconnected(*args, **kwargs):
            self.stop.set()
            raise urllib.error.URLError('offline')
        self.llm.side_effect = disconnected
        with self.assertRaises(sts.Sts2Cancelled):
            self.brain.step(self.stop)
        self.llm.assert_called_once()
        self.client.act.assert_not_called()

    def test_game_over_pauses_without_model_or_action(self):
        self.client.state.return_value = {'state_type': 'game_over'}
        self.assertEqual(self.brain.step(self.stop).status, 'paused')
        self.llm.assert_not_called()
        self.client.act.assert_not_called()

    def test_enemy_phase_waits_without_model_cost(self):
        self.client.state.return_value['battle']['is_play_phase'] = False
        self.assertEqual(self.brain.step(self.stop).status, 'waiting')
        self.llm.assert_not_called()

    def test_multiple_actions_execute_only_first_valid_candidate(self):
        value = decision()
        value['tool_calls'] += decision('combat_end_turn', {})['tool_calls']
        self.llm.return_value = value
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'acted')
        self.assertEqual(result.action, 'combat_play_card')
        self.client.act.assert_called_once()
        self.llm.assert_called_once()

    def test_wrong_screen_candidate_is_skipped_without_stopping_play(self):
        wrong = decision('map_choose_node', {'node_index': 0})
        wrong['tool_calls'] += decision()['tool_calls']
        self.llm.return_value = wrong
        self.assertEqual(self.brain.step(self.stop).action, 'combat_play_card')
        self.client.act.assert_called_once()

    def test_no_tool_call_is_repaired_once(self):
        self.llm.side_effect = [{'content': '没有唯一最优解。'}, decision()]
        self.assertEqual(self.brain.step(self.stop).status, 'acted')
        self.assertEqual(self.llm.call_count, 2)
        self.client.act.assert_called_once()

    def test_empty_decisions_still_play_current_card(self):
        self.llm.return_value = {'content': '比较困难', 'tool_calls': []}
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'acted')
        self.assertEqual(result.action, 'combat_play_card')
        self.assertIn('这回合', result.narration)
        self.client.act.assert_called_once_with('combat_play_card', {'card_index': 0}, combat(), self.stop)
        self.assertEqual(self.llm.call_count, 2)

    def test_malformed_tool_arguments_use_fallback_not_fake_success(self):
        self.llm.return_value = {'tool_calls': [{'function': {
            'name': 'combat_play_card', 'arguments': 'not json'}}]}
        self.assertEqual(self.brain.step(self.stop).action, 'combat_play_card')
        self.client.act.assert_called_once()

    def test_unplayable_first_candidate_does_not_skip_valid_second(self):
        value = decision(args={'card_index': 20})
        value['tool_calls'] += decision('combat_end_turn', {})['tool_calls']
        self.llm.return_value = value
        self.assertEqual(self.brain.step(self.stop).action, 'combat_end_turn')
        self.client.act.assert_called_once_with('combat_end_turn', {}, combat(), self.stop)

    def test_no_playable_cards_ends_turn(self):
        state = combat()
        state['player']['hand'][0]['can_play'] = False
        self.client.state.return_value = state
        self.llm.return_value = {}
        self.assertEqual(self.brain.step(self.stop).action, 'combat_end_turn')

    def test_cancel_during_repair_never_falls_back(self):
        def llm(*args, **kwargs):
            if self.llm.call_count == 2:
                self.stop.set()
            return {}
        self.llm.side_effect = llm
        with self.assertRaises(sts.Sts2Cancelled):
            self.brain.step(self.stop)
        self.client.act.assert_not_called()

    def test_repair_rechecks_state_before_playing(self):
        enemy_turn = combat()
        enemy_turn['battle']['is_play_phase'] = False
        self.client.state.side_effect = [combat(), enemy_turn]
        self.llm.return_value = {}
        self.assertEqual(self.brain.step(self.stop).status, 'waiting')
        self.llm.assert_called_once()
        self.client.act.assert_not_called()

    @unittest.skipUnless((sts.SKILL_DIR / 'SKILL.md').is_file(), 'Optional upstream strategy not installed')
    def test_loaded_skill_reaches_actual_model_prompt(self):
        self.brain.step(self.stop)
        prompt = self.llm.call_args.args[0][0]['content']
        self.assertIn('ai-slay-the-spire', str(sts.SKILL_DIR))
        self.assertIn('weakness_tags', prompt)
        self.assertIn('deck_strength_evaluation.md', prompt)
        self.assertIn('broken_star_sts_strategy.md', prompt)
        self.assertNotIn('### data/cards_warrior.yaml', prompt)

    def test_repair_shares_original_decision_deadline(self):
        self.brain._decide = Mock(side_effect=[{}, decision()])
        self.assertEqual(self.brain.step(self.stop).status, 'acted')
        calls = self.brain._decide.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[3], calls[1].args[3])

    def test_fallback_stale_state_still_never_reports_success(self):
        self.llm.return_value = {}
        self.client.act.side_effect = sts.StaleState()
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'waiting')
        self.assertEqual(result.narration, '')

    def test_action_waits_until_narration_finishes(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        events, results = [], []

        def speak(text, stop):
            events.append('speech_started')
            entered.set()
            release.wait(2)
            events.append('speech_finished')

        self.client.act.side_effect = lambda *a: events.append('action') or {'status': 'ok'}
        worker = threading.Thread(target=lambda: results.append(self.brain.step(self.stop, before_action=speak)))
        worker.start()
        self.assertTrue(entered.wait(2))
        self.client.act.assert_not_called()
        release.set()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(events, ['speech_started', 'speech_finished', 'action'])
        self.assertEqual(results[0].status, 'acted')

    def test_stop_after_narration_prevents_action(self):
        with self.assertRaises(sts.Sts2Cancelled):
            self.brain.step(self.stop, before_action=lambda text, stop: stop.set())
        self.client.act.assert_not_called()

    def test_narration_failure_never_executes(self):
        with self.assertRaises(sts.Sts2Error):
            self.brain.step(self.stop, before_action=Mock(side_effect=sts.Sts2Error('未显示')))
        self.client.act.assert_not_called()

    def test_raw_response_parameters_never_enter_narration(self):
        self.llm.return_value = decision()
        self.llm.return_value['content'] = 'target=ENEMY_0 card_index=0。索引和参数如下。'
        self.client.act.return_value = {'status': 'ok', 'message': 'Played card at target=ENEMY_0'}
        speaker = Mock()
        result = self.brain.step(self.stop, before_action=speaker)
        self.assertEqual(speaker.call_args.args[0], result.narration)
        for internal in ('target', 'ENEMY_0', 'card_index', '索引', '参数', 'Played card'):
            self.assertNotIn(internal, result.narration)


class RewardProgressTests(unittest.TestCase):
    setUp = BrainTests.setUp

    @staticmethod
    def rewards(*items, floor=2, can_proceed=True):
        return {'state_type': 'rewards', 'run': {'act': 1, 'floor': floor},
                'rewards': {'items': list(items), 'can_proceed': can_proceed}}

    @staticmethod
    def cards(floor=2):
        return {'state_type': 'card_reward', 'run': {'act': 1, 'floor': floor},
                'card_reward': {'can_skip': True, 'cards': [{'index': 0, 'name': '打击'}]}}

    def step(self, state, name=None, args=None, **kwargs):
        self.client.state.return_value = state
        self.llm.return_value = decision(name, args or {}) if name else {}
        return self.brain.step(self.stop, **kwargs)

    def decline(self, state, index=0):
        self.assertEqual(self.step(state, 'rewards_claim', {'reward_index': index}).status, 'acted')
        self.assertEqual(self.step(self.cards(state['run']['floor']), 'rewards_skip_card').status, 'acted')

    def test_skip_returns_to_rewards_and_proceeds_instead_of_reopening(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.llm.reset_mock()
        self.client.act.reset_mock()
        result = self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.assertEqual(result.action, 'proceed_to_map')
        self.llm.assert_not_called()
        self.client.act.assert_called_once_with('proceed_to_map', {}, rewards, self.stop)

    def test_collects_other_rewards_after_skip_and_tracks_index_changes(self):
        rewards = self.rewards({'index': 0, 'type': 'card'}, {'index': 1, 'type': 'gold', 'gold_amount': 25})
        self.decline(rewards)
        result = self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.assertEqual(result.action, 'rewards_claim')
        self.client.act.assert_called_with('rewards_claim', {'reward_index': 1}, rewards, self.stop)
        sent_state = json.loads(self.llm.call_args.args[0][1]['content'].split('\n')[0])
        self.assertEqual(sent_state['rewards']['items'], [rewards['rewards']['items'][1]])
        offered = next(t for t in self.llm.call_args.kwargs['tools'] if t['function']['name'] == 'rewards_claim')
        self.assertEqual(offered['function']['parameters']['properties']['reward_index']['enum'], [1])
        self.assertEqual(len(rewards['rewards']['items']), 2)
        # Collecting gold changes the card's numeric index, but not its identity.
        self.assertEqual(self.step(self.rewards({'index': 0, 'type': 'card'})).action, 'proceed_to_map')

    def test_skip_survives_gold_claim_before_the_card(self):
        initial = self.rewards({'index': 0, 'type': 'gold'}, {'index': 1, 'type': 'card'})
        self.step(initial, 'rewards_claim', {'reward_index': 0})
        remaining = self.rewards({'index': 0, 'type': 'card'})
        self.decline(remaining)
        self.assertEqual(self.step(remaining).action, 'proceed_to_map')

    def test_different_card_rewards_are_not_all_skipped(self):
        rewards = self.rewards({'index': 0, 'type': 'card', 'description': '普通奖励'},
                               {'index': 1, 'type': 'card', 'description': '稀有奖励'})
        self.decline(rewards)
        self.step(rewards, 'rewards_claim', {'reward_index': 1})
        self.client.act.assert_called_with('rewards_claim', {'reward_index': 1}, rewards, self.stop)
        self.step(self.cards(), 'rewards_pick_card', {'card_index': 0})
        self.assertEqual(self.step(self.rewards(rewards['rewards']['items'][0])).action, 'proceed_to_map')

    def test_duplicate_looking_rewards_track_the_selected_occurrence(self):
        rewards = self.rewards({'index': 0, 'type': 'card'}, {'index': 1, 'type': 'card'})
        self.decline(rewards, index=1)
        self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.client.act.assert_called_with('rewards_claim', {'reward_index': 0}, rewards, self.stop)
        self.step(self.cards(), 'rewards_pick_card', {'card_index': 0})
        # The picked occurrence disappears and the previously skipped one moves left.
        self.assertEqual(self.step(self.rewards({'index': 0, 'type': 'card'})).action, 'proceed_to_map')

    def test_game_removed_skipped_reward_does_not_hide_other_card_reward(self):
        rewards = self.rewards({'index': 0, 'type': 'card'}, {'index': 1, 'type': 'card'})
        self.decline(rewards)
        remaining = self.rewards({'index': 0, 'type': 'card'})
        self.assertEqual(self.step(remaining, 'rewards_claim', {'reward_index': 0}).action, 'rewards_claim')
        self.client.act.assert_called_with('rewards_claim', {'reward_index': 0}, remaining, self.stop)

    def test_skip_outside_brain_opened_popup_matches_single_card_reward(self):
        self.step(self.cards(), 'rewards_skip_card')
        self.assertEqual(self.step(self.rewards({'index': 0, 'type': 'card'})).action, 'proceed_to_map')

    def test_unknown_origin_with_multiple_rewards_pauses_instead_of_guessing(self):
        self.step(self.cards(), 'rewards_skip_card')
        self.client.act.reset_mock()
        with self.assertRaisesRegex(sts.Sts2Error, '无法区分'):
            self.step(self.rewards({'index': 0, 'type': 'card'}, {'index': 1, 'type': 'card'}))
        self.client.act.assert_not_called()

    def test_next_floor_and_leaving_room_clear_declined_rewards(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.step(rewards)
        self.step(self.rewards({'index': 0, 'type': 'card'}, floor=3),
                  'rewards_claim', {'reward_index': 0})
        self.assertFalse(self.brain._declined_rewards)
        self.step({'state_type': 'map', 'run': {'act': 1, 'floor': 3}}, 'map_choose_node', {'node_index': 0})
        self.assertIsNone(self.brain._pending_reward)

    def test_resume_keeps_reward_decision(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.brain.reset_for_resume()
        self.assertEqual(self.step(rewards).action, 'proceed_to_map')

    def test_unchanged_snapshot_after_open_does_not_forget_pending_reward(self):
        rewards = self.rewards({'index': 0, 'type': 'card'}, {'index': 1, 'type': 'card'})
        self.step(rewards, 'rewards_claim', {'reward_index': 1})
        self.assertEqual(self.step(rewards).status, 'waiting')
        self.step(self.cards(), 'rewards_skip_card')
        self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.client.act.assert_called_with('rewards_claim', {'reward_index': 0}, rewards, self.stop)

    def test_failed_skip_is_not_recorded_as_a_declined_reward(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.client.act.side_effect = sts.Sts2GameError('POST', '/', 'failed')
        with self.assertRaises(sts.Sts2GameError):
            self.step(self.cards(), 'rewards_skip_card')
        self.client.act.side_effect = None
        self.brain.reset_for_resume()
        self.assertEqual(self.step(rewards, 'rewards_claim', {'reward_index': 0}).action, 'rewards_claim')

    def test_stale_skip_is_not_recorded_and_redecides_from_latest_reward(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.step(rewards, 'rewards_claim', {'reward_index': 0})
        self.client.act.side_effect = sts.StaleState()
        self.assertEqual(self.step(self.cards(), 'rewards_skip_card').status, 'waiting')
        self.client.act.side_effect = None
        # Change player data so this is not the previous unchanged parent snapshot.
        rewards = dict(rewards, player={'hp': 50})
        self.assertEqual(self.step(rewards, 'rewards_claim', {'reward_index': 0}).action, 'rewards_claim')

    def test_cleanup_waits_for_ready_proceed_and_never_reopens_skipped_card(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.client.act.reset_mock()
        with self.assertRaisesRegex(sts.Sts2Error, '前进按钮暂不可用'):
            self.step(self.rewards({'index': 0, 'type': 'card'}, can_proceed=False))
        self.client.act.assert_not_called()

    def test_cancel_before_cleanup_never_executes_proceed(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.client.act.reset_mock()
        self.stop.set()
        with self.assertRaises(sts.Sts2Cancelled):
            self.step(rewards)
        self.client.act.assert_not_called()

    def test_missing_reward_list_does_not_guess_or_proceed(self):
        rewards = self.rewards({'index': 0, 'type': 'card'})
        self.decline(rewards)
        self.client.act.reset_mock()
        with self.assertRaisesRegex(sts.Sts2Error, '读不到剩余奖励'):
            self.step({'state_type': 'rewards', 'run': {'act': 1, 'floor': 2},
                       'rewards': {'can_proceed': True}})
        self.client.act.assert_not_called()


class StrategyTests(unittest.TestCase):
    @unittest.skipUnless((sts.SKILL_DIR / 'SKILL.md').is_file(), 'Optional upstream strategy not installed')
    def test_combat_references_are_small_and_keep_combat_priorities(self):
        for character in ('IRONCLAD', 'SILENT'):
            context = sts.strategy_context({'state_type': 'monster', 'player': {'character': character}})
            self.assertLess(len(context), 6500)
            for important in ('weakness_tags', 'Combat Priorities', 'incoming damage is lethal',
                              'deck_strength_evaluation.md', 'broken_star_sts_strategy.md'):
                self.assertIn(important, context)
            for irrelevant in ('cards_warrior.yaml', '## Output Format', '### 11.1 地图节点评分'):
                self.assertNotIn(irrelevant, context)

    def test_combat_tool_schema_constrains_to_playable_cards_and_live_targets(self):
        state = combat()
        state['player']['hand'].append({'index': 7, 'can_play': False})
        state['battle']['enemies'].append({'entity_id': 'DEAD', 'hp': 0})
        properties = sts.tools_for(state)[0]['function']['parameters']['properties']
        self.assertEqual(properties['card_index']['enum'], [0])
        self.assertEqual(properties['target']['enum'], ['ENEMY_0'])
        state['player']['hand'] = []
        names = [tool['function']['name'] for tool in sts.tools_for(state)]
        self.assertNotIn('combat_play_card', names)
        self.assertIn('combat_end_turn', names)

    @unittest.skipUnless((sts.SKILL_DIR / 'SKILL.md').is_file(), 'Optional upstream strategy not installed')
    def test_reward_and_ironclad_references_load_only_when_relevant(self):
        state = {'state_type': 'card_reward', 'player': {'character': 'IRONCLAD'}}
        context = sts.strategy_context(state)
        self.assertIn('card_selection_scoring.md', context)
        self.assertIn('cards_warrior.yaml', context)
        self.assertNotIn('proposals/', context.split('### references/deck_strength_evaluation.md')[1])
        self.assertLessEqual(len(context), 32000)

    def test_targeted_fallback_uses_live_enemy_id(self):
        state = combat()
        state['player']['hand'][0]['target_type'] = 'AnyEnemy'
        self.assertEqual(sts.fallback_action(state),
            ('combat_play_card', {'card_index': 0, 'target': 'ENEMY_0'}))
        with self.assertRaises(sts.Sts2Error):
            sts.validate_action('combat_play_card', {'card_index': 0, 'target': 'MADE_UP'}, state)

    def test_no_enemy_target_never_invents_one(self):
        state = combat()
        state['player']['hand'][0]['target_type'] = 'AnyEnemy'
        state['battle']['enemies'] = []
        self.assertEqual(sts.fallback_action(state), ('combat_end_turn', {}))

    def test_fallback_reward_skips_and_map_uses_existing_node(self):
        self.assertEqual(sts.fallback_action({'state_type': 'card_reward', 'card_reward': {'can_skip': True}}),
                         ('rewards_skip_card', {}))
        state = {'state_type': 'map', 'map': {'next_options': [
            {'index': 3, 'type': 'Elite'}, {'index': 7, 'type': 'RestSite'}]}}
        self.assertEqual(sts.fallback_action(state), ('map_choose_node', {'node_index': 7}))

    def test_fallback_avoids_locked_events_and_disabled_camp_choices(self):
        event = {'state_type': 'event', 'event': {'options': [
            {'index': 0, 'is_locked': True}, {'index': 1, 'is_locked': False}]}}
        self.assertEqual(sts.fallback_action(event), ('event_choose_option', {'option_index': 1}))
        camp = {'state_type': 'rest_site', 'rest_site': {'options': [
            {'index': 0, 'is_enabled': False}, {'index': 1, 'is_enabled': True}]}}
        self.assertEqual(sts.fallback_action(camp), ('rest_choose_option', {'option_index': 1}))

    def test_confirm_treasure_bundle_and_sphere_fallbacks(self):
        cases = [
            ('hand_select', {'can_confirm': True}, ('combat_confirm_selection', {})),
            ('card_select', {'can_confirm': True}, ('deck_confirm_selection', {})),
            ('treasure', {'relics': [{'index': 4}]}, ('treasure_claim_relic', {'relic_index': 4})),
            ('bundle_select', {'can_confirm': True}, ('bundle_confirm_selection', {})),
            ('crystal_sphere', {'can_proceed': True}, ('crystal_sphere_proceed', {})),
            ('crystal_sphere', {'tool': 'small', 'clickable_cells': [{'x': 1, 'y': 2}]},
             ('crystal_sphere_click_cell', {'x': 1, 'y': 2})),
        ]
        for screen, section, expected in cases:
            with self.subTest(screen=screen):
                self.assertEqual(sts.fallback_action({'state_type': screen, screen: section}), expected)

    def test_invalid_visible_index_and_disabled_confirmation_are_filtered(self):
        state = {'state_type': 'map', 'map': {'next_options': [{'index': 1}]}}
        self.assertEqual(sts.decision_candidates(decision('map_choose_node', {'node_index': 8}), state)[0], [])
        state = {'state_type': 'hand_select', 'hand_select': {'can_confirm': False}}
        self.assertEqual(sts.decision_candidates(decision('combat_confirm_selection', {}), state)[0], [])

    def test_no_fallback_can_reset_start_or_delete_runs(self):
        for screen in ('menu', 'overlay', 'game_over', 'unknown'):
            self.assertIsNone(sts.fallback_action({'state_type': screen}))

    def test_narration_uses_display_names_not_ids(self):
        state = combat()
        state['player']['hand'][0]['name'] = '打击'
        state['battle']['enemies'][0]['name'] = '甲虫'
        text = sts.action_narration('combat_play_card', {'card_index': 0, 'target': 'ENEMY_0'}, state,
                                    '先压低它的血量，减少后续压力。')
        self.assertIn('打击', text)
        self.assertIn('甲虫', text)
        self.assertIn('减少后续压力', text)
        self.assertNotIn('ENEMY_0', text)

    def test_every_tool_has_natural_chinese_narration(self):
        for name, spec in sts.SPECS.items():
            args = {key.rstrip('?'): 0 if kind == 'integer' else 'INTERNAL_0'
                    for key, kind in spec[3].items()}
            with self.subTest(name=name):
                text = sts.action_narration(name, args, combat())
                self.assertTrue(text)
                self.assertFalse(any(c.isascii() and c.isalpha() for c in text))
                self.assertNotIn(name, text)


class ContinuityTests(unittest.TestCase):
    setUp = BrainTests.setUp

    def test_stale_state_is_not_narrated_as_success(self):
        self.client.act.side_effect = sts.StaleState()
        result = self.brain.step(self.stop)
        self.assertEqual(result.status, 'waiting')
        self.assertEqual(result.narration, '')

    def test_unchanged_state_does_not_repeat_last_action(self):
        self.brain.step(self.stop)
        self.assertEqual(self.brain.step(self.stop).status, 'waiting')
        self.assertEqual(self.brain.step(self.stop).status, 'waiting')
        self.assertEqual(self.brain.step(self.stop).status, 'paused')
        self.llm.assert_called_once()
        self.client.act.assert_called_once()

    def test_stalled_decision_can_cancel_without_late_action(self):
        entered, release, completed = (threading.Event() for _ in range(3))
        self.addCleanup(release.set)

        def llm(*a, **k):
            entered.set()
            release.wait(2)
            completed.set()
            return decision()

        self.brain.llm = llm
        result = []

        def work():
            try:
                self.brain.step(self.stop)
            except Exception as exc:
                result.append(exc)

        worker = threading.Thread(target=work)
        worker.start()
        self.assertTrue(entered.wait(2))
        self.stop.set()
        worker.join(1)
        self.assertFalse(worker.is_alive())
        self.assertIsInstance(result[0], sts.Sts2Cancelled)
        release.set()
        self.assertTrue(completed.wait(2))
        self.client.act.assert_not_called()


class RoundStrategyTests(unittest.TestCase):
    def test_first_card_log_is_not_a_round_plan(self):
        for text in ('我先打出打击。', '这回合我先打出防御，防守牌比较节省费用。',
                     '我先用打击攻击这个敌人，再留一点费用用于防守。',
                     '我先打一张打击输出，再用防御挡下这 6 点伤害。',
                     '这回合先出打击进攻，再出防御把剩下的费用用完。'):
            with self.subTest(text=text):
                self.assertEqual(sts._round_plan_text(text), '')

    def test_round_summary_does_not_claim_exact_or_guaranteed_outcomes(self):
        for text in ('这回合挡住这 6 点伤害，把剩余费用用于输出。',
                     '这回合保证完全挡住攻击，把余下费用留给进攻。'):
            self.assertEqual(sts._round_plan_text(text), '')

    def test_whole_round_plan_is_used_without_card_prefix(self):
        text = '这回合先挡住主要伤害，再用剩余费用集中进攻，尽量少掉血。'
        self.assertEqual(sts._round_plan_text(text), text)
        self.assertEqual(sts._round_plan_text(text).count('。'), 1)

    def test_internal_arguments_never_enter_round_plan(self):
        for text in ('这回合先格挡，再用费用攻击 target=ENEMY_0。',
                     '这回合以防守为主，模型说可以把费用留给输出。',
                     '这回合先格挡，再分配费用进攻。\ncard_index=0'):
            with self.subTest(text=text):
                self.assertEqual(sts._round_plan_text(text), '')

    def test_fallback_uses_known_enemy_intents_and_survival_needs(self):
        state = combat()
        state['battle']['enemies'][0]['intents'] = [{'type': 'MultiAttack'}]
        self.assertIn('稳住防守', sts.round_strategy(state))
        state['battle']['enemies'][0]['intents'] = [{'type': 'Buff'}]
        self.assertIn('敌人没有进攻', sts.round_strategy(state))
        state['player']['hp'] = 10
        self.assertIn('保命', sts.round_strategy(state))

    def test_missing_intents_do_not_invent_non_attacking_enemy(self):
        self.assertNotIn('敌人没有进攻', sts.round_strategy(combat()))
        self.assertNotIn('打出', sts.round_strategy(combat()))
        state = combat()
        state['battle']['enemies'][0]['intents'] = [{'type': 'UnrecognizedIntent'}]
        self.assertNotIn('敌人没有进攻', sts.round_strategy(state))

    def test_long_commentary_is_not_spoken_and_fallbacks_are_short(self):
        self.assertEqual(sts._round_plan_text('这回合先稳住防守，把费用留给进攻，' + '别贪伤害' * 10), '')
        for intent in ('Attack', 'Buff', 'Unknown'):
            state = combat()
            state['battle']['enemies'][0]['intents'] = [{'type': intent}]
            self.assertLessEqual(len(sts.round_strategy(state)), 40)
            self.assertEqual(sts._round_plan_text(sts.round_strategy(state)), sts.round_strategy(state))


class RoundNarrationTests(unittest.TestCase):
    def setUp(self):
        self.clock = patch('sts2_bridge.time.monotonic', return_value=100).start()
        self.addCleanup(patch.stopall)
        self.client = Mock()
        self.client.act.return_value = {'status': 'ok'}
        self.llm = Mock(return_value=decision())
        self.brain = sts.Sts2Brain(self.client, self.llm, sts.DEFAULTS)
        self.speaker = Mock()
        self.stop = threading.Event()
        self.sequence = 0

    def step(self, state=None, instruction=''):
        state = state or combat()
        self.sequence += 1
        state['observed_step'] = self.sequence
        self.client.state.return_value = state
        return self.brain.step(self.stop, instruction, before_action=self.speaker)

    def test_continuous_cards_and_end_turn_are_silent_after_opening(self):
        self.assertTrue(self.step().narrated)
        for instant in (105, 125, 160):
            self.clock.return_value = instant
            self.assertFalse(self.step().narrated)
        self.llm.return_value = decision('combat_end_turn', {})
        self.assertFalse(self.step().narrated)
        self.speaker.assert_called_once()
        self.assertEqual(self.client.act.call_count, 5)

    def test_new_battle_speaks_even_if_round_number_restarts_quickly(self):
        self.step()
        state = combat()
        state['run']['floor'] = 3
        self.clock.return_value = 110
        self.assertTrue(self.step(state).narrated)
        state = combat()
        state['run']['floor'] = 3
        self.clock.return_value = 121
        self.assertFalse(self.step(state).narrated)
        state = combat()
        state['run']['floor'] = 3
        self.clock.return_value = 150
        self.assertFalse(self.step(state).narrated)
        self.assertEqual(self.speaker.call_count, 2)

    def test_choices_speak_once_per_scene_not_every_purchase(self):
        self.step()
        self.clock.return_value = 125
        self.llm.return_value = decision('shop_purchase', {'item_index': 0})
        shop = {'state_type': 'shop', 'run': {'act': 1, 'floor': 3}}
        self.assertTrue(self.step(dict(shop)).narrated)
        self.clock.return_value = 155
        self.assertFalse(self.step(dict(shop)).narrated)
        self.assertEqual(self.speaker.call_count, 2)

    def test_cleanup_and_confirmation_steps_do_not_speak(self):
        self.step()
        self.clock.return_value = 200
        for screen, action, args in (
                ('rewards', 'rewards_claim', {'reward_index': 0}),
                ('rewards', 'proceed_to_map', {}),
                ('card_select', 'deck_confirm_selection', {}),
                ('event', 'event_advance_dialogue', {}),
                ('crystal_sphere', 'crystal_sphere_click_cell', {'x': 0, 'y': 0})):
            with self.subTest(action=action):
                self.llm.return_value = decision(action, args)
                self.assertFalse(self.step({'state_type': screen}).narrated)
        self.speaker.assert_called_once()

    def test_health_changes_do_not_add_extra_speech_in_same_round(self):
        self.step()
        self.clock.return_value = 101
        state = combat()
        state['player']['hp'] = 15
        result = self.step(state)
        self.assertFalse(result.narrated)
        state = combat()
        state['player']['hp'] = 10
        self.clock.return_value = 150
        self.assertFalse(self.step(state).narrated)
        self.speaker.assert_called_once()

    def test_changed_instruction_does_not_repeat_round_commentary(self):
        self.step()
        self.clock.return_value = 101
        self.assertFalse(self.step(instruction='优先防御').narrated)
        self.speaker.assert_called_once()

    def test_next_round_speaks_once_without_time_based_cooldown(self):
        self.step()
        self.clock.return_value = 101
        state = combat()
        state['battle']['round'] = 2
        result = self.step(state)
        self.assertTrue(result.narrated)
        self.assertTrue(result.narration.startswith('这回合'))
        self.assertEqual(result.narration.count('。'), 1)
        state = combat()
        state['battle']['round'] = 2
        self.assertFalse(self.step(state).narrated)
        self.assertEqual(self.speaker.call_count, 2)

    def test_potion_does_not_add_extra_speech_in_same_round(self):
        self.step()
        self.llm.return_value = decision('use_potion', {'slot': 0})
        self.assertFalse(self.step().narrated)
        self.speaker.assert_called_once()

    def test_enemy_phase_does_not_consume_next_round_commentary(self):
        self.step()
        state = combat()
        state['battle'].update(round=2, turn='enemy', is_play_phase=False)
        self.assertEqual(self.step(state).status, 'waiting')
        self.speaker.assert_called_once()
        state = combat()
        state['battle']['round'] = 2
        self.assertTrue(self.step(state).narrated)
        self.assertEqual(self.speaker.call_count, 2)

    def test_disabled_narration_does_not_invoke_speaker(self):
        self.brain.cfg['narration'] = False
        self.assertFalse(self.step(instruction='优先防御').narrated)
        self.speaker.assert_not_called()
        self.client.act.assert_called_once()

    def test_selection_popup_does_not_restart_battle_commentary(self):
        self.step()
        self.clock.return_value = 125
        self.llm.return_value = decision('combat_select_card', {'card_index': 0})
        self.assertFalse(self.step({'state_type': 'hand_select'}).narrated)
        self.llm.return_value = decision()
        self.assertFalse(self.step().narrated)
        self.speaker.assert_called_once()

    def test_failed_speech_does_not_consume_commentary_slot(self):
        self.speaker.side_effect = sts.Sts2Error('Audio failed')
        with self.assertRaises(sts.Sts2Error):
            self.step()
        self.client.act.assert_not_called()
        self.speaker.side_effect = None
        self.assertTrue(self.step().narrated)

    def test_stale_after_speech_does_not_repeat_same_commentary(self):
        self.client.act.side_effect = sts.StaleState()
        self.assertEqual(self.step().status, 'waiting')
        self.client.act.side_effect = None
        self.clock.return_value = 150
        self.assertFalse(self.step().narrated)
        self.speaker.assert_called_once()

    def test_overall_plan_replaces_first_card_and_guides_later_steps(self):
        plan = '这回合优先挡住伤害，把剩余费用留给进攻，别为了输出掉太多血。'
        value = decision()
        value['content'] = plan
        self.llm.return_value = value
        result = self.step()
        self.assertEqual(result.narration, plan)
        self.speaker.assert_called_once_with(plan, self.stop)
        self.llm.assert_called_once()
        self.assertFalse(self.step().narrated)
        self.assertIn('本回合已说明的打法：' + plan, self.llm.call_args.args[0][0]['content'])

    def test_tool_only_response_uses_instant_plan_without_extra_model_request(self):
        value = decision()
        value['content'] = None
        self.llm.return_value = value
        result = self.step()
        self.assertEqual(result.narration, sts.round_strategy(self.client.state.return_value))
        self.llm.assert_called_once()
        prompt = self.llm.call_args.args[0][0]['content']
        self.assertIn('结合整手牌', prompt)
        self.assertIn('不展开推理过程', prompt)
        self.assertIn('主播', prompt)
        self.assertIn('最长四十字', prompt)
        self.client.act.assert_called_once()

    def test_joint_tool_commentary_is_required_once_and_never_sent_to_game(self):
        plan = '这波先稳住防守，剩余费用找输出机会，不贪伤害。'
        value = decision(args={'card_index': 0, 'round_commentary': plan})
        self.llm.return_value = value
        result = self.step()
        self.assertEqual(result.narration, plan)
        self.speaker.assert_called_once_with(plan, self.stop)
        self.client.act.assert_called_once_with('combat_play_card', {'card_index': 0},
                                                self.client.state.return_value, self.stop)
        self.llm.assert_called_once()
        for tool in self.llm.call_args.kwargs['tools']:
            self.assertIn('round_commentary', tool['function']['parameters']['required'])
        self.assertFalse(self.step().narrated)
        for tool in self.llm.call_args.kwargs['tools']:
            self.assertNotIn('round_commentary', tool['function']['parameters']['properties'])
        # Parsing does not mutate provider responses or widen the HTTP parameter contract.
        self.assertIn('round_commentary', json.loads(value['tool_calls'][0]['function']['arguments']))
        with self.assertRaises(sts.Sts2Error):
            sts.validate_action('combat_play_card', {'card_index': 0, 'round_commentary': plan}, combat())

    def test_disabled_speech_does_not_request_tool_commentary(self):
        self.brain.cfg['narration'] = False
        self.step()
        for tool in self.llm.call_args.kwargs['tools']:
            self.assertNotIn('round_commentary', tool['function']['parameters']['properties'])

    def test_bad_plan_falls_back_without_requesting_summary(self):
        for summary in ('我先打出防御，节约防守费用。', 'target=ENEMY_0', '', '输出' * 60):
            with self.subTest(summary=summary):
                self.brain = sts.Sts2Brain(self.client, self.llm, sts.DEFAULTS)
                self.llm.reset_mock()
                value = decision()
                value['content'] = summary
                self.llm.return_value = value
                result = self.step()
                self.assertTrue(result.narrated)
                self.assertIn('防守和进攻', result.narration)
                self.assertNotIn('打出', result.narration)
                self.assertNotIn('target', result.narration)
                self.llm.assert_called_once()

    def test_cancelling_joint_decision_never_speaks_or_executes(self):
        def model(*args, **kwargs):
            self.stop.set()
            return decision()
        self.llm.side_effect = model
        with self.assertRaises(sts.Sts2Cancelled):
            self.step()
        self.speaker.assert_not_called()
        self.client.act.assert_not_called()

    def test_later_actions_do_not_request_repeated_prose_and_keep_full_hand(self):
        self.step()
        self.assertFalse(self.step().narrated)
        messages = self.llm.call_args.args[0]
        self.assertIn('不生成正文，只给一个动作', messages[0]['content'])
        sent_state = json.loads(messages[1]['content'])
        self.assertEqual(sent_state, self.client.state.return_value)


class WindowTests(unittest.TestCase):
    def test_resuming_keeps_reward_memory_and_refreshes_chat_client(self):
        brain = Mock()
        chat = SimpleNamespace(ready=lambda: True, complete=Mock(), persona='new persona')
        window = SimpleNamespace(sts2_busy=False, chat_client=chat,
            sts2_cfg={'enabled': True, 'interval_seconds': 2}, sts2_brain=brain,
            sts2_steps=12, sts2_timer=Mock(), _sts2_step=Mock(), sts2_status=Mock())
        PetWindow._sts2_start(window)
        self.assertIs(window.sts2_brain, brain)
        brain.reset_for_resume.assert_called_once()
        self.assertIs(brain.llm, chat.complete)
        self.assertEqual(brain.persona, 'new persona')
        self.assertEqual(window.sts2_steps, 0)
        window._sts2_step.assert_called_once()

    def test_voice_commands_are_queued_to_gui_thread(self):
        signal = Mock()
        window = SimpleNamespace(sts2_ui_command=signal)
        results = []
        worker = threading.Thread(target=lambda: results.extend([
            PetWindow._handle_sts2_command(window, '继续尖塔'),
            PetWindow._handle_sts2_command(window, '今天天气不错')]))
        worker.start()
        worker.join(2)
        self.assertEqual(results, [True, False])
        signal.emit.assert_called_once_with('继续尖塔')

    def test_plain_chat_is_not_routed_to_game(self):
        self.assertFalse(PetWindow._handle_sts2_command(SimpleNamespace(), '尖塔这个游戏好玩吗'))

    def test_step_budget_pauses_automatic_play(self):
        window = SimpleNamespace(sts2_busy=True, sts2_token=1, sts2_stop=threading.Event(),
            sts2_steps=0, sts2_cfg={'narration': False, 'max_steps': 1},
            sts2_timer=Mock(), sts2_status=Mock(), memory=Mock(), dialogue=Mock(),
            _sts2_pause=Mock(), _update_dialogue_busy=Mock())
        PetWindow._sts2_on_finished(window, sts.StepResult('state', 'acted', 'accepted', 'end_turn'), 1)
        self.assertEqual(window.sts2_steps, 1)
        window._sts2_pause.assert_called_once_with(notify=False)
        window.dialogue.submit.assert_not_called()
        window.memory.record_line.assert_not_called()

    def test_late_completion_after_pause_is_ignored(self):
        window = SimpleNamespace(sts2_busy=True, sts2_token=2, sts2_stop=threading.Event(),
                                 memory=Mock(), dialogue=Mock(), _update_dialogue_busy=Mock())
        PetWindow._sts2_on_finished(window, sts.StepResult('old', 'acted', 'old'), 1)
        self.assertFalse(window.sts2_busy)
        window.memory.record_line.assert_not_called()

    def test_http_failure_pauses_and_logs_server_diagnostics(self):
        window = SimpleNamespace(sts2_busy=True, sts2_token=1,
            sts2_stop=threading.Event(), _sts2_pause=Mock(), diagnostics=Mock(),
            sts2_status=Mock(), _update_dialogue_busy=Mock())
        error = sts.Sts2HttpError(500, 'GET', '/api/v1/singleplayer?format=json', {
            'error': 'Method not found: CombatManager.get_IsPlayPhase()',
            'exception_type': 'System.MissingMethodException'})
        PetWindow._sts2_on_finished(window, error, 1)
        window._sts2_pause.assert_called_once_with(notify=False)
        window.diagnostics.event.assert_called_once_with(
            'sts2.error', error='Sts2HttpError', **error.diagnostic_data)
        self.assertIn('版本不兼容', window.sts2_status.emit.call_args.args[0])

    def test_config_defaults_and_limits(self):
        self.assertFalse(sts.normalize_config(None)['enabled'])
        cfg = sts.normalize_config({'port': 90000, 'max_steps': -1, 'interval_seconds': 'oops'})
        self.assertEqual(cfg['port'], 65535)
        self.assertEqual(cfg['max_steps'], 1)
        self.assertEqual(cfg['interval_seconds'], 2)

    def test_stop_control_is_available_during_game_thinking(self):
        window = SimpleNamespace(page_loaded=True, sts2_busy=True,
            sts2_stop=threading.Event(), sts2_timer=SimpleNamespace(isActive=lambda: False),
            dialogue=SimpleNamespace(busy=False), _run_js=Mock())
        PetWindow._update_dialogue_busy(window)
        window._run_js.assert_called_once_with('window.setDialogueBusy(true)')


class NarrationDeliveryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        dialogue = pet_runtime.DialogueRuntime(pet_runtime.Diagnostics(str(Path(directory.name) / 'events.log')))
        self.addCleanup(dialogue.close)
        self.stop = threading.Event()
        self.window = SimpleNamespace(sts2_cfg={'narration': True}, dialogue=dialogue,
                                      _speech_generation=1, _emit_speech=Mock())

    def run_before(self):
        self.errors, self.completed = [], threading.Event()

        def run():
            try:
                PetWindow._sts2_before_action(self.window, '我先打出打击。', self.stop)
            except Exception as exc:
                self.errors.append(exc)
            finally:
                self.completed.set()
        worker = threading.Thread(target=run)
        worker.start()
        self.addCleanup(lambda: worker.join(2))
        return worker

    def test_actual_dialogue_queue_waits_for_speech_completion(self):
        started, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)

        def speak(*args, **kwargs):
            started.set()
            release.wait(2)
        self.window._emit_speech.side_effect = speak
        worker = self.run_before()
        self.assertTrue(started.wait(2))
        self.assertFalse(self.completed.is_set())
        release.set()
        worker.join(2)
        self.assertTrue(self.completed.is_set())
        self.assertEqual(self.errors, [])

    def test_interrupting_queued_speech_cancels_action_barrier(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        blocker = self.window.dialogue.submit('chat', lambda: entered.set() or release.wait(2))
        self.assertTrue(entered.wait(2))
        submitted = threading.Event()
        original_submit = self.window.dialogue.submit

        def submit(*args, **kwargs):
            future = original_submit(*args, **kwargs)
            submitted.set()
            return future
        self.window.dialogue.submit = submit
        worker = self.run_before()
        self.assertTrue(submitted.wait(2))
        self.window.dialogue.interrupt()
        worker.join(2)
        self.assertFalse(worker.is_alive())
        self.assertIsInstance(self.errors[0], sts.Sts2Cancelled)
        self.window._emit_speech.assert_not_called()
        release.set()

    def test_text_only_delivery_waits_for_gui_acknowledgement(self):
        requested, release = threading.Event(), threading.Event()
        packet = []
        self.addCleanup(release.set)

        def request(text, delivery):
            packet.append(delivery)
            requested.set()
        self.window.sts2_text_requested = SimpleNamespace(emit=request)
        self.window._emit_speech.side_effect = lambda text, text_delivery, **kw: text_delivery(text)
        worker = self.run_before()
        self.assertTrue(requested.wait(2))
        self.assertFalse(self.completed.is_set())
        packet[0]['shown'] = True
        packet[0]['done'].set()
        worker.join(2)
        self.assertEqual(self.errors, [])

    def test_disabled_narration_does_not_wait(self):
        self.window.sts2_cfg['narration'] = False
        PetWindow._sts2_before_action(self.window, '我先打出打击。', self.stop)
        self.window._emit_speech.assert_not_called()

    def test_gui_text_delivery_is_acknowledged_after_javascript(self):
        callbacks = []
        page = SimpleNamespace(runJavaScript=lambda script, callback: callbacks.append(callback))
        window = SimpleNamespace(page_loaded=True, _speech_generation=1,
                                 view=SimpleNamespace(page=lambda: page))
        delivery = {'stop': self.stop, 'done': threading.Event(), 'shown': False, 'generation': 1}
        PetWindow._show_sts2_text(window, '我先打出打击。', delivery)
        self.assertFalse(delivery['done'].is_set())
        callbacks[0](True)
        self.assertTrue(delivery['done'].is_set())
        self.assertTrue(delivery['shown'])

    def test_stale_text_delivery_never_reaches_page(self):
        page = Mock()
        window = SimpleNamespace(page_loaded=True, _speech_generation=2,
                                 view=SimpleNamespace(page=lambda: page))
        delivery = {'stop': self.stop, 'done': threading.Event(), 'shown': False, 'generation': 1}
        PetWindow._show_sts2_text(window, '旧旁白', delivery)
        page.runJavaScript.assert_not_called()
        self.assertTrue(delivery['done'].is_set())
        self.assertFalse(delivery['shown'])


if __name__ == '__main__':
    unittest.main()
