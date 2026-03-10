# HPV Vaginal Self-Sampling (Underscreened) — Scoping Evidence Map

This repository contains a scoping evidence map (non–meta-analysis) focused on HPV vaginal self-sampling implementation for underscreened populations (eg, non-attenders, overdue, never-screened). The package is designed to be reproducible without subscription access by using an open-access / abstract-sufficient inclusion policy.

## Contents
- Core outputs:
  - Included study index (Dataset S1): `results/map/study_index.tsv`
  - Exclusion log with reason codes (Dataset S2): `results/screening/exclusion_reasons.tsv`
  - Summary tables: `results/summary/`
  - Final figure PDFs: `plots/publication/`
- Supplementary files (appendices, datasets, code zip): `supplement/` (see `supplement/INDEX.md`)
- Reproducibility docs:
  - Data sources: `docs/DATA_MANIFEST.tsv`
  - Figure provenance: `docs/FIGURE_PROVENANCE.tsv`
  - Decision rules: `docs/STATISTICAL_DECISION_RULES.md`

## One-click rebuild (from frozen charting outputs)
This regenerates the summary tables and PDFs from the included `results/` tables:
```bash
bash scripts/reproduce_one_click.sh
```

## Full refresh (PubMed exports → screening/charting → outputs)
Export PubMed records via E-utilities:
```bash
bash scripts/run_pubmed_exports.sh
```
This generates `results/search/pubmed_query_a.tsv` and `results/search/pubmed_query_b.tsv` locally; these raw exports are not versioned in the public repository.

Screen + chart into the evidence-map schema:
```bash
python3 scripts/screen_and_chart_pubmed.py --in-tsv results/search/pubmed_query_a.tsv results/search/pubmed_query_b.tsv --append
```

Then rebuild summaries/figures:
```bash
python3 scripts/build_evidence_map_counts_and_plots.py
python3 scripts/summarize_prisma_and_descriptives.py
python3 scripts/build_prisma_flow.py
```

## Build the canonical review bundle ZIP (for GitHub Release assets)
```bash
bash scripts/build_public_review_bundle.sh v1.0.0
```
Outputs:
- `dist/public_review_bundle_v1.0.0.zip`
- `dist/CHECKSUMS.sha256`
