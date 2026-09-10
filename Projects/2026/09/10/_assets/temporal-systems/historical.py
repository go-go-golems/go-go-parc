"""Educational historical-session coordination, not browser measurement.

Uses the shared clock/controller/barrier, event clock and archive index. Index
assets and byte lengths here are model inputs, NOT generated-media metadata.
"""
from dataclasses import dataclass
import json
from archive_index import ArchiveIndex, Sample, Segment
from clocks import Barrier, DriftController, MasterClock, moving_target
from scheduler import EventClock

BASE=1_788_912_000_000_000

def camera_index(camera):
    intervals=[(0,4 if camera==4 else 6)]+[(a,a+6) for a in range(6,36,6)]
    segments=[]
    for i,(a,b) in enumerate(intervals):
        samples=tuple(Sample(q,q,q==0) for q in range((b-a)*10))
        segments.append(Segment(f'camera-{camera}-{i}.m4s',1000,f'camera-{camera}-epoch-{i}',
                                'model',BASE+a*1_000_000,BASE+b*1_000_000,0,10,samples))
    return ArchiveIndex({'model':{'asset':'model-init.mp4','range_start':0,'range_length':100}},segments)

@dataclass
class Player:
    camera: int
    utc: int | None = None
    epoch: str | None = None
    pending: bool = False
    visible: bool = False
    rate: float = 1.0
    version: int = 0
    last_ms: int = 0

class HistoricalCoordinator:
    def __init__(self,clock):
        self.clock=clock
        self.master=MasterClock(BASE)
        self.master.configure(0,running=False)
        self.indexes={c:camera_index(c) for c in range(1,5)}
        self.players={c:Player(c) for c in range(1,5)}
        self.controllers={c:DriftController() for c in range(1,5)}
        self.session=None
        self.session_serial=0
        self.generation=0
        self.barrier=None
        self.want_running=True
        self.trace=[]
        self.stats={'created':0,'released':0,'reused':0,'stale_reports':0,'hard_seeks':0,'deadline_releases':0}

    def record(self,kind,**data):
        if len(self.trace)>=512:
            raise ValueError('trace admission exceeded')
        self.trace.append({'p_ms':self.clock.now,'kind':kind,**data})

    def commit_seek(self,target,initial=False):
        now=self.clock.now
        if self.session is None or not self.session['start']<=target<self.session['end']:
            if self.session is not None:
                self.stats['released']+=1
            self.session_serial+=1
            self.session={'id':self.session_serial,'start':target,'end':target+12_000_000}
            self.stats['created']+=1
            self.record('session-open',**self.session)
        else:
            self.stats['reused']+=1
            self.record('session-reuse',id=self.session['id'])
        self.generation+=1
        self.master.configure(now,seek=target,running=False)
        self.barrier=Barrier(self.generation,range(1,5),now)
        self.record('seek',target_us=target,generation=self.generation)
        for camera in self.players:
            self.controllers[camera]=DriftController()
            delay=([40,2600,200,100] if initial else [40,160,120,80])[camera-1]
            self.prepare(camera,target,delay)

    def prepare(self,camera,target,delay):
        player=self.players[camera]
        player.version+=1
        version,generation,session=player.version,self.generation,self.session['id']
        player.visible=False
        plan=self.indexes[camera].resolve(target)
        if plan['status']!='ready':
            player.utc=None;player.epoch=None;player.pending=False
            self.record('unavailable',camera=camera,target_us=target,status=plan['status'])
            return
        player.pending=True
        def ready():
            if self.session is None or self.session['id']!=session or self.generation!=generation or player.version!=version:
                self.stats['stale_reports']+=1
                return
            player.utc=plan['selected_utc_us'];player.epoch=plan['epoch'];player.pending=False;player.last_ms=self.clock.now
            player.rate=float(self.master.rate)
            self.barrier.arrive(generation,camera)
            self.record('ready',camera=camera,generation=generation,epoch=player.epoch)
        self.clock.at(self.clock.now+delay,ready)

    def change(self,**kwargs):
        now=self.clock.now
        before=self.master.now(now)
        self.master.configure(now,**kwargs)
        assert self.master.now(now)==before
        if 'running' in kwargs:
            self.want_running=kwargs['running']
        self.record('clock-change',utc=before,rate=float(self.master.rate),running=self.master.running)

    def report(self,camera,generation,session,version,observed,target_at_observation,observed_at):
        player=self.players[camera]
        if self.session is None or self.session['id']!=session or self.generation!=generation or player.version!=version:
            self.stats['stale_reports']+=1
            return
        # Drift is compared against the master sampled at the SAME instant.
        drift=(observed-target_at_observation)/1000
        action,rate=self.controllers[camera].decide(self.clock.now,drift,float(self.master.rate))
        player.rate=rate
        if action=='seek' and not player.pending:
            self.stats['hard_seeks']+=1
            self.prepare(camera,self.master.now(self.clock.now),80)
        if self.clock.now%1000==0 or action=='seek':
            self.record('observation',camera=camera,observed_at=observed_at,utc=observed,
                        target_at_observation=target_at_observation,drift_ms=drift,action=action)

    def tick(self):
        if self.session is None:return
        now=self.clock.now
        released=self.barrier.poll(now)
        if released:
            self.stats['deadline_releases']+=int(released['reason']=='deadline')
            self.master.configure(now,running=self.want_running)
            self.record('barrier-release',generation=self.generation,**released)
        target=self.master.now(now)
        if not self.session['start']<=target<self.session['end']:
            self.master.configure(now,running=False)
            for player in self.players.values():player.visible=False
            self.record('session-window-ended',target_us=target)
            return
        for camera,player in self.players.items():
            elapsed=0 if released else now-player.last_ms
            player.last_ms=now
            plan=self.indexes[camera].resolve(target)
            if plan['status']!='ready':
                self.controllers[camera].decide(now,None,float(self.master.rate))
                if player.utc is not None or player.pending:
                    player.version+=1;player.utc=None;player.epoch=None;player.pending=False;player.visible=False
                    self.record('gap',camera=camera,target_us=target)
                continue
            if player.utc is None and not player.pending:
                self.prepare(camera,target,80)
            if player.utc is not None and not player.pending:
                if self.master.running and not (camera==2 and 3000<=now<3400):
                    player.utc+=round(elapsed*1000*player.rate)
                local=self.indexes[camera].resolve(player.utc)
                player.epoch=local.get('epoch')
                if player.epoch is None:
                    player.visible=False
                    self.prepare(camera,target,80)
                    continue
                drift=(player.utc-target)/1000
                player.visible=(abs(drift)<=150 and self.session['start']<=player.utc<self.session['end'])
                observed,observed_target=player.utc,target
                delay=200 if camera==3 and 4000<=now<8000 else 0
                args=(camera,self.generation,self.session['id'],player.version,observed,observed_target,now)
                self.clock.at(now+delay,lambda args=args:self.report(*args))
        if now%500==0:
            self.record('checkpoint',master_us=target,generation=self.generation,session=self.session['id'],
                        players=[{'camera':c,'utc':p.utc,'epoch':p.epoch,'visible':p.visible,'pending':p.pending,'rate':p.rate}
                                 for c,p in self.players.items()])

    def close(self):
        if self.session is not None:self.stats['released']+=1
        self.session=None;self.generation+=1
        for player in self.players.values():
            player.version+=1;player.utc=None;player.epoch=None;player.visible=False;player.pending=False
        self.record('closed')


