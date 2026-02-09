#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADS ESTIMATION HUB - HR PROTOTYPE V4
Interactive dashboard for Croatian Google Ads campaign analysis
COMPLETE VERSION with Brand Fix, Metric Selector & Drill-down Context
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Estimator Terminator V4 - HR",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def parse_number(value):
    """Parse numeric values."""
    if pd.isna(value):
        return 0
    value_str = str(value).strip().replace(',', '').strip()
    try:
        return int(float(value_str))
    except:
        return 0

def parse_float(value):
    """Parse float values."""
    if pd.isna(value):
        return 0.0
    value_str = str(value).strip().replace(',', '').replace('%', '').strip()
    try:
        return float(value_str)
    except:
        return 0.0

@st.cache_data
def load_campaign_data(file_path):
    """Load and parse the campaign data."""
    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')

    # Parse numeric columns
    df['Cost_parsed'] = df['Cost'].apply(parse_cost)
    df['Impr_parsed'] = df['Impr.'].apply(parse_number)
    df['Reach_parsed'] = df['Peak_Reach'].apply(parse_number)

    # Parse additional metrics if they exist
    if 'Clicks' in df.columns:
        df['Clicks_parsed'] = df['Clicks'].apply(parse_number)
    else:
        df['Clicks_parsed'] = 0

    if 'CTR' in df.columns:
        df['CTR_parsed'] = df['CTR'].apply(parse_float)
    else:
        df['CTR_parsed'] = 0.0

    if 'Avg. CPC' in df.columns:
        df['Avg_CPC_parsed'] = df['Avg. CPC'].apply(parse_cost)
    else:
        df['Avg_CPC_parsed'] = 0.0

    if 'Avg. CPM' in df.columns:
        df['Avg_CPM_parsed'] = df['Avg. CPM'].apply(parse_cost)
    else:
        df['Avg_CPM_parsed'] = 0.0

    if 'TrueView views' in df.columns:
        df['TrueView_views_parsed'] = df['TrueView views'].apply(parse_number)
    else:
        df['TrueView_views_parsed'] = 0

    if 'TrueView avg. CPV' in df.columns:
        df['TrueView_CPV_parsed'] = df['TrueView avg. CPV'].apply(parse_cost)
    else:
        df['TrueView_CPV_parsed'] = 0.0

    if 'Conversions' in df.columns:
        df['Conversions_parsed'] = df['Conversions'].apply(parse_float)
    else:
        df['Conversions_parsed'] = 0.0

    if 'Conv. rate' in df.columns:
        df['Conv_rate_parsed'] = df['Conv. rate'].apply(parse_float)
    else:
        df['Conv_rate_parsed'] = 0.0

    if 'Cost / conv.' in df.columns:
        df['Cost_per_conv_parsed'] = df['Cost / conv.'].apply(parse_cost)
    else:
        df['Cost_per_conv_parsed'] = 0.0

    # Calculate CPM
    df['CPM'] = np.where(df['Impr_parsed'] > 0, (df['Cost_parsed'] / df['Impr_parsed']) * 1000, 0)

    # Extract Quarter from Date_Range
    def extract_quarter(date_range):
        if pd.isna(date_range):
            return 'Unknown'
        date_str = str(date_range).lower()

        if any(month in date_str for month in ['jan', 'feb', 'mar']):
            if '25' in date_str:
                return 'Q1 2025'
        if any(month in date_str for month in ['apr', 'may', 'jun']):
            if '25' in date_str:
                return 'Q2 2025'
        if any(month in date_str for month in ['jul', 'aug', 'sep']):
            if '25' in date_str:
                return 'Q3 2025'
        if any(month in date_str for month in ['oct', 'nov', 'dec']):
            if '25' in date_str:
                return 'Q4 2025'

        return 'Unknown'

    df['Quarter'] = df['Date_Range'].apply(extract_quarter)

    return df

@st.cache_data
def load_demographics_data(file_path):
    """Load demographics (age-gender) data."""
    try:
        df = pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')
        df['Cost_parsed'] = df['Cost'].apply(parse_cost)
        return df
    except:
        return pd.DataFrame()

