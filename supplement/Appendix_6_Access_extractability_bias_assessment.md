# Appendix 6. Access and information-bias assessment

## Purpose

This appendix addresses the concern that an abstract/open-access-constrained charting strategy may introduce selection and information bias. The analysis is based on the frozen charting outputs used for the frozen evidence map:

- Dataset S1: `supplement/Dataset_S1_Charted_study_index.tsv`
- Dataset S2: `supplement/Dataset_S2_Exclusion_log.tsv`
- Overall cascade summary: `supplement/Table_S3a_Cascade_reporting_overall.tsv`
- PMCID-availability proxy sensitivity analysis: `supplement/Table_S5_PMC_fulltext_proxy_sensitivity.tsv`

This assessment does not claim that access-constrained extraction is unbiased. Its purpose is to quantify where information was unavailable under the record-level extraction workflow and to clarify the likely direction of bias.

## Clarification of the access policy

The evidence map was not designed as a full-text systematic review of all potentially relevant records. It was a scoping evidence map based on PubMed-indexed records, abstracts where available, and open-access full text when available. Records were included when the core eligibility criteria and minimum charting fields could be determined from those sources.

Accordingly, the findings should be interpreted as evidence about **record-level reporting**, not as a complete account of all information that may exist in subscription-only full texts, companion publications, trial registries, or programme reports.

## Selection-level impact

Across 1,716 deduplicated PubMed records screened, 530 records were included and 1,186 records were excluded. Twelve excluded records were assigned the exclusion reason `INSUFFICIENT_ABSTRACT_INFO`.

| Screening quantity | Count | Percentage |
| --- | ---: | ---: |
| Deduplicated records screened | 1,716 | 100.0 |
| Included records | 530 | 30.9 |
| Excluded records | 1,186 | 69.1 |
| Excluded for insufficient abstract/record information | 12 | 0.7 of screened; 1.0 of excluded |

The low number of exclusions coded specifically as insufficient abstract information suggests that the access policy did not primarily operate by excluding large numbers of otherwise eligible records. The larger methodological issue is information bias among included records: many programme details were not extractable at record level.

## Information-level impact among included records

Among the 530 included records, missingness or "unknown" coding was substantial for several implementation domains.

| Charting domain | Extractable, n | Missing/unknown, n | Missing/unknown, % |
| --- | ---: | ---: | ---: |
| Country/region | 177 | 353 | 66.6 |
| Income level | 177 | 353 | 66.6 |
| Delivery model | 356 | 174 | 32.8 |
| Return channel | 337 | 193 | 36.4 |
| Follow-up support mechanism | 87 | 443 | 83.6 |
| HPV assay type | 204 | 326 | 61.5 |
| Triage pathway | 423 | 107 | 20.2 |
| Invitation or reach denominator | 102 | 428 | 80.8 |
| Participation count | 123 | 407 | 76.8 |
| Uptake percentage | 117 | 413 | 77.9 |
| Follow-up completion percentage | 41 | 489 | 92.3 |

The highest missingness occurred for denominator, uptake, follow-up support, assay type, geography, and completion percentage fields. These are precisely the domains that often require full-text tables, supplementary files, or linked programme reports.

## PMCID-availability proxy sensitivity analysis

We used the PMCID field in the PubMed export as a reproducible proxy for PubMed Central full-text availability. This is not a complete open-access classification: some publisher open-access records do not have a PMCID, and PMCID availability does not guarantee that all implementation details are visible in the abstract or main text. It nevertheless provides a transparent sensitivity check for whether reporting visibility differed between records with and without a readily identifiable PMC full-text route.

Among the 530 included records, 359 had a PMCID and 171 did not. PMCID-available records had higher delivery-model classifiability than records without a PMCID (260/359, 72.4% vs 96/171, 56.1%), and higher return-channel classifiability (250/359, 69.6% vs 94/171, 55.0%). However, follow-up completion reporting was lower among PMCID-available records (20/359, 5.6%) than records without a PMCID (22/171, 12.9%). Follow-up support reporting was similar (16.2% vs 17.0%). Full results are provided in Table S5.

These results suggest that access-related effects varied by field. PMCID availability appeared to improve visibility of delivery and return-channel details, but it did not uniformly explain missing follow-up completion reporting.

## Direction of likely bias

The likely direction of bias is conservative for programme completeness and potentially unstable for delivery-model comparisons:

- **Under-capture of programme completeness:** If companion papers, subscription-only full texts, supplementary files, or registry records report follow-up completion, support mechanisms, or equity analyses not visible in PubMed abstracts, then the map may overstate single-publication reporting gaps.
- **Misclassification toward "unknown":** Delivery model, return channel, geography, and assay details may be coded as unknown when the information exists in full text but not in the record-level source.
- **Uncertain direction for follow-up completion proportions:** Completion can be under-captured when only referrals are visible in abstracts; however, highly successful completion may also be preferentially reported in abstracts, so the direction of completion-percentage bias cannot be assumed.
- **Programme-level evidence may be more complete than publication-level evidence:** Multi-publication programmes may distribute cascade domains across several papers, which a publication-level map does not fully represent unless companion publications are linked.

## Manual validation context

Appendix 5 manually reviewed 30 records initially labeled as unknown delivery model. Nineteen of 30 (63.3%) remained unclassifiable after manual abstract-level review, while 11 (36.7%) could be assigned a plausible manual label from the available record text. This supports two points:

1. Unknown labels often reflect limited record-level reporting rather than automated charting failure.
2. Some unknown labels can be reduced by targeted manual review, especially when the abstract contains implicit delivery details.

## Interpretation for this evidence map

This evidence map should avoid claims that the underlying implementation programmes failed to measure or report cascade elements. A more defensible interpretation is:

> In PubMed-indexed, record-level reporting, downstream completion, support mechanisms, equity analyses, and cost/resource signals were often not visible. This may reflect true reporting gaps, distribution of evidence across companion publications, limited abstract detail, or access restrictions.

This distinction is central to the revised interpretation of Figures 2 and 3 and to the revised recommendation for programme-level outcome visibility.
