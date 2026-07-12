"""
Fix legibility issues in Figures 2, 7, 8, 12:
 - Figure 2: faint legend, axis labels, caption
 - Figure 7: x-axis label overlaps footer caption
 - Figure 8: caption not legible
 - Figure 12: x-axis label overlaps footer caption
"""
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings; warnings.filterwarnings('ignore')

OUT = '/sessions/beautiful-gallant-pascal/analysis_outputs/'
GH_GREEN='#006B3F'; GH_RED='#CE1126'; GH_GOLD='#FCD116'
GH_BLUE='#2563EB'; GH_BLACK='#000000'

# ── Shared style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
 'font.family':'DejaVu Serif',
 'font.size':11,
 'axes.spines.top':False,
 'axes.spines.right':False,
 'figure.facecolor':'white',
 'axes.facecolor':'#fafafa',
 'axes.grid':True,
 'grid.color':'#e0e0e0',
 'grid.linewidth':0.6,
})

TITLE_KW = dict(fontsize=13, fontweight='bold', color=GH_BLACK, pad=14)

def style_ax(ax, title='', xlabel='', ylabel=''):
 ax.set_title(title, **TITLE_KW)
 if xlabel: ax.set_xlabel(xlabel, fontsize=11, fontweight='semibold', color='#111', labelpad=8)
 if ylabel: ax.set_ylabel(ylabel, fontsize=11, fontweight='semibold', color='#111', labelpad=8)
 ax.tick_params(labelsize=10, colors='#222')

def footer(ax, txt, y=-0.13):
 """Caption placed further below axes to avoid x-label overlap."""
 ax.text(0.5, y, txt, transform=ax.transAxes,
 ha='center', fontsize=9, color='#444', style='italic',
 wrap=True)

# ── Load data ─────────────────────────────────────────────────────────────────
panel = pd.read_csv(OUT+'01_regional_health_panel.csv')
morans = pd.read_csv(OUT+'04_temporal_morans_i.csv')

reg_map = {'..Northeast':'North East','Ahafo':'Ahafo','Ashanti':'Ashanti',
 'Bono':'Bono','Central':'Central','Eastern':'Eastern','Greater Accra':'Greater Accra',
 'Northern':'Northern','Oti':'Oti','Savannah':'Savannah','Upper East':'Upper East',
 'Upper West':'Upper West','Volta':'Volta','Western':'Western',
 'Bono East':'Bono','Western North':'Western'}
panel['Region_std'] = panel['Region'].map(reg_map).fillna(panel['Region'])

north_regions = ['Northern','Upper East','Upper West','North East','Savannah']
south_regions = ['Greater Accra','Central','Western','Eastern']
mid_regions = ['Ashanti','Ahafo','Bono']

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — ANC Trajectories (fix: faint text, legend, caption)
# ══════════════════════════════════════════════════════════════════════════════
try:
 national = pd.read_csv(OUT+'03_national_statistics_clean.csv')
 fig, ax = plt.subplots(figsize=(12,6.5)); fig.patch.set_facecolor('white')
 ax.set_facecolor('#fafafa')

 for reg in panel['Region_std'].unique():
  sub = panel[panel['Region_std']==reg].sort_values('SurveyYear')
  if reg in north_regions: c, lw, ls, alpha = GH_RED, 2.0, '-', 0.80
  elif reg in south_regions: c, lw, ls, alpha = GH_GREEN, 2.0, '-', 0.80
  else: c, lw, ls, alpha = GH_GOLD, 2.0, '--', 0.80
  ax.plot(sub['SurveyYear'],
  sub['Antenatal care from a skilled provider'],
  color=c, linewidth=lw, linestyle=ls, alpha=alpha)

 # National mean overlay
  nat = national.sort_values('SurveyYear')
  ax.plot(nat['SurveyYear'], nat['Mean_ANC'], 'k-o',
  linewidth=3.0, markersize=8, label='National Mean', zorder=6)

  patches = [
  mpatches.Patch(color=GH_RED, label='Northern Belt'),
  mpatches.Patch(color=GH_GREEN, label='Southern Belt'),
  mpatches.Patch(color=GH_GOLD, label='Middle Belt'),
  mpatches.Patch(color='black', label='National Mean'),
  ]
  leg = ax.legend(handles=patches, fontsize=10.5, framealpha=0.95,
  edgecolor='#bbb', loc='lower right',
  title='Geographic Belt', title_fontsize=10)
  leg.get_title().set_fontweight('bold')

  ax.set_xticks(sorted(panel['SurveyYear'].unique()))
  ax.tick_params(axis='x', rotation=30)
  style_ax(ax,
  "Figure 2: Skilled ANC Coverage Trajectories by Region, Ghana 1988–2022",
  "Survey Year", "Skilled ANC Coverage (%)")
  ax.set_ylim(30, 105)
  ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v:.0f}%'))

 # Legible footer — extra bottom space prevents overlap
  fig.subplots_adjust(bottom=0.15)
  footer(ax, "Source: Ghana DHS 1988–2022 (Subnational, Preferred Estimates). "
  "Belt classification: Northern = Upper East/West, North East, Northern, Savannah; "
  "Southern = Greater Accra, Central, Western, Eastern; Middle = remaining regions.",
  y=-0.14)
  plt.savefig(OUT+'06_figure_02_anc_trajectories.png', dpi=300,
  bbox_inches='tight', facecolor='white')
  plt.close()
  print("✓ Figure 2 saved")
