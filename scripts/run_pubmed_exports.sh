#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/search

RUN_DATE_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Query A: coverage-first (underscreened focus; self-sampling delivery)
TERM_A='((human papillomavirus OR HPV) AND (self-sampling OR self sampling OR self-collected OR self collected OR home-based OR mail OR postal)) AND (cervical cancer screening OR cervical screening) AND (underscreened OR "under-screened" OR nonattender* OR "non-attender*" OR "never screened" OR "never-screened" OR "hard to reach" OR outreach OR rural OR migrant)'

# Query B: implementation/outcomes-first
TERM_B='((human papillomavirus OR HPV) AND (self-sampling OR self sampling OR self-collected OR home-based OR mail OR postal OR outreach OR community health worker)) AND (cervical screening) AND (uptake OR participation OR acceptability OR feasibility OR implementation OR adherence OR follow-up OR navigation OR reminder OR equity OR cost)'

python3 scripts/pubmed_export_records.py \
  --term "${TERM_A}" \
  --retmax 2000 \
  --out-tsv results/search/pubmed_query_a.tsv

python3 scripts/pubmed_export_records.py \
  --term "${TERM_B}" \
  --retmax 2000 \
  --out-tsv results/search/pubmed_query_b.tsv

{
  printf "source\trun_date_utc\tquery_id\tquery\tretmax\treturned_rows\texport_file\n"
  printf "PubMed\t%s\tquery_a\t%s\t2000\t%s\t%s\n" "${RUN_DATE_UTC}" "${TERM_A}" "$(($(wc -l < results/search/pubmed_query_a.tsv) - 1))" "results/search/pubmed_query_a.tsv"
  printf "PubMed\t%s\tquery_b\t%s\t2000\t%s\t%s\n" "${RUN_DATE_UTC}" "${TERM_B}" "$(($(wc -l < results/search/pubmed_query_b.tsv) - 1))" "results/search/pubmed_query_b.tsv"
} > results/search/search_log.tsv

echo "Wrote: results/search/search_log.tsv"

