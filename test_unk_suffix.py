#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT - '+ UNK' Suffix Logic
Tests that campaigns with Unknown spend get '+ UNK' suffix
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("TEST: '+ UNK' SUFFIX LOGIC")
print("=" * 80)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_cost(value):
    """Parse cost values."""
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace('EUR', '').replace(',', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

def parse_age_range(age_str):
    """Parse age range string to get min and max age."""
    age_str = str(age_str).strip()
    if age_str in ['Unknown', '', 'N/A']:
        return (0, 0)
    age_str_clean = age_str.replace(' ', '')
    if '-' in age_str_clean:
        parts = age_str_clean.split('-')
        try:
            age_min = int(parts[0])
            age_max_str = parts[1].replace('+', '')
            age_max = int(age_max_str) if age_max_str else 100
        except:
            return (0, 0)
    elif '+' in age_str_clean:
        try:
            age_min = int(age_str_clean.replace('+', ''))
            age_max = 100
        except:
            return (0, 0)
    else:
        try:
            age_min = age_max = int(age_str_clean)
        except:
            return (0, 0)
    return (age_min, age_max)

def get_full_range_demographics(campaign_id, df_demographics, threshold=0.10):
    """Get FULL RANGE demographics with THRESHOLD and + UNK suffix."""
    if df_demographics is None or len(df_demographics) == 0:
        return ("Unknown", "Unknown")

    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    if len(demo_data) == 0:
        return ("Unknown", "Unknown")

    total_spend = demo_data['Cost_parsed'].sum()

    if total_spend == 0:
        return ("Unknown", "Unknown")

    age_spend = demo_data.groupby('Age')['Cost_parsed'].sum()

    significant_ages = []
    for age, spend in age_spend.items():
        age_str = str(age).strip()

        if age_str in ['Unknown', 'nan', '', 'N/A']:
            continue

        percentage = spend / total_spend

        if percentage >= threshold:
            significant_ages.append((age_str, spend, percentage))

    if len(significant_ages) == 0:
        valid_ages = {age: spend for age, spend in age_spend.items()
                      if str(age).strip() not in ['Unknown', 'nan', '', 'N/A']}

        if len(valid_ages) > 0:
            dominant_age = max(valid_ages, key=valid_ages.get)
            dominant_spend = valid_ages[dominant_age]
            significant_ages = [(str(dominant_age), dominant_spend, dominant_spend / total_spend)]
        else:
            return ("Unknown", "Unknown")

    significant_ages.sort(key=lambda x: x[2], reverse=True)

    if len(significant_ages) == 1:
        age_range = significant_ages[0][0]
    else:
        age_strings = [a[0] for a in significant_ages]

        age_min = 999
        age_max = 0

        for age_str in age_strings:
            min_age, max_age = parse_age_range(age_str)
            if min_age > 0:
                if min_age < age_min:
                    age_min = min_age
                if max_age < 100 and max_age > age_max:
                    age_max = max_age
                elif max_age >= 100:
                    age_max = 65

        if age_min == 999 or age_max == 0:
            age_range = significant_ages[0][0]
        elif age_min == age_max:
            age_range = str(age_min)
        elif age_max >= 65:
            age_range = f"{age_min}-65+"
        else:
            age_range = f"{age_min}-{age_max}"

    gender_spend = demo_data.groupby('Gender')['Cost_parsed'].sum()

    significant_genders = []
    for gender, spend in gender_spend.items():
        gender_str = str(gender).strip()

        if gender_str in ['Unknown', 'nan', '', 'N/A']:
            continue

        percentage = spend / total_spend

        if percentage >= threshold:
            significant_genders.append(gender_str)

    if len(significant_genders) == 0:
        valid_genders = {gender: spend for gender, spend in gender_spend.items()
                        if str(gender).strip() not in ['Unknown', 'nan', '', 'N/A']}

        if len(valid_genders) > 0:
            dominant_gender = max(valid_genders, key=valid_genders.get)
            significant_genders = [str(dominant_gender)]
        else:
            gender = 'Unknown'
            return (age_range, gender)

    gender_map = {
        'F': 'Female',
        'M': 'Male',
        'Female': 'Female',
        'Male': 'Male',
    }

    genders_normalized = [gender_map.get(g, g) for g in significant_genders]

    if len(genders_normalized) > 1:
        gender = 'All'
    else:
        gender = genders_normalized[0]

    # CRITICAL: Check if campaign has ANY spend in Unknown category
    unknown_spend = 0
    for age, spend in age_spend.items():
        age_str = str(age).strip()
        if age_str in ['Unknown', 'nan', '', 'N/A', 'Undetermined']:
            unknown_spend += spend

    # Add + UNK suffix if there's at least 0.01 EUR in Unknown
    if unknown_spend >= 0.01:
        age_range = age_range + ' + UNK'

    return (age_range, gender)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n[LOAD] Loading demographics data...")
df_demographics = pd.read_csv('data - v3/age - gender - v3/campaign age - gender - version 3.csv',
                              delimiter=';',
                              encoding='utf-8-sig')

print(f"[OK] Loaded {len(df_demographics)} demographic rows")

# Parse costs
df_demographics['Cost_parsed'] = df_demographics['Cost'].apply(parse_cost)

# ============================================================================
# TEST '+ UNK' SUFFIX
# ============================================================================

print("\n" + "=" * 80)
print("TESTING: Finding campaigns with Unknown spend")
print("=" * 80)

campaign_ids = df_demographics['Campaign ID'].unique()

campaigns_with_unknown = []
campaigns_without_unknown = []

for campaign_id in campaign_ids[:200]:  # Test first 200
    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    total_spend = demo_data['Cost_parsed'].sum()

    if total_spend == 0:
        continue

    # Check Unknown spend
    age_spend = demo_data.groupby('Age')['Cost_parsed'].sum()

    unknown_spend = 0
    for age, spend in age_spend.items():
        age_str = str(age).strip()
        if age_str in ['Unknown', 'nan', '', 'N/A', 'Undetermined']:
            unknown_spend += spend

    if unknown_spend >= 0.01:
        unknown_pct = (unknown_spend / total_spend) * 100
        campaigns_with_unknown.append({
            'campaign_id': campaign_id,
            'total_spend': total_spend,
            'unknown_spend': unknown_spend,
            'unknown_pct': unknown_pct
        })
    else:
        campaigns_without_unknown.append(campaign_id)

print(f"\n[RESULT] Campaigns with Unknown spend: {len(campaigns_with_unknown)}")
print(f"[RESULT] Campaigns without Unknown spend: {len(campaigns_without_unknown)}")

# Test first 5 campaigns with Unknown
print("\n" + "=" * 80)
print("DETAILED TEST: Campaigns WITH Unknown spend")
print("=" * 80)

for i, test in enumerate(campaigns_with_unknown[:5]):
    campaign_id = test['campaign_id']

    print(f"\n[TEST {i+1}] Campaign ID: {campaign_id}")

    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]
    campaign_name = demo_data['Campaign'].iloc[0] if 'Campaign' in demo_data.columns else 'N/A'

    print(f"[INFO] Name: {campaign_name[:80]}")
    print(f"[INFO] Total Spend: EUR {test['total_spend']:,.2f}")
    print(f"[INFO] Unknown Spend: EUR {test['unknown_spend']:,.2f} ({test['unknown_pct']:.2f}%)")

    # Apply logic
    age_range, gender = get_full_range_demographics(campaign_id, df_demographics, threshold=0.10)

    print(f"\n[RESULT] Age Range: {age_range}")
    print(f"[RESULT] Gender: {gender}")

    # Check if + UNK suffix is present
    if ' + UNK' in age_range:
        print("  [PASS] '+ UNK' suffix correctly added!")
    else:
        print("  [FAIL] '+ UNK' suffix missing!")

    print("-" * 80)

