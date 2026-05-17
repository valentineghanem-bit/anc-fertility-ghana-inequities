import pandas as pd, numpy as np, geopandas as gpd
import matplotlib.pyplot as plt, matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
import openpyxl, os, warnings
warnings.filterwarnings('ignore')

from shapely.geometry import Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union, voronoi_diagram as shp_voronoi
from scipy.spatial import Voronoi

OUT = '/sessions/beautiful-gallant-pascal/analysis_outputs/'

# ── Ghana palette ──────────────────────────────────────────────────────────
GH_GREEN='#006B3F'; GH_RED='#CE1126'; GH_GOLD='#FCD116'; GH_BLACK='#000000'

# ── Simplified Ghana boundary polygon (lon,lat) ────────────────────────────
# Hand-crafted from known border coordinates (clockwise)
ghana_coords = [
 (-3.260,10.640),(-2.830,10.990),(-2.500,11.010),(-2.090,11.090),
 (-1.570,11.080),(-1.120,11.090),(-0.680,11.130),(-0.170,11.110),
 (0.150,11.060),(0.520,10.790),(0.800,10.530),(1.000,10.190),
 (1.070,9.710),(0.870,9.220),(0.660,8.720),(0.560,8.210),
 (0.580,7.700),(0.570,7.200),(0.530,6.800),(0.370,6.450),
 (0.140,6.080),(0.200,5.750),(0.430,5.440),(0.510,5.140),
 (0.300,4.950),(0.100,4.790),(-0.090,4.750),(-0.290,4.700),
 (-0.750,4.760),(-1.090,4.850),(-1.400,4.950),(-1.720,5.020),
 (-1.980,4.980),(-2.280,5.010),(-2.670,5.090),(-2.950,5.140),
 (-3.080,5.240),(-3.230,5.420),(-3.270,5.770),(-3.230,6.090),
 (-3.250,6.430),(-3.080,6.780),(-2.900,7.040),(-2.750,7.360),
 (-2.670,7.650),(-2.760,7.990),(-2.920,8.250),(-3.060,8.550),
 (-2.990,8.920),(-2.810,9.190),(-2.680,9.510),(-2.750,9.830),
 (-2.900,10.100),(-3.000,10.350),(-3.260,10.640)
]
ghana_poly = Polygon(ghana_coords)

# ── Load data ──────────────────────────────────────────────────────────────
wb = openpyxl.load_workbook('/sessions/beautiful-gallant-pascal/mnt/uploads/Master Sheet.xlsx')
ws = wb.active
rows = list(ws.values)
df_master = pd.DataFrame(rows[1:], columns=rows[0])

reg_centroids = df_master.groupby('Region').agg(
 lat=('Latitude','mean'), lon=('Longitude','mean')
).reset_index()

panel = pd.read_csv(OUT+'01_regional_health_panel.csv')
cei_df = pd.read_csv(OUT+'05_care_efficiency_index.csv')
# Individual risk per region-year from panel
# Recreate risk zones: z-score approach
panel['anc_z'] = (panel['Antenatal care from a skilled provider'] -
 panel['Antenatal care from a skilled provider'].mean()) / \
 panel['Antenatal care from a skilled provider'].std()
panel['tfr_z'] = (panel['Total fertility rate 15-49'] -
 panel['Total fertility rate 15-49'].mean()) / \
 panel['Total fertility rate 15-49'].std()

def risk_zone(row):
 if row['anc_z'] < 0 and row['tfr_z'] > 0: return 'Critical'
 elif row['anc_z'] < 0 and row['tfr_z'] <= 0: return 'Emerging'
 elif row['anc_z'] >= 0 and row['tfr_z'] > 0: return 'Workhorse'
 else: return 'Resilient'
panel['RiskZone'] = panel.apply(risk_zone, axis=1)

# Region name mapping between panel and Master Sheet
reg_map = {
 '..Northeast':'North East','Ahafo':'Ahafo','Ashanti':'Ashanti',
 'Bono':'Bono','Central':'Central','Eastern':'Eastern',
 'Greater Accra':'Greater Accra','Northern':'Northern','Oti':'Oti',
 'Savannah':'Savannah','Upper East':'Upper East','Upper West':'Upper West',
 'Volta':'Volta','Western':'Western'
}