def get_dominant_demographics(campaign_id, df_demographics):
    """
    Get dominant demographics for a campaign based on actual spend data.
    Returns format: "Age | Gender" or "Multi-Age | Gender"
    """
    if df_demographics is None or len(df_demographics) == 0:
        return ("Unknown", "Unknown")

    # Filter for this campaign
    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    if len(demo_data) == 0:
        return ("Unknown", "Unknown")

    # Group by Age and Gender, sum spend
    demo_grouped = demo_data.groupby(['Age', 'Gender'])['Cost_parsed'].sum()

    if len(demo_grouped) == 0:
        return ("Unknown", "Unknown")

    # Find dominant segment (highest spend)
    dominant_segment = demo_grouped.idxmax()
    dominant_age, dominant_gender = dominant_segment
    dominant_spend = demo_grouped.max()
    total_spend = demo_grouped.sum()

    # Check if this is multi-segment (no single segment has >50% of spend)
    if dominant_spend / total_spend < 0.5:
        # Multi-segment campaign
        ages = sorted(demo_grouped.index.get_level_values(0).unique())
        genders = demo_grouped.index.get_level_values(1).unique()

        # Determine age representation
        if len(ages) > 3:
            age_part = "Multi-Age"
        elif len(ages) > 1:
            age_part = f"{ages[0]}-{ages[-1]}"
        else:
            age_part = ages[0]

        # Determine gender representation
        if len(genders) > 1:
            gender_part = "All"
        else:
            gender_part = genders[0]

        return (age_part, gender_part)
    else:
        # Single dominant segment
        # Map gender codes
        gender_map = {
            'F': 'Female',
            'M': 'Male',
            'Female': 'Female',
            'Male': 'Male',
            'Unknown': 'Unknown'
        }

        gender_label = gender_map.get(str(dominant_gender).strip(), dominant_gender)

        return (str(dominant_age), gender_label)

def calculate_weighted_cpm(df):
    """Calculate weighted average CPM."""
    total_cost = df['Cost_parsed'].sum()
    total_impressions = df['Impr_parsed'].sum()

    if total_impressions > 0:
        return (total_cost / total_impressions) * 1000
    else:
        return 0.0

def fix_croatia_brand(df):
    """Fix campaigns where Brand is incorrectly set to 'Croatia'."""
    # Try different column names for Account
    account_col = None
    if 'Account' in df.columns:
        account_col = 'Account'
    elif 'Account name' in df.columns:
        account_col = 'Account name'

    mask_croatia = df['Brand'] == 'Croatia'

    if mask_croatia.any() and account_col:
        st.sidebar.warning(f"🔧 Fixing {mask_croatia.sum()} campaigns with Brand='Croatia'...")

        for idx in df[mask_croatia].index:
            account = df.loc[idx, account_col]

            if pd.notna(account):
                account_str = str(account).lower()

                # Check for specific brands
                if 'bison' in account_str:
                    df.loc[idx, 'Brand'] = 'Bison'
                elif 'ceresit' in account_str:
                    df.loc[idx, 'Brand'] = 'Ceresit'
                else:
                    # Extract from account name (first word before underscore)
                    brand_extracted = str(account).split('_')[0].split()[0][:30]
                    df.loc[idx, 'Brand'] = brand_extracted if brand_extracted else 'Unknown'

        st.sidebar.success("✅ Brand 'Croatia' errors fixed!")

    return df

def rebuild_campaign_name(row):
    """Rebuild standardized name with correct demographics and brand."""
    parts = []

    if pd.notna(row.get('Brand')):
        parts.append(str(row['Brand']))

    if pd.notna(row.get('Ad_Format')):
        parts.append(str(row['Ad_Format']))

    # Use corrected demographics
    if 'Target_Corrected' in row:
        parts.append(row['Target_Corrected'])
    elif pd.notna(row.get('Target')):
        parts.append(str(row['Target']))

    if pd.notna(row.get('Date_Range')):
        parts.append(str(row['Date_Range']))

    if pd.notna(row.get('Bid_Strategy_Short')):
        parts.append(str(row['Bid_Strategy_Short']))

    if pd.notna(row.get('Goal')):
        parts.append(str(row['Goal']))

    return " | ".join(parts)

# ============================================================================
# LOAD DATA
# ============================================================================

CAMPAIGN_PATH = "ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"
DEMOGRAPHICS_PATH = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"

