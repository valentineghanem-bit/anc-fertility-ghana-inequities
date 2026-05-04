"""
Ghana ANC Fertility Spatial Analysis — Interactive Dashboard (Dash/Plotly)
===========================================================================
Companion to: "Temporal and Spatial Dynamics of Antenatal Care Coverage and
Fertility Inequities in Ghana: A Subnational Ecological Study (1988–2022)"

Author : V. Ghanem
Data : Ghana DHS subnational 1988–2022; Ghana Master Sheet (population/socioeconomic)
Run : python app.py (opens at http://127.0.0.1:8050)
Requires: pip install dash dash-bootstrap-components plotly pandas numpy scipy
 pip install geopandas libpysal esda scikit-learn matplotlib
"""

import os, json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, '..', 'outputs', 'data',
 'Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv')

try:
 df = pd.read_csv(DATA_PATH)
 df['SurveyYear'] = df['SurveyYear'].astype(int)
except FileNotFoundError:
 # Fallback: generate synthetic data matching the published values
 # (used only if the CSV is not present; see outputs/data/ directory)
 raise SystemExit(
 f"Dataset not found at:\n {DATA_PATH}\n"
 "Please copy Ghana_ANC_Fertility_Analysis_Dataset_FINAL.csv into "
 "outputs/data/ and restart."
 )

YEARS = sorted(df['SurveyYear'].unique())
REGIONS = sorted(df['Region'].unique())

GEO_JSON_PATH = os.path.join(BASE, '..', 'outputs', 'data', 'ghana_regions.geojson')
GEOJSON = None
if os.path.exists(GEO_JSON_PATH):
 with open(GEO_JSON_PATH) as f:
 GEOJSON = json.load(f)

