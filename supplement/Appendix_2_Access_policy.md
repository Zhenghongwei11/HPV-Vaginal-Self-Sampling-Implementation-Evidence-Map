# Appendix 2. Access and Information Policy

## Policy Statement
To ensure that the evidence map is reproducible without subscription access, studies were charted only when the core implementation fields could be obtained from:
1) a sufficiently detailed PubMed record/abstract and indexing metadata, or
2) open-access full text (e.g., PMC, publisher open access, OpenAlex open-access URL, or Semantic Scholar open-access PDF).

Paywalled studies that required subscription-only full text to extract core implementation fields were excluded and recorded with reason codes.

## Core Charting Fields (must be extractable to include)
- target population and underscreened definition
- setting and implementation context
- kit distribution and return model
- self-sampling modality: vaginal self-collection (confirm in abstract/OA)
- study design (RCT/program evaluation/etc.)
- uptake metric (any participation/uplift metric; can be partial, e.g., “kits returned”)
- triage / downstream follow-up existence (at least described at a high level; completion rate is a bonus if reported)

If these fields could not be obtained without subscription-only full text, the record was excluded from charting and logged.

## OA Discovery Heuristics (allowed)
- PubMed “Free PMC article”
- DOI landing page indicating OA PDF
- OpenAlex `oa_url`
- Semantic Scholar `openAccessPdf`

## Exclusion Recording
All exclusions are recorded in Dataset S2, including exclusions for insufficient record/abstract information.

## Bias Note
This access policy may introduce selection and information bias because open-access availability and abstract completeness are not random across countries, journals, study types, and programme types. This release therefore treats unknown categories as record-level non-reporting rather than definitive programme-level absence and reports an access and information-bias assessment in Appendix 6.
