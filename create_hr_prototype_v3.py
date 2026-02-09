#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR PROTOTYPE V3 - EXTRACTION
Kreiranje ciste hrvatske baze iz master backup-a
"""

import pandas as pd
import numpy as np

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_print(text):
    """Safely print text with encoding handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

# ============================================================================
# PATHS
# ============================================================================

INPUT_PATH = "ads_estimation_hub_V3_MASTER_BACKUP_RAW.csv"
OUTPUT_PATH = "ads_estimation_hub_HR_PROTOTYPE_V3.csv"

print("=" * 120)
print("HR PROTOTYPE V3 - EXTRACTION")
print("=" * 120)
print("\nCILJ: Ekstrahirati SAMO hrvatske kampanje (Location = Croatia)")
print("Izvor: Master Backup (100% sirovi podaci)\n")

# ============================================================================
# STEP 1: UCITAJ MASTER BACKUP
# ============================================================================

print("=" * 120)
print("STEP 1: UCITAVANJE MASTER BACKUP FILE")
print("=" * 120)

df_master = pd.read_csv(INPUT_PATH, delimiter=';', encoding='utf-8-sig')

print(f"\nMaster Backup file: {INPUT_PATH}")
print(f"Broj kampanja (GLOBAL): {len(df_master):,}")
print(f"Grand Total (GLOBAL): EUR {df_master['Cost'].sum():,.2f}")
print(f"Broj kolona: {len(df_master.columns)}")

# ============================================================================
# STEP 2: HR EXTRACTION - FILTRIRANJE PO LOKACIJI
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2: HR EXTRACTION - FILTRIRANJE PO LOKACIJI")
print("=" * 120)

# Provjeri kolonu Target_Countries
if 'Target_Countries' not in df_master.columns:
    print("\n[GRESKA] Kolona 'Target_Countries' ne postoji u master file-u!")
    exit(1)

# Analiziraj koliko kampanja ima samo Croatia
print("\nAnaliza Target_Countries kolone:\n")

# Primjeri
print("Primjeri Target_Countries vrijednosti:")
for i, val in enumerate(df_master['Target_Countries'].head(10), 1):
    safe_print(f"  {i}. {val}")

# Filtriraj samo kampanje gdje je ISKLJUČIVO Croatia
# Moguce vrijednosti:
# - "Croatia" (samo HR)
# - "Croatia, Serbia" (multi-market - NE zelimo)
# - "Serbia, Slovenia" (bez HR - NE zelimo)

df_hr = df_master[df_master['Target_Countries'] == 'Croatia'].copy()

print(f"\n\nRezultati filtriranja:")
print(f"  Kampanje sa ISKLJUČIVO Croatia: {len(df_hr):,}")
print(f"  Kampanje odbačene (multi-market): {len(df_master) - len(df_hr):,}")

# Provjeri koje su odbacene
df_rejected = df_master[df_master['Target_Countries'] != 'Croatia']

if len(df_rejected) > 0:
    print(f"\n\nOdbačene kampanje (Top 10 po trošku):")
    df_rejected_sorted = df_rejected.sort_values('Cost', ascending=False)

    for i, row in df_rejected_sorted.head(10).iterrows():
        campaign_name = str(row['Campaign'])[:60].encode('ascii', 'ignore').decode('ascii')
        countries = str(row['Target_Countries'])[:50].encode('ascii', 'ignore').decode('ascii')
        safe_print(f"  - {campaign_name}... | Zemlje: {countries} | EUR {row['Cost']:,.2f}")

    # Ukupni spend odbacenih kampanja
    rejected_spend = df_rejected['Cost'].sum()
    print(f"\n  Ukupni spend odbacenih kampanja: EUR {rejected_spend:,.2f}")

# ============================================================================
# STEP 3: SANITY CHECK - GRAND TOTAL
# ============================================================================

print("\n" + "=" * 120)
print("STEP 3: SANITY CHECK - GRAND TOTAL VERIFICATION")
print("=" * 120)

hr_grand_total = df_hr['Cost'].sum()
expected_hr_total = 2120976.88
tolerance = 1.0  # €1 tolerancija

print(f"\nHR Grand Total (izračunato): EUR {hr_grand_total:,.2f}")
print(f"Očekivani HR Total:          EUR {expected_hr_total:,.2f}")
print(f"Razlika:                     EUR {abs(hr_grand_total - expected_hr_total):,.2f}")

if abs(hr_grand_total - expected_hr_total) <= tolerance:
    print("\n[OK] HR Grand Total MATCH! Filtriranje uspjesno.")
else:
    print(f"\n[UPOZORENJE] HR Grand Total ne odgovara tocno ocekivanom!")
    print(f"Razlika: EUR {abs(hr_grand_total - expected_hr_total):,.2f}")
    print("Ovo je moguce zbog zaokruzivanja ili sitnih razlika u location podacima.")

# ============================================================================
# STEP 4: COLUMN INTEGRITY CHECK
# ============================================================================

print("\n" + "=" * 120)
print("STEP 4: COLUMN INTEGRITY CHECK")
print("=" * 120)

print(f"\nBroj kolona u HR Prototype: {len(df_hr.columns)}")
print(f"Kolone:")

for i, col in enumerate(df_hr.columns, 1):
    print(f"  {i:2d}. {col}")

# Provjeri smart labels
print(f"\n\nSmart Labels provjera:")
print(f"  YouTube_Ad_Formats kolona: {'OK' if 'YouTube_Ad_Formats' in df_hr.columns else 'NEDOSTAJE'}")
print(f"  Demographics_Label kolona: {'OK' if 'Demographics_Label' in df_hr.columns else 'NEDOSTAJE'}")
print(f"  Interests_Label kolona:    {'OK' if 'Interests_Label' in df_hr.columns else 'NEDOSTAJE'}")
print(f"  Start_Date kolona:         {'OK' if 'Start_Date' in df_hr.columns else 'NEDOSTAJE'}")
print(f"  Peak_Reach kolona:         {'OK' if 'Peak_Reach' in df_hr.columns else 'NEDOSTAJE'}")

