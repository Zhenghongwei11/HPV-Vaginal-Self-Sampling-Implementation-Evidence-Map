#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SeedRecord:
    pmid: str
    title: str
    year: int
    abstract: str


def _infer_country(title: str, abstract: str) -> str:
    text = f"{title}\n{abstract}".lower()
    # Minimal, high-precision heuristics (prefer false-unknown over false-positive).
    if "sloven" in text:
        return "Slovenia"
    if "estonia" in text:
        return "Estonia"
    if "dutch" in text or "netherlands" in text:
        return "Netherlands"
    if "ontario" in text or "canada" in text:
        return "Canada"
    if "south florida" in text or "u.s." in text or "united states" in text:
        return "United States"
    if "australia" in text:
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
    # Coarse World Bank-style buckets (sufficient for mapping; can be refined later).
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
    if "indigenous" in text or "first nations" in text or "māori" in text or "maori" in text or "pacific" in text:
        return ("other", "Indigenous/minority focus")
    return ("other", "Underscreened focus implied but not explicitly codable")


def _setting_and_delivery(title: str, abstract: str) -> tuple[str, str, str]:
    text = f"{title}\n{abstract}".lower()
    if (
        "mailed" in text
        or "mailing" in text
        or "mail-to-home" in text
        or "home-based" in text
        or "postal" in text
        or "pre-paid envelope" in text
        or "prepaid envelope" in text
    ):
        return ("home_mail", "mail_to_home_return_mail", "mail")
    if ("at home" in text or "home" in text) and ("kit" in text or "self-sampl" in text):
        return ("home_mail", "unk", "unk")
    if "community" in text or "outreach" in text:
        return ("community_outreach", "outreach_event_distribution", "mixed")
    return ("other", "unk", "unk")


def _followup_support(abstract: str) -> str:
    text = abstract.lower()
    if "reminder" in text or "phone call" in text or "letter" in text:
        return "reminders"
    if "navigator" in text or "navigation" in text:
        return "navigation"
    return "unk"


def _design(title: str, abstract: str) -> str:
    text = f"{title}\n{abstract}".lower()
    if "cluster" in text and "random" in text:
        return "cluster_RCT"
    if "random" in text or "randomised" in text or "randomized" in text:
        return "individual_RCT"
    if "mixed-method" in text or "mixed methods" in text:
        return "observational"
    if "questionnaire" in text or "survey" in text:
        return "observational"
    return "other"


def _assay_type(abstract: str) -> str:
    text = abstract.lower()
    if "mrna" in text:
        return "mRNA"
    if "hybrid capture" in text or "hpv dna" in text or "hrhpv" in text or "high-risk hpv" in text:
        return "DNA"
    return "UNK"


def _triage_pathway(abstract: str) -> str:
    text = abstract.lower()
    if "colposcopy" in text:
        return "direct_colposcopy"
    if "cytolog" in text or "pap" in text:
        return "cytology"
    return "unk"


