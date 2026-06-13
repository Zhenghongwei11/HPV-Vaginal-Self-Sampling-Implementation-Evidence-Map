# Search Strategy (HPV Vaginal Self-Sampling Implementation; Underscreened Populations)

## Databases
- PubMed (primary)
- Optional: OpenAlex, Semantic Scholar (supplementary coverage)

## Date Window
- Start: database inception (no start-date restriction applied)
- End: run date (recorded in search log)

## PubMed Query Blocks (copy/paste)

Notes:
- This is a **scoping** search: run iteratively and stop when new queries add few/no new eligible studies.
- The evidence map run reported in this evidence map used **Query 01** and **Query 02** (see the run log). The additional query blocks below are provided as optional extensions when coverage is incomplete.
- Recommended export format for reproducibility: PubMed UI → **Send to → File → Format: PubMed (.nbib)**.
- Optional efficiency filters:
  - Add `NOT urine[Title/Abstract]` to reduce urine self-sampling noise (we exclude urine anyway).
  - If a query becomes too narrow, remove the underscreened block and filter at screening.

### Query 01 (coverage-first; underscreened focus)
```text
((human papillomavirus OR HPV) AND (self-sampling OR self sampling OR self-collected OR self collected OR home-based OR mail OR postal))
AND (cervical cancer screening OR cervical screening)
AND (underscreened OR "under-screened" OR nonattender* OR "non-attender*" OR "never screened" OR "never-screened" OR "hard to reach" OR outreach OR rural OR migrant)
```

### Query 02 (implementation/outcomes-first)
```text
((human papillomavirus OR HPV) AND (self-sampling OR self sampling OR self-collected OR home-based OR mail OR postal OR outreach OR community health worker))
AND (cervical screening)
AND (uptake OR participation OR acceptability OR feasibility OR implementation OR adherence OR follow-up OR navigation OR reminder OR equity OR cost)
```

### Query 03 (nonattenders; direct-mail vs opt-in/opt-out)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (nonattend* OR "non-attend*" OR nonrespon* OR "non-respon*" OR "second reminder" OR "reminder letter")
AND (direct-mail OR "direct mail" OR send-to-all OR "send to all" OR opt-in OR "opt in" OR opt-out OR "opt out" OR "mail to home" OR mailed OR postal)
NOT urine[Title/Abstract]
```

### Query 04 (program rollout / real-world / pragmatic implementation)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (implementation OR feasibility OR pragmatic OR "real-world" OR rollout OR "scale-up" OR "scale up" OR pilot OR "program evaluation" OR "service evaluation")
AND (underscreened OR "under-screened" OR nonattend* OR "never screened" OR overdue OR "long-term nonattend*" OR "long term nonattend*")
NOT urine[Title/Abstract]
```

### Query 05 (follow-up adherence / triage / referral pathway; “闭环”)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (follow-up OR "follow up" OR adherence OR compliance OR "loss to follow-up" OR "lost to follow-up" OR triage OR referral OR colposcopy)
AND (underscreened OR "under-screened" OR nonattend* OR "never screened" OR overdue)
NOT urine[Title/Abstract]
```

### Query 06 (navigation / reminders / outreach support)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (navigator OR navigation OR reminder* OR SMS OR text-message* OR phone-call* OR "telephone" OR outreach OR "patient navigation")
AND (underscreened OR "under-screened" OR nonattend* OR "never screened" OR overdue OR underserved)
NOT urine[Title/Abstract]
```

### Query 07 (community health workers / door-to-door / community distribution)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND ("community health worker" OR CHW OR "door-to-door" OR "door to door" OR community-based OR "community based" OR "community outreach")
AND (underscreened OR "under-screened" OR "hard to reach" OR underserved OR "low access" OR rural OR remote)
NOT urine[Title/Abstract]
```

### Query 08 (pharmacy / primary care opportunistic offer / clinic pick-up)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (pharmacy OR pharmacist OR "primary care" OR "general practice" OR GP OR clinic OR opportunistic)
AND (underscreened OR "under-screened" OR nonattend* OR overdue OR underserved)
NOT urine[Title/Abstract]
```

### Query 09 (equity-focused populations: migrant/minority/Indigenous; access barriers)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (migrant* OR immigrant* OR minority OR ethnic* OR Indigenous OR Maori OR "First Nations" OR "low income" OR deprivation OR uninsured OR "hard to reach" OR underserved)
NOT urine[Title/Abstract]
```

### Query 10 (acceptability / preferences / qualitative implementation insights)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (acceptab* OR preference* OR experience* OR perception* OR interview* OR questionnaire* OR survey OR qualitative OR "mixed methods")
AND (underscreened OR "under-screened" OR nonattend* OR overdue OR underserved)
NOT urine[Title/Abstract]
```

### Query 11 (cost / resource use / economic evaluation)
```text
((human papillomavirus OR HPV) AND (self-sampl* OR self-collect* OR "self collected" OR "self-collected"))
AND (cervical screening OR "cervical cancer screening")
AND (cost OR economic OR "cost-effect*" OR "cost util*" OR "budget impact" OR "resource use")
AND (underscreened OR "under-screened" OR nonattend* OR overdue OR underserved)
NOT urine[Title/Abstract]
```

## PRESS-style Self-check (lightweight)
- Sensitivity: does the query retrieve at least 5 known self-sampling implementation papers?
- Specificity: if results are dominated by lab/assay-only studies, add a delivery/uptake term block.
- Population focus: ensure “underscreened/nonattender” block is present; if too restrictive, broaden to “low access” terms and filter at screening.

## Documentation Requirements
- Record run date/time, query string, and returned count.
- Save record exports in a stable table for screening.
