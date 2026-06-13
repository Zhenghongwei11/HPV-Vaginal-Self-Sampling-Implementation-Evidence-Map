#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


STUDY_INDEX = Path("results/map/study_index.tsv")
AUDIT = Path("results/summary/implementation_core_eligibility_audit.tsv")
OUT_CORE = Path("results/map/study_index_implementation_core.tsv")
OUT_ANNOTATED = Path("results/map/study_index_with_implementation_core_status.tsv")
SUPP_CORE = Path("supplement/Dataset_S1b_Implementation_core_study_index.tsv")
SUPP_AUDIT = Path("supplement/Dataset_S6_Implementation_core_eligibility_audit.tsv")
SUMMARY = Path("results/summary/implementation_core_summary.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    study = read_tsv(STUDY_INDEX)
    audit = read_tsv(AUDIT)
    audit_by_pmid = {r["pmid"]: r for r in audit}

    annotated: list[dict[str, str]] = []
    core: list[dict[str, str]] = []
    counts = {"broader_map_records": len(study), "implementation_core_records": 0, "non_core_records": 0}
    follow_counts: dict[str, int] = {}

    for row in study:
        pmid = row["pmid"]
        a = audit_by_pmid.get(pmid)
        if not a:
            raise SystemExit(f"PMID {pmid} missing from {AUDIT}")

        manual = a.get("manual_core_decision", "").strip().upper()
        if manual == "CORE":
            status = "CORE"
            reason = a.get("manual_decision_reason", "")
        elif manual == "NON_CORE":
            status = "NON_CORE"
            reason = a.get("manual_decision_reason", "")
        elif manual == "UNCERTAIN":
            status = "UNCERTAIN"
            reason = a.get("manual_decision_reason", "")
        elif a.get("candidate_core_status") == "candidate_core":
            status = "CORE"
            reason = a.get("candidate_reason", "")
        else:
            raise SystemExit(f"PMID {pmid} lacks final implementation-core decision")

        out = dict(row)
        out["implementation_core_status"] = status
        out["implementation_core_reason"] = reason
        out["implementation_core_evidence"] = a.get("manual_evidence_text", "")

        new_level = a.get("manual_followup_level_if_changed", "").strip()
        new_pct = a.get("manual_followup_pct_if_changed", "").strip()
        if new_level:
            out["followup_reporting_level"] = new_level
            out["followup_closure_reported"] = "N" if new_level == "none" else "Y"
        if new_pct:
            out["followup_completion_pct"] = new_pct
        if a.get("manual_notes", "").strip():
            out["followup_notes"] = (out.get("followup_notes", "").strip() + " " + a["manual_notes"].strip()).strip()

        annotated.append(out)
        if status == "CORE":
            core.append(out)
            counts["implementation_core_records"] += 1
            follow_counts[out["followup_reporting_level"]] = follow_counts.get(out["followup_reporting_level"], 0) + 1
        elif status == "NON_CORE":
            counts["non_core_records"] += 1

    fields = list(annotated[0].keys())
    write_tsv(OUT_ANNOTATED, annotated, fields)
    write_tsv(OUT_CORE, core, fields)
    write_tsv(SUPP_CORE, core, fields)
    write_tsv(SUPP_AUDIT, audit, list(audit[0].keys()))

    summary_rows = [{"metric": k, "value": str(v)} for k, v in counts.items()]
    for k, v in sorted(follow_counts.items()):
        summary_rows.append({"metric": f"implementation_core_followup_{k}", "value": str(v)})
    write_tsv(SUMMARY, summary_rows, ["metric", "value"])

    print(f"Wrote {OUT_CORE} ({len(core)} records)")
    print(f"Wrote {OUT_ANNOTATED}")
    print(f"Wrote {SUPP_CORE}")
    print(f"Wrote {SUPP_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
