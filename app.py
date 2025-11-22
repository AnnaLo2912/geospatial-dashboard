import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "NYC Taxi Analytics"
# ============================================
# DATA LOADING (Assets Version for Deployment)
# ============================================

import pandas as pd
from datetime import datetime

SAMPLE_SIZE = 200000

# Folder where Render + Dash will reliably load static data
DATA_FOLDER = "assets/data/"


def load_data():
    """Load taxi data + cluster metrics from assets/data/"""

    metrics_df = None
    taxi_df = None

    # ---- LOAD METRICS ----
    try:
        metrics_df = pd.read_csv(DATA_FOLDER + "dbscan_cluster_metrics.csv")
        print(f"✓ Loaded {len(metrics_df)} clusters from DBSCAN analysis")
    except Exception as e:
        print(f"⚠ Could not load cluster metrics: {e}")

    # ---- LOAD TAXI TRIPS ----
    try:
        print(f"\nLoading taxi sample ({SAMPLE_SIZE:,} rows)...")

        taxi_df = pd.read_csv(
            DATA_FOLDER + "merged_cleaned_taxi_data.csv",
            nrows=SAMPLE_SIZE,
            low_memory=False
        )

        # Normalize date column
        if 'tpep_pickup_datetime' in taxi_df.columns:
            taxi_df['pickup_datetime'] = pd.to_datetime(taxi_df['tpep_pickup_datetime'])
        elif 'pickup_datetime' in taxi_df.columns:
            taxi_df['pickup_datetime'] = pd.to_datetime(taxi_df['pickup_datetime'])

        print(f"✓ Loaded {len(taxi_df):,} trips")

    except Exception as e:
        print(f"❌ Error loading taxi data: {e}")
        taxi_df = None

    return metrics_df, taxi_df



def detect_available_dates(df):
    """Detect available date ranges dynamically."""
    if df is None or 'pickup_datetime' not in df.columns:
        return [{
            'start': datetime(2015, 1, 1).date(),
            'end': datetime(2015, 1, 31).date(),
            'label': 'January 2015'
        }]

    df['year_month'] = df['pickup_datetime'].dt.to_period('M')
    available_periods = df['year_month'].unique()

    date_ranges = []
    for period in sorted(available_periods):
        month_data = df[df['year_month'] == period]
        start_date = month_data['pickup_datetime'].min().date()
        end_date = month_data['pickup_datetime'].max().date()

        date_ranges.append({
            'start': start_date,
            'end': end_date,
            'label': period.strftime('%B %Y')
        })

    return date_ranges



def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(int(num))



# ---- LOAD EVERYTHING ----
metrics_df, taxi_df = load_data()
AVAILABLE_DATES = detect_available_dates(taxi_df)

print("\nAvailable Date Ranges:")
for d in AVAILABLE_DATES:
    print(f" - {d['label']} ({d['start']} → {d['end']})")

# Set default min/max
if AVAILABLE_DATES:
    data_min_date = AVAILABLE_DATES[0]['start']
    data_max_date = AVAILABLE_DATES[-1]['end']


