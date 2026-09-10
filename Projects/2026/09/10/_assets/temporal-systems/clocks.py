"""Educational deterministic clock/control model, not browser measurement.

All controller observations are instantaneous in the generic scenario. Seek
completion and initial decoding are delayed separately. Event time is injected
integer milliseconds; UTC is integer microseconds; media time is float seconds.
"""
from dataclasses import dataclass
from fractions import Fraction
import json


@dataclass(frozen=True)
class Epoch:
    identity: str
    utc_start: int
    utc_end: int
    media_start: float = 0.0

    def __post_init__(self):
        if self.utc_end <= self.utc_start:
            raise ValueError('empty epoch')

    def local(self, utc):
        return self.media_start + (utc - self.utc_start) / 1_000_000


class ClockMap:
    def __init__(self, epochs):
        self.epochs = sorted(epochs, key=lambda e: e.utc_start)
        if len({e.identity for e in self.epochs}) != len(self.epochs):
            raise ValueError('duplicate epoch identity')
        if any(a.utc_end > b.utc_start for a, b in zip(self.epochs, self.epochs[1:])):
            raise ValueError('ambiguous UTC coverage')

    def to_media(self, utc):
        for e in self.epochs:
            if e.utc_start <= utc < e.utc_end:
                return e.identity, e.local(utc)
        return None

    def to_utc(self, identity, media):
        for e in self.epochs:
            if e.identity == identity and e.media_start <= media < e.local(e.utc_end):
                return min(e.utc_end - 1, e.utc_start + round((media - e.media_start) * 1_000_000))
        return None


def ticks_to_utc(utc_anchor, tick, tick_anchor, timescale):
    if timescale <= 0:
        raise ValueError('positive timescale required')
    return utc_anchor + round(Fraction((tick-tick_anchor)*1_000_000, timescale))


class MasterClock:
    def __init__(self, utc, now_ms=0, rate=1):
        self.anchor, self.at, self.rate = utc, now_ms, Fraction(rate)
        self.running = True

    def now(self, p):
        if p < self.at:
            raise ValueError('monotonic time went backwards')
        return self.anchor + (round((p-self.at)*1000*self.rate) if self.running else 0)

    def configure(self, p, *, rate=None, running=None, seek=None):
        current = self.now(p)
        if rate is not None and not 0 < Fraction(rate) <= 4:
            raise ValueError('supported positive rate required')
        self.anchor, self.at = current if seek is None else seek, p
        if rate is not None:
            self.rate = Fraction(rate)
        if running is not None:
            self.running = running


class DriftController:
    def __init__(self):
        self.excess_since = None

    def decide(self, p, drift_ms, master_rate=1):
        if drift_ms is None:
            self.excess_since = None
            return 'unknown', master_rate
        if abs(drift_ms) <= 200:
            self.excess_since = None
            if abs(drift_ms) <= 50 or master_rate != 1:
                return 'normal', master_rate
            return 'rate', 0.95 if drift_ms > 0 else 1.05
        if self.excess_since is None:
            self.excess_since = p
        if p-self.excess_since >= 500:
            self.excess_since = None
            return 'seek', master_rate
        return 'wait', master_rate


class Barrier:
    def __init__(self, generation, members, start_ms, timeout_ms=2000):
        self.generation = generation
        self.members = frozenset(members)
        self.ready = set()
        self.deadline = start_ms + timeout_ms
        self.released = False

    def arrive(self, generation, member):
        if generation == self.generation and member in self.members and not self.released:
            self.ready.add(member)

    def poll(self, p):
        if self.released:
            return None
        if self.ready == self.members or p >= self.deadline:
            self.released = True
            return {'reason': 'ready' if self.ready == self.members else 'deadline',
                    'ready': sorted(self.ready), 'missing': sorted(self.members-self.ready)}
        return None


def moving_target(repaired):
    """Seek application takes 120 ms; initial decode takes another 200 ms.

    Broken policy pauses between application and decode and retries against a
    moving master. Repaired policy progresses at 1x behind cover during decode.
    This deliberately selected model proves neither policy works for all delays.
    """
    attempts, now = 0, 0
    trace = []
    while attempts < 5:
        target = now
        applied, decoded = now+120, now+320
        frame_ms = target + (decoded-applied if repaired else 0)
        drift = frame_ms-decoded
        visible = abs(drift) <= 150
        trace.append({'attempt': attempts+1, 'request_ms': now, 'decoded_ms': decoded,
                      'frame_ms': frame_ms, 'drift_ms': drift, 'visible': visible})
        attempts += 1
        if visible:
            break
        now = decoded
    return trace