# ── Build Voronoi GeoDataFrame for 16 regions ─────────────────────────────
def build_voronoi_gdf(centroids_df, boundary_poly):
 pts_lon = centroids_df['lon'].values
 pts_lat = centroids_df['lat'].values
 
 # Add far-away mirror points to bound the Voronoi
 eps = 8
 mirror_x = [pts_lon.min()-eps, pts_lon.max()+eps,
 pts_lon.mean(), pts_lon.mean()]
 mirror_y = [pts_lat.mean(), pts_lat.mean(),
 pts_lat.min()-eps, pts_lat.max()+eps]
 all_pts = np.vstack([np.column_stack([pts_lon, pts_lat]),
 np.column_stack([mirror_x, mirror_y])])
 
 vor = Voronoi(all_pts)
 n_regions = len(pts_lon)
 polygons = []
 
 for i in range(n_regions):
  region_idx = vor.point_region[i]
  verts = vor.regions[region_idx]
  if -1 in verts or len(verts) == 0:
   polygons.append(None)
   continue
   poly = Polygon(vor.vertices[verts])
   clipped = poly.intersection(boundary_poly)
   polygons.append(clipped)
 
   gdf = gpd.GeoDataFrame(centroids_df.copy(), geometry=polygons, crs='EPSG:4326')
   gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
   return gdf

gdf_base = build_voronoi_gdf(reg_centroids, ghana_poly)
print("Voronoi GDF regions:", len(gdf_base))
print(gdf_base[['Region','lat','lon']].to_string())

# ── Helper: merge data onto GDF ───────────────────────────────────────────
def merge_gdf(gdf, data_df, key_gdf, key_data, value_col):
 merged = gdf.copy()
 merged = merged.merge(data_df[[key_data, value_col]], 
 left_on=key_gdf, right_on=key_data, how='left')
 return merged

# ── Standardize region names in panel for merge ───────────────────────────
panel_2022 = panel[panel['SurveyYear']==2022].copy()
panel_2022['Region_std'] = panel_2022['Region'].map(reg_map)

cei_df['Region_std'] = cei_df['Region'].map(reg_map).fillna(cei_df['Region'])
risk_2022 = panel_2022[['Region_std','RiskZone']].drop_duplicates()

# ── FIGURE STYLE CONSTANTS ────────────────────────────────────────────────
def set_ghana_style():
 plt.rcParams.update({
 'font.family':'DejaVu Serif','font.size':10,
 'axes.spines.top':False,'axes.spines.right':False,
 'figure.facecolor':'white','axes.facecolor':'white',
 })

TITLE_FONT = dict(fontsize=13, fontweight='bold', color=GH_BLACK, fontfamily='DejaVu Serif')
LABEL_FONT = dict(fontsize=9, color='#333333')

def add_ghana_fig_border(fig):
 """Add subtle Ghana-flag-color bar at top"""
 fig.patches.append(mpatches.FancyBboxPatch(
 (0,0.985), 1, 0.015, transform=fig.transFigure,
 facecolor=GH_GREEN, edgecolor='none', zorder=10))

def draw_map_base(ax, gdf, facecolor='#f0f0f0', edgecolor='white', lw=0.8):
 gdf.plot(ax=ax, facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
 ax.set_axis_off()
 # Add north arrow
 ax.annotate('N', xy=(0.95, 0.92), xycoords='axes fraction',
 fontsize=11, fontweight='bold', ha='center', va='center',
 color='#333333')
 ax.annotate('▲', xy=(0.95, 0.96), xycoords='axes fraction',
 fontsize=9, ha='center', va='center', color='#333333')
 # Scale bar placeholder
 ax.plot([0.05, 0.25], [0.03, 0.03], transform=ax.transAxes,
 color='#555', lw=2)
 ax.text(0.15, 0.06, '~200 km', transform=ax.transAxes,
 ha='center', fontsize=7, color='#555')

def add_region_labels(ax, gdf, col='Region', fontsize=6.5, color='#111'):
 for _, row in gdf.iterrows():
  if row.geometry is None or row.geometry.is_empty: continue
  c = row.geometry.centroid
  name = str(row[col])
 # Abbreviate long names
  abbrevs = {
  'Greater Accra':'Gr. Accra','Upper East':'Upper\nEast',
  'Upper West':'Upper\nWest','Western North':'W. North',
  'North East':'N. East','Bono East':'Bono E.',
  }
  name = abbrevs.get(name, name)
  ax.text(c.x, c.y, name, fontsize=fontsize, ha='center', va='center',
  color=color, fontweight='normal',
  bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
  alpha=0.6, edgecolor='none'))

