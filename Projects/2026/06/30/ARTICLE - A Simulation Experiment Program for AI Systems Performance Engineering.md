---
title: "A Simulation Experiment Program for AI Systems Performance Engineering"
aliases:
  - codesign experiment program
  - GPU performance experiment catalog
  - researchctl experiment catalog
tags:
  - article
  - researchctl
  - cpu-gpu-codesign
  - simulation
  - experiments
  - roofline
  - occupancy
  - inference-serving
  - disaggregated-prefill-decode
status: active
type: article
created: 2026-07-01
repo: /home/manuel/workspaces/2026-06-30/benchmark-cpu-inference/researchctl
---

# A Simulation Experiment Program for AI Systems Performance Engineering

This article documents the complete set of simulation experiments designed to reproduce, in a deterministic discrete-event simulator, the performance concepts of *AI Systems Performance Engineering* (Chris Fregly, O'Reilly, 2025). The experiments span twelve chapters of the book, from storage input/output through CUDA kernel efficiency, instruction-level parallelism, dynamic scheduling, and large-scale inference serving. For each experiment the article states what it tests, the underlying hardware or software technique it models, how the simulator expresses it, what the experiment is expected to show, and what the result is useful for.

The simulator used is the `researchctl` codesign backend, a discrete-event scheduler over devices that estimate task cost. Every experiment reduces to a choice of device cost formula, workload shape, and scheduling policy. The article is organized by the layer of the system each experiment targets: the storage and data pipeline, the single kernel and memory hierarchy, the kernel and launch orchestration, and the multi-device inference serving system. A final section covers the experiments that require extending the simulator with new device families and explains why those extensions are necessary.

> [!summary]
> The program comprises forty-two experiments across twelve chapters. Twenty-nine are runnable today with the simulator's built-in primitives. Thirteen require new device types whose cost formulas express concepts the built-in devices cannot. Two experiments — a roofline arithmetic-intensity sweep and a disaggregated prefill-and-decode goodput comparison — have been validated and reproduce the book's claims deterministically. The article's purpose is to make the full program reviewable before the heavy implementation of extensions begins.

## The simulation substrate

Before the experiments, the substrate must be fixed. The codesign simulator models a system as a set of devices, a workload of requests, and a policy that assigns each task to a device. A device's cost model is a function called `Estimate` that returns a duration. The most important device for this program is the bandwidth device, whose duration separates the cost of moving data from the cost of computing on it.

```
transfer = ceil((bytesIn + bytesOut) / bandwidthBytesPerNs)
compute  = ceil(computeUnits / computeUnitsPerNs)
duration = setupNs + transfer + compute
```

This formula is the roofline primitive. Arithmetic intensity — compute work divided by bytes transferred — is the horizontal axis of the roofline model. By separating the transfer rate from the compute rate, the bandwidth device lets an experiment sweep arithmetic intensity and observe a task transition from transfer-dominated (memory-bound) to compute-dominated (compute-bound). The crossover, where transfer time equals compute time, is the roofline ridge point, and it is predictable analytically as the ratio of compute rate to memory rate.

Two structural properties of the simulator bound what it can express. First, the stages of a request run serially; there is no inter-stage overlap in the built-in model. Second, each device tracks a single busy-until timestamp, so it runs one task at a time. These properties make the simulator precise about which cost term dominates and about how scheduling decisions distribute work, but they prevent it from expressing the speedup that comes from overlapping independent operations. Experiments whose subject is overlap require a device whose duration takes the maximum of the transfer and compute terms rather than their sum. That device, called the pipelined device, is the single highest-leverage extension.

## Part I — The storage and data pipeline

The first layer of the system is the path from storage to the compute units. The book's fifth chapter is devoted to it, and its central concern is keeping that path full so the compute units never idle waiting for data.

### Aggregate storage bandwidth and GPU starvation

The foundational experiment in this layer tests whether the storage system can supply data fast enough to keep a compute device busy. The hypothesis is quantitative: if each compute unit requires a fixed rate of input bytes to stay saturated, then a storage device whose bandwidth falls below that rate starves the compute device, and the measured throughput of completed tasks plateaus regardless of further increases in compute speed.

The simulator expresses this with a two-stage request. The first stage, the load, runs on a bandwidth device modeling storage with a low memory rate. The second stage, the inference, runs on a bandwidth device modeling a GPU with a high compute rate. The experiment sweeps the storage device's memory rate while holding the GPU's compute rate fixed and measures the number of requests completed per unit of time. The expected result is a rising throughput curve that flattens once the storage rate can no longer feed the GPU. The use of this experiment is to size storage bandwidth against compute demand, which is the central planning question for large training clusters where hundreds of GPUs must each receive a steady byte stream.

### Direct storage access versus staged transfer

The second experiment models GPU Direct Storage, a technology that lets a GPU read from a storage device without first copying the data through host memory. The book reports approximately twenty percent higher read throughput from removing the host-memory bounce. The experiment tests whether modeling the bounce as an extra transfer stage through a host device adds latency proportional to the bounced bytes, and whether removing that stage yields the reported improvement.

The simulator expresses the staged path as three serial stages — storage to host, host to GPU, then compute — and the direct path as two stages: storage to GPU, then compute. The compute work is identical in both. The difference in latency between the two runs is the simulated cost of the host-memory bounce, and the ratio is the simulated throughput improvement. The use of the experiment is to justify the deployment complexity of GPU Direct Storage for a given workload, since the benefit depends on whether the path was transfer-bound in the first place.

### Compression as a memory-bandwidth trade

The third experiment tests the book's claim that storing data compressed reduces transferred bytes at the cost of decompression compute, and that the trade pays off only when the path is memory-bound. The hypothesis is that on a transfer-dominated device, halving the input bytes while adding decompression compute units lowers latency, while on a compute-dominated device the same change raises latency.

The simulator expresses this as two variants of a single stage at each tested arithmetic-intensity point. The compressed variant has half the input bytes and additional compute units representing decompression. The uncompressed variant has the original bytes and compute. Sweeping the base arithmetic intensity and comparing the two variants at each point should produce a crossover: the compressed variant wins below the roofline ridge and loses above it. The use of the experiment is to decide, for a given workload and device, whether on-the-fly decompression is worth the compute it costs.

### Storage striping for aggregate bandwidth

The fourth experiment models the book's striping technique, in which a file is distributed across multiple storage targets so that aggregate read bandwidth multiplies. The book gives the example of four targets each delivering five hundred megabytes per second combining for two gigabytes per second. The hypothesis is that adding parallel storage devices scales the aggregate completed-task rate roughly linearly until the compute stage becomes the bottleneck.

The simulator expresses this with one, two, and four storage bandwidth devices feeding a single GPU, using a policy that assigns each load task to the device that will finish earliest. The expected result is linear scaling that saturates when the GPU's compute rate can no longer absorb the combined storage bandwidth. The use of the experiment is to size the number of storage targets needed to balance a given compute capacity.

## Part II — The roofline and arithmetic intensity

The roofline model is the analytical core of the program. It appears in the sixth chapter and recurs throughout, because it provides the quantitative basis for deciding whether a kernel is limited by memory or by compute and therefore which optimization will help.

### The arithmetic-intensity ridge sweep

The canonical roofline experiment sweeps the arithmetic intensity of a single bandwidth device and observes the regime transition. The hypothesis, validated in the program, is that the task is memory-bound when the transfer time exceeds the compute time and compute-bound when the compute time exceeds the transfer time, and that the transition occurs exactly at the arithmetic intensity equal to the ratio of the device's compute rate to its memory rate.

The simulator expresses this with one bandwidth device running a fixed workload of requests on a single inference stage. A sweep varies the stage's compute units against its transferred bytes. The validated result shows the regime label flipping from memory-bound to compute-bound precisely where the analytic prediction places the ridge. For a device with a compute rate of twenty units per nanosecond and a memory rate of eight bytes per nanosecond, the ridge lies at arithmetic intensity two and a half, and the sweep confirms the transition between one and three. The use of this experiment is foundational: it establishes that the simulator faithfully expresses the roofline, which is the model underlying every subsequent memory-versus-compute decision.

### Kernel fusion

The sixth and ninth chapters describe kernel fusion, the combination of sequential operations into a single kernel so that intermediate results never traverse global memory. The book's example fuses a sine followed by a square root so that each input element is loaded once rather than twice. The hypothesis, validated in the program, is that a fused stage has higher arithmetic intensity and lower latency than two unfused stages with an intermediate memory round-trip.

The simulator expresses the fused variant as a single stage with one read and one write, and the unfused variant as two serial stages where the first writes an intermediate value that the second reads. The validated result shows the fused stage's arithmetic intensity at two point six against the unfused one point six, with fused latency approximately thirty-six percent lower. The use of the experiment is to quantify the benefit of fusion, which is the compiler's primary tool for raising arithmetic intensity without changing the algorithm.

### Reduced precision

The ninth chapter describes reduced precision as a way to raise arithmetic intensity by halving or quartering the bytes per element. Moving from thirty-two-bit to sixteen-bit floats halves the transferred bytes and doubles the arithmetic intensity; eight-bit and four-bit formats halve again. The hypothesis is that halving the input bytes on a memory-bound device doubles the arithmetic intensity and halves the transfer time, with the latency improvement largest when the device is transfer-dominated and vanishing as the device becomes compute-bound.

The simulator expresses this by sweeping the input bytes of a single stage through powers of two while holding compute fixed. The expected result is a transfer time that halves at each step and a latency that converges to the compute-only floor as arithmetic intensity rises. The use of the experiment is to predict the throughput gain from adopting lower-precision tensor-core formats, which is among the highest-impact optimizations available on modern hardware.

### Structured sparsity

The ninth chapter describes two-to-four structured sparsity, in which half the weights are pruned so that each memory load delivers twice as many useful values, raising arithmetic intensity by nearly a factor of two. The simulator expresses this identically to reduced precision — halving the input bytes — because the measurable effect is the same: fewer bytes transferred per unit of compute. The hypothesis and expected result match the reduced-precision experiment. The distinction is conceptual: sparsity removes bytes because they are zeros, while reduced precision removes bytes because each element is smaller. The simulator models the effect; the experiment states the cause in the hypothesis. The use is to predict the inference speedup from pruning, which the book places near two times for suitable workloads.

### Recomputation against memory

The ninth chapter describes recomputation as a trade of compute for memory: recomputing a value in registers can be faster than loading a precomputed value from global memory when the path is memory-bound. The hypothesis is that on a memory-bound device a variant with more compute and fewer bytes has lower latency, and that on a compute-bound device the ordering reverses, with the crossover at the same roofline ridge.

The simulator expresses this as two variants per arithmetic-intensity point: a loading variant with more bytes and less compute, and a recompute variant with fewer bytes and more compute. Sweeping the base intensity should show the crossover at the ridge. The use of the experiment is to decide whether activation checkpointing and on-the-fly recomputation help a given workload, which matters for fitting large models into limited memory.

### Batching for amortized memory traffic

The ninth chapter describes batching as a way to amortize shared memory traffic — such as weight loads — over more compute. The hypothesis is that scaling the compute units of a stage while holding the shared input bytes roughly fixed raises the arithmetic intensity and lowers the latency per unit of work. The simulator expresses this by scaling compute units with sub-linear growth in input bytes. The expected result is a per-unit-work latency that falls as the batch grows. The use is to predict the throughput curve of batched inference, which determines the economical batch size for a serving system.

## Part III — Occupancy, memory access, and warp efficiency

The seventh and eighth chapters address the efficiency of work running on a single streaming multiprocessor. These chapters introduce concepts that the built-in single-slot device cannot fully express, because they concern concurrency within a device and the cost of disordered execution.

### Coalesced versus strided memory access

The seventh chapter describes coalesced memory access, in which the threads of a warp load contiguous addresses that the hardware combines into one wide transaction, against strided or random access, which generates many small transactions and wastes bandwidth. The hypothesis is that inflating the effective transferred bytes by a waste factor derived from the access pattern raises the transfer time and lowers throughput proportionally.

The built-in bandwidth device uses a fixed function of bytes for its transfer cost and cannot model the inflation. The experiment requires an access-pattern device whose transfer cost multiplies the bytes by a waste factor: one for coalesced access, approximately the stride for strided access, and higher for random access. Sweeping the waste factor should reproduce the efficiency curve the book describes, with throughput falling as the pattern becomes more irregular. The use is to quantify the cost of poor memory layout, which is among the most common and most fixable performance problems.

### Warp divergence

The eighth chapter describes warp divergence, in which threads of a warp take different branches and the hardware executes each branch serially, multiplying the effective work by the number of paths. The book notes that removing one divergent branch can nearly double throughput. The hypothesis is that scaling the effective compute units by a divergence factor raises the compute time and lowers throughput, with a factor of two corresponding to a fifty-fifty branch split.

This experiment requires a divergence device whose compute cost multiplies the compute units by a divergence factor between one and the number of branch paths. The expected result is a throughput that falls linearly with the factor, halving at a factor of two. The use is to quantify the cost of control-flow irregularity and to motivate the partitioning or predication techniques that remove it.

### Occupancy and latency hiding

The sixth and eighth chapters describe occupancy, the fraction of a streaming multiprocessor's warp slots that are active, as the mechanism by which a GPU hides memory latency: when one warp stalls on a load, another runs. The hypothesis is that a device with more concurrent slots sustains higher throughput under memory-bound workloads because a stalled slot does not block ready tasks.

This experiment requires a multi-slot device that tracks several busy-until timestamps, one per slot, and assigns each arriving task to the earliest available slot. The expected result is that throughput under a memory-bound workload rises with the slot count up to the point where the compute rate saturates, while under a compute-bound workload additional slots do not help. The use is to model the latency-hiding benefit of high occupancy, which is the foundational reason GPUs run thousands of threads.

## Part IV — Pipelining and orchestration

The tenth and eleventh chapters address the overlap of memory operations with computation, first within a kernel and then across kernels on separate streams. These chapters are the primary consumers of the pipelined device extension, because overlap is precisely what the serial built-in formula cannot express.

### Intra-kernel pipelining

The tenth chapter describes double-buffered pipelines in which the load of one tile overlaps the compute of the previous tile, hiding the load latency behind ongoing arithmetic. The hypothesis is that a device whose duration takes the maximum of the transfer and compute times, rather than their sum, exhibits lower latency than the serial model, with the speedup growing as the two terms balance.

This experiment requires the pipelined device. The expected result is that the overlap model's latency approaches the maximum of the two terms while the serial model's latency remains their sum, and the gap is largest when transfer and compute are balanced. The use is to model the benefit of the producer-consumer pipelines that underlie high-throughput tensor-core kernels.

### Warp specialization

The tenth chapter describes warp specialization, in which warps take distinct roles such as memory loader, compute unit, and storer, running concurrently within a block. This experiment requires a workload model in which a request has multiple concurrent stage-roles on one device, which is the multi-slot device combined with the pipelined formula. The use is to model the architecture of modern attention kernels, which are built on specialized producer and consumer warps.

### Inter-kernel stream overlap

The eleventh chapter describes CUDA streams, which let independent kernels run concurrently so long as hardware resources permit. The hypothesis is that running independent requests on a multi-slot pipelined device yields higher aggregate throughput than serial execution, with the gain bounded by resource contention. This experiment requires the multi-slot and pipelined devices together. The use is to model the concurrency that streams provide, which is the basis for overlapping computation with data transfer.

### Launch overhead and CUDA graphs

The twelfth chapter describes CUDA graphs, which capture a sequence of kernel launches and replay them, amortizing the per-launch overhead. The book emphasizes that the benefit is largest for many small launches. The hypothesis, which is runnable today, is that with a large request count the total latency is dominated by the per-request setup overhead, and reducing that overhead lowers the total latency proportionally.

The simulator expresses this with the setup-overhead field of a device. The experiment runs a large workload at two setup-overhead values and compares the total latency. The lower-overhead run models the graph-captured path. The expected result is that the relative improvement grows with the request count, because the overhead is paid per request. The use is to quantify the value of launch-overhead reduction, which is significant for the many small kernels characteristic of autoregressive decoding.

### Dynamic scheduling with atomic work queues

The twelfth chapter describes atomic work queues, in which thread blocks pull work dynamically to balance load across multiprocessors and avoid the idle periods that arise from uneven static assignments. The book describes batching the atomic operations to reduce contention. This experiment requires a variable-work workload, in which requests have differing compute requirements, and a batching policy that claims several tasks at once. The expected result is that dynamic balancing reduces the idle fraction compared to static assignment, and that batching the claims reduces contention overhead. The use is to model the load-balancing strategies used by persistent kernels.

## Part V — Inference serving and disaggregation

The serving chapters — fifteen, seventeen, eighteen, and nineteen — are the most thoroughly simulatable in the book because they concern scheduling and placement rather than intra-device cost formulas. Sixteen of the eighteen serving experiments are runnable with the built-in primitives. The central concept is disaggregated prefill and decode.

### Disaggregated prefill and decode goodput

The seventeenth chapter describes disaggregation, the assignment of the prefill phase and the decode phase to separate pools of GPUs to eliminate the interference that arises when they share a device. The book reports that disaggregation can raise goodput — the rate of requests meeting both a time-to-first-token and a time-per-output-token target — by several times. The hypothesis, validated in the program, is that when arrivals outpace a single-slot device's service time, a colocated device backs up because a long prefill blocks decode work, while disaggregation onto two devices lets the phases overlap across requests and relieves the backlog.

The simulator expresses the colocated baseline as a single bandwidth device running a heavy prefill stage and a light decode stage serially. The disaggregated variant uses a fast-compute prefill device and a high-bandwidth decode device with a small transfer stage between them representing the key-value cache handoff. The validated result, under an arrival rate that exceeds the single-slot service rate, shows the colocated p95 latency at thirty-four thousand nine hundred forty-four nanoseconds against the disaggregated eight thousand two hundred sixty, a factor of four point two reduction, with goodput within a latency target rising from eighty percent to one hundred percent. The use of this experiment is foundational for serving system design: it establishes that disaggregation helps precisely when interference is present, and it quantifies the gain.

### Prefill and decode pool sizing

The seventeenth chapter describes the two-prefill-one-decode configuration studied in the DistServe system, in which goodput per GPU is the minimum of the prefill and decode pool throughputs divided by the total GPU count. The hypothesis is that goodput is bounded by the slower pool and that the optimal pool ratio matches the workload's prefill-to-decode service-time ratio. The simulator expresses this with a configurable number of prefill and decode devices, and the experiment sweeps the ratio to find the goodput peak. The use is to size serving clusters, where over-provisioning one pool wastes hardware and under-provisioning it bounds the system.

### Latency-first versus throughput-first batching

The seventeenth chapter contrasts latency-first scheduling, which processes each prompt immediately at low utilization, with throughput-first scheduling, which batches prompts to raise arithmetic intensity at the cost of batching delay. The hypothesis is that the optimal batch size depends on load: small batches minimize latency at low load, and large batches maximize throughput at high load. The experiment models a batch as a single request with scaled compute and sweeps the batch size and arrival rate. The use is to choose the scheduling policy that meets a service-level objective at the lowest cost.

### Head-of-line blocking

The seventeenth chapter describes head-of-line blocking, in which a long prompt at the front of a first-in-first-out queue delays shorter prompts behind it, amplifying tail latency. The hypothesis is that under a first-in-first-out policy with variable request sizes, the ninety-ninth percentile latency is dominated by the longest request, and that a shortest-job-first or class-based policy tightens the tail. The simulator expresses this with a variable-compute workload. The use is to motivate priority scheduling and the length-based routing that modern serving systems use.

### Parallelism strategies

The fifteenth chapter describes the four parallelism strategies used to serve large models across many GPUs. Tensor parallelism splits a layer's matrices across GPUs for near-linear speedup on compute-bound layers at the cost of an all-reduce synchronization. Pipeline parallelism assigns different layers to different GPUs for memory scaling at the cost of pipeline bubbles on single-token decoding. Data parallelism replicates the entire model for throughput scaling at the cost of multiplied memory and no per-query latency gain. Expert parallelism distributes the experts of a mixture-of-experts model across GPUs at the cost of all-to-all communication.

Each strategy is expressible in the simulator as a topology and policy choice. Tensor parallelism is multiple devices each performing a fraction of a stage's compute. Pipeline parallelism is serial stages on different devices. Data parallelism is replicated devices with a spreading policy. Expert parallelism is multiple expert devices with a routing policy. The use of these experiments is to predict the throughput and latency of each strategy for a given model and hardware topology, which is the central configuration problem of large-model serving.

### Speculative decoding

The fifteenth chapter describes speculative decoding, in which a small draft model proposes several tokens and a large target model verifies them in a single batched pass, achieving approximately a two-times speedup in practice. The hypothesis is that modeling a decode step as producing several tokens at once reduces the number of serial steps by the draft depth, lowering end-to-end latency provided the draft acceptance rate is high. The simulator expresses this by comparing a one-token-per-step decode against a multi-token-per-step decode with scaled compute. The use is to predict the speedup from speculative decoding and to understand how it depends on the acceptance rate.

### Expert load balancing and capacity factor

The fifteenth chapter describes the capacity factor, a parameter that caps the tokens each expert processes per batch and routes overflow to a second-choice expert, smoothing the load imbalance that arises when the gating network concentrates tokens on a few hot experts. The hypothesis is that under uneven routing, one expert device saturates while others idle, raising tail latency, and that a capacity-factor policy that reroutes overflow lowers the tail. The simulator expresses this with multiple expert devices and a routing policy. The use is to tune the capacity factor, which the book places commonly at one point two, against the quality cost of rerouting.

### Heterogeneous hardware

The eighteenth chapter describes heterogeneous hardware, in which compute-optimized GPUs serve the prefill phase and memory-optimized GPUs serve the decode phase, achieving the Splitwise study's reported two-point-three-five-times throughput improvement at the same cost and power as a homogeneous deployment. The hypothesis is that matching each phase to the device it stresses yields higher goodput per unit of cost than a homogeneous pool, because each device is used where its cost-performance is best. The simulator expresses this with two device profiles — high compute rate and low bandwidth for prefill, low compute rate and high bandwidth for decode — against a homogeneous mid-range device, with a cost attribute per device. The use is to evaluate the cost-performance of mixed-GPU deployments, which is a significant economic question at the scale of hundreds of thousands of GPUs.

### Admission control and early rejection

The eighteenth chapter describes early rejection, in which a system that predicts it cannot meet a request's latency target refuses it immediately rather than queueing it and missing the deadline, preserving goodput for the requests it does accept. The hypothesis is that under overload, rejecting requests that would breach the target keeps accepted-request latency within bounds, whereas accepting everything causes latency to collapse as queues grow. The simulator expresses this with a workload whose arrival rate exceeds capacity. The use is to set admission thresholds, which determine whether a serving system degrades gracefully or catastrophically under load spikes.

### Adaptive batching and parallelism

The nineteenth chapter describes adaptive batching, which adjusts the batch size by load, and adaptive parallelism, which routes requests to differently-sharded model instances by length. The hypotheses are that an adaptive batch size holds latency low at low load while raising throughput at high load — strictly dominating any fixed batch size across the load range — and that a length-based parallelism selector beats a single fixed strategy. The simulator expresses these as policy decisions over load and request length. The use is to design the runtime schedulers that modern inference engines use to meet service-level objectives under varying traffic.

## Part VI — Extensions and the experiments they unlock

Thirteen experiments require device families that the built-in registry does not provide. Each extension is a new device type implementing the device interface and registered alongside the built-ins; the simulator's dispatch loop does not change. The extensions and the experiments they unlock are as follows.

The pipelined device, whose duration is the maximum of the transfer and compute terms rather than their sum, unlocks intra-kernel pipelining, inter-kernel stream overlap, and the overlap of key-value cache transfer with computation. It is the highest-leverage extension because it is the only one that lets the simulator express the overlap of independent operations, which is the subject of three chapters.

The multi-slot device, which tracks several busy-until timestamps and assigns each task to the earliest available slot, unlocks occupancy and latency hiding, warp specialization, and continuous batching within a single GPU. It is the device that models concurrency within a device, which the single-slot built-in cannot.

The access-pattern device, whose transfer cost multiplies the bytes by a waste factor derived from the access pattern, unlocks coalesced versus strided versus random memory access. The divergence device, whose compute cost multiplies the compute units by a divergence factor, unlocks warp divergence. These two are direct translations of the book's efficiency concepts into cost formulas.

A tiered-storage device would unlock key-value cache offloading across the GPU, CPU, and solid-state tiers. A batching policy and a variable-work workload would unlock the dynamic-scheduling experiments. These extensions are smaller in scope than the device families but are needed for the twelfth-chapter experiments on atomic work queues.

The sequencing of these extensions follows their leverage. The pipelined device comes first because it unlocks the most experiments and because settling its cost formula — the maximum of two terms rather than their sum — forces the precision that the later extensions depend on. The multi-slot device comes second because occupancy and continuous batching are foundational to the serving experiments' fidelity. The access-pattern and divergence devices are isolated additions that can come in any order.

## What the program is for

The program is not a substitute for measuring real hardware. The simulator is deterministic and its device formulas are simplifications. Its value is that it lets a researcher ask, cheaply and reproducibly, whether a quantitative relationship holds across a sweep of one parameter, and it lets that question be asked before the expensive work of hardware measurement or runtime implementation.

Each experiment is designed so that its result is checkable. The roofline ridge is predictable analytically; the disaggregation benefit appears only when arrivals outpace service; the fusion improvement is a direct consequence of removing a memory round-trip. When a simulated result matches its analytic prediction, the researcher has evidence that the model expresses the concept faithfully. When it does not, the model or the experiment is wrong, and the discrepancy is itself the finding.

The program's output is a set of validated relationships — which techniques help which workloads, where the crossovers lie, how the gains scale — that guide the expensive implementation work. The device extensions turn currently-blocked experiments into runnable ones, and the sweep specification turns shell-driven sweeps into first-class experiment types. Together they convert the simulator from a single-run tool into an experiment platform for the performance concepts of an entire book.

## Related notes

- The simulation substrate and the chapter five-through-eight catalog: `Projects/2026/06/30/PROJECT REPORT - researchctl CPU GPU Codesign Experiment Runtime Deep Dive.md`.
- The experiment-extraction methodology and the chapter nine-through-twelve and serving catalogs: `Projects/2026/06/30/ARTICLE - researchctl Codesign Experiment Setup Chapter Mapping and API Refinement.md`.
- The requested simulator extensions (experiment types, device families, JavaScript callbacks): `Projects/2026/06/30/ARTICLE - researchctl Codesign Experiment Setup Chapter Mapping and API Refinement.md`, section on API refinements.
- The book was prepared as Markdown by the tool documented in `Projects/2026/06/30/ARTICLE - epub-extract A Born-Digital EPUB to Markdown Pipeline.md`.
- Source repository: `github.com/wesen/researchctl`, branch `task/benchmark-cpu-inference`, tickets RESEARCHCTL-004 and RESEARCHCTL-005.
