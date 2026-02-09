#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVJERA ACCOUNT FILTERA
Analiza mogućih filtera koji mogu objasniti razliku između 74 i 56 accounta
"""

import pandas as pd
from datetime import datetime

# ============================================================================
# UCITAJ CAMPAIGN METRICS
# ============================================================================

path_no_seg = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - no segmentation - all campaigns.csv"

print("=" * 100)
print("ANALIZA MOGUCIH FILTERA - Zasto 74 accounta u Report Editoru, a samo 56 u CSV-u?")
print("=" * 100)

df = pd.read_csv(path_no_seg, delimiter=';', encoding='utf-8-sig')

print(f"\nUkupno kampanja u CSV-u: {len(df)}")
print(f"Ukupno unikatnih Campaign ID-eva: {df['Campaign ID'].nunique()}")
print(f"Ukupno unikatnih Accounta: {df['Account'].nunique()}\n")

# Parse Cost
def parse_cost(value):
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

df['Cost_parsed'] = df['Cost'].apply(parse_cost)

# ============================================================================
# PROVJERA 1: ACCOUNTI SA ZERO SPEND
# ============================================================================

print("=" * 100)
print("PROVJERA 1: POSTOJE LI ACCOUNTI SA ZERO SPEND?")
print("=" * 100)

account_spend = df.groupby('Account')['Cost_parsed'].sum()
zero_spend_accounts = account_spend[account_spend == 0]

print(f"\nBroj accounta sa spend = 0: {len(zero_spend_accounts)}")

if len(zero_spend_accounts) > 0:
    print("\nAccounti sa zero spend:")
    for account in zero_spend_accounts.index:
        num_campaigns = df[df['Account'] == account]['Campaign ID'].nunique()
        print(f"  - {account} ({num_campaigns} kampanja)")

# ============================================================================
# PROVJERA 2: KAMPANJE SA ZERO SPEND
# ============================================================================

print("\n" + "=" * 100)
print("PROVJERA 2: KOLIKO KAMPANJA IMA ZERO SPEND?")
print("=" * 100)

zero_spend_campaigns = df[df['Cost_parsed'] == 0]
print(f"\nBroj kampanja sa cost = 0: {len(zero_spend_campaigns)} ({len(zero_spend_campaigns)/len(df)*100:.2f}%)")

# Accounti koji imaju barem jednu kampanju sa zero spend
accounts_with_zero = zero_spend_campaigns['Account'].unique()
print(f"Broj accounta koji imaju barem 1 kampanju sa zero spend: {len(accounts_with_zero)}")

# ============================================================================
# PROVJERA 3: ANALIZA KAMPANJA - PERIOD
# ============================================================================

print("\n" + "=" * 100)
print("PROVJERA 3: ANALIZA NAZIVA KAMPANJA - PERIOD")
print("=" * 100)

# Pokusaj izvuci godine iz naziva kampanja
def extract_year(campaign_name):
    """Izvuci godinu iz naziva kampanje."""
    if pd.isna(campaign_name):
        return None

    name = str(campaign_name)

    # Trazi godine 2024, 2025, 2026
    if '2026' in name:
        return 2026
    elif '2025' in name:
        return 2025
    elif '2024' in name:
        return 2024
    elif '2023' in name:
        return 2023
    else:
        return None

df['Year'] = df['Campaign'].apply(extract_year)

year_distribution = df['Year'].value_counts().sort_index()
print("\nDistribucija kampanja po godinama (iz naziva):")
for year, count in year_distribution.items():
    if pd.notna(year):
        print(f"  {int(year)}: {count} kampanja")
    else:
        print(f"  Unknown: {count} kampanja")

# ============================================================================
# PROVJERA 4: MINIMUM SPEND THRESHOLD
# ============================================================================

print("\n" + "=" * 100)
print("PROVJERA 4: DISTRIBUCIJA ACCOUNTA PO SPEND THRESHOLDIMA")
print("=" * 100)

account_spend_sorted = account_spend.sort_values(ascending=False)

thresholds = [0, 100, 500, 1000, 5000, 10000]

print("\nBroj accounta po spend threshold-ima:\n")
for threshold in thresholds:
    count = len(account_spend_sorted[account_spend_sorted > threshold])
    print(f"  Spend > EUR {threshold:>6,}: {count} accounta")

# ============================================================================
# PROVJERA 5: POKUSAJ DETEKTIRATI MISSING ACCOUNTE
# ============================================================================

print("\n" + "=" * 100)
print("PROVJERA 5: MOGUCE HIPOTEZE ZA RAZLIKU (74 vs 56)")
print("=" * 100)

print(f"""
TRENUTNA SITUACIJA:
- Google Ads Report Editor: 74 accounta odabrano
- Campaign Metrics CSV:     56 accounta sa podacima
- Razlika:                  18 accounta (~24%)

MOGUCE HIPOTEZE:

1. PERIOD FILTER
   CSV mozda sadrzi samo kampanje iz odredjenog perioda (npr. Q1 2026),
   dok 18 accounta nema aktivnih kampanja u tom periodu.

   PROVJERA: Distribucija godina u CSV-u:
   {year_distribution.to_dict()}

2. COST THRESHOLD
   CSV mozda ima filter 'Cost > 0' ili neki minimalni spend.

   PROVJERA: Accounti sa zero spend: {len(zero_spend_accounts)}
   (Ovo ne objasnjava razliku!)

3. CAMPAIGN STATUS
   CSV mozda sadrzi samo 'Enabled' ili 'Active' kampanje,
   dok 18 accounta ima samo 'Paused/Removed' kampanje.

   PROVJERA: Nema 'Status' kolone u CSV-u.

4. HIERARCHIJA ACCOUNTA
   Report Editor mozda broji MCC sub-accounte odvojeno,
   dok CSV grupira ih pod parent account.

   PROVJERA: Trebas provjeriti u Report Editoru jesu li neki accounti
   grupirani hierarhijski.

5. PRAZAN EXPORT
   18 accounta mozda nema nikakvih kampanja koje matchaju filter u Report Editoru,
   pa su izostavljeni iz CSV-a.

PREPORUKA:
----------
U Google Ads Report Editoru:
1. Provjeri koliko od tih 74 accounta ima "Campaigns: > 0"
2. Provjeri koliko od tih 74 accounta ima "Cost: > 0"
3. Provjeri je li filter postavljen na neki period (Date range)
4. Provjeri jesu li neki accounti u hierarchiji (MCC struktura)

Alternativno:
- Napravi export SA SVIM dostupnim accountima BEZ filtera
- Usporedi total spend - ako je i dalje ~EUR 2.3M, znaci da 18 accounta
  stvarno nema podataka u ovom periodu
""")

print("\n" + "=" * 100)
print("DODATNO: TOP 10 NAJMANJIH ACCOUNTA (po spend-u)")
print("=" * 100)

print("\nMozda su ovi na granici filtera?\n")
smallest_accounts = account_spend_sorted.tail(10).sort_values()

for account, spend in smallest_accounts.items():
    num_campaigns = df[df['Account'] == account]['Campaign ID'].nunique()
    print(f"  {account[:50]:50s} - EUR {spend:>10,.2f} ({num_campaigns} kampanja)")

print("\n" + "=" * 100)