# ============================================
# STYLING
# ============================================
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            background: #05070a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        
        .app-container {
            background: 
                radial-gradient(ellipse at 0% 0%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 100% 100%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
                #05070a;
            min-height: 100vh;
        }
        
        .glass-card {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 24px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
            border-radius: 16px;
            padding: 18px 16px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            min-height: 115px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .stat-card:hover::before { opacity: 1; }
        .stat-card:hover { border-color: rgba(59, 130, 246, 0.3); }
        
        .stat-value { 
            font-size: 1.65rem; 
            font-weight: 700; 
            color: #f8fafc;
            letter-spacing: -0.025em;
            line-height: 1;
            margin: 8px 0 4px 0;
            word-break: break-all;
            max-width: 100%;
        }
        .stat-label { 
            font-size: 0.68rem; 
            color: #64748b; 
            text-transform: uppercase; 
            letter-spacing: 0.08em;
            margin-top: 2px;
        }
        .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }
        
        .section-label {
            font-size: 0.7rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 16px;
        }
        
        .info-box {
            background: rgba(59, 130, 246, 0.1);
            border-left: 3px solid #3b82f6;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-size: 0.85rem;
            line-height: 1.5;
            color: #cbd5e1;
        }
        .info-box-title {
            font-weight: 600;
            color: #3b82f6;
            margin-bottom: 4px;
            font-size: 0.9rem;
        }
        
        .Select-control { 
            background: rgba(30, 41, 59, 0.8) !important; 
            border: 1px solid rgba(255, 255, 255, 0.08) !important; 
            border-radius: 10px !important;
            min-height: 42px !important;
        }
        .Select-control:hover { border-color: rgba(59, 130, 246, 0.4) !important; }
        .Select-menu-outer { 
            background: rgba(30, 41, 59, 0.95) !important; 
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            margin-top: 4px;
            backdrop-filter: blur(12px);
        }
        .Select-option { background: transparent !important; color: #e2e8f0 !important; padding: 12px 14px !important; }
        .Select-option:hover, .Select-option.is-focused { background: rgba(59, 130, 246, 0.15) !important; }
        .Select-value-label { color: #e2e8f0 !important; }
        .Select-placeholder { color: #64748b !important; }
        .Select-input input { color: #e2e8f0 !important; }
        
        .DateInput_input { 
            background: rgba(30, 41, 59, 0.8) !important; 
            color: #e2e8f0 !important; 
            border: 1px solid rgba(255, 255, 255, 0.08) !important; 
            border-radius: 10px !important; 
            padding: 10px 14px !important;
            font-size: 0.875rem !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .DateInput_input:focus { border-color: #3b82f6 !important; }
        .CalendarDay__selected { background: #3b82f6 !important; }
        .DayPickerKeyboardShortcuts_buttonReset { display: none; }
        
        .toggle-group { display: inline-flex; background: rgba(30, 41, 59, 0.6); border-radius: 10px; padding: 4px; }
        .toggle-btn {
            background: transparent;
            border: none;
            color: #64748b;
            padding: 8px 18px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .toggle-btn:hover { color: #e2e8f0; }
        .toggle-btn.active { background: #3b82f6; color: #fff; }
        
        .location-panel {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 16px;
        }
        .location-panel a { color: #3b82f6; text-decoration: none; font-weight: 500; }
        .location-panel a:hover { text-decoration: underline; }
        
        .tour-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tour-modal {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            max-width: 520px;
            width: 90%;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }
        .tour-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px; color: #f8fafc; }
        .tour-subtitle { color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px; line-height: 1.5; }
        .tour-feature { 
            display: flex; 
            align-items: flex-start; 
            gap: 14px; 
            padding: 14px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .tour-feature:last-child { border-bottom: none; }
        .tour-feature-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            flex-shrink: 0;
        }
        .tour-feature-text h4 { font-size: 0.9rem; font-weight: 600; color: #f1f5f9; margin-bottom: 2px; }
        .tour-feature-text p { font-size: 0.8rem; color: #94a3b8; line-height: 1.4; }
        .tour-btn {
            width: 100%;
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            border: none;
            color: #fff;
            padding: 14px 24px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 24px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .tour-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3); }
        
        .map-wrapper {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        
        @media (max-width: 1024px) {
            .grid-3 { grid-template-columns: repeat(2, 1fr) !important; }
            .flex-row { flex-direction: column !important; gap: 16px !important; }
        }
        @media (max-width: 640px) {
            .grid-3 { grid-template-columns: 1fr !important; }
            .stat-value { font-size: 1.5rem; }
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
'''

# ============================================
# LAYOUT
# ============================================
app.layout = html.Div([
    dcc.Store(id='tour-shown', storage_type='local', data=False),
    
    # Tour Overlay
    html.Div([
        html.Div([
            html.H2("Welcome to NYC Taxi Analytics", className='tour-title'),
            html.P("Explore taxi pickup patterns across New York City with interactive visualizations and spatial analysis.", className='tour-subtitle'),
            
            html.Div([
                html.Div([
                    html.Div("1", className='tour-feature-icon', style={'background': 'rgba(59, 130, 246, 0.15)', 'color': '#3b82f6'}),
                    html.Div([
                        html.H4("Interactive Map"),
                        html.P("Click any point to see the neighborhood name and exact coordinates")
                    ], className='tour-feature-text')
                ], className='tour-feature'),
                
                html.Div([
                    html.Div("2", className='tour-feature-icon', style={'background': 'rgba(139, 92, 246, 0.15)', 'color': '#8b5cf6'}),
                    html.Div([
                        html.H4("Multiple Views"),
                        html.P("Switch between scatter plots, heatmaps, and DBSCAN cluster views")
                    ], className='tour-feature-text')
                ], className='tour-feature'),
                
                html.Div([
                    html.Div("3", className='tour-feature-icon', style={'background': 'rgba(16, 185, 129, 0.15)', 'color': '#10b981'}),
                    html.Div([
                        html.H4("Time Filtering"),
                        html.P("Filter by date and time of day to discover hourly patterns")
                    ], className='tour-feature-text')
                ], className='tour-feature'),
                
                html.Div([
                    html.Div("4", className='tour-feature-icon', style={'background': 'rgba(245, 158, 11, 0.15)', 'color': '#f59e0b'}),
                    html.Div([
                        html.H4("Cluster Analysis"),
                        html.P("View DBSCAN clustering results to identify pickup hotspots")
                    ], className='tour-feature-text')
                ], className='tour-feature'),
            ]),
            
            html.Button("Get Started", id='close-tour', className='tour-btn')
        ], className='tour-modal')
    ], id='tour-overlay', className='tour-overlay', style={'display': 'flex'}),
    
    # Main App
    html.Div([
        # Header
        html.Div([
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': '10px', 'height': '10px', 'borderRadius': '50%',
                        'background': 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                        'marginRight': '12px'
                    }),
                    html.Span("NYC Taxi Analytics", style={'fontSize': '1.1rem', 'fontWeight': '700', 'color': '#f8fafc'})
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ]),
            html.Div([
                html.Span(f"Loading...", id='trip-count-display', style={
                    'fontSize': '0.75rem', 'color': '#64748b', 'marginRight': '16px'
                }),
                html.Button("View Guide", id='show-tour', style={
                    'background': 'transparent', 'border': '1px solid rgba(255,255,255,0.1)',
                    'color': '#94a3b8', 'padding': '6px 14px', 'borderRadius': '8px',
                    'fontSize': '0.75rem', 'cursor': 'pointer', 'fontFamily': 'Plus Jakarta Sans'
                })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
            'padding': '16px 32px', 'borderBottom': '1px solid rgba(255,255,255,0.05)'
        }),
        
        # Main Content
        html.Div([
            # Left Sidebar
            html.Div([
                # Stats
                html.Div([
                    html.Div("Overview", className='section-label'),
                    html.Div([
                        html.Div([
                            html.Div(className='stat-icon', style={'background': 'rgba(59,130,246,0.1)', 'color': '#3b82f6'}, children="🚕"),
                            html.Div(id='stat-trips', className='stat-value'),
                            html.Div("Trips", className='stat-label')
                        ], className='stat-card'),
                        html.Div([
                            html.Div(className='stat-icon', style={'background': 'rgba(139,92,246,0.1)', 'color': '#8b5cf6'}, children="📍"),
                            html.Div(id='stat-clusters', className='stat-value'),
                            html.Div("Clusters", className='stat-label')
                        ], className='stat-card'),
                        html.Div([
                            html.Div(className='stat-icon', style={'background': 'rgba(16,185,129,0.1)', 'color': '#10b981'}, children="💰"),
                            html.Div(id='stat-fare', className='stat-value'),
                            html.Div("Avg Fare", className='stat-label')
                        ], className='stat-card'),
                    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '12px'}, className='grid-3')
                ], style={'marginBottom': '28px'}),
                
                # Filters
                html.Div([
                    html.Div("Filters", className='section-label'),
                    
                    html.Div([
                        html.Label("Date Selection", style={'fontSize': '0.8rem', 'fontWeight': '500', 'color': '#94a3b8', 'marginBottom': '10px', 'display': 'block'}),
                        html.Div([
                            html.Button("Single Day", id='mode-single', className='toggle-btn', n_clicks=0),
                            html.Button("Date Range", id='mode-range', className='toggle-btn active', n_clicks=0),
                        ], className='toggle-group'),
                    ], style={'marginBottom': '16px'}),
                    
                    html.Div([
                        html.Label("Month Range", style={'fontSize': '0.8rem', 'fontWeight': '500', 'color': '#94a3b8', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.Dropdown(
                            id='month-selector',
                            options=[{'label': d['label'], 'value': i} for i, d in enumerate(AVAILABLE_DATES)],
                            value=0,
                            clearable=False
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Div([
                            html.Label(id='label-start', children="Start", style={'fontSize': '0.75rem', 'color': '#64748b', 'marginBottom': '6px', 'display': 'block'}),
                            dcc.DatePickerSingle(
                                id='start-date',
                                date=data_min_date,
                                display_format='MMM D, YYYY'
                            )
                        ], style={'marginRight': '12px'}),
                        html.Div([
                            html.Label("End", style={'fontSize': '0.75rem', 'color': '#64748b', 'marginBottom': '6px', 'display': 'block'}),
                            dcc.DatePickerSingle(
                                id='end-date',
                                date=data_max_date,
                                display_format='MMM D, YYYY'
                            )
                        ], id='end-date-container')
                    ], style={'display': 'flex', 'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Label("Time of Day", style={'fontSize': '0.8rem', 'fontWeight': '500', 'color': '#94a3b8', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.Dropdown(
                            id='time-filter',
                            options=[
                                {'label': 'All Hours', 'value': 'all'},
                                {'label': 'Morning Rush (6-10 AM)', 'value': 'morning_rush'},
                                {'label': 'Midday (10 AM - 4 PM)', 'value': 'midday'},
                                {'label': 'Evening Rush (4-8 PM)', 'value': 'evening_rush'},
                                {'label': 'Night (8 PM - 6 AM)', 'value': 'night'},
                            ],
                            value='all',
                            clearable=False
                        )
                    ], style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Label("Map View", style={'fontSize': '0.8rem', 'fontWeight': '500', 'color': '#94a3b8', 'marginBottom': '10px', 'display': 'block'}),
                        dcc.Dropdown(
                            id='map-type',
                            options=[
                                {'label': 'Scatter - Individual Pickups', 'value': 'scatter'},
                                {'label': 'Heatmap - Density', 'value': 'heatmap'},
                                {'label': 'Clusters - DBSCAN Groups', 'value': 'clusters'},
                            ],
                            value='scatter',
                            clearable=False
                        )
                    ])
                ], className='glass-card')
            ], style={'width': '320px', 'flexShrink': '0', 'marginRight': '24px'}),
            
            # Main Content Area
            html.Div([
                # Map
                html.Div([
                    html.Div([
                        html.Span("Map", style={'fontSize': '0.8rem', 'fontWeight': '600', 'color': '#f8fafc'}),
                        html.Span(" — Click points for location details", style={'fontSize': '0.75rem', 'color': '#64748b'})
                    ], style={'marginBottom': '16px'}),
                    
                    # Info Box - dynamically updated based on map type
                    html.Div(id='map-info-box'),
                    
                    html.Div([
                        dcc.Loading(
                            dcc.Graph(id='main-map', config={'displayModeBar': True, 'scrollZoom': True}, style={'height': '420px'}),
                            type='circle', color='#3b82f6'
                        )
                    ], className='map-wrapper'),
                    html.Div(id='location-info')
                ], className='glass-card', style={'marginBottom': '20px'}),
                
                # Charts Row
                html.Div([
                    html.Div([
                        html.Div("Trips by Date", style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': '#94a3b8', 'marginBottom': '12px', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                        dcc.Graph(id='time-chart', config={'displayModeBar': False}, style={'height': '180px'})
                    ], className='glass-card', style={'flex': '1', 'marginRight': '10px'}),
                    
                    html.Div([
                        html.Div("Pickups by Hour", style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': '#94a3b8', 'marginBottom': '12px', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                        dcc.Graph(id='hourly-chart', config={'displayModeBar': False}, style={'height': '180px'})
                    ], className='glass-card', style={'flex': '1', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'marginBottom': '20px'}, className='flex-row'),
                
                # Cluster Chart
                html.Div([
                    html.Div("Cluster Distribution", style={'fontSize': '0.75rem', 'fontWeight': '600', 'color': '#94a3b8', 'marginBottom': '12px', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                    dcc.Loading(
                        dcc.Graph(id='cluster-chart', config={'displayModeBar': False}, style={'height': '280px'}),
                        type='circle', color='#f59e0b'
                    )
                ], className='glass-card')
                
            ], style={'flex': '1', 'minWidth': '0'})
            
        ], style={'display': 'flex', 'padding': '24px 32px'}, className='flex-row')
        
    ], className='app-container')
])

# ============================================
# HELPER FUNCTIONS
# ============================================

def filter_data(df, start_date, end_date, time_filter, single_mode=False):
    if df is None or 'pickup_datetime' not in df.columns:
        return df
    
    filtered = df.copy()
    
    if start_date:
        start = pd.to_datetime(start_date).date()
        end = pd.to_datetime(end_date).date() if end_date and not single_mode else start
        
        mask = (filtered['pickup_datetime'].dt.date >= start) & (filtered['pickup_datetime'].dt.date <= end)
        filtered = filtered[mask]
    
    if time_filter != 'all' and len(filtered) > 0:
        hour = filtered['pickup_datetime'].dt.hour
        if time_filter == 'morning_rush':
            filtered = filtered[(hour >= 6) & (hour < 10)]
        elif time_filter == 'midday':
            filtered = filtered[(hour >= 10) & (hour < 16)]
        elif time_filter == 'evening_rush':
            filtered = filtered[(hour >= 16) & (hour < 20)]
        elif time_filter == 'night':
            filtered = filtered[(hour >= 20) | (hour < 6)]
    
    return filtered

def get_count_column(df):
    """Find the count column in metrics dataframe"""
    if df is None:
        return None
    for col in ['points', 'point_count', 'count', 'size', 'num_points']:
        if col in df.columns:
            return col
    num_cols = df.select_dtypes(include=[np.number]).columns
    return num_cols[0] if len(num_cols) > 0 else None

def get_location_name(lat, lon):
    """Get location name from coordinates using Nominatim"""
    try:
        from urllib.request import urlopen, Request
        import json
        
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = Request(url, headers={'User-Agent': 'NYC-Taxi-Analytics/1.0'})
        
        with urlopen(req, timeout=3) as response:
            data = json.loads(response.read())
        
        address = data.get('address', {})
        neighborhood = address.get('neighbourhood') or address.get('suburb') or address.get('city_district')
        city = address.get('city') or address.get('town') or address.get('village')
        
        if neighborhood and city:
            return f"{neighborhood}, {city}"
        elif neighborhood:
            return neighborhood
        elif city:
            return city
        else:
            display_name = data.get('display_name', '')
            return display_name.split(',')[0] if display_name else None
    except Exception as e:
        print(f"Location lookup error: {e}")
        return None

# ============================================
# CALLBACKS
# ============================================

@app.callback(
    Output('trip-count-display', 'children'),
    Input('trip-count-display', 'id')
)
def update_trip_count(_):
    if taxi_df is not None:
        months = len(AVAILABLE_DATES)
        month_text = "month" if months == 1 else "months"
        return f"{len(taxi_df):,} trips • {months} {month_text}"
    return f"{SAMPLE_SIZE:,} trips"

@app.callback(
    Output('tour-overlay', 'style'),
    [Input('close-tour', 'n_clicks'),
     Input('show-tour', 'n_clicks')],
    [State('tour-shown', 'data')]
)
def toggle_tour(close_clicks, show_clicks, was_shown):
    ctx = callback_context
    if not ctx.triggered:
        if was_shown:
            return {'display': 'none'}
        return {'display': 'flex'}
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'close-tour':
        return {'display': 'none'}
    elif trigger == 'show-tour':
        return {'display': 'flex'}
    return {'display': 'none'}

@app.callback(
    Output('tour-shown', 'data'),
    Input('close-tour', 'n_clicks'),
    prevent_initial_call=True
)
def mark_tour_shown(n):
    return True

@app.callback(
    [Output('start-date', 'date'),
     Output('end-date', 'date'),
     Output('start-date', 'min_date_allowed'),
     Output('start-date', 'max_date_allowed'),
     Output('end-date', 'min_date_allowed'),
     Output('end-date', 'max_date_allowed'),
     Output('mode-single', 'className'),
     Output('mode-range', 'className'),
     Output('end-date-container', 'style'),
     Output('label-start', 'children')],
    [Input('month-selector', 'value'),
     Input('mode-single', 'n_clicks'),
     Input('mode-range', 'n_clicks')],
    [State('start-date', 'date'),
     State('mode-single', 'className')]
)
def update_all_date_controls(month_idx, single_clicks, range_clicks, current_start, single_class):
    ctx = callback_context
    date_range = AVAILABLE_DATES[month_idx]
    
    start = date_range['start']
    end = date_range['end']
    single_active = 'toggle-btn'
    range_active = 'toggle-btn active'
    end_visible = {'display': 'block'}
    label = 'Start'
    
    is_single_mode = single_class and 'active' in single_class
    
    if ctx.triggered:
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger == 'mode-single':
            single_active = 'toggle-btn active'
            range_active = 'toggle-btn'
            end_visible = {'display': 'none'}
            label = 'Date'
            if current_start:
                start = pd.to_datetime(current_start).date()
                end = start
            else:
                start = date_range['start']
                end = start
                
        elif trigger == 'mode-range':
            single_active = 'toggle-btn'
            range_active = 'toggle-btn active'
            end_visible = {'display': 'block'}
            label = 'Start'
            start = date_range['start']
            end = date_range['end']
            
        elif trigger == 'month-selector':
            if is_single_mode:
                single_active = 'toggle-btn active'
                range_active = 'toggle-btn'
                end_visible = {'display': 'none'}
                label = 'Date'
                start = date_range['start']
                end = start
            else:
                single_active = 'toggle-btn'
                range_active = 'toggle-btn active'
                end_visible = {'display': 'block'}
                label = 'Start'
                start = date_range['start']
                end = date_range['end']
    
    return (
        start,
        end,
        date_range['start'],
        date_range['end'],
        date_range['start'],
        date_range['end'],
        single_active,
        range_active,
        end_visible,
        label
    )

@app.callback(
    [Output('stat-trips', 'children'),
     Output('stat-clusters', 'children'),
     Output('stat-fare', 'children')],
    [Input('start-date', 'date'), Input('end-date', 'date'), 
     Input('time-filter', 'value'), Input('mode-single', 'className')]
)
def update_stats(start, end, time_filter, single_class):
    single_mode = 'active' in (single_class or '')
    filtered = filter_data(taxi_df, start, end, time_filter, single_mode)
    
    if filtered is None or len(filtered) == 0:
        return "0", str(len(metrics_df)) if metrics_df is not None else "—", "—"
    
    # Format numbers to fit in stat boxes - handle both small and large numbers
    trip_count = len(filtered)
    if trip_count >= 1000000:
        trips = f"{trip_count/1000000:.1f}M"
    elif trip_count >= 10000:
        trips = f"{trip_count/1000:.1f}K"
    elif trip_count >= 1000:
        trips = f"{trip_count/1000:.2f}K"
    else:
        trips = f"{trip_count:,}"
    
    # Clusters - always show full number since it's typically small
    clusters = str(len(metrics_df)) if metrics_df is not None else "—"
    
    # Average fare - show with dollar sign and 2 decimals
    if 'total_amount' in filtered.columns:
        avg_fare = filtered['total_amount'].mean()
        avg_fare_str = f"${avg_fare:.2f}"
    else:
        avg_fare_str = "—"
    
    return trips, clusters, avg_fare_str

@app.callback(
    Output('map-info-box', 'children'),
    Input('map-type', 'value')
)
def update_map_info(map_type):
    """Display helpful information about the current map view"""
    if map_type == 'scatter':
        return html.Div([
            html.Div("📊 Scatter Plot", className='info-box-title'),
            html.Div("Each blue dot represents an individual taxi pickup location. Clustered dots indicate popular pickup areas. Click any point to see its exact neighborhood and coordinates.")
        ], className='info-box')
    
    elif map_type == 'heatmap':
        return html.Div([
            html.Div("🔥 Density Heatmap", className='info-box-title'),
            html.Div("Warmer colors (red/yellow) show areas with high pickup density where many taxis are requested, while cooler colors (blue/green) indicate fewer pickups. This visualization helps identify the busiest zones across NYC and understand spatial demand patterns.")
        ], className='info-box')
    
    elif map_type == 'clusters':
        return html.Div([
            html.Div("🎯 DBSCAN Clusters", className='info-box-title'),
            html.Div("Each circle represents a density-based cluster identified by the DBSCAN algorithm (eps=60m, min_samples=50). Larger circles indicate more pickups in that hotspot. This reveals distinct pickup concentration areas and eliminates noise points for clearer pattern identification.")
        ], className='info-box')
    
    return None

@app.callback(
    Output('main-map', 'figure'),
    [Input('start-date', 'date'), Input('end-date', 'date'), 
     Input('time-filter', 'value'), Input('map-type', 'value'),
     Input('mode-single', 'className')]
)
def update_map(start, end, time_filter, map_type, single_class):
    single_mode = 'active' in (single_class or '')
    filtered = filter_data(taxi_df, start, end, time_filter, single_mode)
    
    if filtered is None or len(filtered) == 0:
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[{
                'text': 'No data available for selected filters',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 16, 'color': '#64748b'}
            }],
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return fig
    
    if map_type in ['scatter', 'heatmap'] and len(filtered) > 5000:
        display_df = filtered.sample(5000)
        print(f"📍 Displaying 5,000 sample points from {len(filtered):,} total trips")
    else:
        display_df = filtered
    
    if 'pickup_latitude' not in display_df.columns or 'pickup_longitude' not in display_df.columns:
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[{
                'text': 'Location data not available',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 16, 'color': '#64748b'}
            }]
        )
        return fig
    
    if map_type == 'scatter':
        fig = px.scatter_mapbox(
            display_df,
            lat='pickup_latitude',
            lon='pickup_longitude',
            hover_data={'pickup_latitude': ':.4f', 'pickup_longitude': ':.4f'},
            zoom=10,
            height=420
        )
        fig.update_traces(marker=dict(size=5, color='#3b82f6', opacity=0.6))
    
    elif map_type == 'heatmap':
        fig = px.density_mapbox(
            display_df,
            lat='pickup_latitude',
            lon='pickup_longitude',
            radius=10,
            zoom=10,
            height=420,
            color_continuous_scale='Turbo'
        )
    
    else:
        if metrics_df is not None and len(metrics_df) > 0:
            lat_col = None
            lon_col = None
            
            for lat_name in ['center_lat', 'lat', 'latitude', 'center_latitude']:
                if lat_name in metrics_df.columns:
                    lat_col = lat_name
                    break
            
            for lon_name in ['center_lon', 'lon', 'longitude', 'center_longitude']:
                if lon_name in metrics_df.columns:
                    lon_col = lon_name
                    break
            
            if lat_col and lon_col:
                count_col = get_count_column(metrics_df)
                fig = px.scatter_mapbox(
                    metrics_df,
                    lat=lat_col,
                    lon=lon_col,
                    size=count_col if count_col else None,
                    color=count_col if count_col else None,
                    hover_data={count_col: True} if count_col else {},
                    zoom=10,
                    height=420,
                    color_continuous_scale='Viridis'
                )
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text='Cluster location data not available',
                    xref='paper', yref='paper',
                    x=0.5, y=0.5,
                    showarrow=False,
                    font={'size': 16, 'color': '#64748b'}
                )
        else:
            fig = go.Figure()
            fig.add_annotation(
                text='Cluster data not available',
                xref='paper', yref='paper',
                x=0.5, y=0.5,
                showarrow=False,
                font={'size': 16, 'color': '#64748b'}
            )
    
    fig.update_layout(
        mapbox_style='open-street-map',
        mapbox=dict(center=dict(lat=40.7580, lon=-73.9855)),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('location-info', 'children'),
    Input('main-map', 'clickData')
)
def display_click_info(click_data):
    if not click_data:
        return None
    
    try:
        point = click_data['points'][0]
        lat = point.get('lat')
        lon = point.get('lon')
        
        if lat and lon:
            location_name = get_location_name(lat, lon)
            
            return html.Div([
                html.Div([
                    html.Span("📍 Selected Location", style={'fontWeight': '600', 'fontSize': '0.85rem', 'color': '#f8fafc'}),
                ], style={'marginBottom': '8px'}),
                
                html.Div([
                    html.Span(f"{location_name}", style={'color': '#e2e8f0', 'fontSize': '0.9rem', 'fontWeight': '500', 'display': 'block', 'marginBottom': '6px'}),
                ], style={'marginBottom': '6px'}) if location_name else None,
                
                html.Div([
                    html.Span(f"Coordinates: ", style={'color': '#94a3b8', 'fontSize': '0.8rem'}),
                    html.Span(f"{lat:.4f}, {lon:.4f}", style={'color': '#e2e8f0', 'fontSize': '0.8rem', 'fontWeight': '500'}),
                ]),
                html.Div([
                    html.A("View on Google Maps", 
                           href=f"https://www.google.com/maps?q={lat},{lon}",
                           target="_blank",
                           style={'fontSize': '0.75rem', 'marginTop': '8px', 'display': 'inline-block'})
                ])
            ], className='location-panel')
    except Exception as e:
        print(f"Error in location display: {e}")
        return None
    
    return None

@app.callback(
    Output('time-chart', 'figure'),
    [Input('start-date', 'date'), Input('end-date', 'date'),
     Input('time-filter', 'value'), Input('mode-single', 'className')]
)
def update_time_chart(start, end, time_filter, single_class):
    try:
        single_mode = 'active' in (single_class or '')
        filtered = filter_data(taxi_df, start, end, time_filter, single_mode)
        
        if filtered is None or len(filtered) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text='No data for selected date range',
                xref='paper', yref='paper',
                x=0.5, y=0.5,
                showarrow=False,
                font={'size': 14, 'color': '#64748b'}
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis={'visible': False},
                yaxis={'visible': False},
                margin=dict(l=50, r=20, t=20, b=40),
                height=200
            )
            return fig
        
        if single_mode:
            hourly = filtered.groupby(filtered['pickup_datetime'].dt.hour).size().reset_index()
            hourly.columns = ['hour', 'trips']
            
            all_hours = pd.DataFrame({'hour': range(24)})
            hourly = all_hours.merge(hourly, on='hour', how='left').fillna(0)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=hourly['hour'],
                y=hourly['trips'],
                marker=dict(color='#3b82f6'),
                hovertemplate='<b>Hour %{x}:00</b><br>Trips: %{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=20, t=20, b=40),
                xaxis=dict(
                    title='Hour of Day',
                    gridcolor='rgba(255,255,255,0.05)',
                    showgrid=True,
                    dtick=2
                ),
                yaxis=dict(
                    title='Trips',
                    gridcolor='rgba(255,255,255,0.05)',
                    showgrid=True
                ),
                showlegend=False,
                height=200,
                bargap=0.15
            )
        else:
            daily = filtered.groupby(filtered['pickup_datetime'].dt.date).size().reset_index()
            daily.columns = ['date', 'trips']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily['date'],
                y=daily['trips'],
                mode='lines',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)',
                hovertemplate='<b>%{x}</b><br>Trips: %{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=20, t=20, b=40),
                xaxis=dict(
                    title='',
                    gridcolor='rgba(255,255,255,0.05)',
                    showgrid=True
                ),
                yaxis=dict(
                    title='Trips',
                    gridcolor='rgba(255,255,255,0.05)',
                    showgrid=True
                ),
                hovermode='x unified',
                showlegend=False,
                height=200
            )
        
        return fig
    except Exception as e:
        print(f"Error in time chart: {e}")
        import traceback
        traceback.print_exc()
        fig = go.Figure()
        fig.add_annotation(
            text='Error loading chart',
            xref='paper', yref='paper',
            x=0.5, y=0.5,
            showarrow=False,
            font={'size': 14, 'color': '#ef4444'}
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200
        )
        return fig

@app.callback(
    Output('hourly-chart', 'figure'),
    [Input('start-date', 'date'), Input('end-date', 'date'),
     Input('time-filter', 'value'), Input('mode-single', 'className')]
)
def update_hourly_chart(start, end, time_filter, single_class):
    try:
        single_mode = 'active' in (single_class or '')
        filtered = filter_data(taxi_df, start, end, time_filter, single_mode)
        
        if filtered is None or len(filtered) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text='No data for selected date range',
                xref='paper', yref='paper',
                x=0.5, y=0.5,
                showarrow=False,
                font={'size': 14, 'color': '#64748b'}
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis={'visible': False},
                yaxis={'visible': False},
                margin=dict(l=50, r=20, t=20, b=40),
                height=200
            )
            return fig
        
        hourly = filtered.groupby(filtered['pickup_datetime'].dt.hour).size().reset_index()
        hourly.columns = ['hour', 'trips']
        
        all_hours = pd.DataFrame({'hour': range(24)})
        hourly = all_hours.merge(hourly, on='hour', how='left').fillna(0)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly['hour'],
            y=hourly['trips'],
            marker=dict(
                color='#8b5cf6',
                line=dict(width=0)
            ),
            text=hourly['trips'].astype(int),
            texttemplate='%{text:,}',
            textposition='outside',
            textfont=dict(size=9, color='#94a3b8'),
            hovertemplate='<b>Hour %{x}:00</b><br>Trips: %{y:,}<extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=20, t=30, b=40),
            xaxis=dict(
                title='Hour of Day',
                gridcolor='rgba(255,255,255,0.05)',
                showgrid=False,
                dtick=2,
                range=[-0.5, 23.5]
            ),
            yaxis=dict(
                title='Trips',
                gridcolor='rgba(255,255,255,0.05)',
                showgrid=True
            ),
            bargap=0.15,
            showlegend=False,
            height=200
        )
        
        return fig
    except Exception as e:
        print(f"Error in hourly chart: {e}")
        import traceback
        traceback.print_exc()
        fig = go.Figure()
        fig.add_annotation(
            text='Error loading chart',
            xref='paper', yref='paper',
            x=0.5, y=0.5,
            showarrow=False,
            font={'size': 14, 'color': '#ef4444'}
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200
        )
        return fig

@app.callback(
    Output('cluster-chart', 'figure'),
    Input('cluster-chart', 'id')
)
def update_cluster_chart(_):
    try:
        if metrics_df is None or len(metrics_df) == 0:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                annotations=[{
                    'text': 'No cluster data available',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False,
                    'font': {'size': 14, 'color': '#64748b'}
                }],
                xaxis={'visible': False},
                yaxis={'visible': False},
                height=250
            )
            return fig
        
        count_col = get_count_column(metrics_df)
        
        if count_col is None:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                annotations=[{
                    'text': 'Count column not found in cluster data',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False,
                    'font': {'size': 14, 'color': '#64748b'}
                }],
                xaxis={'visible': False},
                yaxis={'visible': False},
                height=250
            )
            return fig
        
        top_clusters = metrics_df.nlargest(12, count_col).copy()
        top_clusters = top_clusters.sort_values(count_col, ascending=True)
        
        if 'cluster_id' in top_clusters.columns:
            cluster_ids = top_clusters['cluster_id'].astype(str)
        elif 'cluster' in top_clusters.columns:
            cluster_ids = top_clusters['cluster'].astype(str)
        else:
            cluster_ids = top_clusters.reset_index()['index'].astype(str)
        
        top_clusters['label'] = 'Cluster ' + cluster_ids
        
        colors = ['#f59e0b', '#f97316', '#ef4444', '#ec4899', '#d946ef', '#c026d3', 
                  '#a855f7', '#9333ea', '#7c3aed', '#6366f1', '#3b82f6', '#0ea5e9']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_clusters[count_col],
            y=top_clusters['label'],
            orientation='h',
            marker=dict(
                color=colors[:len(top_clusters)],
                line=dict(width=0)
            ),
            text=top_clusters[count_col],
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Trips: %{x:,}<extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=90, r=80, t=10, b=40),
            xaxis=dict(
                title='',
                gridcolor='rgba(255,255,255,0.05)',
                showgrid=True,
                zeroline=False
            ),
            yaxis=dict(
                title='',
                gridcolor='rgba(0,0,0,0)',
                showgrid=False,
                automargin=True
            ),
            showlegend=False,
            height=280,
            bargap=0.2
        )
        
        return fig
    except Exception as e:
        print(f"Error in cluster chart: {e}")
        import traceback
        traceback.print_exc()
        fig = go.Figure()
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[{
                'text': 'Error loading cluster chart',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 12, 'color': '#ef4444'}
            }],
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=250
        )
        return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)