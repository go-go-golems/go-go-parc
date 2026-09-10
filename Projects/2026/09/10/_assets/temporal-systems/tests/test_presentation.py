from dataclasses import replace
import unittest
from presentation import Event, State, opened, permutation_check, races, transition


class PresentationTests(unittest.TestCase):
    def ready(self, machine):
        token = machine.state.token()
        machine.send(Event('buffer', token))
        machine.send(Event('seeked', token))
        return token

    def test_named_races_and_release_ledger(self):
        for name, result in races().items():
            with self.subTest(name=name):
                self.assertFalse(result['state']['revealed'])
                self.assertIsNone(result['state']['accepted'])
                self.assertEqual(result['owned'], [])
                self.assertEqual(result['pending_events'], 0)
                self.assertEqual(list(result['release_counts'].values()), [1]*4)
                late = [row for row in result['trace'] if row.get('ms') == 11]
                self.assertTrue(late)
                self.assertTrue(all(len(row['owned']) == 4 for row in late))
                self.assertTrue(all(not row['state']['revealed'] for row in late))
        revoked = races()['buffered-at-revocation']['trace']
        self.assertTrue(any(row.get('state', {}).get('revealed') for row in revoked))

    def test_every_identity_and_evidence_predicate(self):
        machine = opened(); token = self.ready(machine)
        for key, value in [('session','foreign'), ('lifetime',999), ('authority',999),
                           ('generation',999), ('visibility',999), ('media','other-camera')]:
            machine.send(Event('frame', replace(token, **{key:value}), utc=1_000_000))
            self.assertIsNone(machine.state.accepted, key)
        for kwargs in [{'mapped':False}, {'ready':False}, {'seeking':True},
                       {'evidence':'currentTime'}, {'evidence':'seeked'}]:
            machine.send(Event('frame', token, utc=1_000_000, **kwargs))
            self.assertFalse(machine.state.revealed)
        machine.send(Event('frame', token, utc=1_150_001))
        self.assertFalse(machine.state.revealed)
        machine.send(Event('frame', token, utc=1_150_000))
        self.assertTrue(machine.state.revealed)
        self.assertEqual(machine.state.accepted, 1_150_000)
        machine.send(Event('frame', replace(token, authority=999), utc=1_000_001))
        self.assertEqual(machine.state.accepted, 1_150_000)
        self.assertTrue(machine.state.revealed)  # Rejection isn't a fresh revocation.

    def test_old_seek_same_target_and_visibility_round_trip(self):
        machine = opened(); old = self.ready(machine)
        machine.send(Event('seek', utc=1_000_000))
        machine.send(Event('seeked', old))
        self.assertFalse(machine.state.seek_done)
        token = self.ready(machine)
        machine.send(Event('frame', token, utc=1_000_000))
        for kind in ('visibility', 'document'):
            old = machine.state.token()
            machine.send(Event(kind, value=False))
            machine.send(Event('frame', old, utc=1_000_000))
            self.assertFalse(machine.state.revealed)
            machine.send(Event(kind, value=True))
            machine.send(Event('frame', old, utc=1_000_000))
            self.assertFalse(machine.state.revealed)
            token = self.ready(machine)
            machine.send(Event('frame', token, utc=1_000_000))
            self.assertTrue(machine.state.revealed)

    def test_renewal_expiry_replacement_and_idempotent_close(self):
        machine = opened(); old = machine.state.token()
        machine.send(Event('seek', utc=2_000_000))
        machine.send(Event('renew', old, deadline=120))  # Seek doesn't replace lease.
        self.assertEqual(machine.state.deadline, 120)
        machine.send(Event('open', session='S1', utc=1_000_000, deadline=130))
        machine.send(Event('renew', old, deadline=999))  # Same name, new lifetime.
        self.assertEqual(machine.state.deadline, 130)
        current = machine.state.token()
        machine.later(130, Event('renew', current, deadline=999))
        machine.later(130, Event('seeked', current))
        machine.clock.run(132)
        self.assertEqual(machine.state.phase, 'expired')
        self.assertFalse(machine.owned)
        self.assertEqual(len(machine.releases), 8)
        machine.send(Event('close')); machine.send(Event('close'))
        self.assertTrue(all(n == 1 for n in machine.releases.values()))
        self.assertFalse(machine.clock.events)

    def test_gap_unmapped_failure_and_pure_transition(self):
        original = State()
        new, effects = transition(original, Event('open', session='S', utc=0, deadline=5), 0)
        self.assertEqual(original, State())
        self.assertEqual(new.phase, 'loading')
        self.assertEqual(sum(kind == 'acquire' for kind, _ in effects), 4)
        for kind in ('gap', 'unmapped', 'fail'):
            machine = opened(); token = self.ready(machine)
            machine.send(Event(kind, token))
            machine.send(Event('frame', token, utc=1_000_000))
            self.assertIsNone(machine.state.accepted)
            self.assertEqual(machine.state.phase, 'failed' if kind == 'fail' else kind)
            machine.send(Event('close')); machine.clock.run(102)
            self.assertFalse(machine.owned)
            self.assertFalse(machine.clock.events)

    def test_bounded_permutations_and_admission(self):
        self.assertEqual(permutation_check()['permutations'], 120)
        machine = opened()
        for i in range(3):
            machine.send(Event('open', session=f'S{i+2}', utc=0, deadline=100))
        state = machine.state
        with self.assertRaisesRegex(ValueError, 'admission'):
            machine.send(Event('open', session='overflow', utc=0, deadline=100))
        self.assertEqual(machine.state, state)
        machine.send(Event('close')); machine.clock.run(102)
        self.assertEqual(len(machine.releases), 16)
        self.assertFalse(machine.owned)
        full = opened()
        while len(full.clock.events) < full.clock.limit:
            full.clock.at(1, lambda:None)
        state = full.state
        with self.assertRaisesRegex(ValueError, 'effect queue'):
            full.send(Event('renew', state.token(), deadline=200))
        self.assertEqual(full.state, state)
        full.clock.run(1)
        full.send(Event('close')); full.clock.run(102)
        self.assertFalse(full.owned)


if __name__ == '__main__':
    unittest.main()
