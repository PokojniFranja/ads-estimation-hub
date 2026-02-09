#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA-MERGE & STANDARDIZATION V4
Finalna standardizacija HR Prototypea sa mega-imenima
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

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

def shorten_bidding_strategy(bid_strategy):
    """Skrati naziv bidding strategije."""
    if pd.isna(bid_strategy):
        return "Unknown"

    bid = str(bid_strategy).strip()

    # Mapping
    mapping = {
        'Viewable CPM': 'vCPM',
        'viewable CPM': 'vCPM',
        'Maximize conversions': 'MaxConv',
        'Maximise conversions': 'MaxConv',
        'Maximize conversion value': 'MaxConvValue',
        'Maximise conversion value': 'MaxConvValue',
        'Target CPA': 'tCPA',
        'Target ROAS': 'tROAS',
        'Target CPM': 'tCPM',
        'Manual CPC': 'CPC',
        'Manual CPM': 'CPM',
        'Manual CPV': 'CPV',
        'Target CPV': 'tCPV',
        'Maximize clicks': 'MaxClicks',
        'Maximise clicks': 'MaxClicks'
    }

    for key, value in mapping.items():
        if key.lower() in bid.lower():
            return value

    return bid

def format_date_range(start_date, end_date):
    """Format date range to 'Oct-Dec 25' style."""
    if pd.isna(start_date) or pd.isna(end_date):
        return "Unknown Period"

    try:
        # Parse dates
        start = pd.to_datetime(start_date, dayfirst=True, errors='coerce')
        end = pd.to_datetime(end_date, dayfirst=True, errors='coerce')

        if pd.isna(start) or pd.isna(end):
            return "Unknown Period"

        # Format
        start_month = start.strftime('%b')
        end_month = end.strftime('%b')
        year = start.strftime('%y')

        if start_month == end_month:
            return f"{start_month} {year}"
        else:
            return f"{start_month}-{end_month} {year}"

    except:
        return "Unknown Period"

def extract_brand_from_account(account_name, campaign_name):
    """Extract brand from account or campaign name."""
    if pd.isna(account_name):
        account_name = ""
    if pd.isna(campaign_name):
        campaign_name = ""

    name = str(campaign_name).lower()
    account = str(account_name).lower()

    # Known brands
    if "mcdonald" in name or "mcdonald" in account:
        return "McDonald's"
    elif "kaufland" in account or "kaufland" in name:
        return "Kaufland"
    elif "nivea" in account or "nivea" in name:
        return "Nivea"
    elif "eucerin" in account or "eucerin" in name:
        return "Eucerin"
    elif "philips" in account or "philips" in name:
        return "Philips"
    elif "persil" in name or "persil" in account:
        return "Persil"
    elif "perwoll" in name or "perwoll" in account:
        return "Perwoll"
    elif "syoss" in name or "syoss" in account:
        return "Syoss"
    elif "weisser" in name or "weisser" in account:
        return "Weisser Riese"
    elif "somat" in name or "somat" in account:
        return "Somat"
    elif "bref" in name or "bref" in account:
        return "Bref"
    elif "porsche" in account:
        return "Porsche"
    elif "nissan" in account or "nissan" in name:
        return "Nissan"
    elif "zott" in account or "zott" in name:
        return "Zott"
    elif "jgl" in account:
        return "JGL"
    elif "energycom" in name or "energycom" in account:
        return "Energycom"
    elif "bosch" in account:
        return "Bosch"
    elif "saponia" in account:
        return "Saponia"
    else:
        # Fallback
        return str(account_name).split('_')[0].split('//')[0][:20] if account_name else "Unknown"

