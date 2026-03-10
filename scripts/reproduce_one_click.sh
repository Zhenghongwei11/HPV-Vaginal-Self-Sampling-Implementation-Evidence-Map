#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"

if [[ ! -d ".venv" ]]; then
  "$PY" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

python scripts/build_evidence_map_counts_and_plots.py
python scripts/summarize_prisma_and_descriptives.py
python scripts/build_prisma_flow.py

echo "[reproduce] Done. Key PDFs in plots/publication/ and supplementary tables in results/summary/."