# ============================================================================
# STEP 5: EXPORT HR PROTOTYPE
# ============================================================================

print("\n" + "=" * 120)
print("STEP 5: EXPORT HR PROTOTYPE FILE")
print("=" * 120)

df_hr.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig', sep=';')

print(f"\nHR Prototype file exported: {OUTPUT_PATH}")
print(f"Broj redaka: {len(df_hr):,}")
print(f"Broj kolona: {len(df_hr.columns):,}")
print(f"Grand Total: EUR {hr_grand_total:,.2f}")

# ============================================================================
# STEP 6: PROTOTYPE STATS
# ============================================================================

print("\n" + "=" * 120)
print("STEP 6: PROTOTYPE STATS - HRVATSKA BAZA")
print("=" * 120)

print(f"\n\nFINALNI HR SPEND: EUR {hr_grand_total:,.2f}")
print(f"BROJ HR KAMPANJA: {len(df_hr):,}")

# Statistika po tipovima
youtube_campaigns = (df_hr['YouTube_Ad_Formats'] != 'Non-YouTube Format').sum()
non_youtube = len(df_hr) - youtube_campaigns

pmax_campaigns = (~df_hr['Has_Demographics']).sum()
demographics_campaigns = df_hr['Has_Demographics'].sum()

print(f"\n\nBREAKDOWN PO TIPOVIMA:")
print(f"  YouTube kampanje:        {youtube_campaigns:,} ({youtube_campaigns/len(df_hr)*100:.1f}%)")
print(f"  Non-YouTube kampanje:    {non_youtube:,} ({non_youtube/len(df_hr)*100:.1f}%)")
print(f"\n  Sa Demographics:         {demographics_campaigns:,} ({demographics_campaigns/len(df_hr)*100:.1f}%)")
print(f"  Bez Demographics (PMax): {pmax_campaigns:,} ({pmax_campaigns/len(df_hr)*100:.1f}%)")

# Reach coverage
with_reach = (df_hr['Peak_Reach'] > 0).sum()
without_reach = (df_hr['Peak_Reach'] == 0).sum()

print(f"\n  Sa Reach podacima:       {with_reach:,} ({with_reach/len(df_hr)*100:.1f}%)")
print(f"  Bez Reach podataka:      {without_reach:,} ({without_reach/len(df_hr)*100:.1f}%)")

# ============================================================================
# STEP 7: TOP 5 BRENDOVA (HRVATSKA)
# ============================================================================

print("\n" + "=" * 120)
print("STEP 7: TOP 5 BRENDOVA U HRVATSKOJ")
print("=" * 120)

# Extract brand from existing data (ako postoji Brand kolona)
if 'Brand' in df_hr.columns:
    brand_col = 'Brand'
else:
    # Kreiraj Brand kolonu iz Account/Campaign
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

    df_hr['Brand'] = df_hr.apply(
        lambda row: extract_brand_smart(row['Campaign'], row['Account']),
        axis=1
    )
    brand_col = 'Brand'

# Top 5 brendova
brand_spend = df_hr.groupby(brand_col)['Cost'].sum().sort_values(ascending=False)

print(f"\n\nTOP 5 BRENDOVA (samo Hrvatska):\n")

for i, (brand, spend) in enumerate(brand_spend.head(5).items(), 1):
    num_campaigns = len(df_hr[df_hr[brand_col] == brand])
    percentage = (spend / hr_grand_total) * 100
    safe_print(f"{i}. {brand:40s} - EUR {spend:>12,.2f} ({percentage:>5.2f}%) - {num_campaigns:>3} kampanja")

# Usporedba sa globalnom bazom
print(f"\n\n{'='*120}")
print("USPOREDBA: GLOBALNA vs HRVATSKA BAZA")
print("=" * 120)

print(f"\n{'Metrika':<40} {'GLOBAL (sve zemlje)':>25} {'HR (samo Croatia)':>25} {'Razlika':>20}")
print("-" * 120)

global_total = df_master['Cost'].sum()
global_campaigns = len(df_master)

safe_print(f"{'Grand Total Spend':<40} EUR {global_total:>18,.2f} EUR {hr_grand_total:>18,.2f} EUR {global_total - hr_grand_total:>15,.2f}")
safe_print(f"{'Broj kampanja':<40} {global_campaigns:>25,} {len(df_hr):>25,} {global_campaigns - len(df_hr):>20,}")

# Spend difference
spend_diff_pct = ((global_total - hr_grand_total) / global_total) * 100
campaign_diff_pct = ((global_campaigns - len(df_hr)) / global_campaigns) * 100

print("\n")
safe_print(f"{'NON-HR Spend (odbaceno)':<40} {'':>25} {'':>25} EUR {global_total - hr_grand_total:>15,.2f} ({spend_diff_pct:.2f}%)")
safe_print(f"{'NON-HR Kampanje (odbacene)':<40} {'':>25} {'':>25} {global_campaigns - len(df_hr):>20,} ({campaign_diff_pct:.2f}%)")

print("\n" + "=" * 120)
print("HR PROTOTYPE KREIRAN - FILE SPREMAN!")
print("=" * 120)
print(f"\nFile: {OUTPUT_PATH}")
print(f"HR Grand Total: EUR {hr_grand_total:,.2f}")
print(f"HR Kampanje: {len(df_hr):,}")
print(f"Status: CISTA HRVATSKA BAZA - spremna za Prototype!")
print("=" * 120)