def extract_ad_format(youtube_formats, campaign_name):
    """Extract ad format."""
    if pd.isna(youtube_formats) or youtube_formats == 'Non-YouTube Format':
        # Non-YouTube - pokusaj iz naziva
        name = str(campaign_name).lower()
        if 'pmax' in name or 'performance max' in name:
            return "PMax"
        elif 'gdn' in name or 'display' in name:
            return "Display"
        elif 'demand' in name or '(dg)' in name:
            return "Demand Gen"
        else:
            return "Other"
    else:
        # YouTube formats
        formats = str(youtube_formats)
        if 'Skippable in-stream' in formats:
            return "YouTube In-Stream"
        elif 'Bumper' in formats:
            return "YouTube Bumper"
        elif 'Shorts' in formats:
            return "YouTube Shorts"
        elif 'In-feed' in formats:
            return "YouTube In-Feed"
        elif 'Non-skippable' in formats:
            return "YouTube Non-Skip"
        else:
            return "YouTube"

def determine_goal(bid_strategy, ad_format):
    """Determine campaign goal based on bidding strategy and ad format."""
    bid = str(bid_strategy).lower()
    fmt = str(ad_format).lower()

    # Awareness goals
    if 'vcpm' in bid or 'cpm' in bid:
        return "Awareness"
    # Action goals
    elif 'maxconv' in bid or 'tcpa' in bid or 'troas' in bid:
        return "Action"
    # Consideration goals
    elif 'cpv' in bid or 'tcpv' in bid:
        return "Consideration"
    # Based on format
    elif 'bumper' in fmt or 'shorts' in fmt:
        return "Awareness"
    elif 'pmax' in fmt:
        return "Action"
    else:
        return "Consideration"

# ============================================================================
# PATHS
# ============================================================================

PATH_HR_PROTOTYPE = "ads_estimation_hub_HR_PROTOTYPE_V3_CLEANED.csv"
PATH_BIDDING = "data - v3/campaign - bidding strategies - v3/campaign - bidding strategies - version 3.csv"
PATH_AGE_GENDER = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"
OUTPUT_PATH = "ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"

print("=" * 120)
print("MEGA-MERGE & STANDARDIZATION V4")
print("=" * 120)
print("\nCILJ: Kreirati finalni standardizirani HR Prototype sa 'mega-imenima'\n")

# ============================================================================
# STEP 1: UCITAJ HR PROTOTYPE (CLEANED)
# ============================================================================

print("=" * 120)
print("STEP 1: UCITAVANJE HR PROTOTYPE (CLEANED)")
print("=" * 120)

df_hr = pd.read_csv(PATH_HR_PROTOTYPE, delimiter=';', encoding='utf-8-sig')

print(f"\nHR Prototype file: {PATH_HR_PROTOTYPE}")
print(f"Broj kampanja: {len(df_hr):,}")
print(f"Grand Total Spend: EUR {df_hr['Cost'].sum():,.2f}")

# ============================================================================
# STEP 2: UCITAJ BIDDING STRATEGIES
# ============================================================================

print("\n" + "=" * 120)
print("STEP 2: UCITAVANJE BIDDING STRATEGIES")
print("=" * 120)

df_bidding = pd.read_csv(PATH_BIDDING, delimiter=';', encoding='utf-8-sig')

print(f"\nBidding file: {PATH_BIDDING}")
print(f"Broj redaka: {len(df_bidding):,}")
print(f"Broj unikatnih Campaign ID-eva: {df_bidding['Campaign ID'].nunique():,}")

# Selektiraj samo relevantne kolone
df_bidding_clean = df_bidding[['Campaign ID', 'Campaign bid strategy type']].drop_duplicates()

# Merge sa HR prototype
df_hr = df_hr.merge(df_bidding_clean, on='Campaign ID', how='left')

print(f"\nNakon merge-a:")
print(f"  Kampanje sa bidding podacima: {df_hr['Campaign bid strategy type'].notna().sum():,}")
print(f"  Kampanje bez bidding podataka: {df_hr['Campaign bid strategy type'].isna().sum():,}")

# ============================================================================
# STEP 3: UCITAJ AGE-GENDER (ZA TARGET INFO)
# ============================================================================

print("\n" + "=" * 120)
print("STEP 3: UCITAVANJE AGE-GENDER (za TARGET informacije)")
print("=" * 120)

