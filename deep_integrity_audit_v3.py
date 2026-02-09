#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEEP INTEGRITY AUDIT - V3 FINAL
Pancirni audit integriteta prije Master Merge-a
"""

import pandas as pd
import numpy as np
from collections import defaultdict

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_cost(value):
    """Parsiraj Cost vrijednost."""
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

def safe_print(text):
    """Safely print text with encoding handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

# ============================================================================
# PATHS
# ============================================================================

PATH_ANCHOR = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - no segmentation - all campaigns.csv"
PATH_SEGMENTED = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - segmented by ad format - only youtube campaigns.csv"
PATH_COUNTRY = "data - v3/campaign - country - v3/campaign location - version 3.csv"
PATH_AGE_GENDER = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"
PATH_INTERESTS = "data - v3/campaign - interests - v3/campaign - audience segements or interests - version 3.csv"
PATH_DURATION = "data - v3/campaign - duration - v3/campaign - duration - version 3.csv"
PATH_REACH_Q1 = "data - v3/campaign reach - frequency - v3/campaign - reach - frequency - q1 - version 3.csv"
PATH_REACH_Q2 = "data - v3/campaign reach - frequency - v3/campaign - reach - frequency - q2 - version 3.csv"
PATH_REACH_Q3 = "data - v3/campaign reach - frequency - v3/campaign - reach - frequency - q3 - version 3.csv"
PATH_REACH_Q4 = "data - v3/campaign reach - frequency - v3/campaign - reach - frequency - q4 - version.csv"

print("=" * 120)
print("DEEP INTEGRITY AUDIT - V3 FINAL DATA")
print("=" * 120)
print("\nAUDIT PROTOKOL: Provjera 100% integriteta podataka prije Master Merge-a\n")

# Status tracking
issues = []
warnings = []

# ============================================================================
# STEP 1: FINANCIAL ANCHOR CHECK
# ============================================================================

print("=" * 120)
print("STEP 1: FINANCIAL ANCHOR CHECK")
print("=" * 120)

df_anchor = pd.read_csv(PATH_ANCHOR, delimiter=';', encoding='utf-8-sig')
df_anchor['Cost_parsed'] = df_anchor['Cost'].apply(parse_cost)

grand_total = df_anchor['Cost_parsed'].sum()
expected_total = 2354918.67
tolerance = 0.10  # 10 centi tolerancija

print(f"\nFinancijsko Sidro: {PATH_ANCHOR}")
print(f"Broj kampanja: {len(df_anchor):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_anchor['Campaign ID'].nunique():,}")
print(f"\nGrand Total Spend: EUR {grand_total:,.2f}")
print(f"Ocekivani Total:   EUR {expected_total:,.2f}")
print(f"Razlika:           EUR {abs(grand_total - expected_total):,.2f}")

if abs(grand_total - expected_total) <= tolerance:
    print("\n[OK] Financijsko sidro POTVRDJENO!")
else:
    issues.append(f"KRITICNO: Grand Total ({grand_total:,.2f}) ne odgovara ocekivanom ({expected_total:,.2f})")
    print(f"\n[GRESKA] Financijsko sidro NE ODGOVARA! Razlika: EUR {abs(grand_total - expected_total):,.2f}")

# ============================================================================
# STEP 2: COVERAGE & GAP CHECK - COUNTRY
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2A: COVERAGE & GAP CHECK - COUNTRY (Location)")
print("=" * 120)

df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')
df_country['Cost_parsed'] = df_country['Cost'].apply(parse_cost)

country_total = df_country['Cost_parsed'].sum()
country_diff = abs(grand_total - country_total)
country_tolerance = 300.0

print(f"\nCountry Location file: {PATH_COUNTRY}")
print(f"Broj redaka: {len(df_country):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_country['Campaign ID'].nunique():,}")
print(f"\nCountry Total Spend: EUR {country_total:,.2f}")
print(f"Financijsko Sidro:   EUR {grand_total:,.2f}")
print(f"Razlika:             EUR {country_diff:,.2f}")
print(f"Tolerancija:         EUR {country_tolerance:,.2f}")

if country_diff <= country_tolerance:
    print(f"\n[OK] Country spend unutar tolerancije!")
else:
    issues.append(f"Country spend razlika ({country_diff:,.2f}) IZVAN tolerancije ({country_tolerance:,.2f})")
    print(f"\n[GRESKA] Country spend razlika prevelika!")

# ============================================================================
# STEP 2B: COVERAGE & GAP CHECK - AGE GENDER
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2B: COVERAGE & GAP CHECK - AGE GENDER")
print("=" * 120)

df_age = pd.read_csv(PATH_AGE_GENDER, delimiter=';', encoding='utf-8-sig')
df_age['Cost_parsed'] = df_age['Cost'].apply(parse_cost)

