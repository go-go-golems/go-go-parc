---
title: "Film Dust Detector, Part 1: Classifiers, Judges and an Honest Gold Set — A Technical Deep Dive"
aliases:
  - DUST-002 to DUST-006 detector report
  - film dust detector deep dive
  - gold pass 2 and judge models
tags:
  - project
  - film-scanning
  - computer-vision
  - machine-learning
  - evaluation
  - agents
  - goja-cv
status: active
type: project
created: 2026-11-14
repo: /Users/manuel/code/wesen/2026-11-07--dust-scanning
---

# Film Dust Detector, Part 1: Classifiers, Judges and an Honest Gold Set — A Technical Deep Dive

The dataset series ended with labels from eleven thousand Lightroom heals and a hand-labelled gold set
([[PROJECT REPORT - Film Dust Dataset - Part 8 - The Gold Set and the Annotation Tool - A Technical Deep Dive|Dataset, Part 8]]),
and the annotation series built the tools and agents that filled that gold set
([[PROJECT REPORT - Film Dust Annotation - Part 4 - Annotator Agents - Playbook, Trials and Pre-Annotation over MCP - A Technical Deep Dive|Annotation, Part 4]]).
This report covers what happened next: two rounds of detector experiments, the point where every model stopped
improving, the discovery that the gold set itself was undercounting dust, and the machinery — vision-language
judges driving a scriptable image engine, scored on blind controls — that found the missing dust and confirmed it
with the user. It ends with the design of the next layer: classical computer vision feeding a stacker on top of
the neural classifier.

The report is written for a reader who knows the project's goal (find dust on raw film scans with few false repairs)
but not the experiments. Every number comes from a run in `runs/results.csv` or a step in a ticket diary.

> [!summary]
> - **The detector plateaued on architecture.** A B1 classical candidate generator plus a two-branch neural classifier
>   (E19: stride-1 ResNet18 on a 64 px crop, ConvNeXt-Tiny on a 256 px context) is the best model. Three seeds of the
>   same configuration differ as much as all recent architecture changes did; ensembles do not help.
> - **The gold set was missing dust, not the detector.** Of the detector's confident "false positives", most were real
>   dust nobody had labelled. A Claude Opus judge pre-sorted 559 unlabelled detections, the user confirmed them, and
>   gold-dev grew from 353 to 495 points. E19's recall at one false positive per tile went from 0.27 to 0.49 at 0.89
>   precision; at five per tile from 0.57 to 0.74.
> - **Judges are measurable instruments.** With blind controls, five models and three prompt versions were compared:
>   Claude Opus was best (AUC 0.91 on a 24-item probe), deepseek-4.1-flash best among the cheap ones, and a prompt that
>   taught a plausible but non-predictive cue made a judge *worse*.
> - **Next: labels and classical features.** Train-side labels get the same judge + user loop (DUST-005); a
>   gradient-boosted stacker on classifier logit plus classical features is built and smoke-tested (DUST-006).

## 1. The problem and how it is measured

A scan is a 16-bit linear DNG of a film negative. The project works in optical density, `D = −log10(I / I_base)`
per channel, because dust blocks light equally in all three channels: in density it is an additive bump of the same
height in R, G and B, independent of the scene under it. That makes dust bright and neutral in density views, while
colour grain and coloured scene details are tinted.

A detector outputs scored positions. It is evaluated on **gold tiles** — 1024 × 1024 px tiles on which a person marked
every speck — by matching detections to gold points and reporting **recall at a fixed number of false positives per
tile**. The fixed-FP framing matters because the cost of a mistake is per mistake: a missed speck costs a minute of
manual cleanup, a false repair destroys real image detail. Two operating points matter for the user, who will use the
detector both ways:

| use | operating point | what matters |
|---|---|---|
| suggestions reviewed in Lightroom | ~5 false positives per tile | recall at moderate precision |
| automatic repair | ~1 false positive per 31 MP frame (~30 tiles) | precision first |

The 50 gold tiles are split into 30 **gold-dev** tiles (for comparing runs) and 20 **gold-test** tiles (scored only at
checkpoints), stratified into five content strata: smooth, high texture, dark (thin negative), bright (dense
negative) and fine detail.

## 2. Round one: from hand-built features to a classifier (DUST-002)

