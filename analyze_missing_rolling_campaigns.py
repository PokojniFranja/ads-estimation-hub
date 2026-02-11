#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSIS: Missing Campaigns in Rolling Reach Data
Identifies campaigns in MASTER file but not in ROLLING file
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("MISSING ROLLING REACH CAMPAIGNS ANALYSIS")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

print("\n[STEP 1] LOADING DATA...")
print("-" * 80)

# Load MASTER file
df_master = pd.read_csv('MASTER_ADS_HR_CLEANED.csv', delimiter=';', encoding='utf-8-sig')
print(f"MASTER file loaded: {len(df_master)} campaigns")

# Load ROLLING file
df_rolling = pd.read_csv('MASTER_ROLLING_DATA_2025_CLEAN.csv', encoding='utf-8-sig')
print(f"ROLLING file loaded: {len(df_rolling)} rows")

# Get unique Campaign IDs from rolling
rolling_campaigns = df_rolling['Campaign_ID'].unique()
print(f"Unique campaigns in ROLLING: {len(rolling_campaigns)}")

# ============================================================================
# STEP 2: IDENTIFY MISSING CAMPAIGNS
# ============================================================================

print("\n[STEP 2] IDENTIFYING MISSING CAMPAIGNS...")
print("-" * 80)

# Find campaigns in MASTER but not in ROLLING
df_master['Has_Rolling_Data'] = df_master['Campaign ID'].isin(rolling_campaigns)
df_missing = df_master[~df_master['Has_Rolling_Data']].copy()

print(f"Campaigns in MASTER but NOT in ROLLING: {len(df_missing)}")
print(f"Percentage missing: {len(df_missing)/len(df_master)*100:.1f}%")

# ============================================================================
# STEP 3: PARSE COST AND ANALYZE
# ============================================================================

print("\n[STEP 3] PARSING COST AND ANALYZING...")
print("-" * 80)

# Parse cost
def parse_cost(value):
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

df_missing['Cost_Parsed'] = df_missing['Cost'].apply(parse_cost)

# Total cost of missing campaigns
total_missing_cost = df_missing['Cost_Parsed'].sum()
total_all_cost = df_master['Cost'].apply(parse_cost).sum()

print(f"Total cost of MISSING campaigns: EUR {total_missing_cost:,.2f}")
print(f"Total cost of ALL campaigns: EUR {total_all_cost:,.2f}")
print(f"Missing campaigns represent: {total_missing_cost/total_all_cost*100:.2f}% of total cost")

# ============================================================================
# STEP 4: GROUP BY ACCOUNT AND BRAND
# ============================================================================

print("\n[STEP 4] GROUPING BY ACCOUNT AND BRAND...")
print("-" * 80)

# Group by Account
account_summary = df_missing.groupby('Account').agg({
    'Campaign ID': 'count',
    'Cost_Parsed': 'sum',
    'Ad_Format': lambda x: x.value_counts().to_dict()
}).reset_index()
account_summary.columns = ['Account', 'Campaign_Count', 'Total_Cost', 'Format_Breakdown']
account_summary = account_summary.sort_values('Campaign_Count', ascending=False)

print("\nMISSING CAMPAIGNS BY ACCOUNT:")
print(account_summary[['Account', 'Campaign_Count', 'Total_Cost']])

# Group by Brand
brand_summary = df_missing.groupby('Brand').agg({
    'Campaign ID': 'count',
    'Cost_Parsed': 'sum',
    'Ad_Format': lambda x: x.value_counts().to_dict()
}).reset_index()
brand_summary.columns = ['Brand', 'Campaign_Count', 'Total_Cost', 'Format_Breakdown']
brand_summary = brand_summary.sort_values('Campaign_Count', ascending=False)

print("\nMISSING CAMPAIGNS BY BRAND:")
print(brand_summary[['Brand', 'Campaign_Count', 'Total_Cost']])

# ============================================================================
# STEP 5: DETAILED CAMPAIGN LIST
# ============================================================================

print("\n[STEP 5] DETAILED CAMPAIGN LIST...")
print("-" * 80)

# Sort by cost descending
df_missing_sorted = df_missing.sort_values('Cost_Parsed', ascending=False)

# Save to CSV for detailed review
output_file = 'MISSING_ROLLING_CAMPAIGNS_DETAILED.csv'
df_missing_sorted[['Account', 'Brand', 'Campaign', 'Ad_Format', 'Cost_Parsed', 'Campaign ID']].to_csv(
    output_file, index=False, encoding='utf-8-sig'
)
print(f"Detailed list saved to: {output_file}")

# ============================================================================
# STEP 6: CRITICAL CAMPAIGNS (YouTube/Display with high cost)
# ============================================================================

print("\n[STEP 6] CRITICAL CAMPAIGNS ANALYSIS...")
print("=" * 80)

# Define critical formats
critical_formats = ['YouTube In-Stream', 'YouTube Bumper', 'YouTube Non-Skip', 'YouTube Shorts', 'Display']

# Filter critical campaigns
df_critical = df_missing[df_missing['Ad_Format'].isin(critical_formats)].copy()
df_critical_sorted = df_critical.sort_values('Cost_Parsed', ascending=False)

