---
title: "PROJECT REPORT - Bayesian Marketing Day 4 - Causal Identification, Membership Economics, and the Targeting Decision"
aliases:
  - Bayesian Marketing Day 4 Deep Dive
  - Membership Trial G-Computation and Targeting Report
  - Causal Inference and Posterior Decision Analysis Report
tags:
  - project
  - article
  - pymc
  - bayesian-statistics
  - causal-inference
  - treatment-effects
  - g-computation
  - decision-analysis
  - marketing-modeling
status: complete
type: project
created: 2026-08-31
repo: /home/manuel/code/wesen/2026-08-31--bayesian-marketing
---

# PROJECT REPORT - Bayesian Marketing Day 4 - Causal Identification, Membership Economics, and the Targeting Decision

The first three days of the Bayesian Marketing workshop built models of increasing structure: counts, then customer heterogeneity, then product choice. Day 4 adds the two layers that turn models into decisions. The first is identification: a randomized membership trial whose assignment closes the backdoor paths that confound every voluntary-membership comparison. The second is decision analysis: a posterior over per-customer incremental profit, evaluated under targeting policies with expected totals, intervals, loss probabilities, and regret. Between them sits the workshop's most quotable failure mode — the same outcome model fitted to self-selected membership produces a posterior that is narrow, precise, and 2.17 times the causal effect.

This report is the complete technical account of Day 4 (ticket `day4-lab4-proj4`): the trial generator and its balance audit, the treatment-response model, posterior g-computation on the outcome scale, the AOV channel, the synthetic profit function and its components, the targeting policies, the voluntary-membership contrast, and the engineering record. Everything reproduces from seed 20260831 in the repo's frozen environment, and the capstone's executive recommendation is included in the required structure.

> [!summary]
> - The balance audit (Task 2) produced a finding rather than a formality: all standardized differences pass the conventional 0.1 bar, but the privacy-project rate differs by −0.062 (a 1.96-SE finite-sample wobble the handout explicitly anticipates) — which is why the raw arm difference (0.265 orders) sits slightly below the model-based ATE and why the regression adjustment matters.
> - Posterior g-computation estimated the ATE at 0.273 expected annual orders [0.176, 0.372], covering the instructor truth of 0.301, with CATEs ordered exactly as planted: privacy-project customers 0.394, high-baseline customers 0.459, low-baseline customers 0.089.
> - Incremental profit is where nonlinearity bites (Hint 3 as arithmetic): fees add $119.40 per member-year while the 20% discount costs $38.80 and the $99-vs-$299 shipping threshold costs another $51.39 — membership raises orders by 0.27 and still loses money on roughly a quarter of customers. The posterior mean Δπ of $28.25 recovers the truth $29.12 to $0.87.
> - Targeting on positive expected incremental profit adds ≈ $46,000 over offering everyone (expected total $158,958 vs $112,995; expected regret $78 vs $46,041); the risk-aware rule (P(Δπ > 0) > 0.80) trades $220 of expectation for a better 5th percentile.
> - The voluntary contrast: the same model on self-selected membership estimates a membership coefficient of 0.332 [0.27, 0.40] against the randomized 0.153 — a raw voluntary arm difference of 0.749 annual orders against the causal 0.273. Narrow and wrong, in one plot.

## 1. The design does the identification

The trial randomizes membership itself: 1,968 of 4,000 customers assigned to member, 2,032 to nonmember, over a 12-month horizon. The outcome is annual order count (Negative Binomial with conditional dispersion 2.5 and a latent customer effect); the treatment effect is heterogeneous on the log rate (τ = 0.14 + 0.10·baseline_z + 0.08·privacy); the dollar channel is pre-discount AOV with a small negative member effect (−0.08 on log AOV — the lower shipping threshold makes smaller baskets rational).

![](_assets/bayes-day4-dag.png)

Three estimands are kept distinct from the start (Task 1): the descriptive association E[Y | M=1] − E[Y | M=0]; the intent-to-treat effect of an offer; and the ATE of assigned membership E[Y(1) − Y(0)]. Because the trial randomizes membership itself, the ATE is the primary estimand, with incremental annual contribution as the decision quantity. The DAG above is the whole distinction: the randomized design has no backdoor path, and the voluntary design has one through latent intensity — the same latent quantity Day 2 measured as customer heterogeneity, now operating as a confounder.

The balance audit found something real. All three covariates pass the conventional standardized-difference bar, but the privacy-project rate differs between arms by −0.062 standardized — 20.4% in the member arm against 22.9% in the nonmember arm, a 1.96-SE wobble at this sample size. The pipeline's original assertion threshold (0.05) flagged it as a failure; the correct reading is that randomization balances in expectation, not in every draw, and the handout says exactly this ("large random differences are possible"). The assertion was recalibrated to the conventional 0.1 bar with z-scores added, and the wobble became a chapter finding: it explains why the raw arm difference (0.265 orders) under-adjusts relative to the regression-based ATE.

