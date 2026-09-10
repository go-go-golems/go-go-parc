"""Educational presentation policy, not a decoder or a browser security boundary.

Immutable transitions emit effects. The injected executor delays disposal so
revoked buffers remain identifiable while already ineligible for presentation.
Times are monotonic milliseconds; target/frame UTC is integer microseconds.
"""
from collections import Counter, deque
from dataclasses import asdict, dataclass, replace
from itertools import permutations
import json
from scheduler import EventClock


@dataclass(frozen=True)
class Token:
    session: str
    lifetime: int
    authority: int
    generation: int
    visibility: int
    media: str


@dataclass(frozen=True)
class State:
    phase: str = 'closed'
    session: str = ''
    lifetime: int = 0
    authority: int = 0
    generation: int = 0
    visibility: int = 0
    media: str = ''
    deadline: int = 0
    target: int = 0
    onscreen: bool = True
    document_visible: bool = True
    buffered: bool = False
    seek_done: bool = False
    accepted: int | None = None
    revealed: bool = False
    resources: tuple[str, ...] = ()

    def token(self):
        return Token(self.session, self.lifetime, self.authority,
                     self.generation, self.visibility, self.media)


@dataclass(frozen=True)
class Event:
    kind: str
    token: Token | None = None
    session: str = ''
    media: str = 'camera-1/epoch-0'
    utc: int | None = None
    deadline: int = 0
    value: bool = True
    mapped: bool = True
    ready: bool = True
    seeking: bool = False
    evidence: str = 'frame-callback'


TERMINAL = {'closed', 'expired', 'revoked', 'failed'}
KINDS = {'open', 'close', 'revoke', 'renew', 'seek', 'visibility', 'document',
         'buffer', 'seeked', 'frame', 'gap', 'unmapped', 'fail', 'tick'}


def terminate(state, reason):
    effects = [('conceal', reason), ('cancel', state.session)]
    effects += [('release', resource) for resource in state.resources]
    return replace(state, phase=reason, session='', resources=(), buffered=False,
                   seek_done=False, accepted=None, revealed=False,
                   generation=state.generation+1), effects


def transition(state, event, now):
    """Pure policy. Caller supplies trusted, typed fixture events and clock time.

    Deadline is exclusive. Expiration takes precedence over any same-time
    renewal/frame. Renewals need session/lifetime/authority identity, not the
    seek generation: seeking does not invalidate the session lease itself.
    """
    if event.kind not in KINDS:
        raise ValueError('unknown presentation event')
    effects = []
    if state.session and now >= state.deadline:
        state, effects = terminate(state, 'expired')
    if event.kind == 'tick':
        return state, effects
    if event.kind == 'close':
        if not state.session:
            return state, effects
        result, more = terminate(state, 'closed')
        return result, effects+more
    if event.kind == 'revoke':
        effects.append(('revoke-grants', str(state.authority)))
        if state.session:
            state, more = terminate(state, 'revoked'); effects += more
        return replace(state, authority=state.authority+1, phase='revoked'), effects
    if event.kind == 'open':
        if not event.session or event.deadline <= now or event.utc is None:
            return state, effects+[('reject', 'invalid admission')]
        if state.session:
            state, more = terminate(state, 'closed'); effects += more
        lifetime = state.lifetime+1
        resources = tuple(f'{lifetime}/{kind}' for kind in ('session','request','decoder','buffer'))
        state = replace(state, phase='loading', session=event.session,
                        lifetime=lifetime, generation=state.generation+1,
                        media=event.media, deadline=event.deadline, target=event.utc,
                        resources=resources, buffered=False, seek_done=False,
                        accepted=None, revealed=False)
        return state, effects+[('acquire', r) for r in resources]+[('fetch-start', event.session)]
    if not state.session:
        return state, effects+[('reject', 'no live session')]
    if event.kind == 'renew':
        old = event.token
        if (old is None or (old.session,old.lifetime,old.authority) !=
                (state.session,state.lifetime,state.authority) or event.deadline <= state.deadline):
            return state, effects+[('reject', 'renewal identity/deadline')]
        return replace(state, deadline=event.deadline), effects+[('renewed', state.session)]
    if event.kind == 'seek':
        if event.utc is None:
            return state, effects+[('reject', 'missing target')]
        return replace(state, phase='loading', target=event.utc,
                       generation=state.generation+1, accepted=None, revealed=False,
                       buffered=False, seek_done=False), effects+[('conceal','seek'), ('cancel','old seek')]
    if event.kind in {'visibility', 'document'}:
        key = 'onscreen' if event.kind == 'visibility' else 'document_visible'
        if getattr(state, key) == event.value:
            return state, effects
        state = replace(state, **{key:event.value}, visibility=state.visibility+1,
                        accepted=None, revealed=False, seek_done=False,
                        phase='loading' if event.value else 'hidden')
        return state, effects+[('conceal',event.kind),
                               ('resume' if state.onscreen and state.document_visible else 'stop',state.session)]
    if event.token != state.token():
        return state, effects+[('reject','obsolete evidence')]
    if event.kind == 'fail':
        result, more = terminate(state, 'failed')
        return result, effects+more
    if event.kind in {'gap','unmapped'}:
        return replace(state, phase=event.kind, generation=state.generation+1,
                       accepted=None, revealed=False, buffered=False, seek_done=False), effects+[('conceal',event.kind)]
    if event.kind == 'buffer':
        return replace(state, buffered=True), effects+[('buffered',state.session)]
    if event.kind == 'seeked':
        return replace(state, seek_done=True), effects+[('seek-completed',state.session)]
    if event.kind == 'frame':
        eligible = (state.phase not in {'gap','unmapped','hidden'}
                    and state.onscreen and state.document_visible and state.buffered and state.seek_done
                    and event.mapped and event.ready and not event.seeking
                    and event.evidence == 'frame-callback' and event.utc is not None
                    and abs(event.utc-state.target) <= 150_000)
        if not eligible:
            return state, effects+[('reject','frame predicate')]
        return replace(state, phase='admitted', accepted=event.utc, revealed=True), effects+[('reveal',str(event.utc))]
    raise AssertionError('event dispatch incomplete')