age_total = df_age['Cost_parsed'].sum()
age_gap = grand_total - age_total
age_gap_pct = (age_gap / grand_total) * 100

print(f"\nAge-Gender file: {PATH_AGE_GENDER}")
print(f"Broj redaka: {len(df_age):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_age['Campaign ID'].nunique():,}")
print(f"\nAge-Gender Total Spend: EUR {age_total:,.2f}")
print(f"Financijsko Sidro:      EUR {grand_total:,.2f}")
print(f"GAP (Missing):          EUR {age_gap:,.2f} ({age_gap_pct:.2f}%)")

# Provjeri jesu li kampanje u GAP-u PMax
age_campaign_ids = set(df_age['Campaign ID'].unique())
anchor_campaign_ids = set(df_anchor['Campaign ID'].unique())
missing_in_age = anchor_campaign_ids - age_campaign_ids

if len(missing_in_age) > 0:
    # Provjeri jesu li to PMax kampanje
    df_missing = df_anchor[df_anchor['Campaign ID'].isin(missing_in_age)]
    missing_spend = df_missing['Cost_parsed'].sum()

    print(f"\nKampanje koje NEDOSTAJU u Age-Gender:")
    print(f"  Broj kampanja: {len(missing_in_age):,}")
    print(f"  Spend: EUR {missing_spend:,.2f}")

    # Pokusaj identificirati PMax iz naziva
    pmax_count = sum(1 for cid in missing_in_age
                     if 'pmax' in str(df_anchor[df_anchor['Campaign ID'] == cid]['Campaign'].iloc[0]).lower()
                     or 'performance max' in str(df_anchor[df_anchor['Campaign ID'] == cid]['Campaign'].iloc[0]).lower())

    print(f"  PMax kampanje (iz naziva): {pmax_count}")

    # Primjeri
    print(f"\n  Primjeri kampanja koje nedostaju (Top 10 po trošku):")
    for i, row in df_missing.sort_values('Cost_parsed', ascending=False).head(10).iterrows():
        campaign_name = str(row['Campaign'])[:70].encode('ascii', 'ignore').decode('ascii')
        safe_print(f"    - {campaign_name}... (EUR {row['Cost_parsed']:,.2f})")

    if abs(missing_spend - age_gap) > 1.0:
        warnings.append(f"Age-Gender GAP ({age_gap:,.2f}) ne odgovara potpuno missing spend ({missing_spend:,.2f})")

# ============================================================================
# STEP 2C: COVERAGE & GAP CHECK - INTERESTS
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2C: COVERAGE & GAP CHECK - INTERESTS")
print("=" * 120)

df_interests = pd.read_csv(PATH_INTERESTS, delimiter=';', encoding='utf-8-sig')
df_interests['Cost_parsed'] = df_interests['Cost'].apply(parse_cost)

interests_total = df_interests['Cost_parsed'].sum()
interests_gap = grand_total - interests_total
interests_gap_pct = (interests_gap / grand_total) * 100

print(f"\nInterests file: {PATH_INTERESTS}")
print(f"Broj redaka: {len(df_interests):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_interests['Campaign ID'].nunique():,}")
print(f"\nInterests Total Spend: EUR {interests_total:,.2f}")
print(f"Financijsko Sidro:     EUR {grand_total:,.2f}")
print(f"GAP (Missing):         EUR {interests_gap:,.2f} ({interests_gap_pct:.2f}%)")

# ============================================================================
# STEP 3: CROSS-CHECK REACH (TOP 20 KAMPANJA)
# ============================================================================

print("\n" + "=" * 120)
print("STEP 3: CROSS-CHECK REACH - TOP 20 KAMPANJA")
print("=" * 120)

# Ucitaj reach data za sve kvartale
df_reach_q1 = pd.read_csv(PATH_REACH_Q1, delimiter=';', encoding='utf-8-sig')
df_reach_q2 = pd.read_csv(PATH_REACH_Q2, delimiter=';', encoding='utf-8-sig')
df_reach_q3 = pd.read_csv(PATH_REACH_Q3, delimiter=';', encoding='utf-8-sig')
df_reach_q4 = pd.read_csv(PATH_REACH_Q4, delimiter=';', encoding='utf-8-sig')

# Kombinuj sve kvartale
df_reach_all = pd.concat([df_reach_q1, df_reach_q2, df_reach_q3, df_reach_q4], ignore_index=True)
reach_campaign_ids = set(df_reach_all['Campaign ID'].unique())

print(f"\nReach data (svi kvartali):")
print(f"  Q1: {df_reach_q1['Campaign ID'].nunique():,} kampanja")
print(f"  Q2: {df_reach_q2['Campaign ID'].nunique():,} kampanja")
print(f"  Q3: {df_reach_q3['Campaign ID'].nunique():,} kampanja")
print(f"  Q4: {df_reach_q4['Campaign ID'].nunique():,} kampanja")
print(f"  UKUPNO (unikatnih): {len(reach_campaign_ids):,} kampanja")

