#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER FILE GENERATOR - ADS ESTIMATION HUB
Kreira čistu, trajno popravljenu master bazu podataka.
"""

import pandas as pd
import shutil
from datetime import datetime

# ============================================================================
# KONFIGURACIJA
# ============================================================================

# Putanje
MAIN_DB_PATH = "ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"
AD_FORMAT_FIX_PATH = "other-format-cleaned.csv"
BACKUP_PATH = "BACKUP_ADS_HR_PRE_CLEANUP.csv"
MASTER_OUTPUT_PATH = "MASTER_ADS_HR_CLEANED.csv"

print("=" * 80)
print("MASTER FILE GENERATOR - ADS ESTIMATION HUB")
print("=" * 80)
print()

# ============================================================================
# KORAK 1: SIGURNOSNI BACKUP
# ============================================================================

print("KORAK 1: Kreiranje sigurnosnog backup-a...")
print(f"   Kopiram: {MAIN_DB_PATH}")
print(f"   U: {BACKUP_PATH}")

try:
    shutil.copy2(MAIN_DB_PATH, BACKUP_PATH)
    print("   OK - Backup uspjesno kreiran!")
except Exception as e:
    print(f"   ERROR - GRESKA pri kreiranju backup-a: {e}")
    exit(1)

print()

# ============================================================================
# KORAK 2: UČITAVANJE PODATAKA
# ============================================================================

print("KORAK 2: Ucitavanje podataka...")

try:
    # Učitaj glavnu bazu
    df_main = pd.read_csv(MAIN_DB_PATH, delimiter=';', encoding='utf-8-sig')
    print(f"   OK - Ucitana glavna baza: {len(df_main)} redova")

    # Učitaj Ad Format popravke
    df_format_fix = pd.read_csv(AD_FORMAT_FIX_PATH, delimiter=';', encoding='utf-8-sig')
    print(f"   OK - Ucitani Ad Format popravci: {len(df_format_fix)} redova")

except Exception as e:
    print(f"   ERROR - GRESKA pri ucitavanju: {e}")
    exit(1)

print()

# ============================================================================
# KORAK 3: PRIMJENA AD FORMAT POPRAVAKA
# ============================================================================

print("KORAK 3: Primjena Ad Format popravaka...")

# Pripremi lookup dictionary iz df_format_fix
# Ključ: Campaign (originalno ime kampanje)
# Vrijednost: Campaign Type (ispravan format)
format_fix_dict = {}

for idx, row in df_format_fix.iterrows():
    campaign_name = row['Campaign']
    correct_format = row['Campaign Type']
    format_fix_dict[campaign_name] = correct_format

print(f"   Pripremljen dictionary s {len(format_fix_dict)} popravaka")

# Primijeni popravke na glavnu bazu
fixed_count = 0
for idx, row in df_main.iterrows():
    campaign_name = row['Campaign']

    if campaign_name in format_fix_dict:
        # Zamijeni Ad_Format s ispravnom vrijednošću
        correct_format = format_fix_dict[campaign_name]
        df_main.at[idx, 'Ad_Format'] = correct_format
        fixed_count += 1

print(f"   OK - Popravljeno: {fixed_count} kampanja (ocekivano: 131)")

if fixed_count != 131:
    print(f"   UPOZORENJE: Ocekivali smo 131 popravaka, ali smo primijenili {fixed_count}")

print()

# ============================================================================
# KORAK 4: ZAMJENA BRENDA 'CROATIA' → 'HIDRA'
# ============================================================================

print("KORAK 4: Zamjena brenda 'Croatia' -> 'Hidra'...")

# Pronađi sve redove gdje je Brand = 'Croatia'
croatia_mask = df_main['Brand'] == 'Croatia'
croatia_count = croatia_mask.sum()

if croatia_count > 0:
    print(f"   Pronadeno: {croatia_count} kampanja s Brand='Croatia'")

    # Zamijeni sve 'Croatia' s 'Hidra'
    df_main.loc[croatia_mask, 'Brand'] = 'Hidra'

    print(f"   OK - Zamijenjeno: {croatia_count} kampanja -> Brand='Hidra'")
else:
    print("   INFO - Nema kampanja s Brand='Croatia' - preskacujem")

print()

# ============================================================================
# KORAK 5: BRISANJE UNKNOWN QUARTER REDOVA
# ============================================================================

print("KORAK 5: Brisanje redova s Quarter='Unknown'...")

# Provjeri je li 'Quarter' kolona prisutna
if 'Quarter' not in df_main.columns:
    print("   INFO - Kolona 'Quarter' ne postoji - preskacujem brisanje")
    unknown_count = 0
else:
    # Pronađi Unknown redove
    unknown_mask = df_main['Quarter'] == 'Unknown'
    unknown_count = unknown_mask.sum()

    if unknown_count > 0:
        print(f"   Pronadeno: {unknown_count} kampanja s Quarter='Unknown'")

        # Izbriši Unknown redove
        df_main = df_main[~unknown_mask]

        print(f"   OK - Izbrisano: {unknown_count} kampanja")
        print(f"   Preostalo kampanja: {len(df_main)}")
    else:
        print("   INFO - Nema kampanja s Quarter='Unknown' - preskacujem")

print()

# ============================================================================
# KORAK 6: REBUILD STANDARDIZED_CAMPAIGN_NAME
# ============================================================================

print("KORAK 6: Rebuild Standardized_Campaign_Name s novim vrijednostima...")

def rebuild_campaign_name(row):
    """Rebuild standardized name with corrected values."""
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

# Rebuild svih imena
df_main['Standardized_Campaign_Name'] = df_main.apply(rebuild_campaign_name, axis=1)

print(f"   OK - Rebuildan standardizirani naziv za sve kampanje")

print()

# ============================================================================
# KORAK 7: SPREMANJE MASTER FILE-A
# ============================================================================

print("KORAK 7: Spremanje MASTER file-a...")
print(f"   Spremam u: {MASTER_OUTPUT_PATH}")

try:
    df_main.to_csv(MASTER_OUTPUT_PATH, sep=';', encoding='utf-8-sig', index=False)
    print(f"   OK - MASTER file uspjesno kreiran!")
    print(f"   Ukupno kampanja u MASTER-u: {len(df_main)}")
except Exception as e:
    print(f"   ERROR - GRESKA pri spremanju: {e}")
    exit(1)

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("SUCCESS - MASTER FILE GENERIRAN USPJESNO!")
print("=" * 80)
print()
print("SAZETAK:")
print(f"   - Backup kreiran: {BACKUP_PATH}")
print(f"   - Ad Format popravaka: {fixed_count} kampanja")
print(f"   - Brand 'Croatia' -> 'Hidra': {croatia_count} kampanja")
print(f"   - Izbrisano Unknown Quarter: {unknown_count} kampanja")
print(f"   - MASTER file: {MASTER_OUTPUT_PATH}")
print(f"   - Ukupno kampanja u MASTER-u: {len(df_main)}")
print()
print("Sljedeci korak: Azuriraj hub_app.py da ucitava MASTER_ADS_HR_CLEANED.csv")
print("=" * 80)
