"""Educational whole-fragment decode planner with sample-aware target selection.

Indexes are generated from ffprobe evidence. Media ranges cover whole standalone
fragments, not packet payloads spliced into a container. No authorization server
is implemented: caller must validate grants separately before fetching assets.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction
import re


def admitted_asset(value):
    return isinstance(value, str) and value not in ('.', '..') and re.fullmatch(r'[A-Za-z0-9_.-]+', value) is not None

@dataclass(frozen=True)
class Sample:
    pts: int
    dts: int
    key: bool

@dataclass(frozen=True)
class Segment:
    asset: str
    size: int
    epoch: str
    configuration: str
    start_us: int
    end_us: int
    pts_anchor: int
    timescale: int
    samples: tuple[Sample, ...]

    def utc(self, pts):
        return self.start_us+round(Fraction((pts-self.pts_anchor)*1_000_000,self.timescale))


class ArchiveIndex:
    def __init__(self, configurations, segments):
        if len(segments)>64 or len(configurations)>16:
            raise ValueError('index admission exceeded')
        for config in configurations.values():
            if (not admitted_asset(config.get('asset')) or config.get('range_start') != 0
                    or type(config.get('range_length')) is not int
                    or not 0 < config['range_length'] <= 4*1024*1024):
                raise ValueError('invalid whole-initialization byte grant')
        self.configurations = configurations
        self.segments = sorted(segments,key=lambda s:s.start_us)
        for i,s in enumerate(self.segments):
            if not admitted_asset(s.asset) or s.configuration not in configurations or not 0<s.size<=4*1024*1024:
                raise ValueError('configuration or size not admitted')
            if s.start_us>=s.end_us or s.timescale<=0 or not 0<len(s.samples)<=1000:
                raise ValueError('invalid timing/sample admission')
            if i and self.segments[i-1].end_us>s.start_us:
                raise ValueError('ambiguous presentation coverage')
            if any(a.dts>b.dts for a,b in zip(s.samples,s.samples[1:])):
                raise ValueError('packets not in decode order')
            # This deliberately restricted closed-GOP fixture requires each
            # fragment to begin with a certified independent access point.
            if not s.samples[0].key or s.samples[0].pts != s.pts_anchor:
                raise ValueError('fragment lacks admitted independent start')
            if any(not s.start_us<=s.utc(p.pts)<s.end_us for p in s.samples):
                raise ValueError('sample outside presentation coverage')

    def resolve(self, target):
        s = next((s for s in self.segments if s.start_us<=target<s.end_us),None)
        if s is None:
            return {'status':'gap','target_us':target}
        candidates = sorted((s.utc(p.pts),p.pts) for p in s.samples if s.utc(p.pts)>=target)
        # Policy: first frame at or after target, strictly inside this segment.
        # A target after its last PTS is not silently rounded backward.
        if not candidates:
            return {'status':'no-frame-before-segment-end','target_us':target}
        utc, pts = candidates[0]
        config = self.configurations[s.configuration]
        return {'status':'ready','target_us':target,'epoch':s.epoch,
                'configuration':s.configuration,'initialization':config,
                'media':[{'asset':s.asset,'range_start':0,'range_length':s.size}],
                'decode_start_dts':s.samples[0].dts,'decode_start_pts':s.samples[0].pts,
                'timescale':s.timescale,'selected_pts':pts,'selected_utc_us':utc,
                'discard_before_us':target,
                'discarded_frame_count':sum(s.utc(p.pts)<target for p in s.samples),
                'range_semantics':'whole-fragment; initialization precedes media'}


def from_json(value):
    segments=[]
    for item in value['segments']:
        item=dict(item)
        item['samples']=tuple(Sample(**s) for s in item['samples'])
        segments.append(Segment(**item))
    return ArchiveIndex(value['configurations'],segments)


def to_json(index):
    return {'configurations':index.configurations,'segments':[asdict(s) for s in index.segments]}
