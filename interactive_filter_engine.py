#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERACTIVE FILTER ENGINE - PRODUCTION VERSION
Kompletni filter engine sa strukturiranim prikazom
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

def parse_impressions(value):
    if pd.isna(value):
        return 0
    value_str = str(value).strip().replace(',', '').strip()
    try:
        return int(float(value_str))
    except:
        return 0

def safe_print(text):
    """Safely print text with encoding handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

# ============================================================================
# INTERACTIVE FILTER ENGINE CLASS
# ============================================================================

class InteractiveFilterEngine:
    """Interactive filter engine with structured display."""

    def __init__(self, df_campaigns, df_age_gender, df_country):
        self.df_campaigns = df_campaigns.copy()
        self.df_age_gender = df_age_gender.copy()
        self.df_country = df_country.copy()

        # Parse numeric columns
        self.df_campaigns['Cost_parsed'] = self.df_campaigns['Cost'].apply(parse_cost)
        self.df_campaigns['Impr_parsed'] = self.df_campaigns['Impr.'].apply(parse_impressions)

        self.df_age_gender['Cost_parsed'] = self.df_age_gender['Cost'].apply(parse_cost)
        self.df_country['Cost_parsed'] = self.df_country['Cost'].apply(parse_cost)

    def filter_campaigns(self, brand=None, format_type=None, target_gender=None, target_age=None, period=None):
        """Apply filters to campaigns."""
        df = self.df_campaigns.copy()

        # Brand filter
        if brand:
            df = df[df['Brand'].str.lower().str.contains(str(brand).lower(), na=False)]

        # Format filter
        if format_type:
            fmt = str(format_type).lower()
            mask = df['Ad_Format'].str.lower().str.contains(fmt, na=False)
            mask |= df['YouTube_Ad_Formats'].str.lower().str.contains(fmt, na=False)
            df = df[mask]

        # Target Gender filter
        if target_gender:
            gender = str(target_gender).lower()
            if gender in ['female', 'f', 'w', 'women']:
                gender_code = 'f'
            elif gender in ['male', 'm', 'men']:
                gender_code = 'm'
            else:
                gender_code = gender

            mask = df['Target'].str.lower().str.contains(gender_code, na=False)
            mask |= df['Target'].str.lower().str.contains('all', na=False)
            df = df[mask]

        # Target Age filter
        if target_age:
            try:
                if '-' in str(target_age):
                    min_age, max_age = map(int, str(target_age).split('-'))
                else:
                    min_age = max_age = int(target_age)

                # Find overlapping age groups
                overlapping_groups = []
                if min_age <= 24:
                    overlapping_groups.append('18')
                if min_age <= 34 or max_age >= 25:
                    overlapping_groups.append('25')
                if min_age <= 44 or max_age >= 35:
                    overlapping_groups.append('35')
                if min_age <= 54 or max_age >= 45:
                    overlapping_groups.append('45')
                if max_age >= 55:
                    overlapping_groups.append('55')
                if max_age >= 65:
                    overlapping_groups.append('65')

                mask = pd.Series([False] * len(df), index=df.index)
                for age in overlapping_groups:
                    mask |= df['Target'].astype(str).str.contains(age, na=False)
                mask |= df['Target'].str.lower().str.contains('all', na=False)

                df = df[mask]
            except:
                pass  # Invalid age format

        # Period filter
        if period:
            df = df[df['Date_Range'].str.contains(str(period), case=False, na=False)]

        return df

    def display_center_table(self, df):
        """Display center table with campaign details."""
        print("\n" + "=" * 140)
        print("CAMPAIGN TABLE (CENTER)")
        print("=" * 140)

        if len(df) == 0:
            print("\n  No campaigns found matching the filters.\n")
            return

        # Sort by spend
        df_sorted = df.sort_values('Cost_parsed', ascending=False)

        # Display table
        print(f"\n{'#':<4} {'Mega Name':<70} {'Spend':<15} {'Impr.':<15} {'CPM':<10} {'Reach':<12}")
        print("-" * 140)

        for i, row in df_sorted.iterrows():
            rank = list(df_sorted.index).index(i) + 1
            mega_name = str(row['Standardized_Campaign_Name'])[:70]
            spend = row['Cost_parsed']
            impr = row['Impr_parsed']
            cpm = (spend / impr * 1000) if impr > 0 else 0
            reach = row['Peak_Reach'] if 'Peak_Reach' in row and pd.notna(row['Peak_Reach']) else 0

            safe_print(f"{rank:<4} {mega_name:<70} EUR {spend:>10,.2f} {impr:>13,} EUR {cpm:>6.2f} {reach:>10,}")

        print("-" * 140)

    def display_analytics_sidebar(self, campaign_ids):
        """Display analytics sidebar."""
        print("\n" + "=" * 140)
        print("ANALYTICS SIDEBAR (STRANA)")
        print("=" * 140)

        # Gender/Age Distribution
        print("\n1. GENDER & AGE DISTRIBUTION")
        print("-" * 80)

        df_filtered = self.df_age_gender[self.df_age_gender['Campaign ID'].isin(campaign_ids)]

        if len(df_filtered) > 0:
            distribution = df_filtered.groupby(['Age', 'Gender'])['Cost_parsed'].sum().reset_index()
            distribution = distribution.sort_values('Cost_parsed', ascending=False)
            total_spend = distribution['Cost_parsed'].sum()

            print(f"\n{'Age Group':<15} {'Gender':<10} {'Spend (EUR)':<15} {'%':<10} {'Bar':<30}")
            print("-" * 80)

            for i, row in distribution.head(15).iterrows():
                age = str(row['Age'])
                gender = str(row['Gender'])
                spend = row['Cost_parsed']
                pct = (spend / total_spend * 100) if total_spend > 0 else 0

                # Visual bar
                bar_length = int(pct / 2)  # Scale: 2% = 1 char
                bar = '#' * bar_length

                safe_print(f"{age:<15} {gender:<10} EUR {spend:>10,.2f} {pct:>6.2f}%  {bar}")

            print("-" * 80)
            safe_print(f"{'TOTAL':<26} EUR {total_spend:>10,.2f} 100.00%")
        else:
            print("\n  No demographics data available.\n")

        # Location Distribution
        print("\n\n2. TOP 5 LOCATIONS")
        print("-" * 80)

        df_filtered_loc = self.df_country[self.df_country['Campaign ID'].isin(campaign_ids)]

        if len(df_filtered_loc) > 0 and 'Country/Territory (User location)' in df_filtered_loc.columns:
            location_dist = df_filtered_loc.groupby('Country/Territory (User location)')['Cost_parsed'].sum().reset_index()
            location_dist.columns = ['Location', 'Spend']
            location_dist = location_dist.sort_values('Spend', ascending=False)
            total_spend = location_dist['Spend'].sum()

            print(f"\n{'Location':<50} {'Spend (EUR)':<15} {'%':<10} {'Bar':<20}")
            print("-" * 80)

            for i, row in location_dist.head(5).iterrows():
                location = str(row['Location'])[:50]
                spend = row['Spend']
                pct = (spend / total_spend * 100) if total_spend > 0 else 0

                # Visual bar
                bar_length = int(pct / 5)  # Scale: 5% = 1 char
                bar = '#' * bar_length

                safe_print(f"{location:<50} EUR {spend:>10,.2f} {pct:>6.2f}%  {bar}")
        else:
            print("\n  No location data available.\n")

    def display_final_summary(self, df):
        """Display final summary at the bottom."""
        print("\n" + "=" * 140)
        print("FINAL SUMMARY (DNO)")
        print("=" * 140)

        total_spend = df['Cost_parsed'].sum()
        total_impressions = df['Impr_parsed'].sum()
        weighted_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0

        print(f"""
