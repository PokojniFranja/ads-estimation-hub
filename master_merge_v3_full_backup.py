#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER MERGE V3 - FULL BACKUP (RAW DATA)
Spajanje svih V3 izvora u jedan kompletni master file
BEZ filtriranja - zadrzavamo 100% sirovih podataka
"""

import pandas as pd
import numpy as np
from datetime import datetime

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

OUTPUT_PATH = "ads_estimation_hub_V3_MASTER_BACKUP_RAW.csv"

print("=" * 120)
print("MASTER MERGE V3 - FULL BACKUP (RAW DATA)")
print("=" * 120)
print("\nCILJ: Spojiti sve V3 izvore u jedan master file BEZ filtriranja")
print("Format: 1 red = 1 Campaign ID\n")

# ============================================================================
# STEP 1: UCITAJ MASTER (FINANCIJSKO SIDRO)
# ============================================================================

print("=" * 120)
print("STEP 1: UCITAVANJE MASTER FILE (Financijsko Sidro)")
print("=" * 120)

df_master = pd.read_csv(PATH_ANCHOR, delimiter=';', encoding='utf-8-sig')
df_master['Cost_parsed'] = df_master['Cost'].apply(parse_cost)

print(f"\nMaster file: {PATH_ANCHOR}")
print(f"Broj kampanja: {len(df_master):,}")
print(f"Grand Total Spend: EUR {df_master['Cost_parsed'].sum():,.2f}")

# Rename kolone za jasnocu
df_master = df_master.rename(columns={
    'Cost': 'Cost_Original',
    'Cost_parsed': 'Cost'
})

# ============================================================================
# STEP 2: DODAJ YOUTUBE AD FORMAT SEGMENTATION
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2: SPAJANJE YOUTUBE AD FORMAT SEGMENTATION")
print("=" * 120)

df_segmented = pd.read_csv(PATH_SEGMENTED, delimiter=';', encoding='utf-8-sig')

print(f"\nSegmented file: {PATH_SEGMENTED}")
print(f"Broj redaka: {len(df_segmented):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_segmented['Campaign ID'].nunique():,}")

# Grupiraj po Campaign ID i napravi listu ad formata
df_formats = df_segmented.groupby('Campaign ID')['Ad format'].apply(
    lambda x: ', '.join(sorted(set(x)))
).reset_index()
df_formats.columns = ['Campaign ID', 'YouTube_Ad_Formats']

# Merge sa masterom
df_master = df_master.merge(df_formats, on='Campaign ID', how='left')

# Oznaci kampanje bez YouTube formata
df_master['YouTube_Ad_Formats'] = df_master['YouTube_Ad_Formats'].fillna('Non-YouTube Format')

youtube_campaigns = (df_master['YouTube_Ad_Formats'] != 'Non-YouTube Format').sum()
print(f"\nKampanje sa YouTube formatima: {youtube_campaigns:,}")
print(f"Kampanje bez YouTube formata: {len(df_master) - youtube_campaigns:,}")

# ============================================================================
# STEP 3: DODAJ LOCATION DATA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 3: SPAJANJE LOCATION DATA")
print("=" * 120)

df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')

print(f"\nCountry file: {PATH_COUNTRY}")
print(f"Broj redaka: {len(df_country):,}")

# Grupiraj po Campaign ID - uzmi sve zemlje i njihove trosktove
df_countries = df_country.groupby('Campaign ID').agg({
    'Country/Territory (User location)': lambda x: ', '.join(sorted(set(x))),
}).reset_index()
df_countries.columns = ['Campaign ID', 'Target_Countries']

# Dodaj i broj zemalja
df_country_count = df_country.groupby('Campaign ID')['Country/Territory (User location)'].nunique().reset_index()
df_country_count.columns = ['Campaign ID', 'Number_of_Countries']

df_countries = df_countries.merge(df_country_count, on='Campaign ID')

# Merge sa masterom
df_master = df_master.merge(df_countries, on='Campaign ID', how='left')

# Oznaci kampanje bez location podataka
df_master['Target_Countries'] = df_master['Target_Countries'].fillna('Unknown')
df_master['Number_of_Countries'] = df_master['Number_of_Countries'].fillna(0)

print(f"\nKampanje sa location podacima: {(df_master['Target_Countries'] != 'Unknown').sum():,}")
print(f"Kampanje bez location podataka: {(df_master['Target_Countries'] == 'Unknown').sum():,}")

# ============================================================================
# STEP 4: DODAJ AGE-GENDER DATA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 4: SPAJANJE AGE-GENDER DATA")
print("=" * 120)

df_age = pd.read_csv(PATH_AGE_GENDER, delimiter=';', encoding='utf-8-sig')

print(f"\nAge-Gender file: {PATH_AGE_GENDER}")
print(f"Broj redaka: {len(df_age):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_age['Campaign ID'].nunique():,}")

# Oznaci kampanje koje imaju demographics
age_campaign_ids = set(df_age['Campaign ID'].unique())
df_master['Has_Demographics'] = df_master['Campaign ID'].isin(age_campaign_ids)

# Broj Age/Gender kombinacija po kampanji
df_age_count = df_age.groupby('Campaign ID').size().reset_index()
df_age_count.columns = ['Campaign ID', 'Demographics_Segments_Count']

df_master = df_master.merge(df_age_count, on='Campaign ID', how='left')
df_master['Demographics_Segments_Count'] = df_master['Demographics_Segments_Count'].fillna(0).astype(int)

# Labela za kampanje bez demographics
df_master['Demographics_Label'] = df_master['Has_Demographics'].apply(
    lambda x: 'Available' if x else 'Automatic / PMax'
)

print(f"\nKampanje sa Demographics: {df_master['Has_Demographics'].sum():,}")
print(f"Kampanje BEZ Demographics (PMax): {(~df_master['Has_Demographics']).sum():,}")

# ============================================================================
# STEP 5: DODAJ INTERESTS DATA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 5: SPAJANJE INTERESTS DATA")
print("=" * 120)

df_interests = pd.read_csv(PATH_INTERESTS, delimiter=';', encoding='utf-8-sig')

print(f"\nInterests file: {PATH_INTERESTS}")
print(f"Broj redaka: {len(df_interests):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_interests['Campaign ID'].nunique():,}")

# Oznaci kampanje koje imaju interests
interests_campaign_ids = set(df_interests['Campaign ID'].unique())
df_master['Has_Interests'] = df_master['Campaign ID'].isin(interests_campaign_ids)

# Broj interest segmenata po kampanji
df_interests_count = df_interests.groupby('Campaign ID').size().reset_index()
df_interests_count.columns = ['Campaign ID', 'Interest_Segments_Count']

df_master = df_master.merge(df_interests_count, on='Campaign ID', how='left')
df_master['Interest_Segments_Count'] = df_master['Interest_Segments_Count'].fillna(0).astype(int)

# Labela za kampanje bez interests
df_master['Interests_Label'] = df_master['Has_Interests'].apply(
    lambda x: 'Available' if x else 'Automatic / PMax'
)

print(f"\nKampanje sa Interests: {df_master['Has_Interests'].sum():,}")
print(f"Kampanje BEZ Interests (PMax): {(~df_master['Has_Interests']).sum():,}")

# ============================================================================
# STEP 6: DODAJ DURATION DATA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 6: SPAJANJE DURATION DATA")
print("=" * 120)

df_duration = pd.read_csv(PATH_DURATION, delimiter=';', encoding='utf-8-sig')

print(f"\nDuration file: {PATH_DURATION}")
print(f"Broj redaka: {len(df_duration):,}")

# Selektiraj samo relevantne kolone
if 'Campaign start date' in df_duration.columns and 'Campaign end date' in df_duration.columns:
    df_duration_clean = df_duration[['Campaign ID', 'Campaign start date', 'Campaign end date']].drop_duplicates()

    # Rename za konzistentnost
    df_duration_clean = df_duration_clean.rename(columns={
        'Campaign start date': 'Start_Date',
        'Campaign end date': 'End_Date'
    })

    # Merge sa masterom
    df_master = df_master.merge(df_duration_clean, on='Campaign ID', how='left')

    print(f"\nKampanje sa Duration podacima: {df_master['Start_Date'].notna().sum():,}")
    print(f"Kampanje bez Duration podataka: {df_master['Start_Date'].isna().sum():,}")
else:
    print("\nUPOZORENJE: Ne mogu pronaci 'Campaign start date' i 'Campaign end date' kolone u duration file-u")
    df_master['Start_Date'] = None
    df_master['End_Date'] = None

# ============================================================================
# STEP 7: DODAJ REACH-FREQUENCY DATA (Q1-Q4)
# ============================================================================

print("\n" + "=" * 120)
print("STEP 7: SPAJANJE REACH-FREQUENCY DATA (Q1-Q4)")
print("=" * 120)

# Ucitaj sve kvartale
df_reach_q1 = pd.read_csv(PATH_REACH_Q1, delimiter=';', encoding='utf-8-sig')
df_reach_q2 = pd.read_csv(PATH_REACH_Q2, delimiter=';', encoding='utf-8-sig')
df_reach_q3 = pd.read_csv(PATH_REACH_Q3, delimiter=';', encoding='utf-8-sig')
df_reach_q4 = pd.read_csv(PATH_REACH_Q4, delimiter=';', encoding='utf-8-sig')

# Dodaj kvartal oznaku
df_reach_q1['Quarter'] = 'Q1'
df_reach_q2['Quarter'] = 'Q2'
df_reach_q3['Quarter'] = 'Q3'
df_reach_q4['Quarter'] = 'Q4'

# Kombiniraj sve kvartale
df_reach_all = pd.concat([df_reach_q1, df_reach_q2, df_reach_q3, df_reach_q4], ignore_index=True)

print(f"\nReach data:")
print(f"  Q1: {df_reach_q1['Campaign ID'].nunique():,} kampanja")
print(f"  Q2: {df_reach_q2['Campaign ID'].nunique():,} kampanja")
print(f"  Q3: {df_reach_q3['Campaign ID'].nunique():,} kampanja")
print(f"  Q4: {df_reach_q4['Campaign ID'].nunique():,} kampanja")
print(f"  UKUPNO: {df_reach_all['Campaign ID'].nunique():,} kampanja")

# Grupiraj po Campaign ID i agreguj reach
if 'Unique users' in df_reach_all.columns:
    # Parse Unique users (moze biti string sa zarezima)
    def parse_reach(value):
        if pd.isna(value):
            return 0
        value_str = str(value).replace(',', '').strip()
        try:
            return int(value_str)
        except:
            return 0

    df_reach_all['Unique_users_parsed'] = df_reach_all['Unique users'].apply(parse_reach)

    # Reach = max unique users per quarter
    df_reach_agg = df_reach_all.groupby('Campaign ID').agg({
        'Unique_users_parsed': 'max',  # Max reach
        'Quarter': lambda x: ', '.join(sorted(set(x)))  # Liste kvartala
    }).reset_index()
    df_reach_agg.columns = ['Campaign ID', 'Peak_Reach', 'Active_Quarters']

    # Merge sa masterom
    df_master = df_master.merge(df_reach_agg, on='Campaign ID', how='left')

    # Oznaci kampanje bez reach podataka
    df_master['Peak_Reach'] = df_master['Peak_Reach'].fillna(0).astype(int)
    df_master['Active_Quarters'] = df_master['Active_Quarters'].fillna('Unknown')

    print(f"\nKampanje sa Reach podacima: {(df_master['Peak_Reach'] > 0).sum():,}")
    print(f"Kampanje bez Reach podataka: {(df_master['Peak_Reach'] == 0).sum():,}")
else:
    print("\nUPOZORENJE: Ne mogu pronaci 'Unique users' kolonu u reach file-u")
    df_master['Peak_Reach'] = 0
    df_master['Active_Quarters'] = 'Unknown'

# ============================================================================
# STEP 8: FINAL AUDIT & VALIDATION
# ============================================================================

print("\n" + "=" * 120)
print("STEP 8: FINAL AUDIT & VALIDATION")
print("=" * 120)

# Audit Grand Total
final_grand_total = df_master['Cost'].sum()
expected_total = 2354918.67

print(f"\nFINAL GRAND TOTAL: EUR {final_grand_total:,.2f}")
print(f"Expected Total:    EUR {expected_total:,.2f}")
print(f"Razlika:           EUR {abs(final_grand_total - expected_total):,.2f}")

if abs(final_grand_total - expected_total) <= 0.10:
    print("\n[OK] Grand Total MATCH! Svi podaci su ispravno spojeni.")
else:
    print(f"\n[UPOZORENJE] Grand Total ne odgovara ocekivanom! Razlika: EUR {abs(final_grand_total - expected_total):,.2f}")

# Summary statistika
print(f"\n\nFINAL MASTER FILE SUMMARY:")
print(f"  Ukupno kampanja:           {len(df_master):,}")
print(f"  Ukupno accounta:           {df_master['Account'].nunique():,}")
print(f"  Grand Total Spend:         EUR {final_grand_total:,.2f}")
print(f"\n  YouTube kampanje:          {(df_master['YouTube_Ad_Formats'] != 'Non-YouTube Format').sum():,}")
print(f"  Non-YouTube kampanje:      {(df_master['YouTube_Ad_Formats'] == 'Non-YouTube Format').sum():,}")
print(f"\n  Sa Demographics:           {df_master['Has_Demographics'].sum():,}")
print(f"  Bez Demographics (PMax):   {(~df_master['Has_Demographics']).sum():,}")
print(f"\n  Sa Interests:              {df_master['Has_Interests'].sum():,}")
print(f"  Bez Interests (PMax):      {(~df_master['Has_Interests']).sum():,}")
print(f"\n  Sa Location podacima:      {(df_master['Target_Countries'] != 'Unknown').sum():,}")
print(f"  Sa Reach podacima:         {(df_master['Peak_Reach'] > 0).sum():,}")
print(f"  Sa Duration podacima:      {df_master['Start_Date'].notna().sum():,}")

# ============================================================================
# STEP 9: EXPORT BACKUP
# ============================================================================

print("\n" + "=" * 120)
print("STEP 9: EXPORT BACKUP FILE")
print("=" * 120)

# Export sa UTF-8 encoding
df_master.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig', sep=';')

print(f"\nBackup file exported: {OUTPUT_PATH}")
print(f"Broj redaka: {len(df_master):,}")
print(f"Broj kolona: {len(df_master.columns):,}")
print(f"\nKolone: {list(df_master.columns)}")

# ============================================================================
# STEP 10: TOP 5 BRENDOVA PO TROSKU
# ============================================================================

print("\n" + "=" * 120)
print("STEP 10: TOP 5 BRENDOVA PO TROSKU (Kompletna baza)")
print("=" * 120)

def extract_brand_smart(campaign_name, account_name):
    """Pametnija ekstrakcija brenda."""
    if pd.isna(campaign_name):
        campaign_name = ""
    if pd.isna(account_name):
        account_name = ""

    name = str(campaign_name).lower()
    account = str(account_name).lower()

    # Poznati brendovi
    if "mcdonald" in name or "mcdonald" in account:
        return "McDonald's"
    elif "kaufland" in account or "kaufland" in name:
        return "Kaufland"
    elif "nivea" in account or "nivea" in name:
        return "Nivea (Beiersdorf)"
    elif "eucerin" in account or "eucerin" in name:
        return "Eucerin (Beiersdorf)"
    elif "philips" in account or "philips" in name:
        return "Philips"
    elif "persil" in name or "persil" in account:
        return "Persil (Henkel)"
    elif "perwoll" in name or "perwoll" in account:
        return "Perwoll (Henkel)"
    elif "syoss" in name or "syoss" in account:
        return "Syoss (Henkel)"
    elif "weisser" in name or "weisser" in account:
        return "Weisser Riese (Henkel)"
    elif "somat" in name or "somat" in account:
        return "Somat (Henkel)"
    elif "bref" in name or "bref" in account:
        return "Bref (Henkel)"
    elif "gliss" in name or "gliss" in account:
        return "Gliss (Henkel)"
    elif "schauma" in name or "schauma" in account:
        return "Schauma (Henkel)"
    elif "palette" in name or "palette" in account:
        return "Palette (Henkel)"
    elif "taft" in name or "taft" in account:
        return "Taft (Henkel)"
    elif "got2b" in name or "got2b" in account:
        return "got2b (Henkel)"
    elif "porsche" in account:
        return "Porsche (Auto)"
    elif "nissan" in account or "nissan" in name:
        return "Nissan"
    elif "zott" in account or "zott" in name:
        return "Zott"
    elif "jgl" in account:
        return "JGL (Pharma)"
    elif "energycom" in name or "energycom" in account:
        return "Energycom"
    elif "bosch" in account:
        return "Bosch"
    elif "finish" in account or "finish" in name:
        return "Finish"
    elif "rio mare" in account or "rio mare" in name:
        return "Rio Mare"
    elif "bison" in account:
        return "BISON"
    elif "borotalco" in account:
        return "Borotalco"
    elif "saponia" in account:
        return "Saponia"
    elif "ahmad" in account or "ahmad" in name:
        return "Ahmad Tea"
    elif "barilla" in account:
        return "Barilla"
    elif "ceresit" in name or "ceresit" in account:
        return "Ceresit"
    elif "uhu" in account:
        return "UHU"
    elif "reflustat" in name:
        return "Reflustat (JGL)"
    else:
        # Fallback - uzmi account name
        return str(account_name).split('_')[0][:30] if account_name else "Unknown"

# Dodaj Brand kolonu
df_master['Brand'] = df_master.apply(
    lambda row: extract_brand_smart(row['Campaign'], row['Account']),
    axis=1
)

# Top 5 brendova
brand_spend = df_master.groupby('Brand')['Cost'].sum().sort_values(ascending=False)

print(f"\n\nTOP 5 BRENDOVA (Kompletna sirova baza - SVE zemlje, SVI tipovi):\n")

for i, (brand, spend) in enumerate(brand_spend.head(5).items(), 1):
    num_campaigns = len(df_master[df_master['Brand'] == brand])
    percentage = (spend / final_grand_total) * 100
    safe_print(f"{i}. {brand:40s} - EUR {spend:>12,.2f} ({percentage:>5.2f}%) - {num_campaigns:>3} kampanja")

print("\n" + "=" * 120)
print("MASTER MERGE ZAVRSEN - BACKUP FILE SPREMAN!")
print("=" * 120)
print(f"\nFile: {OUTPUT_PATH}")
print(f"Grand Total: EUR {final_grand_total:,.2f}")
print(f"Status: ZLATNI BACKUP - 100% sirovih podataka zadrzano!")
print("=" * 120)
