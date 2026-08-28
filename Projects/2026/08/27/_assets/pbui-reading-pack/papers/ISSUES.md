# Download issues — papers with no open-access copy

Per-paper download results are in `download-report.json` (first automated pass) and the
chronological `../diary.md`. This file lists the entries that could **not** be retrieved as
open-access PDFs and why, plus suggested follow-ups.

Summary: 43 link files → **32 PDFs** + **2 HTML snapshots** + **9 issues** below.

## Paywalled (publisher access control, no OA copy found via Unpaywall / OpenAlex / Semantic Scholar)

| key | citation | publisher | link | follow-up |
|-----|----------|-----------|------|-----------|
| `becker1987brushing` | Becker & Cleveland, *Brushing Scatterplots*, Technometrics 1987 | Taylor & Francis | https://doi.org/10.1080/00401706.1987.10488204 | T&F serves abstract only (`/doi/abs/`); possible author copy on StatLib / Cleveland's site. Try Anna's Archive by DOI. |
| `boukhelifa2003software` | Boukhelifa & Rodgers, *A Model and Software System for Coordinated…*, Information Visualization 2003 | Sage (was Palgrave) | https://doi.org/10.1057/palgrave.ivs.9500057 | Sage Cloudflare 403; paywalled. Try author (Rodgers, Kent) self-archive or Anna's Archive. |
| `green1996cognitive` | Green & Petre, *Usability Analysis of Visual Programming Environments…*, JVLC 1996 | Elsevier | https://doi.org/10.1006/jvlc.1996.0009 | ScienceDirect paywall. Author PDF widely mirrored (Green/Petre cognitive dimensions); try Anna's Archive / author site. |
| `moody2009physics` | Moody, *The Physics of Notations…*, IEEE TSE 2009 | IEEE | https://doi.org/10.1109/TSE.2009.67 | IEEE Xplore (AWS WAF + paywall). Author copy on Moody's site / arXiv? Try Anna's Archive. |
| `north2000snapusers` | North & Shneiderman, *Snap-Together Visualization: Can Users Construct…*, IJHCS 2000 | Elsevier | https://doi.org/10.1006/ijhc.2000.0418 | ScienceDirect paywall. Companion to `north2000snap` (which was retrieved from DRUM). Try Anna's Archive. |
| `weaver2004improvise` | Weaver, *Building Highly-Coordinated Visualizations in Improvise*, IEEE InfoVis 2004 | IEEE | https://doi.org/10.1109/INFVIS.2004.12 | IEEE Xplore paywall. Check Weaver's OU site / author copy. |
| `yi2007interaction` | Yi et al., *Toward a Deeper Understanding of the Role of Interaction…*, IEEE TVCG 2007 | IEEE | https://doi.org/10.1109/TVCG.2007.70515 | IEEE Xplore paywall. Author copies exist (Stasko/Georgia Tech); try Anna's Archive. |

## Linked URL is an HTML essay, not the paper PDF (underlying paper paywalled, no OA)

| key | citation | linked URL | note |
|-----|----------|-----------|------|
| `weaver2005coordination` | Weaver, *Visualizing Coordination in Situ*, IEEE InfoVis 2005 (DOI 10.1109/INFVIS.2005.1532143) | https://www.cs.ou.edu/~weaver/improvise/architecture/mv/index.html | Same `cs.ou.edu` HTML architecture essay (self-signed cert; `curl -k` fetchable). Not the paper PDF. OpenAlex/Semantic Scholar: CLOSED. |
| `weaver2006metavis` | Weaver, *Metavisual Exploration and Analysis of DEVise Coordination in Improvise*, CMV 2006 (no DOI) | https://www.cs.ou.edu/~weaver/improvise/architecture/mv/index.html | Same HTML essay. No DOI; no OA PDF located. |

## Sources that are legitimately HTML (no PDF exists) — snapshots saved

These were saved as `.html` snapshots in `downloaded/`; they are project/documentation sites, not papers.

| key | saved as | note |
|-----|----------|------|
| `keller2024usecoordination` | `keller2024usecoordination.html` | https://use-coordination.dev/ — project site for the Use-Coordination library. |
| `radul2009propagator` | `radul2009propagator.html` | https://groups.csail.mit.edu/mac/users/gjs/propagators/ — MIT propagators tech-report page. |

## Notes on the retrieval method

- ACM DOIs that OpenAlex flagged `is_oa=False` were nonetheless served free by `dl.acm.org`
  once Cloudflare was cleared (ahlberg, baldonado, bohannon, borning, cockburn, johnston) —
  OpenAlex OA flags are unreliable for ACM's free back-catalog; probe empirically.
- Cloudflare (`dl.acm.org`, `onlinelibrary.wiley.com`, `tandfonline.com`, `journals.sagepub.com`)
  requires a Chrome TLS fingerprint (`curl_cffi` `impersonate="chrome"`) + a live `cf_clearance`
  cookie harvested from a real browser session. AWS WAF (`infoscience.epfl.ch`, `ieeexplore.ieee.org`)
  uses an `aws-waf-token` cookie that is reusable via curl_cffi once solved in-browser.
- `download-all-papers.py` has a latent bug: its PDF validator rejects Ghostscript-DSC PDFs
  (which prefix `%PDF-` with `%%[…]%%` comments); fix by detecting `%PDF-` in the first ~2 KB.
