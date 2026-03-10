#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _lower(s: str) -> str:
    return _norm(s).lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    t = text
    return any(term in t for term in terms)


def _infer_country(title: str, abstract: str) -> str:
    text = f"{title}\n{abstract}".lower()
    if "sloven" in text:
        return "Slovenia"
    if "estonia" in text:
        return "Estonia"
    if "dutch" in text or "netherlands" in text:
        return "Netherlands"
    if "ontario" in text or "canada" in text or "first nations" in text:
        return "Canada"
    if "south florida" in text or "united states" in text or "u.s." in text:
        return "United States"
    if "australia" in text or "victoria" in text:
        return "Australia"
    if "new zealand" in text or "aotearoa" in text or "māori" in text or "maori" in text:
        return "New Zealand"
    if "portugal" in text:
        return "Portugal"
    if "france" in text:
        return "France"
    if "spain" in text or "catalonia" in text:
        return "Spain"
    return "UNK"


def _income_level(country: str) -> str:
    hic = {
        "Australia",
        "Canada",
        "Estonia",
        "France",
        "Netherlands",
        "New Zealand",
        "Portugal",
        "Slovenia",
        "Spain",
        "United States",
    }
    if country in hic:
        return "HIC"
    if country == "UNK":
        return "UNK"
    return "UNK"


def _target_population(title: str, abstract: str) -> tuple[str, str]:
    text = f"{title}\n{abstract}".lower()
    if "non-attender" in text or "nonattender" in text or "non responder" in text or "non-responder" in text:
        return ("nonattenders", "")
    if "never-" in text and "screen" in text:
        return ("never_screened", "")
    if "under-screen" in text or "underscreen" in text:
        if "rural" in text:
            return ("rural_low_access", "rural under-screened")
        return ("underscreened_general", "")
    if "immigrant" in text or "minority" in text or "migrant" in text:
        return ("migrant_minority", "")
    if "indigenous" in text or "māori" in text or "maori" in text or "pacific" in text:
        return ("other", "Indigenous/minority focus")
    return ("other", "")


def _setting_and_delivery(title: str, abstract: str) -> tuple[str, str, str]:
    text = f"{title}\n{abstract}".lower()
    if _contains_any(
        text,
        [
            "mailed",
            "mailing",
            "mail-to-home",
            "home-based",
            "postal",
            "pre-paid envelope",
            "prepaid envelope",
        ],
    ):
        return ("home_mail", "mail_to_home_return_mail", "mail")
    if ("at home" in text or "home" in text) and ("kit" in text or "self-sampl" in text):
        return ("home_mail", "unk", "unk")
    if "community health worker" in text or "chw" in text:
        return ("community_outreach", "chw_door_to_door", "mixed")
    if "community" in text or "outreach" in text:
        return ("community_outreach", "outreach_event_distribution", "mixed")
    if "clinic" in text:
        return ("primary_care", "clinic_pickup_return_clinic", "in_person")
    if "pharmacy" in text:
        return ("pharmacy", "pharmacy_distribution", "in_person")
    return ("other", "unk", "unk")


def _followup_support(abstract: str) -> str:
    text = abstract.lower()
    if "reminder" in text or "phone call" in text or "letter" in text or "sms" in text:
        return "reminders"
    if "navigator" in text or "navigation" in text:
        return "navigation"
    if "incentive" in text or "voucher" in text:
        return "incentives"
    return "unk"


def _design(title: str, abstract: str) -> str:
    text = f"{title}\n{abstract}".lower()
    t = title.lower()
    # Avoid false positives from abstracts that contain a "PROTOCOL:" link or trial registration.
    # Restrict protocol detection to title-level signals.
    if "protocol" in t or "study protocol" in t or "rationale and design" in t:
        return "protocol"
    if "cluster" in text and "random" in text:
        return "cluster_RCT"
    if "random" in text or "randomised" in text or "randomized" in text:
        return "individual_RCT"
    if "mixed-method" in text or "mixed methods" in text:
        return "observational"
    if "questionnaire" in text or "survey" in text or "interview" in text:
        return "observational"
    if "program" in text and ("evaluation" in text or "implementation" in text):
        return "program_evaluation"
    return "other"


def _assay_type(abstract: str) -> str:
    text = abstract.lower()
    if "mrna" in text:
        return "mRNA"
    if "hpv dna" in text or "hrhpv" in text or "high-risk hpv" in text or "cobas" in text or "hybrid capture" in text:
        return "DNA"
    return "UNK"