# Top 20 kampanja iz sidra
top20 = df_anchor.sort_values('Cost_parsed', ascending=False).head(20)

print(f"\n\nTOP 20 KAMPANJA - REACH COVERAGE CHECK:\n")
print(f"{'Rank':<5} {'Campaign ID':<15} {'Cost (EUR)':<15} {'Reach?':<8} {'Type':<15} Campaign Name")
print("-" * 120)

missing_reach_count = 0
missing_reach_spend = 0.0

for i, row in top20.iterrows():
    rank = top20.index.get_loc(i) + 1
    campaign_id = row['Campaign ID']
    cost = row['Cost_parsed']
    campaign_name = str(row['Campaign'])[:50].encode('ascii', 'ignore').decode('ascii')

    has_reach = campaign_id in reach_campaign_ids

    # Pokusaj detektirati tip kampanje
    campaign_lower = str(row['Campaign']).lower()
    if 'pmax' in campaign_lower or 'performance max' in campaign_lower:
        campaign_type = 'PMax'
    elif 'demand' in campaign_lower or 'demand gen' in campaign_lower or '(dg)' in campaign_lower:
        campaign_type = 'Demand Gen'
    elif '(gdn)' in campaign_lower or 'display' in campaign_lower:
        campaign_type = 'Display/GDN'
    elif '(yt)' in campaign_lower or 'youtube' in campaign_lower:
        campaign_type = 'YouTube'
    else:
        campaign_type = 'Unknown'

    reach_status = 'YES' if has_reach else 'NO'

    if not has_reach and campaign_type not in ['PMax', 'Demand Gen']:
        missing_reach_count += 1
        missing_reach_spend += cost

    safe_print(f"{rank:<5} {campaign_id:<15} EUR{cost:>12,.2f} {reach_status:<8} {campaign_type:<15} {campaign_name}")

if missing_reach_count > 0:
    warnings.append(f"{missing_reach_count} non-PMax kampanja u Top 20 NEMAJU reach podatke (EUR {missing_reach_spend:,.2f})")
    print(f"\n[UPOZORENJE] {missing_reach_count} non-PMax kampanja u Top 20 nemaju reach podatke!")
else:
    print(f"\n[OK] Sve non-PMax kampanje u Top 20 imaju reach podatke!")

# ============================================================================
# STEP 4: LOCATION ANOMALY - SPEND IZVAN HRVATSKE
# ============================================================================

print("\n" + "=" * 120)
print("STEP 4: LOCATION ANOMALY - SPEND IZVAN HRVATSKE")
print("=" * 120)

# Provjeri koliko je spend izvan HR
if 'Country/Territory (User location)' in df_country.columns:
    country_col = 'Country/Territory (User location)'
elif 'Country' in df_country.columns:
    country_col = 'Country'
elif 'Country/Territory' in df_country.columns:
    country_col = 'Country/Territory'
elif 'Location' in df_country.columns:
    country_col = 'Location'
else:
    country_col = None
    issues.append("KRITICNO: Ne mogu pronaci kolonu Country/Location u country file-u!")

if country_col:
    country_breakdown = df_country.groupby(country_col)['Cost_parsed'].sum().sort_values(ascending=False)

    print(f"\nSpend po lokacijama:\n")

    hr_spend = 0.0
    non_hr_spend = 0.0

    for country, spend in country_breakdown.items():
        pct = (spend / country_total) * 100
        country_clean = str(country).encode('ascii', 'ignore').decode('ascii')

        # Provjeri je li HR
        if 'croatia' in str(country).lower() or 'hrvatska' in str(country).lower():
            hr_spend += spend
            safe_print(f"  {country_clean:40s} - EUR {spend:>12,.2f} ({pct:>5.2f}%) [HR]")
        else:
            non_hr_spend += spend
            safe_print(f"  {country_clean:40s} - EUR {spend:>12,.2f} ({pct:>5.2f}%) [NON-HR]")

    print(f"\n{'UKUPNO:':<42s}")
    print(f"  {'Hrvatska (HR):':<40s} - EUR {hr_spend:>12,.2f} ({hr_spend/country_total*100:>5.2f}%)")
    print(f"  {'Izvan Hrvatske (NON-HR):':<40s} - EUR {non_hr_spend:>12,.2f} ({non_hr_spend/country_total*100:>5.2f}%)")

    if non_hr_spend > 0:
        warnings.append(f"Detektiran spend izvan Hrvatske: EUR {non_hr_spend:,.2f} ({non_hr_spend/country_total*100:.2f}%)")

# ============================================================================
# STEP 5: DURATION AUDIT
# ============================================================================