# Test campaigns WITHOUT Unknown
print("\n" + "=" * 80)
print("DETAILED TEST: Campaigns WITHOUT Unknown spend")
print("=" * 80)

for i, campaign_id in enumerate(campaigns_without_unknown[:3]):
    print(f"\n[TEST {i+1}] Campaign ID: {campaign_id}")

    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]
    campaign_name = demo_data['Campaign'].iloc[0] if 'Campaign' in demo_data.columns else 'N/A'

    print(f"[INFO] Name: {campaign_name[:80]}")

    total_spend = demo_data['Cost_parsed'].sum()
    print(f"[INFO] Total Spend: EUR {total_spend:,.2f}")

    # Apply logic
    age_range, gender = get_full_range_demographics(campaign_id, df_demographics, threshold=0.10)

    print(f"\n[RESULT] Age Range: {age_range}")
    print(f"[RESULT] Gender: {gender}")

    # Check that + UNK suffix is NOT present
    if ' + UNK' not in age_range:
        print("  [PASS] '+ UNK' suffix correctly NOT added!")
    else:
        print("  [FAIL] '+ UNK' suffix incorrectly added!")

    print("-" * 80)

print("\n" + "=" * 80)
print("[DONE] '+ UNK' Suffix Test Complete")
print("=" * 80)