def _triage_pathway(abstract: str) -> str:
    text = abstract.lower()
    if "colposcopy" in text:
        return "direct_colposcopy"
    if "cytolog" in text or "pap" in text:
        return "cytology"
    return "unk"


def _followup_reporting_level(title: str, abstract: str) -> tuple[str, str]:
    """
    Return (level, completion_pct_str):
      - none
      - referral_only
      - completion_reported (with completion % if inferable)
    """
    text = _lower(f"{title}\n{abstract}")
    mention_terms = [
        "follow-up",
        "follow up",
        "referred",
        "referral",
        "invited",
        "colposcopy",
        "triage",
        "attend",
        "attendance",
        "compliance",
        "adherence",
        "completed",
        "completion",
    ]
    if not _contains_any(text, mention_terms):
        return ("none", "")

    ratio_patterns = [
        r"(\d{1,4})\s*/\s*(\d{1,4})[^.]{0,80}(?:attend|attendance|follow[- ]?up|colposcop|compliance|adherence|completed|completion)",
        r"(?:attend|attendance|follow[- ]?up|colposcop|compliance|adherence|completed|completion)[^.]{0,80}(\d{1,4})\s*/\s*(\d{1,4})",
    ]
    for pat in ratio_patterns:
        m = re.search(pat, text)
        if not m:
            continue
        a = int(m.group(1))
        b = int(m.group(2))
        if b <= 0 or a < 0:
            continue
        pct = 100.0 * a / b
        if 0.0 <= pct <= 100.0:
            pct_str = f"{pct:.1f}".rstrip("0").rstrip(".")
            return ("completion_reported", pct_str)

    pct_patterns = [
        r"(\d{1,3}(?:\.\d+)?)\s*%[^.]{0,80}(?:attend|attendance|follow[- ]?up|colposcop|compliance|adherence|completed|completion)",
        r"(?:attend|attendance|follow[- ]?up|colposcop|compliance|adherence|completed|completion)[^.]{0,80}(\d{1,3}(?:\.\d+)?)\s*%",
    ]
    for pat in pct_patterns:
        m = re.search(pat, text)
        if not m:
            continue
        pct = float(m.group(1))
        if 0.0 <= pct <= 100.0:
            pct_str = f"{pct:.1f}".rstrip("0").rstrip(".")
            return ("completion_reported", pct_str)

    return ("referral_only", "")


def _parse_uptake_metrics(title: str, abstract: str) -> tuple[str, str, str]:
    """
    Conservative parsing of invitation/participation/uptake from abstract text.
    Returns (n_invited, n_participated, uptake_pct) as strings (or "" if unknown).

    Principles:
    - Only fill when numbers are explicitly tied to screening participation.
    - Avoid capturing HPV positivity rates.
    """
    text = _lower(f"{title}\n{abstract}")

    def _num(s: str) -> int:
        s = s.replace(",", "").replace(" ", "")
        return int(s)

    n_invited: str = ""
    n_participated: str = ""
    uptake_pct: str = ""

    # Uptake percent near participation/attendance/response/returned (screening-level)
    pct_pats = [
        r"(?:participation|response rate|attendance|uptake|returned)[^.\n]{0,40}(\d{1,3}(?:\.\d+)?)\s*%",
        r"(\d{1,3}(?:\.\d+)?)\s*%[^.\n]{0,40}(?:participation|response rate|attendance|uptake|returned)",
    ]
    for pat in pct_pats:
        m = re.search(pat, text)
        if not m:
            continue
        pct = float(m.group(1))
        if 0.0 <= pct <= 100.0:
            uptake_pct = f"{pct:.1f}".rstrip("0").rstrip(".")
            break

    # N invited/targeted
    invited_pats = [
        r"\b(\d{1,3}(?:,\d{3})+|\d{3,})\b[^.\n]{0,40}(?:women|participants)?[^.\n]{0,20}(?:were )?(?:invited|allocated|randomi[sz]ed|included|targeted)",
        r"(?:invited|allocated|randomi[sz]ed|included|targeted)[^.\n]{0,40}\b(\d{1,3}(?:,\d{3})+|\d{3,})\b",
        r"\bN\s*=\s*(\d{1,3}(?:,\d{3})+|\d{3,})\b[^.\n]{0,60}(?:invited|allocated|randomi[sz]ed|included|targeted)",
    ]
    for pat in invited_pats:
        m = re.search(pat, text)
        if not m:
            continue
        val = m.group(1)
        try:
            n = _num(val)
        except Exception:
            continue
        if n > 0:
            n_invited = str(n)
            break

    # N participated/returned/responded (screening-level)
    part_pats = [
        r"\b(n\s*=\s*)?(\d{1,3}(?:,\d{3})+|\d{2,})\b[^.\n]{0,40}(?:returned|responded|participat(?:ed|ion)|attend(?:ed|ance))",
        r"(?:returned|responded|participat(?:ed|ion)|attend(?:ed|ance))[^.\n]{0,40}\b(n\s*=\s*)?(\d{1,3}(?:,\d{3})+|\d{2,})\b",
    ]
    for pat in part_pats:
        m = re.search(pat, text)
        if not m:
            continue
        val = m.group(2)
        try:
            n = _num(val)
        except Exception:
            continue
        # guardrail: avoid capturing very small n that could be HPV+ follow-up subgroup
        if n >= 30:
            n_participated = str(n)
            break

    # If both N invited and N participated are present but uptake_pct missing, compute.
    if n_invited and n_participated and not uptake_pct:
        try:
            pct = 100.0 * int(n_participated) / int(n_invited)
            if 0.0 <= pct <= 100.0:
                uptake_pct = f"{pct:.1f}".rstrip("0").rstrip(".")
        except Exception:
            pass

    return (n_invited, n_participated, uptake_pct)