try:
    df_campaigns = load_campaign_data(CAMPAIGN_PATH)
    df_demographics = load_demographics_data(DEMOGRAPHICS_PATH)

    # CRITICAL FIX 1: Fix 'Croatia' brand errors
    df_campaigns = fix_croatia_brand(df_campaigns)

    # CRITICAL FIX 2: Calculate actual demographics for each campaign
    st.sidebar.info("🔄 Calculating actual demographics from data...")

    # Apply demographics correction
    demographics_results = df_campaigns['Campaign ID'].apply(
        lambda cid: get_dominant_demographics(cid, df_demographics)
    )

    df_campaigns['Age_Range'] = demographics_results.apply(lambda x: x[0])
    df_campaigns['Gender'] = demographics_results.apply(lambda x: x[1])

    # Update Target column with corrected demographics
    df_campaigns['Target_Corrected'] = df_campaigns['Age_Range'] + " | " + df_campaigns['Gender']

    # Rebuild Standardized_Campaign_Name with corrected demographics AND fixed brands
    df_campaigns['Standardized_Campaign_Name_Corrected'] = df_campaigns.apply(rebuild_campaign_name, axis=1)

    data_loaded = True
    st.sidebar.success("✅ Data loaded & corrected!")

except Exception as e:
    st.error(f"❌ Greška pri učitavanju podataka: {e}")
    data_loaded = False

# ============================================================================
# APP LAYOUT
# ============================================================================

