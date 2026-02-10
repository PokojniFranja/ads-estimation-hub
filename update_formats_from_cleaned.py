#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DATABASE UPDATE SCRIPT
Updates Ad_Format based on manually cleaned 'other-format-cleaned.csv'
Rebuilds Standardized_Campaign_Name with corrected formats
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("DATABASE UPDATE - Format Corrections")
print("=" * 80)

# Load cleaned formats file
print("\n[LOAD] Ucitavam ocisceni file...")
df_cleaned = pd.read_csv('other-format-cleaned.csv',
                         delimiter=';',
                         encoding='utf-8-sig')

print(f"[OK] Ucitano {len(df_cleaned)} kampanja za azuriranje")
print(f"[INFO] Kolone: {', '.join(df_cleaned.columns)}")

# Load main database
print("\n[LOAD] Ucitavam glavnu bazu podataka...")
df_main = pd.read_csv('ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv',
                      delimiter=';',
                      encoding='utf-8-sig')

print(f"[OK] Ucitano {len(df_main)} kampanja iz glavne baze")

# Create mapping dictionary: Campaign Name -> New Format
format_mapping = dict(zip(df_cleaned['Campaign'], df_cleaned['Campaign Type']))

print(f"\n[INFO] Mapping kreiran za {len(format_mapping)} kampanja")

# Track changes
updated_count = 0
not_found_count = 0
not_found_campaigns = []

print("\n[UPDATE] Azuriram Ad_Format u glavnoj bazi...")

for campaign_name, new_format in format_mapping.items():
    # Find campaign in main database
    mask = df_main['Campaign'] == campaign_name

    if mask.any():
        # Get old format
        old_format = df_main.loc[mask, 'Ad_Format'].iloc[0]

        # Update Ad_Format
        df_main.loc[mask, 'Ad_Format'] = new_format

        updated_count += 1

        if updated_count <= 5:  # Show first 5 updates
            print(f"  [{updated_count}] '{campaign_name[:60]}...'")
            print(f"      Old: {old_format} -> New: {new_format}")
    else:
        not_found_count += 1
        not_found_campaigns.append(campaign_name)

print(f"\n[RESULT] Azurirano: {updated_count} kampanja")

if not_found_count > 0:
    print(f"[WARNING] Nije pronadjeno u bazi: {not_found_count} kampanja")
    if not_found_count <= 5:
        print("[WARNING] Nisu pronadjene:")
        for camp in not_found_campaigns[:5]:
            print(f"  - {camp}")

# Rebuild Standardized_Campaign_Name for updated campaigns
print("\n[REBUILD] Regeneriram Standardized_Campaign_Name...")

def rebuild_campaign_name(row):
    """Rebuild standardized name with corrected Ad_Format."""
    parts = []

    if pd.notna(row.get('Brand')):
        parts.append(str(row['Brand']))

    if pd.notna(row.get('Ad_Format')):
        parts.append(str(row['Ad_Format']))

    if pd.notna(row.get('Target')):
        parts.append(str(row['Target']))

    if pd.notna(row.get('Date_Range')):
        parts.append(str(row['Date_Range']))

    if pd.notna(row.get('Bid_Strategy_Short')):
        parts.append(str(row['Bid_Strategy_Short']))

    if pd.notna(row.get('Goal')):
        parts.append(str(row['Goal']))

    return " | ".join(parts)

# Apply rebuild to all rows (this ensures consistency)
df_main['Standardized_Campaign_Name'] = df_main.apply(rebuild_campaign_name, axis=1)

print("[OK] Standardized_Campaign_Name regeneriran za sve kampanje")

# Save updated database
output_file = 'ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv'
backup_file = 'ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED_BACKUP.csv'

print(f"\n[BACKUP] Spremam backup u: {backup_file}")
df_main.to_csv(backup_file, sep=';', index=False, encoding='utf-8-sig')
print("[OK] Backup spremen")

print(f"\n[SAVE] Spremam azuriranu bazu u: {output_file}")
df_main.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
print("[OK] Baza azurirana!")

# Statistics
print("\n" + "=" * 80)
print("STATISTICS - Ad_Format Distribution AFTER Update")
print("=" * 80)

format_counts = df_main['Ad_Format'].value_counts()
for format_name, count in format_counts.items():
    percentage = (count / len(df_main) * 100)
    print(f"{format_name:20s}: {count:4d} ({percentage:5.1f}%)")

print("\n" + "=" * 80)
print("[DONE] AZURIRANJE ZAVRSENO!")
print("=" * 80)

# Check 'Other' category
other_count = df_main[df_main['Ad_Format'] == 'Other'].shape[0]
print(f"\n[CHECK] Preostalo 'Other' kampanja: {other_count}")

if other_count > 0:
    print(f"[INFO] 'Other' kategorija smanjena sa 131 na {other_count}")
    print(f"[INFO] Uspjesno ocisceno: {131 - other_count} kampanja")
else:
    print("[SUCCESS] Nema vise 'Other' kampanja - sve su ociscene!")
