#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def _safe_value_counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[col, "n"])
    s = df[col].fillna("").astype(str).replace({"nan": "", "None": ""})
    s = s.where(s != "", other="UNK")
    vc = s.value_counts(dropna=False).reset_index()
    vc.columns = [col, "n"]
    return vc


def _find_search_exports(search_dir: Path) -> list[Path]:
    if not search_dir.exists():
        return []
    return sorted(p for p in search_dir.glob("pubmed_query_*.tsv") if p.is_file())


def _dedup_candidates(exports: list[Path]) -> tuple[int, int]:
    if not exports:
        return (0, 0)
    frames = []
    for p in exports:
        df = _read_tsv(p)
        if not df.empty and "pmid" in df.columns:
            df["pmid"] = df["pmid"].astype(str).str.strip()
            frames.append(df[["pmid"]])
    if not frames:
        return (0, 0)
    all_df = pd.concat(frames, ignore_index=True)
    all_df = all_df[all_df["pmid"].notna() & (all_df["pmid"] != "") & (all_df["pmid"].str.lower() != "nan")]
    n_total_rows = len(all_df)
    n_dedup = all_df["pmid"].nunique()
    return (n_total_rows, n_dedup)


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize PRISMA-style counts and descriptive breakdowns from the evidence-map TSVs.")
    ap.add_argument("--study-index", type=Path, default=Path("results/map/study_index.tsv"))
    ap.add_argument("--exclusions", type=Path, default=Path("results/screening/exclusion_reasons.tsv"))
    ap.add_argument("--search-dir", type=Path, default=Path("results/search"))
    ap.add_argument("--out-dir", type=Path, default=Path("results/summary"))
    args = ap.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    study = _read_tsv(args.study_index)
    excl = _read_tsv(args.exclusions)

    # Ensure PRISMA-style accounting uses mutually exclusive sets:
    # a record cannot be both included and excluded.
    if not study.empty and not excl.empty and "record_id" in study.columns and "record_id" in excl.columns:
        included_ids = set(study["record_id"].fillna("").astype(str))
        excl = excl[~excl["record_id"].fillna("").astype(str).isin(included_ids)].copy()

    exports = _find_search_exports(args.search_dir)
    n_export_rows, n_candidates_dedup = _dedup_candidates(exports)

    overview = pd.DataFrame(
        [
            {"metric": "search_export_files", "value": str(len(exports))},
            {"metric": "search_export_total_rows", "value": str(n_export_rows)},
            {"metric": "candidates_dedup_screened", "value": str(n_candidates_dedup or "")},
            {"metric": "included_total", "value": str(len(study))},
            {"metric": "excluded_total", "value": str(len(excl))},
        ]
    )
    overview.to_csv(out_dir / "overview.tsv", sep="\t", index=False)

    if not excl.empty:
        reason_counts = _safe_value_counts(excl, "reason_code")
        reason_counts.to_csv(out_dir / "exclusion_reason_counts.tsv", sep="\t", index=False)

    # Core descriptive breakdowns for Results tables.
    breakdown_cols = [
        "year",
        "country_or_region",
        "income_level",
        "target_population",
        "setting",
        "delivery_model",
        "return_channel",
        "followup_support",
        "followup_reporting_level",
        "followup_closure_reported",
        "design",
        "assay_type",
        "triage_pathway",
        "equity_stratified_results_reported",
        "acceptability_reported",
        "cost_reported",
    ]
    for col in breakdown_cols:
        vc = _safe_value_counts(study, col)
        vc.to_csv(out_dir / f"included_{col}_counts.tsv", sep="\t", index=False)

    # Cascade reporting completeness (key story: uptake vs closure)
    if not study.empty:
        s = study.copy()
        # Normalize empties
        for c in ["n_invited", "n_participated", "uptake_pct", "assay_type", "triage_pathway", "followup_support", "followup_reporting_level", "followup_completion_pct"]:
            if c not in s.columns:
                s[c] = ""
            s[c] = s[c].fillna("").astype(str).str.strip().replace({"nan": "", "None": ""})

        def has_any(col: str) -> pd.Series:
            return s[col].astype(str).str.strip().ne("")

        # Step indicators (minimal, abstract-level feasible)
        step = pd.DataFrame(
            {
                "reach_denominator_reported": has_any("n_invited"),
                "uptake_n_reported": has_any("n_participated"),
                "uptake_pct_reported": has_any("uptake_pct"),
                "assay_type_reported": s["assay_type"].ne("") & s["assay_type"].ne("UNK"),
                "triage_pathway_reported": s["triage_pathway"].ne("") & s["triage_pathway"].ne("unk"),
                "followup_support_reported": s["followup_support"].ne("") & s["followup_support"].ne("unk"),
                "followup_referral_mentioned": s.get("followup_reporting_level", "").isin(["referral_only", "completion_reported"]),
                "followup_completion_reported": s.get("followup_reporting_level", "").eq("completion_reported"),
                "followup_completion_pct_reported": has_any("followup_completion_pct"),
            }
        )
        overall = step.mean().reset_index()
        overall.columns = ["element", "proportion"]
        overall["n_studies"] = len(s)
        overall.to_csv(out_dir / "cascade_reporting_overall.tsv", sep="\t", index=False)

        if "delivery_model" in s.columns:
            s2 = pd.concat([s[["delivery_model"]].fillna("UNK"), step], axis=1)
            by_model = s2.groupby("delivery_model", dropna=False).mean(numeric_only=True).reset_index()
            by_model.insert(1, "n_studies", s2.groupby("delivery_model")["delivery_model"].size().values)
            by_model.to_csv(out_dir / "cascade_reporting_by_delivery_model.tsv", sep="\t", index=False)

    # Follow-up reporting level by delivery model (key “落地闭环” table)
    followup_col = "followup_reporting_level" if "followup_reporting_level" in study.columns else "followup_closure_reported"
    if not study.empty and all(c in study.columns for c in ["delivery_model", followup_col]):
        tmp = study.copy()
        tmp["delivery_model"] = tmp["delivery_model"].fillna("UNK").astype(str).replace({"": "UNK"})
        tmp[followup_col] = tmp[followup_col].fillna("UNK").astype(str).replace({"": "UNK"})
        pivot = (
            tmp.pivot_table(
                index="delivery_model",
                columns=followup_col,
                values="record_id" if "record_id" in tmp.columns else "pmid",
                aggfunc="count",
                fill_value=0,
            )
            .reset_index()
            .rename_axis(None, axis=1)
        )
        pivot.to_csv(out_dir / "followup_closure_by_delivery_model.tsv", sep="\t", index=False)

    print(f"Wrote: {out_dir}/overview.tsv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
