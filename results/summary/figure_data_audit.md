# Figure/Data Consistency Audit

- Included records (unique record_id in study_index): **530**
- Overview.tsv included_total: **530**
- Overview.tsv records screened (dedup): **1716**; identified: **2133**; excluded: **1186**

## Figure 2 (delivery model × target population)
- Matrix exported: `results/summary/figure_matrices/Figure2_delivery_model_by_target_population.tsv`
- Delivery-model column sums (should match Table 1 totals):
  - Unclear at record level: 174
  - Clinic/primary care: 145
  - Outreach-event distribution: 103
  - Mail-to-home: 85
  - Community health worker delivery: 15
  - Mixed/multi-arm: 5
  - home_mail: 3
- Target-population row sums (should match Table 1 totals):
  - Other/unclear: 259
  - Underscreened general: 112
  - Non-attenders: 65
  - Migrant/minority: 44
  - Never screened: 27
  - Rural/low access: 23

## Figure 3 (follow-up reporting level × delivery model)
- Matrix exported: `results/summary/figure_matrices/Figure3_followup_reporting_by_delivery_model.tsv`
- Follow-up reporting-level totals:
  - No follow-up reported: 279
  - Referral without completion metrics: 209
  - Completion reported: 42
- Figure 3 consistency (current matrix vs `results/summary/followup_closure_by_delivery_model.tsv`): **PASS**
