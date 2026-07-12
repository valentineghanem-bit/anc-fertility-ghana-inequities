# S+ Sensitivity Analysis Report

Date: 2026-07-12

## Data

- Source: `outputs/data/Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv`
- Analytic rows used: 92 region-year observations
- Regions: 14 harmonized DHS analytic units
- Survey waves: 9 (1988-2022)

## Risk-Zone Sensitivity

Grand-mean risk-zone classification agreed with same-year z-score classification for 53.3% of observations.
Critical-zone overlap Jaccard index: 0.324 (11 shared Critical observations across 34 observations classified Critical by either method).

Grand-mean counts:

```
Risk_Zone_Grand
Resilient    45
Critical     23
Workhorse    18
Emerging      6
```

Same-year counts:

```
Risk_Zone_YearStratified
Resilient    31
Workhorse    22
Critical     22
Emerging     17
```

2022 same-year endpoint counts:

```
Risk_Zone_2022_YearStratified  n
                    Resilient  6
                     Critical  4
                     Emerging  2
                    Workhorse  2
```

Interpretation: the broad equity signal persists, but exact zone labels are sensitive to whether classification uses a grand historical reference or same-year reference. The manuscript keeps risk zones as exploratory targeting strata, not fixed allocation categories.

## ANC-TFR Association Robustness

Pearson r = -0.534 (p = 0.0000); Spearman rho = -0.520 (p = 0.0000).

```
                    model  coef_TFR   se_TFR    p_TFR  coef_year       p_year  n       r2
           OLS HC3 simple -3.927799 0.973902 0.000055        NaN          NaN 92 0.284966
           OLS HC3 + year -1.882292 0.743218 0.011321   0.375971 1.704520e-12 92 0.513923
OLS cluster region + year -1.882292 0.660700 0.004387   0.375971 1.413980e-05 92 0.513923
  OLS cluster year + year -1.882292 0.484416 0.000102   0.375971 1.743210e-20 92 0.513923
```

## Fixed-Effects and GEE Robustness

```
                            model  coef_TFR   se_TFR        p_TFR  n       r2
                   OLS HC3 + year -1.882292 0.743218 1.132122e-02 92 0.513923
              OLS HC3 + region FE -4.787706 0.957212 5.682146e-07 92 0.414499
       OLS HC3 + region FE + year  1.086426 0.990205 2.725657e-01 92 0.656304
         OLS HC3 + survey wave FE -2.052111 0.692037 3.023704e-03 92 0.545841
GEE exchangeable by region + year -0.838982 0.481580 8.148300e-02 92      NaN
```

Interpretation: the negative association remains in crude, survey-year, and clustered models, but attenuates under GEE and simultaneous region-plus-year adjustment. This supports ecological spatial-temporal patterning and decoupling, not individual-level causality.

## CEI Gap Robustness

Pooled CEI leader: Greater Accra (31.90).
Pooled CEI trailing region: North East (14.48).
Observed leader/trailer gap: 2.20x.
Bootstrap descriptive 95% interval for max/min pooled regional CEI gap: 1.55x to 2.20x.

Interpretation: the CEI gap is descriptively robust as an inequity signal, but the interval is descriptive rather than inferential because regions are ecological units, not independent sampled individuals.
