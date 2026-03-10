# Access Policy (OA / Abstract-sufficient Only)

## Policy Statement
To ensure the project is feasible without subscription access and remains reproducible, we will include studies only if the **core charting fields** can be obtained from:
1) a sufficiently detailed abstract/record (e.g., PubMed abstract + indexing metadata), or
2) open-access full text (e.g., PMC, publisher OA, OpenAlex OA URL, Semantic Scholar OA PDF).

Paywalled studies that require full text to extract core charting fields will be excluded and recorded with reason codes.

## Core Charting Fields (must be extractable to include)
- target_population (underscreened definition)
- setting (where/how delivered)
- delivery_model (kit distribution and return model)
- self-sampling modality: vaginal self-collection (confirm in abstract/OA)
- study design (RCT/program evaluation/etc.)
- uptake metric (any participation/uplift metric; can be partial, e.g., “kits returned”)
- triage / downstream follow-up existence (at least described at a high level; completion rate is a bonus if reported)

If any of the above cannot be obtained without paywalled full text, exclude.

## OA Discovery Heuristics (allowed)
- PubMed “Free PMC article”
- DOI landing page indicating OA PDF
- OpenAlex `oa_url`
- Semantic Scholar `openAccessPdf`

## Exclusion Recording
All exclusions are recorded in `results/screening/exclusion_reasons.tsv`, including:
- `PAYWALL_CORE_FIELDS`
- `INSUFFICIENT_ABSTRACT_INFO`

## Bias Note (must appear in Discussion)
This access policy may introduce selection bias (e.g., OA is not random across countries/journals/study types). We will quantify how many records are excluded for access/insufficient-information reasons and discuss implications for generalizability.
