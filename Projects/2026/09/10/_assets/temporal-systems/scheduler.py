"""Educational bounded scheduler. All time and transport events are injected.

Bodies reserve their entire declared size until finish/abort, even after all
bytes have been submitted. Reservation is logical ownership, not RSS. No actual
network sockets, Python body allocation or production authorization is modeled.
"""
from collections import Counter, OrderedDict, deque
from dataclasses import dataclass
from fractions import Fraction
import heapq
import json
import math

class EventClock:
    def __init__(self, limit=256):
        self.now = 0
        self.serial = 0
        self.events = []
        self.limit = limit

    def at(self, when, callback):
        if when < self.now or len(self.events) >= self.limit:
            raise ValueError('event-clock admission exceeded')
        self.serial += 1
        heapq.heappush(self.events, (when, self.serial, callback))

    def run(self, until):
        if until < self.now:
            raise ValueError('time reversal')
        while self.events and self.events[0][0] <= until:
            self.now, _, callback = heapq.heappop(self.events)
            callback()
        self.now = until


@dataclass
class Job:
    identity: int
    key: str
    generation: int
    revision: str
    authority: str
    size: int
    remaining: int
    submitted: int
    eligible_at: int
    blocked_until: int
    state: str = 'queued'
    cancelled: bool = False
    fail: bool = False


class Scheduler:
    def __init__(self, *, rate=1024, burst=512, byte_limit=8192, queue_limit=4,
                 global_limit=2, per_key=1, fail_every=0):
        if min(rate, burst, byte_limit, queue_limit, global_limit, per_key) <= 0:
            raise ValueError('positive limits required')
        if fail_every == 1 or fail_every < 0:
            raise ValueError('failure interval must be zero or at least two')
        self.rate, self.burst = rate, burst
        self.tokens, self.refilled_at = Fraction(burst), 0
        self.byte_limit, self.queue_limit = byte_limit, queue_limit
        self.global_limit, self.per_key, self.fail_every = global_limit, per_key, fail_every
        self.intent = (0, 'r1', 'public')
        self.jobs, self.queue, self.active = {}, [], []
        self.owned = self.ordinal = self.rotation = 0
        self.counters = Counter()
        self.trace = deque(maxlen=256)
        self.latencies = deque(maxlen=64)
        self.high_water = 0

    def record(self, now, kind, **fields):
        self.trace.append({'p_ms': now, 'kind': kind, **fields})

    def submit(self, key, size, now, *, latency=0, blocked_until=0):
        self.ordinal += 1
        if size <= 0 or self.owned+size > self.byte_limit or len(self.queue) >= self.queue_limit:
            self.counters['rejected'] += 1
            self.record(now, 'rejected', ordinal=self.ordinal)
            return None
        identity = self.ordinal
        g, r, a = self.intent
        job = Job(identity, key, g, r, a, size, size, now, now+latency, blocked_until,
                  fail=bool(self.fail_every and identity % self.fail_every == 0))
        self.jobs[identity] = job
        self.queue.append(identity)
        self.owned += size
        self.high_water = max(self.high_water, self.owned)
        self.counters['admitted'] += 1
        self.record(now, 'admitted', identity=identity, size=size)
        return identity

    def cancel(self, identity, now):
        job = self.jobs.get(identity)
        if job is None or job.cancelled:
            return
        job.cancelled = True
        self.counters['cancel_requested'] += 1
        if job.state == 'queued':
            self.finish(identity, now, aborted=True)
        # Active work models an operation whose cancellation is not immediate.
        # Completion still checks eligibility. An explicit abort can end it sooner.

    def finish(self, identity, now, aborted=False):
        job = self.jobs.get(identity)
        if job is None:
            return False
        if not aborted and job.state != 'await_finish':
            raise ValueError('transport has not submitted its complete body')
        if identity in self.queue:
            self.queue.remove(identity)
        if identity in self.active:
            self.active.remove(identity)
        del self.jobs[identity]
        self.owned -= job.size
        self.counters['disposed'] += 1
        if aborted:
            outcome = 'aborted'
        elif job.fail:
            outcome = 'failed'
        else:
            self.counters['completed'] += 1
            self.latencies.append(now-job.submitted)
            outcome = 'published' if (not job.cancelled and
                       (job.generation, job.revision, job.authority) == self.intent) else 'stale'
        self.counters[outcome] += 1
        self.record(now, outcome, identity=identity, owned=self.owned)
        return True

    def pump(self, now):
        if now < self.refilled_at:
            raise ValueError('time reversal')
        self.tokens = min(Fraction(self.burst), self.tokens+Fraction((now-self.refilled_at)*self.rate,1000))
        self.refilled_at = now
        for identity in list(self.queue):
            job = self.jobs[identity]
            keys = Counter(self.jobs[x].key for x in self.active)
            if len(self.active) < self.global_limit and keys[job.key] < self.per_key and now >= job.eligible_at:
                self.queue.remove(identity)
                self.active.append(identity)
                job.state = 'active'
                self.record(now, 'started', identity=identity)
        if self.active:
            start = self.rotation % len(self.active)
            order = self.active[start:]+self.active[:start]
            self.rotation += 1
            for identity in order:
                job = self.jobs[identity]
                if job.state != 'active' or now < job.blocked_until:
                    continue
                amount = min(256, job.remaining, int(self.tokens))
                if amount:
                    job.remaining -= amount
                    self.tokens -= amount
                    self.counters['bytes_submitted'] += amount
                if not job.remaining:
                    job.state = 'await_finish'
                    self.record(now, 'body-submitted', identity=identity, owned=self.owned)
        self.check()

    def check(self):
        assert 0 <= self.owned <= self.byte_limit
        assert self.owned == sum(j.size for j in self.jobs.values())
        assert len(self.queue) <= self.queue_limit and len(self.active) <= self.global_limit
        assert all(n <= self.per_key for n in Counter(self.jobs[x].key for x in self.active).values())
        assert len(self.jobs) == len(self.queue)+len(self.active)
        assert 0 <= self.tokens <= self.burst