df_age = pd.read_csv(PATH_AGE_GENDER, delimiter=';', encoding='utf-8-sig')

print(f"\nAge-Gender file: {PATH_AGE_GENDER}")
print(f"Broj redaka: {len(df_age):,}")

# Grupiraj po Campaign ID i izvuci age/gender info
def extract_target_info(campaign_id):
    """Extract target demographics info."""
    campaign_data = df_age[df_age['Campaign ID'] == campaign_id]

    if len(campaign_data) == 0:
        return "All | All"

    # Extract ages
    ages = campaign_data['Age'].unique()
    genders = campaign_data['Gender'].unique()

    # Parsiraj age range
    age_mapping = {
        '18-24': 18,
        '25-34': 25,
        '35-44': 35,
        '45-54': 45,
        '55-64': 55,
        '65+': 65,
        'Undetermined': 999
    }

    age_nums = []
    for age in ages:
        if pd.notna(age) and age in age_mapping:
            age_nums.append(age_mapping[age])

    if len(age_nums) > 0:
        age_nums = [x for x in age_nums if x < 999]
        if len(age_nums) == 0:
            age_range = "All"
        elif len(age_nums) == 1:
            # Single age group
            for age_label, age_num in age_mapping.items():
                if age_num == age_nums[0]:
                    age_range = age_label
                    break
        else:
            # Range
            min_age = min(age_nums)
            max_age = max(age_nums)

            # Find labels
            min_label = None
            max_label = None
            for age_label, age_num in age_mapping.items():
                if age_num == min_age:
                    min_label = age_label.split('-')[0]
                if age_num == max_age:
                    if age_label == '65+':
                        max_label = '65+'
                    else:
                        max_label = age_label.split('-')[1]

            if min_label and max_label:
                age_range = f"{min_label}-{max_label}"
            else:
                age_range = "All"
    else:
        age_range = "All"

    # Gender
    if len(genders) == 1 and genders[0] in ['Male', 'Female']:
        if genders[0] == 'Male':
            gender_str = "M"
        else:
            gender_str = "F"
    elif set(genders) == {'Male', 'Female'}:
        gender_str = "M/F"
    else:
        gender_str = "All"

    return f"{age_range} | {gender_str}"

# Dodaj TARGET kolonu
print("\nIzvlacenje TARGET informacija...")
df_hr['Target'] = df_hr.apply(
    lambda row: extract_target_info(row['Campaign ID']) if row['Has_Demographics'] else "Auto | All",
    axis=1
)

print(f"  OK - TARGET kolona kreirana")

# ============================================================================
# STEP 4: KREIRANJE KOMPONENTI ZA MEGA NAME
# ============================================================================

print("\n" + "=" * 120)
print("STEP 4: KREIRANJE KOMPONENTI ZA MEGA NAME")
print("=" * 120)

# Brand
df_hr['Brand'] = df_hr.apply(
    lambda row: extract_brand_from_account(row['Account'], row['Campaign']),
    axis=1
)

# Ad Format
df_hr['Ad_Format'] = df_hr.apply(
    lambda row: extract_ad_format(row['YouTube_Ad_Formats'], row['Campaign']),
    axis=1
)

# Date Range
df_hr['Date_Range'] = df_hr.apply(
    lambda row: format_date_range(row['Start_Date'], row['End_Date']),
    axis=1
)

# Bidding Strategy (shortened)
df_hr['Bid_Strategy_Short'] = df_hr['Campaign bid strategy type'].apply(shorten_bidding_strategy)

# Goal
df_hr['Goal'] = df_hr.apply(
    lambda row: determine_goal(row['Bid_Strategy_Short'], row['Ad_Format']),
    axis=1
)

print(f"\nKomponente kreirane:")
print(f"  Brand: {df_hr['Brand'].nunique()} unikatnih")
print(f"  Ad_Format: {df_hr['Ad_Format'].nunique()} tipova")
print(f"  Date_Range: {df_hr['Date_Range'].nunique()} perioda")
print(f"  Bid_Strategy: {df_hr['Bid_Strategy_Short'].nunique()} strategija")
print(f"  Goal: {df_hr['Goal'].nunique()} ciljeva")