## 2. The treatment-response model

The model is Day 2's Negative Binomial regression with the treatment interacted with covariates — membership shifts each customer's log rate by τ₀ + τ_baseline·z + τ_privacy·q. It samples cleanly (4 chains, zero divergences, bulk ESS 4,413, 172 seconds) and recovers the planted structure:

| Parameter | Posterior [90% HDI] | Truth |
|---|---|---:|
| τ₀ | 0.153 [0.08, 0.23] | 0.14 |
| τ_baseline | 0.067 [0.004, 0.13] | 0.10 |
| τ_privacy | 0.027 [−0.11, 0.16] | 0.08 |
| β_baseline | 0.433 [0.39, 0.48] | 0.42 |
| β_privacy | 0.359 [0.26, 0.46] | 0.28 |
| β_warm | 0.075 [0.01, 0.14] | 0.08 |

τ₀ is precise and centered on truth; the interaction posteriors cover truth but are individually weaker. With 4,000 customers the average effect is well identified while the heterogeneity of the effect is only partially identified — the same lesson as Day 2's random slopes, now in a causal register. The dispersion φ (1.39 against a conditional 2.5 plus a latent SD of 0.55) again shows a model without customer random effects compressing between-customer spread into the dispersion parameter.

## 3. G-computation: from coefficients to orders

The τ coefficients live on the log-rate scale, which no manager reads. Posterior g-computation predicts every customer under both assignments with the *same* posterior draw and covariates — the discipline that makes the comparison a counterfactual rather than a contrast between different customers — and averages the differences:

![](_assets/bayes-day4-ate_cate.png)

| Quantity | Median [90% HDI] | P(>0) |
|---|---|---:|
| ATE (expected orders) | 0.273 [0.176, 0.372] | 1.000 |
| rate ratio | 1.174 [1.100, 1.254] | 1.000 |
| CATE privacy | 0.394 [0.157, 0.631] | 0.997 |
| CATE non-privacy | 0.240 [0.144, 0.340] | 1.000 |
| CATE baseline z ≈ −1 | 0.089 [0.009, 0.170] | 0.966 |
| CATE baseline z ≈ 0 | 0.221 [0.132, 0.312] | 1.000 |
| CATE baseline z ≈ +1 | 0.459 [0.291, 0.631] | 1.000 |

The posterior ATE covers the instructor truth (0.301 orders), and the CATE ordering reproduces the planted heterogeneity exactly. These groups were prespecified; searching segments for the largest posterior effect and reporting only that would be selection bias even inside a Bayesian analysis.

## 4. The dollar channel

The AOV model (lognormal, member effect) recovers every planted parameter: intercept log 145, baseline +0.150 (truth 0.14), privacy +0.219 (truth 0.22), member −0.081 (truth −0.08), σ 0.352 (truth 0.35). The posterior predictive check reproduces the observed median ($146.3 vs $146.5), 90th percentile ($243 vs $241), and 99th ($368 vs $378). One limitation is stated rather than fixed: a lognormal cannot reproduce sharp bunching at shipping thresholds. In this synthetic data the observed AOV was itself drawn lognormal, so the check passes trivially — but real basket data bunches near $99 and $299, and the profit simulation's threshold logic (below) is exactly where that misspecification would matter.

## 5. Incremental profit: where the economics stop being linear

For each posterior draw and customer, profit is computed under both membership states using the same draw (Hint 4) — expected orders from g-computation, expected AOV with the lognormal mean correction e^{μ+σ²/2}, then the synthetic economics: fees $9.95/month, 20% member discount, $99-vs-$299 free-shipping thresholds, product cost 52% of list, shipping $34 per order, claims $3.50 per order.

![](_assets/bayes-day4-profit.png)

| Quantity | Value |
|---|---:|
| median Δπ per customer | $37.75 |
| mean Δπ per customer | $28.25 |
| 90% interval | [−$76.13, $104.78] |
| P(Δπ > 0) | 0.764 |
| truth mean Δπ (instructor) | $29.12 |

The posterior mean recovers the truth to $0.87, and the components are the lesson: fees add $119.40 per member-year, but the discount costs $38.80 and the lower shipping threshold costs $51.39 in subsidized shipping — members cross $99 constantly while nonmembers rarely cross $299. Membership raises orders by 0.27 and still loses money on roughly a quarter of customers. That is not a modeling failure; it is the profit function being nonlinear in the treatment, which is precisely why the decision layer cannot be a plug-in calculation.