print("\n" + "=" * 120)
print("STEP 5: DURATION AUDIT - POKRIVENI CAMPAIGN ID-EVI")
print("=" * 120)

df_duration = pd.read_csv(PATH_DURATION, delimiter=';', encoding='utf-8-sig')
duration_campaign_ids = set(df_duration['Campaign ID'].unique())

print(f"\nDuration file: {PATH_DURATION}")
print(f"Broj redaka: {len(df_duration):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_duration['Campaign ID'].nunique():,}")

# Provjeri pokriveni ID-evi
anchor_ids = set(df_anchor['Campaign ID'].unique())
missing_in_duration = anchor_ids - duration_campaign_ids
extra_in_duration = duration_campaign_ids - anchor_ids

coverage_pct = (len(duration_campaign_ids & anchor_ids) / len(anchor_ids)) * 100

print(f"\nCOVERAGE ANALIZA:")
print(f"  Sidro (anchor):           {len(anchor_ids):,} kampanja")
print(f"  Duration file:            {len(duration_campaign_ids):,} kampanja")
print(f"  Pokriveno:                {len(duration_campaign_ids & anchor_ids):,} kampanja ({coverage_pct:.2f}%)")
print(f"  Nedostaje u Duration:     {len(missing_in_duration):,} kampanja")
print(f"  Visak u Duration:         {len(extra_in_duration):,} kampanja")

if len(missing_in_duration) > 0:
    # Koliki je spend tih kampanja?
    df_missing_dur = df_anchor[df_anchor['Campaign ID'].isin(missing_in_duration)]
    missing_dur_spend = df_missing_dur['Cost_parsed'].sum()

    issues.append(f"{len(missing_in_duration)} kampanja NEMA duration podatke (EUR {missing_dur_spend:,.2f})")
    print(f"\n[GRESKA] {len(missing_in_duration)} kampanja nedostaje u Duration file-u!")
    print(f"  Spend tih kampanja: EUR {missing_dur_spend:,.2f}")

    print(f"\n  Primjeri (Top 10 po trošku):")
    for i, row in df_missing_dur.sort_values('Cost_parsed', ascending=False).head(10).iterrows():
        campaign_name = str(row['Campaign'])[:70].encode('ascii', 'ignore').decode('ascii')
        safe_print(f"    - ID {row['Campaign ID']} - {campaign_name}... (EUR {row['Cost_parsed']:,.2f})")
else:
    print(f"\n[OK] Svi Campaign ID-evi iz sidra imaju duration podatke!")

# ============================================================================
# FINAL VERDICT
# ============================================================================

print("\n" + "=" * 120)
print("FINAL VERDICT")
print("=" * 120)

print(f"\n\nSUMARY:\n")
print(f"  Financijsko sidro: EUR {grand_total:,.2f}")
print(f"  Broj kampanja: {len(anchor_ids):,}")
print(f"  Broj accounta: {df_anchor['Account'].nunique()}")

print(f"\n\nCOVERAGE:")
print(f"  Country:      {df_country['Campaign ID'].nunique():,} kampanja, EUR {country_total:,.2f} (diff: EUR {country_diff:,.2f})")
print(f"  Age-Gender:   {df_age['Campaign ID'].nunique():,} kampanja, EUR {age_total:,.2f} (gap: EUR {age_gap:,.2f})")
print(f"  Interests:    {df_interests['Campaign ID'].nunique():,} kampanja, EUR {interests_total:,.2f} (gap: EUR {interests_gap:,.2f})")
print(f"  Reach (Q1-Q4): {len(reach_campaign_ids):,} kampanja")
print(f"  Duration:     {df_duration['Campaign ID'].nunique():,} kampanja")

if len(issues) == 0 and len(warnings) == 0:
    print("\n\n" + "=" * 120)
    print("SUSTAV SPREMAN ZA MASTER MERGE!")
    print("=" * 120)
    print("\n[OK] Nema kriticnih gresaka niti upozorenja. Svi podaci su konzistentni.")

elif len(issues) == 0:
    print("\n\n" + "=" * 120)
    print("SUSTAV SPREMAN ZA MASTER MERGE (SA UPOZORENJIMA)")
    print("=" * 120)
    print(f"\n[OK] Nema kriticnih gresaka, ali postoje upozorenja ({len(warnings)}):")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    print("\nOva upozorenja se mogu rijesiti u sljedecem koraku (filtriranje po lokaciji, itd.)")

else:
    print("\n\n" + "=" * 120)
    print("SUSTAV NIJE SPREMAN!")
    print("=" * 120)
    print(f"\n[GRESKA] Pronadjeno {len(issues)} kriticnih gresaka:\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

    if len(warnings) > 0:
        print(f"\n\nUpozorenja ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")

print("\n" + "=" * 120)
print("AUDIT ZAVRSEN")
print("=" * 120)
