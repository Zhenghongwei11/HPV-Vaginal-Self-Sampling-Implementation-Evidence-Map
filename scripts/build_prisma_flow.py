#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd


def _read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t")


def _get_metric(overview: pd.DataFrame, key: str, default: int = 0) -> int:
    if overview.empty or "metric" not in overview.columns or "value" not in overview.columns:
        return default
    hit = overview.loc[overview["metric"] == key, "value"]
    if hit.empty:
        return default
    try:
        return int(str(hit.iloc[0]).strip() or default)
    except Exception:
        return default


def _wrap_reason_lines(reasons: list[tuple[str, int]], max_lines: int = 5) -> str:
    items = reasons[:max_lines]
    return "\n".join([f"- {k}: {v}" for k, v in items])


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a PRISMA-ScR style flow diagram from summary TSVs.")
    ap.add_argument("--overview", type=Path, default=Path("results/summary/overview.tsv"))
    ap.add_argument("--exclusion-reasons", type=Path, default=Path("results/summary/exclusion_reason_counts.tsv"))
    ap.add_argument("--out-pdf", type=Path, default=Path("plots/publication/prisma_flow.pdf"))
    ap.add_argument("--out-numbers", type=Path, default=Path("results/summary/prisma_flow_numbers.tsv"))
    args = ap.parse_args()

    overview = _read_tsv(args.overview)
    reasons_df = _read_tsv(args.exclusion_reasons)

    n_identified = _get_metric(overview, "search_export_total_rows", 0)
    n_candidates = _get_metric(overview, "candidates_dedup_screened", 0)
    n_included = _get_metric(overview, "included_total", 0)
    n_excluded = _get_metric(overview, "excluded_total", 0)
    n_duplicates_removed = max(0, n_identified - n_candidates) if (n_identified and n_candidates) else 0

    reasons: list[tuple[str, int]] = []
    if not reasons_df.empty and {"reason_code", "n"}.issubset(set(reasons_df.columns)):
        for _, r in reasons_df.iterrows():
            code = str(r["reason_code"]).strip()
            try:
                c = int(r["n"])
            except Exception:
                continue
            if code:
                reasons.append((code, c))

    reasons_text = _wrap_reason_lines(reasons, max_lines=6)

    # Write numbers table for auditability
    args.out_numbers.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {"metric": "records_identified", "value": n_identified},
            {"metric": "duplicates_removed", "value": n_duplicates_removed},
            {"metric": "records_screened", "value": n_candidates},
            {"metric": "records_excluded", "value": n_excluded},
            {"metric": "studies_included", "value": n_included},
        ]
    ).to_csv(args.out_numbers, sep="\t", index=False)

    # Plot diagram (matplotlib only)
    mpl_config_dir = Path("/tmp/mplconfig")
    xdg_cache_dir = Path("/tmp/xdg_cache")
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    xdg_cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache_dir))

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    args.out_pdf.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def box(x: float, y: float, w: float, h: float, text: str, fs: int = 11) -> None:
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.008",
            linewidth=1.2,
            edgecolor="#1f2937",
            facecolor="#f8fafc",
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color="#111827", wrap=True)

    def arrow(x0: float, y0: float, x1: float, y1: float) -> None:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "#111827"})

    ax.text(0.5, 0.965, "PRISMA-ScR Flow (Record-level; abstract/OA charting)", ha="center", va="top", fontsize=14, weight="bold")

    # Main vertical flow boxes
    main_x, main_w, main_h = 0.12, 0.76, 0.10
    y1, y2, y3, y4, y5 = 0.83, 0.67, 0.51, 0.35, 0.19

    box(
        main_x,
        y1,
        main_w,
        main_h,
        f"Records identified from PubMed exports\n(n = {n_identified})",
        fs=12,
    )

    box(
        main_x,
        y2,
        main_w,
        main_h,
        f"Records after duplicates removed\n(n = {n_candidates})",
        fs=12,
    )

    # Side duplicates box
    side_x, side_w, side_h = 0.72, 0.26, 0.07
    box(
        side_x,
        y2 + 0.02,
        side_w,
        side_h,
        f"Duplicates removed\n(n = {n_duplicates_removed})",
        fs=10,
    )

    box(
        main_x,
        y3,
        main_w,
        main_h,
        f"Records screened (title/abstract)\n(n = {n_candidates})",
        fs=12,
    )

    excl_text = f"Records excluded with reasons\n(n = {n_excluded})"
    if reasons_text:
        excl_text += "\n\nTop reasons:\n" + reasons_text
    box(main_x, y4, main_w, 0.14, excl_text, fs=10)

    box(
        main_x,
        y5,
        main_w,
        main_h,
        f"Studies included in evidence map\n(n = {n_included})",
        fs=12,
    )

    # Arrows
    arrow(0.5, y1, 0.5, y2 + main_h)
    arrow(0.5, y2, 0.5, y3 + main_h)
    arrow(0.5, y3, 0.5, y4 + 0.14)
    arrow(0.5, y4, 0.5, y5 + main_h)

    # Footnote
    foot = (
        "Note: Eligibility and charting were performed at the record level using sufficiently detailed abstracts "
        "and/or open-access full text under a reproducible access policy; no separate full-text retrieval step was required."
    )
    ax.text(0.5, 0.06, foot, ha="center", va="center", fontsize=9, color="#374151", wrap=True)

    fig.savefig(args.out_pdf)
    plt.close(fig)

    print(f"Wrote: {args.out_pdf}")
    print(f"Wrote: {args.out_numbers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