class PinnedCache:
    def __init__(self, budget):
        self.budget = budget
        self.entries = OrderedDict()

    @property
    def owned(self):
        return sum(size for size, _ in self.entries.values())

    def install(self, key, size):
        if key in self.entries or size <= 0 or size > self.budget:
            return False
        candidates = [k for k, (_, pins) in self.entries.items() if pins == 0]
        reclaim = sum(self.entries[k][0] for k in candidates)
        if self.owned+size-reclaim > self.budget:
            return False  # Refuse atomically when pinned bytes prevent admission.
        while self.owned+size > self.budget:
            del self.entries[candidates.pop(0)]
        self.entries[key] = [size, 0]
        return True

    def lease(self, key):
        self.entries.move_to_end(key)
        self.entries[key][1] += 1
        released = False
        def release():
            nonlocal released
            if not released:
                self.entries[key][1] -= 1
                released = True
        return release


def percentile(values, percent):
    """Nearest-rank percentile; caller specifies the cohort."""
    return sorted(values)[math.ceil(len(values)*percent/100)-1] if values else None


def experiment(starved=False):
    clock, scheduler = EventClock(), Scheduler()
    for key in ('a','b','c','d'):
        scheduler.submit(key, 1024, 0, blocked_until=100_000 if starved else 0)
    # The same 61 pump callbacks happen in both cohorts.
    for now in range(0,6001,100):
        def tick():
            scheduler.pump(clock.now)
            for identity, job in list(scheduler.jobs.items()):
                if job.state == 'await_finish':
                    clock.at(clock.now+50, lambda identity=identity: scheduler.finish(identity, clock.now))
        clock.at(now,tick)
    clock.run(6050)
    before = {'counters':dict(scheduler.counters), 'owned':scheduler.owned,
              'latency_p95_ms':percentile(scheduler.latencies,95), 'pump_callbacks':61,
              'high_water_owned':scheduler.high_water}
    for identity in list(scheduler.jobs):
        scheduler.finish(identity, clock.now, aborted=True)
    scheduler.check()
    return {'kind':'educational-starved' if starved else 'educational-useful',
            'before_cleanup':before, 'after_cleanup_owned':scheduler.owned,
            'terminal_counters':dict(scheduler.counters), 'trace':list(scheduler.trace)}


def demo():
    a, b = [0]*100, [100]*100
    return {'useful':experiment(), 'starved':experiment(True),
            'percentiles':{'window_p95':[percentile(a,95),percentile(b,95)],
                           'average_p95':50, 'combined_p95':percentile(a+b,95)}}

if __name__ == '__main__':
    print(json.dumps(demo(),indent=2))
