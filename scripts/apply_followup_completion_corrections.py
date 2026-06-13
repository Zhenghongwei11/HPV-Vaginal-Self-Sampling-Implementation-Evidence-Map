#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


STUDY_INDEX = Path("results/map/study_index.tsv")
EXCLUSIONS = Path("results/screening/exclusion_reasons.tsv")
SEARCH_DIR = Path("results/search")
AUDIT_OUT = Path("results/summary/followup_completion_curation_audit.tsv")


# Focused manual review of records previously coded as completion_reported.
# Rule: code completion_reported only when the abstract reports actual
# post-positive clinical follow-up/triage/colposcopy/diagnostic completion,
# not screening uptake, kit return, sample validity, willingness, or model assumptions.
FOLLOWUP_CORRECTIONS: dict[str, tuple[str, str, str]] = {
    "21343937": ("completion_reported", "87.5", "HPV-positive participants: 7/8 attended cervical smear with concurrent colposcopy."),
    "21497619": ("none", "", "Reported self-collection return and Pap appointment attendance; no post-positive follow-up completion."),
    "21752985": ("none", "", "Reported screening attendance/coverage; no post-positive follow-up completion."),
    "21484793": ("completion_reported", "89.1", "HPV-positive self-sampling responders: 89.1% adherence to cytology triage; colposcopy referral adherence 95.8%."),
    "22172570": ("referral_only", "", "Reported CIN yield from linked data but no follow-up attendance/completion metric."),
    "23137168": ("completion_reported", "69.3", "HR-HPV-positive women: 43/62 had 12-month follow-up."),
    "23712523": ("none", "", "Reported screening participation and lesion detection; no post-positive follow-up completion."),
    "23867008": ("completion_reported", "70.0", "hrHPV-positive self-sampled women: 7/10 attended colposcopy."),
    "24529697": ("referral_only", "", "Triage-positive women were referred for colposcopy; attendance/completion not reported."),
    "24736093": ("none", "", "Reported questionnaire/sample return and preferences; no post-positive follow-up completion."),
    "25403717": ("completion_reported", "59.4", "hrHPV-positive participants: 19/32 subsequently attended cytology screening."),
    "25432954": ("none", "", "Model-based evaluation; no empirical post-positive follow-up completion."),
    "25742805": ("none", "", "Reported GP consultation rates among non-attenders; no self-sampling follow-up completion."),
    "26850941": ("completion_reported", "62.2", "HPV16/18-positive participants: 28/45 had colposcopy; other hrHPV pathway reported 82.1% Pap testing."),
    "27073929": ("completion_reported", "94.1", "hrHPV-positive self-sampling subgroup: 32/34 attended follow-up."),
    "27235844": ("completion_reported", "85.0", "HPV-positive participants: 33/39 attended follow-up."),
    "28193227": ("completion_reported", "77.5", "HPV-positive women: 320/414 had follow-up procedures."),
    "28195317": ("none", "", "Reported request/return and physician screening after invitation; no HPV-positive follow-up completion."),
    "28631511": ("referral_only", "", "HPV-positive women were referred to colposcopy; attendance/completion not reported."),
    "29136403": ("referral_only", "", "HPV-positive women were referred for cytology/HPV co-testing; completion not reported."),
    "29569715": ("completion_reported", "88.9", "hrHPV-positive participants: 88.9% attended follow-up cytology."),
    "29594933": ("none", "", "Reported cervical screening completion, not post-positive follow-up completion."),
    "29995217": ("none", "", "81.0% was HPV self-sampling completion, not clinical follow-up after a positive result."),
    "30606132": ("referral_only", "", "HPV-positive women were triaged and VIA-positive women treated; HPV-positive follow-up attendance not reported."),
    "30614524": ("none", "", "Reported willingness to attend follow-up if positive, not observed follow-up completion."),
    "30651294": ("none", "", "Reported screening completion by arm; no post-positive follow-up completion."),
    "30718124": ("none", "", "Model-based cost-effectiveness study; no empirical post-positive follow-up completion."),
    "31002831": ("none", "", "Assay performance/optimization study; no implementation follow-up completion."),
    "31032904": ("completion_reported", "68.3", "Directly referred participants: 43/63 attended colposcopy."),
    "31427275": ("completion_reported", "68.6", "Colposcopy referral compliance reported by age group; lowest explicit value was 68.6%."),
    "32168286": ("none", "", "Reported self-collection uptake after stated willingness; no post-positive follow-up completion."),
    "32234744": ("completion_reported", "77.8", "hrHPV-positive participants: 168/216 underwent same-day colposcopy."),
    "32343627": ("completion_reported", "65.0", "CHWs navigated 65% of HPV-positive women to colposcopy."),
    "32371553": ("none", "", "Reported reasons for screening non-participation; no post-positive follow-up completion."),
    "32393243": ("completion_reported", "56.4", "HPV-positive participants completing follow-up: 22/39 across HPV16/18 and other hrHPV groups."),
    "31522376": ("referral_only", "", "Study describes HPV-positive non-attenders who attended examination but not a completion denominator for all positives."),
    "33219163": ("none", "", "Modeled analysis; no empirical post-positive follow-up completion."),
    "33338505": ("none", "", "Reported screening adherence and modality choice, not post-positive follow-up completion."),
    "33842403": ("completion_reported", "85.7", "HPV-positive women: 353/412 attended follow-up."),
    "34031326": ("none", "", "Reported self-collection perception questionnaire completion, not follow-up completion."),
    "34373426": ("referral_only", "", "HPV-positive participants were referred to cytology triage; follow-up compliance not quantified in abstract."),
    "34875556": ("completion_reported", "73.9", "HPV-positive participants: 17/23 attended colposcopy."),
    "35287163": ("none", "", "Reported acceptability and HPV positivity; no post-positive follow-up completion."),
    "35313763": ("completion_reported", "84.0", "First-round follow-up compliance was 84%; 12-month follow-up compliance was 59.3%."),
    "35594924": ("completion_reported", "92.0", "HPV-positive women: 92% adhered to recommended follow-up."),
    "35995936": ("completion_reported", "92.5", "Women with positive self-sample: 92.5% attended clinic triage testing."),
    "36451884": ("none", "", "Reported barriers/motivators survey; no post-positive follow-up completion."),
    "37174865": ("completion_reported", "57.0", "Among high-risk HPV-positive women, 57% followed up with physicians for care."),
    "37232493": ("none", "", "Reported barriers/motivators survey; no post-positive follow-up completion."),
    "37280031": ("none", "", "Economic model used complete screens, not post-positive clinical follow-up completion."),
    "37664989": ("none", "", "Clinician survey on pandemic-related screening changes; no HPV-positive follow-up completion."),
    "39516742": ("referral_only", "", "hrHPV-positive women were invited for colposcopy; attendance/completion not reported."),
    "39682257": ("completion_reported", "90.0", "Compliance to immediate colposcopy and cytology triage exceeded 90%; coded conservatively as 90.0%."),
    "39727713": ("none", "", "Reported HPV self-sampling choice and positivity; no post-positive follow-up completion."),
    "39617104": ("none", "", "Modeling study using assumed screening/colposcopy adherence, not observed implementation follow-up."),
    "40192218": ("completion_reported", "80.2", "HPV-positive women: 80.2% attended follow-up."),
    "40359821": ("none", "", "Questionnaire response/perceptions study; no post-positive follow-up completion."),
    "40726443": ("completion_reported", "91.7", "hrHPV-positive participants: 11/12 completed gynecological follow-up."),
    "40789299": ("completion_reported", "95.0", "Oncogenic HPV-positive participants: 21/22 completed same-day colposcopic assessment."),
    "41032297": ("none", "", "Economic evaluation of screening completion; no post-positive follow-up completion."),
    "41459991": ("referral_only", "", "Reported HPV positivity and cancer/HSIL yield; follow-up attendance/completion not reported."),
    "41065509": ("none", "", "Modeling study using assumptions about loss to follow-up; no observed follow-up completion."),
    "41505134": ("none", "", "Follow-up care referred to STI-positive participants, not cervical/HPV-positive follow-up completion."),
    "38578742": ("completion_reported", "45.5", "HPV-positive triage compliance was reported by site (53.6%, 45.5%, and 84.6%); lowest explicit site value coded conservatively."),
    "38415526": ("completion_reported", "45.2", "HPV-positive colposcopy attendance increased from 28.5% to 45.2% with outreach clinics; one-year follow-up participation was 60%."),
    "35878625": ("completion_reported", "98.8", "Among 647 HPV-positive women, 602 received same-day thermal ablation and 37/42 referred women attended gynecology review."),
    "35003710": ("completion_reported", "35.0", "Among hrHPV-positive participants who reported receiving SMS follow-up instructions, 6/17 presented for follow-up."),
    "34639352": ("referral_only", "", "Study described follow-up protocols and HPV-positive findings but did not report an observed follow-up completion denominator for all positives."),
    "33555038": ("completion_reported", "98.0", "Among high-risk HPV-positive women, 82% attended after text-message reminder and an additional 16% after text plus phone reminder."),
    "32416283": ("completion_reported", "72.0", "HPV-positive women attending clinic triage examination: 72%."),
    "31995585": ("none", "", "Provider preparedness survey for implementation of renewed screening programme; no observed HPV-positive follow-up completion."),
    "31970767": ("completion_reported", "100.0", "Women positive on HPV with abnormal colposcopy who were eligible for thermal ablation all accepted same-day treatment."),
    "31337647": ("completion_reported", "85.0", "Out of women positive for high-risk HPV, 122 (85%) attended VIA as follow-up test."),
    "26421807": ("referral_only", "", "Diagnostic performance study with baseline and one-year procedures; no HPV-positive follow-up completion denominator reported."),
    "23731506": ("completion_reported", "74.3", "Among women infected with HPV, 26/35 (74.3%) attended colposcopy appointments."),
    "41285635": ("referral_only", "", "Reported HPV self-sampling completion and referral counts after positive results, but not completion of Pap/colposcopy referral."),
    "40275341": ("completion_reported", "40.0", "Follow-up compliance among hrHPV-positive women was 40% (4/10)."),
    "39396430": ("completion_reported", "88.3", "Compliance to colposcopy follow-up among HPV mRNA-positive women was 88.3%."),
    "36316070": ("completion_reported", "96.9", "Among 229 HPV-positive women, 222 attended follow-up."),
    "32614875": ("completion_reported", "87.0", "Attendance to recommended follow-up after abnormality was 87%."),
    "22017806": ("completion_reported", "84.8", "Among high-risk HPV-positive women, 56/66 attended surgery/colposcopy after self-sampling."),
}


