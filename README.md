# 🚕 NYC Taxi Analytics Dashboard

An interactive geospatial dashboard for analyzing NYC Yellow Taxi trip data using DBSCAN clustering and advanced visualizations.

---

## 🎯Overview

This project analyzes **200,000 NYC Yellow Taxi trips** from **January 2015**, identifying pickup hotspots using **DBSCAN clustering** and visualizing patterns through an interactive web dashboard built with **Dash and Plotly**.

The dashboard enables users to:

- Explore taxi pickup patterns across NYC  
- Filter data by date ranges and time of day  
- Switch between scatter plots, heatmaps, and cluster visualizations  
- Identify high-density pickup zones and temporal patterns  

> **Note:** While the preprocessing phase handled **46 million records** (Jan 2015 – Mar 2016), the deployed dashboard uses a **200K sample from January 2015** for optimal performance.

---

## ✨Features

### 📊 Interactive Visualizations
- Scatter Plot – view individual pickup points (up to 5,000 sampled)
- Heatmap – density-based visualization with color gradients
- DBSCAN Clusters – 149 identified pickup hotspots with color-coded circles

### 🔍 Advanced Filtering
- Date selection (single day or range)
- Time of day (morning, midday, evening, night)
- Real-time updates for trips, clusters, and average fares

### 🗺️ Location Intelligence
- Click any map point to view neighborhood (via OpenStreetMap API)
- GPS coordinate precision (4-decimal)
- Direct Google Maps link

### 📈 Analytics Charts
- Trips by date (daily/hourly)
- Pickups by hour (24-hour distribution)
- Cluster distribution (Top 12 clusters)

### 💡 User-Friendly Features
- "Explain View" button
- First-time user guide
- Responsive layout (desktop & tablet friendly)

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Python 3.9+ |
| Dashboard Framework | Dash 2.14+ |
| Visualizations | Plotly |
| Geospatial Processing | GeoPandas, Shapely |
| Data Manipulation | Pandas, NumPy |
| Clustering | scikit-learn (DBSCAN) |
| Mapping | OpenStreetMap (Plotly Mapbox) |
| Styling | Custom CSS, Plus Jakarta Sans |

---

## 📁 Project Structure

```text
geospatial_dashboard/
│
├── data/                          # Raw CSV datasets (not included in repo)
│   └── (Download from Kaggle separately)
│
├── data_cache/                    # Cached files from Google Drive
│   ├── metrics.csv
│   ├── merged_sample.geojson
│   └── (Auto-downloaded on first run)
│
├── outputs/                       # Original processed data (46M rows)
│   ├── cleaned_yellow_tripdata_*.csv
│   ├── merged_cleaned_taxi_data.csv
│   └── (Not deployed, too large)
│
├── scripts/                       # Data processing scripts
│   ├── check_data.py
│   └── fix_cluster_metrics.py
│
├── notebooks/                     # Jupyter notebooks
│
├── app.py                         # Main dashboard application
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python version for deployment
├── .renderignore                  # Deployment ignores
├── Procfile                       # Render deployment config
├── README.md                      # Documentation
└── .gitignore
```
---

## 🔄 Data Flow

Raw Data → Cleaning → Clustering → Sampling → Google Drive → Dashboard

---

## 🚀Installation

### Prerequisites
- Python 3.9+
- pip package manager
- Minimum 2GB RAM
- Internet connection

---

### Data Source

The dashboard auto-downloads these files on first run:

- **metrics.csv** – Cluster stats (149 clusters)
- **merged_sample.geojson** – 200K trip records

✅ No manual data download required.

---

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/nyc-taxi-analytics.git
cd nyc-taxi-analytics
```

Step 2: Create Virtual Environment
```bash
python -m venv venv
```
Step 3: Activate Environment

Windows (PowerShell)
```bash
.\venv\Scripts\activate
```

Mac/Linux
```bash
source venv/bin/activate
```
Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```
---

## 💻Usage
Run the Dashboard
```bash
cd geospatial_dashboard

python app.py
```
Access in Browser

Open:

http://127.0.0.1:8050


OR

http://localhost:8050

Stop Server

Press:

Ctrl + C

👋 First-Time Setup

The dashboard automatically shows a welcome walkthrough.

Click "Get Started" to begin.

---

## 🙏Acknowledgments
 
Dataset

Kaggle — NYC Yellow Taxi Trips

Libraries & Tools

Dash & Plotly — Plotly Technologies Inc.

GeoPandas — GeoPandas Developers

OpenStreetMap — Contributors

Nominatim API — OpenStreetMap Foundation

## 👤Author

Anastasia Lopes

🔗 LinkedIn
https://www.linkedin.com/in/anastasia-lopes-680909303

📧 Email
anastasialopes2912@gmail.com



