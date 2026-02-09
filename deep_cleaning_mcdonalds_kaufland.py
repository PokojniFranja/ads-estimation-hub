#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEEP CLEANING - McDONALD'S & KAUFLAND AUDIT
Identifikacija i uklanjanje worldwide gresaka i multi-market anomalija
"""

import pandas as pd
import numpy as np

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_cost(value):
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

PATH_COUNTRY = "data - v3/campaign - country - v3/campaign location - version 3.csv"
PATH_MASTER = "ads_estimation_hub_V3_MASTER_BACKUP_RAW.csv"
OUTPUT_PATH = "ads_estimation_hub_HR_PROTOTYPE_V3_CLEANED.csv"

print("=" * 120)
print("DEEP CLEANING - McDONALD'S & KAUFLAND AUDIT")
print("=" * 120)
print("\nCILJ 1: Identificirati i izbaciti McDonald's Worldwide greske")
print("CILJ 2: Auditirati Kaufland multi-market kampanje\n")

# ============================================================================
# STEP 1: UCITAJ COUNTRY FILE
# ============================================================================

print("=" * 120)
print("STEP 1: UCITAVANJE COUNTRY FILE")
print("=" * 120)

df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')
df_country['Cost_parsed'] = df_country['Cost'].apply(parse_cost)

print(f"\nCountry file: {PATH_COUNTRY}")
print(f"Ukupno redaka: {len(df_country):,}")
print(f"Ukupno unikatnih kampanja: {df_country['Campaign ID'].nunique():,}")

# ============================================================================
# STEP 2: McDONALD'S WORLDWIDE ERROR DETECTION
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2: McDONALD'S WORLDWIDE ERROR DETECTION")
print("=" * 120)

# Identificiraj sve McDonald's kampanje
df_mcdonalds = df_country[
    df_country['Campaign'].str.contains("McDonald", case=False, na=False) |
    df_country['Account name'].str.contains("McDonald", case=False, na=False)
]

mcdonalds_campaign_ids = df_mcdonalds['Campaign ID'].unique()

print(f"\nUkupno McDonald's kampanja: {len(mcdonalds_campaign_ids):,}")

# Analiziraj svaku McDonald's kampanju
mcdonalds_analysis = []

for cid in mcdonalds_campaign_ids:
    campaign_data = df_country[df_country['Campaign ID'] == cid]

    campaign_name = campaign_data['Campaign'].iloc[0]
    num_countries = campaign_data['Country/Territory (User location)'].nunique()
    countries_list = campaign_data['Country/Territory (User location)'].unique()
    total_cost = campaign_data['Cost_parsed'].sum()

    # Provjeri je li Croatia u listi
    has_croatia = 'Croatia' in countries_list

    # Oznaka za worldwide gresku - ako ima vise od 10 zemalja
    is_worldwide_error = num_countries > 10

    mcdonalds_analysis.append({
        'Campaign ID': cid,
        'Campaign Name': campaign_name,
        'Num Countries': num_countries,
        'Has Croatia': has_croatia,
        'Is Worldwide Error': is_worldwide_error,
        'Total Cost': total_cost,
        'Countries': ', '.join(countries_list[:10])  # Prvi 10 zemalja
    })

df_mcdonalds_analysis = pd.DataFrame(mcdonalds_analysis)

# Worldwide greske
worldwide_errors = df_mcdonalds_analysis[df_mcdonalds_analysis['Is Worldwide Error']]

print(f"\n\nMcDonald's WORLDWIDE GRESKE (> 10 zemalja):")
print(f"Broj kampanja: {len(worldwide_errors)}")

if len(worldwide_errors) > 0:
    print(f"\n{'Campaign ID':<15} {'Countries':<10} {'Cost (EUR)':<15} Campaign Name")
    print("-" * 120)

    for i, row in worldwide_errors.iterrows():
        safe_print(f"{row['Campaign ID']:<15} {row['Num Countries']:<10} EUR {row['Total Cost']:>12,.2f} {row['Campaign Name'][:70]}")

    worldwide_error_spend = worldwide_errors['Total Cost'].sum()
    print(f"\n  UKUPNI SPEND (worldwide greske): EUR {worldwide_error_spend:,.2f}")

    # Lista Campaign ID-eva za izbacivanje
    worldwide_error_ids = set(worldwide_errors['Campaign ID'])
    print(f"\n  Ovi Campaign ID-evi ce biti POTPUNO IZBACENI iz HR Prototypea!")
else:
    print("\n  Nije pronadjeno worldwide gresaka (sve McDonald's kampanje imaju < 10 zemalja).")
    worldwide_error_ids = set()

# Normalne McDonald's kampanje (ne worldwide)
normal_mcdonalds = df_mcdonalds_analysis[~df_mcdonalds_analysis['Is Worldwide Error']]

print(f"\n\nNormalne McDonald's kampanje (< 10 zemalja):")
print(f"Broj kampanja: {len(normal_mcdonalds)}")

if len(normal_mcdonalds) > 0:
    print(f"\n{'Campaign ID':<15} {'Countries':<10} {'Croatia?':<10} {'Cost (EUR)':<15} Campaign Name")
    print("-" * 120)

    for i, row in normal_mcdonalds.iterrows():
        has_hr = 'YES' if row['Has Croatia'] else 'NO'
        safe_print(f"{row['Campaign ID']:<15} {row['Num Countries']:<10} {has_hr:<10} EUR {row['Total Cost']:>12,.2f} {row['Campaign Name'][:60]}")

# ============================================================================
# STEP 3: KAUFLAND MULTI-MARKET AUDIT
# ============================================================================

print("\n" + "=" * 120)
print("STEP 3: KAUFLAND MULTI-MARKET AUDIT")
print("=" * 120)

# Identificiraj sve Kaufland kampanje
df_kaufland = df_country[
    df_country['Campaign'].str.contains("Kaufland", case=False, na=False) |
    df_country['Account name'].str.contains("Kaufland", case=False, na=False)
]

kaufland_campaign_ids = df_kaufland['Campaign ID'].unique()

print(f"\nUkupno Kaufland kampanja: {len(kaufland_campaign_ids):,}")

# Analiziraj svaku Kaufland kampanju
kaufland_analysis = []

for cid in kaufland_campaign_ids:
    campaign_data = df_country[df_country['Campaign ID'] == cid]

    campaign_name = campaign_data['Campaign'].iloc[0]
    num_countries = campaign_data['Country/Territory (User location)'].nunique()
    countries_list = campaign_data['Country/Territory (User location)'].unique()

    # Spend po zemljama
    croatia_spend = campaign_data[campaign_data['Country/Territory (User location)'] == 'Croatia']['Cost_parsed'].sum()
    non_croatia_spend = campaign_data[campaign_data['Country/Territory (User location)'] != 'Croatia']['Cost_parsed'].sum()
    total_spend = campaign_data['Cost_parsed'].sum()

    has_croatia = croatia_spend > 0
    has_non_croatia = non_croatia_spend > 0

    # Anomaly = ima spend izvan Hrvatske
    is_anomaly = has_non_croatia

    kaufland_analysis.append({
        'Campaign ID': cid,
        'Campaign Name': campaign_name,
        'Num Countries': num_countries,
        'Croatia Spend': croatia_spend,
        'Non-Croatia Spend': non_croatia_spend,
        'Total Spend': total_spend,
        'Is Anomaly': is_anomaly,
        'Countries': ', '.join(sorted(countries_list))
    })

df_kaufland_analysis = pd.DataFrame(kaufland_analysis)

# Kaufland anomalije
kaufland_anomalies = df_kaufland_analysis[df_kaufland_analysis['Is Anomaly']]

print(f"\n\nKAUFLAND ANOMALY DETECTION:")
print(f"Broj kampanja sa spend-om izvan HR: {len(kaufland_anomalies)}")

if len(kaufland_anomalies) > 0:
    print(f"\n{'Campaign ID':<15} {'HR Spend':<15} {'NON-HR Spend':<15} {'Countries':<10} Campaign Name")
    print("-" * 120)

    for i, row in kaufland_anomalies.iterrows():
        safe_print(f"{row['Campaign ID']:<15} EUR {row['Croatia Spend']:>10,.2f} EUR {row['Non-Croatia Spend']:>10,.2f} {row['Num Countries']:<10} {row['Campaign Name'][:50]}")

    print(f"\n\nDETALJI ANOMALIJA:\n")

    for i, row in kaufland_anomalies.iterrows():
        safe_print(f"Campaign ID: {row['Campaign ID']}")
        safe_print(f"Naziv: {row['Campaign Name']}")
        safe_print(f"Hrvatske: EUR {row['Croatia Spend']:,.2f}")
        safe_print(f"Izvan HR: EUR {row['Non-Croatia Spend']:,.2f}")
        safe_print(f"Zemlje: {row['Countries']}")
        print()

    kaufland_anomaly_non_hr_spend = kaufland_anomalies['Non-Croatia Spend'].sum()
    print(f"UKUPNI NON-HR SPEND (Kaufland anomalije): EUR {kaufland_anomaly_non_hr_spend:,.2f}")
else:
    print("\n  Nema Kaufland anomalija - sve kampanje trose samo u Hrvatskoj!")

# Pure Croatia Kaufland kampanje
kaufland_pure_hr = df_kaufland_analysis[~df_kaufland_analysis['Is Anomaly']]

print(f"\n\nKaufland kampanje koje trose SAMO u Hrvatskoj:")
print(f"Broj kampanja: {len(kaufland_pure_hr)}")

if len(kaufland_pure_hr) > 0:
    for i, row in kaufland_pure_hr.iterrows():
        safe_print(f"  - {row['Campaign Name'][:70]} | EUR {row['Croatia Spend']:,.2f}")

# ============================================================================
# STEP 4: KREIRANJE CISTOG HR PROTOTYPEA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 4: KREIRANJE CISTOG HR PROTOTYPEA")
print("=" * 120)

# Strategija:
# 1. Uzmi sve kampanje koje imaju Croatia u country file-u
# 2. Izbaci McDonald's worldwide greske (potpuno)
# 3. Za Kaufland kampanje - uzmi samo Croatia spend
# 4. Za ostale kampanje - ako imaju Croatia, uzmi samo Croatia spend

# Filtriraj Croatia redove
df_croatia = df_country[df_country['Country/Territory (User location)'] == 'Croatia'].copy()

print(f"\nRedovi sa Croatia lokacijom: {len(df_croatia):,}")
print(f"Broj unikatnih kampanja: {df_croatia['Campaign ID'].nunique():,}")

# Izbaci McDonald's worldwide greske
df_croatia_cleaned = df_croatia[~df_croatia['Campaign ID'].isin(worldwide_error_ids)].copy()

print(f"\nNakon izbacivanja McDonald's worldwide gresaka:")
print(f"  Redovi: {len(df_croatia_cleaned):,}")
print(f"  Kampanje: {df_croatia_cleaned['Campaign ID'].nunique():,}")

# Grupiraj po Campaign ID i zbroji Croatia spend
croatia_spend_by_campaign = df_croatia_cleaned.groupby('Campaign ID')['Cost_parsed'].sum().reset_index()
croatia_spend_by_campaign.columns = ['Campaign ID', 'Croatia_Spend']

print(f"\nUkupan Croatia Spend (nakon ciscenja): EUR {croatia_spend_by_campaign['Croatia_Spend'].sum():,.2f}")

# ============================================================================
# STEP 5: MERGE SA MASTER BACKUP
# ============================================================================

print("\n" + "=" * 120)
print("STEP 5: MERGE SA MASTER BACKUP")
print("=" * 120)

# Ucitaj master backup
df_master = pd.read_csv(PATH_MASTER, delimiter=';', encoding='utf-8-sig')

print(f"\nMaster Backup: {len(df_master):,} kampanja")

# Merge - uzmi samo kampanje koje imaju Croatia spend
df_hr_prototype = df_master[df_master['Campaign ID'].isin(croatia_spend_by_campaign['Campaign ID'])].copy()

# Zamijeni Cost sa Croatia_Spend
df_hr_prototype = df_hr_prototype.merge(
    croatia_spend_by_campaign[['Campaign ID', 'Croatia_Spend']],
    on='Campaign ID',
    how='left'
)

# Zamijeni Cost kolonu
df_hr_prototype['Cost_Original_Global'] = df_hr_prototype['Cost']
df_hr_prototype['Cost'] = df_hr_prototype['Croatia_Spend']

# Makni privremenu kolonu
df_hr_prototype = df_hr_prototype.drop(columns=['Croatia_Spend'])

print(f"\nHR Prototype (nakon merge-a): {len(df_hr_prototype):,} kampanja")

# ============================================================================
# STEP 6: FINALNI IZRACUN & STATISTIKA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 6: FINALNI IZRACUN")
print("=" * 120)

final_hr_spend = df_hr_prototype['Cost'].sum()

print(f"\n\nFINALNI HR SPEND (CISTENO): EUR {final_hr_spend:,.2f}")

print(f"\n\nBREAKDOWN:")
print(f"  Ukupno kampanja: {len(df_hr_prototype):,}")
print(f"  YouTube kampanje: {(df_hr_prototype['YouTube_Ad_Formats'] != 'Non-YouTube Format').sum():,}")
print(f"  Non-YouTube: {(df_hr_prototype['YouTube_Ad_Formats'] == 'Non-YouTube Format').sum():,}")
print(f"  Sa Demographics: {df_hr_prototype['Has_Demographics'].sum():,}")
print(f"  Bez Demographics (PMax): {(~df_hr_prototype['Has_Demographics']).sum():,}")

# ============================================================================
# STEP 7: EXPORT
# ============================================================================

print("\n" + "=" * 120)
print("STEP 7: EXPORT HR PROTOTYPE (CLEANED)")
print("=" * 120)

df_hr_prototype.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig', sep=';')

print(f"\nFile exported: {OUTPUT_PATH}")
print(f"Broj kampanja: {len(df_hr_prototype):,}")
print(f"Grand Total: EUR {final_hr_spend:,.2f}")

# ============================================================================
# STEP 8: SUMMARY REPORT
# ============================================================================

print("\n" + "=" * 120)
print("STEP 8: SUMMARY REPORT")
print("=" * 120)

print(f"""
McDONALD'S WORLDWIDE GRESKE:
  - Broj kampanja izbaceno: {len(worldwide_error_ids)}
  - Spend izbacen: EUR {worldwide_errors['Total Cost'].sum() if len(worldwide_errors) > 0 else 0:,.2f}