The first round followed a written model-exploration guide: build the evaluation harness, then baselines, synthetic
data, two model families, and a review loop. The pipeline that survived has four stages:

```text
raw window ──► B1 candidates ──► crops ──► classifier ──► P(dust)
               multi-scale DoG     64 px local      two branches
               z-scores, top-hats, + 256 px context  (later rounds)
               median residual     (area-averaged
               ÷ local robust      to 64 px)
               spread
```

**B1**, the classical candidate generator (`dustdet/classical.py`), computes per-channel differences of Gaussians at
σ = 1.5, 3 and 6 px, white top-hats and a median residual on density, divides every map by its local robust spread
(a block MAD), and takes local maxima above a threshold. It finds about 90 % of gold dust somewhere in its candidate
list, at about 240 candidates per megapixel. Everything after it re-ranks those candidates.

The key results of round one, on gold-dev at 1 / 5 / 20 false positives per tile:

| run | what it is | recall @1 | @5 | @20 |
|---|---|---|---|---|
| E1 | B1 alone (rule score) | 0.20 | 0.33 | 0.48 |
| E2f | ResNet18 classifier on B1 candidates, fused with B1 | 0.16 | 0.42 | 0.69 |
| E13 | classifier trained with agent-labelled tiles, fused | 0.18 | 0.44 | 0.72 |
| E4h | U-Net, real labels, h-maxima candidates | 0.12 | 0.29 | 0.29 |
| E8 | U-Net with a full-resolution branch | 0.03 | 0.17 | 0.27 |

Three lessons from round one carried forward:

- **The U-Nets lost on gold.** Trained on heal masks, they learned what the photographer healed — big, obvious
  defects — and capped at about 0.29 recall. E8's masks are good (pixel IoU 0.46), which makes it useful for repair
  later, not for detection.
- **Synthetic dust did not transfer.** A classifier trained on synthetic sprites alone found about half the real heals;
  pretrain-then-finetune did not beat real-only training. A realism classifier told synthetic from real crops at 82 %
  accuracy: straight uniform hairs and oversized sprites gave them away.
- **Heal labels are one-sided.** A heal says "dust here"; the absence of a heal says nothing. Every candidate not under
  a heal was a training negative, including all the dust the photographer never healed.

## 3. Round two: label cleaning, context, and the plateau (DUST-003)

### 3.1 The isolation cut

The last lesson became the first experiment of round two. If unhealed dust sits among the negatives, the classifier is
trained to call it "not dust". The question was how to recognise it without labels. A speck stands out from the grain
around it; a grain blob does not. **Isolation** measures exactly that:

```text
iso = DoG step at the candidate / 95th percentile of the steps of the other DoG peaks in the 64 px crop
```

Gold specks sit at iso 2–16, grain at below 2. Among the 97,548 heal negatives of the training split, 21 % had iso ≥ 2.
Dropping them from training (E14: iso ≥ 3, E14b: iso ≥ 2) was the largest single improvement of the round, and it
landed at the strict end: against the previous best (E13), recall at 1 FP per tile rose from 0.18 to 0.24–0.25 and at
the budget of 1 FP per frame from 0.054 to 0.133, while recall at 20 FP per tile moved only from 0.72 to 0.73–0.74.

### 3.2 Context and the losses that ranked backwards

E15 split the classifier into two branches: a ResNet18 on the 64 px local crop with a stride-1 stem (so a 2 px speck is
not averaged away before the first block) and a ConvNeXt-Tiny on the 256 px context. E16 replaced the context branch
with a frozen DINOv3 ConvNeXt; frozen self-supervised features on negative density were worse than a fine-tuned
ImageNet model. E17 and E18 tried principled losses for incomplete labels (ignoring confident negatives; non-negative
positive-unlabelled risk). They had the best validation AP of any run (0.905, 0.916) and the worst gold results
(recall 0.03–0.06 at 1 FP per tile).

That inversion is worth stating as a rule: **validation AP on heal labels ranks models backwards** once a model learns
to call unhealed dust "dust", because heal-based validation counts that as a false positive. From E17 on, models are
selected on gold only.

E19 combined the two winners — E15's architecture and E14b's iso ≥ 2 cut — and became the best detector: 0.27 / 0.57 /
0.78 at 1 / 5 / 20 FP per tile.

