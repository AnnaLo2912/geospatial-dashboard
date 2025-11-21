import pandas as pd

# Check what columns are in your cluster metrics file
print("=" * 60)
print("CHECKING CLUSTER METRICS FILE")
print("=" * 60)

try:
    metrics_df = pd.read_csv('outputs/dbscan_cluster_metrics.csv')
    print(f"\n✓ Found {len(metrics_df)} clusters")
    print(f"\nColumns in file:")
    for col in metrics_df.columns:
        print(f"  - {col}")
    
    print(f"\nFirst few rows:")
    print(metrics_df.head())
    
    print(f"\nData types:")
    print(metrics_df.dtypes)
    
except Exception as e:
    print(f"❌ Error reading cluster metrics: {e}")

print("\n" + "=" * 60)
print("CHECKING MAIN TAXI DATA FILE")
print("=" * 60)

try:
    taxi_df = pd.read_csv('outputs/merged_cleaned_taxi_data.csv', nrows=100)
    print(f"\nColumns in taxi data:")
    for col in taxi_df.columns:
        print(f"  - {col}")
    
    print(f"\nSample row:")
    print(taxi_df.iloc[0])
    
except Exception as e:
    print(f"❌ Error reading taxi data: {e}")