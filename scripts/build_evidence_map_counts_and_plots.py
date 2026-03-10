#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
from pathlib import Path

import pandas as pd


def _write_tsv(path: Path, header: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in header})


def main() -> int:
    mpl_config_dir = Path("/tmp/mplconfig")
    xdg_cache_dir = Path("/tmp/xdg_cache")
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    xdg_cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache_dir))

    study_index = Path("results/map/study_index.tsv")
    out_counts = Path("results/map/evidence_map_counts.tsv")

    df = pd.read_csv(study_index, sep="\t")

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
        .rename(columns={"record_id": "n_studies"})
    )

    _write_tsv(out_counts, key_cols + ["n_studies"], counts.to_dict(orient="records"))

    # Plotting is optional; keep minimal dependencies. We use matplotlib only.
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"Counts written; plotting skipped (missing deps): {e}")
        return 0

    plots_dir = Path("plots/publication")
    plots_dir.mkdir(parents=True, exist_ok=True)

    def plot_heatmap(pivot: pd.DataFrame, title: str, outpath: Path, cmap: str = "Blues") -> None:
        data = pivot.values
        fig_w = max(8, 0.9 * pivot.shape[1])
        fig_h = max(3.5, 0.55 * pivot.shape[0])
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        im = ax.imshow(data, aspect="auto", cmap=cmap)
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_xticklabels(pivot.columns.tolist(), rotation=35, ha="right")
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
        plt.close(fig)

    hm1 = (
        df.groupby(["target_population", "delivery_model"])["record_id"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    hm1.index.name = "target_population"
    hm1.columns.name = "delivery_model"
    plot_heatmap(
        hm1,
        "Evidence map: delivery model × target population (n studies)",
        plots_dir / "evidence_gap_heatmap.pdf",
        cmap="Blues",
    )

    hm2 = (
        df.groupby(["followup_reporting_level", "delivery_model"])["record_id"]
        .nunique()
        .unstack(fill_value=0)
        .sort_index()
    )
    hm2.index.name = "followup_reporting_level"
    hm2.columns.name = "delivery_model"
    plot_heatmap(
        hm2,
        "Follow-up reporting level by delivery model (n studies)",
        plots_dir / "followup_reporting_heatmap.pdf",
        cmap="Greens",
    )

    print(f"Wrote: {out_counts}")
    print(f"Wrote: {plots_dir / 'evidence_gap_heatmap.pdf'}")
    print(f"Wrote: {plots_dir / 'followup_reporting_heatmap.pdf'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
