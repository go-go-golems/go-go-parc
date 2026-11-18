---
title: "Build a Reasoning Model (From Scratch) on a DGX Spark: Reproducing GRPO and Measuring What It Costs — A Technical Deep Dive"
aliases:
  - Reasoning Model From Scratch on DGX Spark
  - Reproducing GRPO on GB10
  - GRPO from scratch
tags:
  - project
  - reasoning-models
  - grpo
  - reinforcement-learning
  - dgx-spark
  - pytorch
status: active
type: project
created: 2026-11-18
repo: /home/manuel/code/others/reasoning-from-scratch
---

# Build a Reasoning Model (From Scratch) on a DGX Spark: Reproducing GRPO and Measuring What It Costs

This report records the first training experiment run against Sebastian Raschka's *Build a Reasoning Model (From Scratch)* on `bling`, an NVIDIA DGX Spark, on 18 November 2026. The book takes a pretrained Qwen3 0.6B base model and adds reasoning capability using inference-time techniques, reinforcement learning with verifiable rewards, and distillation. This report covers one complete circuit of the training path: a 50-step Group Relative Policy Optimization run, evaluated before and after on MATH-500.

The experiment succeeded. The base model scored 15.6% and the trained checkpoint scored 45.8%, a gain of 30.2 percentage points produced in fifteen minutes of training. Both figures were measured on this machine through the book's own evaluation pipeline. The book's published values for the same configuration are 15.2% and 45.6%.

The more durable result is the cost structure and the failure surface. Training was not the expensive part; evaluation was, by a factor of three. Two of the run's defects were silent, producing plausible-looking output while learning nothing or destroying a previous result. The reported training loop consumes roughly two thirds of its steps producing exactly zero gradient, by construction.

> [!summary]
> - **A 0.6B base model reached 45.8% on MATH-500 after 50 GRPO steps.** Training took 15m07s and peaked at 14.84 GB. The book's figure for the identical configuration is 45.6%, and its base-model baseline is 15.2%.
> - **Two environment failures were necessary before any training could run.** A missing `Python.h` blocked `torch.compile`, and a missing Dynamo configuration flag caused per-token recompilation that silently reduced generation to zero useful throughput.
> - **The token budget is a correctness parameter.** At `--max_new_tokens 96` the loop ran to completion, exited zero, and learned nothing, because the verifier could never observe a `\boxed{}` answer and every reward was structurally zero.
> - **32 of 50 steps produced exactly zero gradient**, because all four rollouts in a group scored identically. This is correct GRPO behaviour, and it means two thirds of the training compute is spent on steps that cannot change the model.
> - **Scripts overwrite tracked reference logs and each other's evaluation output.** `.gitignore` does not protect already-tracked files, and the evaluator's output filename contains neither the checkpoint nor a timestamp.

## 1. The platform and why it matches the book's reference hardware

The book's own benchmarks were run on this hardware generation, which makes the reproduction unusually direct: there is no cross-machine translation to argue about. The Spark pairs an ARM CPU with a Blackwell GPU that reports compute capability 12.1, abbreviated `sm_121`.

A compute capability identifies the instruction set of an NVIDIA GPU. CUDA code for such a device ships in two forms. **SASS** is native machine code for one specific capability. **PTX** is an intermediate representation that the driver compiles for the installed GPU when a kernel is first launched. A wheel built with `compute_120` PTX therefore runs on `sm_121` hardware, with the driver performing the final compilation once and caching the result.

That distinction explains the one warning that appears on every execution in this project and should not be treated as an error:

```
Found GPU0 NVIDIA GB10 which is of cuda capability 12.1.
Minimum and Maximum cuda capability supported by this version of PyTorch is
(8.0) - (12.0)
```

The installed PyTorch was compiled for capabilities up to 12.0 but embeds PTX for `compute_120`. The reported architecture list confirms it directly:

```
arch list: ['sm_80', 'sm_90', 'sm_100', 'sm_110', 'sm_120', 'compute_120']
```