KAUFLAND ANOMALIJE:
  - Broj kampanja sa non-HR spend-om: {len(kaufland_anomalies)}
  - Non-HR spend filtriran: EUR {kaufland_anomalies['Non-Croatia Spend'].sum() if len(kaufland_anomalies) > 0 else 0:,.2f}
  - Croatia spend zadržan: EUR {kaufland_anomalies['Croatia Spend'].sum() if len(kaufland_anomalies) > 0 else 0:,.2f}

FINALNI HR PROTOTYPE:
  - Broj kampanja: {len(df_hr_prototype):,}
  - Grand Total Spend: EUR {final_hr_spend:,.2f}
  - Status: CISTO - bez worldwide gresaka i multi-market anomalija
""")

# Top 5 brendova
if 'Brand' not in df_hr_prototype.columns:
    def extract_brand_smart(campaign_name, account_name):
        """Extract brand."""
        if pd.isna(campaign_name):
            campaign_name = ""
        if pd.isna(account_name):
            account_name = ""

        name = str(campaign_name).lower()
        account = str(account_name).lower()

        if "mcdonald" in name or "mcdonald" in account:
            return "McDonald's"
        elif "kaufland" in account or "kaufland" in name:
            return "Kaufland"
        elif "nivea" in account or "nivea" in name:
            return "Nivea (Beiersdorf)"
        elif "philips" in account or "philips" in name:
            return "Philips"
        elif "porsche" in account:
            return "Porsche"
        elif "zott" in account:
            return "Zott"
        else:
            return str(account_name).split('_')[0][:30] if account_name else "Unknown"

    df_hr_prototype['Brand'] = df_hr_prototype.apply(
        lambda row: extract_brand_smart(row['Campaign'], row['Account']),
        axis=1
    )

brand_spend = df_hr_prototype.groupby('Brand')['Cost'].sum().sort_values(ascending=False)

print(f"\nTOP 5 BRENDOVA (HR Prototype - Cisteno):\n")

for i, (brand, spend) in enumerate(brand_spend.head(5).items(), 1):
    num_campaigns = len(df_hr_prototype[df_hr_prototype['Brand'] == brand])
    percentage = (spend / final_hr_spend) * 100
    safe_print(f"{i}. {brand:40s} - EUR {spend:>12,.2f} ({percentage:>5.2f}%) - {num_campaigns:>3} kampanja")

print("\n" + "=" * 120)
print("DEEP CLEANING ZAVRSEN!")
print("=" * 120)