class Machine:
    """Bounded deterministic effect executor. Logical slots, not byte/RSS counts.

    At most 16 owned resources, 256 queued events (shared EventClock), 256
    retained trace rows, and 64 released-resource identities. Delayed release
    takes two model milliseconds. It is not a browser disposal latency claim.
    Callers must stay within event admission; overflow raises before committing
    a transition. This fixture executor is not a production revocation service.
    Open is trusted completed admission, not an asynchronous server response.
    """
    def __init__(self):
        self.clock = EventClock()
        self.state = State()
        self.owned = set()
        self.releases = Counter()
        self.trace = deque(maxlen=256)

    def send(self, event):
        if event.kind == 'open' and (len(self.owned)+4 > 16 or len(self.releases)+len(self.owned)+4 > 64):
            raise ValueError('model resource admission exceeded')
        old = self.state
        candidate, effects = transition(old, event, self.clock.now)
        timer = bool(candidate.session and
                     (candidate.lifetime != old.lifetime or candidate.deadline != old.deadline))
        needed = sum(kind == 'release' for kind, _ in effects) + int(timer)
        if len(self.clock.events)+needed > self.clock.limit:
            raise ValueError('model effect queue admission exceeded')
        self.state = candidate
        for kind, resource in effects:
            if kind == 'acquire':
                assert resource not in self.owned and resource not in self.releases
                self.owned.add(resource)
            elif kind == 'release':
                self.clock.at(self.clock.now+2, lambda r=resource:self.dispose(r))
        if timer:
            self.clock.at(self.state.deadline, lambda:self.send(Event('tick')))
        self.trace.append({'ms':self.clock.now, 'input':asdict(event),
                           'state':asdict(self.state), 'effects':effects,
                           'owned':sorted(self.owned)})
        self.check()

    def dispose(self, resource):
        assert resource in self.owned and not self.releases[resource]
        self.owned.remove(resource)
        self.releases[resource] += 1
        self.trace.append({'ms':self.clock.now,'disposed':resource,'owned':sorted(self.owned)})
        self.check()

    def check(self):
        s = self.state
        assert len(self.owned) <= 16
        assert all(count == 1 for count in self.releases.values())
        if s.phase in TERMINAL:
            assert not s.revealed and s.accepted is None and not s.resources
        if s.revealed:
            assert s.session and s.onscreen and s.document_visible and s.buffered and s.seek_done
            assert s.accepted is not None and abs(s.accepted-s.target) <= 150_000
            assert self.clock.now < s.deadline
        assert set(s.resources) <= self.owned

    def later(self, when, event):
        self.clock.at(when, lambda:self.send(event))

    def snapshot(self):
        return {'state':asdict(self.state), 'owned':sorted(self.owned),
                'pending_events':len(self.clock.events),
                'release_counts':dict(self.releases), 'trace':list(self.trace)}


def opened():
    machine = Machine()
    machine.send(Event('open', session='S1', utc=1_000_000, deadline=100))
    return machine


def races():
    closed = opened(); token = closed.state.token()
    closed.later(10, Event('close'))
    closed.later(11, Event('seeked', token))
    closed.later(11, Event('frame', token, utc=1_000_000))
    closed.clock.run(102)
    revoked = opened(); token = revoked.state.token()
    revoked.send(Event('buffer', token)); revoked.send(Event('seeked', token))
    revoked.send(Event('frame', token, utc=1_000_000))
    revoked.later(10, Event('revoke'))
    revoked.later(11, Event('frame', token, utc=1_000_000))
    revoked.clock.run(102)
    return {'seek-after-close':closed.snapshot(), 'buffered-at-revocation':revoked.snapshot()}


def permutation_check():
    """Exhaust all 120 orders of five selected same-time events, not all programs."""
    count = 0
    for order in permutations(('buffer','seeked','frame','revoke','close')):
        machine = opened(); token = machine.state.token()
        for kind in order:
            machine.later(10, Event(kind, token, utc=1_000_000))
        machine.clock.run(102)
        machine.check()
        assert not machine.state.revealed and not machine.owned
        assert len(machine.releases) == 4
        count += 1
    return {'permutations':count,'invariant_violations':0,
            'scope':'five events at ms 10, insertion order; not a proof for arbitrary executions'}


if __name__ == '__main__':
    print(json.dumps({'kind':'educational-presentation-policy', 'races':races(),
                      'permutation_check':permutation_check()}, indent=2))
