#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import argparse
from pathlib import Path

import pandas as pd


DELIVERY_MODEL_LABELS = {
    "chw_door_to_door": "Community health worker delivery",
    "clinic_pickup_return_clinic": "Clinic/primary care",
    "mail_to_home_return_mail": "Mail-to-home",
    "home_mail": "Home mail, not otherwise specified",
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


def _write_tsv(path: Path, header: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in header})


def main() -> int:
    ap = argparse.ArgumentParser(description="Build evidence-map count tables and publication heatmaps.")
    ap.add_argument("--study-index", type=Path, default=Path("results/map/study_index.tsv"))
    ap.add_argument("--out-counts", type=Path, default=Path("results/map/evidence_map_counts.tsv"))
    ap.add_argument("--plots-dir", type=Path, default=Path("plots/publication"))
    ap.add_argument("--delivery-plot-name", default="evidence_gap_heatmap")
    ap.add_argument("--followup-plot-name", default="followup_reporting_heatmap")
    ap.add_argument("--title-suffix", default="records")
    args = ap.parse_args()

    mpl_config_dir = Path("/tmp/mplconfig")
    xdg_cache_dir = Path("/tmp/xdg_cache")
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    xdg_cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache_dir))

    df = pd.read_csv(args.study_index, sep="\t")

    key_cols = [
        "target_population",
        "delivery_model",
        "setting",
        "income_level",
        "followup_reporting_level",
    ]
    for c in key_cols:
        if c not in df.columns:
            raise SystemExit(f"Missing required column: {c}")

    counts = (
        df.groupby(key_cols, dropna=False)["record_id"]
        .nunique()
        .reset_index()
        .rename(columns={"record_id": "n_records"})
    )

    _write_tsv(args.out_counts, key_cols + ["n_records"], counts.to_dict(orient="records"))

    # Plotting is optional; keep minimal dependencies. We use matplotlib only.
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"Counts written; plotting skipped (missing deps): {e}")
        return 0

    plots_dir = args.plots_dir
    plots_dir.mkdir(parents=True, exist_ok=True)
    plots_png_dir = plots_dir / "png"
    plots_png_dir.mkdir(parents=True, exist_ok=True)

    def plot_heatmap(pivot: pd.DataFrame, title: str, outpath: Path, cmap: str = "Blues") -> None:
        data = pivot.values
        fig_w = max(9, 1.35 * pivot.shape[1])
        fig_h = max(4.2, 0.7 * pivot.shape[0])
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        im = ax.imshow(data, aspect="auto", cmap=cmap)
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_xticklabels(pivot.columns.tolist(), rotation=30, ha="right")
        ax.set_yticklabels(pivot.index.tolist())
        ax.set_title(title)
        ax.set_xlabel(pivot.columns.name or "")
        ax.set_ylabel(pivot.index.name or "")
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                ax.text(j, i, str(int(data[i, j])), ha="center", va="center", fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
        fig.tight_layout()
        fig.savefig(outpath)
        fig.savefig(plots_png_dir / (outpath.stem + ".png"), dpi=300)
        plt.close(fig)

    hm1 = (
        df.groupby(["target_population", "delivery_model"])["record_id"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    hm1 = hm1.rename(index=TARGET_POPULATION_LABELS, columns=DELIVERY_MODEL_LABELS)
    hm1.index.name = "Target population"
    hm1.columns.name = "Delivery model"
    plot_heatmap(
        hm1,
        f"Distribution by delivery model and target population ({args.title_suffix})",
        plots_dir / f"{args.delivery_plot_name}.pdf",
        cmap="Blues",
    )

    hm2 = (
        df.groupby(["followup_reporting_level", "delivery_model"])["record_id"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    hm2 = hm2.rename(index=FOLLOWUP_REPORTING_LABELS, columns=DELIVERY_MODEL_LABELS)
    hm2.index.name = "Follow-up reporting level"
    hm2.columns.name = "Delivery model"
    plot_heatmap(
        hm2,
        f"Follow-up reporting by delivery model ({args.title_suffix})",
        plots_dir / f"{args.followup_plot_name}.pdf",
        cmap="Greens",
    )

    print(f"Wrote: {args.out_counts}")
    print(f"Wrote: {plots_dir / f'{args.delivery_plot_name}.pdf'}")
    print(f"Wrote: {plots_dir / f'{args.followup_plot_name}.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
