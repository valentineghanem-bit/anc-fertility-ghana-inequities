# PLOS Global Public Health Alignment QA

Date: 2026-07-12

## Verdict

Submission package is aligned for PLOS Global Public Health file preparation and cross-artifact scientific consistency.

## Region-Unit Decision

- Analytic inference remains 14 harmonized Ghana DHS regional analytic units.
- Local data audit found no complete 16-region outcome panel for ANC, TFR, CEI, or Moran's I. The master analytic CSV has 92 region-year observations and 14 regions; Bono East and Western North do not have separate DHS outcome rows in the master panel.
- Dashboard/poster/manuscript now treat modern district boundaries as display geometry only. Bono East is harmonized to Bono and Western North to Western for display and interpretation.
- Using 16 analytic regions would be inconsistent with the data and would likely be criticised in review.

## Moran's I

- Live result is TFR Moran's I = 0.570, p = 0.001.
- This is the exact 999-permutation floor and is compatible with PLOS exact-p reporting expectations.
- No live manuscript/dashboard/poster/README claim uses the impossible `p < 0.001` wording. Remaining instances are explanatory QA notes documenting the correction.

## PLOS File Preparation Fixes

- Manuscript DOCX is unlocked, figure-free, double-spaced, page-numbered, and has continuous line numbering.
- Captions remain in the manuscript after first citation zones; figures are exported separately.
- `figures/Fig1.tif` through `figures/Fig17.tif` are RGB TIFF, 300 dpi, no alpha channel, LZW-compressed, and within PLOS pixel/file-size limits.
- Visible "Part I"/"Part II" serial-publication framing was removed from dashboard, poster, README, citation metadata, and app metadata.
- Literal encoding artifacts in the manuscript (`?` in ranges/R2 values) were removed.

## PLOS Guideline Items Checked

- Article structure: title page, abstract, introduction, methods, results, discussion, declarations, references, and figure captions present.
- Statistical reporting: software named, exact p-values used where applicable, permutation floor disclosed, missing-data/analytic-unit caveats retained.
- Human subjects: secondary anonymised aggregate DHS data and no individual-level data stated; ethics-review non-requirement stated.
- Data availability: repository URL is present. Strong upgrade before submission: create a stable Zenodo/GitHub release DOI or reviewer-accessible archived release and paste that identifier into the PLOS submission form.
- Funding/APC: funding is not embedded as a manuscript funding section; enter funding and any APC/waiver information in the PLOS submission system, not the cover letter.

## PLOS Sources Used

- PLOS Global Public Health submission guidelines: https://journals.plos.org/globalpublichealth/s/submission-guidelines
- PLOS figure guidelines: https://journals.plos.org/globalpublichealth/s/figures
