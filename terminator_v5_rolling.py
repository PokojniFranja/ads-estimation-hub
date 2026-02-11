#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADS ESTIMATION HUB - HR MASTER VERSION V5 - ROLLING REACH
Interactive dashboard for Croatian Google Ads campaign analysis
PRODUCTION VERSION with Rolling Reach Integration (90-day windows)
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
    page_title="Estimator Terminator - HR Master",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS CUSTOMIZATION - Ultra Precise Spacing
# ============================================================================

st.markdown("""
<style>
    /* Main container - increased padding to prevent cut-off */
    div.block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    /* Sidebar - AGGRESSIVE ZERO top padding to absolute top */
    section[data-testid="stSidebar"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Force zero on ALL child divs in sidebar (first 3 levels) */
    [data-testid="stSidebar"] > div {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] > div > div {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] > div > div > div {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Target ALL Streamlit internal padding classes - force zero */
    [data-testid="stSidebar"] .st-emotion-cache-6qob1r {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] [class*="st-emotion-cache"] {
        padding-top: 0rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Additional Streamlit cache classes that might add padding */
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] [class*="css-"] {
        padding-top: 0rem !important;
    }

    [data-testid="stSidebar"] .element-container:first-child {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Nuclear option - force sidebar content wrapper */
    [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
    }

    /* Drastically reduce gap between sidebar elements */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.3rem !important;
    }

    [data-testid="stSidebar"] .element-container {
        margin-bottom: 0.3rem !important;
    }

    /* Tight spacing for sidebar widgets */
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.2rem !important;
        margin-top: 0.2rem !important;
    }

    [data-testid="stSidebar"] .stTextInput {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    [data-testid="stSidebar"] .stMultiSelect {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    [data-testid="stSidebar"] .stSlider {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    [data-testid="stSidebar"] .stNumberInput {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    [data-testid="stSidebar"] .stCheckbox {
        margin-bottom: 0.3rem !important;
        margin-top: 0.3rem !important;
    }

    /* Dividers - minimal margin */
    [data-testid="stSidebar"] hr {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Sidebar headers - reduce spacing */
    [data-testid="stSidebar"] h1 {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0rem !important;
    }

    [data-testid="stSidebar"] h2 {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    [data-testid="stSidebar"] h3 {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Caption text - minimal spacing */
    [data-testid="stSidebar"] .stCaptionContainer {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }

    /* Reduce spacing in main content headers */
    .main h1 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    .main h2 {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    .main h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Reduce spacing between main content sections */
    .main .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Tighten spacing for charts and visualizations */
    .main [data-testid="stPlotlyChart"] {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Compact spacing for metric cards */
    .main [data-testid="stMetric"] {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Eliminate gap above Key Metrics section */
    [data-testid="stMetricBlock"] {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* Force tight spacing for metric containers */
    .main [data-testid="column"] {
        padding-top: 0rem !important;
    }

    /* Minimal margin on hr elements */
    .main hr {
        margin-top: 0rem !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

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
    """Load and parse the campaign data.
    NOTE: Reach_parsed will be overridden with rolling reach data after loading.
    """
    df = pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')

    # Parse numeric columns
    df['Cost_parsed'] = df['Cost'].apply(parse_cost)
    df['Impr_parsed'] = df['Impr.'].apply(parse_number)
    df['Reach_parsed'] = df['Peak_Reach'].apply(parse_number)  # Temporary, will be replaced

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

def parse_age_range(age_str):
    """
    Parse age range string to get min and max age.
    Examples:
    - '18-24' -> (18, 24)
    - '25 - 34' -> (25, 34)  [handles spaces]
    - '65+' -> (65, 100)
    - 'Unknown' -> (0, 0)
    """
    age_str = str(age_str).strip()

    if age_str in ['Unknown', '', 'N/A']:
        return (0, 0)

    # Remove all spaces for easier parsing
    age_str_clean = age_str.replace(' ', '')

    if '-' in age_str_clean:
        # Format: "18-24" or "25-34" or "25 - 34"
        parts = age_str_clean.split('-')
        try:
            age_min = int(parts[0])
            age_max_str = parts[1].replace('+', '')
            age_max = int(age_max_str) if age_max_str else 100
        except:
            return (0, 0)
    elif '+' in age_str_clean:
        # Format: "65+" or "65 +"
        try:
            age_min = int(age_str_clean.replace('+', ''))
            age_max = 100
        except:
            return (0, 0)
    else:
        # Single number or unknown
        try:
            age_min = age_max = int(age_str_clean)
        except:
            return (0, 0)

    return (age_min, age_max)

def get_full_range_demographics(campaign_id, df_demographics, threshold=0.10):
    """
    Get FULL RANGE demographics with THRESHOLD FILTERING.

    CRITICAL CHANGE: Only includes age/gender segments that account for at least
    10% of total campaign spend. This eliminates noise from optimized targeting
    and accidental impressions.

    Examples:
    - Campaign with 95% spend in 25-34 → Returns "25-34" (NOT "18-65+")
    - Campaign with 40% in 18-24, 45% in 25-34 → Returns "18-34"
    - Campaign with 5% in each age → Returns dominant segment only

    This ensures accurate targeting representation and meaningful filter options.
    """
    if df_demographics is None or len(df_demographics) == 0:
        return ("Unknown", "Unknown")

    # Filter for this campaign
    demo_data = df_demographics[df_demographics['Campaign ID'] == campaign_id]

    if len(demo_data) == 0:
        return ("Unknown", "Unknown")

    # Calculate total spend for this campaign
    total_spend = demo_data['Cost_parsed'].sum()

    if total_spend == 0:
        return ("Unknown", "Unknown")

    # Group by Age and calculate spend per segment
    age_spend = demo_data.groupby('Age')['Cost_parsed'].sum()

    # Filter ages by threshold (10% minimum) AND exclude Unknown
    significant_ages = []
    for age, spend in age_spend.items():
        age_str = str(age).strip()

        # CRITICAL: Skip Unknown and invalid values
        if age_str in ['Unknown', 'nan', '', 'N/A']:
            continue

        percentage = spend / total_spend

        # Only include if meets 10% threshold
        if percentage >= threshold:
            significant_ages.append((age_str, spend, percentage))

    # If no significant ages meet threshold, fall back to dominant segment
    if len(significant_ages) == 0:
        valid_ages = {age: spend for age, spend in age_spend.items()
                      if str(age).strip() not in ['Unknown', 'nan', '', 'N/A']}

        if len(valid_ages) > 0:
            dominant_age = max(valid_ages, key=valid_ages.get)
            dominant_spend = valid_ages[dominant_age]
            significant_ages = [(str(dominant_age), dominant_spend, dominant_spend / total_spend)]
        else:
            return ("Unknown", "Unknown")

    # Sort by percentage descending
    significant_ages.sort(key=lambda x: x[2], reverse=True)

    # CRITICAL: If only ONE significant age segment, return it AS IS (don't create range)
    if len(significant_ages) == 1:
        age_range = significant_ages[0][0]
    else:
        # Multiple significant segments - create range from min to max
        age_strings = [a[0] for a in significant_ages]

        # Parse all significant ages to find min/max
        age_min = 999
        age_max = 0

        for age_str in age_strings:
            min_age, max_age = parse_age_range(age_str)
            if min_age > 0:
                if min_age < age_min:
                    age_min = min_age
                # Don't let 65+ (100) inflate the max
                if max_age < 100 and max_age > age_max:
                    age_max = max_age
                elif max_age >= 100:  # This is 65+
                    age_max = 65

        # Construct range
        if age_min == 999 or age_max == 0:
            age_range = significant_ages[0][0]  # Fallback to dominant
        elif age_min == age_max:
            age_range = str(age_min)
        elif age_max >= 65:
            age_range = f"{age_min}-65+"
        else:
            age_range = f"{age_min}-{age_max}"

    # Gender logic with threshold
    gender_spend = demo_data.groupby('Gender')['Cost_parsed'].sum()

    significant_genders = []
    for gender, spend in gender_spend.items():
        gender_str = str(gender).strip()

        # CRITICAL: Skip Unknown
        if gender_str in ['Unknown', 'nan', '', 'N/A']:
            continue

        percentage = spend / total_spend

        if percentage >= threshold:
            significant_genders.append(gender_str)

    # If no significant genders, fall back to dominant
    if len(significant_genders) == 0:
        valid_genders = {gender: spend for gender, spend in gender_spend.items()
                        if str(gender).strip() not in ['Unknown', 'nan', '', 'N/A']}

        if len(valid_genders) > 0:
            dominant_gender = max(valid_genders, key=valid_genders.get)
            significant_genders = [str(dominant_gender)]
        else:
            gender = 'Unknown'
            return (age_range, gender)

    # Map gender codes
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
    # If yes, add '+ UNK' suffix to indicate "grey zone" users
    unknown_spend = 0
    for age, spend in age_spend.items():
        age_str = str(age).strip()
        if age_str in ['Unknown', 'nan', '', 'N/A', 'Undetermined']:
            unknown_spend += spend

    # Add + UNK suffix if there's at least 0.01 EUR in Unknown
    if unknown_spend >= 0.01:
        age_range = age_range + ' + UNK'

    return (age_range, gender)

def calculate_weighted_cpm(df):
    """Calculate weighted average CPM."""
    total_cost = df['Cost_parsed'].sum()
    total_impressions = df['Impr_parsed'].sum()

    if total_impressions > 0:
        return (total_cost / total_impressions) * 1000
    else:
        return 0.0

def get_targeting_level(df_filtered):
    """
    Determine targeting level based on 80% MAJORITY RULE.

    LOCAL TARGETING bubble is shown ONLY if local campaigns (city keywords)
    make up MORE THAN 80% of currently filtered data.

    In all other cases (including initial view), shows NATIONAL TARGETING.

    Returns: (icon_text, level_text, color)
    """
    city_keywords = ['McDelivery', 'Zagreb', 'Split', 'Rijeka', 'Osijek', 'Zadar', 'Pula']

    total_campaigns = len(df_filtered)

    # If no campaigns, default to NATIONAL
    if total_campaigns == 0:
        return ('🌍 NATIONAL TARGETING', 'Croatia', '#28a745')

    # Count campaigns with city keywords
    local_count = 0
    for campaign_name in df_filtered['Campaign']:
        campaign_str = str(campaign_name).lower()
        if any(keyword.lower() in campaign_str for keyword in city_keywords):
            local_count += 1

    # Calculate percentage
    local_percentage = (local_count / total_campaigns) * 100

    # 80% MAJORITY RULE
    if local_percentage > 80:
        return ('📍 LOCAL TARGETING', 'City Level', '#ffc107')  # Yellow - only if >80% local
    else:
        return ('🌍 NATIONAL TARGETING', 'Croatia', '#28a745')  # Green - default

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

CAMPAIGN_PATH = "MASTER_ADS_HR_CLEANED.csv"
ROLLING_REACH_PATH = "MASTER_ROLLING_DATA_2025_CLEAN.csv"
DEMOGRAPHICS_PATH = "data - v3/age - gender - v3/campaign age - gender - version 3.csv"

try:
    df_campaigns = load_campaign_data(CAMPAIGN_PATH)
    df_demographics = load_demographics_data(DEMOGRAPHICS_PATH)

    # Load rolling reach data
    df_rolling = pd.read_csv(ROLLING_REACH_PATH, encoding='utf-8-sig')
    df_rolling['Reach'] = pd.to_numeric(df_rolling['Reach'], errors='coerce')
    df_rolling['Avg_Frequency'] = pd.to_numeric(df_rolling['Avg_Frequency'], errors='coerce')

    # Get peak reach and avg frequency per campaign from rolling data
    rolling_agg = df_rolling.groupby('Campaign_ID').agg({
        'Reach': 'max',  # Peak reach across all windows
        'Avg_Frequency': 'mean'  # Average frequency across windows
    }).reset_index()
    rolling_agg.columns = ['Campaign ID', 'Peak_Reach_Rolling', 'Avg_Frequency_Rolling']

    # Merge rolling reach data into campaigns dataframe
    df_campaigns = df_campaigns.merge(rolling_agg, on='Campaign ID', how='left')

    # Use rolling reach if available, otherwise fallback to original
    df_campaigns['Peak_Reach_Final'] = df_campaigns['Peak_Reach_Rolling'].fillna(df_campaigns['Peak_Reach'])
    df_campaigns['Reach_parsed'] = df_campaigns['Peak_Reach_Final'].apply(parse_number)

    # Add frequency from rolling data
    df_campaigns['Avg_Frequency'] = df_campaigns['Avg_Frequency_Rolling']

    # Count how many campaigns got rolling reach data
    rolling_count = df_campaigns['Peak_Reach_Rolling'].notna().sum()
    total_count = len(df_campaigns)

    # This will be shown in sidebar later (after sidebar title)

    # SAFETY CLEANUP: Remove campaigns with Unknown quarter
    unknown_quarter_count = len(df_campaigns[df_campaigns['Quarter'] == 'Unknown'])
    if unknown_quarter_count > 0:
        df_campaigns = df_campaigns[df_campaigns['Quarter'] != 'Unknown']

    # Calculate FULL RANGE demographics with THRESHOLD filtering
    demographics_results = df_campaigns['Campaign ID'].apply(
        lambda cid: get_full_range_demographics(cid, df_demographics)
    )

    df_campaigns['Age_Range'] = demographics_results.apply(lambda x: x[0])
    df_campaigns['Gender'] = demographics_results.apply(lambda x: x[1])

    # Update Target column with corrected demographics
    df_campaigns['Target_Corrected'] = df_campaigns['Age_Range'] + " | " + df_campaigns['Gender']

    # Rebuild Standardized_Campaign_Name with corrected demographics
    df_campaigns['Standardized_Campaign_Name_Corrected'] = df_campaigns.apply(rebuild_campaign_name, axis=1)

    # Aggregate by Campaign ID to ensure one campaign = one row
    duplicate_count = df_campaigns['Campaign ID'].duplicated().sum()

    if duplicate_count > 0:
        # Define aggregation rules
        agg_rules = {
            'Campaign': 'first',
            'Brand': 'first',
            'Ad_Format': 'first',
            'Date_Range': 'first',
            'Bid_Strategy_Short': 'first',
            'Goal': 'first',
            'Cost': 'first',
            'Impr.': 'first',
            'Peak_Reach': 'first',
            'Cost_parsed': 'sum',
            'Impr_parsed': 'sum',
            'Reach_parsed': 'max',
            'Avg_Frequency': 'mean',
            'Clicks_parsed': 'sum',
            'CTR_parsed': 'mean',
            'Avg_CPC_parsed': 'mean',
            'Avg_CPM_parsed': 'mean',
            'TrueView_views_parsed': 'sum',
            'TrueView_CPV_parsed': 'mean',
            'Conversions_parsed': 'sum',
            'Conv_rate_parsed': 'mean',
            'Cost_per_conv_parsed': 'mean',
            'CPM': 'mean',
            'Quarter': 'first',
            'Age_Range': 'first',
            'Gender': 'first',
            'Target_Corrected': 'first',
            'Standardized_Campaign_Name_Corrected': 'first'
        }

        # Add Account column if it exists
        if 'Account' in df_campaigns.columns:
            agg_rules['Account'] = 'first'
        elif 'Account name' in df_campaigns.columns:
            agg_rules['Account name'] = 'first'

        # Aggregate by Campaign ID
        df_campaigns = df_campaigns.groupby('Campaign ID', as_index=False).agg(agg_rules)

    data_loaded = True

except Exception as e:
    st.error(f"❌ Greška pri učitavanju podataka: {e}")
    data_loaded = False

# ============================================================================
# APP LAYOUT
# ============================================================================

if data_loaded:

    # ========================================================================
    # SESSION STATE INITIALIZATION (for reset functionality)
    # ========================================================================

    if 'reset_key' not in st.session_state:
        st.session_state.reset_key = 0

    # ========================================================================
    # LEFT SIDEBAR - FILTERS
    # ========================================================================

    st.sidebar.title('⚙️ Filteri')

    # Show rolling reach coverage info
    rolling_count = df_campaigns['Peak_Reach_Rolling'].notna().sum()
    total_count = len(df_campaigns)
    st.sidebar.caption(f"📊 Rolling Reach: {rolling_count}/{total_count} ({rolling_count/total_count*100:.0f}%) | 90-Day Windows")

    # ========================================================================
    # 1. RESET BUTTON (First element - no separators)
    # ========================================================================

    if st.sidebar.button("🔄 Resetiraj sve filtre", use_container_width=True, type="secondary"):
        # Increment reset key to force all widgets to reset to defaults
        st.session_state.reset_key += 1
        st.rerun()

    # ========================================================================
    # 2. SEARCH MODULE (Priority filter - searches original campaign names)
    # ========================================================================

    search_query = st.sidebar.text_input(
        "🔍 Pretraži kampanje",
        value="",
        placeholder="Upiši dio naziva kampanje...",
        help="Pretraga po ORIGINALNOM nazivu kampanje (case-insensitive). Ima prioritet nad ostalim filterima.",
        key=f"search_{st.session_state.reset_key}"
    )

    # ========================================================================
    # 2b. TOGGLE ZA PRIKAZ ORIGINALNIH IMENA (odmah ispod Search-a)
    # ========================================================================

    show_original_names = st.sidebar.toggle(
        "📄 Prikaži originalna imena kampanja",
        value=False,
        help="Kad je uključeno, tablica prikazuje originalna imena kampanja umjesto standardiziranih.",
        key=f"show_original_{st.session_state.reset_key}"
    )

    # ========================================================================
    # 3. DUALNI BUDGET FILTER (Third element - Benchmark Tool)
    # ========================================================================

    st.sidebar.markdown("### 💰 Budžet")

    min_cost = float(df_campaigns['Cost_parsed'].min())
    max_cost = float(df_campaigns['Cost_parsed'].max())

    # Target Budget Input (for benchmarking)
    target_budget = st.sidebar.number_input(
        "Ciljani budžet (€):",
        min_value=0.0,
        max_value=max_cost * 2,
        value=0.0,
        step=100.0,
        format="%.0f",
        help="Prikazuje kampanje slične vrijednosti za lakši benchmark (± 10% od ciljanog iznosa)",
        key=f"target_budget_{st.session_state.reset_key}"
    )

    # Budget Range Slider (disabled if target budget is set)
    selected_budget_range = st.sidebar.slider(
        "Raspon troška (EUR):",
        min_value=min_cost,
        max_value=max_cost,
        value=(min_cost, max_cost),
        format="€%.0f",
        disabled=(target_budget > 0),
        key=f"budget_slider_{st.session_state.reset_key}"
    )

    # Show active filter info (compact)
    if target_budget > 0:
        lower_bound = target_budget * 0.9
        upper_bound = target_budget * 1.1
        st.sidebar.caption(f"🎯 Benchmark: €{lower_bound:,.0f} - €{upper_bound:,.0f} (± 10%)")
    else:
        st.sidebar.caption(f"📊 Raspon: €{selected_budget_range[0]:,.0f} - €{selected_budget_range[1]:,.0f}")

    st.sidebar.divider()

    # ========================================================================
    # 4. OSTALI FILTERI
    # ========================================================================

    # Brand filter
    brands = ['Svi'] + sorted(df_campaigns['Brand'].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect(
        "Brand:",
        options=brands,
        default=['Svi'],
        key=f"brands_{st.session_state.reset_key}"
    )

    # Ad Format filter
    ad_formats = ['Svi'] + sorted(df_campaigns['Ad_Format'].dropna().unique().tolist())
    selected_formats = st.sidebar.multiselect(
        "Ad Format:",
        options=ad_formats,
        default=['Svi'],
        key=f"formats_{st.session_state.reset_key}"
    )

    # Age Range filter (using corrected demographics)
    age_ranges = ['Svi'] + sorted([x for x in df_campaigns['Age_Range'].dropna().unique().tolist() if x != 'Unknown'])
    selected_ages = st.sidebar.multiselect(
        "Age Group:",
        options=age_ranges,
        default=['Svi'],
        help="⚠️ STRICT MATCH: Odabir '18-24' prikazuje SAMO kampanje koje targetiraju isključivo 18-24. Kampanje s širim rasponom (npr. 18-34) NEĆE biti prikazane.",
        key=f"ages_{st.session_state.reset_key}"
    )

    # Gender filter (using corrected demographics)
    genders = ['Svi'] + sorted([x for x in df_campaigns['Gender'].dropna().unique().tolist() if x != 'Unknown'])
    selected_genders = st.sidebar.multiselect(
        "Gender:",
        options=genders,
        default=['Svi'],
        help="⚠️ STRICT MATCH: Odabir 'Female' prikazuje SAMO kampanje koje targetiraju isključivo žene. Kampanje s 'All' NEĆE biti prikazane.",
        key=f"genders_{st.session_state.reset_key}"
    )

    # Bid Strategy filter
    bid_strategies = ['Svi'] + sorted(df_campaigns['Bid_Strategy_Short'].dropna().unique().tolist())
    selected_bid_strategies = st.sidebar.multiselect(
        "Bid Strategy:",
        options=bid_strategies,
        default=['Svi'],
        key=f"bid_strategies_{st.session_state.reset_key}"
    )

    # Quarter filter
    quarters = ['Svi'] + sorted(df_campaigns['Quarter'].dropna().unique().tolist())
    selected_quarters = st.sidebar.multiselect(
        "Quarter:",
        options=quarters,
        default=['Svi'],
        key=f"quarters_{st.session_state.reset_key}"
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
        help="Odaberi dodatne metrike koje želiš vidjeti u tablici",
        key=f"metrics_{st.session_state.reset_key}"
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
            pass

    st.sidebar.markdown("---")

    # ========================================================================
    # APPLY FILTERS
    # ========================================================================

    df_filtered = df_campaigns.copy()

    # ========================================================================
    # PRIORITY: SEARCH FILTER (Applied FIRST - has priority over other filters)
    # ========================================================================

    if search_query and search_query.strip():
        # Case-insensitive search on ORIGINAL campaign names
        search_term = search_query.strip()
        df_filtered = df_filtered[
            df_filtered['Campaign'].str.contains(search_term, case=False, na=False)
        ]

    # Apply Brand filter
    if 'Svi' not in selected_brands and len(selected_brands) > 0:
        df_filtered = df_filtered[df_filtered['Brand'].isin(selected_brands)]

    # Apply Budget filter (DUALNI - Target Budget ili Slider)
    if target_budget > 0:
        # BENCHMARK MODE: Use target budget with ± 10% range
        lower_bound = target_budget * 0.9
        upper_bound = target_budget * 1.1
        df_filtered = df_filtered[
            (df_filtered['Cost_parsed'] >= lower_bound) &
            (df_filtered['Cost_parsed'] <= upper_bound)
        ]
    else:
        # STANDARD MODE: Use slider range
        df_filtered = df_filtered[
            (df_filtered['Cost_parsed'] >= selected_budget_range[0]) &
            (df_filtered['Cost_parsed'] <= selected_budget_range[1])
        ]

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

        # Show search indicator if active
        if search_query and search_query.strip():
            st.markdown(f"🔍 **Search aktivan:** '{search_query}'")

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

        # ====================================================================
        # DRILL-DOWN CONTEXT SELECTOR
        # ====================================================================

        st.markdown("### 🔍 Drill-down Context View")

        # Create selectbox for campaign selection
        df_filtered_sorted = df_filtered.sort_values('Cost_parsed', ascending=False)

        # Create campaign options list with original names in parentheses
        if show_original_names:
            # Show only original names
            campaign_options = ['-- Odaberi kampanju za detalje --'] + df_filtered_sorted['Campaign'].tolist()
            search_column = 'Campaign'
        else:
            # Show "Standardized (Original)"
            campaign_display_list = (
                df_filtered_sorted['Standardized_Campaign_Name_Corrected'] +
                " (" + df_filtered_sorted['Campaign'] + ")"
            ).tolist()
            campaign_options = ['-- Odaberi kampanju za detalje --'] + campaign_display_list
            search_column = 'Campaign_Display_Dropdown'

            # Create mapping column for search
            df_filtered_sorted['Campaign_Display_Dropdown'] = (
                df_filtered_sorted['Standardized_Campaign_Name_Corrected'] +
                " (" + df_filtered_sorted['Campaign'] + ")"
            )

        selected_campaign_name = st.selectbox(
            "Odaberi kampanju za prikaz originalnog naziva i dodatnih detalja:",
            options=campaign_options,
            index=0,
            help="Odaberi kampanju da vidiš originalni naziv i druge detalje"
        )

        # Show campaign details if selected
        if selected_campaign_name != '-- Odaberi kampanju za detalje --':
            campaign_row = df_filtered_sorted[df_filtered_sorted[search_column] == selected_campaign_name].iloc[0]

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

        # Visual feedback for toggle state
        if show_original_names:
            st.caption("📄 Prikazujem originalna imena kampanja (kao što su unesena u Google Ads)")
        else:
            st.caption("💡 Prikazujem standardizirana imena s originalnim u zagradi. Uključi toggle '📄 Prikaži originalna imena kampanja' za samo originalne nazive.")

        # Prepare display dataframe with dynamic columns
        # CONDITIONAL: Use original or standardized name based on toggle
        if show_original_names:
            display_columns = ['Campaign']
            display_column_names = ['Original Campaign Name']
        else:
            # Create combined column: "Standardized Name (Original Name)"
            df_filtered['Campaign_Display'] = (
                df_filtered['Standardized_Campaign_Name_Corrected'] +
                " (" + df_filtered['Campaign'] + ")"
            )
            display_columns = ['Campaign_Display']
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

        # Sort by Cost by default
        if 'Cost (EUR)' in display_column_names:
            df_display = df_display.sort_values('Cost (EUR)', ascending=False)

        # Configure column formatting for proper sortable display
        column_config = {}

        for col in display_column_names[1:]:  # Skip campaign name
            if 'EUR' in col or 'CPM' in col or 'CPC' in col or 'CPV' in col or 'Cost' in col:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="€%.2f",
                    help=f"Sortable {col}"
                )
            elif '%' in col or 'Rate' in col or 'CTR' in col:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"Sortable {col}"
                )
            elif 'Impressions' in col or 'Reach' in col or 'Clicks' in col or 'Views' in col:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%d",
                    help=f"Sortable {col}"
                )
            elif 'Conversions' in col:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f",
                    help=f"Sortable {col}"
                )

        # Display table with sortable columns
        st.dataframe(
            df_display,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config=column_config
        )

        # ====================================================================
        # RIGHT SIDEBAR - INSIGHTS
        # ====================================================================

        col_left, col_right = st.columns([2, 1])

        with col_left:
            # Age Group Distribution (using corrected demographics)
            st.markdown("### 👥 Distribucija po Dobnim Skupinama")
            st.caption("💡 Prikazuje trošak po značajnim rasponima (≥10% threshold). Kampanja s 95% troška u 25-34 prikazuje se kao '25-34', ne '18-65+'.")

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
                st.caption("Nema podataka o dobnim skupinama za odabrane filtre.")

        with col_right:
            # Location Badge (DYNAMIC - changes based on campaign names)
            st.markdown("### 📍 Lokacija")

            # Get targeting level dynamically
            targeting_icon, targeting_level, border_color = get_targeting_level(df_filtered)

            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                border: 3px solid {border_color};
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin-top: 20px;
            ">
                <h2 style="color: #212529; margin: 0; font-size: 24px;">{targeting_icon}</h2>
                <h3 style="color: #212529; margin: 10px 0; font-size: 16px;">{targeting_level}</h3>
                <p style="color: #6c757d; margin: 0; font-size: 12px;">Croatia 🇭🇷</p>
            </div>
            """, unsafe_allow_html=True)

            # Gender distribution
            st.markdown("### 👤 Distribucija po Spolu")

            gender_distribution = df_filtered.groupby('Gender')['Cost_parsed'].sum().sort_values(ascending=False)

            if len(gender_distribution) > 0:
                for gender, cost in gender_distribution.items():
                    pct = (cost / gender_distribution.sum() * 100)
                    st.markdown(f"**{gender}:** €{cost:,.2f} ({pct:.1f}%)")

            # ================================================================
            # NOISE ANALYSIS CHART (Shows ALL age segments, no threshold)
            # ================================================================

            st.markdown("---")
            st.markdown("### 📊 Detaljna Raspodjela po Godinama")
            st.caption("💡 Prikazuje SVE age segmente uključujući 'noise' ispod 10% thresholda")

            # Get Campaign IDs from filtered data
            campaign_ids_filtered = df_filtered['Campaign ID'].tolist()

            # Get demographics for these campaigns
            demo_filtered = df_demographics[df_demographics['Campaign ID'].isin(campaign_ids_filtered)]

            if len(demo_filtered) > 0:
                # Group by Age and sum spend (NO THRESHOLD - show everything)
                age_breakdown = demo_filtered.groupby('Age')['Cost_parsed'].sum().sort_values(ascending=False)

                # Remove completely empty segments
                age_breakdown = age_breakdown[age_breakdown > 0]

                if len(age_breakdown) > 0:
                    # Create dataframe for chart
                    df_age_noise = pd.DataFrame({
                        'Age': age_breakdown.index,
                        'Cost': age_breakdown.values
                    })

                    # Calculate percentages
                    total_cost_noise = df_age_noise['Cost'].sum()
                    df_age_noise['Percentage'] = (df_age_noise['Cost'] / total_cost_noise * 100).round(2)

                    # Create bar chart
                    fig_age_noise = px.bar(
                        df_age_noise,
                        x='Age',
                        y='Cost',
                        title='',
                        labels={'Cost': 'Trošak (EUR)', 'Age': 'Dobna Skupina'},
                        text='Percentage',
                        color='Percentage',
                        color_continuous_scale='Reds',
                        hover_data={'Cost': ':,.2f', 'Percentage': ':.2f'}
                    )

                    fig_age_noise.update_traces(
                        texttemplate='%{text:.1f}%',
                        textposition='outside',
                        textfont_size=10
                    )
                    fig_age_noise.update_layout(showlegend=False, height=350)

                    st.plotly_chart(fig_age_noise, use_container_width=True)
                else:
                    st.caption("Nema dostupnih podataka o dobnim segmentima.")
            else:
                st.caption("Nema demographics podataka za odabrane kampanje.")

        # ====================================================================
        # FOOTER - BIG METRICS
        # ====================================================================

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
                <p style="margin: 0; font-size: 14px; opacity: 0.8;">Peak Reach (90-day): {df_filtered['Reach_parsed'].max():,}</p>
                <p style="margin: 0; font-size: 12px; opacity: 0.7;">Avg Freq: {df_filtered['Avg_Frequency'].mean():.2f}</p>
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

    else:
        st.caption("⚠️ Nema kampanja koje odgovaraju odabranim filterima. Promijenite kriterije.")

    # ========================================================================
    # FOOTER INFO
    # ========================================================================

    st.markdown("""
    <div style="text-align: center; color: #888; padding: 20px;">
        <p><strong>Ads Estimation Hub - HR Master V5 - Rolling Reach</strong> | Production-Ready for Croatian Market 🇭🇷</p>
        <p>Data Sources: MASTER_ADS_HR_CLEANED.csv (Cost, Impressions, Brand) + MASTER_ROLLING_DATA_2025_CLEAN.csv (90-Day Reach & Frequency)</p>
        <p>Total Campaigns in Database: {total} | Coverage: Q1-Q4 2025</p>
        <p><em>✨ Rolling Reach Data | S-Curve Saturations | 90-Day Windows | Precise Reach Estimation</em></p>
    </div>
    """.format(total=len(df_campaigns)), unsafe_allow_html=True)

else:
    st.error("❌ Aplikacija ne može učitati podatke. Provjerite da li postoje datoteke 'MASTER_ADS_HR_CLEANED.csv' i 'data - v3/age - gender - v3/campaign age - gender - version 3.csv'.")