# ══════════════════════════════════════════════════════════════════════════
# FIGURE C1 — ANC Coverage 2022 Choropleth
# ══════════════════════════════════════════════════════════════════════════
set_ghana_style()
gdf_anc = gdf_base.merge(panel_2022[['Region_std','Antenatal care from a skilled provider']],
 left_on='Region', right_on='Region_std', how='left')
gdf_anc.rename(columns={'Antenatal care from a skilled provider':'ANC'}, inplace=True)

fig, ax = plt.subplots(1,1, figsize=(8,9))
fig.patch.set_facecolor('white')

# Custom colormap: red → gold → green
cmap_anc = LinearSegmentedColormap.from_list('ghana_anc',
 ['#CE1126','#FCD116','#006B3F'], N=256)

gdf_anc_valid = gdf_anc[gdf_anc['ANC'].notna()]
gdf_anc_na = gdf_anc[gdf_anc['ANC'].isna()]

vmin, vmax = 80, 100
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
gdf_anc_valid.plot(ax=ax, column='ANC', cmap=cmap_anc, norm=norm,
 edgecolor='white', linewidth=1.0)
if len(gdf_anc_na):
 gdf_anc_na.plot(ax=ax, facecolor='#cccccc', edgecolor='white', linewidth=1.0)

# Colorbar
sm = cm.ScalarMappable(cmap=cmap_anc, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02, aspect=30)
cbar.set_label('ANC Coverage (%)', fontsize=10, labelpad=8)
cbar.ax.tick_params(labelsize=9)

add_region_labels(ax, gdf_anc)
draw_map_base(ax, gdf_anc, facecolor='none')
ax.set_title('Figure C1: Skilled Antenatal Care Coverage by Region, Ghana 2022',
 **TITLE_FONT, pad=14)
ax.text(0.5,-0.02,'Source: Ghana DHS 2022 (Subnational). Survey-weighted estimates.',
 transform=ax.transAxes, ha='center', fontsize=8, color='#666')

plt.tight_layout()
plt.savefig(OUT+'06_figure_C1_anc_choropleth_2022.png', dpi=300,
 bbox_inches='tight', facecolor='white')
plt.close()
print("Saved C1 ANC choropleth")

# ══════════════════════════════════════════════════════════════════════════
# FIGURE C2 — TFR 2022 Choropleth
# ══════════════════════════════════════════════════════════════════════════
gdf_tfr = gdf_base.merge(panel_2022[['Region_std','Total fertility rate 15-49']],
 left_on='Region', right_on='Region_std', how='left')
gdf_tfr.rename(columns={'Total fertility rate 15-49':'TFR'}, inplace=True)

fig, ax = plt.subplots(1,1, figsize=(8,9))
fig.patch.set_facecolor('white')
cmap_tfr = LinearSegmentedColormap.from_list('ghana_tfr',
 ['#006B3F','#FCD116','#CE1126'], N=256)

vmin_t, vmax_t = 2.5, 7.0
norm_t = mcolors.Normalize(vmin=vmin_t, vmax=vmax_t)
gdf_tfr_v = gdf_tfr[gdf_tfr['TFR'].notna()]
gdf_tfr_v.plot(ax=ax, column='TFR', cmap=cmap_tfr, norm=norm_t,
 edgecolor='white', linewidth=1.0)
gdf_tfr[gdf_tfr['TFR'].isna()].plot(ax=ax, facecolor='#cccccc',
 edgecolor='white', linewidth=1.0)