| Property | Value |
|---|---|
| Host | `bling`, NVIDIA DGX Spark |
| CPU | aarch64, 20 cores (Cortex-X925 and Cortex-A725) |
| GPU | NVIDIA GB10, compute capability 12.1 |
| Memory | 121 GiB unified between CPU and GPU |
| Driver and CUDA | 580.178.04, CUDA 13.0 |
| Python | 3.12.15, uv-managed |
| PyTorch | 2.10.0+cu130 |
| Triton | 3.6.0 |

Unified memory is the property that matters for the training chapters. The GRPO loop holds a policy model, rollout buffers for long token sequences, and an activation graph for the backward pass simultaneously. On a discrete GPU all of that must fit in a fixed VRAM budget. Here the same 121 GiB serves both roles, so the book's stated ceiling of about 70 GB for its larger run is reachable without changing the code.

## 2. What the book's code requires, and what it declared

The companion repository at `https://github.com/rasbt/reasoning-from-scratch` is a Python package plus per-chapter directories. Two files describe the dependency set, and they differ in a way that determines which installation path works.

`requirements.txt` lists the versions a reader needs. `pyproject.toml` lists the same libraries but also declares a platform-specific package index:

```toml
[tool.uv.sources]
torch = [{ index = "pytorch-cu130", marker = "sys_platform == 'linux' and platform_machine == 'aarch64'" }]

[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

That marker matches this machine exactly. Resolving through `uv` therefore selects the CUDA 13.0 build of PyTorch for aarch64 automatically. The `pip` route reads only `requirements.txt`, which contains no such marker, and would install the default x86-oriented wheel. The two installation paths described in the book are not equivalent on this hardware, and the difference is worth roughly 40 tokens per second.

Three facts about the repository state are worth recording because they are not what the book says:

- The book states that the repository ships a `.python-version` file so that `uv` selects a compatible interpreter. It does not exist on `main`; the path returns 404. Section 3 shows that this omission is what makes the first environment failure reachable.
- `requirements.txt` lists `reasoning-from-scratch >= 0.1.2`, a PyPI package, so the `pip` path installs a published snapshot rather than the working tree. The `uv` path builds the local package.
- The metrics logs under `ch06/02_rlvr_grpo_scripts_intro/logs/` are tracked files containing the author's reference runs. Any local training run overwrites them. Section 8 develops this.

## 3. Two environment failures

Neither failure was caused by the book's code being wrong. Both were caused by the environment resolving to something valid but insufficient, which is the harder class to diagnose because the first symptom appears far from the cause.

### 3.1 A header that `torch.compile` needs and the system interpreter lacks

The first attempt to compile the model failed inside Triton's runtime build step:

```
torch._inductor.exc.InductorError: CalledProcessError: Command '['/usr/bin/gcc',
'/tmp/tmp5uwkuil9/cuda_utils.c', '-O3', '-shared', '-fPIC', '-Wno-psabi',
'-o', '...cuda_utils.cpython-312-aarch64-linux-gnu.so',
'-l:libcuda.so.1', ... '-I/usr/include/python3.12']' returned non-zero exit status 1.
```

The relevant argument is the last one. Triton compiles a small C extension at run time to query device properties, and that extension includes `Python.h`. `uv` had selected the system interpreter at `/usr/bin/python3.12`, version 3.12.3, and the `python3.12-dev` package is not installed on this host, so `/usr/include/python3.12/Python.h` does not exist.

Two repairs are possible. Installing `python3.12-dev` requires sudo. The alternative keeps every change inside the home directory: install a uv-managed interpreter, which ships its own include directory, and pin the project to it.

```bash
uv python install 3.12          # cpython-3.12.15, includes include/python3.12/
echo "3.12" > .python-version   # uv prefers the managed interpreter over the system one
rm -rf .venv && uv sync
```

After that, `Python.h` resolves under `/home/manuel/.local/share/uv/python/cpython-3.12.15-linux-aarch64-gnu/include/python3.12/` and compilation proceeds. The general lesson is that a Python interpreter being present says nothing about whether its development headers are, and only a build step reveals the difference.

### 3.2 Dynamic shapes that turn compilation into a per-token rebuild

With compilation working, the `--compile` flag on the chapter-2 script produced this:

```
Time: 161.09 sec
0 tokens/sec
```

Dynamo explained why in its recompilation log:

```
[0/8] last reason: 0/7: tensor 'cache.cache[0][0]' size mismatch at index 2.
      expected 16, actual 17
