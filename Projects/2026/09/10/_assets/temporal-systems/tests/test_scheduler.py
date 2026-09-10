import random
import unittest
from scheduler import EventClock, PinnedCache, Scheduler, demo

class SchedulerTests(unittest.TestCase):
    def test_admission_finish_and_stale(self):
        for intent in ((1,'r1','public'), (0,'r2','public'), (0,'r1','revoked')):
            isolated = Scheduler()
            identity = isolated.submit('a',16,0)
            isolated.pump(0)
            isolated.intent = intent
            isolated.finish(identity,1)
            self.assertEqual(isolated.counters['stale'],1)
        count_limited = Scheduler(queue_limit=1)
        count_limited.submit('a',1,0)
        self.assertIsNone(count_limited.submit('b',1,0))
        self.assertEqual(count_limited.owned,1)
        s = Scheduler(byte_limit=512, queue_limit=2)
        first = s.submit('a',256,0)
        second = s.submit('b',256,0)
        self.assertIsNone(s.submit('c',1,0))
        s.pump(0)
        self.assertEqual(s.owned,512)  # Submission did not release either body.
        self.assertTrue(all(j.state == 'await_finish' for j in s.jobs.values()))
        s.intent = (1,'r2','private')
        s.finish(first,10)
        s.cancel(second,10)
        s.finish(second,20)
        self.assertEqual(s.counters['stale'],2)
        self.assertEqual(s.owned,0)
        self.assertFalse(s.finish(first,30))
        self.assertEqual(s.counters['disposed'],2)
        queued = s.submit('c',64,40)
        s.cancel(queued,40)
        self.assertEqual(s.counters['aborted'],1)
        self.assertEqual(s.owned,0)

    def test_backpressure_and_token_bound(self):
        s = Scheduler()
        blocked = s.submit('a',1024,0,blocked_until=500)
        s.submit('b',1024,0)
        for p in range(0,2001,10):
            s.pump(p)
            self.assertLessEqual(s.counters['bytes_submitted'],512+1024*p/1000)
            if p < 500:
                self.assertEqual(s.jobs[blocked].remaining,1024)
            for identity,j in list(s.jobs.items()):
                if j.state == 'await_finish':
                    s.finish(identity,p)
        self.assertEqual(s.owned,0)
        self.assertEqual(s.counters['published'],2)

    def test_cache_pins_and_clock_order(self):
        cache = PinnedCache(8)
        self.assertTrue(cache.install('a',8))
        release = cache.lease('a')
        self.assertFalse(cache.install('b',8))
        release(); release()
        self.assertTrue(cache.install('b',8))
        self.assertNotIn('a',cache.entries)
        events, clock = [], EventClock(limit=2)
        clock.at(1,lambda:events.append('a'))
        clock.at(1,lambda:events.append('b'))
        with self.assertRaises(ValueError):
            clock.at(2,lambda:None)
        clock.run(1)
        self.assertEqual(events,['a','b'])

    def test_seeded_terminal_ownership(self):
        for seed in range(20):
            rng,s = random.Random(seed),Scheduler(fail_every=3)
            for p in range(0,2000,20):
                if rng.random()<.4:
                    s.submit(str(rng.randrange(3)),rng.randrange(1,1025),p)
                if rng.random()<.1 and s.jobs:
                    s.cancel(rng.choice(list(s.jobs)),p)
                if rng.random()<.05:
                    s.intent=(p,'r1','changed')
                s.pump(p)
                for identity,j in list(s.jobs.items()):
                    if j.state == 'await_finish':
                        s.finish(identity,p+1)
                s.check()
            for identity in list(s.jobs):
                s.finish(identity,2000,aborted=True)
            self.assertEqual(s.owned,0)
            self.assertEqual(s.counters['admitted'],s.counters['disposed'])

    def test_useful_work_and_percentiles(self):
        result = demo()
        useful,starved = result['useful']['before_cleanup'],result['starved']['before_cleanup']
        self.assertEqual(useful['pump_callbacks'],starved['pump_callbacks'])
        self.assertEqual(useful['counters']['published'],4)
        self.assertEqual(starved['counters'].get('published',0),0)
        self.assertEqual(starved['owned'],4096)
        self.assertIsNone(starved['latency_p95_ms'])
        self.assertEqual(result['percentiles']['combined_p95'],100)
        self.assertNotEqual(result['percentiles']['average_p95'],100)

if __name__ == '__main__':
    unittest.main()