sm2 = cm.ScalarMappable(cmap=cmap_tfr, norm=norm_t)
sm2.set_array([])
cbar2 = fig.colorbar(sm2, ax=ax, fraction=0.035, pad=0.02, aspect=30)
cbar2.set_label('Total Fertility Rate (births/woman)', fontsize=10, labelpad=8)
cbar2.ax.tick_params(labelsize=9)

add_region_labels(ax, gdf_tfr)
draw_map_base(ax, gdf_tfr, facecolor='none')
ax.set_title('Figure C2: Total Fertility Rate by Region, Ghana 2022',
 **TITLE_FONT, pad=14)
ax.text(0.5,-0.02,'Source: Ghana DHS 2022 (Subnational). Survey-weighted estimates.',
 transform=ax.transAxes, ha='center', fontsize=8, color='#666')

plt.tight_layout()
plt.savefig(OUT+'06_figure_C2_tfr_choropleth_2022.png', dpi=300,
 bbox_inches='tight', facecolor='white')
plt.close()
print("Saved C2 TFR choropleth")

# ══════════════════════════════════════════════════════════════════════════
# FIGURE C3 — Care Efficiency Index Choropleth
# ══════════════════════════════════════════════════════════════════════════
gdf_cei = gdf_base.merge(cei_df[['Region_std','Care_Efficiency_Index']],
 left_on='Region', right_on='Region_std', how='left')

fig, ax = plt.subplots(1,1, figsize=(8,9))
fig.patch.set_facecolor('white')
cmap_cei = LinearSegmentedColormap.from_list('ghana_cei',
 ['#CE1126','#FCD116','#006B3F'], N=256)

vmin_c, vmax_c = 14, 33
norm_c = mcolors.Normalize(vmin=vmin_c, vmax=vmax_c)
gdf_cei[gdf_cei['Care_Efficiency_Index'].notna()].plot(
 ax=ax, column='Care_Efficiency_Index', cmap=cmap_cei, norm=norm_c,
 edgecolor='white', linewidth=1.0)
gdf_cei[gdf_cei['Care_Efficiency_Index'].isna()].plot(
 ax=ax, facecolor='#cccccc', edgecolor='white', linewidth=1.0)

sm3 = cm.ScalarMappable(cmap=cmap_cei, norm=norm_c)
sm3.set_array([])
cbar3 = fig.colorbar(sm3, ax=ax, fraction=0.035, pad=0.02, aspect=30)
cbar3.set_label('Care Efficiency Index (ANC% ÷ TFR)', fontsize=10, labelpad=8)
cbar3.ax.tick_params(labelsize=9)

add_region_labels(ax, gdf_cei)
draw_map_base(ax, gdf_cei, facecolor='none')
ax.set_title('Figure C3: Care Efficiency Index by Region, Ghana (Pooled Avg.)',
 **TITLE_FONT, pad=14)
ax.text(0.5,-0.02,'CEI = Skilled ANC Coverage (%) ÷ Total Fertility Rate. Higher = more efficient.',
 transform=ax.transAxes, ha='center', fontsize=8, color='#666')

plt.tight_layout()
plt.savefig(OUT+'06_figure_C3_cei_choropleth.png', dpi=300,
 bbox_inches='tight', facecolor='white')
plt.close()
print("Saved C3 CEI choropleth")

# ══════════════════════════════════════════════════════════════════════════
# FIGURE C4 — Risk Zone Choropleth 2022
# ══════════════════════════════════════════════════════════════════════════
gdf_risk = gdf_base.merge(risk_2022, left_on='Region', right_on='Region_std', how='left')
ZONE_COLORS = {
 'Critical':'#CE1126','Emerging':'#FCD116',
 'Workhorse':'#4a90d9','Resilient':'#006B3F'
}

fig, ax = plt.subplots(1,1, figsize=(8,9))
fig.patch.set_facecolor('white')

for zone, color in ZONE_COLORS.items():
 sub = gdf_risk[gdf_risk['RiskZone']==zone]
 if len(sub):
  sub.plot(ax=ax, facecolor=color, edgecolor='white', linewidth=1.0, alpha=0.88)