```

A key-value cache stores the attention keys and values for every token already processed, so that each new token attends over cached state rather than the full prefix. The cache is therefore a tensor whose sequence dimension grows by one on every step. TorchDynamo specializes a compiled graph on the shapes it observes. A dimension of 16 and a dimension of 17 are different specializations, so the model recompiles for every token it generates. Compilation cost dominates and throughput collapses.

PyTorch 2.8 introduced a configuration flag that tells Dynamo to treat integer attributes on modules as unspecified rather than specialized. The book's notebooks set it, and so do `reasoning_from_scratch/ch03.py`, `qwen3_optimized.py`, and `qwen3_batched.py`. The standalone script `ch02/05_use_model/generate_simple.py` does not, which makes `--compile` on that script a trap rather than an optimization.

```python
torch._dynamo.config.allow_unspec_int_on_nn_module = True
```

With the flag set, and with two warmup passes to exclude compilation from the measurement, the same KV-cached generator reported:

| Mode | This machine | Book's DGX Spark table |
|---|---|---|
| KV cache, eager | 75.2 tok/s | 68 tok/s |
| KV cache, compiled | 102.9 tok/s | 98 tok/s |

The machine is at or slightly above the reference figures once the recompilation problem is removed. A correct diagnosis changes the answer by a factor of about 100 rather than by a few percent, which is why "compilation made it slower" is never sufficient evidence that compilation is unsuited to the workload.

## 4. The GRPO algorithm as the book implements it

Before describing the run, this section states what the training actually computes, because the shape of the algorithm explains both the results and the wasted compute in Section 6.

The setting is reinforcement learning with verifiable rewards. A prompt is a mathematics problem. The reward is not learned from human preferences; it is computed by a deterministic program. The book's chapter 3 builds that program: extract the content of a `\boxed{...}` expression from the model's response, normalize it, and compare it for symbolic equivalence using SymPy. A response scores 1 if a correct final answer can be extracted and 0 otherwise. Nothing in between exists, so the reward is binary.

Group Relative Policy Optimization generates several complete responses to the same prompt and turns their rewards into a learning signal by comparison within that group. The pipeline has five stages, and the fourth is the one that distinguishes it from supervised fine-tuning.

```mermaid
flowchart TD
    P[Prompt from MATH training split] --> R[Generate N rollouts<br/>temperature 0.8, top-p 0.9<br/>max 512 tokens each]
    R --> V[Verifier<br/>extract boxed answer<br/>SymPy equivalence check]
    V --> RW[Binary rewards r_i in 0,1]
    RW --> A[Advantages<br/>a_i = r_i - mean r / std r]
    R --> LP[Sequence log-probs<br/>sum of token log-probs<br/>under current weights]
    A --> L[Policy gradient loss<br/>negative mean of a_i times logp_i]
    LP --> L
    L --> U[Backward, clip gradients, AdamW step]
    U --> R
    style V fill:#fde2e2
    style L fill:#dbeafe
