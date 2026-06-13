#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DELIVERY_MODEL_LABELS = {
    "chw_door_to_door": "Community health worker delivery",
    "clinic_pickup_return_clinic": "Clinic/primary care",
    "mail_to_home_return_mail": "Mail-to-home",
    "outreach_event_distribution": "Outreach-event distribution",
    "mixed_or_multiarm": "Mixed/multi-arm",
    "unk": "Unclear at record level",
}

TARGET_POPULATION_LABELS = {
    "migrant_minority": "Migrant/minority",
    "never_screened": "Never screened",
    "nonattenders": "Non-attenders",
    "other": "Other/unclear",
    "rural_low_access": "Rural/low access",
    "underscreened_general": "Underscreened general",
    "unk": "Unclear at record level",
}

FOLLOWUP_REPORTING_LABELS = {
    "completion_reported": "Completion reported",
    "none": "No follow-up reported",
    "referral_only": "Referral without completion metrics",
    "unk": "Unclear at record level",
}


def _read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def _n_unique(df: pd.DataFrame, col: str) -> int:
    return int(df[col].nunique(dropna=True))


def _counts(df: pd.DataFrame, col: str, id_col: str = "record_id") -> pd.Series:
    return df.groupby(col, dropna=False)[id_col].nunique().sort_values(ascending=False)


def _crosstab_counts(df: pd.DataFrame, a: str, b: str, id_col: str = "record_id") -> pd.DataFrame:
    tmp = (
        df.groupby([a, b], dropna=False)[id_col]
        .nunique()
        .reset_index()
        .rename(columns={id_col: "n"})
    )
    return tmp.pivot(index=a, columns=b, values="n").fillna(0).astype(int)


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit whether figure-driving tables match the current study_index and summary TSVs.")
    ap.add_argument("--study-index", type=Path, default=Path("results/map/study_index.tsv"))
    ap.add_argument("--overview", type=Path, default=Path("results/summary/overview.tsv"))
    ap.add_argument("--table-s4", type=Path, default=Path("results/summary/followup_closure_by_delivery_model.tsv"))
    ap.add_argument("--out-md", type=Path, default=Path("results/summary/figure_data_audit.md"))
    ap.add_argument("--out-dir", type=Path, default=Path("results/summary/figure_matrices"))
    args = ap.parse_args()

    df = _read_tsv(args.study_index)
    overview = _read_tsv(args.overview)
    s4 = _read_tsv(args.table_s4)

    required = [
        "record_id",
        "target_population",
        "delivery_model",
        "followup_reporting_level",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"study_index missing required columns: {missing}")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    included = _n_unique(df, "record_id")

    # Figure 2 matrix: target_population x delivery_model
    fig1 = _crosstab_counts(df, "target_population", "delivery_model")
    fig1_path = out_dir / "Figure2_delivery_model_by_target_population.tsv"
    fig1.to_csv(fig1_path, sep="\t")

    # Figure 3 matrix: followup_reporting_level x delivery_model
    fig2 = _crosstab_counts(df, "followup_reporting_level", "delivery_model")
    fig2_path = out_dir / "Figure3_followup_reporting_by_delivery_model.tsv"
    fig2.to_csv(fig2_path, sep="\t")

    # Compare Figure 3 against the raw audit matrix. The upload-facing
    # supplementary Table S4 uses human-readable labels, so this script reads
    # the internal matrix by default while retaining compatibility with the
    # older raw Table S4 shape.
    if "followup_reporting_level" in s4.columns:
        s4_norm = s4.set_index("followup_reporting_level").astype(int)
    elif "delivery_model" in s4.columns:
        s4_map = {
            "none": "none",
            "referral_only": "referral_only",
            "completion_reported": "completion_reported",
        }
        s4_norm = (
            s4.set_index("delivery_model")[["none", "referral_only", "completion_reported"]]
            .astype(int)
            .T.rename(index=s4_map)
        )
    else:
        raise SystemExit(f"{args.table_s4} must be either the raw Figure 3 matrix or the summary Table S4 shape")

    # Ensure fig2 has these rows; reindex if needed.
    row_order = ["none", "referral_only", "completion_reported"]

    fig2_norm = fig2.copy()
    for r in row_order:
        if r not in fig2_norm.index:
            fig2_norm.loc[r] = 0
    fig2_norm = fig2_norm.loc[row_order].astype(int)
    s4_norm = s4_norm.loc[row_order].astype(int)

    # Align columns
    common_cols = sorted(set(fig2_norm.columns) & set(s4_norm.columns))
    fig2_aligned = fig2_norm[common_cols]
    s4_aligned = s4_norm[common_cols]
    s4_match = bool((fig2_aligned.values == s4_aligned.values).all())

    # Overview numbers
    overview_map = dict(zip(overview["metric"].astype(str), overview["value"].astype(int)))
    expected_included = int(overview_map.get("included_total", -1))
    expected_screened = int(overview_map.get("candidates_dedup_screened", -1))
    expected_identified = int(overview_map.get("search_export_total_rows", -1))
    expected_excluded = int(overview_map.get("excluded_total", -1))

    # Basic totals used in the evidence-map report.
    delivery_totals = _counts(df, "delivery_model").to_dict()
    target_totals = _counts(df, "target_population").to_dict()
    followup_totals = _counts(df, "followup_reporting_level").to_dict()

    lines: list[str] = []
    lines.append("# Figure/Data Consistency Audit")
    lines.append("")
    lines.append(f"- Included records (unique record_id in study_index): **{included}**")
    lines.append(f"- Overview.tsv included_total: **{expected_included}**")
    lines.append(f"- Overview.tsv records screened (dedup): **{expected_screened}**; identified: **{expected_identified}**; excluded: **{expected_excluded}**")
    lines.append("")
    lines.append("## Figure 2 (delivery model × target population)")
    lines.append(f"- Matrix exported: `{fig1_path}`")
    lines.append("- Delivery-model column sums (should match Table 1 totals):")
    for k, v in sorted(delivery_totals.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"  - {DELIVERY_MODEL_LABELS.get(str(k), str(k))}: {v}")
    lines.append("- Target-population row sums (should match Table 1 totals):")
    for k, v in sorted(target_totals.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"  - {TARGET_POPULATION_LABELS.get(str(k), str(k))}: {v}")
    lines.append("")
    lines.append("## Figure 3 (follow-up reporting level × delivery model)")
    lines.append(f"- Matrix exported: `{fig2_path}`")
    lines.append("- Follow-up reporting-level totals:")
    for k, v in sorted(followup_totals.items(), key=lambda x: (-x[1], str(x[0]))):
        lines.append(f"  - {FOLLOWUP_REPORTING_LABELS.get(str(k), str(k))}: {v}")
    lines.append(f"- Figure 3 consistency (current matrix vs `{args.table_s4}`): **{'PASS' if s4_match else 'FAIL'}**")
    if not s4_match:
        lines.append("")
        lines.append("### Differences (Figure3 - Table S4)")
        diff = fig2_aligned - s4_aligned
        lines.append(diff.to_string())
    lines.append("")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"[audit] Wrote: {args.out_md}")
    print(f"[audit] Wrote: {fig1_path}")
    print(f"[audit] Wrote: {fig2_path}")
    print(f"[audit] Table S4 match: {s4_match}")

    # Strict sanity checks (exit non-zero if something fundamental diverges).
    ok = True
    if expected_included != -1 and included != expected_included:
        ok = False
    if not s4_match:
        ok = False
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