def scenario():
    clock=EventClock()
    coordinator=HistoricalCoordinator(clock)
    coordinator.commit_seek(BASE,initial=True)
    # Ticks are scheduled before equal-time user actions; insertion order is part
    # of this deterministic scenario, not an assertion about browser scheduling.
    for p in range(100,13_001,100):clock.at(p,coordinator.tick)
    clock.at(6500,lambda:coordinator.commit_seek(BASE+6_500_000))
    clock.at(6550,lambda:coordinator.commit_seek(BASE+6_700_000)) # invalidate in-flight readiness
    clock.at(7600,lambda:coordinator.change(running=False))
    clock.at(8000,lambda:coordinator.change(running=True,rate=2))
    clock.at(9000,lambda:coordinator.commit_seek(BASE+20_000_000))
    clock.at(12000,coordinator.close)
    clock.run(13_000)
    assert coordinator.stats['created']==coordinator.stats['released']==2
    assert all(p.utc is None and not p.visible and not p.pending for p in coordinator.players.values())
    return {'kind':'educational-historical-session-simulation','step_ms':100,
            'observations':'continuous modeled positions, not decoded frames; visible is a policy flag',
            'index_assets':'model identifiers and lengths, not real-media evidence',
            'stats':coordinator.stats,'trace':coordinator.trace,'remaining_events':len(clock.events),
            'archive_recovery':{name:[{**e,'camera':2,'session':'recovery-model',
                                      'requested_utc':BASE+e['request_ms']*1000,
                                      'observed_utc':BASE+e['frame_ms']*1000,
                                      'state':'visible' if e['visible'] else 'covered-retry'}
                                     for e in moving_target(repaired)]
                                for name,repaired in [('paused',False),('concealed-progress',True)]}}

def availability_svg():
    elements=['<svg xmlns="http://www.w3.org/2000/svg" width="660" height="240" viewBox="0 0 660 240">',
              '<rect width="660" height="240" fill="white"/>',
              '<text x="20" y="24" font-family="sans-serif" font-size="15">Model archive availability — UTC seconds from anchor</text>']
    for camera in range(1,5):
        y=45+(camera-1)*38
        elements.append(f'<text x="12" y="{y+19}" font-family="sans-serif" font-size="13">Camera {camera}</text>')
        elements.append(f'<rect x="100" y="{y}" width="480" height="26" fill="#eeeeee"/>')
        for segment in camera_index(camera).segments:
            a=max(0,(segment.start_us-BASE)/1_000_000);b=min(12,(segment.end_us-BASE)/1_000_000)
            if a<b:elements.append(f'<rect x="{100+40*a}" y="{y}" width="{40*(b-a)}" height="26" fill="#21667a" stroke="white"/>')
    for second in range(0,13,2):
        elements.append(f'<text x="{96+40*second}" y="216" font-family="sans-serif" font-size="13">{second}</text>')
    elements.append('<text x="270" y="179" font-family="sans-serif" font-size="12">gap</text></svg>')
    return ''.join(elements)

if __name__=='__main__':
    from pathlib import Path
    (Path(__file__).resolve().parent/'outputs'/'historical-availability.svg').write_text(availability_svg())
    print(json.dumps(scenario(),indent=2))