+==================================================================================================================+
|                                            FILTER SUMMARY                                                      |
+==================================================================================================================+
|                                                                                                                |
|   Total Campaigns:              {len(df):>6,}                                                                       |
|                                                                                                                |
|   Total Spend:                  EUR {total_spend:>15,.2f}                                                            |
|   Total Impressions:            {total_impressions:>20,}                                                             |
|                                                                                                                |
|   WEIGHTED AVERAGE CPM:         EUR {weighted_cpm:>15,.2f}  <- KEY METRIC FOR ESTIMATION                            |
|                                                                                                                |
+==================================================================================================================+
""")

    def run_filter(self, brand=None, format_type=None, target_gender=None, target_age=None, period=None):
        """Run complete filter with structured display."""
        print("=" * 140)
        print("INTERACTIVE FILTER ENGINE - PRODUCTION VERSION")
        print("=" * 140)

        # Display applied filters
        print(f"\nAPPLIED FILTERS:")
        print(f"  Brand:         {brand if brand else 'All'}")
        print(f"  Format:        {format_type if format_type else 'All'}")
        print(f"  Target Gender: {target_gender if target_gender else 'All'}")
        print(f"  Target Age:    {target_age if target_age else 'All'}")
        print(f"  Period:        {period if period else 'All'}")

        # Apply filters
        df_filtered = self.filter_campaigns(brand, format_type, target_gender, target_age, period)

        print(f"\n  -> {len(df_filtered):,} campaigns matched")

        if len(df_filtered) == 0:
            print("\n  No campaigns found. Try adjusting your filters.\n")
            return df_filtered

        # Display center table
        self.display_center_table(df_filtered)

        # Display analytics sidebar
        campaign_ids = df_filtered['Campaign ID'].unique()
        self.display_analytics_sidebar(campaign_ids)

        # Display final summary
        self.display_final_summary(df_filtered)

        return df_filtered

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Paths
    PATH_PROTOTYPE = "ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"
    PATH_AGE_GENDER = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"
    PATH_COUNTRY = "data - v3/campaign - country - v3/campaign location - version 3.csv"

    print("=" * 140)
    print("INTERACTIVE FILTER ENGINE - INITIALIZING")
    print("=" * 140)
    print("\nLoading data...\n")

    # Load data
    df_campaigns = pd.read_csv(PATH_PROTOTYPE, delimiter=';', encoding='utf-8-sig')
    df_age_gender = pd.read_csv(PATH_AGE_GENDER, delimiter=';', encoding='utf-8-sig')
    df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')

    print(f"OK Campaigns:      {len(df_campaigns):,}")
    print(f"OK Age-Gender:     {len(df_age_gender):,} rows")
    print(f"OK Country:        {len(df_country):,} rows")

    # Initialize engine
    engine = InteractiveFilterEngine(df_campaigns, df_age_gender, df_country)

    # TEST CASE: Brand: Nivea | Format: Bumper | Target: Female 25-45
    print("\n\n")
    print("=" * 140)
    print("TEST CASE: Brand: Nivea | Format: Bumper | Target: Female 25-45")
    print("=" * 140)
    print()

    result = engine.run_filter(
        brand="Nivea",
        format_type="Bumper",
        target_gender="Female",
        target_age="25-45"
    )

    print("\n\nOK Filter engine execution completed!")
    print(f"OK Final result: {len(result):,} campaigns")
