"""Educational integer-time viewport model; not a product implementation.

Coordinates use Fraction until output. Python round uses ties-to-even, unlike
JavaScript Math.round; round-trip/anchor tests allow the stated microsecond error.
No source observations or videos are allocated by this model.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import floor, log2

SECOND = 1_000_000
MAX_SPAN = 7 * 86400 * SECOND
MAX_REFERENCES = 512
MAX_INSTANCES = 50_000
MAX_PACKED_BYTES = 512 * 1024

@dataclass(frozen=True)
class Domain:
    start: int
    end: int

    def __post_init__(self):
        if not all(type(x) is int for x in (self.start, self.end)):
            raise ValueError('integer microseconds required')
        if not 4 * SECOND <= self.end - self.start <= MAX_SPAN:
            raise ValueError('domain outside four-second/seven-day bounds')

    @property
    def span(self):
        return self.end - self.start


def width_check(width):
    if type(width) is not int or width <= 0:
        raise ValueError('positive integer CSS width required')


def time_to_x(utc, domain, width):
    width_check(width)
    return Fraction((utc - domain.start) * width, domain.span)


def x_to_time(x, domain, width):
    width_check(width)
    return domain.start + round(Fraction(x) * domain.span / width)


def zoom(domain, x, width, factor):
    width_check(width)
    factor = Fraction(factor)
    if factor <= 0:
        raise ValueError('positive zoom factor required')
    anchor = x_to_time(x, domain, width)
    span = max(4 * SECOND, min(MAX_SPAN, round(domain.span / factor)))
    start = anchor - round(Fraction(x) * span / width)
    return Domain(start, start + span)


def level(domain, width, kind):
    width_check(width)
    if kind not in ('numeric', 'image'):
        raise ValueError('unknown representation')
    pixels, base = (Fraction(3, 4), Fraction(1, 4)) if kind == 'numeric' else (80, 2)
    ratio = Fraction(domain.span, SECOND * width) * pixels / base
    return max(0, min(14, floor(log2(ratio) + 0.5)))


def tile_span(resolution):
    if type(resolution) is not int or not 0 <= resolution <= 14:
        raise ValueError('unsupported level')
    return 64 * SECOND * (1 << resolution)


def tile_indices(domain, resolution):
    span = tile_span(resolution)
    first, last = domain.start // span, (domain.end - 1) // span
    if last - first + 1 > MAX_REFERENCES:
        raise ValueError('reference admission exceeded')
    return range(first, last + 1)


def visible_rows(count, height, top, viewport, overscan=2):
    if not (0 <= count <= 128 and height > 0 and viewport > 0 and 0 <= overscan <= 16):
        raise ValueError('row admission exceeded')
    top = max(0, min(top, max(0, count * height - viewport)))
    first = max(0, top // height - overscan)
    end = min(count, (top + viewport + height - 1) // height + overscan)
    return range(first, end)


def geometry(domain, width, rows, resolution):
    """Emit temporal envelope extents, not reconstructed samples.

    Enumeration O(R*K*256); reject that upper bound before allocating output.
    At most MAX_INSTANCES extents are retained. Each output is a Python tuple,
    not a claimed 16-byte native allocation; packed float32 size is reported only
    as an equivalent four-scalar representation estimate in the demo.
    """
    width_check(width)
    if not hasattr(rows, '__len__') or len(rows) > 128:
        raise ValueError('finite admitted row collection required')
    rows = tuple(rows)
    indices = tile_indices(domain, resolution)
    candidate_count = len(rows) * len(indices) * 256
    if candidate_count * 16 > MAX_PACKED_BYTES:
        raise ValueError('packed output byte admission exceeded')
    if candidate_count > MAX_INSTANCES:
        raise ValueError('instance enumeration admission exceeded')
    step = tile_span(resolution) // 256
    output = []
    for row in rows:
        for index in indices:
            origin = index * tile_span(resolution)
            for bucket in range(256):
                a, b = origin + bucket * step, origin + (bucket + 1) * step
                if a >= domain.end or b <= domain.start:
                    continue
                left = max(Fraction(0), time_to_x(a, domain, width))
                right = min(Fraction(width), time_to_x(b, domain, width))
                output.append((row, float(left), float(right), bucket))
    return output


class Engine:
    def __init__(self, domain):
        self.domain = domain
        self.generation = 0
        self.before = None

    def begin_pan(self, x, width):
        width_check(width)
        self.before = (self.domain, Fraction(x), width)

    def move(self, x):
        if self.before is None:
            raise ValueError('no gesture')
        before, origin_x, width = self.before
        delta = x_to_time(origin_x, before, width) - x_to_time(x, before, width)
        self.domain = Domain(before.start + delta, before.end + delta)
        self.generation += 1

    def cancel(self):
        if self.before is not None:
            self.domain = self.before[0]
            self.before = None
            self.generation += 1

    def eligible(self, completion_generation):
        return completion_generation == self.generation


if __name__ == '__main__':
    import json
    day = Domain(1788912000000000, 1788998400000000)
    rows = visible_rows(16, 232, 0, 720)
    numeric, image = level(day, 1400, 'numeric'), level(day, 1400, 'image')
    rectangles = geometry(day, 1400, rows, numeric)
    changed = zoom(day, 700, 1400, 1440)
    engine = Engine(changed)
    engine.begin_pan(700, 1400)
    engine.move(840)
    pending_generation = engine.generation
    moved = engine.domain
    engine.cancel()
    print(json.dumps({'kind': 'educational-model',
                      'zoom_domain': [changed.start, changed.end],
                      'zoom_tiles': list(tile_indices(changed, level(changed, 1400, 'numeric'))),
                      'pan_domain': [moved.start, moved.end],
                      'cancel_domain': [engine.domain.start, engine.domain.end],
                      'late_completion_eligible': engine.eligible(pending_generation), 'numeric_level': numeric, 'image_level': image,
                      'rows': list(rows), 'numeric_tiles_per_row': list(tile_indices(day, numeric)),
                      'instances': len(rectangles), 'four_float32_equivalent_bytes': len(rectangles) * 16,
                      'actual_python_memory_measured': False,
                      'first_rectangles': rectangles[:3]}, indent=2))