```

### 4.1 Rollouts

A rollout is one complete sampled response. Sampling uses temperature 0.8 and top-p 0.9 rather than greedy decoding, because a deterministic decoder would return the same response N times and the group would contain no variation to compare. The generator keeps the end-of-sequence token inside the response so that long training runs do not unlearn how to stop.

### 4.2 Rewards

The verifier from chapter 3 supplies the reward. This is what replaces the reward model that a preference-based pipeline would train. Its consequence for the experiment is direct: the reward function cannot be gamed by fluent prose, only by producing a correct, extractable final answer.

### 4.3 Advantages

Advantages normalize each rollout against its own group:

```python
rewards = torch.tensor(rollout_rewards, device=device)
advantages = (rewards - rewards.mean()) / (rewards.std() + 1e-4)
```

The book's worked example uses rewards `[1., 1., 0., 0.]`, which produces advantages `[0.8659, 0.8659, -0.8659, -0.8659]`. A positive advantage raises the likelihood of the actions that produced that rollout; a negative advantage lowers it.

The arithmetic of this formula has a consequence that governs the entire training budget. If every rollout in a group receives the same reward, the numerator of every advantage is zero and the group produces no gradient at all. That happens in two distinct situations: all rollouts correct, and all rollouts wrong. Section 6 measures how often each occurred.

### 4.4 Sequence log-probabilities

The fourth stage computes, for each rollout, the sum of the log-probabilities of its generated tokens under the *current* weights:

```python
logps = torch.stack(rollout_logps)          # one scalar per rollout
pg_loss = -(advantages.detach() * logps).mean()
```

The sum is taken over the whole sequence rather than averaged per token. Averaging would divide each term by its response length and thereby rescale the learning signal, which is not part of the original GRPO formulation. Chapter 7 revisits token-level normalization when it adds further modifications.

`advantages` is detached because it acts as a fixed learning signal for this update; gradients must flow only through the log-probabilities, which are the only term that depends on the parameters being optimized.

The leading minus sign converts a maximization into a minimization, because PyTorch optimizers minimize. Minimizing the negated objective produces exactly the same parameter updates as maximizing the original.

### 4.5 What this variant omits

The chapter-6 implementation deliberately omits the KL divergence term that penalizes drift from a reference policy. The repository argues this from published results in DAPO, Dr. GRPO, and Olmo 3, all of which report that the KL term can hurt performance on mathematics tasks. Chapter 7 reintroduces it and shows both the stabilizing effect and a specific failure it can cause.

## 5. Designing a run that is small and still meaningful

Two probes preceded the real run. The first was cheap and revealed the trap that governs the rest of this section.

A three-step run with `--num_rollouts 2 --max_new_tokens 96` completed in 16 seconds and reported:

```
[Step 1/3] loss=-0.0000 reward_avg=0.000 tok/sec=41.6 avg_resp_len=51.0
[Step 2/3] loss=-0.0000 reward_avg=0.000 tok/sec=37.0 avg_resp_len=8.0
[Step 3/3] loss=-0.0000 reward_avg=0.000 tok/sec=31.6 avg_resp_len=8.0
```

Every reward is zero. The cause is structural rather than statistical: the verifier only awards credit for a final answer it can extract from a `\boxed{...}`, and a base model that has not been trained to produce that format does not reach a boxed answer within 96 tokens. Every rollout therefore scores zero, every advantage is zero, and the loss is exactly zero. The loop ran correctly and learned nothing.

A second probe used the book's token budget:

```
[Step 1/6] loss=-0.0000 reward_avg=0.000 tok/sec=65.3 avg_resp_len=229.2
[Step 3/6] loss=-0.0000 reward_avg=1.000 tok/sec=68.4 avg_resp_len=107.8
[Step 5/6] loss=13.7501 reward_avg=0.250 tok/sec=68.5 avg_resp_len=219.8
[Step 6/6] loss=11.3951 reward_avg=0.250 tok/sec=69.5 avg_resp_len=257.8
```

Rewards become non-zero, and step 3 shows `reward_avg=1.000` — a group in which all four rollouts were correct, which is equally gradient-free but for the opposite reason. Section 6 shows that this is not an edge case.

The final run used the book's chapter-6 configuration exactly, so that the outcome is comparable to a published number rather than being an uninterpretable one-off:

```bash
uv run ch06/02_rlvr_grpo_scripts_intro/rlvr_grpo_original_no_kl.py \
  --steps 50 --num_rollouts 4 --max_new_tokens 512 --show_eta
