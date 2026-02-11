#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROLLING REACH V2 - FULL PROCESSING & ANALYSIS
Sanitizes, maps, analyzes, and creates final master rolling file
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("ROLLING REACH V2 - PROCESSING PIPELINE")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD AND SANITIZE
# ============================================================================

print("\n[STEP 1] LOADING AND SANITIZING DATA...")
print("-" * 80)

# Load v2 rolling reach file
df_rolling = pd.read_csv('GAds - 90 days reach + freq - Rolling Script - v2 - Sheet1.csv',
                          encoding='utf-8-sig')

print(f"Initial rows: {len(df_rolling)}")
print(f"Columns: {list(df_rolling.columns)}")

# Check for 2026 data
df_rolling['Window_End'] = pd.to_datetime(df_rolling['Window_End'], errors='coerce')
df_rolling['Window_Start'] = pd.to_datetime(df_rolling['Window_Start'], errors='coerce')

rows_2026 = df_rolling[df_rolling['Window_End'].dt.year == 2026]
print(f"\n2026 data found: {len(rows_2026)} rows")

if len(rows_2026) > 0:
    print("Removing 2026 data...")
    df_rolling = df_rolling[df_rolling['Window_End'].dt.year != 2026]
    print(f"Rows after 2026 removal: {len(df_rolling)}")

# Check for duplicates (same Campaign_ID in same Window_Start)
if 'Campaign_ID' in df_rolling.columns:
    duplicates = df_rolling[df_rolling.duplicated(subset=['Campaign_ID', 'Window_Start'], keep=False)]
    print(f"\nDuplicates found: {len(duplicates)} rows")
    if len(duplicates) > 0:
        print("Sample duplicates:")
        print(duplicates[['Campaign_ID', 'Campaign', 'Window_Start', 'Reach']].head(10))

        # Keep first occurrence
        print("\nRemoving duplicates (keeping first occurrence)...")
        df_rolling = df_rolling.drop_duplicates(subset=['Campaign_ID', 'Window_Start'], keep='first')
        print(f"Rows after duplicate removal: {len(df_rolling)}")

# ============================================================================
# STEP 2: LOAD MASTER FILE AND MAP
# ============================================================================

print("\n[STEP 2] LOADING MASTER FILE AND MAPPING...")
print("-" * 80)

# Load MASTER file
df_master = pd.read_csv('MASTER_ADS_HR_CLEANED.csv', delimiter=';', encoding='utf-8')

print(f"MASTER file loaded: {len(df_master)} campaigns")
print(f"MASTER columns: {list(df_master.columns)}")

# Create mapping dictionaries from MASTER
campaign_to_format = dict(zip(df_master['Campaign ID'], df_master['Ad_Format']))
campaign_to_brand = dict(zip(df_master['Campaign ID'], df_master['Brand']))
campaign_to_target = dict(zip(df_master['Campaign ID'], df_master['Target']))
campaign_to_bid_strategy = dict(zip(df_master['Campaign ID'], df_master['Bid_Strategy_Short']))

# Map Type (Ad_Format) from MASTER
df_rolling['Type_Original'] = df_rolling['Type']  # Keep original
df_rolling['Type'] = df_rolling['Campaign_ID'].map(campaign_to_format)

# Map Brand from MASTER
df_rolling['Brand'] = df_rolling['Campaign_ID'].map(campaign_to_brand)

# Map additional fields
df_rolling['Target'] = df_rolling['Campaign_ID'].map(campaign_to_target)
df_rolling['Bid_Strategy'] = df_rolling['Campaign_ID'].map(campaign_to_bid_strategy)

# Check mapping success
mapped_type = df_rolling['Type'].notna().sum()
mapped_brand = df_rolling['Brand'].notna().sum()
unmapped = df_rolling['Type'].isna().sum()

print(f"\nMapping results:")
print(f"  Type mapped: {mapped_type}/{len(df_rolling)} ({mapped_type/len(df_rolling)*100:.1f}%)")
print(f"  Brand mapped: {mapped_brand}/{len(df_rolling)} ({mapped_brand/len(df_rolling)*100:.1f}%)")
print(f"  Unmapped rows: {unmapped} ({unmapped/len(df_rolling)*100:.1f}%)")

# Show unmapped campaigns
if unmapped > 0:
    print(f"\nUnmapped campaigns (sample):")
    unmapped_df = df_rolling[df_rolling['Type'].isna()][['Campaign_ID', 'Campaign', 'Account_Name']].drop_duplicates()
    print(unmapped_df.head(20))

# ============================================================================
# STEP 3: REACH ANALYSIS BY BRAND AND FORMAT
# ============================================================================

