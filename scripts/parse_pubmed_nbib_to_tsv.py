#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path


TAG_RE = re.compile(r"^([A-Z0-9]{2,4})\s*-\s(.*)$")
CONT_RE = re.compile(r"^\s{6}(.*)$")


@dataclass
class Record:
    fields: dict[str, list[str]] = field(default_factory=dict)

    def add(self, tag: str, text: str) -> None:
        self.fields.setdefault(tag, []).append(text.strip())

    def get_first(self, tag: str) -> str:
        vals = self.fields.get(tag, [])
        return vals[0].strip() if vals else ""

    def get_joined(self, tag: str) -> str:
        vals = [v.strip() for v in self.fields.get(tag, []) if v.strip()]
        return " ".join(vals).strip()


def parse_nbib(text: str) -> list[Record]:
    records: list[Record] = []
    cur: Record | None = None
    last_tag: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        if not line.strip():
            if cur is not None and cur.fields:
                records.append(cur)
            cur = None
            last_tag = None
            continue

        if cur is None:
            cur = Record()

        m = TAG_RE.match(line)
        if m:
            tag, val = m.group(1), m.group(2)
            cur.add(tag, val)
            last_tag = tag
            continue

        m2 = CONT_RE.match(line)
        if m2 and last_tag:
            cont = m2.group(1).strip()
            if cont:
                cur.add(last_tag, cont)
            continue

        # Fallback: treat as continuation if we can.
        if last_tag:
            cur.add(last_tag, line.strip())

    if cur is not None and cur.fields:
        records.append(cur)

    return records


def _infer_year(dp: str) -> str:
    m = re.search(r"\b(19|20)\d{2}\b", dp or "")
    return m.group(0) if m else ""


def _extract_doi(record: Record) -> str:
    # DOI often appears in AID or LID with [doi] suffix in MEDLINE/PubMed format exports.
    for tag in ("AID", "LID"):
        for v in record.fields.get(tag, []):
            s = v.strip()
            if "[doi]" in s.lower():
                doi = s.split(" ")[0].strip().lower()
                return doi
    return ""


def records_to_rows(records: list[Record]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for r in records:
        pmid = r.get_first("PMID")
        if not pmid:
            continue

        title = r.get_joined("TI")
        abstract = r.get_joined("AB")
        year = _infer_year(r.get_first("DP"))
        doi = _extract_doi(r)
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        rows.append(
            {
                "pmid": pmid,
                "doi": doi,
                "year": year,
                "title": title,
                "abstract": abstract,
                "url": url,
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["pmid", "doi", "year", "title", "abstract", "url"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert PubMed NBIB (MEDLINE) exports into a TSV usable by screening/charting scripts.")
    ap.add_argument("--in-nbib", type=Path, nargs="+", required=True, help="One or more .nbib files exported from PubMed")
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    all_records: list[Record] = []
    for p in args.in_nbib:
        txt = p.read_text(encoding="utf-8", errors="replace")
        all_records.extend(parse_nbib(txt))

    rows = records_to_rows(all_records)

    # Deduplicate by PMID (stable first-seen order)
    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        pmid = row["pmid"]
        if pmid in seen:
            continue
        seen.add(pmid)
        deduped.append(row)

    write_tsv(args.out_tsv, deduped)
    print(f"Wrote: {args.out_tsv} (records={len(all_records)} rows={len(deduped)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