```

The `--skip-zero-advantage-updates` flag available in this script was deliberately not used, because it changes the run relative to the published baseline.

## 6. Training dynamics

The run finished with `exit=0` in `15m07.152s` and peaked at `Max CUDA memory allocated: 14.84 GB`.

Reward rose and so did response length. Grouping the fifty steps into five blocks of ten:

| Steps | Mean `reward_avg` |
|---|---|
| 1–10 | 0.175 |
| 11–20 | 0.400 |
| 21–30 | 0.575 |
| 31–40 | 0.775 |
| 41–50 | 0.650 |

Over the full run, `corr(step, reward) = +0.440` and `corr(step, response_length) = +0.526`. The mean reward was 0.515 with a standard deviation of 0.420, which is large relative to the mean and visible in the step-by-step output.

The joint movement of reward and length is the expected signature of this training procedure. A base model that answers in a few tokens cannot satisfy a verifier that requires a boxed derivation, so the only way for a rollout to become rewardable is to emit a longer response containing that derivation. Length and reward are coupled through the reward function and not merely correlated by accident.

### 6.1 Two thirds of the steps cannot change the model

The reward distribution over fifty steps was:

| `reward_avg` | Count | Gradient |
|---|---|---|
| 0.00 | 14 | none, all wrong |
| 0.25 | 9 | present |
| 0.50 | 5 | present |
| 0.75 | 4 | present |
| 1.00 | 18 | none, all right |

Thirty-two of fifty steps had a reward of either 0.00 or 1.00 with four rollouts, meaning every advantage in the group was zero and the backward pass produced no update. Only 18 steps had non-zero loss. The loss values observed ranged from −23.46 to +13.75, and their magnitude should not be read as a quality signal: a step where one rollout is correct and three are wrong produces large advantages and therefore a large loss, while a step where all four agree produces exactly zero regardless of how good the model is.

This yields a concrete efficiency observation. In this configuration roughly 64% of the sampling compute produced no gradient. The sampling is where nearly all the wall-clock time goes, because generating 512 tokens four times takes far longer than the backward pass over them. A training run at this scale is therefore dominated by generating responses that are then discarded.

The repository already provides the corresponding optimization. `--skip-zero-advantage-updates` detects the all-equal case and skips the backward and optimizer step. That saves the cheaper half of the work. The expensive half, sampling the rollouts in the first place, cannot be skipped, because whether the group is degenerate is only known after the rewards have been computed. Strategies that would address the sampling cost itself — larger groups to raise the chance of mixed outcomes, difficulty filtering to avoid problems the model always solves or never solves — are the subject of chapter 7.

### 6.2 What a step costs

| Configuration | Peak memory | Steps | Wall clock |
|---|---|---|---|
| 2 rollouts, 96 tokens | — | 3 | 16 s including load |
| 4 rollouts, 512 tokens | 10.14 GB | 6 | 61 s including load |
| 4 rollouts, 512 tokens | 14.84 GB | 50 | 15m07s |

The repository publishes a memory table for larger groups: 8 rollouts at 1,024 tokens requires 30.50 GB and 8 rollouts at 512 tokens requires 20.31 GB. Scaling to the book's 8-rollout configuration would roughly double training time per step to about 36 seconds, putting 50 steps near 30 minutes, still far below the multi-hour figures the book's prose associates with its larger runs.

## 7. Evaluation, and why it dominated the budget

The reward trend is a property of the training loop. Demonstrating that the model reasons better requires the held-out benchmark, and this is where the experiment's real cost appeared.

The book uses MATH-500: 500 problems sampled from the MATH dataset, deliberately disjoint from the 12,000 problems used for training. Evaluation renders each problem as a prompt, generates up to 2,048 tokens, extracts a boxed answer, and grades it against the reference with the same SymPy-based verifier used to produce training rewards.

```bash
uv run ch03/02_math500-verifier-scripts/evaluate_math500_batched.py \
  --dataset_size 500 --which_model base \
  --checkpoint_path ch06/02_rlvr_grpo_scripts_intro/checkpoints/rlvr_grpo_original_no_kl/qwen3-0.6B-rlvr-grpo-step00050.pth \
  --batch_size 128
