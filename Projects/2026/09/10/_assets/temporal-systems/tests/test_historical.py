import unittest
from historical import BASE, HistoricalCoordinator, scenario
from scheduler import EventClock

class HistoricalTests(unittest.TestCase):
    def test_full_archive_scenario(self):
        result=scenario()
        self.assertEqual(result['stats']['created'],2)
        self.assertEqual(result['stats']['released'],2)
        self.assertEqual(result['stats']['reused'],2)
        self.assertGreaterEqual(result['stats']['stale_reports'],3)
        self.assertEqual(result['remaining_events'],0)
        self.assertTrue(all(e['state']=='covered-retry' for e in result['archive_recovery']['paused']))
        self.assertEqual(result['archive_recovery']['concealed-progress'][0]['state'],'visible')
        deadline=next(e for e in result['trace'] if e['kind']=='barrier-release')
        self.assertEqual(deadline['reason'],'deadline')
        self.assertEqual(deadline['missing'],[2])
        self.assertTrue(any(e['kind']=='ready' and e['camera']==2 and e['p_ms']==2600 for e in result['trace']))
        self.assertTrue(any(e['kind']=='gap' and e['camera']==4 for e in result['trace']))
        checkpoints=[e for e in result['trace'] if e['kind']=='checkpoint']
        self.assertTrue(any(p['camera']==4 and p['epoch']=='camera-4-epoch-1' and p['visible']
                            for e in checkpoints for p in e['players']))
        for event in checkpoints:
            for player in event['players']:
                self.assertTrue(player['rate'] in (0.95,1,1.05,2))
        delayed=[e for e in result['trace'] if e['kind']=='observation' and e['camera']==3 and e['p_ms']>e['observed_at']]
        self.assertTrue(delayed)
        for e in delayed:
            self.assertEqual(e['drift_ms'],(e['utc']-e['target_at_observation'])/1000)

    def test_session_window_and_late_readiness(self):
        clock=EventClock();coordinator=HistoricalCoordinator(clock)
        coordinator.commit_seek(BASE,initial=True)
        first=coordinator.session['id']
        clock.run(100)
        coordinator.commit_seek(BASE+1_000_000)
        self.assertEqual(coordinator.session['id'],first)
        clock.run(3000)
        self.assertGreater(coordinator.stats['stale_reports'],0)
        coordinator.commit_seek(BASE+12_000_000)
        self.assertNotEqual(coordinator.session['id'],first)
        coordinator.close();clock.run(4000)
        self.assertEqual(coordinator.stats['created'],coordinator.stats['released'])
        self.assertTrue(all(p.utc is None for p in coordinator.players.values()))

    def test_continuity(self):
        clock=EventClock();c=HistoricalCoordinator(clock)
        c.commit_seek(BASE)
        clock.run(300);c.tick()
        clock.run(1000)
        before=c.master.now(clock.now);c.change(rate=2)
        self.assertEqual(c.master.now(clock.now),before)
        clock.run(1500);c.change(running=False)
        paused=c.master.now(clock.now)
        clock.run(2000);self.assertEqual(c.master.now(clock.now),paused)
        c.change(running=True)
        self.assertEqual(c.master.now(clock.now),paused)
        c.close()

if __name__=='__main__':unittest.main()
