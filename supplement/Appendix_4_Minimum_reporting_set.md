# Self-Sampling Implementation Cascade: Minimum Reporting Set (Draft)

This project treats “落地” as an **end-to-end implementation cascade** rather than a single uptake metric.
The minimum reporting set below is designed for **HPV vaginal self-sampling** among **underscreened** populations and is feasible under an **OA / abstract-sufficient** policy.

## 1) Minimum Reporting Set (what every implementation study should report)
### A. Reach / offer (denominator)
- Eligible/targeted population definition (e.g., nonattender ≥ X years; overdue ≥ X years; never-screened).
- **N invited/approached/offered** (or a clearly defined eligible denominator).

### B. Uptake (screening participation)
- **N participated** (kit accepted, kit returned, or sample collected—define which).
- Participation/uptake (%) with denominator specified.
- Delivery model details: how the kit is distributed and returned (mail/clinic/outreach/CHW/pharmacy; return channel).

### C. Test result flow (screening outcome)
- HPV assay type (DNA/mRNA) and high-level positivity reporting (at least whether positivity was measured and acted upon).

### D. Triage / referral step
- Triage/referral pathway for HPV-positive participants (e.g., cytology, genotyping, direct colposcopy).
- Whether a follow-up invitation/referral was issued (and how).

### E. Follow-up completion (the “闭环” outcome)
- **Follow-up completion / attendance** among HPV-positive participants (numerator/denominator or %).
- Time window for completion (if available) and handling of loss to follow-up.
- Any support components enabling completion (reminders, navigation, incentives).

### F. Equity & implementation context (minimal)
- At least one equity-stratified uptake/follow-up comparison OR a clear description of priority populations (migrant/minority/low access).
- Setting and health-system context (primary care vs outreach vs home-based).
- Resource/cost signal (even a brief statement) when available.

## 2) How this maps to our charting schema (`results/map/study_index.tsv`)
The minimum set aligns to existing fields:
- Population: `target_population`, `target_population_notes`
- Reach: `n_invited` (if known)
- Uptake: `n_participated`, `uptake_pct`
- Delivery: `setting`, `delivery_model`, `return_channel`
- Test: `assay_type`
- Triage/referral: `triage_pathway`
- Follow-up support: `followup_support`
- Follow-up closure reporting:
  - `followup_reporting_level` (`none` / `referral_only` / `completion_reported`)
  - `followup_completion_pct` (if reported)
- Equity/cost signals: `equity_stratified_results_reported`, `cost_reported`

## 3) Synthesis principle (what we do in IJWH without meta-analysis)
- Do **not** pool effect sizes.
- Instead, report:
  - distribution of delivery models across target populations,
  - the proportion of studies reaching each cascade step (especially completion),
  - where evidence is thin (cells/gaps) and which reporting elements are most frequently missing.

