import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pet_runtime


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'runtime.log'
        self.runtime = pet_runtime.DialogueRuntime(pet_runtime.Diagnostics(str(self.path)))
        self.addCleanup(self.runtime.close)

    def block(self, source='chat', priority=0):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)

        def work():
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test timed out')
            pet_runtime.checkpoint()
            return source

        future = self.runtime.submit(source, work, priority)
        self.assertTrue(entered.wait(2))
        return future, release

    def test_user_turns_run_in_order(self):
        first, release = self.block()
        seen = []
        second = self.runtime.submit('chat', lambda: seen.append('second'))
        third = self.runtime.submit('voice', lambda: seen.append('third'))
        self.assertEqual(seen, [])
        release.set()
        first.result(2)
        second.result(2)
        third.result(2)
        self.assertEqual(seen, ['second', 'third'])

    def test_user_input_drops_pending_ambient_turns(self):
        first, release = self.block()
        ambient = self.runtime.submit('proactive', lambda: self.fail('stale output'), 20)
        user = self.runtime.submit('chat', lambda: 'new input')
        with self.assertRaises(pet_runtime.TurnCancelled):
            ambient.result(2)
        release.set()
        first.result(2)
        self.assertEqual(user.result(2), 'new input')

    def test_user_input_interrupts_active_ambient_turn(self):
        active, release = self.block('proactive', 20)
        user = self.runtime.submit('chat', lambda: 'user')
        release.set()
        with self.assertRaises(pet_runtime.TurnCancelled):
            active.result(2)
        self.assertEqual(user.result(2), 'user')

    def test_interrupt_cancels_active_and_queued_turns(self):
        active, release = self.block()
        queued = self.runtime.submit('voice', lambda: self.fail('cancelled turn ran'))
        self.runtime.interrupt()
        release.set()
        for future in (active, queued):
            with self.assertRaises(pet_runtime.TurnCancelled):
                future.result(2)
        self.assertEqual(self.runtime.submit('chat', lambda: 'retry').result(2), 'retry')

    def test_task_failure_does_not_stop_dispatcher(self):
        def fail():
            raise ValueError('failed')

        with self.assertRaises(ValueError):
            self.runtime.submit('chat', fail).result(2)
        self.assertEqual(self.runtime.submit('chat', lambda: 123).result(2), 123)

    def test_interruption_releases_stalled_io_without_late_output(self):
        entered, release, finished = (threading.Event() for _ in range(3))
        self.addCleanup(release.set)
        seen = []

        def io():
            entered.set()
            try:
                release.wait(2)
                pet_runtime.checkpoint()
                seen.append('stale output')
            finally:
                finished.set()

        active = self.runtime.submit('chat', lambda: pet_runtime.cancellable_io(io))
        self.assertTrue(entered.wait(2))
        self.runtime.interrupt()
        with self.assertRaises(pet_runtime.TurnCancelled):
            active.result(1)
        self.assertEqual(self.runtime.submit('voice', lambda: 'next').result(1), 'next')
        self.assertFalse(finished.is_set())
        release.set()
        self.assertTrue(finished.wait(2))
        self.assertEqual(seen, [])

    def test_io_timeout_exception_is_preserved(self):
        def io():
            raise TimeoutError('upstream timeout')

        with self.assertRaisesRegex(TimeoutError, 'upstream timeout'):
            self.runtime.submit('chat', lambda: pet_runtime.cancellable_io(io)).result(2)

    def test_cancelled_pending_future_can_be_interrupted(self):
        active, release = self.block()
        queued = self.runtime.submit('voice', lambda: self.fail('cancelled turn ran'))
        queued.cancel()
        self.runtime.interrupt()
        release.set()
        with self.assertRaises(pet_runtime.TurnCancelled):
            active.result(2)
        self.assertEqual(self.runtime.submit('chat', lambda: 'next').result(2), 'next')

    def test_cancelled_future_does_not_execute_or_stop_dispatcher(self):
        active, release = self.block()
        skipped = self.runtime.submit('chat', lambda: self.fail('cancelled future ran'))
        self.assertTrue(skipped.cancel())
        next_turn = self.runtime.submit('chat', lambda: 'next')
        release.set()
        active.result(2)
        self.assertEqual(next_turn.result(2), 'next')

    def test_stage_logs_share_turn_id_and_have_duration(self):
        def work():
            with pet_runtime.stage('model.stream'):
                pet_runtime.mark('model.first_chunk')

        self.runtime.submit('chat', work, turn_id='test-turn').result(2)
        rows = [json.loads(line) for line in self.path.read_text(encoding='utf-8').splitlines()]
        ended = next(row for row in rows if row['event'] == 'model.stream.end')
        self.assertEqual(ended['turn'], 'test-turn')
        self.assertGreaterEqual(ended['duration_ms'], 0)
        self.assertEqual(rows[0]['event'], 'dialogue.queued')

    def test_context_budget_retains_recent_complete_turns(self):
        history = [{'role': role, 'content': text * 100}
                   for text in ('甲', '乙', '丙', '丁')
                   for role in ('user', 'assistant')]
        messages = pet_runtime.dialogue_messages('persona', history, 'now', 'memory', budget=350)
        self.assertLessEqual(sum(pet_runtime.estimate_tokens(m['content']) for m in messages), 350)
        self.assertEqual(messages[-1]['content'], 'now')
        self.assertEqual(messages[2]['role'], 'user')
        self.assertEqual(messages[2]['content'], '丁' * 100)
        self.assertEqual(len(history), 8)

    def test_oversized_input_is_rejected_explicitly(self):
        with self.assertRaises(ValueError):
            pet_runtime.dialogue_messages('persona', [], '甲' * 2000, budget=1000)


if __name__ == '__main__':
    unittest.main()
