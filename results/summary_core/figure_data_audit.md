# Figure/Data Consistency Audit

- Included records (unique record_id in study_index): **389**
- Overview.tsv included_total: **389**
- Overview.tsv records screened (dedup): **1716**; identified: **2133**; excluded: **1186**

## Figure 2 (delivery model × target population)
- Matrix exported: `results/summary_core/figure_matrices/Figure2_delivery_model_by_target_population.tsv`
- Delivery-model column sums (should match Table 1 totals):
  - Unclear at record level: 126
  - Clinic/primary care: 97
  - Outreach-event distribution: 86
  - Mail-to-home: 63
  - Community health worker delivery: 11
  - home_mail: 3
  - Mixed/multi-arm: 3
- Target-population row sums (should match Table 1 totals):
  - Other/unclear: 186
  - Underscreened general: 82
  - Non-attenders: 59
  - Migrant/minority: 24
  - Never screened: 20
  - Rural/low access: 18

## Figure 3 (follow-up reporting level × delivery model)
- Matrix exported: `results/summary_core/figure_matrices/Figure3_followup_reporting_by_delivery_model.tsv`
- Follow-up reporting-level totals:
  - Referral without completion metrics: 208
  - No follow-up reported: 139
  - Completion reported: 42
- Figure 3 consistency (current matrix vs `results/summary_core/followup_closure_by_delivery_model.tsv`): **PASS**
