"""
Comprehensive Spatial Machine Learning Analysis Pipeline
Spatial ML and Longitudinal Analysis of Skilled Antenatal Care Access and 
Fertility-Related Inequities in Ghana (1988–2022)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from scipy.spatial.distance import cdist
import os

# Set up paths
output_dir = '/sessions/beautiful-gallant-pascal/analysis_outputs/'
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("PART 1: DATA CLEANING & MERGING")
print("="*80)

# Load datasets
anc_df = pd.read_csv('/sessions/beautiful-gallant-pascal/mnt/uploads/access-to-health-care_subnational_gha.csv', 
 skiprows=[1]) # Skip HXL tags row
fertility_df = pd.read_csv('/sessions/beautiful-gallant-pascal/mnt/uploads/fertility-rates_subnational_gha.csv', 
 skiprows=[1])

# Load Master Sheet
master_df = pd.read_excel('/sessions/beautiful-gallant-pascal/mnt/uploads/Master Sheet.xlsx')

print(f"ANC data shape: {anc_df.shape}")
print(f"Fertility data shape: {fertility_df.shape}")
print(f"Master Sheet shape: {master_df.shape}")

# Function to harmonize region names
def harmonize_region_name(region_name):
 """Map various region name formats to 16 modern Ghana regions"""
 if pd.isna(region_name):
  return None
 
 region_name = str(region_name).strip().lower()
 
 # Define mapping for historical regions
 region_mapping = {
 'western': 'Western',
 'central': 'Central',
 'greater accra': 'Greater Accra',
 'eastern': 'Eastern',
 'ashanti': 'Ashanti',
 'northern': 'Northern',
 'upper east': 'Upper East',
 'upper west': 'Upper West',
 'volta': 'Volta',
 'brong ahafo': 'Ahafo',
 'ahafo': 'Ahafo',
 'bono': 'Bono',
 'bono east': 'Bono East',
 'savannah': 'Savannah',
 'north east': 'North East',
 'oti': 'Oti',
 'western (pre 2022)': 'Western',
 'western south': 'Western',
 'ghana': 'National',
 }
 
 for key, value in region_mapping.items():
  if key in region_name:
   return value

 # If no mapping found, try exact match after cleanup
 for key, value in region_mapping.items():
  if region_name == key:
   return value
 
 return region_name.title()

# Clean ANC data
anc_df.columns = anc_df.columns.str.strip()
anc_clean = anc_df.copy()

# Map columns
anc_clean['Region'] = anc_clean['Location'].apply(harmonize_region_name)
anc_clean['SurveyYear'] = anc_clean['SurveyYear']
anc_clean['Indicator'] = anc_clean['Indicator']
anc_clean['Value'] = pd.to_numeric(anc_clean['Value'], errors='coerce')

# Filter to preferred estimates if available
if 'isPreferred' in anc_clean.columns:
 anc_clean = anc_clean[anc_clean['isPreferred'] == 1].copy()

# Extract key ANC indicators
key_anc_indicators = [
 "Antenatal care from a skilled provider",
 "No antenatal care",
 "Place of delivery: Health facility",
 "Assistance during delivery from a skilled provider"
]

anc_filtered = anc_clean[anc_clean['Indicator'].isin(key_anc_indicators)][
 ['Region', 'SurveyYear', 'Indicator', 'Value']
].copy()

print(f"ANC filtered shape: {anc_filtered.shape}")
print(f"ANC indicators found: {anc_filtered['Indicator'].unique()}")

# Clean Fertility data
fertility_clean = fertility_df.copy()
fertility_clean.columns = fertility_clean.columns.str.strip()

fertility_clean['Region'] = fertility_clean['Location'].apply(harmonize_region_name)
fertility_clean['SurveyYear'] = fertility_clean['SurveyYear']
fertility_clean['Indicator'] = fertility_clean['Indicator']
fertility_clean['Value'] = pd.to_numeric(fertility_clean['Value'], errors='coerce')

if 'isPreferred' in fertility_clean.columns:
 fertility_clean = fertility_clean[fertility_clean['isPreferred'] == 1].copy()

# Extract key fertility indicators
key_fertility_indicators = [
 "Total fertility rate 15-49",
 "Age specific fertility rate: 15-19",
 "General fertility rate",
 "Wanted fertility rate"
]

fertility_filtered = fertility_clean[fertility_clean['Indicator'].isin(key_fertility_indicators)][
 ['Region', 'SurveyYear', 'Indicator', 'Value']
].copy()

print(f"Fertility filtered shape: {fertility_filtered.shape}")
print(f"Fertility indicators found: {fertility_filtered['Indicator'].unique()}")

# Create pivot tables for easier analysis
anc_pivot = anc_filtered.pivot_table(
 index=['Region', 'SurveyYear'],
 columns='Indicator',
 values='Value',
 aggfunc='first'
).reset_index()

fertility_pivot = fertility_filtered.pivot_table(
 index=['Region', 'SurveyYear'],
 columns='Indicator',
 values='Value',
 aggfunc='first'
).reset_index()

# Merge datasets
merged_data = anc_pivot.merge(
 fertility_pivot,
 on=['Region', 'SurveyYear'],
 how='outer'
)

# Exclude National level for regional analysis
regional_data = merged_data[merged_data['Region'] != 'National'].copy()

print(f"Merged regional data shape: {regional_data.shape}")
print(f"Regions in data: {regional_data['Region'].nunique()}")
print(f"Survey years: {sorted(regional_data['SurveyYear'].dropna().unique())}")

# Clean Master Sheet for district-level analysis
master_clean = master_df.copy()
master_clean.columns = master_clean.columns.str.strip()

print(f"Master Sheet districts: {len(master_clean)}")
print(f"Master Sheet regions: {master_clean['Region'].nunique()}")

# Create district-level region aggregations
district_regional_agg = master_clean.groupby('Region').agg({
 'Latitude': 'mean',
 'Longitude': 'mean',
 'Employed Population': 'sum',
 'Unemployed Population': 'sum',
 'Illiterate Population': 'sum',
 'Uninsured Population': 'sum',
 'Total Population': 'sum'
}).reset_index()

district_regional_agg['Unemployment_Rate'] = (
 district_regional_agg['Unemployed Population'] / 
 (district_regional_agg['Employed Population'] + district_regional_agg['Unemployed Population']) * 100
)

district_regional_agg['Illiteracy_Rate'] = (
 district_regional_agg['Illiterate Population'] / 
 district_regional_agg['Total Population'] * 100
)

district_regional_agg['Uninsured_Rate'] = (
 district_regional_agg['Uninsured Population'] / 
 district_regional_agg['Total Population'] * 100
)

# Save cleaned data
regional_data.to_csv(f'{output_dir}01_regional_health_panel.csv', index=False)
district_regional_agg.to_csv(f'{output_dir}02_district_regional_aggregates.csv', index=False)
anc_filtered.to_csv(f'{output_dir}01_anc_clean.csv', index=False)
fertility_filtered.to_csv(f'{output_dir}01_fertility_clean.csv', index=False)

print(f"\nData saved to {output_dir}")

print("\n" + "="*80)
print("PART 2: DESCRIPTIVE STATISTICS & TEMPORAL TRENDS")
print("="*80)

# Function to calculate Gini coefficient
def gini_coefficient(values):
 """Calculate Gini coefficient for inequality"""
 values = np.array(values)
 values = values[~np.isnan(values)]
 if len(values) < 2:
 return np.nan
 sorted_vals = np.sort(values)
 n = len(values)
 return (2 * np.sum(np.arange(1, n+1) * sorted_vals)) / (n * np.sum(sorted_vals)) - (n + 1) / n

# Get main ANC indicator
anc_indicator = "Antenatal care from a skilled provider"
regional_anc = regional_data[['Region', 'SurveyYear', anc_indicator]].copy()
regional_anc.columns = ['Region', 'SurveyYear', 'Skilled_ANC']

# Get TFR
tfr_indicator = "Total fertility rate 15-49"
regional_tfr = regional_data[['Region', 'SurveyYear', tfr_indicator]].copy()
regional_tfr.columns = ['Region', 'SurveyYear', 'TFR']

# Get adolescent fertility
adol_indicator = "Age specific fertility rate: 15-19"
regional_adol = regional_data[['Region', 'SurveyYear', adol_indicator]].copy()
regional_adol.columns = ['Region', 'SurveyYear', 'Adolescent_Fertility']

# Merge into single dataset
analysis_panel = regional_anc.merge(regional_tfr, on=['Region', 'SurveyYear'], how='outer')
analysis_panel = analysis_panel.merge(regional_adol, on=['Region', 'SurveyYear'], how='outer')

print(f"Analysis panel shape: {analysis_panel.shape}")

# Calculate national statistics
national_stats = analysis_panel.groupby('SurveyYear').agg({
 'Skilled_ANC': ['mean', 'median', 'min', 'max', 'std'],
 'TFR': ['mean', 'median', 'min', 'max', 'std'],
 'Adolescent_Fertility': ['mean', 'median', 'min', 'max', 'std']
}).round(2)

# Calculate regional statistics
regional_stats = analysis_panel.groupby('Region').agg({
 'Skilled_ANC': ['mean', 'min', 'max'],
 'TFR': ['mean', 'min', 'max'],
 'Adolescent_Fertility': ['mean', 'min', 'max']
}).round(2)

# Calculate change from first to last year
first_year = analysis_panel['SurveyYear'].min()
last_year = analysis_panel['SurveyYear'].max()

baseline = analysis_panel[analysis_panel['SurveyYear'] == first_year].set_index('Region')
latest = analysis_panel[analysis_panel['SurveyYear'] == last_year].set_index('Region')

# Create change table only for regions present in both years
common_regions = set(baseline.index) & set(latest.index)

regional_change_list = []
for region in common_regions:
 try:
 anc_1st = baseline.loc[region, 'Skilled_ANC']
 anc_lst = latest.loc[region, 'Skilled_ANC']
 tfr_1st = baseline.loc[region, 'TFR']
 tfr_lst = latest.loc[region, 'TFR']
 
 if pd.notna(anc_1st) and pd.notna(anc_lst) and anc_1st != 0:
 anc_change = anc_lst - anc_1st
 anc_pct = (anc_change / anc_1st) * 100
 else:
 anc_change = np.nan
 anc_pct = np.nan
 
 if pd.notna(tfr_1st) and pd.notna(tfr_lst) and tfr_1st != 0:
 tfr_change = tfr_lst - tfr_1st
 tfr_pct = (tfr_change / tfr_1st) * 100
 else:
 tfr_change = np.nan
 tfr_pct = np.nan
 
 regional_change_list.append({
 'Region': region,
 'ANC_First': anc_1st,
 'ANC_Last': anc_lst,
 'ANC_Absolute_Change': anc_change,
 'ANC_Percent_Change': anc_pct,
 'TFR_First': tfr_1st,
 'TFR_Last': tfr_lst,
 'TFR_Absolute_Change': tfr_change,
 'TFR_Percent_Change': tfr_pct
 })
 except:
 pass

regional_change = pd.DataFrame(regional_change_list)

# Calculate Gini coefficients over time
gini_by_year = []
for year in sorted(analysis_panel['SurveyYear'].dropna().unique()):
 year_data = analysis_panel[analysis_panel['SurveyYear'] == year]
 gini_anc = gini_coefficient(year_data['Skilled_ANC'].values)
 gini_tfr = gini_coefficient(year_data['TFR'].values)
 gini_by_year.append({
 'SurveyYear': int(year),
 'Gini_ANC': gini_anc,
 'Gini_TFR': gini_tfr
 })

gini_df = pd.DataFrame(gini_by_year)

# Identify coldspots (persistently below national average)
national_mean = analysis_panel['Skilled_ANC'].mean()
coldspot_analysis = analysis_panel.groupby('Region').apply(
 lambda x: (x['Skilled_ANC'] < national_mean).sum() / len(x)
).sort_values(ascending=False)
coldspot_regions = coldspot_analysis[coldspot_analysis > 0.5]

print(f"\nColdspot regions (>50% below national average): {coldspot_regions.index.tolist()}")

# North-South divide analysis
north_regions = ['Northern', 'Upper East', 'Upper West', 'Savannah', 'North East']
south_regions = ['Greater Accra', 'Western', 'Central', 'Eastern', 'Volta']

analysis_panel['Zone'] = 'Middle'
analysis_panel.loc[analysis_panel['Region'].isin(north_regions), 'Zone'] = 'North'
analysis_panel.loc[analysis_panel['Region'].isin(south_regions), 'Zone'] = 'South'

zone_trends = analysis_panel.groupby(['SurveyYear', 'Zone']).agg({
 'Skilled_ANC': 'mean',
 'TFR': 'mean'
}).reset_index()

zone_gap = zone_trends.pivot(index='SurveyYear', columns='Zone', values='Skilled_ANC')
if 'North' in zone_gap.columns and 'South' in zone_gap.columns:
 zone_gap['North_South_Gap'] = zone_gap['South'] - zone_gap['North']

# Save summary statistics
national_stats.to_csv(f'{output_dir}03_national_statistics.csv')
regional_stats.to_csv(f'{output_dir}03_regional_statistics.csv')
regional_change.to_csv(f'{output_dir}03_regional_change.csv', index=False)
gini_df.to_csv(f'{output_dir}03_gini_inequality.csv', index=False)
zone_gap.to_csv(f'{output_dir}03_zone_gaps.csv')

print(f"\nSummary statistics saved")
print(f"Gini coefficients (ANC inequality):")
print(gini_df.to_string())
print(f"\nZone gaps (ANC access):")
print(zone_gap)

print("\n" + "="*80)
print("PART 3: SPATIAL ANALYSIS")
print("="*80)

try:
 from libpysal.weights import KNN
 from esda import Moran, moran_local
 
 # Get unique regions with coordinates
 region_coords = district_regional_agg[['Region', 'Latitude', 'Longitude']].copy()
 region_coords = region_coords.dropna(subset=['Latitude', 'Longitude'])
 
 # Create spatial weights using KNN
 coords = region_coords[['Latitude', 'Longitude']].values
 
 # Use KNN since we don't have actual boundaries
 w = KNN.from_array(coords, k=4)
 w.transform = 'r' # Row standardize
 
 print(f"Spatial weights created for {len(region_coords)} regions")
 
 # Prepare data for spatial analysis - use latest year
 latest_year = int(analysis_panel['SurveyYear'].max())
 spatial_data = analysis_panel[analysis_panel['SurveyYear'] == latest_year].copy()
 spatial_data = spatial_data.merge(region_coords[['Region', 'Latitude', 'Longitude']], 
 on='Region', how='inner')
 spatial_data = spatial_data.sort_values('Region').reset_index(drop=True)
 
 # Get uninsured rate from master sheet
 spatial_data = spatial_data.merge(
 district_regional_agg[['Region', 'Uninsured_Rate']], 
 on='Region', how='left'
 )
 
 # Global Moran's I for uninsured population
 uninsured_vals = spatial_data['Uninsured_Rate'].dropna().values
 moran_uninsured = Moran(uninsured_vals, w)
 
 # Moran's I for ANC
 anc_vals = spatial_data['Skilled_ANC'].dropna().values
 if len(anc_vals) > 3:
 moran_anc = Moran(anc_vals, w)
 
 # LISA (Local Indicators of Spatial Association)
 lisa_anc = moran_local(anc_vals, w)
 
 # Classify clusters
 spatial_data['LISA_Cluster'] = 'Non-significant'
 
 # High-High, High-Low, Low-High, Low-Low
 threshold = np.nanmean(anc_vals)
 lag_anc = np.array(w.sparse.dot(anc_vals))
 
 for i in range(len(anc_vals)):
 if i < len(lisa_anc.p_sim) and lisa_anc.p_sim[i] < 0.05:
 val = anc_vals[i]
 lag_val = lag_anc[i]
 
 if val > threshold and lag_val > threshold:
 spatial_data.loc[i, 'LISA_Cluster'] = 'HH (High-High)'
 elif val > threshold and lag_val < threshold:
 spatial_data.loc[i, 'LISA_Cluster'] = 'HL (High-Low)'
 elif val < threshold and lag_val > threshold:
 spatial_data.loc[i, 'LISA_Cluster'] = 'LH (Low-High)'
 else:
 spatial_data.loc[i, 'LISA_Cluster'] = 'LL (Low-Low)'
 
 # Temporal Moran's I by epoch
 temporal_epochs = [
 (1988, 1998, '1988-1998'),
 (1999, 2010, '1999-2010'),
 (2011, 2022, '2011-2022')
 ]
 
 temporal_morans = []
 for start, end, label in temporal_epochs:
 epoch_data = analysis_panel[
 (analysis_panel['SurveyYear'] >= start) & 
 (analysis_panel['SurveyYear'] <= end)
 ].copy()
 
 if len(epoch_data) > 0:
 epoch_data = epoch_data.merge(region_coords[['Region', 'Latitude', 'Longitude']], 
 on='Region', how='inner')
 epoch_data = epoch_data.sort_values('Region').reset_index(drop=True)
 
 anc_epoch = epoch_data['Skilled_ANC'].dropna().values
 if len(anc_epoch) > 3:
 try:
 moran_epoch = Moran(anc_epoch, w)
 temporal_morans.append({
 'Epoch': label,
 'Morans_I': moran_epoch.I,
 'P_value': moran_epoch.p_norm
 })
 except:
 pass
 
 temporal_moran_df = pd.DataFrame(temporal_morans)
 
 # Save spatial results
 spatial_results = pd.DataFrame({
 'Region': spatial_data['Region'],
 'Skilled_ANC': spatial_data['Skilled_ANC'],
 'TFR': spatial_data['TFR'],
 'Uninsured_Rate': spatial_data['Uninsured_Rate'],
 'LISA_Cluster': spatial_data['LISA_Cluster'],
 'Latitude': spatial_data['Latitude'],
 'Longitude': spatial_data['Longitude']
 })
 
 spatial_results.to_csv(f'{output_dir}04_spatial_analysis_lisa.csv', index=False)
 temporal_moran_df.to_csv(f'{output_dir}04_temporal_morans_i.csv', index=False)
 
 print(f"\nGlobal Moran's I (Uninsured Rate): {moran_uninsured.I:.4f} (p={moran_uninsured.p_norm:.4f})")
 print(f"Global Moran's I (ANC): {moran_anc.I:.4f} (p={moran_anc.p_norm:.4f})")
 print(f"\nLISA Cluster distribution:")
 print(spatial_data['LISA_Cluster'].value_counts())
 print(f"\nTemporal Moran's I by epoch:")
 print(temporal_moran_df.to_string())
 
except Exception as e:
 print(f"Spatial analysis error: {str(e)}")
 print("Continuing with remaining analyses...")

print("\n" + "="*80)
print("PART 4: MACHINE LEARNING")
print("="*80)

# Prepare data for ML
ml_data = analysis_panel.dropna(subset=['Skilled_ANC', 'TFR', 'Adolescent_Fertility']).copy()
ml_data = ml_data.merge(
 district_regional_agg[['Region', 'Uninsured_Rate']], 
 on='Region', how='left'
)

# Encode geographic zone
zone_mapping = {'North': 0, 'Middle': 1, 'South': 2}
ml_data['Zone_Code'] = ml_data['Zone'].map(zone_mapping)

# Features and target
X = ml_data[['TFR', 'SurveyYear', 'Zone_Code', 'Adolescent_Fertility']].values
y = ml_data['Skilled_ANC'].values

# Remove any NaNs
mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
X = X[mask]
y = y[mask]
ml_data = ml_data.iloc[mask]

print(f"ML dataset size: {len(X)} observations")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Decision Tree
dt_model = DecisionTreeRegressor(max_depth=5, random_state=42, min_samples_leaf=3)
dt_model.fit(X_train, y_train)

dt_pred_train = dt_model.predict(X_train)
dt_pred_test = dt_model.predict(X_test)

dt_r2_train = r2_score(y_train, dt_pred_train)
dt_r2_test = r2_score(y_test, dt_pred_test)
dt_rmse = np.sqrt(mean_squared_error(y_test, dt_pred_test))
dt_mae = mean_absolute_error(y_test, dt_pred_test)

dt_cv_scores = cross_val_score(dt_model, X_train, y_train, cv=5, scoring='r2')

print(f"\nDecision Tree Performance:")
print(f" Train R²: {dt_r2_train:.4f}")
print(f" Test R²: {dt_r2_test:.4f}")
print(f" Cross-validated R² (mean±std): {dt_cv_scores.mean():.4f} ± {dt_cv_scores.std():.4f}")
print(f" RMSE: {dt_rmse:.4f}")
print(f" MAE: {dt_mae:.4f}")

# Feature importance
dt_importance = pd.DataFrame({
 'Feature': ['TFR', 'SurveyYear', 'Zone', 'Adolescent_Fertility'],
 'Importance': dt_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Random Forest
rf_model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, min_samples_leaf=2)
rf_model.fit(X_train, y_train)

rf_pred_train = rf_model.predict(X_train)
rf_pred_test = rf_model.predict(X_test)

rf_r2_train = r2_score(y_train, rf_pred_train)
rf_r2_test = r2_score(y_test, rf_pred_test)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred_test))
rf_mae = mean_absolute_error(y_test, rf_pred_test)

rf_cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='r2')

print(f"\nRandom Forest Performance:")
print(f" Train R²: {rf_r2_train:.4f}")
print(f" Test R²: {rf_r2_test:.4f}")
print(f" Cross-validated R² (mean±std): {rf_cv_scores.mean():.4f} ± {rf_cv_scores.std():.4f}")
print(f" RMSE: {rf_rmse:.4f}")
print(f" MAE: {rf_mae:.4f}")

# Feature importance
rf_importance = pd.DataFrame({
 'Feature': ['TFR', 'SurveyYear', 'Zone', 'Adolescent_Fertility'],
 'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

# Find critical TFR threshold (where ANC = 80%)
tfr_range = np.linspace(X[:, 0].min(), X[:, 0].max(), 100)
test_X_tfr = np.column_stack([
 tfr_range,
 np.full(len(tfr_range), X[:, 1].mean()), # Mean survey year
 np.full(len(tfr_range), 1), # Middle zone
 np.full(len(tfr_range), X[:, 3].mean()) # Mean adolescent fertility
])

pred_anc = rf_model.predict(test_X_tfr)
threshold_80 = tfr_range[np.argmin(np.abs(pred_anc - 80))]

print(f"\nCritical TFR threshold (ANC ~80%): {threshold_80:.2f}")

# Care Efficiency Index
ml_data['Care_Efficiency_Index'] = ml_data['Skilled_ANC'] / ml_data['TFR']

cei_by_region = ml_data.groupby('Region').agg({
 'Skilled_ANC': 'mean',
 'TFR': 'mean',
 'Care_Efficiency_Index': 'mean',
 'Adolescent_Fertility': 'mean'
}).round(3)

# Risk stratification
ml_data['ANC_zscore'] = stats.zscore(ml_data['Skilled_ANC'].fillna(ml_data['Skilled_ANC'].mean()))
ml_data['TFR_zscore'] = stats.zscore(ml_data['TFR'].fillna(ml_data['TFR'].mean()))

def risk_classification(anc_z, tfr_z):
 """Classify risk zones based on ANC and TFR Z-scores"""
 if anc_z > 0.5 and tfr_z < 0.5:
 return 'Resilient' # High ANC, Low TFR
 elif anc_z > 0.5 and tfr_z > 0.5:
 return 'Workhorse' # High ANC, High TFR
 elif anc_z < -0.5 and tfr_z < 0.5:
 return 'Emerging' # Low ANC, Low TFR
 else:
 return 'Critical' # Low ANC, High TFR

ml_data['Risk_Zone'] = ml_data.apply(
 lambda row: risk_classification(row['ANC_zscore'], row['TFR_zscore']), 
 axis=1
)

risk_profiles = ml_data.groupby('Risk_Zone').agg({
 'Region': 'count',
 'Skilled_ANC': 'mean',
 'TFR': 'mean',
 'Adolescent_Fertility': 'mean',
 'Care_Efficiency_Index': 'mean'
}).round(3)
risk_profiles.columns = ['Count', 'Avg_ANC', 'Avg_TFR', 'Avg_Adol_Fert', 'Avg_CEI']

# Save ML results
ml_performance = pd.DataFrame({
 'Model': ['Decision Tree', 'Random Forest'],
 'Train_R2': [dt_r2_train, rf_r2_train],
 'Test_R2': [dt_r2_test, rf_r2_test],
 'CV_R2_Mean': [dt_cv_scores.mean(), rf_cv_scores.mean()],
 'CV_R2_Std': [dt_cv_scores.std(), rf_cv_scores.std()],
 'RMSE': [dt_rmse, rf_rmse],
 'MAE': [dt_mae, rf_mae]
})

ml_performance.to_csv(f'{output_dir}05_ml_model_performance.csv', index=False)
dt_importance.to_csv(f'{output_dir}05_decision_tree_importance.csv', index=False)
rf_importance.to_csv(f'{output_dir}05_random_forest_importance.csv', index=False)
cei_by_region.to_csv(f'{output_dir}05_care_efficiency_index.csv')
risk_profiles.to_csv(f'{output_dir}05_risk_stratification.csv')

print(f"\nCare Efficiency Index (top regions):")
print(cei_by_region.sort_values('Care_Efficiency_Index', ascending=False).head(10).to_string())

print(f"\nRisk Stratification Summary:")
print(risk_profiles.to_string())

print("\n" + "="*80)
print("PART 5: GENERATING FIGURES")
print("="*80)

import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set publication-quality settings
rcParams['font.size'] = 10
rcParams['font.family'] = 'sans-serif'
plt.style.use('seaborn-v0_8-darkgrid')

color_palette = ['#FFB81C', '#007A5E', '#CE1126', '#000000'] # Ghana colors
sns.set_palette(color_palette)

# Figure 1: Heatmap of Skilled ANC by region over time
fig1, ax = plt.subplots(figsize=(14, 8), dpi=300)

pivot_anc = analysis_panel.pivot_table(
 index='Region', columns='SurveyYear', values='Skilled_ANC'
)
pivot_anc = pivot_anc.dropna(how='all')

sns.heatmap(pivot_anc, cmap='RdYlGn', annot=True, fmt='.1f', 
 cbar_kws={'label': 'Skilled ANC %'}, ax=ax, vmin=0, vmax=100)
ax.set_title('Skilled Antenatal Care Access by Region (1988-2022)', fontsize=14, fontweight='bold')
ax.set_xlabel('Survey Year', fontsize=12)
ax.set_ylabel('Region', fontsize=12)
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_01_anc_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 1 - ANC Heatmap")

# Figure 2: Longitudinal trajectory of ANC by region
fig2, ax = plt.subplots(figsize=(14, 8), dpi=300)

for region in analysis_panel['Region'].unique():
 region_data = analysis_panel[analysis_panel['Region'] == region].sort_values('SurveyYear')
 ax.plot(region_data['SurveyYear'], region_data['Skilled_ANC'], 
 marker='o', label=region, linewidth=2, markersize=6, alpha=0.7)

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Skilled ANC Access (%)', fontsize=12, fontweight='bold')
ax.set_title('Longitudinal Trajectory of Skilled Antenatal Care Access by Region', 
 fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_02_anc_trajectories.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 2 - ANC Trajectories")

# Figure 3: TFR vs ANC scatter with regional labels
fig3, ax = plt.subplots(figsize=(12, 8), dpi=300)

scatter = ax.scatter(analysis_panel['TFR'], analysis_panel['Skilled_ANC'], 
 s=100, alpha=0.6, c=analysis_panel['SurveyYear'], 
 cmap='viridis', edgecolors='black', linewidth=0.5)

# Add regression line
valid_data = analysis_panel[['TFR', 'Skilled_ANC']].dropna()
z = np.polyfit(valid_data['TFR'], valid_data['Skilled_ANC'], 1)
p = np.poly1d(z)
x_line = np.linspace(valid_data['TFR'].min(), valid_data['TFR'].max(), 100)
ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Trend')

ax.set_xlabel('Total Fertility Rate', fontsize=12, fontweight='bold')
ax.set_ylabel('Skilled ANC Access (%)', fontsize=12, fontweight='bold')
ax.set_title('Relationship: Fertility Rate vs. Skilled Antenatal Care Access', 
 fontsize=14, fontweight='bold')
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Survey Year', fontsize=11)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_03_tfr_vs_anc_scatter.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 3 - TFR vs ANC Scatter")

# Figure 4: Decision Tree Visualization
fig4, ax = plt.subplots(figsize=(16, 10), dpi=300)

feature_names = ['TFR', 'SurveyYear', 'Zone', 'Adolescent_Fertility']
plot_tree(dt_model, feature_names=feature_names, filled=True, 
 ax=ax, fontsize=10, rounded=True)
plt.title('Decision Tree: Predicting Skilled ANC Access', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_04_decision_tree.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 4 - Decision Tree")

# Figure 5: Multi-panel Feature Importance
fig5, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)

# Panel A: Random Forest Importance
ax = axes[0, 0]
rf_imp_sorted = rf_importance.sort_values('Importance', ascending=True)
ax.barh(rf_imp_sorted['Feature'], rf_imp_sorted['Importance'], color=color_palette[0])
ax.set_xlabel('Importance', fontweight='bold')
ax.set_title('A. Random Forest Feature Importance', fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')

# Panel B: Correlation with ANC
ax = axes[0, 1]
valid_tfr_anc = analysis_panel[['TFR', 'Skilled_ANC']].dropna()
valid_adol_anc = analysis_panel[['Adolescent_Fertility', 'Skilled_ANC']].dropna()
valid_year_anc = analysis_panel[['SurveyYear', 'Skilled_ANC']].dropna()

corr_tfr = np.corrcoef(valid_tfr_anc['TFR'], valid_tfr_anc['Skilled_ANC'])[0, 1]
corr_adol = np.corrcoef(valid_adol_anc['Adolescent_Fertility'], valid_adol_anc['Skilled_ANC'])[0, 1]
corr_year = np.corrcoef(valid_year_anc['SurveyYear'], valid_year_anc['Skilled_ANC'])[0, 1]

correlations = pd.DataFrame({
 'Feature': ['TFR', 'Adolescent Fertility', 'Survey Year'],
 'Correlation': [corr_tfr, corr_adol, corr_year]
}).sort_values('Correlation', ascending=True)

ax.barh(correlations['Feature'], correlations['Correlation'], color=color_palette[1])
ax.set_xlabel('Correlation with ANC', fontweight='bold')
ax.set_title('B. Correlation with Skilled ANC', fontweight='bold')
ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax.grid(True, alpha=0.3, axis='x')

# Panel C: Zone gaps in ANC
ax = axes[1, 0]
zone_means = analysis_panel.groupby('Zone')['Skilled_ANC'].mean().sort_values(ascending=True)
ax.barh(zone_means.index, zone_means.values, color=color_palette[2])
ax.set_xlabel('Mean Skilled ANC (%)', fontweight='bold')
ax.set_title('C. ANC Access by Geographic Zone', fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')

# Panel D: Risk Classification Distribution
ax = axes[1, 1]
risk_counts = ml_data['Risk_Zone'].value_counts().sort_values(ascending=True)
colors_risk = {
 'Critical': '#CE1126',
 'Emerging': '#FFB81C', 
 'Workhorse': '#007A5E',
 'Resilient': '#1B1B1B'
}
colors_mapped = [colors_risk.get(z, '#000000') for z in risk_counts.index]
ax.barh(risk_counts.index, risk_counts.values, color=colors_mapped)
ax.set_xlabel('Number of Region-Years', fontweight='bold')
ax.set_title('D. Risk Stratification Distribution', fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')

plt.suptitle('Feature Importance & Machine Learning Insights', fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_05_feature_importance_multi.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 5 - Feature Importance Multi-panel")

# Figure 6: LISA Cluster Map (if spatial analysis successful)
try:
 fig6, ax = plt.subplots(figsize=(12, 10), dpi=300)
 
 cluster_colors = {
 'HH (High-High)': '#007A5E',
 'HL (High-Low)': '#FFB81C',
 'LH (Low-High)': '#CE1126',
 'LL (Low-Low)': '#1B1B1B',
 'Non-significant': '#CCCCCC'
 }
 
 for cluster in cluster_colors.keys():
 cluster_data = spatial_results[spatial_results['LISA_Cluster'] == cluster]
 if len(cluster_data) > 0:
 ax.scatter(cluster_data['Longitude'], cluster_data['Latitude'], 
 s=300, alpha=0.7, label=cluster, color=cluster_colors[cluster],
 edgecolors='black', linewidth=1.5)
 
 ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
 ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
 ax.set_title('LISA Cluster Map: Spatial Association of ANC Access\n(High/Low ANC regions with spatial clustering)', 
 fontsize=14, fontweight='bold')
 ax.legend(loc='best', fontsize=10)
 ax.grid(True, alpha=0.3)
 
 plt.tight_layout()
 plt.savefig(f'{output_dir}06_figure_06_lisa_map.png', dpi=300, bbox_inches='tight')
 plt.close()
 
 print("Saved: Figure 6 - LISA Cluster Map")
except Exception as e:
 print(f"Skipped: Figure 6 - LISA Map ({str(e)})")

# Figure 7: Temporal Moran's I
try:
 if len(temporal_moran_df) > 0:
 fig7, ax = plt.subplots(figsize=(10, 6), dpi=300)
 
 ax.plot(range(len(temporal_moran_df)), temporal_moran_df['Morans_I'], 
 marker='o', linewidth=3, markersize=10, color=color_palette[0])
 ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
 ax.fill_between(range(len(temporal_moran_df)), 0, temporal_moran_df['Morans_I'], 
 alpha=0.3, color=color_palette[0])
 
 ax.set_xticks(range(len(temporal_moran_df)))
 ax.set_xticklabels(temporal_moran_df['Epoch'])
 ax.set_ylabel("Moran's I Statistic", fontsize=12, fontweight='bold')
 ax.set_title("Temporal Evolution of Spatial Autocorrelation in ANC Access", 
 fontsize=14, fontweight='bold')
 ax.grid(True, alpha=0.3)
 
 plt.tight_layout()
 plt.savefig(f'{output_dir}06_figure_07_temporal_morans_i.png', dpi=300, bbox_inches='tight')
 plt.close()
 
 print("Saved: Figure 7 - Temporal Moran's I")
except:
 print("Skipped: Figure 7 - Temporal Moran's I")

# Figure 8: Risk Stratification Radar/Dashboard
fig8, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)

for idx, risk_zone in enumerate(['Critical', 'Emerging', 'Workhorse', 'Resilient']):
 ax = axes[idx // 2, idx % 2]
 
 zone_data = ml_data[ml_data['Risk_Zone'] == risk_zone]
 
 metrics = {
 'ANC Access': zone_data['Skilled_ANC'].mean(),
 'TFR': zone_data['TFR'].mean(),
 'Adol. Fert.': zone_data['Adolescent_Fertility'].mean(),
 'CEI': zone_data['Care_Efficiency_Index'].mean() * 10,
 'N Regions': len(zone_data['Region'].unique())
 }
 
 ax.bar(metrics.keys(), metrics.values(), color=color_palette)
 ax.set_ylabel('Value', fontweight='bold')
 ax.set_title(f'{risk_zone} Zones (n={len(zone_data)})', fontweight='bold', fontsize=12)
 ax.grid(True, alpha=0.3, axis='y')
 
 for spine in ['top', 'right']:
 ax.spines[spine].set_visible(False)

plt.suptitle('Risk Stratification Zone Profiles', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_08_risk_stratification_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 8 - Risk Stratification Dashboard")

# Figure 9: North-South Gap Convergence
fig9, ax = plt.subplots(figsize=(12, 7), dpi=300)

if 'North' in zone_gap.columns and 'South' in zone_gap.columns:
 ax.plot(zone_gap.index, zone_gap['North'], marker='o', label='North', 
 linewidth=2.5, markersize=8, color=color_palette[1])
 ax.plot(zone_gap.index, zone_gap['South'], marker='s', label='South', 
 linewidth=2.5, markersize=8, color=color_palette[2])
 ax.plot(zone_gap.index, zone_gap['North_South_Gap'], marker='^', label='Gap (S-N)', 
 linewidth=2.5, markersize=8, color=color_palette[3])
 
 ax.fill_between(zone_gap.index, zone_gap['North'], zone_gap['South'], 
 alpha=0.2, color='gray')

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Skilled ANC Access (%)', fontsize=12, fontweight='bold')
ax.set_title('North-South Equity Gap in Skilled Antenatal Care: Convergence Analysis', 
 fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_09_north_south_gap.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 9 - North-South Gap")

# Figure 10: Adolescent Fertility Trends
fig10, ax = plt.subplots(figsize=(14, 8), dpi=300)

for region in analysis_panel['Region'].unique():
 region_data = analysis_panel[analysis_panel['Region'] == region].sort_values('SurveyYear')
 ax.plot(region_data['SurveyYear'], region_data['Adolescent_Fertility'], 
 marker='o', label=region, linewidth=2, markersize=6, alpha=0.7)

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Adolescent Fertility Rate (15-19 years)', fontsize=12, fontweight='bold')
ax.set_title('Longitudinal Trends in Adolescent Fertility Rate by Region', 
 fontsize=14, fontweight='bold')
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_10_adolescent_fertility_trends.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 10 - Adolescent Fertility Trends")

# Figure 11: Gini Coefficient of ANC Inequality
fig11, ax = plt.subplots(figsize=(12, 7), dpi=300)

ax.plot(gini_df['SurveyYear'], gini_df['Gini_ANC'], marker='o', 
 linewidth=3, markersize=10, color=color_palette[0], label='ANC Access')
ax.fill_between(gini_df['SurveyYear'], 0, gini_df['Gini_ANC'], 
 alpha=0.3, color=color_palette[0])

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Gini Coefficient', fontsize=12, fontweight='bold')
ax.set_title('Temporal Evolution of Inter-Regional Inequality in Skilled ANC Access\n(Gini Coefficient: 0=Perfect Equality, 1=Perfect Inequality)', 
 fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_11_gini_inequality.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 11 - Gini Inequality")

# Figure 12: Partial Dependence Plot (TFR effect on predicted ANC)
fig12, ax = plt.subplots(figsize=(12, 7), dpi=300)

# Create partial dependence data
pd_tfr = np.linspace(X[:, 0].min(), X[:, 0].max(), 50)
pd_data = np.column_stack([
 pd_tfr,
 np.full(len(pd_tfr), X[:, 1].mean()),
 np.full(len(pd_tfr), 1),
 np.full(len(pd_tfr), X[:, 3].mean())
])

pd_pred = rf_model.predict(pd_data)

ax.plot(pd_tfr, pd_pred, linewidth=3, color=color_palette[0], label='Predicted ANC')
ax.fill_between(pd_tfr, pd_pred - rf_rmse, pd_pred + rf_rmse, 
 alpha=0.3, color=color_palette[0])

ax.axhline(y=80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='80% ANC Target')
ax.axvline(x=threshold_80, color='green', linestyle='--', linewidth=2, alpha=0.7, 
 label=f'Critical TFR={threshold_80:.2f}')

ax.set_xlabel('Total Fertility Rate (TFR)', fontsize=12, fontweight='bold')
ax.set_ylabel('Predicted Skilled ANC Access (%)', fontsize=12, fontweight='bold')
ax.set_title('Partial Dependence: Effect of Fertility Rate on ANC Access\n(Random Forest Model)', 
 fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}06_figure_12_partial_dependence_tfr.png', dpi=300, bbox_inches='tight')
plt.close()

print("Saved: Figure 12 - Partial Dependence Plot")

print("\n" + "="*80)
print("PART 6: SUMMARY TABLES")
print("="*80)

# Table 1: Longitudinal audit of regional maternal health disparities
table1 = regional_change.copy()
table1['ANC_Progress'] = 'Improved'
table1.loc[table1['ANC_Absolute_Change'] < 0, 'ANC_Progress'] = 'Declined'
table1_sorted = table1[['Region', 'ANC_First', 'ANC_Last', 'ANC_Absolute_Change', 
 'ANC_Percent_Change', 'ANC_Progress', 'TFR_First', 'TFR_Last']].round(2)
table1_sorted.to_csv(f'{output_dir}07_table_01_regional_disparities.csv', index=False)

# Table 2: Temporal evolution of spatial association
table2_data = []
for year in sorted(analysis_panel['SurveyYear'].dropna().unique()):
 year_subset = analysis_panel[analysis_panel['SurveyYear'] == year]
 n_regions = year_subset['Region'].nunique()
 anc_mean = year_subset['Skilled_ANC'].mean()
 tfr_mean = year_subset['TFR'].mean()
 
 valid_tfr_anc = year_subset[['TFR', 'Skilled_ANC']].dropna()
 if len(valid_tfr_anc) > 2:
 corr = np.corrcoef(valid_tfr_anc['TFR'], valid_tfr_anc['Skilled_ANC'])[0, 1]
 else:
 corr = np.nan
 
 gini = gini_coefficient(year_subset['Skilled_ANC'].values)
 
 table2_data.append({
 'SurveyYear': int(year),
 'N_Regions': n_regions,
 'ANC_Mean': round(anc_mean, 2),
 'ANC_Std': round(year_subset['Skilled_ANC'].std(), 2),
 'TFR_Mean': round(tfr_mean, 2),
 'TFR_Std': round(year_subset['TFR'].std(), 2),
 'TFR_ANC_Correlation': round(corr, 3),
 'Gini_ANC': round(gini, 3)
 })

table2 = pd.DataFrame(table2_data)
table2.to_csv(f'{output_dir}07_table_02_spatial_temporal_evolution.csv', index=False)

# Table 3: High-priority risk region profiles
risk_critical = ml_data[ml_data['Risk_Zone'] == 'Critical'].groupby('Region').agg({
 'Skilled_ANC': 'mean',
 'TFR': 'mean',
 'Adolescent_Fertility': 'mean',
 'Care_Efficiency_Index': 'mean'
}).round(2).sort_values('Skilled_ANC')

if len(risk_critical) > 0:
 risk_critical['Risk_Level'] = 'Critical'
 risk_critical['Recommended_Interventions'] = risk_critical.apply(
 lambda row: 'Strengthen ANC, reduce fertility' if row['TFR'] > 3 else 'Increase ANC access',
 axis=1
 )
 
 table3 = risk_critical.reset_index()[['Region', 'Risk_Level', 'Skilled_ANC', 'TFR', 
 'Care_Efficiency_Index', 'Recommended_Interventions']]
 table3.to_csv(f'{output_dir}07_table_03_critical_regions.csv', index=False)

# Table 4: ML model performance and critical thresholds
table4_data = {
 'Metric': [
 'Decision Tree R² (Train)',
 'Decision Tree R² (Test)',
 'Random Forest R² (Train)',
 'Random Forest R² (Test)',
 'RF Cross-Val R² (mean)',
 'RF RMSE',
 'RF MAE',
 'Critical TFR Threshold (ANC=80%)',
 'Top Feature (RF)',
 'Correlation: TFR-ANC'
 ],
 'Value': [
 f'{dt_r2_train:.4f}',
 f'{dt_r2_test:.4f}',
 f'{rf_r2_train:.4f}',
 f'{rf_r2_test:.4f}',
 f'{rf_cv_scores.mean():.4f}',
 f'{rf_rmse:.4f}',
 f'{rf_mae:.4f}',
 f'{threshold_80:.2f}',
 rf_importance.iloc[0]['Feature'],
 f'{corr_tfr:.3f}'
 ]
}

table4 = pd.DataFrame(table4_data)
table4.to_csv(f'{output_dir}07_table_04_ml_performance.csv', index=False)

# Table 5: Care Efficiency Index profiles
table5 = cei_by_region.round(3).reset_index().sort_values('Care_Efficiency_Index', ascending=False)
table5['CEI_Rank'] = range(1, len(table5) + 1)
table5_final = table5[['CEI_Rank', 'Region', 'Skilled_ANC', 'TFR', 'Care_Efficiency_Index']]
table5_final.to_csv(f'{output_dir}07_table_05_care_efficiency.csv', index=False)

# Table 6: Risk stratification dashboard
risk_summary = ml_data.groupby('Risk_Zone').agg({
 'Region': 'nunique',
 'Skilled_ANC': ['mean', 'min', 'max'],
 'TFR': ['mean', 'min', 'max'],
 'Adolescent_Fertility': 'mean',
 'Care_Efficiency_Index': 'mean'
}).round(2)

risk_summary.columns = ['N_Regions', 'ANC_Mean', 'ANC_Min', 'ANC_Max', 'TFR_Mean', 
 'TFR_Min', 'TFR_Max', 'Adolescent_Fert_Mean', 'CEI_Mean']
risk_summary = risk_summary.reset_index()

risk_order = {'Critical': 0, 'Emerging': 1, 'Workhorse': 2, 'Resilient': 3}
risk_summary['Order'] = risk_summary['Risk_Zone'].map(risk_order)
risk_summary = risk_summary.sort_values('Order').drop('Order', axis=1)

table6 = risk_summary[['Risk_Zone', 'N_Regions', 'ANC_Mean', 'TFR_Mean', 'Adolescent_Fert_Mean', 'CEI_Mean']]
table6.to_csv(f'{output_dir}07_table_06_risk_dashboard.csv', index=False)

print(f"\nAll summary tables saved to {output_dir}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

print(f"\nAll outputs saved to: {output_dir}")
print(f"\nOutput files generated:")
import glob
output_files = sorted(glob.glob(f'{output_dir}*'))
for i, f in enumerate(output_files, 1):
 fname = os.path.basename(f)
 size = os.path.getsize(f) / 1024
 print(f" {i:2d}. {fname:50s} ({size:8.1f} KB)")

print("\n" + "="*80)
