#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _not_unknown(series: pd.Series) -> pd.Series:
    return ~series.astype(str).str.strip().str.lower().isin(["", "unk", "unknown", "other/unclear"])


def _nonempty(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().ne("")


def build_table(study_index: Path, pubmed_exports: list[Path]) -> pd.DataFrame:
    records = pd.read_csv(study_index, sep="\t", dtype=str).fillna("")
    search = pd.concat(
        [pd.read_csv(path, sep="\t", dtype=str).fillna("") for path in pubmed_exports],
        ignore_index=True,
    ).drop_duplicates("pmid")

    meta = search[["pmid", "pmcid"]].copy()
    meta["pmcid"] = meta["pmcid"].astype(str).str.strip()
    meta["pmc_fulltext_proxy"] = meta["pmcid"].ne("")

    df = records.merge(meta, on="pmid", how="left")
    df["pmc_fulltext_proxy"] = df["pmc_fulltext_proxy"].fillna(False)
    df["access_proxy_group"] = df["pmc_fulltext_proxy"].map(
        {True: "PMCID available", False: "No PMCID recorded"}
    )

    metrics = [
        ("Country/region extractable", _not_unknown(df["country_or_region"])),
        ("Income level extractable", _not_unknown(df["income_level"])),
        ("Delivery model classifiable", ~df["delivery_model"].str.lower().isin(["unk", "unknown", ""])),
        ("Return channel classifiable", ~df["return_channel"].str.lower().isin(["unk", "unknown", ""])),
        ("Follow-up support reported", ~df["followup_support"].str.lower().isin(["unk", "unknown", ""])),
        ("Triage pathway classifiable", ~df["triage_pathway"].str.lower().isin(["unk", "unknown", ""])),
        ("Invitation/reach denominator reported", _nonempty(df["n_invited"])),
        ("Participation count reported", _nonempty(df["n_participated"])),
        ("Uptake percentage reported", _nonempty(df["uptake_pct"])),
        ("Follow-up completion reported", df["followup_reporting_level"].eq("completion_reported")),
        ("Follow-up completion percentage reported", _nonempty(df["followup_completion_pct"])),
        ("Equity-stratified result reported", df["equity_stratified_results_reported"].eq("Y")),
        ("Cost/resource information reported", df["cost_reported"].eq("Y")),
    ]

    rows: list[dict[str, object]] = []
    for metric, mask in metrics:
        for group, sub in df.groupby("access_proxy_group", sort=False):
            group_mask = mask.loc[sub.index]
            n_records = len(sub)
            n_yes = int(group_mask.sum())
            rows.append(
                {
                    "metric": metric,
                    "access_proxy_group": group,
                    "n_records": n_records,
                    "reported_or_extractable_n": n_yes,
                    "reported_or_extractable_pct": round(100 * n_yes / n_records, 1),
                }
            )

        pmc = df["access_proxy_group"].eq("PMCID available")
        no_pmc = df["access_proxy_group"].eq("No PMCID recorded")
        rows.append(
            {
                "metric": metric,
                "access_proxy_group": "Difference: PMCID available minus no PMCID (percentage points)",
                "n_records": "",
                "reported_or_extractable_n": "",
                "reported_or_extractable_pct": round(100 * mask[pmc].mean() - 100 * mask[no_pmc].mean(), 1),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build PMCID-availability proxy sensitivity table for record-level reporting visibility."
    )
    parser.add_argument("--study-index", type=Path, default=Path("supplement/Dataset_S1_Charted_study_index.tsv"))
    parser.add_argument(
        "--pubmed-export",
        type=Path,
        action="append",
        required=True,
        help="PubMed export TSV with pmid and pmcid columns. Repeat for multiple exports.",
    )
    parser.add_argument("--out", type=Path, default=Path("supplement/Table_S5_PMC_fulltext_proxy_sensitivity.tsv"))
    args = parser.parse_args()

    table = build_table(args.study_index, args.pubmed_export)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, sep="\t", index=False)
    print(f"Wrote {args.out} ({len(table)} rows).")


if __name__ == "__main__":
    main()