### 3.3 Seed noise and the end of architecture search

Gold-dev has 353 points on 30 tiles. Two more seeds of E19 measured how much of the differences between runs was noise:

| run | @1 FP/tile | @5 | @20 |
|---|---|---|---|
| E19 seeds 1, 2, 3 | 0.25–0.31 | 0.54–0.57 | 0.78–0.79 |
| E19e (mean logit of 3 seeds) | 0.29 | 0.55 | 0.79 |
| E19x (E14b + E15 + E19) | 0.29 | 0.56 | 0.78 |
| E20 (E19 + 120 judge-labelled hard negatives) | 0.31 | 0.53 | 0.77 |

The seed spread at 1 FP per tile (±0.03) is as large as every difference among the recent runs. The budget metric
(1 FP per frame) swung from 0.085 to 0.150 between seeds — unusable for ranking. Ensembles of seeds agreed too much
(logit correlation 0.94) to help. The one gain that held across seeds was E19's label cut at the high-recall end
(0.78–0.79 vs E15's 0.74). Architecture and averaging had plateaued; the next gain would have to come from labels.

## 4. Judges: vision-language models with an image engine

### 4.1 The setup

Reviewing thousands of crops is not something the user wanted to do. The annotation series had already given agents
**goja-cv**, a JavaScript image-analysis engine exposed over MCP: an agent writes a short program that opens a density
tile, crops, measures and renders views, and gets back numbers and images. Helper functions encode the project's
knowledge (`mem.tile`, `mem.probe`, `mem.zoom`, and later `mem.isolation`).

For round two the agents became **judges**: given up to six positions, decide for each whether a careful person would
heal it, and return a probability `p_heal`. The harness (DUST-003 scripts 06–11) runs each judge as an isolated
non-interactive process — the `pi` coding agent with built-in tools disabled, or a headless `claude -p` limited to the
goja-cv wrapper and its own working directory — so a judge cannot read labels or other judges' answers.

Every batch mixes **blind controls** with known answers into the items. Scoring a judge on the controls gives its AUC,
its calibration (Brier score), and the thresholds at which its confident calls reach a target precision. Without
controls there is no way to tell a better judge or a better prompt from a different one.

![goja-cv in one picture: a gold dust speck (top row) and its five strongest neighbouring peaks (rows below), each shown in six analyses — stretched scene, speck view, speck colour, detail, DoG in false colour and local contrast. The speck is compact, neutral and much stronger than its neighbours in every column](_assets/dust-det-goja-sheet-spot-vs-neighbours.png)

### 4.2 Which model judges best

Three pi models judged the same 360 items (300 candidates, 60 controls) with the same first prompt:

| judge (thinking high) | control AUC | Brier | confident calls usable | tool calls per run of 6 |
|---|---|---|---|---|
| deepseek-4.1-flash | **0.78** | **0.195** | 120 of 300 | 23 |
| glm-5.3-flash | 0.67 | 0.253 | 36 (all dust) | 16.5 |
| gpt-6-luna | 0.71 | 0.279 | 33 (all dust) | 12 |

The ranking followed how much each model inspected. gpt-6-luna was fastest and most decisive (answers near 0.05 or
0.95) but looked least, never checked colour, and called ten known dust specks "grain" or "scene" with confidence. Then
a 24-item probe compared Claude models with the cheap judge, using a third prompt version (section 4.3):

| judge | AUC | accuracy | Brier | unlabelled dust found (of 9) | looks over 4 runs |
|---|---|---|---|---|---|
| **Claude Opus** | **0.91** | **0.83** | **0.128** | **8** | 171 |
| deepseek-4.1-flash | 0.81 | 0.67 | 0.197 | 7 | — |
| Claude Sonnet | 0.74 | 0.71 | 0.220 | 6 | 116 |
| Claude Haiku | 0.70 | 0.54 | 0.225 | 5 | 115 |

Opus investigated the most and noticed things the prompt never asked about: an isolation number skewed because the
"neighbours" were the frame edge, and a control position sitting 15 px beside the speck it was supposed to mark.

### 4.3 Prompts are behaviour, and a cue can hurt

The first prompt prescribed three steps (probe, zoom, wide zoom). The judges' transcripts showed them doing exactly
those three steps, although every helper's documentation was in their tool results. The second prompt described the
whole toolbox — seven views, contrast, false colour, profiles, peaks, morphology — and required four checks including
isolation, with the sentence "iso ≥ 2 stands out from the grain". Tool use rose sharply (isolation 347 times, colour
checks 183, profiles 118 over 360 items). Accuracy fell: control AUC 0.78 → 0.71.

The cause was measurable. Every position a judge sees was flagged by the detector, so nearly all of them stand out
from the grain; on the controls, isolation alone had AUC 0.63. A cue that separates dust from random places is useless
among detector positives, and stating it as a rule pushed the judge toward "dust". A second trap appeared while
writing the third prompt: plain chroma (channel spread) grows with brightness, so a bright dust speck has *higher*
chroma than its surroundings; only relative chroma (spread ÷ brightness) shows dust as less coloured than the area
around it (0.2–0.36 vs 0.4–1.2 on gold specks).

The third prompt reframed the question — every candidate stands out, so is it on the film or in the picture? — gave
concrete cues for both (dust is neutral, ignores scene edges, does not repeat; scene highlights sit on objects,
repeat, are tinted), required a full-precision close-up (32 px at 12×) and relative chroma, and made isolation
optional. It also asked for a **rationale**: why, how it was validated (which looks and measurements, with numbers) and
what speaks against the call. Version 3 was the best prompt for deepseek (AUC 0.80) and the one used with Opus.

## 5. The gold set was the problem

### 5.1 How it surfaced

To calibrate judges, the first control sets used gold-dev detections with no gold match as "known not-dust". When the
user checked ten of them, nine were dust. The controls were wrong — and so was every precision number measured on
gold-dev: a large share of the detector's confident false positives were specks the first labelling pass had missed.

### 5.2 Gold pass 2

Opus (prompt v3, 60 headless runs grouped by gold tile) judged all 294 E19 detections on gold-dev with score ≥ 0.5 and
no gold match, with 12 blind gold-dust controls (10 called dust). Its 207 calls at `p_heal ≥ 0.4` went to the user in
the review tool, each crop shown with Opus's verdict and rationale as a note, a zoomable context panel (128–4096 px)
and new keys for hair and scratch. A second round (gd3) reviewed every classifier run's remaining unlabelled false
positives up to five per tile, so that the completed gold is fair to all compared runs.

| round | judged | sent to the user (Opus ≥ 0.4) | dust | hair / scratch | unsure | not dust |
|---|---|---|---|---|---|---|
| gd2: E19 ≥ 0.5 | 294 | 207 | 93 | 8 / 0 | 86 | 9 |
| gd3: all runs, ≤ 5 FP/tile | 265 | 76 | 40 | 0 / 2 | 32 | 2 |

Of the items the user decided either way, Opus's dust call held for 92 % in round one and 95 % in round two. Confirmed
points are stored outside the read-only dataset (`~/dustdet/gold_pass2/`) and form a new evaluation set,
**gold-dev2**: 495 points instead of 353, with the 117 "unsure" positions as uncertain targets that count neither as
hits nor as misses. The original gold-dev stays reproducible.

### 5.3 The real numbers

![Recall at 1, 5 and 20 false positives per tile on gold-dev (first labelling pass) and gold-dev2 (with the 142 reviewed points). The neural classifiers gain most at the strict end; the hand-built detector and the U-Net lose slightly because the added points are mostly faint dust they do not find](_assets/dust-det-gold-dev2-recall.png)

| run (gold-dev2) | @1 FP/tile (precision) | @5 | @20 |
|---|---|---|---|
| E1 hand-built | 0.16 (0.73) | 0.29 | 0.47 |
| E4h U-Net | 0.09 (0.61) | 0.24 | 0.24 |
| E15 two-branch | 0.35 (0.85) | 0.67 | 0.83 |
| **E19** | **0.49 (0.89)** | **0.74** | **0.87** |
| E19 seeds 2 / 3 | 0.41 / 0.45 | 0.73 / 0.72 | 0.86 |
| E20 | 0.41 (0.87) | 0.72 | 0.84 |

The ranking survived the correction, which is reassuring: E19 > E15 > E14b, and E20 within E19's seed range. The
absolute picture changed. At one false positive per tile, the best detector finds about half the dust at about 0.89
precision; in review mode it finds three quarters. Precision had been understated by every gold-dev number reported
before.

The same pattern holds on gold-test: of 142 unlabelled E19 detections there, Opus calls 77 likely dust. Those are in
the user's review now, so that the first gold-test checkpoint uses completed labels as well.

## 6. What the judges teach the pipeline

The judges' transcripts record which checks resolved hard cases. Each check is a classical vision operation that the
classifier, which sees a 64 px crop and a blurred 256 px context normalised by a constant, does not perform
explicitly:

| failure mode | what resolved it | classical operation |
|---|---|---|
| grain vs faint dust | spot vs its strongest neighbouring peaks | isolation: step ÷ 95th percentile of neighbours, rank |
| colour grain, tinted glints | colour at the spot vs a ring around it | relative chroma ratio |
| point lights, ripples (dark stratum: night scenes) | "does it repeat?" in a wide view | count of similar peaks within 100–200 px |
| highlights on contours | profiles along and across | structure-tensor coherence, distance to strong edges |
| hairs (weak as dots) | tracing the thread | Hessian ridge strength, ridge length |
| faint dust in dense areas | local contrast stretch | noise-normalised density |

DUST-006 implements these as `dustdet/features.py`: per-tile maps (DoG peaks with a KD-tree, relative chroma of the
density detail, structure tensor, distance transform, ridge map, local noise, film mask) sampled at candidate
positions, 14 features with NaN where undefined (chroma on black-and-white film). Two implementation details came from
tests on synthetic tiles:

- scikit-image's Frangi vesselness sets its sensitivity per image, so its values were not comparable across tiles (a
  pure-grain tile looked as ridge-like as a tile with a real line). The replacement is a scale-normalised Hessian
  measure with blob damping, computed on the noise-normalised density: a 3 px line scores 5.1 in units of local noise,
  the 99.5th percentile of grain 0.8, a round speck 0.9.
