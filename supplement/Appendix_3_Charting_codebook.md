# Charting Codebook (Study Index + Evidence Map)

This codebook defines how to chart included studies into `results/map/study_index.tsv` and how to derive `results/map/evidence_map_counts.tsv`.

## 1) Stable Identifiers
- Prefer PMID; else DOI; else stable URL + internal `record_id`.

## 2) Required Fields (study_index.tsv)
### Bibliographic
- `record_id`: PMID_<pmid> or DOI_<doi> (lowercase DOI; no spaces)
- `pmid`: optional
- `doi`: optional
- `year`
- `title_short` (<=120 chars; for human readability)

### Geography / resource context
- `country_or_region`
- `income_level`: World Bank (HIC/UMIC/LMIC/LIC) if inferable; else `UNK`

### Population & setting
- `target_population`: controlled vocabulary:
  - `underscreened_general`
  - `nonattenders`
  - `never_screened`
  - `rural_low_access`
  - `migrant_minority`
  - `other` (specify in `target_population_notes`)
- `target_population_notes` (free text)
- `setting`: controlled vocabulary:
  - `home_mail`
  - `community_outreach`
  - `primary_care`
  - `pharmacy`
  - `workplace_school`
  - `other`

### Implementation model (core)
- `delivery_model`: controlled vocabulary:
  - `mail_to_home_return_mail`
  - `mail_to_home_return_dropoff`
  - `clinic_pickup_return_clinic`
  - `chw_door_to_door`
  - `outreach_event_distribution`
  - `pharmacy_distribution`
  - `mixed_or_multiarm`
  - `other`
- `return_channel`: `mail` | `dropoff` | `in_person` | `mixed` | `unk`
- `followup_support`: `none_reported` | `navigation` | `reminders` | `incentives` | `mixed` | `unk`

### Test / pathway (high-level only)
- `self_sampling_confirmed`: `Y`/`N` (must be `Y` for inclusion; vaginal self-collection)
- `assay_type`: `DNA` | `mRNA` | `UNK`
- `triage_pathway`: `cytology` | `genotyping` | `p16_k i67` | `methylation` | `direct_colposcopy` | `other` | `unk`

### Study design and scale
- `design`: `individual_RCT` | `cluster_RCT` | `pragmatic_trial` | `implementation_study` | `program_evaluation` | `observational` | `other`
- `n_invited` (integer or blank)
- `n_participated` (integer or blank)
- `uptake_pct` (0–100; blank if not computable)

### Follow-up closure (the “落地闭环” anchor)
- `followup_reporting_level`: `none` | `referral_only` | `completion_reported`
- `followup_closure_reported`: `Y`/`N` (derived convenience flag; `Y` if `followup_reporting_level != none`)
- `followup_completion_pct`: blank if not available
- `followup_notes` (free text)

### Equity / acceptability / costs (do not force numbers)
- `equity_stratified_results_reported`: `Y`/`N`
- `acceptability_reported`: `Y`/`N`
- `cost_reported`: `Y`/`N`

### Notes
- `key_barriers_facilitators` (short code list or 1–2 sentences)
- `limitations` (1–2 sentences)

## 3) Derivation: evidence_map_counts.tsv
Each row is a cell count with fields:
- `target_population`
- `delivery_model`
- `setting`
- `income_level`
- `followup_reporting_level` (`none`/`referral_only`/`completion_reported`)
- `n_studies`

## 4) Decision Rules (important)
- If delivery involves multiple arms, set `delivery_model=mixed_or_multiarm` and specify arms in notes; counts treat the study as one unit unless arms are separable in charting.
- If uptake is only reported as “returned kits” without invited denominator, fill `n_participated` and leave `uptake_pct` blank; still include the study.
- Do not infer triage pathway beyond what is stated in abstract/OA.