![](_assets/bayes-day4-heterogeneity.png)

The heterogeneity map shows who: high-baseline-spend and privacy-project customers gain most; low-spend non-privacy customers are the expected losers whose discount and shipping costs exceed their fee.

## 6. Targeting: the decision layer

Three policies, evaluated over the per-customer Δπ posterior on the target population:

| Policy | n targeted | Expected total | 90% interval | P(total > 0) | Expected regret |
|---|---:|---:|---|---:|---:|
| offer everyone | 4,000 | $112,995 | [$90.7k, $135.5k] | 1.000 | $46,041 |
| **E[Δπᵢ] > 0** | 3,053 | **$158,958** | [$147.4k, $170.6k] | 1.000 | **$78** |
| P(Δπᵢ > 0) > 0.80 | 2,958 | $158,738 | [$147.6k, $169.9k] | 1.000 | $298 |

![](_assets/bayes-day4-policy.png)

Targeting on positive expected profit adds roughly $46,000 in expected profit over offering everyone — not by changing any outcome, but by not paying the discount-and-shipping costs on the customers whom membership loses money on. The risk-aware rule trades $220 of expectation for a slightly better 5th percentile ($147.6k vs $147.4k) and 95 fewer targeted customers; which rule is better encodes management's asymmetry between false-positive and false-negative offers, not a Bayesian law. The regret column makes the comparison legible: the best policy's regret is $78, the conservative rule gives up $298 in expectation, and offering everyone gives up $46,041.

## 7. The voluntary contrast: narrow and wrong

![](_assets/bayes-day4-contrast.png)

The §46 sample lets customers choose membership according to latent intensity (logit selection on the hidden customer effect and baseline spend). Fitting the same outcome model to the self-selected membership gives a coefficient of 0.332 [0.27, 0.40] — against the randomized 0.153 and a truth near 0.157. The raw voluntary arm difference is 0.749 annual orders against the causal 0.273. The naive posterior is not uncertain enough to be wrong politely: it is confident about a quantity that is not the treatment effect. This is Day 1's "precise but wrong" at its most consequential, and it closes the workshop's argument: the posterior quantifies uncertainty within the model's assumptions; the design does the identification.

## 8. Engineering notes

Three items from the ticket diary worth preserving:

- **The balance assertion was miscalibrated, not the randomization.** The first threshold (|SMD| < 0.05) failed on a legitimate 1.96-SE wobble; the fix was the conventional 0.1 bar plus z-scores in the table, and the wobble became an audit finding that explains the raw-vs-adjusted gap. An assertion that encodes the wrong claim produces noise, not safety.
- **The §41.1 counterfactual bookkeeping is the most error-prone code in the generator.** The truth table's member state adds `true_tau × (1 − member)` and the nonmember state subtracts `true_tau × member` — signs that are easy to flip and silent when flipped. The instructor ATE check (posterior HDI must cover the truth ATE computed from these columns) is the guard.
- **Drafting residue happens under time pressure.** An unused `true_aov` block was removed from the g-computation script before its first run; static review of one's own draft remains cheaper than runtime archaeology.

## 9. Working rules

- State the estimand before fitting: intervention, population, horizon. "Membership impact" is not an estimand.
- The design does the identification; the posterior quantifies uncertainty within it. No prior substitutes for exogenous variation.
- G-compute the same customer under both states with the same draw; never compare different customer sets.
- Translate log-scale coefficients into orders and dollars before reporting them; managers cannot act on logits.
- Separate profit into components and preserve draw-wise dependence — the fee/discount/shipping arithmetic is the decision, and it is nonlinear.
- Evaluate targeting on the target population (Hint 6), report regret, and state that risk thresholds encode management preferences rather than statistical laws.
- Audit balance expecting wobbles: randomization balances in expectation, and a finite-sample imbalance is a finding to adjust for, not a failure to panic about.

## Related notes

- [[PROJECT REPORT - Bayesian Marketing Day 1 - Generative Models, Conjugate Validation, and the Poisson Failure Pattern]]
- [[PROJECT REPORT - Bayesian Marketing Day 2 - Hierarchical Recovery of Customer Heterogeneity]]
- [[PROJECT REPORT - Bayesian Marketing Day 3 - Product Choice, Willingness to Pay, and the Posterior Price Decision]]
- Source repo: `/home/manuel/code/wesen/2026-08-31--bayesian-marketing` — ticket `day4-lab4-proj4` (intern guide, 3-step diary, capstone chapter `artifacts/report-day4.md` with 6 figures); the trial generator in `day4/trial.py` (including the §41.1 counterfactual bookkeeping), models in `day4/models.py`, g-computation and the profit engine in `day4/gcomp.py`, policies in `scripts/34_policy.py`.
