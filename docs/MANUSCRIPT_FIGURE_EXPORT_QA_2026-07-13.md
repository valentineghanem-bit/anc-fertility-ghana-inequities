# Manuscript Figure Export QA - Article 1
Date: 2026-07-13

## Scope
All manuscript source figures in `outputs/figures/` were standardized for journal upload.

## Fixes Applied
- Converted every source PNG to RGB with a white background.
- Set every source PNG to 300 dpi metadata.
- Regenerated all PLOS upload TIFFs as RGB, 300 dpi, LZW-compressed, no alpha channel.
- Added non-overlapping cartographic bands to the manuscript map figures with:
  - north arrow;
  - true-north bearing;
  - approximate 0-100-200 km scale bar;
  - cartographic note.

## Map Figures Updated
- `06_figure_06_lisa_map_2022.png` -> `Fig12.tif`
- `06_figure_C4_risk_zone_choropleth.png` -> `Fig13.tif`
- `06_figure_C1_anc_choropleth_2022.png` -> `Fig14.tif`
- `06_figure_C2_tfr_choropleth_2022.png` -> `Fig15.tif`
- `06_figure_C3_cei_choropleth.png` -> `Fig16.tif`
- `06_figure_C5_anc_temporal_choropleth.png` -> `Fig17.tif`

## Verification
- Source PNGs: 17/17 RGB, white background, 300 dpi.
- PLOS TIFFs in `Q1_FINAL_2026-07-12/figures`: 17/17 RGB, 300 dpi, LZW-compressed.
- PLOS TIFFs in `SPLUS_2026-07-12/figures`: 17/17 RGB, 300 dpi, LZW-compressed.
- Test suite: 4 passed, 1 skipped.