- Absolute density units failed too: at σ = 1, random grain produced higher ridge values than a real line. Hairs are
  2–6 px wide, so the ridge scales start at σ = 1.5.

Measured on E19's gold-dev2 detections, the strongest single features among the classifier's confident detections are
isolation (AUC 0.76), repetition within 100 px (0.74, more siblings means not dust) and edge strength on a ring around
the spot (0.70); ridges reach 0.79 on dark tiles. B1's existing local features are almost fully redundant with the
classifier's logit.

A stacker — gradient-boosted trees on the classifier logit plus these features — is the planned consumer. Two
measurements shaped its design:

- **A stacker fitted on gold is noise.** A grouped-CV preview on gold-dev2 showed +10 points of recall at 30 false
  positives before the second gold review and +2 after it, with ~600 rows. The stacker is trained on train-side labels
  only.
- **The base scores must be out-of-sample and the stacker must stay in its support.** E19's scores on its own training
  candidates are over-confident; but 98 % of the train-side review batch (hn2) were heal negatives E19's iso cut
  dropped from training, so its scores there are honest. Those items all have E19 ≥ 0.5, so the stacker re-ranks only
  that region and keeps E19's order below it. Applied to every detection, a smoke-test stacker fell from 0.49 to 0.32
  at 1 FP per tile; restricted to its support it matched E19 (0.47 vs 0.49) on provisional labels.

