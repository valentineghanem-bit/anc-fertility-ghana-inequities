#!/usr/bin/env python3
"""
S+ sensitivity analyses for the Ghana ANC-fertility ecological panel.

Inputs:
  outputs/data/Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv

Outputs:
  outputs/sensitivity/*.csv
  outputs/sensitivity/SPLUS_SENSITIVITY_ANALYSIS_2026-07-12.md

These analyses are intentionally conservative. They test whether the headline
equity interpretation depends on risk-zone reference distributions, simple
ANC-TFR model specification, fixed effects, repeated regional observations, or
the descriptive CEI gap definition.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.cov_struct import Exchangeable


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "data" / "Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv"
OUT = ROOT / "outputs" / "sensitivity"


def classify_risk(anc_z: float, tfr_z: float) -> str:
    if anc_z < 0 and tfr_z > 0:
        return "Critical"
    if anc_z < 0 and tfr_z <= 0:
        return "Emerging"
    if anc_z >= 0 and tfr_z > 0:
        return "Workhorse"
    return "Resilient"


def fmt_p(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.4f}"


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA).dropna(
        subset=["Skilled_ANC_pct", "TFR", "SurveyYear", "Region"]
    )
    df = df.copy()

    # Risk-zone sensitivity: grand historical z-score vs same-year z-score.
    df["Risk_Zone_Grand"] = df["Risk_Zone"]
    df["ANC_z_year"] = df.groupby("SurveyYear")["Skilled_ANC_pct"].transform(
        lambda s: (s - s.mean()) / s.std(ddof=1)
    )
    df["TFR_z_year"] = df.groupby("SurveyYear")["TFR"].transform(
        lambda s: (s - s.mean()) / s.std(ddof=1)
    )
    df["Risk_Zone_YearStratified"] = [
        classify_risk(a, t)
        for a, t in zip(df["ANC_z_year"], df["TFR_z_year"], strict=False)
    ]

    risk_crosstab = pd.crosstab(
        df["Risk_Zone_Grand"], df["Risk_Zone_YearStratified"]
    )
    risk_year_counts = pd.crosstab(df["SurveyYear"], df["Risk_Zone_YearStratified"])
    endpoint_counts = (
        df.loc[df["SurveyYear"] == 2022, "Risk_Zone_YearStratified"]
        .value_counts()
        .rename_axis("Risk_Zone_2022_YearStratified")
        .reset_index(name="n")
    )

    agreement = (df["Risk_Zone_Grand"] == df["Risk_Zone_YearStratified"]).mean()
    critical_grand = set(df.index[df["Risk_Zone_Grand"] == "Critical"])
    critical_year = set(df.index[df["Risk_Zone_YearStratified"] == "Critical"])
    overlap = len(critical_grand & critical_year)
    union = len(critical_grand | critical_year)
    jaccard = overlap / union if union else np.nan

    df.to_csv(OUT / "risk_zone_year_stratified_sensitivity.csv", index=False)
    risk_crosstab.to_csv(OUT / "risk_zone_sensitivity_crosstab.csv")
    risk_year_counts.to_csv(OUT / "risk_zone_year_counts.csv")
    endpoint_counts.to_csv(OUT / "risk_zone_2022_year_stratified_counts.csv", index=False)

    # ANC-TFR association robustness.
    df["YearCentered"] = df["SurveyYear"] - df["SurveyYear"].mean()
    pearson = stats.pearsonr(df["TFR"], df["Skilled_ANC_pct"])
    spearman = stats.spearmanr(df["TFR"], df["Skilled_ANC_pct"])

    model_specs = {
        "OLS HC3 simple": "Skilled_ANC_pct ~ TFR",
        "OLS HC3 + year": "Skilled_ANC_pct ~ TFR + YearCentered",
    }
    rows: list[dict[str, float | int | str]] = []
    for name, formula in model_specs.items():
        model = smf.ols(formula, data=df).fit(cov_type="HC3")
        rows.append(
            {
                "model": name,
                "coef_TFR": model.params.get("TFR", np.nan),
                "se_TFR": model.bse.get("TFR", np.nan),
                "p_TFR": model.pvalues.get("TFR", np.nan),
                "coef_year": model.params.get("YearCentered", np.nan),
                "p_year": model.pvalues.get("YearCentered", np.nan),
                "n": int(model.nobs),
                "r2": model.rsquared,
            }
        )

    clustered = {
        "OLS cluster region + year": (
            {"groups": df["Region"]},
            "Skilled_ANC_pct ~ TFR + YearCentered",
        ),
        "OLS cluster year + year": (
            {"groups": df["SurveyYear"]},
            "Skilled_ANC_pct ~ TFR + YearCentered",
        ),
    }
    for name, (cov_kwds, formula) in clustered.items():
        model = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds=cov_kwds)
        rows.append(
            {
                "model": name,
                "coef_TFR": model.params.get("TFR", np.nan),
                "se_TFR": model.bse.get("TFR", np.nan),
                "p_TFR": model.pvalues.get("TFR", np.nan),
                "coef_year": model.params.get("YearCentered", np.nan),
                "p_year": model.pvalues.get("YearCentered", np.nan),
                "n": int(model.nobs),
                "r2": model.rsquared,
            }
        )

    association = pd.DataFrame(rows)
    association.to_csv(OUT / "anc_tfr_association_robustness.csv", index=False)

    fe_rows: list[dict[str, float | int | str]] = []
    fe_specs = {
        "OLS HC3 + year": "Skilled_ANC_pct ~ TFR + YearCentered",
        "OLS HC3 + region FE": "Skilled_ANC_pct ~ TFR + C(Region)",
        "OLS HC3 + region FE + year": (
            "Skilled_ANC_pct ~ TFR + YearCentered + C(Region)"
        ),
        "OLS HC3 + survey wave FE": "Skilled_ANC_pct ~ TFR + C(SurveyYear)",
    }
    for name, formula in fe_specs.items():
        model = smf.ols(formula, data=df).fit(cov_type="HC3")
        fe_rows.append(
            {
                "model": name,
                "coef_TFR": model.params.get("TFR", np.nan),
                "se_TFR": model.bse.get("TFR", np.nan),
                "p_TFR": model.pvalues.get("TFR", np.nan),
                "n": int(model.nobs),
                "r2": model.rsquared,
            }
        )

    try:
        gee = smf.gee(
            "Skilled_ANC_pct ~ TFR + YearCentered",
            groups="Region",
            data=df,
            cov_struct=Exchangeable(),
            family=sm.families.Gaussian(),
        ).fit()
        fe_rows.append(
            {
                "model": "GEE exchangeable by region + year",
                "coef_TFR": gee.params.get("TFR", np.nan),
                "se_TFR": gee.bse.get("TFR", np.nan),
                "p_TFR": gee.pvalues.get("TFR", np.nan),
                "n": len(df),
                "r2": np.nan,
            }
        )
    except Exception as exc:  # pragma: no cover - diagnostic fallback only
        fe_rows.append(
            {
                "model": f"GEE failed: {type(exc).__name__}: {exc}",
                "coef_TFR": np.nan,
                "se_TFR": np.nan,
                "p_TFR": np.nan,
                "n": len(df),
                "r2": np.nan,
            }
        )

    fixed_effects = pd.DataFrame(fe_rows)
    fixed_effects.to_csv(OUT / "anc_tfr_fixed_effects_gee_robustness.csv", index=False)

    # CEI gap robustness: descriptive regional mean gap with bootstrap over regions.
    regional = df.groupby("Region", as_index=False).agg(
        mean_cei=("Care_Efficiency_Index", "mean"),
        mean_anc=("Skilled_ANC_pct", "mean"),
        mean_tfr=("TFR", "mean"),
        n_waves=("SurveyYear", "count"),
    )
    leader = regional.loc[regional["mean_cei"].idxmax()]
    trailer = regional.loc[regional["mean_cei"].idxmin()]
    gap = leader["mean_cei"] / trailer["mean_cei"]

    rng = np.random.default_rng(20260712)
    boots = []
    for _ in range(10_000):
        sample = regional.sample(
            n=len(regional),
            replace=True,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        boots.append(sample["mean_cei"].max() / sample["mean_cei"].min())
    lo, hi = np.percentile(boots, [2.5, 97.5])
    regional.to_csv(OUT / "regional_pooled_cei_summary.csv", index=False)

    report = f"""# S+ Sensitivity Analysis Report

