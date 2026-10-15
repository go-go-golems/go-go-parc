#!/usr/bin/env python3
"""Figures for the Falllinie 60 FPS release report. Usage: figures.py SPIKE_REPO OUT_DIR"""
import glob,json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SURFACE,INK,INK2,GRID,S1,S2,S3='#fcfcfb','#0b0b0b','#52514e','#e4e3df','#2a78d6','#eb6834','#1baf7a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.facecolor':SURFACE,'figure.facecolor':SURFACE,'savefig.facecolor':SURFACE,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'svg.fonttype':'none'})
repo=Path(sys.argv[1]);out=Path(sys.argv[2])
def load(pat):return json.loads(Path(glob.glob(str(repo/'ttmp/2026/10/14'/pat))[0]).read_text())
a9=load('FALLLINIE-PERF-009*/scripts/evidence/acceptance-*/summary.json');a10=load('FALLLINIE-PERF-010*/scripts/evidence/accept60-*/summary.json')
l512=load('FALLLINIE-PERF-010*/scripts/evidence/long512-*/summary.json');lod=load('FALLLINIE-PERF-010*/scripts/evidence/lod-*/summary.json')
def metrics(p):
 f=p['frames'];pf=p['per_frame_mean'];return f['long_share']*100,pf['MaliGPUActiveCy']*f['loop_fps']/8e8*100,f['p95_ms']
stages=[('Before (live, 384×288)',metrics(a9['pooled']['original-live'])),
        ('+ bounds, culling, 16-bit indices',metrics(a9['pooled']['defaults-live'])),
        ('+ 60 m terrain detail',metrics(a10['pooled']['lod60-live'])),
        ('+ 512×384 internal (110 s × 3)',tuple(sum(metrics(l512['pooled'][g])[i] for g in ['r512-s42','r512-s7','r512-s1234'])/3 for i in range(3)))]
fig,axes=plt.subplots(1,3,figsize=(10.2,3.6),sharey=True)
labels=[s for s,_ in stages][::-1]
for ax,(title,idx,fmt,color,lim) in zip(axes,[('Frames ≥ 25 ms (%)',0,'{:.1f}%',S2,9),('GPU busy (%)',1,'{:.0f}%',S1,110),('p95 frame interval (ms)',2,'{:.1f}',S3,32)]):
 vals=[m[idx] for _,m in stages][::-1]
 ax.barh(range(len(vals)),vals,color=color,height=.6,edgecolor=SURFACE,linewidth=2)
 for y,v in enumerate(vals):ax.text(v+lim*.02,y,fmt.format(v),va='center',fontsize=9,color=INK)
 ax.set_xlim(0,lim);ax.set_title(title,loc='left',fontsize=10,color=INK);ax.grid(True,axis='x',color=GRID);ax.set_axisbelow(True)
 if idx==2:ax.axvline(1000/60,color=INK2,linestyle='--',linewidth=1)
axes[0].set_yticks(range(len(labels)));axes[0].set_yticklabels(labels,color=INK)
fig.suptitle('Live dual-view autoplay with audio synthesis, each step added to the previous one',x=.01,ha='left',fontsize=11,color=INK)
fig.tight_layout();fig.savefig(out/'01-journey.svg');plt.close(fig)
# Primitive fate per frame.
d=lod['pooled']['defaults-geom']['per_frame_mean'];l=lod['pooled']['lod60-geom']['per_frame_mean']
parts=[('Visible','MaliGeomVisiblePrim',S1),('Covers no sample','MaliGeomSampleCullPrim',S2),('Outside near/far plane','MaliGeomZPlaneCullPrim',S3),('Facing or side planes','MaliGeomFaceXYPlaneCullPrim','#eda100')]
fig,ax=plt.subplots(figsize=(8.6,2.9))
for row,(name,data) in enumerate([('60 m terrain detail',l),('Full detail',d)]):
 left=0
 for label,key,color in parts:
  v=data[key]/1000;ax.barh(row,v,left=left,color=color,height=.55,edgecolor=SURFACE,linewidth=2,label=label if row==0 else None)
  if v>18:ax.text(left+v/2,row,f'{v:.0f}k',ha='center',va='center',fontsize=9,color='white')
  left+=v
 ax.text(left+4,row,f'{data["MaliGeomTotalPrim"]/1000:.0f}k total',va='center',fontsize=9,color=INK)
ax.set_yticks([0,1]);ax.set_yticklabels(['60 m terrain detail','Full detail'],color=INK);ax.set_xlim(0,430)
ax.set_xlabel('Primitives per loop frame (thousands), shipping replay, both views');ax.grid(True,axis='x',color=GRID);ax.set_axisbelow(True)
ax.legend(frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.45,1.28),fontsize=9)
fig.tight_layout();fig.savefig(out/'02-primitive-fate.svg');plt.close(fig)
print('ok')
