#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT - Threshold Logic Verification
Tests that 10% threshold filtering works correctly
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("THRESHOLD LOGIC TEST (10% Minimum)")
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
    """Get FULL RANGE demographics with THRESHOLD FILTERING."""
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
# TEST THRESHOLD LOGIC
# ============================================================================

print("\n" + "=" * 80)
print("TESTING: Finding campaigns with concentrated spend (95%+ in one segment)")
print("=" * 80)

# Group by campaign and analyze spend distribution
campaign_ids = df_demographics['Campaign ID'].unique()

test_campaigns = []

for campaign_id in campaign_ids[:100]:  # Test first 100 campaigns
    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    total_spend = demo_data['Cost_parsed'].sum()

    if total_spend == 0:
        continue

    # Calculate age spend distribution
    age_spend = demo_data.groupby('Age')['Cost_parsed'].sum()

    # Find max percentage (excluding Unknown)
    valid_ages = {age: spend for age, spend in age_spend.items()
                  if str(age).strip() not in ['Unknown', 'nan', '', 'N/A']}

    if len(valid_ages) > 0:
        max_age = max(valid_ages, key=valid_ages.get)
        max_spend = valid_ages[max_age]
        max_percentage = max_spend / total_spend

        # If one segment has 90%+ of spend, it's a good test case
        if max_percentage >= 0.90:
            test_campaigns.append({
                'campaign_id': campaign_id,
                'max_age': max_age,
                'max_percentage': max_percentage,
                'total_spend': total_spend,
                'num_segments': len(demo_data)
            })

print(f"\n[FOUND] {len(test_campaigns)} campaigns with 90%+ spend in one age segment")

# Test first 5 campaigns
print("\n" + "=" * 80)
print("DETAILED TEST RESULTS:")
print("=" * 80)

for i, test in enumerate(test_campaigns[:5]):
    campaign_id = test['campaign_id']

    print(f"\n[TEST {i+1}] Campaign ID: {campaign_id}")

    # Get campaign name
    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]
    campaign_name = demo_data['Campaign'].iloc[0] if 'Campaign' in demo_data.columns else 'N/A'

    print(f"[INFO] Name: {campaign_name[:80]}")
    print(f"[INFO] Total Spend: EUR {test['total_spend']:,.2f}")
    print(f"[INFO] Segments: {test['num_segments']}")

    # Show spend distribution
    age_spend = demo_data.groupby('Age')['Cost_parsed'].sum().sort_values(ascending=False)

    print(f"\n[DISTRIBUTION] Age Spend Breakdown:")
    for age, spend in age_spend.head(5).items():
        percentage = (spend / test['total_spend']) * 100
        print(f"  {age:15s}: EUR {spend:8,.2f} ({percentage:5.1f}%)")

    # Apply threshold logic
    age_range, gender = get_full_range_demographics(campaign_id, df_demographics, threshold=0.10)

    print(f"\n[RESULT] With 10% Threshold:")
    print(f"  Age Range: {age_range}")
    print(f"  Gender: {gender}")

    # Expected result
    print(f"\n[EXPECTED] Should be: '{test['max_age']}' (since {test['max_percentage']*100:.1f}% in one segment)")

    # Validation
    if age_range == test['max_age']:
        print(f"  [PASS] Correct! Not expanded to full range.")
    else:
        print(f"  [INFO] Result differs: got '{age_range}' instead of '{test['max_age']}'")

    print("-" * 80)

# ============================================================================
# STATISTICS ON UNIQUE AGE RANGES
# ============================================================================

print("\n" + "=" * 80)
print("AGE RANGE STATISTICS (with 10% threshold)")
print("=" * 80)

# Calculate age ranges for all campaigns
age_ranges = {}

for campaign_id in campaign_ids:
    age_range, gender = get_full_range_demographics(campaign_id, df_demographics, threshold=0.10)

    if age_range not in age_ranges:
        age_ranges[age_range] = 0
    age_ranges[age_range] += 1

# Sort by count
sorted_ranges = sorted(age_ranges.items(), key=lambda x: x[1], reverse=True)

print(f"\n[RESULT] Total unique age ranges: {len(sorted_ranges)}")
print(f"\n[TOP 20] Most common age ranges:")

for i, (age_range, count) in enumerate(sorted_ranges[:20]):
    percentage = (count / len(campaign_ids)) * 100
    print(f"  {i+1:2d}. {age_range:20s}: {count:4d} campaigns ({percentage:5.1f}%)")

# Count how many are "18-65+"
full_range_count = age_ranges.get('18-65+', 0)
full_range_pct = (full_range_count / len(campaign_ids)) * 100

print(f"\n[CHECK] Campaigns with '18-65+' range: {full_range_count} ({full_range_pct:.1f}%)")

if full_range_pct < 50:
    print("[PASS] Threshold logic is working! Most campaigns are NOT '18-65+'")
else:
    print("[WARNING] Still too many '18-65+' campaigns. Threshold may need adjustment.")

print("\n" + "=" * 80)
print("[DONE] Threshold Logic Test Complete")
print("=" * 80)