Date: 2026-07-12

## Data

- Source: `outputs/data/Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv`
- Analytic rows used: {len(df)} region-year observations
- Regions: {df.Region.nunique()} harmonized DHS analytic units
- Survey waves: {df.SurveyYear.nunique()} ({int(df.SurveyYear.min())}-{int(df.SurveyYear.max())})

## Risk-Zone Sensitivity

Grand-mean risk-zone classification agreed with same-year z-score classification for {agreement:.1%} of observations.
Critical-zone overlap Jaccard index: {jaccard:.3f} ({overlap} shared Critical observations across {union} observations classified Critical by either method).

Grand-mean counts:

```
{df["Risk_Zone_Grand"].value_counts().to_string()}
```

Same-year counts:

```
{df["Risk_Zone_YearStratified"].value_counts().to_string()}
```

2022 same-year endpoint counts:

```
{endpoint_counts.to_string(index=False)}
```

Interpretation: the broad equity signal persists, but exact zone labels are sensitive to whether classification uses a grand historical reference or same-year reference. The manuscript keeps risk zones as exploratory targeting strata, not fixed allocation categories.

## ANC-TFR Association Robustness

Pearson r = {pearson.statistic:.3f} (p = {fmt_p(pearson.pvalue)}); Spearman rho = {spearman.statistic:.3f} (p = {fmt_p(spearman.pvalue)}).

```
{association.to_string(index=False)}
```

## Fixed-Effects and GEE Robustness

```
{fixed_effects.to_string(index=False)}
```

Interpretation: the negative association remains in crude, survey-year, and clustered models, but attenuates under GEE and simultaneous region-plus-year adjustment. This supports ecological spatial-temporal patterning and decoupling, not individual-level causality.

## CEI Gap Robustness

Pooled CEI leader: {leader.Region} ({leader.mean_cei:.2f}).
Pooled CEI trailing region: {trailer.Region} ({trailer.mean_cei:.2f}).
Observed leader/trailer gap: {gap:.2f}x.
Bootstrap descriptive 95% interval for max/min pooled regional CEI gap: {lo:.2f}x to {hi:.2f}x.

Interpretation: the CEI gap is descriptively robust as an inequity signal, but the interval is descriptive rather than inferential because regions are ecological units, not independent sampled individuals.
"""
    (OUT / "SPLUS_SENSITIVITY_ANALYSIS_2026-07-12.md").write_text(
        report, encoding="utf-8"
    )
    print(f"Wrote sensitivity outputs to {OUT}")


if __name__ == "__main__":
    run()