# Ghana flag colours
GH_GREEN = '#006B3F'
GH_RED = '#CE1126'
GH_GOLD = '#FCD116'
GH_BLACK = '#111111'
ZONE_COLORS = {
 'Northern Belt': '#CE1126',
 'Middle Belt': '#FCD116',
 'Southern Belt': GH_GREEN,
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. HELPER — reusable figure layout
# ─────────────────────────────────────────────────────────────────────────────
def base_layout(title='', xtitle='', ytitle='', height=420):
 return dict(
 title=dict(text=title, font=dict(size=13, color=GH_BLACK, family='Arial'),
 x=0.5, xanchor='center'),
 xaxis=dict(title=xtitle, gridcolor='#e5e5e5', linecolor='#ccc'),
 yaxis=dict(title=ytitle, gridcolor='#e5e5e5', linecolor='#ccc'),
 plot_bgcolor='white', paper_bgcolor='white',
 font=dict(family='Arial', size=11, color=GH_BLACK),
 margin=dict(t=50, b=50, l=60, r=20),
 height=height,
 legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#ccc', borderwidth=1),
 )


# ─────────────────────────────────────────────────────────────────────────────
# 3. FIGURE BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def fig_anc_trajectories(selected_regions=None):
 """Fig 2 – ANC coverage trajectories by region and belt."""
 d = df.dropna(subset=['Skilled_ANC_pct'])
 if selected_regions:
 d = d[d['Region'].isin(selected_regions)]
 fig = go.Figure()
 for region, grp in d.groupby('Region'):
 grp = grp.sort_values('SurveyYear')
 zone = grp['Geographic_Zone'].iloc[0]
 fig.add_trace(go.Scatter(
 x=grp['SurveyYear'], y=grp['Skilled_ANC_pct'],
 mode='lines+markers', name=region,
 line=dict(color=ZONE_COLORS.get(zone, '#888'), width=1.5),
 marker=dict(size=6),
 hovertemplate=f'<b>{region}</b><br>Year: %{{x}}<br>ANC: %{{y:.1f}}%<extra></extra>',
 ))
 # National mean
 nat = d.groupby('SurveyYear')['Skilled_ANC_pct'].mean().reset_index()
 fig.add_trace(go.Scatter(
 x=nat['SurveyYear'], y=nat['Skilled_ANC_pct'],
 mode='lines+markers', name='National Mean',
 line=dict(color=GH_BLACK, width=3, dash='dash'),
 marker=dict(size=8, symbol='diamond'),
 hovertemplate='National Mean<br>Year: %{x}<br>ANC: %{y:.1f}%<extra></extra>',
 ))
 fig.update_layout(**base_layout(
 title='Figure 2. Skilled ANC Coverage Trajectories by Region (1988–2022)',
 xtitle='Survey Year', ytitle='Skilled ANC Coverage (%)'
 ))
 fig.update_yaxes(range=[30, 105])
 return fig


def fig_tfr_anc_scatter(year=2022):
 """Fig 3 – TFR vs ANC scatter for selected year."""
 d = df[df['SurveyYear'] == year].dropna(subset=['TFR', 'Skilled_ANC_pct'])
 fig = px.scatter(
 d, x='TFR', y='Skilled_ANC_pct', text='Region',
 color='Geographic_Zone',
 color_discrete_map=ZONE_COLORS,
 size_max=14,
 labels={'TFR': 'Total Fertility Rate', 'Skilled_ANC_pct': 'Skilled ANC (%)'},
 title=f'Figure 3. TFR vs Skilled ANC Coverage — {year}',
 )
 fig.update_traces(textposition='top center', marker=dict(size=10))
 fig.update_layout(**base_layout(
 title=f'Figure 3. TFR vs Skilled ANC Coverage — {year}',
 xtitle='Total Fertility Rate',
 ytitle='Skilled ANC Coverage (%)'
 ))
 return fig


def fig_gini_trend():
 """Fig 11 – Gini coefficient over time."""
 gini_by_year = []
 for yr, grp in df.groupby('SurveyYear'):
 vals = grp['Skilled_ANC_pct'].dropna().values
 if len(vals) < 2:
 continue
 vals = np.sort(vals)
 n = len(vals)
 idx = np.arange(1, n + 1)
 g = (2 * (idx * vals).sum() / (n * vals.sum())) - (n + 1) / n
 gini_by_year.append({'SurveyYear': yr, 'Gini': round(g, 4)})
 gdf = pd.DataFrame(gini_by_year)
 fig = go.Figure()
 fig.add_trace(go.Bar(
 x=gdf['SurveyYear'], y=gdf['Gini'],
 marker_color=GH_GREEN, opacity=0.8,
 hovertemplate='Year: %{x}<br>Gini: %{y:.4f}<extra></extra>',
 ))
 fig.update_layout(**base_layout(
 title='Figure 11. Inter-Regional Gini Coefficient of ANC Coverage (1988–2022)',
 xtitle='Survey Year', ytitle='Gini Coefficient'
 ))
 return fig


def fig_morans_temporal():
 """Fig 7 – Temporal Moran's I for ANC and TFR."""
 morans_cols = ['SurveyYear', 'Moran_I_ANC', 'p_ANC', 'Moran_I_TFR', 'p_TFR']
 m = df[morans_cols].drop_duplicates().sort_values('SurveyYear')
 fig = go.Figure()
 # ANC
 fig.add_trace(go.Scatter(
 x=m['SurveyYear'], y=m['Moran_I_ANC'],
 mode='lines+markers', name="Moran's I (ANC)",
 line=dict(color=GH_GREEN, width=2),
 marker=dict(
 size=10, color=GH_GREEN,
 symbol=['circle' if p < 0.05 else 'circle-open' for p in m['p_ANC']],
 ),
 hovertemplate='Year: %{x}<br>Moran I (ANC): %{y:.3f}<extra></extra>',
 ))
 # TFR
 fig.add_trace(go.Scatter(
 x=m['SurveyYear'], y=m['Moran_I_TFR'],
 mode='lines+markers', name="Moran's I (TFR)",
 line=dict(color=GH_RED, width=2),
 marker=dict(
 size=10, color=GH_RED,
 symbol=['circle' if p < 0.05 else 'circle-open' for p in m['p_TFR']],
 ),
 hovertemplate='Year: %{x}<br>Moran I (TFR): %{y:.3f}<extra></extra>',
 ))
 fig.add_hline(y=0, line_dash='dash', line_color='#999', line_width=1)
 fig.update_layout(**base_layout(
 title="Figure 7. Temporal Evolution of Moran's I (ANC & TFR) — Ghana 1988–2022",
 xtitle='Survey Year', ytitle="Moran's I"
 ))
 return fig


def fig_north_south_gap():
 """Fig 9 – North–South ANC gap over time."""
 NORTH = ['North East', 'Northern', 'Savannah', 'Upper East', 'Upper West', 'Oti']
 SOUTH = ['Greater Accra', 'Central', 'Eastern', 'Western', 'Volta']
 gap_rows = []
 for yr, grp in df.groupby('SurveyYear'):
 n = grp[grp['Region'].isin(NORTH)]['Skilled_ANC_pct'].mean()
 s = grp[grp['Region'].isin(SOUTH)]['Skilled_ANC_pct'].mean()
 gap_rows.append({'SurveyYear': yr, 'Northern': n, 'Southern': s, 'Gap': s - n})
 gdf = pd.DataFrame(gap_rows)
 fig = go.Figure()
 fig.add_trace(go.Scatter(x=gdf['SurveyYear'], y=gdf['Southern'],
 mode='lines+markers', name='Southern Belt',
 line=dict(color=GH_GREEN, width=2)))
 fig.add_trace(go.Scatter(x=gdf['SurveyYear'], y=gdf['Northern'],
 mode='lines+markers', name='Northern Belt',
 line=dict(color=GH_RED, width=2)))
 fig.add_trace(go.Bar(x=gdf['SurveyYear'], y=gdf['Gap'],
 name='N–S Gap', marker_color='rgba(252,209,22,0.5)',
 yaxis='y2'))
 fig.update_layout(
 **base_layout(title='Figure 9. North–South ANC Gap Over Time',
 xtitle='Survey Year', ytitle='Mean Skilled ANC (%)'),
 yaxis2=dict(title='Gap (pp)', overlaying='y', side='right',
 showgrid=False, range=[0, 50]),
 )
 return fig


def fig_cei_bar():
 """Fig — CEI by region pooled average."""
 d = df.groupby('Region').agg(
 Skilled_ANC_pct=('Skilled_ANC_pct', 'mean'),
 TFR=('TFR', 'mean'),
 Care_Efficiency_Index=('Care_Efficiency_Index', 'mean'),
 Geographic_Zone=('Geographic_Zone', 'first'),
 ).reset_index().sort_values('Care_Efficiency_Index', ascending=True)
 fig = go.Figure(go.Bar(
 x=d['Care_Efficiency_Index'], y=d['Region'],
 orientation='h',
 marker_color=[ZONE_COLORS.get(z, '#888') for z in d['Geographic_Zone']],
 hovertemplate='<b>%{y}</b><br>CEI: %{x:.2f}<extra></extra>',
 ))
 fig.update_layout(**base_layout(
 title='Care Efficiency Index (CEI = ANC% / TFR) by Region — Pooled Average',
 xtitle='Care Efficiency Index', ytitle='', height=500
 ))
 return fig


def fig_risk_zone_pie():
 """Risk zone distribution pie chart."""
 d = df.dropna(subset=['Risk_Zone']).groupby('Risk_Zone').size().reset_index(name='Count')
 RISK_COLORS = {'Critical': GH_RED, 'Emerging': '#b8860b',
 'Workhorse': '#2563EB', 'Resilient': GH_GREEN}
 fig = px.pie(d, names='Risk_Zone', values='Count',
 color='Risk_Zone', color_discrete_map=RISK_COLORS,
 title='Risk Zone Distribution (n=90 region-year observations)')
 fig.update_traces(textposition='inside', textinfo='percent+label',
 hovertemplate='<b>%{label}</b><br>N: %{value}<br>%{percent}<extra></extra>')
 fig.update_layout(**base_layout(
 title='Risk Zone Distribution (n=90 region-year observations)', height=380))
 return fig


def fig_adol_fertility():
 """Fig 10 – Adolescent fertility rate trends."""
 NORTH = ['North East', 'Northern', 'Savannah', 'Upper East', 'Upper West', 'Oti']
 SOUTH = ['Greater Accra', 'Central', 'Eastern', 'Volta', 'Western']
 d = df.dropna(subset=['Adolescent_Fertility_Rate'])
 fig = go.Figure()
 for region, grp in d.groupby('Region'):
 grp = grp.sort_values('SurveyYear')
 zone = grp['Geographic_Zone'].iloc[0]
 fig.add_trace(go.Scatter(
 x=grp['SurveyYear'], y=grp['Adolescent_Fertility_Rate'],
 mode='lines+markers', name=region,
 line=dict(color=ZONE_COLORS.get(zone, '#888'), width=1.5),
 marker=dict(size=5),
 hovertemplate=f'<b>{region}</b><br>Year: %{{x}}<br>ASFR 15-19: %{{y:.0f}}<extra></extra>',
 ))
 fig.update_layout(**base_layout(
 title='Figure 10. Adolescent Fertility Rate Trends by Region (1988–2022)',
 xtitle='Survey Year', ytitle='ASFR 15–19 (per 1,000 women)'
 ))
 return fig


def make_kpi_cards():
 """Top-level KPI summary cards."""
 d22 = df[df['SurveyYear'] == df['SurveyYear'].max()]
 d88 = df[df['SurveyYear'] == df['SurveyYear'].min()]
 kpis = [
 ('National ANC 2022', f"{d22['Skilled_ANC_pct'].mean():.1f}%", GH_GREEN),
 ('Gini Decline 1988→2022', '−87.5%', GH_GOLD),
 ("TFR Moran's I 2022", '0.570**', GH_RED),
 ('Critical TFR Threshold', '5.90', '#b8860b'),
 ('CEI Gap (GA / NE)', '30.8 / 14.3', GH_GREEN),
 ('Risk Zone: Critical', '55/90 obs.', GH_RED),
 ]
 cards = []
 for label, value, color in kpis:
 cards.append(
 dbc.Col(
 dbc.Card([
 dbc.CardBody([
 html.H3(value, style={'color': color, 'fontWeight': 'bold',
 'fontSize': '1.6rem', 'margin': 0}),
 html.P(label, style={'fontSize': '0.78rem', 'color': '#555',
 'margin': 0, 'lineHeight': '1.2'}),
 ], style={'textAlign': 'center', 'padding': '10px 6px'}),
 ], style={'borderTop': f'4px solid {color}', 'borderRadius': '6px',
 'boxShadow': '0 1px 6px rgba(0,0,0,0.08)'}),
 width=2,
 )
 )
 return cards


# ─────────────────────────────────────────────────────────────────────────────
# 4. BUILD TABLES
# ─────────────────────────────────────────────────────────────────────────────

def table_regional_panel():
 d = df[['Region', 'Geographic_Zone', 'SurveyYear',
 'Skilled_ANC_pct', 'TFR', 'Adolescent_Fertility_Rate',
 'Care_Efficiency_Index', 'Risk_Zone',
 'Moran_I_ANC', 'Moran_I_TFR']].round(3)
 d.columns = ['Region', 'Zone', 'Year', 'Skilled ANC%', 'TFR',
 'ASFR 15-19', 'CEI', 'Risk Zone',
 "Moran I (ANC)", "Moran I (TFR)"]
 return dash_table.DataTable(
 data=d.to_dict('records'),
 columns=[{'name': c, 'id': c} for c in d.columns],
 page_size=15,
 sort_action='native',
 filter_action='native',
 style_table={'overflowX': 'auto'},
 style_cell={'fontSize': '11px', 'padding': '4px 8px',
 'fontFamily': 'Arial', 'textAlign': 'left'},
 style_header={'backgroundColor': GH_GREEN, 'color': 'white',
 'fontWeight': 'bold', 'fontSize': '11px'},
 style_data_conditional=[
 {'if': {'filter_query': '{Risk Zone} = Critical'},
 'backgroundColor': '#fff0f0', 'color': GH_RED},
 {'if': {'filter_query': '{Risk Zone} = Resilient'},
 'backgroundColor': '#f0fff4', 'color': GH_GREEN},
 ],
 )


# ─────────────────────────────────────────────────────────────────────────────
# 5. APP LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
app = dash.Dash(
 __name__,
 external_stylesheets=[dbc.themes.BOOTSTRAP],
 title='Ghana ANC Fertility Dashboard',
)

NAVBAR = dbc.Navbar(
 dbc.Container([
 dbc.Row([
 dbc.Col(html.Div([
 html.Span('🇬🇭', style={'fontSize': '1.4rem', 'marginRight': '8px'}),
 html.Span('Ghana ANC & Fertility Spatial Analysis — Part II (1988–2022)',
 style={'fontWeight': 'bold', 'fontSize': '1rem', 'color': 'white'}),
 ])),
 dbc.Col(html.Small('V. Ghanem | Ghana DHS subnational data',
 style={'color': 'rgba(255,255,255,0.75)', 'fontSize': '0.8rem'}),
 className='text-end'),
 ], align='center', className='w-100'),
 ], fluid=True),
 color=GH_GREEN, dark=True, sticky='top',
 style={'borderBottom': f'4px solid {GH_GOLD}'},
)

YEAR_SLIDER = dcc.Slider(
 id='year-slider',
 min=min(YEARS), max=max(YEARS),
 marks={y: str(y) for y in YEARS},
 value=2022, step=None,
 tooltip={'placement': 'bottom'},
)

REGION_DROPDOWN = dcc.Dropdown(
 id='region-dropdown',
 options=[{'label': r, 'value': r} for r in REGIONS],
 value=None, multi=True,
 placeholder='Filter by region(s)...',
 style={'fontSize': '12px'},
)

app.layout = dbc.Container([
 NAVBAR,
 html.Br(),

 # ── KPI row ──────────────────────────────────────────────────────────────
 dbc.Row(make_kpi_cards(), className='g-2 mb-3'),

 # ── Controls ─────────────────────────────────────────────────────────────
 dbc.Card(dbc.CardBody([
 dbc.Row([
 dbc.Col([html.Label('Survey Year (for cross-sections):',
 style={'fontSize': '12px', 'fontWeight': 'bold'}),
 YEAR_SLIDER], width=8),
 dbc.Col([html.Label('Region filter (trend charts):',
 style={'fontSize': '12px', 'fontWeight': 'bold'}),
 REGION_DROPDOWN], width=4),
 ])
 ]), className='mb-3 shadow-sm'),

 # ── Tabs ─────────────────────────────────────────────────────────────────
 dbc.Tabs([

 dbc.Tab(label='📈 ANC Trends', tab_id='tab-trends', children=[
 html.Br(),
 dbc.Row([
 dbc.Col(dcc.Graph(id='fig-anc-traj', figure=fig_anc_trajectories()), width=8),
 dbc.Col(dcc.Graph(id='fig-gini', figure=fig_gini_trend()), width=4),
 ], className='mb-3'),
 dbc.Row([
 dbc.Col(dcc.Graph(id='fig-ns-gap', figure=fig_north_south_gap()), width=6),
 dbc.Col(dcc.Graph(id='fig-adol', figure=fig_adol_fertility()), width=6),
 ]),
 ]),

 dbc.Tab(label='🔵 Spatial Analysis', tab_id='tab-spatial', children=[
 html.Br(),
 dbc.Row([
 dbc.Col(dcc.Graph(id='fig-morans', figure=fig_morans_temporal()), width=6),
 dbc.Col(dcc.Graph(id='fig-scatter', figure=fig_tfr_anc_scatter()), width=6),
 ], className='mb-3'),
 ]),

 dbc.Tab(label='⚡ Machine Learning', tab_id='tab-ml', children=[
 html.Br(),
 dbc.Row([
 dbc.Col(dcc.Graph(id='fig-risk-pie', figure=fig_risk_zone_pie()), width=4),
 dbc.Col(dcc.Graph(id='fig-cei', figure=fig_cei_bar()), width=8),
 ]),
 ]),

 dbc.Tab(label='📋 Data Table', tab_id='tab-table', children=[
 html.Br(),
 html.P("Full region-year panel dataset — sortable and filterable. "
 "Source: Ghana DHS subnational, Master Sheet, derived analysis columns.",
 style={'fontSize': '12px', 'color': '#555'}),
 table_regional_panel(),
 ]),

 ], id='main-tabs', active_tab='tab-trends'),

 # ── Footer ───────────────────────────────────────────────────────────────
 html.Hr(),
 html.Small([
 html.Strong('Data: '), 'Ghana DHS subnational (dhsprogram.com) | ',
 html.Strong('Methods: '), 'LISA, Random Forest, Partial Dependence, Care Efficiency Index | ',
 html.Strong('Reporting: '), 'STROBE ecological | ',
 html.Strong('Contact: '), 'valentineghanem@gmail.com',
 ], style={'color': '#888', 'fontSize': '10px'}),
 html.Br(), html.Br(),

], fluid=True, style={'backgroundColor': '#f8f9fa'})


# ─────────────────────────────────────────────────────────────────────────────
# 6. CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(
 Output('fig-anc-traj', 'figure'),
 Input('region-dropdown', 'value'),
)
def update_traj(regions):
 return fig_anc_trajectories(regions)


@app.callback(
 Output('fig-scatter', 'figure'),
 Input('year-slider', 'value'),
)
def update_scatter(year):
 return fig_tfr_anc_scatter(year)


# ─────────────────────────────────────────────────────────────────────────────
# 7. ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
 print("\n" + "="*60)
 print(" Ghana ANC Fertility Spatial Analysis Dashboard")
 print(" Open browser at: http://127.0.0.1:8050")
 print("="*60 + "\n")
 app.run(debug=False, host='127.0.0.1', port=8050)