print("\n[STEP 3] REACH ANALYSIS BY BRAND AND FORMAT...")
print("-" * 80)

# Convert numeric columns
df_rolling['Cost'] = pd.to_numeric(df_rolling['Cost'], errors='coerce')
df_rolling['Reach'] = pd.to_numeric(df_rolling['Reach'], errors='coerce')
df_rolling['Impressions'] = pd.to_numeric(df_rolling['Impressions'], errors='coerce')
df_rolling['Avg_Frequency'] = pd.to_numeric(df_rolling['Avg_Frequency'], errors='coerce')

# Group by Brand and Type
brand_format_stats = df_rolling.groupby(['Brand', 'Type']).agg({
    'Reach': ['mean', 'median', 'min', 'max', 'count'],
    'Avg_Frequency': ['mean', 'median'],
    'Cost': 'sum',
    'Impressions': 'sum'
}).round(2)

print("\nAverage 90-day Reach and Frequency by Brand and Format:")
print(brand_format_stats.head(20))

# Overall statistics by Format
format_stats = df_rolling.groupby('Type').agg({
    'Reach': ['mean', 'median'],
    'Avg_Frequency': ['mean', 'median'],
    'Campaign_ID': 'nunique'
}).round(2)

print("\n\nOverall statistics by Format:")
print(format_stats)

# ============================================================================
# STEP 4: S-CURVE ANALYSIS (SATURATION)
# ============================================================================

print("\n[STEP 4] S-CURVE SATURATION ANALYSIS...")
print("-" * 80)

# Sort by Campaign_ID and Window_Start
df_rolling_sorted = df_rolling.sort_values(['Campaign_ID', 'Window_Start'])

# Find campaigns with multiple windows
campaign_window_counts = df_rolling_sorted.groupby('Campaign_ID').size()
multi_window_campaigns = campaign_window_counts[campaign_window_counts > 1]

print(f"Campaigns with multiple windows: {len(multi_window_campaigns)}")
print(f"Total campaigns: {df_rolling_sorted['Campaign_ID'].nunique()}")

# Analyze reach growth patterns
saturation_data = []

