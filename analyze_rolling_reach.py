#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALIZA NOVOG ROLLING REACH EKSPORTA
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("1. ANALIZA ACCOUNT_ID-OVA")
print("=" * 80)

# Load new rolling reach file
df_new = pd.read_csv('GAds - 90 days reach + freq - Rolling Script - Sheet1.csv', encoding='utf-8-sig')

# Count unique Account IDs
unique_accounts = sorted(df_new['Account_ID'].dropna().unique().tolist())
print(f"\nUkupno jedinstvenih Account_ID-ova: {len(unique_accounts)}\n")

# Print all Account IDs with their names
account_mapping = df_new[['Account_ID', 'Account_Name']].drop_duplicates().sort_values('Account_ID')
print("POPIS ACCOUNT_ID-OVA S NAZIVIMA:")
print("-" * 80)
for idx, row in account_mapping.iterrows():
    # Handle encoding issues
    acc_name = str(row['Account_Name']).encode('ascii', 'replace').decode('ascii')
    print(f"{row['Account_ID']:15s} | {acc_name}")

print("\n" + "=" * 80)
print("2. PROVJERA KVALITETE PODATAKA")
print("=" * 80)

# Check for Reach=0 but Cost>0
df_new['Cost'] = pd.to_numeric(df_new['Cost'], errors='coerce')
df_new['Reach'] = pd.to_numeric(df_new['Reach'], errors='coerce')
df_new['Impressions'] = pd.to_numeric(df_new['Impressions'], errors='coerce')
df_new['Avg_Frequency'] = pd.to_numeric(df_new['Avg_Frequency'], errors='coerce')

problematic = df_new[(df_new['Reach'] == 0) & (df_new['Cost'] > 0)]
print(f"\nRedova gdje je Reach = 0 a Cost > 0: {len(problematic)}")
if len(problematic) > 0:
    print("\nPrimjeri problematičnih redova:")
    print(problematic[['Account_Name', 'Campaign', 'Cost', 'Reach', 'Impressions']].head(10))

# Check for negative values
print(f"\nRedova s negativnim Cost: {len(df_new[df_new['Cost'] < 0])}")
print(f"Redova s negativnim Reach: {len(df_new[df_new['Reach'] < 0])}")
print(f"Redova s negativnim Impressions: {len(df_new[df_new['Impressions'] < 0])}")

print("\n" + "=" * 80)
print("3. ANALIZA AVG_FREQUENCY PO TIPU KAMPANJE")
print("=" * 80)

# Convert Type to string first
df_new['Type'] = df_new['Type'].astype(str)

# Group by Type
freq_by_type = df_new.groupby('Type')['Avg_Frequency'].agg(['mean', 'median', 'min', 'max', 'count'])
print("\nFrekvencija po tipu kampanje:")
print(freq_by_type)

# Separate Display vs Video
display_freq = df_new[df_new['Type'].str.contains('Display', case=False, na=False)]['Avg_Frequency']
video_freq = df_new[df_new['Type'].str.contains('Video', case=False, na=False)]['Avg_Frequency']

if len(video_freq) > 0:
    print(f"\n📺 VIDEO kampanje - Avg Frequency: {video_freq.mean():.2f} (median: {video_freq.median():.2f})")
if len(display_freq) > 0:
    print(f"📱 DISPLAY kampanje - Avg Frequency: {display_freq.mean():.2f} (median: {display_freq.median():.2f})")

print("\n" + "=" * 80)
print("4. USPOREDBA SA MASTER FILE-OM")
print("=" * 80)

# Load MASTER file
df_master = pd.read_csv('MASTER_ADS_HR_CLEANED.csv', delimiter=';', encoding='utf-8')

# Compare Account coverage
master_accounts = df_master['Account'].nunique()
print(f"\nMASTER file - Unique Accounts: {master_accounts}")
print(f"ROLLING REACH file - Unique Account_IDs: {len(unique_accounts)}")
print(f"Razlika: {len(unique_accounts) - master_accounts} Account_ID-ova")

