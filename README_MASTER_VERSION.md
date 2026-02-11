# 🤖 ADS ESTIMATION HUB - MASTER VERSION

**Production-Ready Dashboard za analizu Google Ads kampanja na hrvatskom tržištu**

---

## 🚀 QUICK START

### Pokretanje Dashboard-a:
```bash
streamlit run hub_app.py
```

Dashboard će se otvoriti u browseru na `http://localhost:8501`

---

## 📊 ŠTO JE NOVO U MASTER VERZIJI?

### ✅ Čisti Podaci
- **131 Ad Format greška** trajno ispravljena
- **Brand 'Croatia'** zamijenjen s 'Hidra'
- Više nema potrebe za "krpanjem" podataka

### ✅ Sortabilne Kolone
- **Klikni na bilo koje zaglavlje stupca** za sortiranje
- Radi sa svim numeričkim i tekstualnim kolonama
- Uzlazno/silazno sortiranje

### ✅ Jednostavnija Arhitektura
- Uklonjena sva logika za "krpanje" podataka
- Brže učitavanje aplikacije
- Čišći kod, lakše održavanje

---

## 📁 KLJUČNE DATOTEKE

| Datoteka | Opis |
|----------|------|
| `MASTER_ADS_HR_CLEANED.csv` | **GLAVNA BAZA** - čista, production-ready |
| `hub_app.py` | Dashboard aplikacija |
| `create_master_file.py` | Script za regeneriranje master file-a |
| `BACKUP_ADS_HR_PRE_CLEANUP.csv` | Sigurnosna kopija prije čišćenja |

---

## 🔧 REGENERIRANJE MASTER FILE-A

Ako trebaš regenerirati master file (npr. nakon novih izmjena):

```bash
python create_master_file.py
```

**Potrebni ulazni file-ovi:**
- `ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv` (originalna baza)
- `other-format-cleaned.csv` (Ad Format popravci)

**Izlazni file-ovi:**
- `MASTER_ADS_HR_CLEANED.csv` (čista baza)
- `BACKUP_ADS_HR_PRE_CLEANUP.csv` (backup)

---

## 💡 GLAVNE FUNKCIONALNOSTI

### 🔍 Search & Filter
- **Search:** Pretraži po originalnom nazivu kampanje
- **Brand Filter:** Filtriraj po brendu
- **Ad Format:** YouTube, Display, Demand Gen, PMax
- **Demographics:** Age groups i Gender (10% threshold)
- **Budget:** Raspon ili ciljani budžet (±10% benchmark)
- **Quarter:** Q1-Q4 2025

### 📊 Sortiranje
- Klikni na **zaglavlje bilo kojeg stupca** za sortiranje
- Automatsko formatiranje brojeva (€, %, itd.)
- Zadržava numeričke vrijednosti za točno sortiranje

### 📈 Visualizacije
- Distribucija po dobnim skupinama
- Distribucija po spolu
- Top 10 brandova
- CPM distribucija
- Kvartalna analiza

### 🔬 Drill-down Context
- Odaberi kampanju za detalje
- Originalni naziv kampanje
- Campaign ID, Account, Brand
- Key metrics

---

## 📋 DATA QUALITY

### Master Data Features:
- ✅ **131 Ad Format greška** ispravljena (Other → Display/YouTube/DG)
- ✅ **3 Brand greške** ispravljene (Croatia → Hidra)
- ✅ **HR-only troškovi** (očišćeno od worldwide)
- ✅ **10% Threshold** za demographics (eliminira noise)
- ✅ **Smart Range Detection** (kampanja 95% u 25-34 = "25-34", NE "18-65+")

### Demographics Logic:
- Samo segmenti s ≥10% troška prikazani
- '+ UNK' oznaka za kampanje s troškom u 'Unknown' kategoriji
- Strict filtering (odabir '18-24' prikazuje SAMO kampanje koje targetiraju 18-24)

---

## 🎯 USE CASES

### 1. Benchmark Analiza
- Postavi ciljani budžet (npr. €5000)
- Sustav prikazuje kampanje ±10% od ciljanog iznosa
- Usporedi CPM, Reach, Impressions

### 2. Demographic Insights
- Filtriraj po Age Group i Gender
- Vidi detaljnu raspodjelu po godinama (Noise Analysis)
- Identificiraj targeting noise (<10% segments)

### 3. Brand Performance
- Filtriraj po brendu
- Vidi Top 10 brandova po trošku
- Usporedi performance metrike

### 4. Format Optimization
- Filtriraj po Ad Format
- Usporedi CPM između YouTube/Display/DG
- Identificiraj optimalne formate

---

## 🛠️ TEHNIČKI STACK

- **Python 3.11+**
- **Streamlit** - Dashboard framework
- **Pandas** - Data processing
- **Plotly** - Visualizacije
- **NumPy** - Numeric operations

---

## 📞 SUPPORT

Za pitanja i feedback, kontaktiraj development tim.

---

## 📄 VERZIJA

**Master Version 1.0** | Released: 2026-02-11

---

**🇭🇷 Razvijeno za hrvatsko tržište | Production-Ready**
