import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pet_memory import PetMemory


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.memory = PetMemory({'use_embedding': False}, self.temp.name)
        self.addCleanup(self.memory.close)

    def extraction(self, response):
        entered, release, finished = (threading.Event() for _ in range(3))
        self.addCleanup(release.set)
        original = self.memory._extract

        def extract(*args, **kwargs):
            try:
                return original(*args, **kwargs)
            finally:
                finished.set()

        self.memory._extract = extract

        def complete(*args, **kwargs):
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test timed out')
            return json.dumps(response, ensure_ascii=False)

        return SimpleNamespace(raw_complete=complete), entered, release, finished

    def test_disabled_memory_excludes_history_and_summary(self):
        self.memory.record_turn('hello', 'reply')
        self.memory.summary = 'previous context'
        self.memory.enabled = False
        self.assertEqual(self.memory.dialogue_context('new input'), ([], None))

    def test_record_turn_returns_while_extraction_is_still_running(self):
        client, entered, release, finished = self.extraction({'facts': [], 'summary': '讨论新任务'})
        returned = threading.Event()

        def record():
            self.memory.record_turn('新任务', '好的', extract=True, chat_client=client)
            returned.set()

        threading.Thread(target=record, daemon=True).start()
        self.assertTrue(returned.wait(1))
        self.assertTrue(entered.wait(2))
        self.assertFalse(finished.is_set())
        self.assertEqual(len(self.memory.short_term_messages()), 2)
        release.set()
        self.assertTrue(finished.wait(2))

    def test_embedding_request_does_not_hold_memory_lock(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)

        def embed(*args, **kwargs):
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test timed out')
            return [[1.0, 0.0]]

        self.memory._embed = SimpleNamespace(embed=embed)
        self.memory._embed_ok = True
        client, _, raw_release, finished = self.extraction(
            {'facts': [{'content': '用户喜欢咖啡', 'importance': 4}], 'summary': '喝咖啡'})
        raw_release.set()
        self.memory.record_turn('咖啡', '好的', extract=True, chat_client=client)
        self.assertTrue(entered.wait(2))
        acquired = self.memory._lock.acquire(timeout=0.2)
        self.assertTrue(acquired)
        if acquired:
            self.memory._lock.release()
        self.assertTrue(Path(self.memory.summary_path).exists())
        release.set()
        self.assertTrue(finished.wait(2))

    def test_clear_during_extraction_does_not_restore_old_memories(self):
        client, entered, release, finished = self.extraction(
            {'facts': [{'content': '旧事实', 'importance': 4}], 'summary': '旧摘要'})
        self.memory.record_turn('旧对话', '好的', extract=True, chat_client=client)
        self.assertTrue(entered.wait(2))
        self.memory.clear()
        release.set()
        self.assertTrue(finished.wait(2))
        self.assertEqual(self.memory.long_term_entries(), [])
        self.assertEqual(self.memory.short_term_messages(), [])
        self.assertEqual(self.memory.summary, '')

    def test_summary_survives_restart(self):
        self.memory.summary = '还要继续讨论房子的设计'
        self.memory._save_snapshot(self.memory.summary_path, 'summary')
        restored = PetMemory({}, self.temp.name)
        self.addCleanup(restored.close)
        _, note = restored.dialogue_context('房子')
        self.assertIn('还要继续讨论房子的设计', note)

    def test_similar_opposite_facts_are_not_merged(self):
        self.memory._merge_fact('用户喜欢喝咖啡', 3, 'chat')
        self.memory._merge_fact('用户不喜欢喝咖啡', 4, 'voice')
        entries = self.memory.long_term_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]['source'], 'voice')
        self.assertNotEqual(entries[0]['id'], entries[1]['id'])

    def test_recall_does_not_rewrite_fact_observation_time(self):
        self.memory._merge_fact('用户喜欢喝咖啡', 3)
        self.memory.long_term[0]['updated_at'] = 1234567890
        self.assertIn('咖啡', self.memory.recall('咖啡'))
        self.assertEqual(self.memory.long_term[0]['updated_at'], 1234567890)

    def test_embedding_failure_falls_back_with_short_timeout(self):
        self.memory._merge_fact('用户喜欢喝咖啡', 3)
        self.memory.long_term[0]['embedding'] = [1, 0]
        self.memory._embed_ok = True
        self.memory.cfg['use_embedding'] = True
        timeouts = []

        def fail(texts, timeout):
            timeouts.append(timeout)
            raise TimeoutError()

        self.memory._embed = SimpleNamespace(embed=fail)
        self.assertIn('咖啡', self.memory.recall('咖啡'))
        self.assertIn('咖啡', self.memory.recall('咖啡'))
        self.assertEqual(timeouts, [2])


if __name__ == '__main__':
    unittest.main()
