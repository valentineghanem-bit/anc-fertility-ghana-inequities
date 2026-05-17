"""
Build the final combined replicable analysis dataset.
Merges: DHS panel (ANC + TFR) + Master Sheet (district-level socioeconomic data) 
 + derived analysis columns (CEI, Risk Zone, LISA, Gini).
Output: Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv
"""
import pandas as pd
import numpy as np

# ── 1. Load all sources ─────────────────────────────────────────────────────
panel = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/01_regional_health_panel.csv')
lisa = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/04_spatial_analysis_lisa.csv')
morans = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/04_temporal_morans_i.csv')
gini = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/03_gini_inequality.csv')
ml_perf= pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/05_ml_model_performance.csv')
rf_imp = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/05_random_forest_importance.csv')
dt_imp = pd.read_csv('/sessions/beautiful-gallant-pascal/analysis_outputs/05_decision_tree_importance.csv')

master_raw = pd.ExcelFile('/sessions/beautiful-gallant-pascal/mnt/uploads/Master Sheet.xlsx').parse('Sheet1')

print("Panel shape:", panel.shape)
print("LISA shape:", lisa.shape)
print("Master raw shape:", master_raw.shape)

# ── 2. Rename panel columns ─────────────────────────────────────────────────
panel = panel.rename(columns={
 'Antenatal care from a skilled provider': 'Skilled_ANC_pct',
 'Assistance during delivery from a skilled provider': 'Skilled_Delivery_pct',
 'No antenatal care': 'No_ANC_pct',
 'Place of delivery: Health facility': 'Health_Facility_Delivery_pct',
 'Age specific fertility rate: 15-19': 'Adolescent_Fertility_Rate',
 'General fertility rate': 'General_Fertility_Rate',
 'Total fertility rate 15-49': 'TFR',
})

# Fix region name inconsistency
panel['Region'] = panel['Region'].replace('..Northeast', 'North East')

# ── 3. Compute CEI per region-year ──────────────────────────────────────────
panel['Care_Efficiency_Index'] = (panel['Skilled_ANC_pct'] / panel['TFR']).round(3)

# ── 4. Compute z-score risk zones per region-year ──────────────────────────
valid = panel.dropna(subset=['Skilled_ANC_pct','TFR'])
anc_mean, anc_std = valid['Skilled_ANC_pct'].mean(), valid['Skilled_ANC_pct'].std()
tfr_mean, tfr_std = valid['TFR'].mean(), valid['TFR'].std()

panel['ANC_zscore'] = (panel['Skilled_ANC_pct'] - anc_mean) / anc_std
panel['TFR_zscore'] = (panel['TFR'] - tfr_mean) / tfr_std

def risk_zone(row):
 if pd.isna(row['ANC_zscore']) or pd.isna(row['TFR_zscore']): return None
 az, tz = row['ANC_zscore'], row['TFR_zscore']
 if az < 0 and tz > 0: return 'Critical'
 elif az < 0 and tz <= 0: return 'Emerging'
 elif az >= 0 and tz > 0: return 'Workhorse'
 else: return 'Resilient'

panel['Risk_Zone'] = panel.apply(risk_zone, axis=1)

# ── 5. Geographic zone classification ──────────────────────────────────────
NORTHERN = ['North East','Northern','Savannah','Upper East','Upper West','Oti']
MIDDLE = ['Ashanti','Brong-Ahafo','Bono','Ahafo','Bono East']
SOUTHERN = ['Greater Accra','Central','Eastern','Western','Volta','Western North']

def geo_zone(r):
 if r in NORTHERN: return 'Northern Belt'
 elif r in SOUTHERN: return 'Southern Belt'
 return 'Middle Belt'

panel['Geographic_Zone'] = panel['Region'].apply(geo_zone)

# ── 6. Merge LISA results (region-year level) ───────────────────────────────
lisa['Region'] = lisa['Region'].replace('..Northeast', 'North East')
lisa_cols = ['Region','SurveyYear','LISA_ANC','Quad_ANC','LISA_TFR','Quad_TFR']
df = panel.merge(lisa[lisa_cols], on=['Region','SurveyYear'], how='left')

# ── 7. Merge Moran's I (survey year level) ─────────────────────────────────
morans_cols = ['SurveyYear','Moran_I_ANC','p_ANC','Moran_I_TFR','p_TFR','n_regions']
df = df.merge(morans[morans_cols], on='SurveyYear', how='left')

