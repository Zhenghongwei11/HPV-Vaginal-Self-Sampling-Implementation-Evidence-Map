#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


WORKSHEET = Path("results/summary/FINAL_58_ADJUDICATION_WORKSHEET.tsv")
STUDY_INDEX = Path("results/map/study_index.tsv")
EXCLUSIONS = Path("results/screening/exclusion_reasons.tsv")
AUDIT = Path("results/summary/implementation_core_eligibility_audit.tsv")
SEARCH_EXPORTS = [Path("results/search/pubmed_query_a.tsv"), Path("results/search/pubmed_query_b.tsv")]


STUDY_FIELDS = [
    "record_id",
    "pmid",
    "doi",
    "year",
    "title_short",
    "country_or_region",
    "income_level",
    "target_population",
    "target_population_notes",
    "setting",
    "delivery_model",
    "return_channel",
    "followup_support",
    "self_sampling_confirmed",
    "assay_type",
    "triage_pathway",
    "design",
    "n_invited",
    "n_participated",
    "uptake_pct",
    "followup_closure_reported",
    "followup_reporting_level",
    "followup_completion_pct",
    "followup_notes",
    "equity_stratified_results_reported",
    "acceptability_reported",
    "cost_reported",
    "key_barriers_facilitators",
    "limitations",
]

AUDIT_FIELDS = [
    "pmid",
    "year",
    "title_short",
    "current_design",
    "current_target_population",
    "current_delivery_model",
    "current_followup_reporting_level",
    "current_followup_completion_pct",
    "n_invited",
    "n_participated",
    "uptake_pct",
    "acceptability_reported",
    "cost_reported",
    "candidate_core_status",
    "candidate_reason",
    "manual_reviewer_decision",
    "manual_reviewer_notes",
    "manual_core_decision",
    "manual_decision_reason",
    "manual_evidence_text",
    "manual_followup_level_if_changed",
    "manual_followup_pct_if_changed",
    "manual_notes",
    "reviewer_initials",
    "review_date",
]


CORE_PMIDS = {
    "35436908",
    "33660168",
    "41621746",
    "40956285",
    "40952305",
    "40877387",
    "40567147",
    "38648390",
    "38109300",
    "37964260",
    "37692077",
    "37289798",
    "36635749",
    "35078829",
    "34972808",
    "29523108",
    "26294825",
    "26242529",
    "26031572",
}