## 7. Engineering notes

- **Isolated judges.** `pi -p --no-builtin-tools --no-context-files --no-skills --no-prompt-templates` with tools only
  through a per-run `.mcp.json`; for Claude, `claude -p --tools Bash Read Write --allowedTools "Bash(<wrapper> *)"
  "Read(//<workdir>/**)" "Edit(//<workdir>/**)" --permission-mode dontAsk`. File writes need `Edit(...)` rules; a
  `Write(...)` rule alone left every write denied.
- **Answer extraction.** One fenced JSON block per run, extracted from the event stream, with repairs for three slips
  models actually made: a dropped key (`{"q003", …}`), a colon instead of a key (`{"q173": "kind": …}`), and raw
  newlines inside strings.
- **Throughput.** Prompt v3 made deepseek runs take 10–18 minutes (vs 3 with v1). Two batch runners share a run list
  through per-run atomic locks (`mkdir locks/RUN`); the judge script is swapped in by `mv` so in-flight processes keep
  the old file.
- **The Spark lost Wi-Fi twice.** The MediaTek MT7925 lost its access point, a scan never completed, and NetworkManager
  never retried, for six hours. The Spark is now on Ethernet; the inference container (`--rm`) is restarted by hand
  after a reboot.
- **Review tool.** dustview's review page gained a zoomable context panel, typed positives (dust, hair, scratch) and
  per-item notes; the judges' rationales appear next to each crop.