```

Results, with both ends of the comparison measured on this machine:

| Model | MATH-500 | Samples | Eval time |
|---|---|---|---|
| Qwen3 0.6B base | **15.6%** | 78/500 | 9.5 min |
| + GRPO, 50 steps, 4 rollouts, 512 tok | **45.8%** | 229/500 | 46.3 min |
| Qwen3 0.6B official reasoning checkpoint (published, not run here) | 48.2% | — | — |

Against the repository's published baseline for the same configuration (15.2%) and the same trained configuration (45.6%), the reproduction is within 0.4 and 0.2 percentage points respectively. The gain is a factor of 2.9, achieved in fifteen minutes on one GPU.

The trained model landed within 2.4 points of the officially released Qwen3 0.6B reasoning checkpoint, which was produced with a substantially larger recipe. That is the central result of the experiment: at this model scale, a binary verifier plus a few dozen policy updates recovers most of what supervised reasoning training provides.

### 7.1 Evaluation costs more than training

The asymmetry in the table is the practically important finding. The same 500 problems, the same batch size, the same generated-token ceiling produced a 9.5-minute evaluation for the base model and a 46.3-minute evaluation for the trained one, a factor of 4.9.

The cause is batching and generation length. A batch of 128 sequences must remain allocated until its longest member finishes. The base model averages a short answer, so most batches free quickly. The trained model averages around 580 tokens per response and reaches the 2,048-token ceiling often, so each batch is padded to the longest trajectory in it and every sequence in the batch occupies that padded length. Training the model made evaluating the model five times more expensive, because the training taught it to think longer.

For the experiment as a whole the split was:

| Phase | Wall clock |
|---|---|
| Training (50 steps) | 15m07s |
| Evaluation, trained checkpoint | 46.3 min |
| Evaluation, baseline | 9.5 min |
| **Total** | **≈71 min** |

Two thirds of the time went to establishing that the training had worked. Any plan that treats evaluation as a cheap afterthought will mis-budget the work by a large factor. The batched evaluator is not an optimization but a requirement at this model scale: the book reports 185.4 minutes for a reasoning-model pass over MATH-500 on an H100 without batching, against 14.6 minutes with it. This run's batched pass took 46.3 minutes, about 3.2 times the H100 figure, so the unbatched path here is expected in the region of ten hours per checkpoint.

## 8. Defects found in the tooling

Four defects surfaced during this experiment. None is a bug in the algorithms; all four are properties of the scripts and of git's behaviour that would silently mislead a reader who did not check.

**The training script overwrites tracked reference logs.** `ch06/02_rlvr_grpo_scripts_intro/rlvr_grpo_original_no_kl.py` writes to `logs/rlvr_grpo_original_no_kl_metrics.{csv,txt}`, which are committed in the repository as the author's reference runs. After the training run, `git status` reported both as modified:

```
 M ch06/02_rlvr_grpo_scripts_intro/logs/rlvr_grpo_original_no_kl_metrics.csv
 M ch06/02_rlvr_grpo_scripts_intro/logs/rlvr_grpo_original_no_kl_metrics.txt