except Exception as e:
 print(f"✗ Figure 2: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 7 — Moran's I Temporal Trend (fix: x-label / caption overlap)
# ══════════════════════════════════════════════════════════════════════════════
try:
 fig, ax = plt.subplots(figsize=(10,5.5)); fig.patch.set_facecolor('white')
 ax.set_facecolor('#fafafa')

 ax.plot(morans['SurveyYear'], morans['Moran_I_ANC'], 'o-', color=GH_GREEN,
 linewidth=2.5, markersize=8, label="Moran's I (ANC)", zorder=5)
 ax.plot(morans['SurveyYear'], morans['Moran_I_TFR'], 's--', color=GH_RED,
 linewidth=2.5, markersize=8, label="Moran's I (TFR)", zorder=5)
 ax.axhline(0, color='#999', linewidth=1.2, linestyle=':')

 # Shade statistically significant years
 for _, r in morans.iterrows():
  if r['p_ANC'] < 0.05:
   ax.axvspan(r['SurveyYear']-1, r['SurveyYear']+1,
   alpha=0.09, color=GH_GREEN, zorder=1)
   if r['p_TFR'] < 0.05:
    ax.axvspan(r['SurveyYear']-1, r['SurveyYear']+1,
    alpha=0.09, color=GH_RED, zorder=1)

    leg = ax.legend(fontsize=10.5, framealpha=0.95, edgecolor='#bbb')
    ax.set_xticks(morans['SurveyYear'])
    ax.tick_params(axis='x', rotation=30)
    style_ax(ax,
    "Figure 7: Temporal Evolution of Spatial Autocorrelation (Moran's I), Ghana 1988–2022",
    "Survey Year", "Moran's I Statistic")

 # Extra bottom space so caption sits below x-axis label without touching
    fig.subplots_adjust(bottom=0.20)
    footer(ax,
    "Shaded bands = statistically significant year (p<0.05). "
    "Rook contiguity weights. Permutation inference (999 permutations).",
    y=-0.16)

    plt.savefig(OUT+'06_figure_07_morans_temporal.png', dpi=300,
    bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Figure 7 saved")
except Exception as e:
 print(f"✗ Figure 7: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 8 — Risk Stratification Scatter (fix: caption not legible)
# ══════════════════════════════════════════════════════════════════════════════
try:
 panel_r = panel.dropna(subset=['Antenatal care from a skilled provider',
 'Total fertility rate 15-49'])
 panel_r = panel_r.copy()
 anc_mean = panel_r['Antenatal care from a skilled provider'].mean()
 tfr_mean = panel_r['Total fertility rate 15-49'].mean()
 panel_r['anc_z'] = (panel_r['Antenatal care from a skilled provider'] - anc_mean) / \
 panel_r['Antenatal care from a skilled provider'].std()
 panel_r['tfr_z'] = (panel_r['Total fertility rate 15-49'] - tfr_mean) / \
 panel_r['Total fertility rate 15-49'].std()

 def risk_zone(row):
  if row['anc_z'] < 0 and row['tfr_z'] > 0: return 'Critical'
  elif row['anc_z'] < 0 and row['tfr_z'] <= 0: return 'Emerging'
  elif row['anc_z'] >= 0 and row['tfr_z'] > 0: return 'Workhorse'
  else: return 'Resilient'
  panel_r['RiskZone'] = panel_r.apply(risk_zone, axis=1)

  ZONE_C = {'Critical':GH_RED,'Emerging':'#b8860b','Workhorse':GH_BLUE,'Resilient':GH_GREEN}

  fig, ax = plt.subplots(figsize=(10,8)); fig.patch.set_facecolor('white')
  ax.set_facecolor('#fafafa')

  for zone, color in ZONE_C.items():
   sub = panel_r[panel_r['RiskZone']==zone]
   ax.scatter(sub['Total fertility rate 15-49'],
   sub['Antenatal care from a skilled provider'],
   c=color, alpha=0.75, s=80, label=zone,
   edgecolors='white', linewidths=0.6, zorder=5)

   ax.axvline(tfr_mean, color='#888', lw=1.5, ls='--', alpha=0.9)
   ax.axhline(anc_mean, color='#888', lw=1.5, ls='--', alpha=0.9)

 # Quadrant labels — use offset text boxes
   offset = 0.3
   for (x, y, txt, col) in [
    (6.5, 68, 'Critical\n(Low ANC / High TFR)', GH_RED),
    (2.5, 68, 'Emerging\n(Low ANC / Low TFR)', '#b8860b'),
    (6.5, 99.5, 'Workhorse\n(High ANC / High TFR)', GH_BLUE),
    (2.5, 99.5, 'Resilient\n(High ANC / Low TFR)', GH_GREEN),
    ]:
    ax.text(x, y, txt, fontsize=9, color=col, ha='center', va='top',
    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
    edgecolor=col, alpha=0.85, linewidth=0.8))

    leg = ax.legend(fontsize=10.5, framealpha=0.95, edgecolor='#bbb',
    title='Risk Zone', title_fontsize=10, loc='lower left')
    leg.get_title().set_fontweight('bold')

    style_ax(ax,
    "Figure 8: ANC–TFR Bivariate Risk Stratification, Ghana 1988–2022",
    "Total Fertility Rate", "Skilled ANC Coverage (%)")

 # Legible caption below: larger font, dark colour, explicit padding
    fig.subplots_adjust(bottom=0.14)
    footer(ax,
    "Dashed lines = national means (ANC: {:.1f}%; TFR: {:.2f}). "
    "Zone classification based on z-score quadrant method.".format(anc_mean, tfr_mean),
    y=-0.11)

    plt.savefig(OUT+'06_figure_08_risk_stratification_dashboard.png', dpi=300,
    bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Figure 8 saved")
except Exception as e:
 print(f"✗ Figure 8: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 12 — Partial Dependence of ANC on TFR (fix: x-label / caption overlap)
# ══════════════════════════════════════════════════════════════════════════════
try:
 panel_ml = panel.dropna(subset=[
 'Antenatal care from a skilled provider',
 'Total fertility rate 15-49',
 'Age specific fertility rate: 15-19']).copy()
 north_regs2 = ['Northern','Upper East','Upper West','North East','Savannah']
 south_regs2 = ['Greater Accra','Central','Western','Eastern']
 panel_ml['Zone'] = panel_ml['Region'].apply(
 lambda x: 0 if x in north_regs2 else 2 if x in south_regs2 else 1)

 X = panel_ml[['Total fertility rate 15-49','SurveyYear','Zone',
 'Age specific fertility rate: 15-19']].values
 y = panel_ml['Antenatal care from a skilled provider'].values
 Xtr,Xte,ytr,yte = train_test_split(X, y, test_size=0.2, random_state=42)
 rf = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=6)
 rf.fit(Xtr, ytr)

 tfr_range = np.linspace(panel_ml['Total fertility rate 15-49'].min(),
 panel_ml['Total fertility rate 15-49'].max(), 100)
 X_pd = np.tile(X.mean(axis=0), (100,1))
 X_pd[:,0] = tfr_range
 pdp_vals = rf.predict(X_pd)
 crit_tfr = tfr_range[np.gradient(pdp_vals).argmin()]

 fig, ax = plt.subplots(figsize=(10,5.5)); fig.patch.set_facecolor('white')
 ax.set_facecolor('#fafafa')
 ax.plot(tfr_range, pdp_vals, color=GH_GREEN, lw=2.8, label='Partial Dependence (RF)')
 ax.fill_between(tfr_range, pdp_vals, alpha=0.12, color=GH_GREEN)
 ax.axvline(crit_tfr, color=GH_RED, lw=2, linestyle='--',
 label=f'Critical TFR ≈ {crit_tfr:.2f}')
 ax.axhline(pdp_vals[tfr_range<=crit_tfr].mean(), color=GH_GOLD, lw=1.5, ls=':')

 leg = ax.legend(fontsize=10.5, framealpha=0.95, edgecolor='#bbb')
 ax.set_xticks(np.arange(int(tfr_range.min()), int(tfr_range.max())+1, 1))
 style_ax(ax,
 "Figure 12: Partial Dependence of Skilled ANC on TFR (Random Forest)",
 "Total Fertility Rate", "Predicted Skilled ANC Coverage (%)")

 # Extra bottom space prevents x-label / caption collision
 fig.subplots_adjust(bottom=0.20)
 footer(ax,
 f"Random Forest (200 trees, max depth 6). "
 f"Critical TFR threshold = {crit_tfr:.2f} "
 f"(maximum gradient change in predicted ANC). "
 f"All other features held at sample mean.",
 y=-0.16)

 plt.savefig(OUT+'06_figure_12_partial_dependence_tfr.png', dpi=300,
 bbox_inches='tight', facecolor='white')
 plt.close()
 print(f"✓ Figure 12 saved (critical TFR = {crit_tfr:.2f})")
except Exception as e:
 print(f"✗ Figure 12: {e}")

print("\nAll legibility fixes complete.")
