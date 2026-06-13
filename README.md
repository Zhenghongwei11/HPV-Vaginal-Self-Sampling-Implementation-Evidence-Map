# HPV Vaginal Self-Sampling Implementation Evidence Map

This repository contains the public reproducibility package for a PubMed-indexed scoping evidence map of HPV vaginal self-sampling implementation among under-screened or underserved populations.

The repository is designed to reproduce the derived tables and publication figures from the frozen charting outputs. It contains only public analysis code, derived data, figures, and reproducibility documentation.

## Current Release Snapshot

- PubMed records screened after deduplication: 1,716
- Broad evidence-map records: 530
- Implementation-core records: 389
- Excluded records with reason codes: 1,186
- Implementation-core follow-up reporting:
  - Completion reported: 42/389 (10.8%)
  - Referral without completion metrics: 208/389 (53.5%)
  - No follow-up reported: 139/389 (35.7%)

## Repository Contents

- `scripts/`: analysis and reproduction scripts used to rebuild the charted datasets, summaries, and figures.
- `results/`: frozen derived tables, search exports, screening logs, summary tables, and figure anchor tables.
- `plots/publication/`: publication-ready PDF and PNG figures regenerated from `results/`.
- `supplement/`: supplementary appendices, charted datasets, exclusion logs, and summary tables.
- `docs/`: public data manifest, figure provenance, decision rules, and reproduction notes.

## Quick Reproduction

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the main reproduction workflow from the repository root:

```bash
bash scripts/reproduce_one_click.sh
```

The script rebuilds the implementation-core dataset, summary tables, evidence matrices, heatmaps, PRISMA-style flow diagram, PMCID proxy sensitivity table, and figure-data consistency checks from the included frozen inputs.

## Optional PubMed Refresh

The frozen release includes minimal PubMed metadata TSV exports under `results/search`. To refresh the search from PubMed E-utilities, run:

```bash
bash scripts/run_pubmed_exports.sh
python3 scripts/screen_and_chart_pubmed.py --in-tsv results/search/pubmed_query_a.tsv results/search/pubmed_query_b.tsv --append
```

Because PubMed records and indexing can change over time, the archived release should be used for exact reproduction of the reported results.

## Main Reproduction Outputs

- Broad evidence map: `results/map/study_index.tsv`
- Implementation-core evidence map: `results/map/study_index_implementation_core.tsv`
- Exclusion log: `results/screening/exclusion_reasons.tsv`
- Implementation-core eligibility audit: `results/summary/implementation_core_eligibility_audit.tsv`
- Main figure anchor tables: `results/summary/figure_matrices/` and `results/summary_core/figure_matrices/`
- Main figures: `plots/publication/prisma_flow.pdf`, `plots/publication/evidence_gap_heatmap_implementation_core.pdf`, and `plots/publication/followup_reporting_heatmap_implementation_core.pdf`

## Interpretation Boundaries

This is a record-level evidence map. Counts describe what was visible in PubMed-indexed records, abstracts, and open-access full text when available under the declared access policy. They should not be interpreted as complete programme-level evidence counts or as pooled estimates of intervention effectiveness.

## License

Code is released under the MIT License. Derived tables, documentation, and figures are released under CC BY 4.0; see `LICENSE-DATA`.