```

`.gitignore` lists `*.csv` and `*.txt`, which suggests protection that does not exist: ignore rules do not apply to files that are already tracked. The reference logs were preserved by copying this run's output elsewhere and restoring the tracked files with `git restore`.

**The metrics CSV accumulates across runs.** The file appends rather than truncates, so after three probe runs and the real run it contained 317 rows spanning four separate runs, with no column identifying which run a row belongs to. Exactly 258 of those rows are the author's tracked reference log, whose steps run 1 to 258; the remaining 59 are this project's three-step probe, six-step probe, and fifty-step run. Summed naively, it reported a mean reward of 0.572 and a step-to-reward correlation of −0.259, both of which are artifacts of mixing a 258-row reference run with a 50-row run of this project. Filtering on the `total_steps` column recovered the correct figures of 0.515 and +0.440. Any analysis of these logs must segment by run explicitly.

**The evaluator's output filename omits the checkpoint.** `evaluate_math500_batched.py` writes `math500_{which_model}-{device}-batched-bs{batch_size}.jsonl`. Because both evaluations used `--which_model base --batch_size 128`, the baseline run replaced the trained model's per-problem results. The headline accuracy survived only because it had already been recorded; the per-problem data needed to classify the 271 failures as format errors or reasoning errors was lost, and recovering it requires repeating a 46-minute evaluation.

**A standalone script omits a configuration flag its siblings set.** As described in Section 3.2, `generate_simple.py --compile` runs at zero useful throughput because the Dynamo flag is absent. The notebooks and three library modules set it, so the omission is inconsistent rather than deliberate.

## 9. Reproducing the experiment

The repository is a read-only upstream project. All local work is on the branch `local/spark-grpo-run`, which adds three files and modifies no source. `origin` remains the upstream repository and is never pushed to.

```bash
cd /home/manuel/code/others/reasoning-from-scratch

# Environment: uv-managed Python 3.12 is required for torch.compile.
uv python install 3.12
echo "3.12" > .python-version
uv sync                                    # resolves torch 2.10.0+cu130 for aarch64

# Train. Expect 15-20 minutes and about 15 GB.
uv run ch06/02_rlvr_grpo_scripts_intro/rlvr_grpo_original_no_kl.py \
  --steps 50 --num_rollouts 4 --max_new_tokens 512 --show_eta

# Evaluate. Rename the output immediately: the filename does not include the checkpoint.
uv run ch03/02_math500-verifier-scripts/evaluate_math500_batched.py \
  --dataset_size 500 --which_model base --batch_size 128 \
  --checkpoint_path ch06/02_rlvr_grpo_scripts_intro/checkpoints/rlvr_grpo_original_no_kl/qwen3-0.6B-rlvr-grpo-step00050.pth
mv math500_base-cuda-batched-bs128.jsonl math500_grpo-50.jsonl

# Restore the tracked reference logs that training overwrote.
git restore ch06/02_rlvr_grpo_scripts_intro/logs/

# Baseline for comparison.
uv run ch03/02_math500-verifier-scripts/evaluate_math500_batched.py \
  --dataset_size 500 --which_model base --batch_size 128
