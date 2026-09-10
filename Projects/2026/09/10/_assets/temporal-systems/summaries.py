"""Educational mergeable summaries; stable variance is not product code.

Merge inputs must represent disjoint observations. Identity is (UTC, unique id);
retries must be deduplicated before reduction. No bounded summary can infer this
precondition from only extrema/counts. Coverage is separately supplied evidence.
"""
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from math import fsum, isfinite
import json
import statistics

@dataclass(frozen=True, order=True)
class Observation:
    utc: int
    identity: int
    value: float

@dataclass(frozen=True)
class Summary:
    n: int = 0
    total: float = 0.0
    mean: float = 0.0
    m2: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    first: Observation | None = None
    last: Observation | None = None

    def variance(self, sample=False):
        denominator = self.n - int(sample)
        return self.m2 / denominator if denominator > 0 else None


def leaf(utc, identity, value):
    if value is None:
        return Summary()
    if not isfinite(value):
        raise ValueError('non-finite observation')
    observation = Observation(utc, identity, float(value))
    return Summary(1, float(value), float(value), 0., float(value), float(value), observation, observation)


def merge(a, b):
    if not a.n:
        return b
    if not b.n:
        return a
    n = a.n+b.n
    delta = b.mean-a.mean
    mean = a.mean+delta*(b.n/n)
    m2 = fsum((a.m2, b.m2, delta*delta*(a.n/n)*b.n))
    total = a.total+b.total
    if not all(isfinite(x) for x in (mean, m2, total)):
        raise OverflowError('summary exceeds binary64 range')
    return Summary(n, total, mean, m2, min(a.minimum, b.minimum), max(a.maximum, b.maximum),
                   min(a.first, b.first), max(a.last, b.last))


def reduce_balanced(summaries):
    nodes = list(summaries)
    while len(nodes) > 1:
        nodes = [merge(nodes[i], nodes[i+1]) if i+1 < len(nodes) else nodes[i]
                 for i in range(0, len(nodes), 2)]
    return nodes[0] if nodes else Summary()


def summarize(observations):
    return reduce_balanced(leaf(*item) for item in observations)


def hierarchy(buckets, depth):
    """Sparse canonical buckets; omitted siblings mean absent input, not coverage.

    O(depth * K) worst-case work/storage for K sparse input buckets. Only a dense
    contiguous hierarchy has a geometric-series storage bound approaching 2K.
    """
    if not 0 <= depth <= 16 or len(buckets) > 4096:
        raise ValueError('educational hierarchy admission exceeded')
    levels = [dict(buckets)]
    for _ in range(depth):
        parent = {}
        for index, summary in sorted(levels[-1].items()):
            key = index//2
            parent[key] = merge(parent.get(key, Summary()), summary)
        levels.append(parent)
    return levels


def weighted_mean(values_and_weights):
    pairs = list(values_and_weights)
    if any(not isfinite(x) or not isfinite(w) or w < 0 for x, w in pairs):
        raise ValueError('finite values and nonnegative weights required')
    weight = fsum(w for _, w in pairs)
    return fsum(x*w for x, w in pairs)/weight if weight else None


def coverage(start, end, evidence):
    """Disjoint labeled intervals inside [start,end); uncovered time is unknown."""
    if start >= end:
        raise ValueError('empty domain')
    result = {'available': 0, 'missing': 0, 'unknown': 0}
    cursor = start
    for a, b, status in sorted(evidence):
        if status not in result or a < cursor or b <= a or b > end:
            raise ValueError('invalid or overlapping coverage evidence')
        result['unknown'] += a-cursor
        result[status] += b-a
        cursor = b
    result['unknown'] += end-cursor
    assert sum(result.values()) == end-start
    return result


def demo():
    values = [1e12+i*.125 for i in range(8)]
    stable = summarize((i, i, x) for i, x in enumerate(values))
    with localcontext() as context:
        context.prec = 80
        exact = [Decimal.from_float(x) for x in values]
        center = sum(exact)/len(exact)
        reference = sum((x-center)**2 for x in exact)
    sequential = Summary()
    for i, value in enumerate(values):
        sequential = merge(sequential, leaf(i, i, value))
    split = merge(summarize((i, i, x) for i, x in enumerate(values[:3])),
                  summarize((i+3, i+3, x) for i, x in enumerate(values[3:])))
    distributions = [[0, 0, 3, 3, 4, 8], [0, 1, 1, 4, 4, 8]]
    grid = {i: leaf(i*1000, i, float(i)) for i in (3, 4, 5)}
    return {'kind': 'educational-summary-experiment', 'stable': asdict(stable),
            'reference_m2': str(reference),
            'large_offset_tree_m2': {'balanced': stable.m2, 'sequential': sequential.m2, 'split_3_5': split.m2},
            'naive_m2': sum(x*x for x in values)-sum(values)**2/len(values),
            'averaging_averages': {'correct': weighted_mean([(10, 9), (100, 1)]), 'wrong': 55},
            'duration_example': weighted_mean([(0, 9), (10, 1)]),
            'quantile_counterexample': [{'values': xs, 'sum': sum(xs), 'sum_squares': sum(x*x for x in xs),
                                         'median': statistics.median(xs)} for xs in distributions],
            'aligned_levels': [{str(k): {'n': v.n, 'sum': v.total} for k, v in level.items()}
                               for level in hierarchy(grid, 2)],
            'coverage_us': coverage(0, 10_000_000, [(0, 4_000_000, 'available'),
                                                  (4_000_000, 6_000_000, 'missing')])}

if __name__ == '__main__':
    print(json.dumps(demo(), indent=2))
