#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/apply_final_58_adjudication.py
python3 scripts/build_implementation_core_dataset.py

python3 scripts/summarize_prisma_and_descriptives.py \
  --study-index results/map/study_index.tsv \
  --exclusions results/screening/exclusion_reasons.tsv \
  --out-dir results/summary

python3 scripts/summarize_prisma_and_descriptives.py \
  --study-index results/map/study_index_implementation_core.tsv \
  --exclusions results/screening/exclusion_reasons.tsv \
  --out-dir results/summary_core

python3 scripts/build_evidence_map_counts_and_plots.py \
  --study-index results/map/study_index.tsv \
  --out-counts results/map/evidence_map_counts.tsv \
  --plots-dir plots/publication \
  --delivery-plot-name evidence_gap_heatmap \
  --followup-plot-name followup_reporting_heatmap \
  --title-suffix "broad records"

python3 scripts/build_evidence_map_counts_and_plots.py \
  --study-index results/map/study_index_implementation_core.tsv \
  --out-counts results/map/evidence_map_counts_implementation_core.tsv \
  --plots-dir plots/publication \
  --delivery-plot-name evidence_gap_heatmap_implementation_core \
  --followup-plot-name followup_reporting_heatmap_implementation_core \
  --title-suffix "implementation-core records"

python3 scripts/build_prisma_flow.py

python3 scripts/analyze_pmc_proxy_sensitivity.py \
  --study-index results/map/study_index.tsv \
  --pubmed-export results/search/pubmed_query_a.tsv \
  --pubmed-export results/search/pubmed_query_b.tsv \
  --out supplement/Table_S5_PMC_fulltext_proxy_sensitivity.tsv

python3 scripts/audit_figure_data_consistency.py \
  --study-index results/map/study_index.tsv \
  --overview results/summary/overview.tsv \
  --table-s4 results/summary/followup_closure_by_delivery_model.tsv \
  --out-md results/summary/figure_data_audit.md \
  --out-dir results/summary/figure_matrices

python3 scripts/audit_figure_data_consistency.py \
  --study-index results/map/study_index_implementation_core.tsv \
  --overview results/summary_core/overview.tsv \
  --table-s4 results/summary_core/followup_closure_by_delivery_model.tsv \
  --out-md results/summary_core/figure_data_audit.md \
  --out-dir results/summary_core/figure_matrices

echo "Reproduction workflow completed."
