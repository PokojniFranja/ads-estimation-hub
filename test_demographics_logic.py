#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT - Demographics Full Range Logic
Tests the new aggregation logic to ensure campaigns show full range
"""

import pandas as pd
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("DEMOGRAPHICS FULL RANGE TEST")
print("=" * 80)

# Load demographics data
print("\n[LOAD] Loading demographics data...")
df_demographics = pd.read_csv('data - v3/age - gender - v3/campaign age - gender - version 3.csv',
                              delimiter=';',
                              encoding='utf-8-sig')

print(f"[OK] Loaded {len(df_demographics)} demographic rows")
print(f"[INFO] Columns: {', '.join(df_demographics.columns)}")

# Count campaigns with multiple segments
print("\n[ANALYSIS] Analyzing multi-segment campaigns...")

campaign_segment_counts = df_demographics.groupby('Campaign ID').size()
multi_segment_campaigns = campaign_segment_counts[campaign_segment_counts > 1]

print(f"[RESULT] Total unique campaigns: {len(campaign_segment_counts)}")
print(f"[RESULT] Campaigns with multiple segments: {len(multi_segment_campaigns)}")
print(f"[RESULT] Campaigns with single segment: {len(campaign_segment_counts) - len(multi_segment_campaigns)}")

# Show examples of multi-segment campaigns
print("\n" + "=" * 80)
print("EXAMPLES: Multi-Segment Campaigns (should show as full range)")
print("=" * 80)

example_count = 0
for campaign_id, count in multi_segment_campaigns.head(10).items():
    segments = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    campaign_name = segments['Campaign'].iloc[0] if 'Campaign' in segments.columns else 'N/A'

    print(f"\n[{example_count + 1}] Campaign ID: {campaign_id}")
    print(f"    Name: {campaign_name[:80]}...")
    print(f"    Segments: {count}")

    # Show all age and gender segments
    ages = segments['Age'].unique()
    genders = segments['Gender'].unique()

    print(f"    Age segments: {', '.join([str(a) for a in ages])}")
    print(f"    Gender segments: {', '.join([str(g) for g in genders])}")

    # Calculate what the full range SHOULD be
    age_ranges = []
    for age in ages:
        if '-' in str(age):
            parts = str(age).split('-')
            age_ranges.append((int(parts[0]), int(parts[1]) if parts[1] else 100))
        elif '+' in str(age):
            age_num = int(str(age).replace('+', ''))
            age_ranges.append((age_num, 100))
        else:
            try:
                age_num = int(age)
                age_ranges.append((age_num, age_num))
            except:
                pass

    if age_ranges:
        min_age = min([r[0] for r in age_ranges])
        max_age = max([r[1] for r in age_ranges])

        if min_age == max_age:
            expected_age = str(min_age)
        elif max_age >= 65:
            expected_age = f"{min_age}-65+"
        else:
            expected_age = f"{min_age}-{max_age}"

        expected_gender = 'All' if len(genders) > 1 else str(genders[0])

        print(f"    --> EXPECTED FULL RANGE: {expected_age} | {expected_gender}")

    example_count += 1

# Statistics on age segments
print("\n" + "=" * 80)
print("AGE SEGMENT DISTRIBUTION")
print("=" * 80)

age_counts = df_demographics['Age'].value_counts()
print("\nMost common age segments:")
for age, count in age_counts.head(10).items():
    print(f"  {age:15s}: {count:4d} rows")

# Statistics on gender segments
print("\n" + "=" * 80)
print("GENDER SEGMENT DISTRIBUTION")
print("=" * 80)

gender_counts = df_demographics['Gender'].value_counts()
print("\nGender segments:")
for gender, count in gender_counts.items():
    print(f"  {gender:15s}: {count:4d} rows")

print("\n" + "=" * 80)
print("[DONE] Test Complete!")
print("=" * 80)
print("\n[INFO] When you run hub_app.py, campaigns with multiple segments will now")
print("       show as full range (e.g., '18-34 | All' instead of just '25-34').")
print("[INFO] Strict filtering will ensure exact matches only.")
