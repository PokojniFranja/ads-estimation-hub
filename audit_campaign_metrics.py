#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMPAIGN METRICS - V2 AUDIT
Analiza apsolutnog Total Spend-a bez filtera
"""

import pandas as pd
import re
from collections import defaultdict

# Učitaj CSV
csv_path = "data - v2/campaign metrics - v2/campaign metrics - v2.csv"
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8-sig')

print("=" * 80)
print("CAMPAIGN METRICS - V2 AUDIT")
print("=" * 80)

# Osnovne informacije
print(f"\nDatoteka: {csv_path}")
print(f"Ukupan broj redaka: {len(df):,}")
print(f"Broj kolona: {len(df.columns)}")
print(f"\nKolone: {list(df.columns)}\n")

# Provjera Cost kolone
print("=" * 80)
print("COST ANALIZA")
print("=" * 80)

# Konvertiraj Cost u numerički format (ukloni € i zapete)
df['Cost_numeric'] = df['Cost'].astype(str).str.replace('€', '').str.replace(',', '.').str.strip()
df['Cost_numeric'] = pd.to_numeric(df['Cost_numeric'], errors='coerce').fillna(0)

# APSOLUTNI TOTAL SPEND (bez ikakvih filtera)
grand_total = df['Cost_numeric'].sum()
print(f"\n GRAND TOTAL SPEND (svi ad formati, svi statusi): €{grand_total:,.2f}")

# Provjera duplikata - jedna kampanja s više ad formata
print("\n" + "=" * 80)
print(" PROVJERA: Jedna kampanja = više Ad formata?")
print("=" * 80)

# Group by Campaign ID i broji ad formate
campaign_formats = df.groupby('Campaign ID')['Ad format'].apply(list).reset_index()
campaign_formats['format_count'] = campaign_formats['Ad format'].apply(len)

# Kampanje s više od 1 ad formata
multi_format = campaign_formats[campaign_formats['format_count'] > 1]
print(f"\n Broj kampanja s više od 1 Ad formata: {len(multi_format)}")

if len(multi_format) > 0:
    print("\n Primjeri kampanja s više Ad formata (prvih 10):")
    for idx, row in multi_format.head(10).iterrows():
        campaign_id = row['Campaign ID']
        formats = set(row['Ad format'])

        # Dohvati naziv kampanje
        campaign_name = df[df['Campaign ID'] == campaign_id]['Campaign'].iloc[0]

        # Dohvati total cost za ovu kampanju (zbroj svih formata)
        campaign_cost = df[df['Campaign ID'] == campaign_id]['Cost_numeric'].sum()

        print(f"\n  Campaign ID: {campaign_id}")
        print(f"  Naziv: {campaign_name[:80]}...")
        print(f"  Ad formati: {', '.join(formats)}")
        print(f"  Total Cost: €{campaign_cost:,.2f}")

# Izvlačenje brenda iz naziva kampanje
print("\n" + "=" * 80)
print(" TOP 10 BRENDOVA PO TROŠKU")
print("=" * 80)

def extract_brand(campaign_name):
    """
    Izvlači brend iz naziva kampanje.
    Format: VID_OMD_[MARKET]_[BRAND]_...
    Ili: [BRAND]_...
    """
    if pd.isna(campaign_name):
        return "Unknown"

    parts = str(campaign_name).split('_')

    # Provjeri je li naziv u standardnom formatu (VID_OMD_...)
    if len(parts) >= 4 and parts[0] in ['VID', 'DISP', 'PMAX', 'DG']:
        # Četvrti dio je obično brand (nakon VID_OMD_MARKET_)
        brand = parts[3]
        return brand
    elif len(parts) >= 2:
        # Ako nije standardni format, uzmi prvi dio koji izgleda kao brend
        # Provjeri neki poznate brendove
        known_brands = ['McDonalds', 'Nivea', 'Philips', 'Kaufland', 'OMV', 'Beiersdorf', 'Garnier']
        for part in parts:
            if any(kb.lower() in part.lower() for kb in known_brands):
                return part
        # Ako nije pronađen, uzmi drugi dio
        return parts[1] if len(parts) > 1 else parts[0]
    else:
        return parts[0] if len(parts) > 0 else "Unknown"

# Dodaj brend kolonu
df['Brand'] = df['Campaign'].apply(extract_brand)

# Grupiraj po brendovima
brand_spend = df.groupby('Brand')['Cost_numeric'].sum().sort_values(ascending=False)

print("\n TOP 10 BRENDOVA:\n")
for i, (brand, spend) in enumerate(brand_spend.head(10).items(), 1):
    percentage = (spend / grand_total) * 100
    print(f"{i:2d}. {brand:20s} - €{spend:12,.2f} ({percentage:5.2f}%)")

# Dodatne statistike
print("\n" + "=" * 80)
print(" DODATNE STATISTIKE")
print("=" * 80)

unique_campaigns = df['Campaign ID'].nunique()
unique_formats = df['Ad format'].nunique()
formats_list = df['Ad format'].unique()

print(f"\n Broj jedinstvenih kampanja: {unique_campaigns:,}")
print(f" Broj različitih Ad formata: {unique_formats}")
print(f" Ad formati: {', '.join(formats_list)}")

# Raspored po Ad formatima
print("\n TROŠAK PO AD FORMATU:\n")
format_spend = df.groupby('Ad format')['Cost_numeric'].sum().sort_values(ascending=False)
for ad_format, spend in format_spend.items():
    percentage = (spend / grand_total) * 100
    print(f"  {ad_format:30s} - €{spend:12,.2f} ({percentage:5.2f}%)")

print("\n" + "=" * 80)
print(" AUDIT ZAVRŠEN")
print("=" * 80)