def _is_secondary_review(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in ["systematic review", "scoping review", "meta-analysis", "meta analysis", "review"])


@dataclass(frozen=True)
class Excl:
    record_id: str
    stage: str
    reason_code: str
    reason_notes: str
    source: str
    url: str


def main() -> int:
    ap = argparse.ArgumentParser(description="Screen PubMed exports and chart included studies into the evidence map schema.")
    ap.add_argument("--in-tsv", type=Path, nargs="+", required=True)
    ap.add_argument("--out-study-index", type=Path, default=Path("results/map/study_index.tsv"))
    ap.add_argument("--out-exclusions", type=Path, default=Path("results/screening/exclusion_reasons.tsv"))
    ap.add_argument("--append", action="store_true", help="Append to existing outputs (dedupe by record_id).")
    args = ap.parse_args()

    df = pd.concat([pd.read_csv(p, sep="\t") for p in args.in_tsv], ignore_index=True)
    df["pmid"] = df["pmid"].astype(str)
    df = df.drop_duplicates(subset=["pmid"])

    included_rows: list[dict[str, object]] = []
    exclusions: list[Excl] = []

    for _, r in df.iterrows():
        pmid = str(r.get("pmid", "")).strip()
        if not pmid or pmid.lower() == "nan":
            continue
        title = _norm(str(r.get("title", "")))
        abstract = _norm(str(r.get("abstract", "")))
        url = _norm(str(r.get("url", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")))

        record_id = f"PMID_{pmid}"
        text = _lower(f"{title}\n{abstract}")

        # Quick out: secondary reviews (we only chart primary studies)
        if _is_secondary_review(title):
            exclusions.append(Excl(record_id, "title_abstract", "SECONDARY_REVIEW", "Secondary evidence (review) not charted.", "PubMed", url))
            continue

        design = _design(title, abstract)
        if design == "protocol":
            exclusions.append(
                Excl(record_id, "title_abstract", "PROTOCOL_NO_OUTCOMES", "Protocol/design paper; not a primary implementation outcome report.", "PubMed", url)
            )
            continue

        # Scope: must be HPV + self-sampling + cervical screening
        if not _contains_any(text, ["hpv", "human papillomavirus"]) or not _contains_any(text, ["self-sampling", "self sampling", "self-collected", "self collected"]):
            exclusions.append(Excl(record_id, "title_abstract", "NOT_CERVICAL_SCREENING", "Not clearly HPV self-sampling in cervical screening context.", "PubMed", url))
            continue
        if not _contains_any(text, ["cervical", "cervix", "cervical-cancer", "cervical cancer"]):
            exclusions.append(Excl(record_id, "title_abstract", "NOT_CERVICAL_SCREENING", "Not cervical screening context.", "PubMed", url))
            continue

        # Exclude urine self-sampling (project boundary)
        if "urine" in text and "vaginal" not in text and "cervicovag" not in text:
            exclusions.append(Excl(record_id, "title_abstract", "NOT_VAGINAL_SELF_SAMPLING", "Urine self-sampling or vaginal self-sampling not confirmed.", "PubMed", url))
            continue

        # Access policy: abstract must support core fields
        if len(abstract) < 180:
            exclusions.append(Excl(record_id, "title_abstract", "INSUFFICIENT_ABSTRACT_INFO", "Abstract too short for core charting fields.", "PubMed", url))
            continue

        # Underscreened focus (hard requirement)
        underscreen_terms = [
            "underscreen",
            "under-screen",
            "nonattend",
            "non-attend",
            "never-screen",
            "non-responder",
            "hard-to-reach",
            "underserved",
        ]
        if not _contains_any(text, underscreen_terms):
            exclusions.append(Excl(record_id, "title_abstract", "NOT_UNDERSCREENED_FOCUS", "Does not clearly target underscreened/nonattender populations.", "PubMed", url))
            continue

        country = _infer_country(title, abstract)
        income = _income_level(country)
        target_pop, target_notes = _target_population(title, abstract)
        setting, delivery_model, return_channel = _setting_and_delivery(title, abstract)
        followup_support = _followup_support(abstract)
        assay = _assay_type(abstract)
        triage = _triage_pathway(abstract)

        n_invited, n_participated, uptake_pct = _parse_uptake_metrics(title, abstract)

        followup_reporting_level, followup_completion_pct = _followup_reporting_level(title, abstract)
        followup_closure_reported = "N" if followup_reporting_level == "none" else "Y"

        included_rows.append(
            {
                "record_id": record_id,
                "pmid": pmid,
                "doi": str(r.get("doi", "") or ""),
                "year": str(r.get("year", "") or ""),
                "title_short": title[:120],
                "country_or_region": country,
                "income_level": income,
                "target_population": target_pop,
                "target_population_notes": target_notes,
                "setting": setting,
                "delivery_model": delivery_model,
                "return_channel": return_channel,
                "followup_support": followup_support,
                "self_sampling_confirmed": "Y",
                "assay_type": assay,
                "triage_pathway": triage,
                "design": design,
                "n_invited": n_invited,
                "n_participated": n_participated,
                "uptake_pct": uptake_pct,
                "followup_closure_reported": followup_closure_reported,
                "followup_reporting_level": followup_reporting_level,
                "followup_completion_pct": followup_completion_pct,
                "followup_notes": "",
                "equity_stratified_results_reported": "Y" if "inequal" in text or "disparit" in text else "N",
                "acceptability_reported": "Y" if ("acceptab" in text or "perception" in text or "preference" in text) else "N",
                "cost_reported": "Y" if "cost" in text else "N",
                "key_barriers_facilitators": "",
                "limitations": "Auto-charted from abstract-level info; verify/complete when OA full text is available.",
            }
        )

    out_study = args.out_study_index
    out_study.parent.mkdir(parents=True, exist_ok=True)
    new_df = pd.DataFrame(included_rows)
    if args.append and out_study.exists() and out_study.stat().st_size > 0:
        existing = pd.read_csv(out_study, sep="\t")
        combined = pd.concat([existing, new_df], ignore_index=True) if not new_df.empty else existing
        if "record_id" in combined.columns:
            combined = combined.drop_duplicates(subset=["record_id"], keep="first")
        combined.to_csv(out_study, sep="\t", index=False)
    else:
        if included_rows:
            new_df.to_csv(out_study, sep="\t", index=False)
        else:
            out_study.write_text("", encoding="utf-8")

    out_excl = args.out_exclusions
    out_excl.parent.mkdir(parents=True, exist_ok=True)
    excl_header = ["record_id", "stage", "reason_code", "reason_notes", "source", "url"]
    if args.append and out_excl.exists() and out_excl.stat().st_size > 0:
        existing = pd.read_csv(out_excl, sep="\t")
        new_excl = pd.DataFrame(
            [
                {
                    "record_id": e.record_id,
                    "stage": e.stage,
                    "reason_code": e.reason_code,
                    "reason_notes": e.reason_notes,
                    "source": e.source,
                    "url": e.url,
                }
                for e in exclusions
            ]
        )
        combined = pd.concat([existing, new_excl], ignore_index=True) if not new_excl.empty else existing
        combined = combined.drop_duplicates(subset=["record_id", "stage"], keep="first")
        combined.to_csv(out_excl, sep="\t", index=False)
    else:
        with out_excl.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=excl_header, delimiter="\t")
            w.writeheader()
            for e in exclusions:
                w.writerow(
                    {
                        "record_id": e.record_id,
                        "stage": e.stage,
                        "reason_code": e.reason_code,
                        "reason_notes": e.reason_notes,
                        "source": e.source,
                        "url": e.url,
                    }
                )

    print(f"Candidates deduped: {len(df)}")
    print(f"Included (auto): {len(included_rows)} → {out_study}")
    print(f"Excluded: {len(exclusions)} → {out_excl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