TRIAGE_PATHWAY_CORRECTIONS: dict[str, tuple[str, str]] = {
    "25403717": ("cytology", "The reported 19/32 follow-up completion refers to attendance for cytology triage after an hrHPV-positive self-sample."),
}


ADD_RECORD_41787233 = {
    "record_id": "PMID_41787233",
    "pmid": "41787233",
    "doi": "10.1007/s10900-026-01554-1",
    "year": "2026",
    "title_short": "Acceptability and Feasibility of Home-Based Human Papillomavirus Self-Testing as Primary Screening for Cervical Cancer Detection in the State of Alabama.",
    "country_or_region": "United States",
    "income_level": "HIC",
    "target_population": "underscreened_general",
    "target_population_notes": "No Pap test in last 3.5 years; rural residency or African American eligibility criterion.",
    "setting": "home_mail",
    "delivery_model": "mail_to_home_return_mail",
    "return_channel": "mail",
    "followup_support": "none_reported",
    "self_sampling_confirmed": "Y",
    "assay_type": "DNA",
    "triage_pathway": "direct_colposcopy",
    "design": "observational",
    "n_invited": "58",
    "n_participated": "35",
    "uptake_pct": "60.0",
    "followup_closure_reported": "Y",
    "followup_reporting_level": "referral_only",
    "followup_completion_pct": "",
    "followup_notes": "HR-HPV-positive participants received referral information for follow-up; completion not reported in abstract.",
    "equity_stratified_results_reported": "N",
    "acceptability_reported": "Y",
    "cost_reported": "N",
    "key_barriers_facilitators": "CHW recruitment, health literacy, medical trust, mailed home test kit.",
    "limitations": "Follow-up completion after referral not reported in abstract.",
}


