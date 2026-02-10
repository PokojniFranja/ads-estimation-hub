#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT SCRIPT - Other Formats Analysis
Extracting campaigns with Ad_Format == 'Other' for manual review
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load data
print("[LOAD] Ucitavam bazu podataka...")
df = pd.read_csv('ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv',
                 delimiter=';',
                 encoding='utf-8-sig')

print(f"[OK] Ucitano ukupno {len(df)} kampanja\n")

# Filter for 'Other' formats
print("[FILTER] Filtriram kampanje s Ad_Format == 'Other'...")
df_other = df[df['Ad_Format'] == 'Other'].copy()

print(f"[FOUND] Pronadjeno {len(df_other)} kampanja s formatom 'Other'\n")

# Check which columns exist
required_columns = ['Brand', 'Standardized_Campaign_Name', 'Campaign']
optional_columns = ['Account', 'Account name']

# Determine account column name
account_col = None
if 'Account' in df_other.columns:
    account_col = 'Account'
elif 'Account name' in df_other.columns:
    account_col = 'Account name'

# Extract required columns
if account_col:
    columns_to_extract = ['Brand', 'Standardized_Campaign_Name', 'Campaign', account_col]
else:
    columns_to_extract = ['Brand', 'Standardized_Campaign_Name', 'Campaign']
    print("[WARNING] UPOZORENJE: Stupac 'Account' nije pronadjen u bazi!\n")

df_audit = df_other[columns_to_extract].copy()

# Rename account column to 'Account' for consistency
if account_col and account_col != 'Account':
    df_audit.rename(columns={account_col: 'Account'}, inplace=True)

# Export to CSV
output_file = 'other_formats_audit_list.csv'
df_audit.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')

print(f"[EXPORT] USPJESAN: {output_file}")
print(f"[INFO] Broj redova: {len(df_audit)}")
print(f"[INFO] Stupci: {', '.join(df_audit.columns)}\n")

print("=" * 80)
print("PRVIH 20 REZULTATA:")
print("=" * 80)

# Display first 20 results
for idx, row in df_audit.head(20).iterrows():
    print(f"\n[{idx + 1}] BRAND: {row['Brand']}")
    print(f"    STANDARDIZED: {row['Standardized_Campaign_Name']}")
    print(f"    ORIGINAL: {row['Campaign']}")
    if 'Account' in row:
        print(f"    ACCOUNT: {row['Account']}")
    print("-" * 80)

print(f"\n[DONE] AUDIT ZAVRSEN!")
print(f"[FILE] Otvori file: {output_file}")
print(f"[TOTAL] Ukupno 'Other' kampanja: {len(df_audit)}")
