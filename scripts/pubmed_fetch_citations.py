#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import ssl
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _ssl_context() -> ssl.SSLContext:
    env_cafile = os.environ.get("SSL_CERT_FILE")
    if env_cafile and Path(env_cafile).exists():
        return ssl.create_default_context()

    default_paths = ssl.get_default_verify_paths()
    if default_paths.openssl_cafile and Path(default_paths.openssl_cafile).exists():
        return ssl.create_default_context()

    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _http_get(url: str, timeout_s: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "hpv-scoping-evidence-map/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_s, context=_ssl_context()) as r:  # noqa: S310
        return r.read().decode("utf-8", errors="replace")


def _text_or_empty(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def _first(elem: ET.Element, xpath: str) -> ET.Element | None:
    return elem.find(xpath)


def _all(elem: ET.Element, xpath: str) -> list[ET.Element]:
    return list(elem.findall(xpath))


def _parse_year(article: ET.Element) -> str:
    pubdate = _first(article, ".//JournalIssue/PubDate")
    if pubdate is None:
        pubdate = _first(article, ".//ArticleDate")
    if pubdate is None:
        return ""
    year = _text_or_empty(_first(pubdate, "Year"))
    if year:
        return year
    medline_date = _text_or_empty(_first(pubdate, "MedlineDate"))
    return medline_date.split(" ")[0] if medline_date else ""


def _parse_doi(pubmed_data: ET.Element) -> str:
    for aid in _all(pubmed_data, ".//ArticleIdList/ArticleId"):
        if (aid.get("IdType") or "").lower() == "doi":
            v = (aid.text or "").strip().lower()
            if v:
                return v
    return ""


def _parse_authors(article: ET.Element) -> list[str]:
    out: list[str] = []
    for a in _all(article, ".//AuthorList/Author"):
        collective = _text_or_empty(_first(a, "CollectiveName"))
        if collective:
            out.append(collective)
            continue
        last = _text_or_empty(_first(a, "LastName"))
        initials = _text_or_empty(_first(a, "Initials"))
        if last and initials:
            out.append(f"{last} {initials}")
        elif last:
            out.append(last)
    return out


def _format_authors_vancouver(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) <= 6:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + ", et al"


@dataclass(frozen=True)
class Citation:
    pmid: str
    authors: str
    title: str
    journal: str
    year: str
    volume: str
    issue: str
    pages: str
    doi: str

    def to_dict(self) -> dict[str, str]:
        return {
            "pmid": self.pmid,
            "authors": self.authors,
            "title": self.title,
            "journal": self.journal,
            "year": self.year,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "doi": self.doi,
        }

    def to_vancouver(self) -> str:
        bits: list[str] = []
        if self.authors:
            bits.append(self.authors + ".")
        if self.title:
            bits.append(self.title.rstrip(".") + ".")
        if self.journal:
            bits.append(self.journal + ".")

        y = self.year or ""
        vol = self.volume or ""
        iss = self.issue or ""
        pages = self.pages or ""

        y_part = y + ";" if y else ""
        vi = ""
        if vol and iss:
            vi = f"{vol}({iss})"
        elif vol:
            vi = vol
        elif iss:
            vi = f"({iss})"

        tail = ""
        if y_part or vi or pages:
            if vi and pages:
                tail = f"{y_part}{vi}:{pages}."
            elif vi:
                tail = f"{y_part}{vi}."
            elif pages:
                tail = f"{y_part}{pages}."
            else:
                tail = f"{y_part}".rstrip(";") + "."
            bits.append(tail)

        if self.doi:
            bits.append(f"doi:{self.doi}.")
        return " ".join([b for b in bits if b]).replace("..", ".")


def efetch_citations(pmids: list[str], timeout_s: int, sleep_s: float) -> list[Citation]:
    if not pmids:
        return []
    params = {"db": "pubmed", "retmode": "xml", "id": ",".join(pmids)}
    url = f"{EUTILS}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    xml_text = _http_get(url, timeout_s)
    root = ET.fromstring(xml_text)

    rows: list[Citation] = []
    for article in root.findall(".//PubmedArticle"):
        medline = _first(article, "MedlineCitation")
        if medline is None:
            continue
        pmid = _text_or_empty(_first(medline, "PMID"))
        art = _first(medline, "Article")
        if art is None or not pmid:
            continue

        title = _text_or_empty(_first(art, "ArticleTitle"))
        journal = _text_or_empty(_first(art, ".//Journal/ISOAbbreviation")) or _text_or_empty(_first(art, ".//Journal/Title"))
        year = _parse_year(art)
        volume = _text_or_empty(_first(art, ".//JournalIssue/Volume"))
        issue = _text_or_empty(_first(art, ".//JournalIssue/Issue"))
        pages = _text_or_empty(_first(art, ".//Pagination/MedlinePgn"))

        pubmed_data = _first(article, "PubmedData")
        doi = _parse_doi(pubmed_data) if pubmed_data is not None else ""

        authors_list = _parse_authors(art)
        authors = _format_authors_vancouver(authors_list)

        rows.append(
            Citation(
                pmid=pmid,
                authors=authors,
                title=title,
                journal=journal,
                year=year,
                volume=volume,
                issue=issue,
                pages=pages,
                doi=doi,
            )
        )

    if sleep_s > 0:
        time.sleep(sleep_s)
    return rows


def read_pmids(paths: list[Path]) -> list[str]:
    pmids: list[str] = []
    for p in paths:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            t = line.strip()
            if not t or t.startswith("#"):
                continue
            pmids.append(t)
    # stable dedupe
    seen: set[str] = set()
    out: list[str] = []
    for x in pmids:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def write_tsv(path: Path, rows: list[Citation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["pmid", "authors", "title", "journal", "year", "volume", "issue", "pages", "doi"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r.to_dict())


def write_md(path: Path, rows: list[Citation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. {r.to_vancouver()}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch PubMed citations for a list of PMIDs and format Vancouver-style references.")
    ap.add_argument("--in-pmids", type=Path, nargs="+", required=True)
    ap.add_argument("--out-md", type=Path, default=Path("docs/REFERENCES_VANCOUVER.md"))
    ap.add_argument("--out-tsv", type=Path, default=Path("results/summary/references.tsv"))
    ap.add_argument("--timeout-s", type=int, default=60)
    ap.add_argument("--sleep-s", type=float, default=0.2)
    ap.add_argument("--batch-size", type=int, default=80)
    args = ap.parse_args()

    pmids = read_pmids(args.in_pmids)
    rows: list[Citation] = []
    for i in range(0, len(pmids), args.batch_size):
        batch = pmids[i : i + args.batch_size]
        rows.extend(efetch_citations(batch, args.timeout_s, args.sleep_s))

    # stable ordering by input PMID order
    order = {p: idx for idx, p in enumerate(pmids)}
    rows.sort(key=lambda r: order.get(r.pmid, 10**9))

    write_tsv(args.out_tsv, rows)
    write_md(args.out_md, rows)
    print(f"Wrote: {args.out_md}")
    print(f"Wrote: {args.out_tsv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
