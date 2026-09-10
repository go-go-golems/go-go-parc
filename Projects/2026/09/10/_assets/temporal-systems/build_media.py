"""Generate two bounded educational HLS/fMP4 fixtures and a real decode audit.
Run: PYTHONDONTWRITEBYTECODE=1 python3 build_media.py
Requires ffmpeg/ffprobe with libx264, drawtext and the named DejaVu font.
Only owned outputs/media/{no-b,b-frames} are overwritten. No product assets used.
"""
from dataclasses import asdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import gzip
import re
import subprocess
import tempfile
from archive_index import ArchiveIndex, Sample, Segment, to_json

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'/'media'
ANCHOR=1_788_912_000_000_000
COMMANDS=[]

def run(args):
    COMMANDS.append(args)
    result=subprocess.run(args,capture_output=True,text=True,timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result


def generate(name,bframes):
    directory=OUT/name
    directory.mkdir(parents=True,exist_ok=True)
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','testsrc2=size=160x90:rate=10',
         '-t','6','-vf',f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{name} frame %{{n}}':fontsize=12:fontcolor=white:x=4:y=4",
         '-an','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p',
         '-g','20','-keyint_min','20','-sc_threshold','0','-bf',str(bframes),
         '-x264-params','open-gop=0:b-adapt=0','-f','hls','-hls_time','2','-hls_playlist_type','vod',
         '-hls_segment_type','fmp4','-hls_fmp4_init_filename','init.mp4',
         '-hls_segment_filename',str(directory/'fragment-%02d.m4s'),str(directory/'playlist.m3u8')])
    init=directory/'init.mp4'
    configuration=sha256(init.read_bytes()).hexdigest()
    segments=[]
    first_pts=None
    b_frame_count=0
    with tempfile.TemporaryDirectory(prefix='temporal-media-') as temp:
        for fragment in sorted(directory.glob('fragment-*.m4s')):
            joined=Path(temp)/'fragment.mp4'
            joined.write_bytes(init.read_bytes()+fragment.read_bytes())
            packet_data=json.loads(run(['ffprobe','-v','error','-select_streams','v:0',
                                        '-show_streams','-show_packets','-of','json',str(joined)]).stdout)
            frame_data=json.loads(run(['ffprobe','-v','error','-select_streams','v:0',
                                       '-show_frames','-of','json',str(joined)]).stdout)
            assert len(frame_data['frames'])==20
            b_frame_count += sum(f.get('pict_type')=='B' for f in frame_data['frames'])
            (directory/(fragment.stem+'-frames.json')).write_text(json.dumps(frame_data,indent=2)+'\n')
            stream=packet_data['streams'][0]
            tb=Fraction(stream['time_base'])
            assert tb.numerator==1
            samples=tuple(Sample(int(p['pts']),int(p['dts']),'K' in p['flags']) for p in packet_data['packets'])
            pts=min(p.pts for p in samples)
            first_pts=pts if first_pts is None else first_pts
            end=max(int(p['pts'])+int(p['duration']) for p in packet_data['packets'])
            start_us=ANCHOR+round((pts-first_pts)*tb*1_000_000)
            end_us=ANCHOR+round((end-first_pts)*tb*1_000_000)
            segments.append(Segment(fragment.name,fragment.stat().st_size,'continuous',configuration,
                                    start_us,end_us,pts,tb.denominator,samples))
            (directory/(fragment.stem+'-probe.json')).write_text(json.dumps(packet_data,indent=2)+'\n')
        assert len(segments)==3 and all(len(s.samples)==20 for s in segments)
        index=ArchiveIndex({configuration:{'asset':'init.mp4','range_start':0,'range_length':init.stat().st_size}},segments)
        target=ANCHOR+2_750_000
        plan=index.resolve(target)
        assert plan['status']=='ready' and plan['discarded_frame_count']==8
        selected=next(s for s in segments if s.asset==plan['media'][0]['asset'])
        joined=Path(temp)/'decode.mp4'
        joined.write_bytes(init.read_bytes()+(directory/selected.asset).read_bytes())
        # Decode the entire closed-GOP fragment from its independent start;
        # select only after decoding. -copyts retains probed PTS in the filter.
        decoded=run(['ffmpeg','-hide_banner','-nostats','-loglevel','info','-y','-copyts','-i',str(joined),
                     '-vf',f"select=gte(pts\\,{plan['selected_pts']}),showinfo",'-frames:v','1',
                     '-fps_mode','passthrough',str(directory/'selected-frame.png')])
        # Preserve exact stderr compressed; readable log normalizes only trailing
        # whitespace from FFmpeg's final progress line for repository hygiene.
        (directory/'decode.raw.log.gz').write_bytes(gzip.compress(decoded.stderr.encode(),mtime=0))
        (directory/'decode.log').write_text('\n'.join(line.rstrip() for line in decoded.stderr.splitlines())+'\n')
        observed=re.search(r'\bn:\s*0\s+pts:\s*(-?\d+)\s+pts_time:([\d.\-]+)',decoded.stderr)
        assert observed,decoded.stderr
        assert int(observed[1])==plan['selected_pts']
        plan['observed_first_retained_pts']=int(observed[1])
        plan['observed_first_retained_pts_seconds']=float(observed[2])
        plan['observed_first_retained_utc_us']=selected.utc(int(observed[1]))
        plan['b_frame_count']=b_frame_count
        plan['reordered_packet_count']=sum(p.pts!=p.dts for s in segments for p in s.samples)
        assert bool(plan['reordered_packet_count']) == bool(bframes)
        (directory/'index.json').write_text(json.dumps(to_json(index),indent=2)+'\n')
        (directory/'decode-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        assert sum(p.stat().st_size for p in directory.iterdir() if p.is_file())<4*1024*1024
        return plan

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    versions={tool:run([tool,'-version']).stdout.splitlines()[0] for tool in ('ffmpeg','ffprobe')}
    plans={name:generate(name,b) for name,b in (('no-b',0),('b-frames',2))}
    (OUT/'generation-audit.json').write_text(json.dumps({'kind':'executed-educational-media',
                 'versions':versions,'commands':COMMANDS,'plans':plans},indent=2)+'\n')
    print(json.dumps(plans,indent=2))
