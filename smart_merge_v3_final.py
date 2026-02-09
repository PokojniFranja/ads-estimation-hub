#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMART MERGE & FINAL AUDIT - V3
Spajanje no segmentation (SIDRO) i segmented (YOUTUBE DETALJI)
"""

import pandas as pd
import numpy as np

# ============================================================================
# PATHS
# ============================================================================

path_master = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - no segmentation - all campaigns.csv"
path_segmented = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - segmented by ad format - only youtube campaigns.csv"

print("=" * 100)
print("SMART MERGE & FINAL AUDIT - V3 FINAL DATA")
print("=" * 100)

# ============================================================================
# STEP 1: PROVJERA SIDRA (NO SEGMENTATION = APSOLUTNA ISTINA)
# ============================================================================

print("\n" + "=" * 100)
print("STEP 1: PROVJERA FINANCIJSKOG SIDRA (No Segmentation)")
print("=" * 100)

df_master = pd.read_csv(path_master, delimiter=';', encoding='utf-8-sig')

print(f"\nDatoteka: {path_master}")
print(f"Broj redaka: {len(df_master):,}")
print(f"Broj kolona: {len(df_master.columns)}")
print(f"Kolone: {list(df_master.columns)}\n")

# Parsiraj Cost
def parse_cost(value):
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

df_master['Cost_parsed'] = df_master['Cost'].apply(parse_cost)

# GRAND TOTAL SPEND (APSOLUTNA ISTINA)
grand_total = df_master['Cost_parsed'].sum()

print(f"*** GRAND TOTAL SPEND (FINANCIJSKO SIDRO): EUR {grand_total:,.2f} ***\n")

if grand_total < 2_200_000 or grand_total > 2_400_000:
    print(f"UPOZORENJE: Grand Total ({grand_total:,.2f}) nije oko 2.3M!")
else:
    print(f"OK: Grand Total je u ocekivanom rangu (~2.3M)\n")

# Broj jedinstvenih kampanja
unique_campaigns_master = df_master['Campaign ID'].nunique()
print(f"Broj jedinstvenih kampanja u MASTER datoteci: {unique_campaigns_master:,}\n")

# ============================================================================
# STEP 2: UCITAJ YOUTUBE SEGMENTED DATA
# ============================================================================

print("=" * 100)
print("STEP 2: UCITAVANJE YOUTUBE SEGMENTED DATA")
print("=" * 100)

df_segmented = pd.read_csv(path_segmented, delimiter=';', encoding='utf-8-sig')

print(f"\nDatoteka: {path_segmented}")
print(f"Broj redaka: {len(df_segmented):,}")
print(f"Broj kolona: {len(df_segmented.columns)}")

# Parsiraj Cost u segmented
df_segmented['Cost_parsed'] = df_segmented['Cost'].apply(parse_cost)

# Youtube Total Spend
youtube_total = df_segmented['Cost_parsed'].sum()
unique_campaigns_youtube = df_segmented['Campaign ID'].nunique()

print(f"\nYouTube Segmented Spend: EUR {youtube_total:,.2f}")
print(f"Broj jedinstvenih YouTube kampanja: {unique_campaigns_youtube:,}\n")

# ============================================================================
# STEP 3: PAMETNO SPAJANJE
# ============================================================================

print("=" * 100)
print("STEP 3: PAMETNO SPAJANJE")
print("=" * 100)

# Kreiraj set Youtube Campaign ID-eva
youtube_campaign_ids = set(df_segmented['Campaign ID'].unique())

# Oznaci kampanje u MASTER datoteci
df_master['Has_YouTube_Segmentation'] = df_master['Campaign ID'].isin(youtube_campaign_ids)

# Broj kampanja sa i bez YouTube segmentacije
campaigns_with_youtube = df_master[df_master['Has_YouTube_Segmentation']]['Campaign ID'].nunique()
campaigns_without_youtube = df_master[~df_master['Has_YouTube_Segmentation']]['Campaign ID'].nunique()

print(f"\nKampanje SA YouTube segmentacijom: {campaigns_with_youtube:,}")
print(f"Kampanje BEZ YouTube segmentacije: {campaigns_without_youtube:,}")

# Izracunaj spend za kampanje bez YouTube segmentacije
spend_with_youtube = df_master[df_master['Has_YouTube_Segmentation']]['Cost_parsed'].sum()
spend_without_youtube = df_master[~df_master['Has_YouTube_Segmentation']]['Cost_parsed'].sum()

print(f"\nSpend (sa YouTube segmentacijom): EUR {spend_with_youtube:,.2f} ({spend_with_youtube/grand_total*100:.2f}%)")
print(f"Spend (bez YouTube segmentacije): EUR {spend_without_youtube:,.2f} ({spend_without_youtube/grand_total*100:.2f}%)")

# ============================================================================
# STEP 4: AUDIT REPORT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: AUDIT REPORT")
print("=" * 100)

print(f"""
FINANCIJSKI PREGLED:
-------------------
Total Spend (SIDRO):                EUR {grand_total:>14,.2f}  (100.00%)
YouTube Segmented Spend:            EUR {spend_with_youtube:>14,.2f}  ({spend_with_youtube/grand_total*100:>6.2f}%)
Other/Multi-channel Spend (GAP):    EUR {spend_without_youtube:>14,.2f}  ({spend_without_youtube/grand_total*100:>6.2f}%)