# ── 8. Aggregate master sheet to region level ───────────────────────────────
region_master = master_raw.groupby('Region').agg(
 N_Districts=('Region','count'),
 Total_Population=('Total Population','sum'),
 Employed_Population=('Employed Population','sum'),
 Unemployed_Population=('Unemployed Population','sum'),
 Poverty_Incidence_mean_pct=('Incidence of Poverty','mean'),
 Poverty_Intensity_mean_pct=('Intensity of Poverty','mean'),
 Illiterate_Population=('Illiterate Population','sum'),
 Uninsured_Population=('Uninsured Population','sum'),
 Female_Pop_0_14=('Female Population 0-14','sum'),
 Male_Pop_0_14=('Male Population 0-14','sum'),
 Female_Pop_15_64=('Female Population 15-64','sum'),
 Male_Pop_15_64=('Male Population 15-64','sum'),
 Female_Pop_65plus=('Female Population 65+','sum'),
 Male_Pop_65plus=('Male Population 65+','sum'),
).reset_index()

# Derive rates
region_master['Illiteracy_Rate_pct'] = (
 region_master['Illiterate_Population'] / region_master['Total_Population'] * 100).round(2)
region_master['Uninsurance_Rate_pct'] = (
 region_master['Uninsured_Population'] / region_master['Total_Population'] * 100).round(2)
region_master['Unemployment_Rate_pct'] = (
 region_master['Unemployed_Population'] / 
 (region_master['Employed_Population'] + region_master['Unemployed_Population']) * 100).round(2)
region_master['Youth_Dependency_Ratio'] = (
 (region_master['Female_Pop_0_14'] + region_master['Male_Pop_0_14']) /
 (region_master['Female_Pop_15_64'] + region_master['Male_Pop_15_64']) * 100).round(2)

df = df.merge(region_master, on='Region', how='left')

# ── 9. Add source metadata ──────────────────────────────────────────────────
df.insert(0, 'ISO3', 'GHA')
df.insert(1, 'Country', 'Ghana')
df.insert(4, 'Data_Source_ANC', 'Ghana DHS subnational — access-to-health-care_subnational_gha.csv')
df.insert(5, 'Data_Source_TFR', 'Ghana DHS subnational — fertility-rates_subnational_gha.csv')
df.insert(6, 'Data_Source_Socioeconomic', 'Ghana Population & Housing Census / GHS — Master Sheet.xlsx')

# ── 10. Sort and reorder columns ────────────────────────────────────────────
id_cols = ['ISO3','Country','Region','Geographic_Zone','SurveyYear',
 'Data_Source_ANC','Data_Source_TFR','Data_Source_Socioeconomic']
anc_cols= ['Skilled_ANC_pct','No_ANC_pct','Skilled_Delivery_pct',
 'Health_Facility_Delivery_pct']
fert_cols=['TFR','Adolescent_Fertility_Rate','General_Fertility_Rate']
derived = ['Care_Efficiency_Index','Risk_Zone','ANC_zscore','TFR_zscore']
spatial = ['LISA_ANC','Quad_ANC','LISA_TFR','Quad_TFR',
 'Moran_I_ANC','p_ANC','Moran_I_TFR','p_TFR','n_regions']
socio = ['N_Districts','Total_Population','Poverty_Incidence_mean_pct',
 'Poverty_Intensity_mean_pct','Illiteracy_Rate_pct',
 'Uninsurance_Rate_pct','Unemployment_Rate_pct',
 'Youth_Dependency_Ratio','Illiterate_Population',
 'Uninsured_Population','Total_Population',
 'Female_Pop_0_14','Male_Pop_0_14',
 'Female_Pop_15_64','Male_Pop_15_64',
 'Female_Pop_65plus','Male_Pop_65plus']

all_cols = id_cols + anc_cols + fert_cols + derived + spatial + socio
# Only keep cols that exist
all_cols = [c for c in all_cols if c in df.columns]
df = df[all_cols].sort_values(['Region','SurveyYear']).reset_index(drop=True)

# ── 11. Save ────────────────────────────────────────────────────────────────
out = '/sessions/beautiful-gallant-pascal/Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv'
df.to_csv(out, index=False)
print(f'FINAL DATASET saved: {df.shape[0]} rows × {df.shape[1]} cols')
print('Columns:', df.columns.tolist())
print()
print(df.head(3).to_string())