def _read_search_records() -> pd.DataFrame:
    frames = []
    for path in sorted(SEARCH_DIR.glob("pubmed_query_*.tsv")):
        frames.append(pd.read_csv(path, sep="\t", dtype=str).fillna(""))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates("pmid")


def main() -> int:
    study = pd.read_csv(STUDY_INDEX, sep="\t", dtype=str).fillna("")
    exclusions = pd.read_csv(EXCLUSIONS, sep="\t", dtype=str).fillna("")
    search = _read_search_records()

    audit_rows: list[dict[str, str]] = []

    for pmid, (new_level, new_pct, note) in FOLLOWUP_CORRECTIONS.items():
        mask = study["pmid"].eq(pmid)
        if not mask.any():
            raise SystemExit(f"PMID {pmid} not found in {STUDY_INDEX}")
        old = study.loc[mask].iloc[0].to_dict()
        study.loc[mask, "followup_reporting_level"] = new_level
        study.loc[mask, "followup_completion_pct"] = new_pct
        study.loc[mask, "followup_closure_reported"] = "N" if new_level == "none" else "Y"
        study.loc[mask, "followup_notes"] = note
        audit_rows.append(
            {
                "pmid": pmid,
                "title_short": old.get("title_short", ""),
                "old_followup_reporting_level": old.get("followup_reporting_level", ""),
                "old_followup_completion_pct": old.get("followup_completion_pct", ""),
                "new_followup_reporting_level": new_level,
                "new_followup_completion_pct": new_pct,
                "curation_note": note,
            }
        )

    for pmid, (new_triage, note) in TRIAGE_PATHWAY_CORRECTIONS.items():
        mask = study["pmid"].eq(pmid)
        if not mask.any():
            raise SystemExit(f"PMID {pmid} not found in {STUDY_INDEX}")
        study.loc[mask, "triage_pathway"] = new_triage
        if note:
            study.loc[mask, "followup_notes"] = note

    if not study["pmid"].eq("41787233").any():
        row = {col: ADD_RECORD_41787233.get(col, "") for col in study.columns}
        study = pd.concat([study, pd.DataFrame([row])], ignore_index=True)
        title = ADD_RECORD_41787233["title_short"]
        if not search.empty and search["pmid"].eq("41787233").any():
            title = search.loc[search["pmid"].eq("41787233"), "title"].iloc[0]
        audit_rows.append(
            {
                "pmid": "41787233",
                "title_short": title,
                "old_followup_reporting_level": "excluded: NOT_UNDERSCREENED_FOCUS",
                "old_followup_completion_pct": "",
                "new_followup_reporting_level": "referral_only",
                "new_followup_completion_pct": "",
                "curation_note": "Moved from exclusions to included records; abstract specifies no Pap test in last 3.5 years and underserved/rural/African American eligibility.",
            }
        )

    exclusions = exclusions[~exclusions["record_id"].eq("PMID_41787233")].copy()

    STUDY_INDEX.parent.mkdir(parents=True, exist_ok=True)
    EXCLUSIONS.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    study.to_csv(STUDY_INDEX, sep="\t", index=False)
    exclusions.to_csv(EXCLUSIONS, sep="\t", index=False)
    pd.DataFrame(audit_rows).to_csv(AUDIT_OUT, sep="\t", index=False)

    print(f"Wrote: {STUDY_INDEX} ({len(study)} records)")
    print(f"Wrote: {EXCLUSIONS} ({len(exclusions)} exclusions)")
    print(f"Wrote: {AUDIT_OUT} ({len(audit_rows)} curation rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
