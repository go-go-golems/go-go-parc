---
title: "SparkBricks Day Two Results: Reference Choice, Caller Precision, Evo 2 40B and Long Proteins"
aliases:
  - SparkBricks day two results
  - DGX Spark whole-genome accuracy and Evo 2 40B
tags:
  - project
  - sparkbricks
  - dgx-spark
  - genomics
  - unified-memory
status: active
type: project
created: 2026-11-12
repo: /home/manuel/code/wesen/2026-10-11--parabricks-benchmarks
---

# SparkBricks Day Two Results: Reference Choice, Caller Precision, Evo 2 40B and Long Proteins

This note follows [[PROJECT REPORT - SparkBricks - Large Biological Models on a DGX Spark - What Fits in 128 GB]], written on the morning of 12 November 2026 while four systemd queues were still running on `bling`, the DGX Spark (one GB10 GPU, 128 GB of memory shared by CPU and GPU). By 13:20 UTC all four queues had finished. This note records what they showed. Every queued benchmark ran to completion. Together the runs answer the accuracy question left open on day one, finish the HaplotypeCaller-versus-DeepVariant comparison at whole-genome scale, and settle two capacity questions: Evo 2 40B runs, and ESMFold folds nearly 2,000 residues.

> [!summary]
> - **The day-one recall gap came from the reference, not the machine.** On the GRCh38 no-alt analysis set, DeepVariant reaches SNP F1 0.9954 and INDEL F1 0.9908 on HG002 30×, up from 0.9836 / 0.9813 on the reference shipped with the Parabricks sample data. Missed SNPs fell from 101,183 to 23,419.
> - **On an accurate reference, the two callers differ almost entirely in precision.** Unfiltered HaplotypeCaller reaches nearly DeepVariant's recall (0.991 vs 0.993) but makes 5.4× as many SNP false positives, for a run that is only 5 % shorter. DeepVariant on the Spark is CPU-bound: 20 Arm cores at 99.5 % for 29 minutes.
> - **Evo 2 40B runs on one Spark.** The streaming loader passed its bit-exact gate on the 7B, loaded 41.1 B parameters (76.6 GiB) in under ten minutes, and scored 8 kb windows at 585 tokens/s. A 32 kb window does not fit. Generation runs at 2.05 tokens/s, 77 % of the memory-bandwidth bound.
> - **Chunked attention removes ESMFold's length limit at no cost.** At 1,005 residues the chunked structure is identical to the unchunked one, in the same time, using a third of the memory. A 1,953-residue protein folds in 54 minutes in 32.7 GiB.

## 1. What ran

The queues were chained systemd user units (see section 6 of the previous note). In order:

| Queue | Items | Wall-clock (UTC) |
|---|---|---|
| `genomics` | P03 DeepVariant on the no-alt reference; P03 HaplotypeCaller; P02 DeepVariant and HaplotypeCaller from the sample-reference BAM; P01 quiet reruns of four fq2bam variants | 06:04–10:13 |
| `evo40` | streaming-loader gate on Evo 2 7B, then Evo 2 40B (warmup + measured) | 10:13–10:44 |
| `fold` | ESMFold with chunked attention at 1,024, 1,536 and 2,048 residues | 10:44–12:14 |
| `p02noalt` | gate: register the no-alt BAM as a dataset; then P02 DeepVariant and HaplotypeCaller on it | 12:14–13:20 |

The `p02noalt` gate exists because of a working rule from day one: no downloads or hashing while a timed run is active. Registering a BAM hashes about 40 GiB, so it waits until every timed run before it has finished.

## 2. The reference was the recall problem

On day one, DeepVariant on HG002 30× reached SNP recall of only 0.970. The misses were concentrated in the MHC region on chromosome 6 and a few other duplicated regions. In those regions most reads had mapping quality 0. The hypothesis was the reference: the GRCh38 shipped in the Parabricks sample bundle contains 261 ALT contigs, 525 HLA contigs and 2,385 decoys, and the GPU BWA-MEM in Parabricks is not alt-aware. A read from MHC therefore matches the primary chromosome and an HLA contig equally well, receives mapping quality 0, and the caller ignores it.

The test was to rerun the identical pipeline on the GRCh38 no-alt analysis set: the primary assembly plus unplaced and unlocalized contigs and chrEBV, with no ALT, HLA or decoy contigs.

