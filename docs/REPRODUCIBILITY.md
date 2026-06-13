# Reproducibility Notes

## Expected Runtime

On a laptop with Python 3.11 or later, the frozen-output reproduction workflow usually completes in less than one minute. Refreshing PubMed exports depends on network speed and NCBI E-utilities response time.

## Main Workflow

Run:

```bash
bash scripts/reproduce_one_click.sh
```

The workflow performs these steps:

1. Applies the final 58-record adjudication to the broad evidence map and exclusion log.
2. Rebuilds the implementation-core subset.
3. Recomputes broad and implementation-core summary tables.
4. Recreates evidence-map matrices and publication figures.
5. Recreates the PRISMA-style flow diagram.
6. Recomputes the PMCID-availability proxy sensitivity table.
7. Runs figure-data consistency checks.

## Exact Reproduction

Use the frozen `results/search/*.tsv`, `results/map/*.tsv`, and `results/summary/FINAL_58_ADJUDICATION_WORKSHEET.tsv` files included in the release. A fresh PubMed search can return different records because indexing and metadata evolve.