## 8. Where it stands and what comes next

| ticket | what | state |
|---|---|---|
| DUST-005 Part 1 | train-side label cleaning: 1,408 heal negatives E19 rates as dust (hn2), deepseek v3 pre-pass, Opus on the uncertain middle, labels → E21 (E19 + cleaned labels, 3 seeds) | deepseek running |
| DUST-005 Part 2 | run-neutral gold: gold-dev2 complete at 5 FP/tile for all runs; gold-test pass 2 in review; one gold-test checkpoint | gold-test in user review |
| DUST-006 | classical features + stacker: library, tests and feature report done; trainer built and smoke-tested; E22 (logit + B1 features) and E23 (+ new features) wait for hn2 labels | phase 2 ready |
| DUST-004 | infrared dust maps from VueScan RGBI scans | waiting for a test scan |

The common thread of this report is that the bottleneck moved from models to labels and measurement. The classifier
plateaued; the gold set undercounted; the judges, once measured on controls, turned out to be good enough to find what
the labels missed, as long as a person confirms what they find. The next gains are expected from applying the same
loop to the training labels and from giving the model the explicit context measurements the judges relied on.

## Key points

- In density, dust is an equal additive step in every channel: bright, neutral and independent of the scene.
- B1 candidates plus a two-branch classifier (E19) is the best detector; seeds differ as much as recent architectures.
- Heal-based validation ranks models backwards once they find unhealed dust; select on gold.
- Gold-dev undercounted dust at the strict end; with 142 reviewed additions, E19 finds about half the dust at 0.89
  precision at one false positive per tile, and three quarters at five.
- Judges are measured on blind controls; Opus is the best judge, deepseek the best cheap one; how much a model
  inspects predicts how well it judges.
- Prompts shape behaviour directly, and a cue that does not separate the population at hand makes a judge worse.
- The stacker trains off gold on out-of-sample train labels and re-ranks only within its training support.

## Sources

- **Repository:** `/Users/manuel/code/wesen/2026-11-07--dust-scanning`.
- **Tickets and diaries:** `ttmp/2026/11/07/DUST-002…/reference/01-diary.md`; `ttmp/2026/11/10/DUST-003…/reference/01-diary.md`
  (steps 1–12); `ttmp/2026/11/14/DUST-005…/reference/01-diary.md`; `ttmp/2026/11/14/DUST-006…/reference/01-diary.md`
  and its intern guide `design-doc/01-classical-vision-around-the-dust-classifier-intern-guide.md`.
- **Lab notebook and results:** `runs/NOTEBOOK.md`, `runs/results.csv`.
- **Code:**
  - `dustdet/classical.py` (B1), `dustdet/cands.py` (crops, `crop_iso`), `dustdet/models.py` (`TwoBranchClassifier`),
    `dustdet/train_cls.py` (`data.review`, `hardneg_frac`), `dustdet/evaluate.py` (gold-dev2), `dustdet/gold.py`
    (`extra_points`), `dustdet/features.py`;
  - DUST-003 scripts 06–20 (judge batches, prompts v2/v3, helpers, comparison, gold pass 2);
  - DUST-005 scripts 01–04 (headless Claude judge, batch runner, gold top-up, gold-test batch);
  - DUST-006 scripts 01–04 (feature previews, stacker table and trainer);
  - `dustview/review.go`, `dustview/static/review.js` (notes, context zoom, typed positives).
- **Related notes:** [[pi-coding-subagents-handbook|Handbook: running pi coding agents as measured subagents]].
- **Commits (selection):** edfb89f (E19), 94f1b2f (seed noise), ac2acaa (judge model comparison), eea378f (prompt v2),
  0dd136b (prompt v3, control check), f95d9fc (Claude probe), aeda7cb (gold pass 2 judged), 42ded7d (gold-dev2),
  6a01779 (features), ce5922f (stacker trainer).
