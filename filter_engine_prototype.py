#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FUNKCIONALNI FILTER ENGINE - PROTOTYPE
Dinamicko filtriranje i analytics
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
# FILTER ENGINE CLASS
# ============================================================================

class FilterEngine:
    """Dynamic filtering engine for campaign data."""

    def __init__(self, df_campaigns, df_age_gender, df_country):
        self.df_campaigns = df_campaigns
        self.df_age_gender = df_age_gender
        self.df_country = df_country

        # Parse numeric columns
        self.df_campaigns['Cost_parsed'] = self.df_campaigns['Cost'].apply(parse_cost)
        self.df_campaigns['Impr_parsed'] = self.df_campaigns['Impr.'].apply(parse_impressions)

        self.df_age_gender['Cost_parsed'] = self.df_age_gender['Cost'].apply(parse_cost)
        self.df_country['Cost_parsed'] = self.df_country['Cost'].apply(parse_cost)

    def filter_by_format(self, df, format_keyword):
        """Filter by ad format."""
        if not format_keyword:
            return df

        keyword = str(format_keyword).lower()

        # Check in Ad_Format column
        mask = df['Ad_Format'].str.lower().str.contains(keyword, na=False)

        # Also check in YouTube_Ad_Formats
        mask |= df['YouTube_Ad_Formats'].str.lower().str.contains(keyword, na=False)

        return df[mask]

    def filter_by_gender(self, df, gender_keyword):
        """Filter by gender."""
        if not gender_keyword:
            return df

        gender = str(gender_keyword).lower()

        # Map keywords
        if gender in ['female', 'f', 'w', 'women']:
            gender_code = 'f'
        elif gender in ['male', 'm', 'men']:
            gender_code = 'm'
        else:
            return df  # No filter

        # Check in Target column (e.g., "18-65+ | F" or "18-65+ | M/F")
        mask = df['Target'].str.lower().str.contains(gender_code, na=False)

        # Also include "All" gender campaigns
        mask |= df['Target'].str.lower().str.contains('all', na=False)

        return df[mask]

    def filter_by_age(self, df, age_range_str):
        """Filter by age range."""
        if not age_range_str:
            return df

        # Parse age range (e.g., "25-45")
        try:
            if '-' in str(age_range_str):
                min_age, max_age = map(int, str(age_range_str).split('-'))
            else:
                min_age = max_age = int(age_range_str)
        except:
            return df  # Invalid age range

        # Age groups that overlap with requested range
        # 18-24, 25-34, 35-44, 45-54, 55-64, 65+
        overlapping_groups = []

        if min_age <= 24:
            overlapping_groups.append('18')
        if min_age <= 34 or (max_age >= 25 and max_age <= 34):
            overlapping_groups.append('25')
        if min_age <= 44 or (max_age >= 35 and max_age <= 44):
            overlapping_groups.append('35')
        if min_age <= 54 or (max_age >= 45 and max_age <= 54):
            overlapping_groups.append('45')
        if min_age <= 64 or max_age >= 55:
            overlapping_groups.append('55')
        if max_age >= 65:
            overlapping_groups.append('65')

        # Filter campaigns that have these age groups in Target
        if len(overlapping_groups) == 0:
            return df

        # Create regex pattern
        mask = pd.Series([False] * len(df), index=df.index)
        for age in overlapping_groups:
            mask |= df['Target'].astype(str).str.contains(age, na=False)

        # Also include "All" age campaigns
        mask |= df['Target'].str.lower().str.contains('all', na=False)

        return df[mask]

    def apply_filters(self, format_keyword=None, gender_keyword=None, age_range=None):
        """Apply all filters and return filtered dataframe."""
        df = self.df_campaigns.copy()

        if format_keyword:
            df = self.filter_by_format(df, format_keyword)

        if gender_keyword:
            df = self.filter_by_gender(df, gender_keyword)

        if age_range:
            df = self.filter_by_age(df, age_range)

        return df

    def calculate_weighted_avg_cpm(self, df):
        """Calculate weighted average CPM."""
        total_cost = df['Cost_parsed'].sum()
        total_impressions = df['Impr_parsed'].sum()

        if total_impressions > 0:
            weighted_avg_cpm = (total_cost / total_impressions) * 1000
        else:
            weighted_avg_cpm = 0

        return weighted_avg_cpm

    def get_gender_age_distribution(self, campaign_ids):
        """Get gender/age distribution for filtered campaigns."""
        # Filter age-gender data
        df_filtered = self.df_age_gender[self.df_age_gender['Campaign ID'].isin(campaign_ids)]

        if len(df_filtered) == 0:
            return pd.DataFrame()

        # Group by Age and Gender
        distribution = df_filtered.groupby(['Age', 'Gender'])['Cost_parsed'].sum().reset_index()
        distribution = distribution.sort_values('Cost_parsed', ascending=False)

        return distribution

    def get_location_distribution(self, campaign_ids):
        """Get location distribution for filtered campaigns."""
        # Filter country data
        df_filtered = self.df_country[self.df_country['Campaign ID'].isin(campaign_ids)]

        if len(df_filtered) == 0:
            return pd.DataFrame()

        # Group by location
        if 'Country/Territory (User location)' in df_filtered.columns:
            location_col = 'Country/Territory (User location)'
        else:
            return pd.DataFrame()

        distribution = df_filtered.groupby(location_col)['Cost_parsed'].sum().reset_index()
        distribution.columns = ['Location', 'Spend']
        distribution = distribution.sort_values('Spend', ascending=False)

        return distribution

    def generate_report(self, format_keyword=None, gender_keyword=None, age_range=None):
        """Generate complete filter report."""
        print("=" * 120)
        print("FILTER ENGINE - REPORT")
        print("=" * 120)

        # Display filters
        print(f"\nAPPLIED FILTERS:")
        print(f"  Format:  {format_keyword if format_keyword else 'None'}")
        print(f"  Gender:  {gender_keyword if gender_keyword else 'None'}")
        print(f"  Age:     {age_range if age_range else 'None'}")

        # Apply filters
        df_filtered = self.apply_filters(format_keyword, gender_keyword, age_range)

        print(f"\n\nFILTER RESULTS:")
        print(f"  Campaigns found: {len(df_filtered):,}")
        print(f"  Total Spend:     EUR {df_filtered['Cost_parsed'].sum():,.2f}")
        print(f"  Total Impressions: {df_filtered['Impr_parsed'].sum():,}")

        # Weighted Average CPM
        weighted_cpm = self.calculate_weighted_avg_cpm(df_filtered)
        print(f"\n  WEIGHTED AVERAGE CPM: EUR {weighted_cpm:.2f}")

        # Campaign list
        print("\n" + "=" * 120)
        print("CAMPAIGN LIST (Top 20 by Spend)")
        print("=" * 120)

        if len(df_filtered) > 0:
            df_sorted = df_filtered.sort_values('Cost_parsed', ascending=False).head(20)

            print(f"\n{'#':<3} {'Brand':<20} {'Spend':<15} {'Impr.':<12} {'CPM':<10} Standardized Name")
            print("-" * 120)

            for i, row in df_sorted.iterrows():
                rank = list(df_sorted.index).index(i) + 1
                brand = str(row['Brand'])[:20]
                spend = row['Cost_parsed']
                impr = row['Impr_parsed']
                cpm = (spend / impr * 1000) if impr > 0 else 0
                std_name = str(row['Standardized_Campaign_Name'])[:70]

                safe_print(f"{rank:<3} {brand:<20} EUR {spend:>10,.2f} {impr:>12,} EUR {cpm:>6.2f} {std_name}")

        # Side-Panel Analytics
        print("\n" + "=" * 120)
        print("SIDE-PANEL ANALYTICS")
        print("=" * 120)

        campaign_ids = df_filtered['Campaign ID'].unique()

        # Gender/Age Distribution
        print("\n\n1. GENDER/AGE DISTRIBUTION")
        print("-" * 120)

        gender_age_dist = self.get_gender_age_distribution(campaign_ids)

        if len(gender_age_dist) > 0:
            total_spend = gender_age_dist['Cost_parsed'].sum()

            print(f"\n{'Age Group':<15} {'Gender':<10} {'Spend (EUR)':<15} {'%':<10}")
            print("-" * 60)

            for i, row in gender_age_dist.iterrows():
                age = str(row['Age'])
                gender = str(row['Gender'])
                spend = row['Cost_parsed']
                pct = (spend / total_spend * 100) if total_spend > 0 else 0

                safe_print(f"{age:<15} {gender:<10} EUR {spend:>10,.2f} {pct:>6.2f}%")

            print("-" * 60)
            safe_print(f"{'TOTAL':<15} {'':<10} EUR {total_spend:>10,.2f} 100.00%")
        else:
            print("\n  No demographics data available for these campaigns.")

        # Location Distribution
        print("\n\n2. LOCATION DISTRIBUTION (Top 5)")
        print("-" * 120)

        location_dist = self.get_location_distribution(campaign_ids)

        if len(location_dist) > 0:
            total_spend = location_dist['Spend'].sum()

            print(f"\n{'Location':<50} {'Spend (EUR)':<15} {'%':<10}")
            print("-" * 80)

            for i, row in location_dist.head(5).iterrows():
                location = str(row['Location'])[:50]
                spend = row['Spend']
                pct = (spend / total_spend * 100) if total_spend > 0 else 0

                safe_print(f"{location:<50} EUR {spend:>10,.2f} {pct:>6.2f}%")
        else:
            print("\n  No location data available for these campaigns.")

        print("\n" + "=" * 120)
        print("FILTER REPORT COMPLETED")
        print("=" * 120)

        return df_filtered

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Paths
    PATH_PROTOTYPE = "ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"
    PATH_AGE_GENDER = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"
    PATH_COUNTRY = "data - v3/campaign - country - v3/campaign location - version 3.csv"

    print("=" * 120)
    print("FUNKCIONALNI FILTER ENGINE - PROTOTYPE")
    print("=" * 120)
    print("\nLoading data...\n")

    # Load data
    df_campaigns = pd.read_csv(PATH_PROTOTYPE, delimiter=';', encoding='utf-8-sig')
    df_age_gender = pd.read_csv(PATH_AGE_GENDER, delimiter=';', encoding='utf-8-sig')
    df_country = pd.read_csv(PATH_COUNTRY, delimiter=';', encoding='utf-8-sig')

    print(f"Campaigns loaded:   {len(df_campaigns):,}")
    print(f"Age-Gender data:    {len(df_age_gender):,} rows")
    print(f"Country data:       {len(df_country):,} rows")

    # Initialize filter engine
    engine = FilterEngine(df_campaigns, df_age_gender, df_country)

    # TEST CASE: Format: Bumper | Gender: Female | Age: 25-45
    print("\n\n")
    print("=" * 120)
    print("TEST CASE: Format: Bumper | Gender: Female | Age: 25-45")
    print("=" * 120)

    df_result = engine.generate_report(
        format_keyword="Bumper",
        gender_keyword="Female",
        age_range="25-45"
    )

    print(f"\n\nFinal result: {len(df_result):,} campaigns matched")
    print(f"Total Spend: EUR {df_result['Cost_parsed'].sum():,.2f}")
