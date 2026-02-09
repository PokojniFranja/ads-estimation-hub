#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVJERA CROATIA SPEND - iz country file-a
"""

import pandas as pd

def parse_cost(value):
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

# Ucitaj country file
PATH_COUNTRY = "data - v3/campaign - country - v3/campaign location - version 3.csv"

df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')
df_country['Cost_parsed'] = df_country['Cost'].apply(parse_cost)

print("COUNTRY FILE ANALIZA")
print("=" * 80)

print(f"\nUkupno redaka u country file-u: {len(df_country):,}")
print(f"Ukupno unikatnih Campaign ID-eva: {df_country['Campaign ID'].nunique():,}")

# Croatia redovi
df_croatia = df_country[df_country['Country/Territory (User location)'] == 'Croatia']

print(f"\nRedovi sa Croatia lokacijom: {len(df_croatia):,}")
print(f"Broj unikatnih Campaign ID-eva (Croatia): {df_croatia['Campaign ID'].nunique():,}")

# Croatia spend
croatia_spend = df_croatia['Cost_parsed'].sum()
print(f"\nCroatia Spend (direktno iz country file-a): EUR {croatia_spend:,.2f}")

# Proveri koliko kampanja ima SAMO Croatia
croatia_only_ids = []
croatia_multi_ids = []

for cid in df_croatia['Campaign ID'].unique():
    # Provjeri koliko zemalja ima ova kampanja
    campaign_countries = df_country[df_country['Campaign ID'] == cid]['Country/Territory (User location)'].unique()

    if len(campaign_countries) == 1 and campaign_countries[0] == 'Croatia':
        croatia_only_ids.append(cid)
    else:
        croatia_multi_ids.append(cid)

print(f"\n\nBREAKDOWN:")
print(f"  Kampanje koje ciljaju SAMO Croatia: {len(croatia_only_ids):,}")
print(f"  Kampanje koje ciljaju Croatia + druge zemlje: {len(croatia_multi_ids):,}")

# Spend breakdown
croatia_only_spend = df_country[df_country['Campaign ID'].isin(croatia_only_ids) &
                                (df_country['Country/Territory (User location)'] == 'Croatia')]['Cost_parsed'].sum()

croatia_multi_spend = df_croatia[df_croatia['Campaign ID'].isin(croatia_multi_ids)]['Cost_parsed'].sum()

print(f"\n  Spend (SAMO Croatia kampanje): EUR {croatia_only_spend:,.2f}")
print(f"  Spend (Multi-market kampanje, Croatia dio): EUR {croatia_multi_spend:,.2f}")
print(f"  UKUPNO Croatia Spend: EUR {croatia_spend:,.2f}")

print("\n" + "=" * 80)
print("ZAKLJUČAK:")
print("=" * 80)

print(f"""
OPCIJA 1: Samo kampanje koje ciljaju ISKLJUČIVO Hrvatsku
  - Broj kampanja: {len(croatia_only_ids):,}
  - Spend: EUR {croatia_only_spend:,.2f}

OPCIJA 2: Sve kampanje koje UKLJUČUJU Hrvatsku (i multi-market)
  - Broj kampanja: {len(croatia_only_ids) + len(croatia_multi_ids):,}
  - Spend: EUR {croatia_spend:,.2f}

Razlika: EUR {croatia_spend - croatia_only_spend:,.2f}
""")

print("Koji pristup želimo koristiti za HR Prototype?")