if data_loaded:

    # HEADER
    st.title("🤖 Estimator Terminator V4 - HR")
    st.markdown("### neka nam je dragi Bog na pomoći")
    st.markdown("---")

    # ========================================================================
    # LEFT SIDEBAR - FILTERS
    # ========================================================================

    st.sidebar.header("🔍 Filteri")
    st.sidebar.markdown("Odaberite parametre za filtriranje kampanja:")

    # Brand filter
    brands = ['Svi'] + sorted(df_campaigns['Brand'].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect(
        "Brand:",
        options=brands,
        default=['Svi']
    )

    # Ad Format filter
    ad_formats = ['Svi'] + sorted(df_campaigns['Ad_Format'].dropna().unique().tolist())
    selected_formats = st.sidebar.multiselect(
        "Ad Format:",
        options=ad_formats,
        default=['Svi']
    )

    # Age Range filter (using corrected demographics)
    age_ranges = ['Svi'] + sorted([x for x in df_campaigns['Age_Range'].dropna().unique().tolist() if x != 'Unknown'])
    selected_ages = st.sidebar.multiselect(
        "Age Group:",
        options=age_ranges,
        default=['Svi']
    )

    # Gender filter (using corrected demographics)
    genders = ['Svi'] + sorted([x for x in df_campaigns['Gender'].dropna().unique().tolist() if x != 'Unknown'])
    selected_genders = st.sidebar.multiselect(
        "Gender:",
        options=genders,
        default=['Svi']
    )

    # Bid Strategy filter
    bid_strategies = ['Svi'] + sorted(df_campaigns['Bid_Strategy_Short'].dropna().unique().tolist())
    selected_bid_strategies = st.sidebar.multiselect(
        "Bid Strategy:",
        options=bid_strategies,
        default=['Svi']
    )

    # Quarter filter
    quarters = ['Svi'] + sorted(df_campaigns['Quarter'].dropna().unique().tolist())
    selected_quarters = st.sidebar.multiselect(
        "Quarter:",
        options=quarters,
        default=['Svi']
    )

    st.sidebar.markdown("---")

    # ========================================================================
    # DYNAMIC METRICS SELECTION
    # ========================================================================

    st.sidebar.header("📊 Odaberi Metrike za Prikaz")
    st.sidebar.markdown("**Odaberi koje kolone želiš vidjeti:**")

    # Always visible base metrics
    base_metrics = ['Cost (EUR)', 'Impressions', 'CPM (EUR)']

    # Additional optional metrics
    optional_metrics = [
        'Peak Reach',
        'Clicks',
        'CTR (%)',
        'Avg. CPC (EUR)',
        'TrueView Views',
        'TrueView CPV (EUR)',
        'Conversions',
        'Conv. Rate (%)',
        'Cost/Conv. (EUR)'
    ]

    # Metrics mapping to dataframe columns
    metrics_mapping = {
        'Cost (EUR)': 'Cost_parsed',
        'Impressions': 'Impr_parsed',
        'CPM (EUR)': 'CPM',
        'Peak Reach': 'Reach_parsed',
        'Clicks': 'Clicks_parsed',
        'CTR (%)': 'CTR_parsed',
        'Avg. CPC (EUR)': 'Avg_CPC_parsed',
        'TrueView Views': 'TrueView_views_parsed',
        'TrueView CPV (EUR)': 'TrueView_CPV_parsed',
        'Conversions': 'Conversions_parsed',
        'Conv. Rate (%)': 'Conv_rate_parsed',
        'Cost/Conv. (EUR)': 'Cost_per_conv_parsed'
    }

    # Create multiselect for optional metrics
    selected_optional_metrics = st.sidebar.multiselect(
        "Dodatne Metrike:",
        options=optional_metrics,
        default=['Peak Reach'],
        help="Odaberi dodatne metrike koje želiš vidjeti u tablici"
    )

    # Combine base and selected optional metrics
    all_selected_metrics = base_metrics + selected_optional_metrics

    # Show count
    st.sidebar.caption(f"✅ Prikazujem: {len(all_selected_metrics)} metrika")

    # Quick preset buttons
    st.sidebar.markdown("**Brzi odabir:**")
    col_preset1, col_preset2 = st.sidebar.columns(2)

    with col_preset1:
        if st.button("🎯 Minimum", use_container_width=True, help="Cost, Impressions, CPM"):
            st.rerun()

    with col_preset2:
        if st.button("📈 Sve", use_container_width=True, help="Sve dostupne metrike"):
            st.sidebar.info("💡 Odaberi sve metrike ručno iz liste iznad")

    st.sidebar.markdown("---")

    # ========================================================================
    # APPLY FILTERS
    # ========================================================================

    df_filtered = df_campaigns.copy()

    # Apply Brand filter
    if 'Svi' not in selected_brands and len(selected_brands) > 0:
        df_filtered = df_filtered[df_filtered['Brand'].isin(selected_brands)]

    # Apply Ad Format filter
    if 'Svi' not in selected_formats and len(selected_formats) > 0:
        df_filtered = df_filtered[df_filtered['Ad_Format'].isin(selected_formats)]

    # Apply Age Range filter
    if 'Svi' not in selected_ages and len(selected_ages) > 0:
        df_filtered = df_filtered[df_filtered['Age_Range'].isin(selected_ages)]

    # Apply Gender filter
    if 'Svi' not in selected_genders and len(selected_genders) > 0:
        df_filtered = df_filtered[df_filtered['Gender'].isin(selected_genders)]

    # Apply Bid Strategy filter
    if 'Svi' not in selected_bid_strategies and len(selected_bid_strategies) > 0:
        df_filtered = df_filtered[df_filtered['Bid_Strategy_Short'].isin(selected_bid_strategies)]

    # Apply Quarter filter
    if 'Svi' not in selected_quarters and len(selected_quarters) > 0:
        df_filtered = df_filtered[df_filtered['Quarter'].isin(selected_quarters)]

    # ========================================================================
    # MAIN CONTENT - CENTER
    # ========================================================================

    # Show filter results
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### 📋 Filtrirane Kampanje")
        st.markdown(f"**{len(df_filtered):,}** kampanja od ukupno **{len(df_campaigns):,}**")

    with col2:
        st.markdown(f"### 🎯 Coverage")
        coverage_pct = (len(df_filtered) / len(df_campaigns) * 100) if len(df_campaigns) > 0 else 0
        st.markdown(f"**{coverage_pct:.1f}%** ukupnih kampanja")

    with col3:
        st.markdown(f"### 🇭🇷 Market")
        st.markdown("**Croatia** 🟢")

    st.markdown("---")

    # Display filtered campaigns table
    if len(df_filtered) > 0:

        # Show selected metrics as visual tags
        st.markdown("### 📊 Odabrane Metrike u Tablici:")
        metric_tags = " · ".join([f"**{m}**" for m in all_selected_metrics])
        st.markdown(f"{metric_tags}")
        st.caption(f"💡 Prikazujem {len(all_selected_metrics)} metrika. Promijeni odabir u sidebaru → 📊 Odaberi Metrike za Prikaz")

        st.markdown("---")

        # ====================================================================
        # DRILL-DOWN CONTEXT SELECTOR
        # ====================================================================

        st.markdown("### 🔍 Drill-down Context View")

        # Create selectbox for campaign selection
        df_filtered_sorted = df_filtered.sort_values('Cost_parsed', ascending=False)

        # Create campaign options list (using index for mapping)
        campaign_options = ['-- Odaberi kampanju za detalje --'] + df_filtered_sorted['Standardized_Campaign_Name_Corrected'].tolist()

        selected_campaign_name = st.selectbox(
            "Odaberi kampanju za prikaz originalnog naziva i dodatnih detalja:",
            options=campaign_options,
            index=0,
            help="Odaberi kampanju da vidiš originalni naziv i druge detalje"
        )

        # Show campaign details if selected
        if selected_campaign_name != '-- Odaberi kampanju za detalje --':
            # Find the campaign in dataframe
            campaign_row = df_filtered[df_filtered['Standardized_Campaign_Name_Corrected'] == selected_campaign_name].iloc[0]

            # Get account column name
            account_col = 'Account' if 'Account' in df_filtered.columns else 'Account name' if 'Account name' in df_filtered.columns else None

            # Display context card
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h3 style="margin: 0 0 15px 0; color: white;">📋 Campaign Details</h3>
            </div>
            """, unsafe_allow_html=True)

            # Display details in columns
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.markdown("#### 📝 Originalni Naziv Kampanje:")
                st.info(f"**{campaign_row['Campaign']}**")

                st.markdown("#### 🏢 Account:")
                if account_col and pd.notna(campaign_row.get(account_col)):
                    st.info(f"**{campaign_row[account_col]}**")
                else:
                    st.info("N/A")

                st.markdown("#### 🆔 Campaign ID:")
                st.info(f"**{campaign_row['Campaign ID']}**")

            with detail_col2:
                st.markdown("#### 🏷️ Brand:")
                st.info(f"**{campaign_row['Brand']}**")

                st.markdown("#### 📺 Format:")
                st.info(f"**{campaign_row['Ad_Format']}**")

                st.markdown("#### 🎯 Target:")
                st.info(f"**{campaign_row['Target_Corrected']}**")

            # Additional metrics
            st.markdown("#### 💰 Key Metrics:")

            metric_detail_cols = st.columns(4)

            with metric_detail_cols[0]:
                st.metric(
                    "Cost",
                    f"€{campaign_row['Cost_parsed']:,.2f}",
                    help="Total campaign cost"
                )

            with metric_detail_cols[1]:
                st.metric(
                    "Impressions",
                    f"{campaign_row['Impr_parsed']:,}",
                    help="Total impressions"
                )

            with metric_detail_cols[2]:
                st.metric(
                    "CPM",
                    f"€{campaign_row['CPM']:.2f}",
                    help="Cost per 1000 impressions"
                )

            with metric_detail_cols[3]:
                st.metric(
                    "Peak Reach",
                    f"{campaign_row['Reach_parsed']:,}",
                    help="Maximum reach achieved"
                )

            st.markdown("---")

        # ====================================================================
        # CAMPAIGN TABLE
        # ====================================================================

        st.markdown("### 📊 Campaign Table")

        # Prepare display dataframe with dynamic columns
        display_columns = ['Standardized_Campaign_Name_Corrected']
        display_column_names = ['Campaign Name']

        # Add selected metrics
        for metric_name in all_selected_metrics:
            if metric_name in metrics_mapping:
                column_key = metrics_mapping[metric_name]
                # Check if column exists in dataframe
                if column_key in df_filtered.columns:
                    display_columns.append(column_key)
                    display_column_names.append(metric_name)

        # Create display dataframe
        df_display = df_filtered[display_columns].copy()
        df_display.columns = display_column_names

        # Sort by Cost
        if 'Cost (EUR)' in display_column_names:
            df_display = df_display.sort_values('Cost (EUR)', ascending=False)

        # Format numbers for display
        for col in display_column_names[1:]:  # Skip campaign name
            if 'EUR' in col or 'CPM' in col or 'CPC' in col or 'CPV' in col or 'Cost' in col:
                df_display[col] = df_display[col].apply(lambda x: f"€{x:,.2f}" if pd.notna(x) else "€0.00")
            elif '%' in col or 'Rate' in col or 'CTR' in col:
                df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%")
            elif 'Impressions' in col or 'Reach' in col or 'Clicks' in col or 'Views' in col:
                df_display[col] = df_display[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x > 0 else "0")
            elif 'Conversions' in col:
                df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "0.00")

        # Display table
        st.dataframe(
            df_display,
            use_container_width=True,
            height=500,
            hide_index=True
        )

        # ====================================================================
        # RIGHT SIDEBAR - INSIGHTS
        # ====================================================================

        st.markdown("---")
        st.markdown("## 📊 Insights & Analytics")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            # Age Group Distribution (using corrected demographics)
            st.markdown("### 👥 Distribucija po Dobnim Skupinama (Stvarni Podaci)")

            age_distribution = df_filtered.groupby('Age_Range')['Cost_parsed'].sum().sort_values(ascending=False)

            if len(age_distribution) > 0:
                df_age = pd.DataFrame({
                    'Age Group': age_distribution.index,
                    'Cost': age_distribution.values
                })

                total_cost = df_age['Cost'].sum()
                df_age['Percentage'] = (df_age['Cost'] / total_cost * 100).round(2)

                # Create bar chart
                fig_age = px.bar(
                    df_age,
                    x='Age Group',
                    y='Percentage',
                    title='',
                    labels={'Percentage': '% Troška', 'Age Group': 'Dobna Skupina'},
                    text='Percentage',
                    color='Percentage',
                    color_continuous_scale='Blues'
                )

                fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_age.update_layout(showlegend=False, height=400)

                st.plotly_chart(fig_age, use_container_width=True)

                # Show table
                df_age_display = df_age.copy()
                df_age_display['Cost'] = df_age_display['Cost'].apply(lambda x: f"€{x:,.2f}")
                df_age_display['Percentage'] = df_age_display['Percentage'].apply(lambda x: f"{x:.2f}%")

                st.dataframe(df_age_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nema podataka o dobnim skupinama za odabrane filtre.")

        with col_right:
            # Location Badge
            st.markdown("### 📍 Lokacija")
            st.markdown("""
            <div style="
                background-color: #d4edda;
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin-top: 20px;
            ">
                <h2 style="color: #155724; margin: 0;">🇭🇷</h2>
                <h3 style="color: #155724; margin: 10px 0;">CROATIA</h3>
                <p style="color: #155724; margin: 0;">100% Croatian Market</p>
            </div>
            """, unsafe_allow_html=True)

            # Gender distribution
            st.markdown("### 👤 Distribucija po Spolu")

            gender_distribution = df_filtered.groupby('Gender')['Cost_parsed'].sum().sort_values(ascending=False)

            if len(gender_distribution) > 0:
                for gender, cost in gender_distribution.items():
                    pct = (cost / gender_distribution.sum() * 100)
                    st.markdown(f"**{gender}:** €{cost:,.2f} ({pct:.1f}%)")

            # Additional stats
            st.markdown("### 📈 Statistika")

            total_brands = df_filtered['Brand'].nunique()
            total_formats = df_filtered['Ad_Format'].nunique()

            st.metric("Brandova", f"{total_brands}")
            st.metric("Formata", f"{total_formats}")

        # ====================================================================
        # FOOTER - BIG METRICS
        # ====================================================================

        st.markdown("---")
        st.markdown("## 💰 Ključne Metrike")

        # Calculate metrics
        total_cost = df_filtered['Cost_parsed'].sum()
        total_impressions = df_filtered['Impr_parsed'].sum()
        weighted_cpm = calculate_weighted_cpm(df_filtered)

        # Display in big metric cards
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0; font-size: 16px; opacity: 0.9;">UKUPNI TROŠAK</h4>
                <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">€{total_cost:,.2f}</h1>
                <p style="margin: 0; font-size: 14px; opacity: 0.8;">{len(df_filtered)} kampanja</p>
            </div>
            """, unsafe_allow_html=True)

        with metric_col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0; font-size: 16px; opacity: 0.9;">UKUPNE IMPRESIJE</h4>
                <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">{total_impressions:,}</h1>
                <p style="margin: 0; font-size: 14px; opacity: 0.8;">Peak Reach: {df_filtered['Reach_parsed'].max():,}</p>
            </div>
            """, unsafe_allow_html=True)

        with metric_col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0; font-size: 16px; opacity: 0.9;">WEIGHTED AVERAGE CPM</h4>
                <h1 style="margin: 10px 0; font-size: 36px; font-weight: bold;">€{weighted_cpm:.2f}</h1>
                <p style="margin: 0; font-size: 14px; opacity: 0.8;">⭐ Benchmark metrika</p>
            </div>
            """, unsafe_allow_html=True)

        # Budget Transparency Note
        st.markdown("""
        <div style="
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        ">
            <p style="margin: 0; color: #856404; font-size: 14px;">
                <strong>ℹ️ Napomena o podacima:</strong> Prikazani podaci temelje se na <strong>HR-only trošku</strong>
                (očišćeno od worldwide grešaka i regionalnog spenda). Svi iznosi odražavaju isključivo hrvatski market.
                <strong>Demographics su kalkulirani iz stvarnih age-gender podataka</strong> (dominantni segment po spend-u).
                <strong>Brand 'Croatia' greške su automatski ispravljene</strong> (Bison, Ceresit).
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ====================================================================
        # ADDITIONAL VISUALIZATIONS
        # ====================================================================

        st.markdown("## 📈 Dodatne Vizualizacije")

        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            # Top 10 Brands by Spend
            st.markdown("### 🏆 Top 10 Brandova po Trošku")

            brand_spend = df_filtered.groupby('Brand')['Cost_parsed'].sum().sort_values(ascending=False).head(10)

            fig_brands = go.Figure(go.Bar(
                x=brand_spend.values,
                y=brand_spend.index,
                orientation='h',
                marker=dict(
                    color=brand_spend.values,
                    colorscale='Viridis'
                ),
                text=[f"€{x:,.0f}" for x in brand_spend.values],
                textposition='auto'
            ))

            fig_brands.update_layout(
                xaxis_title="Trošak (EUR)",
                yaxis_title="Brand",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig_brands, use_container_width=True)

        with viz_col2:
            # CPM Distribution
            st.markdown("### 📊 Distribucija CPM-a")

            fig_cpm = px.histogram(
                df_filtered,
                x='CPM',
                nbins=30,
                title='',
                labels={'CPM': 'CPM (EUR)', 'count': 'Broj kampanja'},
                color_discrete_sequence=['#636EFA']
            )

            fig_cpm.add_vline(
                x=weighted_cpm,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Weighted Avg: €{weighted_cpm:.2f}",
                annotation_position="top right"
            )

            fig_cpm.update_layout(height=400)

            st.plotly_chart(fig_cpm, use_container_width=True)

        # ====================================================================
        # QUARTER BREAKDOWN
        # ====================================================================

        st.markdown("### 📅 Distribucija po Kvartalima")

        quarter_data = df_filtered.groupby('Quarter').agg({
            'Cost_parsed': 'sum',
            'Impr_parsed': 'sum',
            'Campaign ID': 'count'
        }).reset_index()

        quarter_data.columns = ['Quarter', 'Total Cost', 'Total Impressions', 'Campaigns']
        quarter_data = quarter_data.sort_values('Quarter')

        fig_quarter = go.Figure()

        fig_quarter.add_trace(go.Bar(
            name='Trošak (EUR)',
            x=quarter_data['Quarter'],
            y=quarter_data['Total Cost'],
            yaxis='y',
            marker_color='#667eea',
            text=[f"€{x:,.0f}" for x in quarter_data['Total Cost']],
            textposition='auto'
        ))

        fig_quarter.add_trace(go.Scatter(
            name='Broj kampanja',
            x=quarter_data['Quarter'],
            y=quarter_data['Campaigns'],
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=10, color='#f5576c'),
            line=dict(width=3, color='#f5576c')
        ))

        fig_quarter.update_layout(
            yaxis=dict(title='Trošak (EUR)'),
            yaxis2=dict(title='Broj kampanja', overlaying='y', side='right'),
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig_quarter, use_container_width=True)

    else:
        st.warning("⚠️ Nema kampanja koje odgovaraju odabranim filterima. Promijenite kriterije.")

    # ========================================================================
    # FOOTER INFO
    # ========================================================================

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 20px;">
        <p><strong>Ads Estimation Hub - HR Prototype V4</strong> | Developed for Croatian Market 🇭🇷</p>
        <p>Data Source: ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv + Demographics Data</p>
        <p>Total Campaigns in Database: {total} | Coverage: Q1-Q4 2025</p>
        <p><em>Demographics calculated from actual age-gender spend data | Brand 'Croatia' errors auto-fixed</em></p>
        <p><em>✨ NEW: Drill-down Context View - Select any campaign to see original name and details</em></p>
    </div>
    """.format(total=len(df_campaigns)), unsafe_allow_html=True)

else:
    st.error("❌ Aplikacija ne može učitati podatke. Provjerite da li postoje datoteke 'ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv' i 'data - v3/age - gender - v3/campaign age - gender - version 3.csv'.")