# ============================================================================
# STEP 5: KONSTRUKCIJA MEGA NAME
# ============================================================================

print("\n" + "=" * 120)
print("STEP 5: KONSTRUKCIJA MEGA NAME")
print("=" * 120)

# Format: [BRAND] | [AD_FORMAT] | [TARGET] | [DATE_RANGE] | [BID_STRATEGY] | [GOAL]

df_hr['Standardized_Campaign_Name'] = (
    df_hr['Brand'].astype(str) + " | " +
    df_hr['Ad_Format'].astype(str) + " | " +
    df_hr['Target'].astype(str) + " | " +
    df_hr['Date_Range'].astype(str) + " | " +
    df_hr['Bid_Strategy_Short'].astype(str) + " | " +
    df_hr['Goal'].astype(str)
)

print(f"\nStandardized_Campaign_Name kolona kreirana!")
print(f"Primjer duljina naziva: {df_hr['Standardized_Campaign_Name'].str.len().mean():.0f} znakova (prosjek)")

# ============================================================================
# STEP 6: EXPORT
# ============================================================================

print("\n" + "=" * 120)
print("STEP 6: EXPORT STANDARDIZED PROTOTYPE")
print("=" * 120)

df_hr.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig', sep=';')

print(f"\nFile exported: {OUTPUT_PATH}")
print(f"Broj kampanja: {len(df_hr):,}")
print(f"Broj kolona: {len(df_hr.columns):,}")
print(f"Grand Total: EUR {df_hr['Cost'].sum():,.2f}")

# ============================================================================
# STEP 7: PRIMJERI MEGA-IMENA
# ============================================================================

print("\n" + "=" * 120)
print("STEP 7: PRIMJERI MEGA-IMENA (Top 5 po trosku)")
print("=" * 120)

# Top 5 po trosku
top5 = df_hr.nlargest(5, 'Cost')

print(f"\n\n{'#':<3} {'Spend':<15} {'Original Name':<60} Mega Name")
print("-" * 120)

for i, row in top5.iterrows():
    rank = list(top5.index).index(i) + 1
    spend = row['Cost']
    original = str(row['Campaign'])[:60]
    mega = row['Standardized_Campaign_Name']

    safe_print(f"{rank:<3} EUR {spend:>10,.2f} {original:<60}")
    safe_print(f"{'':>19} MEGA: {mega}\n")

# ============================================================================
# STEP 8: SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 120)
print("STEP 8: SUMMARY STATISTICS")
print("=" * 120)

print(f"""
BREAKDOWN PO KOMPONENTAMA:

BRAND (Top 5):
""")

brand_counts = df_hr['Brand'].value_counts().head(5)
for brand, count in brand_counts.items():
    safe_print(f"  {brand:30s} - {count:>3} kampanja")

print(f"""
AD FORMAT:
""")

format_counts = df_hr['Ad_Format'].value_counts()
for fmt, count in format_counts.items():
    safe_print(f"  {fmt:30s} - {count:>3} kampanja")

print(f"""
BIDDING STRATEGY (Top 5):
""")

bid_counts = df_hr['Bid_Strategy_Short'].value_counts().head(5)
for bid, count in bid_counts.items():
    safe_print(f"  {bid:30s} - {count:>3} kampanja")

print(f"""
GOAL:
""")

goal_counts = df_hr['Goal'].value_counts()
for goal, count in goal_counts.items():
    safe_print(f"  {goal:30s} - {count:>3} kampanja")

print("\n" + "=" * 120)
print("MEGA-MERGE & STANDARDIZATION ZAVRSEN!")
print("=" * 120)
print(f"\nFile: {OUTPUT_PATH}")
print(f"Status: FINALNI HR PROTOTYPE - sa standardiziranim mega-imenima")
print("=" * 120)
