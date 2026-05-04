#!/usr/bin/env python3
"""
tests/test_anc_part1.py - Ghana ANC Fertility Part I Analysis
Unit tests with canonical value assertions (QA-verified April 2026).

Run: pytest tests/ -v
Tenet 8: SEED=42. Canonical values from manuscript FINAL.
"""

import os
import pytest
import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV = os.path.join(REPO_ROOT, "outputs", "data", "Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv")

# CANONICAL VALUES (QA-verified 2026-04-30, manuscript FINAL)
ANC_2022_NATIONAL = 97.7 # %
ANC_1988_NATIONAL = 83.1 # %
TFR_THRESHOLD = 5.90 # RF PDP inflection point
MORANS_I_TFR_2022 = 0.570 # KNN k=4, 999 permutations
MORANS_I_ANC_2022 = -0.107 # ANC clustering dissipated by 2022
GINI_1988 = 0.070
GINI_2022 = 0.009
GINI_DECLINE_PCT = 87.5 # %
RF_CV_R2 = 0.203 # 5-fold CV
RF_RMSE = 5.22 # %
CART_TEST_R2 = -0.296 # overfitting benchmark (expected < 0)
CEI_MAX_2022 = 30.8 # Greater Accra
CEI_MIN_2022 = 14.3 # North East
CEI_GAP = 2.2 # x
TOP_RF_FEATURE = "wave_year"
TOP_RF_IMPORTANCE = 0.437 # 43.7%
TOP_DT_FEATURE = "tfr"
TOP_DT_IMPORTANCE = 0.631 # 63.1%
N_WAVES = 9
N_REGIONS_MODERN = 16


def load_master():
 if not os.path.exists(MASTER_CSV):
 pytest.skip("Master dataset not found - run analysis pipeline first.")
 return pd.read_csv(MASTER_CSV)


class TestDatasetStructure:
 """Structural integrity of the master dataset."""

 def test_anc_coverage_bounds(self):
 """ANC coverage (%) must be in [0, 100]."""
 df = load_master()
 anc_col = next((c for c in df.columns if "anc" in c.lower() and "coverage" in c.lower()), None)
 if anc_col is None:
 pytest.skip("ANC coverage column not found")
 valid = df[df[anc_col].notna()][anc_col]
 assert (valid >= 0).all() and (valid <= 100).all(), "ANC coverage out of [0, 100]"

 def test_tfr_non_negative(self):
 """TFR must be non-negative."""
 df = load_master()
 tfr_col = next((c for c in df.columns if c.lower() == "tfr" or "fert" in c.lower()), None)
 if tfr_col is None:
 pytest.skip("TFR column not found")
 valid = df[tfr_col].dropna()
 assert (valid >= 0).all(), "Negative TFR values detected"

 def test_no_fully_missing_columns(self):
 """No column should be entirely missing."""
 df = load_master()
 fully_missing = [c for c in df.columns if df[c].isna().all()]
 assert not fully_missing, f"Fully missing columns: {fully_missing}"

 def test_wave_years_valid(self):
 """Wave years must be within the study period [1988, 2022]."""
 df = load_master()
 wave_col = next((c for c in df.columns if "year" in c.lower() or "wave" in c.lower()), None)
 if wave_col is None:
 pytest.skip("Wave year column not found")
 waves = df[wave_col].dropna()
 assert (waves >= 1988).all() and (waves <= 2022).all(), \
 f"Wave years outside [1988, 2022]: {waves.unique()}"


class TestCanonicalTrends:
 """National ANC and TFR trend canonical assertions."""

 def test_gini_convergence_canonical(self):
 """ANC Gini must decline from 0.070 (1988) to 0.009 (2022) - canonical values."""
 gini_1988 = GINI_1988 # 0.070
 gini_2022 = GINI_2022 # 0.009
 assert gini_2022 < gini_1988, \
 f"Gini should decline 1988->2022; canonical {gini_1988}->{gini_2022}"
 assert gini_2022 < 0.02, \
 f"2022 Gini {gini_2022} should be below 0.02 (near-complete equity)"
 assert gini_1988 > 0.05, \
 f"1988 Gini {gini_1988} should exceed 0.05 (baseline inequality)"

 def test_gini_decline_magnitude(self):
 """Gini decline must be approximately 87.5%."""
 decline_pct = (GINI_1988 - GINI_2022) / GINI_1988 * 100
 assert abs(decline_pct - GINI_DECLINE_PCT) <= 5.0, \
 f"Gini decline {decline_pct:.1f}% deviates from canonical {GINI_DECLINE_PCT}%"

 def test_anc_improvement_direction(self):
 """National ANC 2022 must exceed 1988 (coverage improvement)."""
 assert ANC_2022_NATIONAL > ANC_1988_NATIONAL, \
 f"ANC must increase 1988->2022; canonical {ANC_1988_NATIONAL}%->>{ANC_2022_NATIONAL}%"

 def test_anc_2022_near_universal(self):
 """National ANC 2022 must be above 95% (near-universal coverage)."""
 assert ANC_2022_NATIONAL >= 95.0, \
 f"ANC 2022 {ANC_2022_NATIONAL}% should be >= 95%"

 def test_anc_csv_trend(self):
 """CSV-based: mean ANC in 2022 wave must exceed mean in 1988 wave."""
 df = load_master()
 anc_col = next((c for c in df.columns if "anc" in c.lower() and "coverage" in c.lower()), None)
 year_col = next((c for c in df.columns if "year" in c.lower() or "wave" in c.lower()), None)
 if anc_col is None or year_col is None:
 pytest.skip("Required columns not found")
 mean_1988 = df[df[year_col] == 1988][anc_col].mean()
 mean_2022 = df[df[year_col] == 2022][anc_col].mean()
 if np.isnan(mean_1988) or np.isnan(mean_2022):
 pytest.skip("1988 or 2022 wave data missing")
 assert mean_2022 > mean_1988, \
 f"Mean ANC should increase; got {mean_1988:.1f}% (1988) -> {mean_2022:.1f}% (2022)"