| DeepVariant, whole genome | Sample-bundle reference | No-alt reference |
|---|---|---|
| SNP precision / recall / F1 | 0.9977 / 0.9699 / 0.9836 | 0.9979 / 0.9930 / 0.9954 |
| INDEL precision / recall / F1 | 0.9938 / 0.9692 / 0.9813 | 0.9939 / 0.9877 / 0.9908 |
| SNP misses (FN) | 101,183 | 23,419 |
| SNP misses on chr6 | 22,994 | 1,107 |
| Wall-clock | 67.5 min | 70.2 min |

Two details matter beyond the headline. First, misses fell outside the named hotspots too: from 75,558 to 22,852 (−70 %). The extra contigs were costing recall across the whole genome, not just in MHC. Second, alignment took the same time on both references (2,300 vs 2,350 s), so the extra contigs do not explain the open question from day one: whole-genome alignment runs at half the per-base speed of the small sample data.

For comparison, the only published truth-set accuracy for a Parabricks 4.8.0-1 DeepVariant run on HG002 (NVIDIA's Complete Genomics on AWS guide, DNBSEQ-T7 reads rather than Illumina) is SNP F1 0.9928 and INDEL F1 0.9922.

The remaining densest clusters of misses (chr9 at 67 Mb and 39 Mb, chr8 at 7 Mb, chr1 at 120 Mb, chr15 at 21 Mb) lie near centromeres or in known segmental duplications. That is placement by coordinates only; the reads there have not been inspected.

## 3. HaplotypeCaller against DeepVariant

`pbrun germline` runs the GATK-style pipeline: fq2bam, then HaplotypeCaller. Two facts shape how to read its numbers. First, the config passes no `--knownSites`, so no BQSR is applied, even though the Parabricks log names the stage "Marking Duplicates, BQSR". Second, Parabricks applies no VQSR or hard filters, so every HaplotypeCaller record has FILTER `.`. The precision below is therefore that of the raw caller.

Each caller was measured three ways: end to end from FASTQ (P03), and caller-only from a ready BAM (P02) on each reference. Caller-only matters because NVIDIA's published tables time DeepVariant from a BAM.

| | DV, sample ref | DV, no-alt | HC, sample ref | HC, no-alt |
|---|---|---|---|---|
| Caller-only time | 26.9 min | 29.0 min | 25.5 min | 27.5 min |
| SNP precision / recall / F1 | 0.9977 / 0.9699 / 0.9836 | 0.9979 / 0.9930 / 0.9954 | 0.9921 / 0.9680 / 0.9799 | 0.9885 / 0.9910 / 0.9897 |
| SNP false positives | 7,421 | 7,179 | 25,979 | 38,733 |
| INDEL F1 | 0.9813 | 0.9908 | 0.9776 | 0.9855 |
| CPU / GPU mean utilisation | 99.5 / 86.6 % | 99.6 / 87.6 % | 72.8 / 61.1 % | 73.4 / 58.1 % |

Three findings come out of this table.

**The calls are deterministic.** Each caller-only run produced exactly the same TP/FP/FN counts as the end-to-end run of the same caller on the same reference. For HaplotypeCaller that is true even though the caller-only run read the BAM written by the *DeepVariant* pipeline. The two pipelines therefore produce equivalent alignments, and the stage times taken from end-to-end runs are a fair stand-in for NVIDIA's per-tool timings.

**The reference switch moves the callers' precision in opposite directions.** On the no-alt reference, reads that used to be lost to HLA and ALT contigs now map into MHC and other duplicated regions. Those regions produce candidate variants that are not real. DeepVariant's network rejects them: its false positives stay flat (7,421 → 7,179). Unfiltered HaplotypeCaller keeps them: its false positives rise by 12,754. So on an accurate reference the gap between the callers is almost entirely precision: 5.4× the SNP false positives for HaplotypeCaller, at nearly the same recall. GATK hard filters would close part of that gap; that variant has not been run.

**DeepVariant on the Spark is limited by the CPU.** For the whole 27–29 minutes the 20 Arm cores average 99.5 % while the GPU sits at 87 %. DeepVariant's CPU side generates the pileup images the network classifies, and on this machine that is the bottleneck. Against published single-GPU DeepVariant-from-BAM times (Parabricks 4.5, read off a chart), the Spark is 1.9× slower than one H100 PCIe (≈13.8 min) and 3.0× slower than one RTX PRO 6000 (≈9.0 min). Faster or more CPU cores would help the Spark more than a faster GPU would. HaplotypeCaller leaves both processors partly idle. It is also 8 % slower run alone than inside `pbrun germline`; the two invocations differ in thread settings and in whether the input BAM was just written, and which of these causes the difference is untested.

## 4. Alignment options, rerun on a quiet machine

Day one flagged three fq2bam variants (GPU sort, GPU BAM write, both) as measured during a 44 GB download. They were rerun with the baseline on a quiet machine:

| Variant | Day one | Quiet rerun | BAM size |
|---|---|---|---|
| A, defaults | 103.1 s | 103.6 s | 4.86 GB |
| F1, `--gpusort` | 103.4 s | 103.7 s | 4.86 GB |
| F2, `--gpuwrite` | 114.9 s | 115.4 s | 5.70 GB |
| F3, both | 114.6 s | 115.7 s | 5.70 GB |

Medians agree within 0.5 % and BAM sizes are byte-identical, so the overlapping download did not affect the first runs. On the GB10, GPU sorting changes nothing, and GPU BAM writing costs 12 s per 26.7 M read pairs, all of it in the final write stage, and makes a 17 % larger file. The defaults are the right choice. The old runs are kept in the runs table as superseded.

## 5. Evo 2 40B: the streaming loader works

Section 5 of the previous note described the problem and the fix. The stock evo2 loader keeps the whole memory-mapped 82 GB checkpoint resident next to the 77 GiB model, and on unified memory both live in the same RAM. The streaming loader applies one block at a time and releases each block's pages. It runs behind a gate that loads Evo 2 7B with both loaders and requires identical results. The gate passed:

```text
"tensors": 344, "tensors_differ": 0, "fp8_states": 108, "fp8_differ": 0,
"logits_identical": true, "logits_max_abs_diff": 0.0,
"stream_info": {"groups": 33, "keys_loaded": 371, "keys_missing": 0}
```

The 40B run that followed:

| Point | Warmup | Measured | Memory |
|---|---|---|---|
| Load (51 groups, 578 keys, none missing) | 579 s | 589 s | 76.6 GiB weights; host had ≈24 GiB available throughout |
| Score 1 kb | 527 tokens/s | 514 tokens/s | 77.8 GiB allocated |
| Score 8 kb | 599 tokens/s | 585 tokens/s | 85.7 GiB allocated |
| Score 32 kb | out of memory | out of memory | asked for 2 GiB with 88.2 allocated + 15.3 reserved at the 103.4 GiB cap |
| Generate 256 bases | 2.08 tokens/s | 2.05 tokens/s | 86.2 GiB allocated |

Two ratios put these numbers in context. Scoring at 8 kb is 2 × 41.1 × 10⁹ × 585 ≈ 48 TFLOP/s, more than the 7B's 35 TFLOP/s and about half of the GB10's measured 92 TFLOP/s bf16 matmul peak. Generation at 2.05 tokens/s is 77 % of the bandwidth bound (220 GB/s ÷ 82 GB = 2.67 tokens/s); the 7B reached 65 % of its bound. Larger matrices keep the GPU busier.

The capacity limit comes from activations. Weights take 77 GiB of the 103 GiB the workload allows itself, and an 8 kb window already needs 8 GiB more. A 32 kb window would need roughly four times that. Raising the allocator cap would gain little: at the failure only about 4 GiB of device memory was free. Two probes remain untried. A 16 kb window might just fit. fp8 weights would halve the 77 GiB of weights to about 41 GiB and could make room for 32 kb or more.

The answer to the capacity question this project was built around is therefore yes. NVIDIA's packaged Evo 2 40B service is x86-only, but the open-source model runs on one Arm Spark, provided the checkpoint is applied block by block.

## 6. ESMFold with chunked attention

Unchunked ESMFold ran out of memory at 1,530 residues. The failed request was the 53 GiB triangle-attention score tensor, which grows as L³. ESMFold's trunk can compute that tensor in slices (`set_chunk_size(64)`), and the chunked run tested one protein each at about 1,024, 1,536 and 2,048 residues:

| Protein | Length | Unchunked | Chunked (64) | Mean pLDDT |
|---|---|---|---|---|
| EVC_MOUSE | 1,005 | 455.4 s, 42.9 GiB | 452.5 s, 14.5 GiB | 59.4 / 59.4 |
| MRP1_BOVIN | 1,530 | out of memory | 27.1 min, 23.1 GiB | 89.7 |
| THADA_HUMAN | 1,953 | not run | 54.4 min, 32.7 GiB | 76.1 |

The 1,005-residue structure is identical with and without chunking: CA RMSD 0.000 Å, and every coordinate and pLDDT value is equal at PDB precision. I had expected chunking to cost time, since it runs more and smaller kernels. It did not: at chunk size 64 each slice is still large enough to keep the GB10 busy. Time now grows about as L³ (exponent 2.98 from 1,005 to 1,953 residues), while memory grows roughly linearly over this range. On the Spark the practical ESMFold limit is time, about an hour at 2,000 residues, not memory, and there is no reason to run unchunked.

## 7. Working rules this produced

- Check the reference before blaming the caller or the hardware. A bundle reference built for a demo can cost two points of recall across the whole genome.
- Compare callers on precision and recall separately, and state whether the calls are filtered. An unfiltered HaplotypeCaller VCF is not the GATK best-practice result.
- Use a caller-only run to validate stage times taken from an end-to-end pipeline before comparing them with published per-tool tables.
- On unified memory, check what the loader keeps resident, not only the size of the weights. The 40B fits once the checkpoint is applied block by block.
- Rerun runs flagged as noisy rather than arguing about them. Here the rerun reproduced the flagged numbers, which turned a suspicion into a finding.

## 8. Current status

As of 13:20 UTC on 2026-11-12, every queued benchmark has run:

- **P00** roofline, **P01** fq2bam option matrix, **P02** germline callers (chr20 and whole genome on both references): done.
- **P03** end-to-end WGS: DeepVariant on both references and HaplotypeCaller on the sample reference are done. No HaplotypeCaller end-to-end run on the no-alt reference was queued; its caller-only result is in P02.
- **P07** ESMFold, unchunked and chunked; **P08** ESM-2 150M–15B; **P09** Evo 2 1B, 7B and 40B: measured.
- **Not started:** long reads (P04), somatic calling (P05), pangenome graphs (P06), the OpenFold2 and Boltz-2 NIMs, ColabFold MSA search, and the ceiling tests (60× coverage, two genomes at once).

The shareable report is at version 16 and contains every result in this note.

## 9. Open questions and next steps

- **Why is whole-genome alignment half as fast per base as the sample data?** The reference has been ruled out. Read length (2×151 here) and the input's duplicate and quality profile remain candidates.
- **How much of HaplotypeCaller's precision gap do GATK hard filters close?** One filtering step on the existing no-alt VCF would answer it, without rerunning the caller.
- **Why does DeepVariant's peak memory differ between the two BAMs** (64.1 vs 26.8 GiB)? Page cache charged on first read is the leading guess and has not been checked.
- **Evo 2 40B at 16 kb, and with fp8 weights.**
- **ESMFold accuracy**, which needs experimental structures released after the model's training cutoff and a TM-score tool.
- From the previous note, still open: ESM-2 15B's bf16 disagreement, its slow small-batch bf16 calls, and its 170 MB/s fp32 load.

## 10. Where things are

- Repository: `/home/manuel/code/wesen/2026-10-11--parabricks-benchmarks`
  - Experiments: `configs/experiments/p03-wgs-deepvariant-noalt.yaml`, `p03-wgs-germline-hc.yaml`, `p02-{dv,hc}-wgs{,-noalt}.yaml`, `p07-esmfold-chunked.yaml`, `p09-evo2-40b.yaml` (variant B).
  - Interpretation of every result: `configs/report/narrative.yaml`; published comparison data: `configs/report/published.yaml`.
  - Loader and gate: `workloads/evo2_score.py`, `scripts/check_evo2_stream_loader.py`.
- Ticket SPARK-001 diary, steps 19–25: `ttmp/2026/11/11/SPARK-001--sparkbricks-genomics-benchmarking-platform-for-dgx-spark/reference/01-diary.md`.
- Shareable report: https://claude.ai/artifact/RES424VPKTMjdcHjWWJode (private until shared).

## Related notes

- [[PROJECT REPORT - SparkBricks - Large Biological Models on a DGX Spark - What Fits in 128 GB]]: the morning note; the model results and the streaming-loader design.
- [[PROJECT REPORT - SparkBricks - Benchmarking Genomics and Biological Models on a DGX Spark - A Technical Deep Dive]]: day one, the framework and the first genomics results.
- [[PROJ - Bling - Bringing a DGX Spark onto Tailscale]]: the machine.