CHARTING: dict[str, dict[str, str]] = {
    "41214745": dict(country_or_region="Uganda", income_level="LMIC", target_population="rural_low_access", setting="health_system_policy", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "35436908": dict(country_or_region="Kenya", income_level="LMIC", target_population="rural_low_access", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="outreach_event", followup_support="referral", assay_type="DNA", triage_pathway="unk", design="cross_sectional", self_sampling_confirmed="Y", n_invited="2016", n_participated="749", uptake_pct="35.6", followup_reporting_level="none", followup_closure_reported="N", equity_stratified_results_reported="Y"),
    "35384556": dict(country_or_region="Uganda", income_level="LMIC", target_population="rural_low_access", setting="community_outreach", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "33660168": dict(country_or_region="Jamaica", income_level="LMIC", target_population="underscreened_general", target_population_notes="Low socioeconomic communities; no Pap test in at least 3 years.", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="unk", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="pilot_intervention", self_sampling_confirmed="Y", n_invited="163", n_participated="156", uptake_pct="95.6", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y", key_barriers_facilitators="Community outreach workers; education and self-test intervention."),
    "41621746": dict(country_or_region="Ghana", income_level="LMIC", target_population="rural_low_access", target_population_notes="Low-resource country pilot in urban hospitals.", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="in_person", assay_type="DNA", triage_pathway="VIA", design="cross_sectional_pilot", self_sampling_confirmed="Y", n_invited="60", n_participated="60", uptake_pct="100.0", followup_reporting_level="referral_only", followup_closure_reported="Y", acceptability_reported="Y", followup_notes="Reports VIA confirmation after self-collection; no post-positive completion denominator."),
    "41095475": dict(country_or_region="United States", income_level="HIC", target_population="migrant_minority", target_population_notes="African American and African-born Black women.", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="unk", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "41048518": dict(country_or_region="India", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "40956285": dict(country_or_region="France", income_level="HIC", target_population="nonattenders", target_population_notes="No screening test recorded for more than 4 years and nonresponse to prior invitation.", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="unk", design="randomized_trial", self_sampling_confirmed="Y", n_invited="13061", n_participated="3075", uptake_pct="23.5", followup_reporting_level="none", followup_closure_reported="N"),
    "40952305": dict(country_or_region="Thailand", income_level="LMIC", target_population="underscreened_general", setting="organized_screening", delivery_model="mixed_or_multiarm", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="retrospective_registry", self_sampling_confirmed="Y", n_invited="11925", n_participated="5056", uptake_pct="42.4", followup_reporting_level="none", followup_closure_reported="N"),
    "40877387": dict(country_or_region="Ethiopia", income_level="LMIC", target_population="other", target_population_notes="Pregnant women historically excluded from screening in LMIC settings.", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="in_person", assay_type="DNA", triage_pathway="VIA", design="feasibility_study", self_sampling_confirmed="Y", n_invited="127", n_participated="117", uptake_pct="92.1", followup_reporting_level="completion_reported", followup_closure_reported="Y", followup_completion_pct="93.1", followup_notes="HPV-positive pregnant women were invited for triage/follow-up; abstract reports 27/29 attendance.", acceptability_reported="Y"),
    "40864371": dict(country_or_region="United States", income_level="HIC", target_population="migrant_minority", target_population_notes="Black women in community intervention-development setting.", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="unk", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="intervention_development", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "40846731": dict(country_or_region="Vietnam", income_level="LMIC", target_population="rural_low_access", setting="community", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "40844094": dict(country_or_region="India", income_level="LMIC", target_population="other", setting="community", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="proof_of_concept", self_sampling_confirmed="Y", n_invited="111", n_participated="111", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "40567147": dict(country_or_region="Japan", income_level="HIC", target_population="nonattenders", target_population_notes="Women not participating in the screening programme for 3 or more years.", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="cytology", design="secondary_RCT_analysis", self_sampling_confirmed="Y", n_invited="15107", followup_reporting_level="none", followup_closure_reported="N"),
    "40308366": dict(country_or_region="United States", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="acceptability_survey", self_sampling_confirmed="Y", n_invited="81", n_participated="81", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "39280202": dict(country_or_region="India", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="questionnaire_study", self_sampling_confirmed="Y", n_invited="210", n_participated="210", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "39036090": dict(country_or_region="Taiwan", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="1210", n_participated="1210", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "38978020": dict(country_or_region="Uganda", income_level="LMIC", target_population="other", target_population_notes="Women living with HIV and providers.", setting="clinic", delivery_model="unk", return_channel="unk", followup_support="peer_navigation", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="N", acceptability_reported="Y"),
    "38869176": dict(country_or_region="United States", income_level="HIC", target_population="other", setting="primary_care", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="survey", self_sampling_confirmed="Y", n_invited="351", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "38809639": dict(country_or_region="Japan", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="cytology", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="38", n_participated="38", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N"),
    "38678760": dict(country_or_region="Estonia", income_level="HIC", target_population="underscreened_general", setting="organized_screening", delivery_model="mixed_or_multiarm", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="program_description", self_sampling_confirmed="Y", uptake_pct="51.0", followup_reporting_level="none", followup_closure_reported="N"),
    "38648390": dict(country_or_region="Japan", income_level="HIC", target_population="nonattenders", target_population_notes="Women not participating in screening for at least 3 years.", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="cytology", design="randomized_trial", self_sampling_confirmed="Y", n_invited="15109", n_participated="1467", uptake_pct="20.0", followup_reporting_level="completion_reported", followup_closure_reported="Y", followup_completion_pct="46.8", followup_notes="Cytology triage compliance among HPV-positive women reported."),
    "38516651": dict(country_or_region="United States", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="47", n_participated="47", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N"),
    "38109300": dict(country_or_region="Kenya", income_level="LMIC", target_population="rural_low_access", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="cluster_RCT_workflow_study", self_sampling_confirmed="Y", uptake_pct="63.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y", key_barriers_facilitators="Video-assisted education in government-supported clinics; compared with standard health talks."),
    "38103276": dict(country_or_region="Netherlands", income_level="HIC", target_population="underscreened_general", setting="organized_screening", delivery_model="mixed_or_multiarm", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="unk", design="registry_cohort", self_sampling_confirmed="Y", uptake_pct="49.8", followup_reporting_level="none", followup_closure_reported="N"),
    "37964260": dict(country_or_region="Malaysia", income_level="LMIC", target_population="rural_low_access", setting="primary_care", delivery_model="mixed_or_multiarm", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="registry_analysis", self_sampling_confirmed="Y", n_invited="36738", n_participated="36738", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", equity_stratified_results_reported="Y"),
    "37692077": dict(country_or_region="Ghana", income_level="LMIC", target_population="other", target_population_notes="Catholic nuns, described as a group potentially missed by screening programmes.", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="outreach_event", followup_support="in_person", assay_type="DNA", triage_pathway="cytology", design="cross_sectional_cohort", self_sampling_confirmed="Y", n_invited="105", n_participated="105", uptake_pct="100.0", followup_reporting_level="referral_only", followup_closure_reported="Y", followup_notes="Screen-positive nuns underwent follow-up Pap smears and EVA colposcopy; no denominator for completion extracted from abstract."),
    "37289798": dict(country_or_region="Japan", income_level="HIC", target_population="nonattenders", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="cytology", design="RCT_companion_survey", self_sampling_confirmed="Y", n_invited="7340", n_participated="1196", uptake_pct="16.3", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "36635749": dict(country_or_region="Argentina", income_level="LMIC", target_population="rural_low_access", setting="community_outreach", delivery_model="chw_door_to_door", return_channel="chw", followup_support="chw_navigation", assay_type="DNA", triage_pathway="unk", design="implementation_fidelity", self_sampling_confirmed="Y", followup_reporting_level="referral_only", followup_closure_reported="Y", equity_stratified_results_reported="Y"),
    "36243709": dict(country_or_region="Nigeria", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="213", n_participated="213", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N"),
    "35078829": dict(country_or_region="South Africa", income_level="LMIC", target_population="rural_low_access", setting="school_community", delivery_model="outreach_event_distribution", return_channel="school_community", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="cross_sectional_trials", self_sampling_confirmed="Y", n_invited="5137", followup_reporting_level="none", followup_closure_reported="N", equity_stratified_results_reported="Y", acceptability_reported="Y"),
    "34972808": dict(country_or_region="United Kingdom", income_level="HIC", target_population="nonattenders", target_population_notes="Older lapsed attenders last screened 6-15 years before randomization.", setting="primary_care", delivery_model="mixed_or_multiarm", return_channel="clinic", followup_support="invitation", assay_type="DNA", triage_pathway="unk", design="randomized_trial", self_sampling_confirmed="Y", n_invited="784", n_participated="80", uptake_pct="20.4", followup_reporting_level="none", followup_closure_reported="N"),
    "34639688": dict(country_or_region="Germany", income_level="HIC", target_population="other", setting="colposcopy_clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="colposcopy", design="diagnostic_validation", self_sampling_confirmed="Y", followup_reporting_level="none", followup_closure_reported="N"),
    "34556128": dict(country_or_region="South Africa", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="527", n_participated="527", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N"),
    "34010238": dict(country_or_region="Sweden", income_level="HIC", target_population="underscreened_general", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="invitation", assay_type="DNA", triage_pathway="cytology", design="randomized_trial", self_sampling_confirmed="Y", n_invited="14765", n_participated="4946", uptake_pct="33.5", followup_reporting_level="referral_only", followup_closure_reported="Y"),
    "36304705": dict(country_or_region="Cameroon", income_level="LMIC", target_population="other", target_population_notes="Women living with HIV and HIV-negative women.", setting="community", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "32234028": dict(country_or_region="Tanzania", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="qualitative_pilot", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "30997147": dict(country_or_region="Malaysia", income_level="LMIC", target_population="underscreened_general", setting="primary_care", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="pilot", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "30541595": dict(country_or_region="Kenya", income_level="LMIC", target_population="other", target_population_notes="High-risk women in Mombasa.", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="cross_sectional_preference", self_sampling_confirmed="Y", n_invited="199", n_participated="199", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "30368651": dict(country_or_region="Kenya", income_level="LMIC", target_population="rural_low_access", setting="community_outreach", delivery_model="chw_door_to_door", return_channel="unk", followup_support="chw_navigation", assay_type="DNA", triage_pathway="unk", design="qualitative", self_sampling_confirmed="Y", acceptability_reported="Y"),
    "29912903": dict(country_or_region="Sweden", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="colposcopy", design="acceptability_study", self_sampling_confirmed="Y", n_invited="479", n_participated="479", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "29538411": dict(country_or_region="United States", income_level="HIC", target_population="migrant_minority", target_population_notes="Trans masculine patients, a low-screening underserved group.", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="150", n_participated="150", uptake_pct="100.0", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "29523108": dict(country_or_region="Denmark", income_level="HIC", target_population="nonattenders", setting="organized_screening", delivery_model="mail_to_home_return_mail", return_channel="mail", followup_support="reminders", assay_type="DNA", triage_pathway="cytology", design="randomized_trial", self_sampling_confirmed="Y", n_invited="9791", followup_reporting_level="none", followup_closure_reported="N"),
    "28950841": dict(country_or_region="Ghana", income_level="LMIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="diagnostic_validation", self_sampling_confirmed="Y", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "28422558": dict(country_or_region="United States", income_level="HIC", target_population="migrant_minority", target_population_notes="Transgender men, low screening uptake group.", setting="survey", delivery_model="unk", return_channel="unk", followup_support="unk", assay_type="DNA", triage_pathway="unk", design="survey", self_sampling_confirmed="Y", n_invited="91", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "26294825": dict(country_or_region="South Africa", income_level="LMIC", target_population="rural_low_access", setting="school_community", delivery_model="outreach_event_distribution", return_channel="school_community", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="implementation_project", self_sampling_confirmed="Y", n_invited="965", followup_reporting_level="none", followup_closure_reported="N"),
    "26242529": dict(country_or_region="South Africa", income_level="LMIC", target_population="rural_low_access", setting="school_community", delivery_model="outreach_event_distribution", return_channel="school_community", followup_support="education_navigation", assay_type="DNA", triage_pathway="unk", design="implementation_project", self_sampling_confirmed="Y", n_invited="1654", followup_reporting_level="none", followup_closure_reported="N"),
    "26031572": dict(country_or_region="Uganda", income_level="LMIC", target_population="rural_low_access", setting="community_outreach", delivery_model="outreach_event_distribution", return_channel="phone_clinic", followup_support="referral", assay_type="DNA", triage_pathway="VIA", design="randomized_trial", self_sampling_confirmed="Y", n_invited="500", n_participated="250", uptake_pct="99.6", followup_reporting_level="completion_reported", followup_closure_reported="Y", followup_notes="Reports referral and treatment rates in abstract.", acceptability_reported="Y"),
    "25730587": dict(country_or_region="Hong Kong", income_level="HIC", target_population="underscreened_general", setting="community_clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="cytology", design="crossover_randomized_trial", self_sampling_confirmed="Y", followup_reporting_level="none", followup_closure_reported="N", acceptability_reported="Y"),
    "24376516": dict(country_or_region="United States", income_level="HIC", target_population="other", setting="clinic", delivery_model="clinic_pickup_return_clinic", return_channel="clinic", followup_support="unk", assay_type="DNA", triage_pathway="cytology", design="diagnostic_validation", self_sampling_confirmed="Y", n_invited="198", n_participated="197", uptake_pct="99.5", followup_reporting_level="referral_only", followup_closure_reported="Y"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_pubmed() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for path in SEARCH_EXPORTS:
        if not path.exists():
            continue
        for row in read_tsv(path):
            pmid = row.get("pmid", "").strip()
            if pmid:
                out[pmid] = row
    return out


def default_study_row(pmid: str, meta: dict[str, str], chart: dict[str, str]) -> dict[str, str]:
    row = {f: "" for f in STUDY_FIELDS}
    row.update(
        {
            "record_id": f"PMID_{pmid}",
            "pmid": pmid,
            "doi": meta.get("doi", ""),
            "year": chart.get("year") or meta.get("year", ""),
            "title_short": meta.get("title", ""),
            "country_or_region": "UNK",
            "income_level": "UNK",
            "target_population": "other",
            "setting": "unk",
            "delivery_model": "unk",
            "return_channel": "unk",
            "followup_support": "unk",
            "self_sampling_confirmed": "Y",
            "assay_type": "DNA",
            "triage_pathway": "unk",
            "design": "observational",
            "followup_closure_reported": "N",
            "followup_reporting_level": "none",
            "equity_stratified_results_reported": "N",
            "acceptability_reported": "N",
            "cost_reported": "N",
            "limitations": "Added after final adjudication of high-risk false-negative records; charted from PubMed abstract-level information.",
        }
    )
    row.update(chart)
    if row["followup_reporting_level"] in {"referral_only", "completion_reported"}:
        row["followup_closure_reported"] = "Y"
    return row


def audit_row(pmid: str, study_row: dict[str, str], decision: str, reason: str) -> dict[str, str]:
    core_status = "candidate_core" if decision == "INCLUDE_CORE" else "candidate_non_core"
    manual_core = "CORE" if decision == "INCLUDE_CORE" else "NON_CORE"
    return {
        "pmid": pmid,
        "year": study_row.get("year", ""),
        "title_short": study_row.get("title_short", ""),
        "current_design": study_row.get("design", ""),
        "current_target_population": study_row.get("target_population", ""),
        "current_delivery_model": study_row.get("delivery_model", ""),
        "current_followup_reporting_level": study_row.get("followup_reporting_level", ""),
        "current_followup_completion_pct": study_row.get("followup_completion_pct", ""),
        "n_invited": study_row.get("n_invited", ""),
        "n_participated": study_row.get("n_participated", ""),
        "uptake_pct": study_row.get("uptake_pct", ""),
        "acceptability_reported": study_row.get("acceptability_reported", ""),
        "cost_reported": study_row.get("cost_reported", ""),
        "candidate_core_status": core_status,
        "candidate_reason": "Final 58-record adjudication",
        "manual_reviewer_decision": "",
        "manual_reviewer_notes": "",
        "manual_core_decision": manual_core,
        "manual_decision_reason": reason,
        "manual_evidence_text": "Final adjudication based on PubMed abstract evidence and independent review worksheet.",
        "manual_followup_level_if_changed": "",
        "manual_followup_pct_if_changed": "",
        "manual_notes": "Added after final 58-record adjudication; not part of the earlier broad map.",
        "reviewer_initials": "COD+HR",
        "review_date": "2026-06-13",
    }


def main() -> int:
    worksheet = read_tsv(WORKSHEET)
    pubmed = load_pubmed()
    include_rows = [r for r in worksheet if r["adjudicator_decision"] in {"INCLUDE_CORE", "INCLUDE_BROAD_NONCORE"}]
    include_pmids = {r["pmid"] for r in include_rows}
    if len(include_rows) != 50:
        raise SystemExit(f"Expected 50 include rows, found {len(include_rows)}")
    missing_chart = sorted(include_pmids - set(CHARTING))
    if missing_chart:
        raise SystemExit(f"Missing charting entries for: {missing_chart}")

    study = read_tsv(STUDY_INDEX)
    exclusions = read_tsv(EXCLUSIONS)
    audit = read_tsv(AUDIT)

    study = [r for r in study if r.get("pmid", "") not in include_pmids]
    exclusions = [r for r in exclusions if r.get("record_id", "").replace("PMID_", "") not in include_pmids]
    audit = [r for r in audit if r.get("pmid", "") not in include_pmids]

    worksheet_by_pmid = {r["pmid"]: r for r in include_rows}
    new_study: list[dict[str, str]] = []
    new_audit: list[dict[str, str]] = []
    for pmid in sorted(include_pmids, key=lambda p: (CHARTING[p].get("year", pubmed.get(p, {}).get("year", "")), p), reverse=True):
        meta = pubmed.get(pmid, {})
        chart = dict(CHARTING[pmid])
        row = default_study_row(pmid, meta, chart)
        if not row["title_short"]:
            row["title_short"] = worksheet_by_pmid[pmid].get("title", "")
        new_study.append(row)
        new_audit.append(audit_row(pmid, row, worksheet_by_pmid[pmid]["adjudicator_decision"], worksheet_by_pmid[pmid]["adjudicator_reason"]))

    all_study = study + new_study
    all_audit = audit + new_audit
    all_study.sort(key=lambda r: (-int(r.get("year") or 0), r.get("pmid", "")), reverse=False)
    all_audit.sort(key=lambda r: (-int(r.get("year") or 0), r.get("pmid", "")), reverse=False)

    write_tsv(STUDY_INDEX, all_study, STUDY_FIELDS)
    write_tsv(EXCLUSIONS, exclusions, ["record_id", "stage", "reason_code", "reason_notes", "source", "url"])
    write_tsv(AUDIT, all_audit, AUDIT_FIELDS)

    n_core = sum(1 for r in include_rows if r["adjudicator_decision"] == "INCLUDE_CORE")
    n_noncore = sum(1 for r in include_rows if r["adjudicator_decision"] == "INCLUDE_BROAD_NONCORE")
    print(f"Added to broad map: {len(include_rows)} records ({n_core} core, {n_noncore} broad non-core)")
    print(f"Updated {STUDY_INDEX}: {len(all_study)} records")
    print(f"Updated {EXCLUSIONS}: {len(exclusions)} records")
    print(f"Updated {AUDIT}: {len(all_audit)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
