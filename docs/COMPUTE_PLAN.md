# Compute plan

## Expected runtime (from frozen outputs)
- Rebuilding summary tables + PDFs from the included `results/` tables typically completes in minutes on a laptop.

## Expected runtime (full refresh)
- Re-running PubMed exports depends on network and NCBI rate limits.
- Screening/charting steps are CPU-light but can take longer if the record set is large.

## Disk
- This repository is designed to remain lightweight; large raw datasets are not redistributed.