print(f"\n🚨 CRITICAL: YouTube/Display campaigns WITHOUT rolling reach data:")
print(f"Count: {len(df_critical)}")
print(f"Total Cost: EUR {df_critical['Cost_Parsed'].sum():,.2f}")

if len(df_critical) > 0:
    print("\nTOP 20 CRITICAL CAMPAIGNS (by cost):")
    print("-" * 80)

    for idx, row in df_critical_sorted.head(20).iterrows():
        print(f"\n{row['Campaign'][:80]}")
        print(f"  Account: {row['Account']}")
        print(f"  Brand: {row['Brand']}")
        print(f"  Format: {row['Ad_Format']}")
        print(f"  Cost: EUR {row['Cost_Parsed']:,.2f}")
        print(f"  Campaign ID: {row['Campaign ID']}")

    # Group critical by format
    critical_by_format = df_critical.groupby('Ad_Format').agg({
        'Campaign ID': 'count',
        'Cost_Parsed': 'sum'
    }).reset_index()
    critical_by_format.columns = ['Format', 'Count', 'Total_Cost']
    critical_by_format = critical_by_format.sort_values('Total_Cost', ascending=False)

    print("\n\nCRITICAL CAMPAIGNS BY FORMAT:")
    print(critical_by_format)

else:
    print("\n✅ NO CRITICAL YouTube/Display campaigns missing!")

# ============================================================================
# STEP 7: NON-CRITICAL CAMPAIGNS (Search/PMax)
# ============================================================================

print("\n[STEP 7] NON-CRITICAL CAMPAIGNS (Search/PMax)...")
print("-" * 80)

non_critical_formats = [fmt for fmt in df_missing['Ad_Format'].unique() if fmt not in critical_formats]
df_non_critical = df_missing[df_missing['Ad_Format'].isin(non_critical_formats)].copy()

print(f"\n✅ Non-critical campaigns (Search/PMax/Other):")
print(f"Count: {len(df_non_critical)}")
print(f"Total Cost: EUR {df_non_critical['Cost_Parsed'].sum():,.2f}")

if len(df_non_critical) > 0:
    non_critical_by_format = df_non_critical.groupby('Ad_Format').agg({
        'Campaign ID': 'count',
        'Cost_Parsed': 'sum'
    }).reset_index()
    non_critical_by_format.columns = ['Format', 'Count', 'Total_Cost']
    non_critical_by_format = non_critical_by_format.sort_values('Total_Cost', ascending=False)

    print("\nNON-CRITICAL CAMPAIGNS BY FORMAT:")
    print(non_critical_by_format)

# ============================================================================
# STEP 8: FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(f"\n📊 OVERALL STATISTICS:")
print(f"  Total campaigns in MASTER: {len(df_master)}")
print(f"  Campaigns with rolling reach: {len(df_master) - len(df_missing)}")
print(f"  Campaigns WITHOUT rolling reach: {len(df_missing)}")
print(f"  Missing percentage: {len(df_missing)/len(df_master)*100:.1f}%")

print(f"\n💰 COST IMPACT:")
print(f"  Cost of missing campaigns: EUR {total_missing_cost:,.2f}")
print(f"  Percentage of total cost: {total_missing_cost/total_all_cost*100:.2f}%")

print(f"\n🚨 CRITICAL CAMPAIGNS (YouTube/Display):")
print(f"  Count: {len(df_critical)}")
print(f"  Cost: EUR {df_critical['Cost_Parsed'].sum():,.2f}")
print(f"  Percentage of missing: {len(df_critical)/len(df_missing)*100:.1f}%")

print(f"\n✅ NON-CRITICAL CAMPAIGNS (Search/PMax):")
print(f"  Count: {len(df_non_critical)}")
print(f"  Cost: EUR {df_non_critical['Cost_Parsed'].sum():,.2f}")
print(f"  Percentage of missing: {len(df_non_critical)/len(df_missing)*100:.1f}%")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)

critical_cost_pct = (df_critical['Cost_Parsed'].sum() / total_missing_cost * 100) if total_missing_cost > 0 else 0

if critical_cost_pct > 20:
    print("\n🚨 HIGH PRIORITY: Significant YouTube/Display campaigns are missing!")
    print(f"   {critical_cost_pct:.1f}% of missing campaign cost is from critical formats.")
    print("   RECOMMENDATION: Re-export rolling reach data to include these campaigns.")
elif critical_cost_pct > 5:
    print("\n⚠️ MEDIUM PRIORITY: Some YouTube/Display campaigns are missing.")
    print(f"   {critical_cost_pct:.1f}% of missing campaign cost is from critical formats.")
    print("   RECOMMENDATION: Consider re-exporting if these are key campaigns.")
else:
    print("\n✅ LOW PRIORITY: Missing campaigns are mostly Search/PMax.")
    print(f"   Only {critical_cost_pct:.1f}% of missing cost is from critical formats.")
    print("   RECOMMENDATION: Current data is sufficient for reach estimation.")

print("\n" + "=" * 80)
print(f"Detailed analysis saved to: {output_file}")
print("=" * 80)