KAMPANJE:
---------
Ukupno kampanja:                    {unique_campaigns_master:>6,}
  - Sa YouTube segmentacijom:       {campaigns_with_youtube:>6,}  ({campaigns_with_youtube/unique_campaigns_master*100:>5.1f}%)
  - Bez segmentacije (Other):       {campaigns_without_youtube:>6,}  ({campaigns_without_youtube/unique_campaigns_master*100:>5.1f}%)
""")

# ============================================================================
# STEP 5: TOP 20 KAMPANJA VALIDATION
# ============================================================================

print("=" * 100)
print("STEP 5: TOP 20 KAMPANJA PO TROSKU (Validation)")
print("=" * 100)

# Sortiraj master po Cost
df_master_sorted = df_master.sort_values('Cost_parsed', ascending=False)

print("\n")
print(f"{'Rank':<5} {'Campaign ID':<15} {'Cost (EUR)':<15} {'YT Seg?':<10} Campaign Name")
print("-" * 100)

for i, row in df_master_sorted.head(20).iterrows():
    rank = df_master_sorted.index.get_loc(i) + 1
    campaign_id = row['Campaign ID']
    cost = row['Cost_parsed']
    has_yt = 'YES' if row['Has_YouTube_Segmentation'] else 'NO'
    campaign_name = row['Campaign'][:60]

    print(f"{rank:<5} {campaign_id:<15} EUR{cost:>12,.2f} {has_yt:<10} {campaign_name}")

# ============================================================================
# DODATNO: PROVJERA BRENDOVA U TOP 20
# ============================================================================

print("\n" + "=" * 100)
print("DODATNO: BRAND CHECK U TOP 20")
print("=" * 100)

def extract_brand_smart(campaign_name):
    """Pametnija ekstrakcija brenda iz naziva kampanje."""
    if pd.isna(campaign_name):
        return "Unknown"

    name = str(campaign_name)

    # Poznati brendovi za provjeru
    known_brands = {
        "McDonald": "McDonald's",
        "McDonalds": "McDonald's",
        "Kaufland": "Kaufland",
        "Nivea": "Nivea",
        "Philips": "Philips",
        "Henkel": "Henkel",
        "Persil": "Persil (Henkel)",
        "Perwoll": "Perwoll (Henkel)",
        "Syoss": "Syoss (Henkel)",
        "Weisser": "Weisser Riese (Henkel)",
        "Somat": "Somat (Henkel)",
        "Garnier": "Garnier",
        "OMV": "OMV",
        "Porsche": "Porsche",
        "Beiersdorf": "Beiersdorf",
        "Eucerin": "Eucerin (Beiersdorf)",
        "Ahmad": "Ahmad Tea",
        "reflustat": "Reflustat"
    }

    for key, brand in known_brands.items():
        if key.lower() in name.lower():
            return brand

    # Ako nije pronađen poznat brend, pokušaj izvući iz strukture
    parts = name.split('_')
    if len(parts) >= 4:
        return parts[3]
    elif len(parts) >= 2:
        return parts[1]
    else:
        return name.split()[0] if ' ' in name else name[:20]

# Dodaj Brand kolonu
df_master_sorted['Brand'] = df_master_sorted['Campaign'].apply(extract_brand_smart)

# Top brendovi
print("\nTop 10 brendova u Top 20 kampanja:\n")
top20_brands = df_master_sorted.head(20).groupby('Brand')['Cost_parsed'].sum().sort_values(ascending=False)

for i, (brand, spend) in enumerate(top20_brands.items(), 1):
    print(f"  {i:2d}. {brand:30s} - EUR {spend:>12,.2f}")

# Provjeri jesu li McDonald's i Kaufland u Top 20
mcdonalds_in_top20 = any('mcdonald' in str(row['Campaign']).lower() for _, row in df_master_sorted.head(20).iterrows())
kaufland_in_top20 = any('kaufland' in str(row['Campaign']).lower() for _, row in df_master_sorted.head(20).iterrows())

print(f"\n\nMcDonald's u Top 20: {'DA' if mcdonalds_in_top20 else 'NE'}")
print(f"Kaufland u Top 20:   {'DA' if kaufland_in_top20 else 'NE'}")

# ============================================================================
# DODATNO: BREAKDOWN PO AD FORMATIMA (YouTube kampanje)
# ============================================================================

print("\n" + "=" * 100)
print("DODATNO: BREAKDOWN PO AD FORMATIMA (samo YouTube kampanje)")
print("=" * 100)

format_breakdown = df_segmented.groupby('Ad format')['Cost_parsed'].sum().sort_values(ascending=False)

print("\n")
for ad_format, spend in format_breakdown.items():
    percentage = (spend / youtube_total) * 100 if youtube_total > 0 else 0
    print(f"  {ad_format:30s} - EUR {spend:>12,.2f} ({percentage:>5.2f}% od YT)")

print("\n" + "=" * 100)
print("AUDIT ZAVRSEN")
print("=" * 100)
