#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACCOUNT AUDIT - V3
Identifikacija svih Google Ads Accounta u V3 podacima
"""

import pandas as pd

# ============================================================================
# PATHS
# ============================================================================

path_no_seg = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - no segmentation - all campaigns.csv"
path_seg = "data - v3/campaign - metrics - v3/campaign metrics - version 3 - segmented by ad format - only youtube campaigns.csv"

print("=" * 100)
print("ACCOUNT AUDIT - V3 FINAL DATA")
print("=" * 100)
print("\nCILJ: Identificirati sve Google Ads Accounte koji moraju biti ukljuceni u Report Editoru\n")

# ============================================================================
# UCITAJ NO SEGMENTATION (MASTER FILE)
# ============================================================================

print("=" * 100)
print("STEP 1: ANALIZA NO SEGMENTATION FILE (MASTER - FINANCIJSKO SIDRO)")
print("=" * 100)

df_no_seg = pd.read_csv(path_no_seg, delimiter=';', encoding='utf-8-sig')

print(f"\nDatoteka: {path_no_seg}")
print(f"Broj redaka: {len(df_no_seg):,}")
print(f"Kolone: {list(df_no_seg.columns)}\n")

# Provjeri postoji li Account stupac
if 'Account' in df_no_seg.columns:
    print("OK: Stupac 'Account' POSTOJI!\n")

    # Unikatni accounti
    unique_accounts = df_no_seg['Account'].unique()
    unique_accounts = sorted([acc for acc in unique_accounts if pd.notna(acc)])

    print(f"Broj unikatnih Accounta: {len(unique_accounts)}\n")

    # Parsiraj Cost za statistiku
    def parse_cost(value):
        if pd.isna(value):
            return 0.0
        value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
        try:
            return float(value_str)
        except:
            return 0.0

    df_no_seg['Cost_parsed'] = df_no_seg['Cost'].apply(parse_cost)

    # Grupiraj po accountima
    account_stats = df_no_seg.groupby('Account').agg({
        'Campaign ID': 'nunique',
        'Cost_parsed': 'sum'
    }).reset_index()

    account_stats.columns = ['Account', 'Broj_kampanja', 'Total_Spend']
    account_stats = account_stats.sort_values('Total_Spend', ascending=False)

    print("=" * 100)
    print("POPIS SVIH ACCOUNTA (sortirano po trošku)")
    print("=" * 100)
    print()
    print(f"{'#':<4} {'Account Name':<60} {'Kampanje':<10} {'Spend (EUR)':<15}")
    print("-" * 100)

    for i, row in account_stats.iterrows():
        idx = account_stats.index.get_loc(i) + 1
        account = str(row['Account']).encode('ascii', 'ignore').decode('ascii')
        campaigns = int(row['Broj_kampanja'])
        spend = row['Total_Spend']

        print(f"{idx:<4} {account:<60} {campaigns:<10} EUR {spend:>12,.2f}")

    # Ukupni spend
    total_spend = account_stats['Total_Spend'].sum()
    print("-" * 100)
    print(f"{'UKUPNO':<65} {int(account_stats['Broj_kampanja'].sum()):<10} EUR {total_spend:>12,.2f}")

    # ========================================================================
    # CLEAN LISTA ZA COPY-PASTE
    # ========================================================================

    print("\n" + "=" * 100)
    print("CLEAN LISTA - KOPIRAJ U GOOGLE ADS REPORT EDITOR")
    print("=" * 100)
    print("\nOznaci (check) sljedece Accounte u Report Editoru:\n")

    for i, account in enumerate(unique_accounts, 1):
        account_clean = str(account).encode('ascii', 'ignore').decode('ascii')
        print(f"  [ ] {i}. {account_clean}")

    # ========================================================================
    # DODATNO: TOP BRENDOVI PO ACCOUNTIMA
    # ========================================================================

    print("\n" + "=" * 100)
    print("DODATNO: TOP 10 ACCOUNTA PO TROSKU (detalji)")
    print("=" * 100)

    for i, row in account_stats.head(10).iterrows():
        account = row['Account']
        account_clean = str(account).encode('ascii', 'ignore').decode('ascii')
        campaigns = int(row['Broj_kampanja'])
        spend = row['Total_Spend']
        percentage = (spend / total_spend) * 100

        print(f"\n{account_stats.index.get_loc(i) + 1}. {account_clean}")
        print(f"   Broj kampanja: {campaigns}")
        print(f"   Total Spend: EUR {spend:,.2f} ({percentage:.2f}% ukupnog spenda)")

        # Primjeri kampanja iz tog accounta
        sample_campaigns = df_no_seg[df_no_seg['Account'] == account].head(3)
        print(f"   Primjeri kampanja:")
        for _, camp in sample_campaigns.iterrows():
            camp_name = str(camp['Campaign'])[:70].encode('ascii', 'ignore').decode('ascii')
            print(f"     - {camp_name}...")

else:
    print("UPOZORENJE: Stupac 'Account' NE POSTOJI!")
    print("Pokusavam identificirati accounte iz naziva kampanja...\n")

    # Fallback: pokusaj identificirati iz naziva kampanja
    def identify_brand(campaign_name):
        """Identificiraj brend/klijenta iz naziva kampanje."""
        if pd.isna(campaign_name):
            return "Unknown"

        name = str(campaign_name).lower()

        # Poznati klijenti/brendovi
        if 'mcdonald' in name:
            return "McDonald's"
        elif 'kaufland' in name:
            return "Kaufland"
        elif 'nivea' in name or 'beiersdorf' in name or 'eucerin' in name:
            return "Beiersdorf (Nivea/Eucerin)"
        elif 'philips' in name:
            return "Philips"
        elif 'henkel' in name or 'persil' in name or 'perwoll' in name or 'syoss' in name or 'somat' in name:
            return "Henkel"
        elif 'porsche' in name:
            return "Porsche"
        elif 'omv' in name:
            return "OMV"
        elif 'garnier' in name:
            return "Garnier"
        elif 'ahmad' in name:
            return "Ahmad Tea"
        else:
            return "Other"

    df_no_seg['Identified_Client'] = df_no_seg['Campaign'].apply(identify_brand)

    client_stats = df_no_seg.groupby('Identified_Client').agg({
        'Campaign ID': 'nunique'
    }).reset_index()

    print("Identificirani klijenti/brendovi iz naziva kampanja:")
    print(client_stats)

# ============================================================================
# PROVJERA SEGMENTED FILE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: PROVJERA SEGMENTED FILE (YouTube Campaigns)")
print("=" * 100)

df_seg = pd.read_csv(path_seg, delimiter=';', encoding='utf-8-sig')

print(f"\nDatoteka: {path_seg}")
print(f"Broj redaka: {len(df_seg):,}")

if 'Account' in df_seg.columns:
    unique_accounts_seg = df_seg['Account'].unique()
    unique_accounts_seg = sorted([acc for acc in unique_accounts_seg if pd.notna(acc)])

    print(f"Broj unikatnih Accounta u segmented file: {len(unique_accounts_seg)}\n")

    # Provjeri jesu li isti kao u no segmentation
    if set(unique_accounts_seg).issubset(set(unique_accounts)):
        print("OK: Svi accounti iz segmented file postoje u no segmentation file")
    else:
        print("UPOZORENJE: Neki accounti iz segmented file ne postoje u no segmentation!")
        missing = set(unique_accounts_seg) - set(unique_accounts)
        print(f"Accounti koji nedostaju: {missing}")

print("\n" + "=" * 100)
print("AUDIT ZAVRSEN")
print("=" * 100)
print("\nKORISTI GORNJU 'CLEAN LISTU' ZA OZNACAVANJE ACCOUNTA U GOOGLE ADS REPORT EDITORU!")
print("=" * 100)