```

All training and evaluation artefacts are gitignored: `checkpoints/`, `math_train.json`, `qwen3/`, `*.pth`, `*.jsonl`. The run's metrics are preserved at `notes/runs/2026-11-18-grpo50/`, and the step-by-step record of the work, including both environment failures with their exact diagnostics, is at `notes/DIARY.md`.

Downloaded data: two model checkpoints of 1.5 GB each (base and reasoning) plus tokenizers, and the 12,000-problem MATH training split, fetched from `raw.githubusercontent.com/rasbt/math_full_minus_math500` with a Backblaze fallback. MATH-500 itself ships in the repository as `ch03/01_main-chapter-code/math500_test.json`, so no dataset library is needed.

## 10. Limitations and open questions

- The trained checkpoint's per-problem JSONL was lost, so the 271 failures have not been classified. The split between extraction failures and genuinely incorrect reasoning is unknown.
- Every timing is a single observation on one machine. No run-to-run variance was measured for either training or evaluation.
- The run used 4 rollouts and 512 tokens, the smallest configuration in the book's results table. The 8-rollout configuration, which the published 47.4% figure uses, was not run.
- Whether the same seed reproduces the same trajectory across GPUs is untested. The book notes that `cuda` and `mps` devices introduce floating-point differences and warns that results may vary.
- The reported correlation between step and reward (+0.440) mixes genuine learning with any difficulty ordering in the 12,000-problem dataset, which is not curriculum-sorted. Only the MATH-500 delta should be treated as evidence of capability.
- Chapters 7 and 8 were not run. The KL term, clipped policy ratios, format rewards, and distillation remain unverified here, and chapter 7's documented reward collapse to 0.4% is exactly the behaviour this configuration was not stressed enough to reveal.
- The reason the book associates multi-hour runtimes with chapter 6 was not established. This 50-step configuration took fifteen minutes, while the book's prose describes about twelve hours and 70 GB for "a few GRPO rounds"; the difference presumably lies in run length, rollout count, or the 2,048-token setting, and the published checkpoints extend to 9,000 steps.

## 11. Key points

- A binary verifiable reward and fifty policy updates moved a 0.6B base model from 15.6% to 45.8% on MATH-500, within 2.4 points of the officially reasoning-tuned checkpoint, in fifteen minutes of training.
- The token budget controlling how long a rollout may run is a correctness parameter. Too small a value produces a training loop that exits successfully, reports zero loss, and cannot learn, because the reward function never observes a rewardable answer.
- Group-relative advantages are exactly zero whenever all rollouts in a group tie, which occurred in 32 of 50 steps here, in both the "all wrong" and "all right" directions. Two thirds of the sampling compute produced no gradient by construction.
- Evaluation, not training, dominates the cost of a reasoning-model experiment: 46.3 minutes for the trained checkpoint against 9.5 minutes for the baseline on identical inputs, because longer generations make batch padding more expensive.
- A GPU warning about unsupported compute capability may be a correct description of a PTX-JIT path rather than an error. Checking the embedded PTX architecture list settles the question.
- When a compiled model slows to zero throughput, the decisive diagnostic is which shape is changing. A key-value cache changes length every token, and a missing Dynamo flag turns that into a rebuild per token.
- `.gitignore` provides no protection for files that are already tracked, so any script that writes into a directory of shipped reference logs will quietly modify the working tree.
- An evaluation artifact whose name omits the input's identity will eventually destroy a previous result, and the loss is discovered when the second run reports a different score than expected.

## Sources and related notes

- Book: *Build a Reasoning Model (From Scratch)*, Sebastian Raschka, Manning, 2026, ISBN 9781633434677. PDF and EPUB read from `/home/manuel/Documents/`.
- Code repository: https://github.com/rasbt/reasoning-from-scratch, local clone at `/home/manuel/code/others/reasoning-from-scratch`, branch `local/spark-grpo-run`, upstream commit `b864602`.
- Step-by-step record with full diagnostics: `/home/manuel/code/others/reasoning-from-scratch/notes/DIARY.md`, seven steps.
- Run artefacts: `/home/manuel/code/others/reasoning-from-scratch/notes/runs/2026-11-18-grpo50/` (metrics.csv, metrics.txt, stdout.log, baseline_stdout.log).
- Model weights: https://huggingface.co/rasbt/qwen3-from-scratch
- Training split: https://github.com/rasbt/math_full_minus_math500
- MATH-500: https://huggingface.co/datasets/HuggingFaceH4/MATH-500
- GRPO, from DeepSeekMath: https://arxiv.org/abs/2402.03300
- DAPO: https://arxiv.org/abs/2503.14476 — argues against the KL term on reasoning tasks
- Dr. GRPO: https://arxiv.org/abs/2503.20783
- DeepSeek-R1: https://arxiv.org/abs/2501.12948
- Other work on this machine: [[PROJECT REPORT - TRELLIS on DGX Spark - Porting Two Generations of Image-to-3D Models to aarch64 and sm_121 - A Technical Deep Dive]]