def main() -> int:
    out_study_index = Path("results/map/study_index.tsv")
    out_exclusions = Path("results/screening/exclusion_reasons.tsv")
    out_study_index.parent.mkdir(parents=True, exist_ok=True)
    out_exclusions.parent.mkdir(parents=True, exist_ok=True)

    # Seed set from MCP (PubMed). This is a starting point; expand via additional searches later.
    included = [
        SeedRecord(
            pmid="30216191",
            year=2018,
            title="Randomised trial of HPV self-sampling among non-attenders in the Slovenian cervical screening programme ZORA: comparing three different screening approaches.",
            abstract="Background To overcome obstacles within the Slovenian organised cervical cancer screening programme, a randomised pilot study of human papillomavirus (HPV) self-sampling among non-attenders was performed, aiming to assess three different screening approaches. Participants and methods Non-attenders aged 30-64 years from two Slovenian regions were randomised to two HPV self-sampling groups-the opt-in (I1, n = 14.400) and the opt-out (I2, n = 9.556), with a control group (P, n = 2.600). Self-collected samples were analysed using the Hybrid Capture 2 assay. HPV-positive women were invited to a colposcopy. The overall and type-specific intention-to-screen response rates and histological outcomes with a positive predictive value (PPV) according to the women's age, the screening approach, the level of protection resulting from previous screening history, and the region of residence were assessed. Results Of the 26.556 women enrolled, 8.972 (33.8%) responded with self-sample for HPV testing and/or traditional cytology within one year of enrolment. Response rates were 37.7%, 34.0% and 18.4% (p < 0.050) for opt-out, opt-in and control groups. Cervical intraepithelial neoplasia (CIN)2+ was diagnosed in 3.9/1.000, 3.4/1.000, and 3.1/1.000 women (p > 0.050), respectively. PPV of the HPV self-sampling was 12.0% and 9.6% for CIN2+ and CIN3+. The highest PPV was obtained in non-attenders in screening programme for more than 10-years and concordant results of HPV testing with 40.8% for CIN2+ and 38.8% for CIN3+. Conclusions The results of our study show that a high response to HPV self-sampling can be achieved also in an opt-in approach, if women are encouraged to choose between self-sampling at home and screening with gynaecologist. In addition, clinically important risk difference for a high-grade cervical lesion exists in the case of a positive result of HPV testing on self-collected samples, depending on the length of the interval since last screening. Stratified management of these women should be strongly considered. Women who were not screened with cytology for at least 10 years should be referred to immediate colposcopy for histology verification instead to delayed re-testing.",
        ),
        SeedRecord(
            pmid="40726443",
            year=2025,
            title="Targeting under-screened women in cervical cancer: combining self-sampling and human papillomavirus testing with a strategic reminder plan.",
            abstract="Cervical cancer (CC) screening is essential for reducing its incidence, yet engaging under-screened women remains challenging. Self-sampling has emerged as a promising solution to enhance attendance; however, its integration into programmes has proven difficult. This study evaluated a multimodal approach combining self-sampling, human papillomavirus (HPV) testing, and personalized contact to reach women not attending conventional CC screening. To achieve this, 801 women aged 30-59 who had not participated in Portugal's Central Region CC screening programme for more than 4 years were selected based on specific criteria. Of these, 114 women were excluded for not meeting eligibility criteria, resulting in 687 eligible participants. Using an 'opt-in' approach, women who consented to participate received cervicovaginal self-sampling kits at home. Multiple contact strategies, including phone calls and reminder letters, were employed to encourage participation. Women testing positive for high-risk HPV (hr-HPV) were referred for gynaecological follow-up. Of the eligible women, 307 (44.7%) consented to participate and 198 (28.8%) provided valid samples for hr-HPV testing. Approximately 60.0% of participants were enrolled after the first reminder phone call, while additional contact strategies accounted for one-third of submitted samples. Among 12 hr-HPV positive cases, 11 completed gynaecological follow-up, resulting in the identification of six cervical lesions.",
        ),
        SeedRecord(
            pmid="29995217",
            year=2018,
            title="A randomized trial of mailed HPV self-sampling for cervical cancer screening among ethnic minority women in South Florida.",
            abstract="HPV self-sampling has previously been shown to increase cervical cancer screening among ethnic minority and immigrant women. We conducted a randomized pragmatic trial to examine the effectiveness of HPV self-sampling delivered via in-person versus by US mail for medically underserved Hispanic, Haitian, and non-Hispanic Black women living in South Florida.",
        ),
        SeedRecord(
            pmid="34694179",
            year=2022,
            title="Human papillomavirus self-sampling for long-term non-attenders in cervical cancer screening: A randomised feasibility study in Estonia.",
            abstract="Organised cervical cancer screening was started in Estonia in 2006, but participation is still low. Human papillomavirus (HPV) self-sampling has proved to increase screening uptake. This study addressed the feasibility of HPV self-sampling and the acceptance of this method among long-term screening non-attenders.",
        ),
        SeedRecord(
            pmid="24736093",
            year=2014,
            title="Reasons for non-attendance to cervical screening and preferences for HPV self-sampling in Dutch women.",
            abstract="High attendance rates in cervical screening are essential for effective cancer prevention. Offering HPV self-sampling to non-responders increases participation rates. The objectives of this study were to determine why non-responders do not attend regular screening, and why they do or do not participate when offered a self-sampling device.",
        ),
        SeedRecord(
            pmid="35313763",
            year=2022,
            title="HPV self-sampling and follow-up over two rounds of cervical screening in Australia - the iPap trial.",
            abstract="Previously, based on 6 months of follow-up, we showed that HPV self-sampling improved participation in cervical screening compared to a reminder letter for Pap testing for never- and under-screened women. Here, we report follow-up and related screening outcomes for women who participated in the initial self-sampling over two screening rounds.",
        ),
        SeedRecord(
            pmid="26850941",
            year=2016,
            title="Home-based HPV self-sampling improves participation by never-screened and under-screened women: Results from a large randomized trial (iPap) in Australia.",
            abstract="We conducted a randomized controlled trial to determine whether HPV self-sampling increases participation in cervical screening by never- and under-screened (not screened in past 5 years) women when compared with a reminder letter for a Pap test. Never- or under-screened Victorian women aged 30-69 years, not pregnant and with no prior hysterectomy were eligible. Within each stratum (never-screened and under-screened), we randomly allocated 7,140 women to self-sampling and 1,020 to Pap test reminders. The self-sampling kit comprised a nylon tipped flocked swab enclosed in a dry plastic tube. The primary outcome was participation, as indicated by returning a swab or undergoing a Pap test; the secondary outcome, for women in the self-sampling arm with a positive HPV test, was undergoing appropriate clinical investigation. The Roche Cobas® 4800 test was used to measure presence of HPV DNA. Participation was higher for the self-sampling arm: 20.3 versus 6.0% for never-screened women (absolute difference 14.4%, 95% CI: 12.6-16.1%, p < 0.001) and 11.5 versus 6.4% for under-screened women (difference 5.1%, 95% CI: 3.4-6.8%, p < 0.001). Of the 1,649 women who returned a swab, 45 (2.7%) were positive for HPV16/18 and 95 (5.8%) were positive for other high-risk HPV types. Within 6 months, 28 (62.2%) women positive for HPV16/18 had colposcopy as recommended and nine (20%) had cytology only. Of women positive for other high-risk HPV types, 78 (82.1%) had a Pap test as recommended. HPV self-sampling improves participation in cervical screening for never- and under-screened women and most women with HPV detected have appropriate clinical investigation.",
        ),
        SeedRecord(
            pmid="34590066",
            year=2021,
            title="Acceptability of human papillomavirus (HPV) self-sampling among never- and under-screened Indigenous and other minority women: a randomised three-arm community trial in Aotearoa New Zealand.",
            abstract="Internationally, self-sampling for human papillomavirus (HPV) has been shown to increase participation in cervical-cancer screening. In Aotearoa New Zealand, there are long-standing ethnic inequalities in cervical-cancer screening, incidence, and mortality, particularly for indigenous Māori women, as well as Pacific and Asian women.",
        ),
        SeedRecord(
            pmid="40359821",
            year=2025,
            title="Women's perceptions and preferences toward HPV self-sampling in France: A questionnaire within the French CapU4 Trial.",
            abstract="Despite organised screening efforts since 2018 targeting under-screened women, cervical cancer (CC) screening coverage remains moderate (60%) in France. The target age for HPV-based screening is women aged 30-65. Vaginal self-sampling (VSS) has recently been introduced for women who have not been screened. This study assesses women's perceptions and preferences toward HPV self-sampling among women enrolled in the CapU4 trial.",
        ),
        SeedRecord(
            pmid="41267012",
            year=2025,
            title="Moroccan and Pakistani women's knowledge and perceptions on cervical cancer screening and HPV self-sampling acceptability in Catalonia, Spain: a mixed-methods study.",
            abstract="Disparities in cervical cancer (CC) screening participation persist, with lower rates among immigrant women from low-resource countries compared to native European women. Evidence-based strategies to reach under-screened women are thus needed, such as adopting self-sampling for human papillomavirus (HPV) testing. Studies have demonstrated that women are receptive to HPV self-sampling. However, results may not be generalizable to all ethnic groups and settings. This is the first study in Spain assessing HPV self-sampling acceptability among immigrant populations. A mixed-methods study was used to explore knowledge and perceptions of CC screening and attitudes towards HPV self-sampling among Moroccan and Pakistani women in Catalonia.",
        ),
        SeedRecord(
            pmid="27855089",
            year=2016,
            title="Community-randomised controlled trial embedded in the Anishinaabek Cervical Cancer Screening Study: human papillomavirus self-sampling versus Papanicolaou cytology.",
            abstract="The incidence of cervical cancer is up to 20-fold higher among First Nations women in Canada than the general population, probably due to lower participation in screening. Offering human papillomavirus (HPV) self-sampling in place of Papanicolaou (Pap) testing may eventually increase screening participation and reduce cervical cancer rates in this population.",
        ),
        SeedRecord(
            pmid="26598955",
            year=2016,
            title="Randomized Intervention of Self-Collected Sampling for Human Papillomavirus Testing in Under-Screened Rural Women: Uptake of Screening and Acceptability.",
            abstract="Our aim was to determine if cervical cancer screening uptake would increase among under-screened women living in rural Ontario, Canada, if at-home self-collected sampling for human papillomavirus (HPV) testing was offered as a primary cervical cancer screening modality, compared to invited papanicolaou (Pap) testing or routine opportunistic screening.",
        ),
    ]

    excluded = [
        ("29113956", "title_abstract", "PROTOCOL_NO_OUTCOMES", "Rationale/design paper; no implementation outcome data in abstract."),
        ("24646201", "title_abstract", "PROTOCOL_NO_OUTCOMES", "Rationale/design paper; no implementation outcome data in abstract."),
        ("31815615", "title_abstract", "PROTOCOL_NO_OUTCOMES", "Protocol paper; no implementation outcome data in abstract."),
        ("28086983", "title_abstract", "PROTOCOL_NO_OUTCOMES", "Protocol paper; no implementation outcome data in abstract."),
        ("25056208", "title_abstract", "PROTOCOL_NO_OUTCOMES", "Protocol paper; no implementation outcome data in abstract."),
    ]

    study_header = [
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

    rows = []
    for r in included:
        country = _infer_country(r.title, r.abstract)
        income = _income_level(country)
        target_pop, target_notes = _target_population(r.title, r.abstract)
        setting, delivery_model, return_channel = _setting_and_delivery(r.title, r.abstract)
        followup_support = _followup_support(r.abstract)
        assay = _assay_type(r.abstract)
        triage = _triage_pathway(r.abstract)
        design = _design(r.title, r.abstract)

        n_invited = ""
        n_participated = ""
        uptake_pct = ""
        followup_closure_reported = "N"
        followup_reporting_level = "none"
        followup_completion_pct = ""
        followup_notes = ""
        equity_reported = "N"
        acceptability_reported = "N"
        cost_reported = "N"

        if r.pmid == "30216191":
            n_invited = "26556"
            n_participated = "8972"
            uptake_pct = "33.8"
            followup_closure_reported = "Y"  # invited to colposcopy; completion not stated in abstract
            followup_reporting_level = "referral_only"
            followup_notes = "HPV-positive invited to colposcopy; completion not reported in abstract"
        if r.pmid == "40726443":
            n_invited = "687"
            n_participated = "198"
            uptake_pct = "28.8"
            followup_closure_reported = "Y"
            followup_reporting_level = "completion_reported"
            followup_completion_pct = "91.7"  # 11/12
            followup_notes = "HPV-positive referred for gynecological follow-up; 11/12 completed"
            acceptability_reported = "N"
        if r.pmid == "26850941":
            followup_closure_reported = "Y"
            followup_reporting_level = "completion_reported"
            followup_notes = (
                "Participation reported by stratum (never-screened vs underscreened); "
                "HPV-positive follow-up reported (HPV16/18 colposcopy 62.2%; other hrHPV cytology 82.1%)"
            )
        if r.pmid in {"34694179", "24736093", "40359821", "41267012", "34590066"}:
            acceptability_reported = "Y"

        rows.append(
            {
                "record_id": f"PMID_{r.pmid}",
                "pmid": r.pmid,
                "doi": "",
                "year": str(r.year),
                "title_short": (r.title[:117] + "...") if len(r.title) > 120 else r.title,
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
                "followup_notes": followup_notes,
                "equity_stratified_results_reported": equity_reported,
                "acceptability_reported": acceptability_reported,
                "cost_reported": cost_reported,
                "key_barriers_facilitators": "",
                "limitations": "Seed charting from abstract-level info; fields may be incomplete.",
            }
        )

    out_study_index.write_text("", encoding="utf-8")
    with out_study_index.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=study_header, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow(row)

    excl_header = ["record_id", "stage", "reason_code", "reason_notes", "source", "url"]
    with out_exclusions.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=excl_header, delimiter="\t")
        w.writeheader()
        for pmid, stage, code, note in excluded:
            w.writerow(
                {
                    "record_id": f"PMID_{pmid}",
                    "stage": stage,
                    "reason_code": code,
                    "reason_notes": note,
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )

    print(f"Wrote: {out_study_index} (n={len(rows)})")
    print(f"Wrote: {out_exclusions} (n={len(excluded)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