def simulate_four():
    """Four processors, 20 ms ticks, 14 s run; observations have no extra lag.

    Camera 3 resets its media timestamp at UTC+8 s; camera 4 has a gap [6,8).
    Camera 2 has a 400 ms stall [4,4.4). Requested seek delay is at most
    120 ms; completion is polled on subsequent 20 ms ticks (zero becomes 20). Frames progress behind the cover while initial decoding completes.
    Trace retains state transitions and 500 ms observations, not every tick.
    """
    anchor = 1_788_912_000_000_000
    master = MasterClock(anchor)
    maps = [ClockMap([Epoch('continuous', anchor, anchor+20_000_000)]) for _ in range(2)]
    maps += [ClockMap([Epoch('before', anchor, anchor+8_000_000),
                       Epoch('reset', anchor+8_000_000, anchor+20_000_000)]),
             ClockMap([Epoch('before', anchor, anchor+6_000_000),
                       Epoch('after-gap', anchor+8_000_000, anchor+20_000_000)])]
    players = [dict(epoch=None, media=0., rate=1., pending=None, decode_at=0,
                    controller=DriftController(), visible=False, status=None,
                    seeks=0, unknown_ticks=0, max_abs_drift_ms=0., rate_changes=0)
               for _ in range(4)]
    delays = [0, 80, 120, 40]
    barrier, trace = Barrier(1, range(4), 0), []
    for p in range(0, 14_001, 20):
        target = master.now(p)
        for i, (mapping, player) in enumerate(zip(maps, players)):
            if p and player['epoch'] is not None and not (i == 1 and 4000 <= p < 4400):
                player['media'] += .02*player['rate']
            desired = mapping.to_media(target)
            if desired is None:
                player['epoch'], player['pending'], player['visible'] = None, None, False
                player['controller'].decide(p, None)
                player['unknown_ticks'] += 1
                status, drift = 'gap', None
            else:
                if player['pending'] is not None and p >= player['pending'][0]:
                    _, player['epoch'], player['media'] = player['pending']
                    player['pending'] = None
                    player['decode_at'] = p+200
                observed = mapping.to_utc(player['epoch'], player['media'])
                drift = None if observed is None else (observed-target)/1000
                action, rate = player['controller'].decide(p, drift)
                if player['pending'] is None and (player['epoch'] != desired[0] or action == 'seek'):
                    player['pending'] = (p+delays[i], *desired)
                    player['visible'] = False
                    player['seeks'] += 1
                if rate != player['rate']:
                    player['rate_changes'] += 1
                player['rate'] = rate
                # This educational model enforces its cover predicate every tick;
                # the product's reveal gate is not that continuous invariant.
                player['visible'] = (player['pending'] is None and p >= player['decode_at']
                                     and drift is not None and abs(drift) <= 150)
                status = 'visible' if player['visible'] else 'covered'
                if player['visible']:
                    barrier.arrive(1, i)
                if drift is not None:
                    player['max_abs_drift_ms'] = max(player['max_abs_drift_ms'], abs(drift))
            if status != player['status'] or p % 500 == 0:
                trace.append({'p_ms': p, 'player': i+1, 'status': status,
                              'epoch': player['epoch'], 'media_s': round(player['media'], 6),
                              'drift_ms': None if drift is None else round(drift, 3),
                              'rate': player['rate']})
                player['status'] = status
        released = barrier.poll(p)
        if released:
            trace.append({'p_ms': p, 'barrier': released})
    return {'kind': 'educational-discrete-simulation', 'step_ms': 20, 'duration_ms': 14000,
            'observation_delay_ms': 0, 'seek_delays_ms': delays,
            'decode_after_seek_ms': 200,
            'summary': [{k: player[k] for k in ('seeks', 'unknown_ticks', 'max_abs_drift_ms',
                                               'rate_changes', 'visible')} for player in players],
            'trace': trace, 'moving_target_broken': moving_target(False),
            'moving_target_repaired': moving_target(True)}


if __name__ == '__main__':
    print(json.dumps(simulate_four(), indent=2))