gdf_risk[gdf_risk['RiskZone'].isna()].plot(ax=ax, facecolor='#cccccc',
 edgecolor='white', linewidth=1.0)

legend_patches = [Patch(facecolor=c, label=z, alpha=0.88, edgecolor='white')
 for z,c in ZONE_COLORS.items()]
legend_patches.append(Patch(facecolor='#cccccc', label='No data'))
ax.legend(handles=legend_patches, loc='lower left', fontsize=9,
 title='Risk Zone', title_fontsize=9, framealpha=0.9,
 edgecolor='#ccc')

add_region_labels(ax, gdf_risk, color='#000')
draw_map_base(ax, gdf_risk, facecolor='none')
ax.set_title('Figure C4: ANC–Fertility Risk Zone Classification by Region, Ghana 2022',
 **TITLE_FONT, pad=14)
ax.text(0.5,-0.02,
 'Critical: Low ANC + High TFR | Resilient: High ANC + Low TFR\n'
 'Workhorse: High ANC + High TFR | Emerging: Low ANC + Low TFR',
 transform=ax.transAxes, ha='center', fontsize=8, color='#555')

plt.tight_layout()
plt.savefig(OUT+'06_figure_C4_risk_zone_choropleth.png', dpi=300,
 bbox_inches='tight', facecolor='white')
plt.close()
print("Saved C4 Risk Zone choropleth")

# ══════════════════════════════════════════════════════════════════════════
# FIGURE C5 — ANC Longitudinal Small Multiples (faceted choropleth)
# ══════════════════════════════════════════════════════════════════════════
years = sorted(panel['SurveyYear'].unique())
n_years = len(years)
ncols = 3; nrows = 3

fig, axes = plt.subplots(nrows, ncols, figsize=(15, 16))
fig.patch.set_facecolor('white')
fig.suptitle('Figure C5: Skilled ANC Coverage by Region — Ghana 1988–2022\n(Spatial Temporal Evolution)',
 fontsize=13, fontweight='bold', y=0.99, color=GH_BLACK)

cmap_t = LinearSegmentedColormap.from_list('ghana_anc',
 ['#CE1126','#FCD116','#006B3F'], N=256)
norm_global = mcolors.Normalize(vmin=40, vmax=100)

for idx, yr in enumerate(years):
 row_i, col_i = divmod(idx, ncols)
 ax = axes[row_i][col_i]
 
 yr_data = panel[panel['SurveyYear']==yr].copy()
 yr_data['Region_std'] = yr_data['Region'].map(reg_map)
 
 gdf_yr = gdf_base.merge(yr_data[['Region_std','Antenatal care from a skilled provider']],
 left_on='Region', right_on='Region_std', how='left')
 gdf_yr.rename(columns={'Antenatal care from a skilled provider':'ANC'}, inplace=True)
 
 gdf_yr[gdf_yr['ANC'].notna()].plot(ax=ax, column='ANC', cmap=cmap_t,
 norm=norm_global,
 edgecolor='white', linewidth=0.5)
 gdf_yr[gdf_yr['ANC'].isna()].plot(ax=ax, facecolor='#dddddd',
 edgecolor='white', linewidth=0.5)
 ax.set_title(str(yr), fontsize=10, fontweight='bold', pad=4)
 ax.set_axis_off()

# Remove empty subplot
if n_years < nrows*ncols:
 for extra in range(n_years, nrows*ncols):
  r,c = divmod(extra, ncols)
  axes[r][c].set_visible(False)

# Shared colorbar
sm5 = cm.ScalarMappable(cmap=cmap_t, norm=norm_global)
sm5.set_array([])
cbar5 = fig.colorbar(sm5, ax=axes, fraction=0.015, pad=0.02, aspect=50)
cbar5.set_label('Skilled ANC Coverage (%)', fontsize=10)
cbar5.ax.tick_params(labelsize=8)

plt.tight_layout(rect=[0,0,0.95,0.98])
plt.savefig(OUT+'06_figure_C5_anc_temporal_choropleth.png', dpi=300,
 bbox_inches='tight', facecolor='white')
plt.close()
print("Saved C5 temporal choropleth")

print("\nAll choropleth figures saved.")