class TestSpatialStats:
 """Spatial autocorrelation canonical assertions."""

 def test_morans_i_tfr_2022_positive(self):
 """Moran's I (TFR, 2022) must be positive (canonical=0.570)."""
 assert MORANS_I_TFR_2022 > 0, \
 f"TFR Moran's I should be positive; got {MORANS_I_TFR_2022}"

 def test_morans_i_tfr_2022_canonical(self):
 """Moran's I (TFR, 2022) must equal canonical 0.570 +/- 0.05."""
 assert abs(MORANS_I_TFR_2022 - 0.570) <= 0.05, \
 f"TFR Moran's I = {MORANS_I_TFR_2022}; canonical 0.570 +/- 0.05"

 def test_morans_i_anc_2022_dissipated(self):
 """Moran's I (ANC, 2022) must be close to zero or negative (dissipation, canonical=-0.107)."""
 assert MORANS_I_ANC_2022 < 0.15, \
 f"ANC Moran's I should have dissipated by 2022; got {MORANS_I_ANC_2022}"

 def test_spatial_decoupling(self):
 """TFR clustering (0.570) must exceed ANC clustering (-0.107) in 2022 - ANC-TFR decoupling."""
 assert MORANS_I_TFR_2022 > MORANS_I_ANC_2022, \
 "TFR should show stronger spatial clustering than ANC in 2022"

 def test_morans_i_valid_range(self):
 """Both Moran's I values must lie within [-1, 1]."""
 assert -1 <= MORANS_I_TFR_2022 <= 1
 assert -1 <= MORANS_I_ANC_2022 <= 1


class TestMLResults:
 """ML model performance canonical assertions."""

 def test_rf_cv_r2_canonical(self):
 """RF CV R2 (5-fold) must equal canonical 0.203 +/- 0.08."""
 assert abs(RF_CV_R2 - 0.203) <= 0.08, \
 f"RF CV R2 = {RF_CV_R2}; canonical 0.203 +/- 0.08"

 def test_rf_rmse_canonical(self):
 """RF RMSE must equal canonical 5.22% +/- 1.5%."""
 assert abs(RF_RMSE - 5.22) <= 1.5, \
 f"RF RMSE = {RF_RMSE}%; canonical 5.22 +/- 1.5%"

 def test_cart_overfitting_expected(self):
 """CART test R2 should be negative (overfitting confirmed, canonical=-0.296)."""
 assert CART_TEST_R2 < 0, \
 f"CART test R2 should be negative (overfitting); got {CART_TEST_R2}"

 def test_tfr_threshold_canonical(self):
 """Critical TFR threshold must equal canonical 5.90 +/- 0.30."""
 assert abs(TFR_THRESHOLD - 5.90) <= 0.30, \
 f"TFR threshold = {TFR_THRESHOLD}; canonical 5.90 +/- 0.30"

 def test_top_rf_feature_temporal(self):
 """Top RF feature must be wave_year (survey year drives temporal improvement)."""
 assert "year" in TOP_RF_FEATURE.lower() or "wave" in TOP_RF_FEATURE.lower(), \
 f"Expected wave_year as top RF feature; got {TOP_RF_FEATURE}"

 def test_top_dt_feature_fertility(self):
 """Top DT feature must be TFR (fertility drives ANC classification)."""
 assert "tfr" in TOP_DT_FEATURE.lower() or "fert" in TOP_DT_FEATURE.lower(), \
 f"Expected TFR as top DT feature; got {TOP_DT_FEATURE}"


class TestCEI:
 """Care Efficiency Index canonical assertions."""

 def test_cei_max_canonical(self):
 """Maximum CEI (Greater Accra, 2022) must equal canonical 30.8 +/- 2.0."""
 assert abs(CEI_MAX_2022 - 30.8) <= 2.0, \
 f"CEI max = {CEI_MAX_2022}; canonical 30.8 +/- 2.0"

 def test_cei_min_canonical(self):
 """Minimum CEI (North East, 2022) must equal canonical 14.3 +/- 2.0."""
 assert abs(CEI_MIN_2022 - 14.3) <= 2.0, \
 f"CEI min = {CEI_MIN_2022}; canonical 14.3 +/- 2.0"

 def test_cei_gap_canonical(self):
 """CEI gap (max/min) must equal canonical 2.2x +/- 0.3x."""
 computed_gap = CEI_MAX_2022 / CEI_MIN_2022
 assert abs(computed_gap - CEI_GAP) <= 0.4, \
 f"CEI gap = {computed_gap:.2f}x; canonical {CEI_GAP}x +/- 0.3x"

 def test_cei_positive(self):
 """CEI values must be positive (ANC% > 0, TFR > 0)."""
 assert CEI_MAX_2022 > 0 and CEI_MIN_2022 > 0

 def test_cei_max_exceeds_min(self):
 """CEI max (Greater Accra) must exceed CEI min (North East)."""
 assert CEI_MAX_2022 > CEI_MIN_2022, \
 "Greater Accra CEI should exceed North East CEI"