# Calculate CPM in rolling reach file
df_new['CPM'] = (df_new['Cost'] / df_new['Impressions'] * 1000)

# Aggregate rolling reach by campaign
rolling_agg = df_new.groupby('Campaign').agg({
    'Cost': 'sum',
    'Impressions': 'sum',
    'Reach': 'max',  # Peak reach
    'Avg_Frequency': 'mean'
}).reset_index()
rolling_agg['CPM'] = (rolling_agg['Cost'] / rolling_agg['Impressions'] * 1000)

print(f"\nNOVI ROLLING REACH DATA:")
print(f"  Total Cost: €{rolling_agg['Cost'].sum():,.2f}")
print(f"  Total Impressions: {rolling_agg['Impressions'].sum():,.0f}")
print(f"  Average CPM: €{rolling_agg['CPM'].mean():.2f}")
print(f"  Average Reach per campaign: {rolling_agg['Reach'].mean():,.0f}")
print(f"  Average Frequency: {rolling_agg['Avg_Frequency'].mean():.2f}")

print(f"\nMASTER FILE DATA:")
# Convert to numeric
df_master['Cost'] = pd.to_numeric(df_master['Cost'], errors='coerce')
df_master['Impr.'] = pd.to_numeric(df_master['Impr.'], errors='coerce')
print(f"  Total Cost: €{df_master['Cost'].sum():,.2f}")
print(f"  Total Impressions: {df_master['Impr.'].sum():,.0f}")
if 'Avg. CPM' in df_master.columns:
    df_master['Avg. CPM'] = pd.to_numeric(df_master['Avg. CPM'], errors='coerce')
    print(f"  Average CPM: €{df_master['Avg. CPM'].mean():.2f}")
if 'Peak_Reach' in df_master.columns:
    df_master['Peak_Reach'] = pd.to_numeric(df_master['Peak_Reach'], errors='coerce')
    print(f"  Average Peak Reach: {df_master['Peak_Reach'].mean():,.0f}")

print("\n" + "=" * 80)
print("5. ZAKLJUČAK I PREPORUKE")
print("=" * 80)

# Data quality score
quality_score = 100
issues = []

if len(problematic) > 0:
    quality_score -= 10
    issues.append(f"❌ {len(problematic)} redova s Reach=0 ali Cost>0")
else:
    issues.append("✅ Nema redova s Reach=0 i Cost>0")

if df_new['Reach'].isna().sum() > 0:
    quality_score -= 5
    issues.append(f"⚠️ {df_new['Reach'].isna().sum()} redova bez Reach podataka")
else:
    issues.append("✅ Svi redovi imaju Reach podatke")

if df_new['Avg_Frequency'].isna().sum() > 0:
    quality_score -= 5
    issues.append(f"⚠️ {df_new['Avg_Frequency'].isna().sum()} redova bez Avg_Frequency")
else:
    issues.append("✅ Svi redovi imaju Avg_Frequency")

if len(unique_accounts) < master_accounts:
    quality_score -= 15
    issues.append(f"❌ Manje Account_ID-ova nego u MASTER file-u ({len(unique_accounts)} vs {master_accounts})")
elif len(unique_accounts) > master_accounts:
    quality_score += 10
    issues.append(f"✅ VIŠE Account_ID-ova nego u MASTER file-u ({len(unique_accounts)} vs {master_accounts})")
else:
    issues.append(f"✅ Isti broj Account_ID-ova kao u MASTER file-u")

print(f"\n📊 QUALITY SCORE: {quality_score}/100")
print("\nISSUES:")
for issue in issues:
    print(f"  {issue}")

if quality_score >= 85:
    print("\n✅ PREPORUKA: Podaci su DOVOLJNO DOBRI za novi standard reach estimacije")
elif quality_score >= 70:
    print("\n⚠️ PREPORUKA: Podaci su OK, ali trebaju MANJE POPRAVKE")
else:
    print("\n❌ PREPORUKA: Podaci trebaju ZNAČAJNE POPRAVKE prije upotrebe")

print("\n" + "=" * 80)
