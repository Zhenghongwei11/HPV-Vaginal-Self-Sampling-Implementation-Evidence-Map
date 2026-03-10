#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
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
    # macOS Python installs sometimes ship without a default CA bundle
    # (e.g., openssl_cafile path does not exist). Prefer certifi when needed.
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


@dataclass(frozen=True)
class PubmedRow:
    pmid: str
    doi: str
    pmcid: str
    title: str
    journal: str
    pubdate: str
    year: str
    first_author: str
    abstract: str
    url: str

    def to_dict(self) -> dict[str, str]:
        return {
            "pmid": self.pmid,
            "doi": self.doi,
            "pmcid": self.pmcid,
            "title": self.title,
            "journal": self.journal,
            "pubdate": self.pubdate,
            "year": self.year,
            "first_author": self.first_author,
            "abstract": self.abstract,
            "url": self.url,
        }


def esearch(term: str, retmax: int, timeout_s: int) -> tuple[int, list[str]]:
    params = {
        "db": "pubmed",
        "retmode": "json",
        "retmax": str(retmax),
        "term": term,
    }
    url = f"{EUTILS}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    payload = _http_get(url, timeout_s)
    data = json.loads(payload)
    result = data.get("esearchresult", {})
    count_total = int(result.get("count", "0") or "0")
    pmids = list(result.get("idlist", []) or [])
    return count_total, pmids


def _parse_article_ids(pubmed_data: ET.Element) -> tuple[str, str]:
    doi = ""
    pmcid = ""
    for aid in _all(pubmed_data, ".//ArticleIdList/ArticleId"):
        id_type = (aid.get("IdType") or "").lower()
        val = (aid.text or "").strip()
        if id_type == "doi" and not doi:
            doi = val.lower()
        if id_type == "pmc" and not pmcid:
            pmcid = val
    return doi, pmcid


def _parse_pub_date(article: ET.Element) -> tuple[str, str]:
    # Try multiple PubDate locations.
    pubdate_elem = _first(article, ".//JournalIssue/PubDate")
    if pubdate_elem is None:
        pubdate_elem = _first(article, ".//ArticleDate")
    if pubdate_elem is None:
        return ("", "")
    year = _text_or_empty(_first(pubdate_elem, "Year"))
    medline_date = _text_or_empty(_first(pubdate_elem, "MedlineDate"))
    if not year and medline_date:
        # MedlineDate examples: "2016 Jan", "2016", "2016 Nov-Dec"
        year = medline_date.strip().split(" ")[0]
    month = _text_or_empty(_first(pubdate_elem, "Month"))
    day = _text_or_empty(_first(pubdate_elem, "Day"))
    pubdate = " ".join([p for p in [year, month, day] if p])
    return pubdate, year


def efetch(pmids: list[str], timeout_s: int, sleep_s: float) -> list[PubmedRow]:
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "retmode": "xml",
        "id": ",".join(pmids),
    }
    url = f"{EUTILS}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    xml_text = _http_get(url, timeout_s)
    root = ET.fromstring(xml_text)

    rows: list[PubmedRow] = []
    for article in root.findall(".//PubmedArticle"):
        medline = _first(article, "MedlineCitation")
        if medline is None:
            continue
        pmid = _text_or_empty(_first(medline, "PMID"))
        art = _first(medline, "Article")
        if art is None or not pmid:
            continue

        title = _text_or_empty(_first(art, "ArticleTitle"))
        journal = _text_or_empty(_first(art, ".//Journal/Title"))
        pubdate, year = _parse_pub_date(art)

        # First author
        first_author = ""
        auth0 = _first(art, ".//AuthorList/Author")
        if auth0 is not None:
            last = _text_or_empty(_first(auth0, "LastName"))
            fore = _text_or_empty(_first(auth0, "ForeName"))
            collective = _text_or_empty(_first(auth0, "CollectiveName"))
            first_author = collective or " ".join([p for p in [fore, last] if p]).strip()

        # Abstract (concatenate sections)
        abs_elems = _all(art, ".//Abstract/AbstractText")
        abstract_parts = []
        for a in abs_elems:
            label = (a.get("Label") or "").strip()
            t = _text_or_empty(a)
            if not t:
                continue
            abstract_parts.append(f"{label}: {t}" if label else t)
        abstract = " ".join(abstract_parts).strip()

        pubmed_data = _first(article, "PubmedData")
        doi = ""
        pmcid = ""
        if pubmed_data is not None:
            doi, pmcid = _parse_article_ids(pubmed_data)

        url_pubmed = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        rows.append(
            PubmedRow(
                pmid=pmid,
                doi=doi,
                pmcid=pmcid,
                title=title,
                journal=journal,
                pubdate=pubdate,
                year=year,
                first_author=first_author,
                abstract=abstract,
                url=url_pubmed,
            )
        )

    if sleep_s > 0:
        time.sleep(sleep_s)
    return rows


def write_tsv(path: Path, rows: list[PubmedRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "pmid",
        "doi",
        "pmcid",
        "title",
        "journal",
        "pubdate",
        "year",
        "first_author",
        "abstract",
        "url",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r.to_dict())


def main() -> int:
    ap = argparse.ArgumentParser(description="Export PubMed records (including abstracts) via E-utilities.")
    ap.add_argument("--term", required=True, help="PubMed search term")
    ap.add_argument("--retmax", type=int, default=500, help="Maximum PMIDs to fetch from esearch")
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--timeout-s", type=int, default=40)
    ap.add_argument("--sleep-s", type=float, default=0.34)
    ap.add_argument("--batch-size", type=int, default=150)
    args = ap.parse_args()

    total, pmids = esearch(args.term, args.retmax, args.timeout_s)
    print(f"esearch count_total={total} retmax={args.retmax} returned_pmids={len(pmids)}")

    rows: list[PubmedRow] = []
    for i in range(0, len(pmids), args.batch_size):
        batch = pmids[i : i + args.batch_size]
        fetched = efetch(batch, args.timeout_s, args.sleep_s)
        rows.extend(fetched)
        print(f"efetch batch {i//args.batch_size+1}: pmids={len(batch)} rows={len(fetched)}")

    # Deduplicate by PMID, keep first (stable ordering from esearch)
    seen: set[str] = set()
    deduped: list[PubmedRow] = []
    for r in rows:
        if r.pmid in seen:
            continue
        seen.add(r.pmid)
        deduped.append(r)

    write_tsv(args.out_tsv, deduped)
    print(f"Wrote: {args.out_tsv} (rows={len(deduped)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