for campaign_id in multi_window_campaigns.index[:50]:  # Analyze top 50 campaigns
    campaign_data = df_rolling_sorted[df_rolling_sorted['Campaign_ID'] == campaign_id].copy()
    campaign_data = campaign_data.sort_values('Window_Start')

    if len(campaign_data) >= 3:  # Need at least 3 windows
        reaches = campaign_data['Reach'].values

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(reaches)):
            if reaches[i-1] > 0:
                growth_rate = (reaches[i] - reaches[i-1]) / reaches[i-1] * 100
                growth_rates.append(growth_rate)

        if len(growth_rates) >= 2:
            # Check if growth is slowing (saturation)
            early_growth = np.mean(growth_rates[:len(growth_rates)//2])
            late_growth = np.mean(growth_rates[len(growth_rates)//2:])

            saturation_indicator = 'Yes' if late_growth < early_growth * 0.5 else 'No'

            saturation_data.append({
                'Campaign_ID': campaign_id,
                'Campaign': campaign_data.iloc[0]['Campaign'],
                'Brand': campaign_data.iloc[0]['Brand'],
                'Windows': len(campaign_data),
                'Initial_Reach': reaches[0],
                'Peak_Reach': reaches.max(),
                'Final_Reach': reaches[-1],
                'Early_Growth_%': round(early_growth, 2),
                'Late_Growth_%': round(late_growth, 2),
                'Saturation': saturation_indicator
            })

df_saturation = pd.DataFrame(saturation_data)

if len(df_saturation) > 0:
    print("\nSaturation Analysis (Top campaigns with multiple windows):")
    print(df_saturation.head(20))

    saturated_count = len(df_saturation[df_saturation['Saturation'] == 'Yes'])
    print(f"\nCampaigns showing saturation: {saturated_count}/{len(df_saturation)} ({saturated_count/len(df_saturation)*100:.1f}%)")
else:
    print("\nNot enough data for saturation analysis")

# ============================================================================
# STEP 5: COMPARISON WITH MASTER FILE
# ============================================================================

print("\n[STEP 5] COMPARISON WITH MASTER FILE...")
print("-" * 80)

# Aggregate rolling data by Campaign_ID (peak reach across all windows)
rolling_agg = df_rolling.groupby('Campaign_ID').agg({
    'Reach': 'max',  # Peak reach
    'Avg_Frequency': 'mean',
    'Cost': 'sum',
    'Impressions': 'sum',
    'Brand': 'first',
    'Type': 'first',
    'Campaign': 'first'
}).reset_index()

# Get MASTER reach data
df_master['Peak_Reach'] = pd.to_numeric(df_master['Peak_Reach'], errors='coerce')

# Merge for comparison
comparison = rolling_agg.merge(
    df_master[['Campaign ID', 'Peak_Reach']],
    left_on='Campaign_ID',
    right_on='Campaign ID',
    how='left'
)

comparison['Reach_Diff_%'] = ((comparison['Reach'] - comparison['Peak_Reach']) / comparison['Peak_Reach'] * 100).round(2)

print("\nReach comparison (Rolling vs MASTER):")
print(f"  Rolling avg reach: {comparison['Reach'].mean():,.0f}")
print(f"  MASTER avg reach: {comparison['Peak_Reach'].mean():,.0f}")
print(f"  Average difference: {comparison['Reach_Diff_%'].mean():.2f}%")

print("\nSample comparisons:")
print(comparison[['Campaign', 'Brand', 'Reach', 'Peak_Reach', 'Reach_Diff_%']].head(15))

# ============================================================================
# STEP 6: CREATE FINAL MASTER ROLLING FILE
# ============================================================================

print("\n[STEP 6] CREATING FINAL MASTER ROLLING FILE...")
print("-" * 80)

# Select and order columns
final_columns = [
    'Window_Start',
    'Window_End',
    'Account_ID',
    'Account_Name',
    'Campaign_ID',
    'Campaign',
    'Brand',
    'Type',
    'Target',
    'Bid_Strategy',
    'Cost',
    'Impressions',
    'Reach',
    'Avg_Frequency'
]

df_final = df_rolling[final_columns].copy()

# Final cleanup
df_final = df_final.dropna(subset=['Type', 'Brand'])  # Remove unmapped rows

print(f"Final dataset: {len(df_final)} rows")
print(f"Unique campaigns: {df_final['Campaign_ID'].nunique()}")
print(f"Unique brands: {df_final['Brand'].nunique()}")
print(f"Unique accounts: {df_final['Account_ID'].nunique()}")

# Save to CSV
output_file = 'MASTER_ROLLING_DATA_2025_CLEAN.csv'
df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nFile saved: {output_file}")

# ============================================================================
# STEP 7: FINAL REPORT
# ============================================================================

print("\n[STEP 7] FINAL REPORT")
print("=" * 80)

total_original = len(pd.read_csv('GAds - 90 days reach + freq - Rolling Script - v2 - Sheet1.csv', encoding='utf-8-sig'))
total_after_sanitize = len(df_rolling)
total_mapped = len(df_final)

print("\nPROCESSING SUMMARY:")
print(f"  Original rows: {total_original}")
print(f"  After 2026 removal: {total_after_sanitize}")
print(f"  After duplicate removal: {total_after_sanitize}")
print(f"  Successfully mapped: {total_mapped}")
print(f"  Mapping success rate: {total_mapped/total_original*100:.1f}%")

print("\nDATA QUALITY:")
print(f"  Unique campaigns: {df_final['Campaign_ID'].nunique()}")
print(f"  Unique brands: {df_final['Brand'].nunique()}")
print(f"  Date range: {df_final['Window_Start'].min()} to {df_final['Window_End'].max()}")

print("\nBRAND BREAKDOWN:")
brand_counts = df_final.groupby('Brand').size().sort_values(ascending=False)
print(brand_counts.head(20))

print("\nFORMAT BREAKDOWN:")
format_counts = df_final.groupby('Type').size().sort_values(ascending=False)
print(format_counts)

print("\nANOMALIES DETECTED:")
anomalies = []

# Check for zero reach
zero_reach = df_final[df_final['Reach'] == 0]
if len(zero_reach) > 0:
    anomalies.append(f"  - {len(zero_reach)} rows with Reach = 0")

# Check for very high frequency (>20)
high_freq = df_final[df_final['Avg_Frequency'] > 20]
if len(high_freq) > 0:
    anomalies.append(f"  - {len(high_freq)} rows with Avg_Frequency > 20")

# Check for negative values
negative_cost = df_final[df_final['Cost'] < 0]
if len(negative_cost) > 0:
    anomalies.append(f"  - {len(negative_cost)} rows with negative Cost")

if anomalies:
    for anomaly in anomalies:
        print(anomaly)
else:
    print("  No major anomalies detected!")

print("\n" + "=" * 80)
print("PROCESSING COMPLETE!")
print("=" * 80)
print(f"\nOutput file: {output_file}")
print("Ready for reach estimation algorithm development.")
