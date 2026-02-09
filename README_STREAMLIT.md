# 📊 ADS ESTIMATION HUB - STREAMLIT APP

## 🚀 BRZI START

### 1. Instalacija Dependencies

Otvori terminal i idi u projekt folder:

```bash
cd "C:\Users\mturkalj\OneDrive - CroWP\Desktop\abandon all hope\ads-estimation-hub"
```

Instaliraj potrebne pakete:

```bash
pip install -r requirements.txt
```

### 2. Pokretanje Aplikacije

Pokreni Streamlit app:

```bash
streamlit run hub_app.py
```

Aplikacija će se automatski otvoriti u browseru na adresi: `http://localhost:8501`

---

## ✨ FUNKCIONALNOSTI

### 🔍 **Lijevi Sidebar - Filteri**
- **Brand:** Odabir jednog ili više brandova
- **Ad Format:** YouTube In-Stream, Bumper, Shorts, Display, itd.
- **Target:** Dobne skupine i spol (npr. "18-65+ | All", "25-44 | F")
- **Bid Strategy:** tCPM, MaxConv, tCPA, CPV, itd.
- **Quarter:** Q1-Q4 2025

### 📋 **Središnji Dio - Campaign Table**
Prikazuje filtrirane kampanje sa:
- **Campaign Name** (standardizirano)
- **Cost (EUR)**
- **Impressions**
- **CPM (EUR)**
- **Peak Reach**

Tablica je sortirana po trošku (descending) i podržava:
- ✅ Scrollanje
- ✅ Pretraživanje
- ✅ Sortiranje po stupcima

### 📊 **Insights & Analytics**
- **Distribucija po Dobnim Skupinama:** Bar chart s postotcima troška
- **Location Badge:** Potvrda hrvatskog tržišta (🇭🇷 100%)
- **Statistika:** Broj brandova, formata i ciljeva

### 💰 **Ključne Metrike (Footer)**
Tri velike kartice s gradient dizajnom:

1. **UKUPNI TROŠAK** - Zbroj svih filtriranih kampanja
2. **UKUPNE IMPRESIJE** - Total impressions
3. **WEIGHTED AVERAGE CPM** ⭐ - Benchmark metrika za procjenu

### 📈 **Dodatne Vizualizacije**
- **Top 10 Brandova po Trošku** (horizontal bar chart)
- **Distribucija CPM-a** (histogram s weighted average linijom)
- **Distribucija po Kvartalima** (dual-axis chart: trošak + broj kampanja)

---

## 🎯 PRIMJERI KORIŠTENJA

### Use Case 1: Nivea Bumper Campaign
**Filteri:**
- Brand: `Nivea`
- Ad Format: `YouTube Bumper`
- Target: `65+ | All`

**Očekivani output:**
- Prikazat će sve Nivea Bumper kampanje
- Weighted Average CPM za taj profil
- Demografsku raspodjelu

### Use Case 2: Q1 Performance Max Overview
**Filteri:**
- Quarter: `Q1 2025`
- Bid Strategy: `MaxConv`

**Očekivani output:**
- Sve PMax kampanje iz Q1
- Ukupni trošak i impresije za taj period
- CPM benchmark za PMax strategiju

### Use Case 3: Female 25-44 Targeting Analysis
**Filteri:**
- Target: Odaberi sve target skupine koje sadrže "25-34" ili "35-44" + "F"

**Očekivani output:**
- Sve kampanje koje targetiraju žene 25-44
- Raspodjela troška po godinama
- CPM benchmark za taj demografski segment

---

## 🛠️ TEHNIČKI DETALJI

### Struktura Aplikacije

```
hub_app.py
├── PAGE CONFIG (wide layout, ikona, naslov)
├── HELPER FUNCTIONS
│   ├── load_data() - učitavanje i parsiranje CSV-a
│   ├── parse_cost() - konverzija EUR formata
│   ├── parse_impressions() - konverzija brojeva
│   ├── calculate_weighted_cpm() - weighted average CPM
│   └── extract_age_groups() - ekstrakcija dobnih skupina
├── DATA LOADING (caching za performanse)
├── FILTERS (sidebar multiselect)
├── MAIN CONTENT
│   ├── Campaign Table (dataframe)
│   ├── Insights Sidebar (age distribution, location badge)
│   └── Footer Metrics (big cards)
└── VISUALIZATIONS (Plotly charts)
```

### Optimizacije

- **@st.cache_data:** Data loading je cached za brže učitavanje
- **Responsive Design:** Radi na svim veličinama ekrana
- **Automatic Refresh:** Podatci se automatski osvježavaju pri promjeni filtera
- **Professional UI:** Gradient cards, Plotly interactive charts

---

## 📦 DEPENDENCIES

```
streamlit==1.31.0    # Web framework
pandas==2.1.4        # Data manipulation
numpy==1.26.3        # Numerical operations
plotly==5.18.0       # Interactive visualizations
```

---

## 🔧 TROUBLESHOOTING

### Problem 1: "ModuleNotFoundError: No module named 'streamlit'"
**Rješenje:** Instaliraj dependencies:
```bash
pip install -r requirements.txt
```

### Problem 2: "FileNotFoundError: ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv"
**Rješenje:** Provjeri da je CSV file u istom folderu kao `hub_app.py`

### Problem 3: Port 8501 je zauzet
**Rješenje:** Pokreni na drugom portu:
```bash
streamlit run hub_app.py --server.port 8502
```

### Problem 4: Encoding error s hrvatskim znakovima
**Rješenje:** CSV file mora biti u UTF-8 encoding-u (što već jest)

---

## 🎨 CUSTOMIZACIJA

### Promjena Boja
Uredi `hub_app.py` i promijeni gradient boje u metric karticama:

```python
# Primjer: Ukupni Trošak (linija ~228)
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Dodavanje Novog Filtera
```python
# U FILTERS sekciji dodaj:
new_filter = st.sidebar.multiselect(
    "Novi Filter:",
    options=['Sve'] + sorted(df_campaigns['Nova_Kolona'].unique()),
    default=['Sve']
)

# U APPLY FILTERS sekciji:
if 'Sve' not in new_filter and len(new_filter) > 0:
    df_filtered = df_filtered[df_filtered['Nova_Kolona'].isin(new_filter)]
```

---

## 📞 SUPPORT

Ako naiđeš na probleme:
1. Provjeri da su svi dependencies instalirani
2. Provjeri encoding CSV file-a (UTF-8)
3. Provjeri da je Python verzija 3.8+

---

**Verzija:** 1.0.0
**Zadnje ažuriranje:** 2026-02-09
**Developer:** Claude Code + CroWP Team 🇭🇷
