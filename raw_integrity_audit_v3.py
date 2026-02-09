#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAW INTEGRITY AUDIT - V3
Forenzicka analiza formatiranja brojeva i integriteta podataka
"""

import pandas as pd
import re
from decimal import Decimal, InvalidOperation

# ============================================================================
# UČITAVANJE PODATAKA
# ============================================================================

csv_path = "data - v3/campaign - metrics - v3 - segmented by ad format/campaign metrics version 3 - segmented by ad format.csv"

print("=" * 100)
print("RAW INTEGRITY AUDIT - CAMPAIGN METRICS V3")
print("=" * 100)
print(f"\nDatoteka: {csv_path}\n")

# Učitaj CSV sa UTF-8 encoding
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8-sig')

print(f"Ukupan broj redaka: {len(df):,}")
print(f"Broj kolona: {len(df.columns)}")
print(f"\nKolone: {list(df.columns)}\n")

# ============================================================================
# STEP 1: SIROVA DETEKCIJA FORMATA
# ============================================================================

print("=" * 100)
print("STEP 1: SIROVA DETEKCIJA FORMATA - COST STUPCA")
print("=" * 100)

print("\nPrvi 10 SIROVH vrijednosti iz Cost stupca (prije konverzije):\n")
for i, cost_value in enumerate(df['Cost'].head(10), 1):
    print(f"  {i:2d}. '{cost_value}' (tip: {type(cost_value).__name__})")

# Provjeri postoje li zapisi s tisućicama
print("\n\nPretraga velikih brojeva (> 10,000):\n")
large_costs = df[df['Cost'].astype(str).str.len() > 7].head(10)
if len(large_costs) > 0:
    for i, row in large_costs.iterrows():
        print(f"  Campaign: {row['Campaign'][:60]}...")
        print(f"  Raw Cost: '{row['Cost']}'")
        print()
else:
    print("  Nema brojeva vecih od 10,000 EUR u Cost stupcu")

# ============================================================================
# STEP 2: PANCIRNO ZBRAJANJE
# ============================================================================

print("=" * 100)
print("STEP 2: PANCIRNO PARSIRANJE I ZBRAJANJE")
print("=" * 100)

def parse_cost_robust(value):
    """
    Robusno parsiranje Cost vrijednosti.
    Pretpostavka: Americki format (tocka = decimale, zarez = tisucice)
    """
    if pd.isna(value):
        return 0.0

    # Konvertiraj u string
    value_str = str(value).strip()

    # Ukloni valutne simbole ako postoje
    value_str = value_str.replace('€', '').replace('EUR', '').strip()

    # Americki format: ukloni zareze (tisucice), zadrzi tocku (decimale)
    # Npr: 1,234.56 -> 1234.56
    value_str = value_str.replace(',', '')

    # Konvertiraj u float
    try:
        return float(value_str)
    except (ValueError, InvalidOperation):
        print(f"UPOZORENJE: Ne mogu parsirati '{value}' - postavljam na 0")
        return 0.0

# Primjeni parsiranje
df['Cost_parsed'] = df['Cost'].apply(parse_cost_robust)

# Provjeri postoje li bilo kakvi problemi
problematic = df[df['Cost_parsed'] == 0][df['Cost'].astype(str) != '0']
if len(problematic) > 0:
    print(f"\nUPOZORENJE: Pronadjeno {len(problematic)} problematicnih zapisa!")
    print("\nPrimjeri:")
    for i, row in problematic.head(5).iterrows():
        print(f"  Raw: '{row['Cost']}' -> Parsed: {row['Cost_parsed']}")
else:
    print("\nOK: Svi Cost zapisi uspjesno parsirani!")

# ============================================================================
# IZRACUN GRAND TOTAL
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: GRAND TOTAL SPEND CALCULATION")
print("=" * 100)

grand_total = df['Cost_parsed'].sum()

print(f"\n*** APSOLUTNI GRAND TOTAL SPEND (V3): EUR{grand_total:,.2f} ***\n")

# ============================================================================
# STEP 4: USPOREDBA S V2
# ============================================================================

print("=" * 100)
print("STEP 4: USPOREDBA S V2 AUDITOM")
print("=" * 100)

# Jedinstveni Campaign ID-evi
unique_campaigns_v3 = df['Campaign ID'].nunique()
unique_campaigns_v2 = 1522  # Iz prethodnog audita

print(f"\nBroj jedinstvenih Campaign ID-eva:")
print(f"  V2: {unique_campaigns_v2:,}")
print(f"  V3: {unique_campaigns_v3:,}")
print(f"  Razlika: {unique_campaigns_v3 - unique_campaigns_v2:+,}")

if unique_campaigns_v3 > unique_campaigns_v2:
    print(f"\n  --> NOVI ID-jevi su se pojavili! (+{unique_campaigns_v3 - unique_campaigns_v2})")
elif unique_campaigns_v3 < unique_campaigns_v2:
    print(f"\n  --> NEDOSTAJU ID-jevi! ({unique_campaigns_v3 - unique_campaigns_v2})")
else:
    print(f"\n  --> Broj ID-jeva ISTI")

# ============================================================================
# STEP 5: TOP 20 KAMPANJA CROSS-CHECK
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: TOP 20 KAMPANJA PO TROSKU (za rucnu verifikaciju)")
print("=" * 100)

# Grupiraj po Campaign ID i zbroji Cost (jer svaka kampanja moze imati vise ad formata)
campaign_totals = df.groupby(['Campaign ID', 'Campaign']).agg({
    'Cost_parsed': 'sum',
    'Ad format': lambda x: list(set(x))
}).reset_index()

campaign_totals = campaign_totals.sort_values('Cost_parsed', ascending=False)

print("\n")
print(f"{'Rank':<5} {'Campaign ID':<15} {'Cost (EUR)':<15} {'# Formats':<12} Campaign Name")
print("-" * 100)

for i, row in campaign_totals.head(20).iterrows():
    rank = campaign_totals.index.get_loc(i) + 1
    campaign_id = row['Campaign ID']
    cost = row['Cost_parsed']
    formats = row['Ad format']
    campaign_name = row['Campaign'][:60]

    print(f"{rank:<5} {campaign_id:<15} EUR{cost:>12,.2f} {len(formats):<12} {campaign_name}")

# ============================================================================
# DODATNE STATISTIKE
# ============================================================================

print("\n" + "=" * 100)
print("DODATNE STATISTIKE")
print("=" * 100)

# Broj redaka vs broj kampanja
print(f"\nBroj redaka ukupno: {len(df):,}")
print(f"Broj jedinstvenih kampanja: {unique_campaigns_v3:,}")
print(f"Prosjecan broj ad formata po kampanji: {len(df) / unique_campaigns_v3:.2f}")

# Raspodjela po ad formatima
print("\n\nTROSAK PO AD FORMATU:\n")
format_spend = df.groupby('Ad format')['Cost_parsed'].sum().sort_values(ascending=False)
for ad_format, spend in format_spend.items():
    percentage = (spend / grand_total) * 100
    print(f"  {ad_format:30s} - EUR{spend:12,.2f} ({percentage:5.2f}%)")

# Provjera nula
zero_cost_campaigns = df[df['Cost_parsed'] == 0]
print(f"\n\nBroj redaka s Cost = 0: {len(zero_cost_campaigns):,} ({len(zero_cost_campaigns)/len(df)*100:.2f}%)")

print("\n" + "=" * 100)
print("AUDIT ZAVRSEN")
print("=" * 100)
