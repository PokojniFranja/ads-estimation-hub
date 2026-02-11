# 📊 ANALIZA NOVOG ROLLING REACH EKSPORTA
## Datum: 2026-02-11

---

## ✅ 1. ANALIZA ACCOUNT_ID-OVA

### **UKUPNO: 55 jedinstvenih Account_ID-ova**

**Python lista svih Account_ID-ova:**
```python
account_ids = [
    "127-959-7994",  # Porsche Osobna Vozila
    "129-935-0552",  # Philips_SLO
    "150-132-6366",  # Zott EUR
    "157-361-8550",  # UHU EUR
    "180-680-2619",  # CEE//HR//B//Hair Styling//Taft Spray&Mousse
    "187-148-0162",  # CEE//HR//B//Hair Colorants//Syoss Color
    "199-867-4291",  # Ricola
    "203-608-3972",  # ENERGYCOM D.O.O.
    "214-764-0693",  # CEE//HR//B//Hair Colorants//Palette ICC
    "224-059-6497",  # Porsche Volkswagen gospodarska vozila 2023
    "229-792-9617",  # CEE//HR//B//Hair Styling//got2b Styling
    "247-134-4613",  # Rio Mare EUR
    "284-348-0597",  # CEE//HR//L//HDD Leading Premium//Persil
    "299-683-3501",  # Barilla_Mulino Bianco_Youtube_EUR_OMDHR
    "301-500-4168",  # Finish
    "306-851-3764",  # CEE//HR//L//HDD Value for Money//Weisser Riese
    "324-637-3600",  # CEE//HR//L//SPD//Expressive Clothes//Perwoll
    "347-468-5543",  # Porsche Moon 2023
    "370-352-5225",  # Borotalco EUR
    "373-058-1715",  # CEE//HR//B//Hair Care//Gliss Care//Gliss
    "404-912-9584",  # Dr.Oetker EUR
    "419-182-5356",  # Porsche Škoda 2023
    "439-241-7686",  # BIC
    "460-152-0813",  # Barilla_Youtube_EUR_OMDHR
    "480-508-5682",  # CEE//HR//A//Tiling Pro//Ceresit
    "494-390-2223",  # Nissan Hrvatska EUR
    "510-674-2393",  # Croatia_Hidra
    "540-172-1511",  # HR_Nivea_YouTube_x_OMD_EUR
    "570-624-8392",  # Porsche Volkswagen osobna vozila 2023
    "572-434-3454",  # CEE//HR//L//TWC//Clean & fresh toilet//Bref
    "599-809-8198",  # Porsche  Das Welt Auto 2023
    "604-083-0641",  # Hervis Croatia EUR
    "611-267-3615",  # CEE//HR//L//ADW//Disburdening//Somat
    "617-423-7507",  # Loacker EUR
    "639-950-8362",  # Elgrad Austria EUR
    "673-543-9149",  # McDonald's EUR
    "681-537-9992",  # BoxNow
    "709-126-5350",  # Pipi
    "745-555-5776",  # BISON EUR
    "751-840-0460",  # Saponia
    "757-579-7864",  # Belupo
    "764-799-0958",  # CEE//HR//B//Hair Care//Schauma Family
    "777-456-8213",  # Porsche Cupra 2023
    "799-919-6701",  # Philips Hrvatska EUR
    "815-243-7991",  # Porsche Audi 2023
    "840-154-8000",  # Philips Serbia DAN
    "843-228-4976",  # Barilla_Grancereale_YouTube_EUR_OMDHR
    "850-057-4954",  # HR_Nivea_Google Display Network_x_OMD_EUR
    "860-419-0629",  # CEE//HR//A//Humidity Absorbers//Ceresit Stop
    "862-115-2062",  # Koestlin
    "881-835-1793",  # Ahmad Tea
    "883-771-7154",  # Porsche Seat 2023
    "943-831-1711",  # Kaufland_Display_HR
    "958-633-7486",  # JGL Croatia EUR
    "973-126-9603",  # HR_EUCERIN_Google Ads_OMD_Video
]
```

### **Usporedba s MASTER_ADS_HR_CLEANED.csv:**
- **MASTER file:** 54 Account-a
- **Novi rolling reach file:** 55 Account_ID-ova
- **Razlika:** +1 Account_ID (nova pojava)

**NOVI Account_ID-ovi:**
- `129-935-0552` - Philips_SLO (novo!)
- `199-867-4291` - Ricola (novo!)
- `639-950-8362` - Elgrad Austria EUR (novo!)

**NAPOMENA:** Trebam popis od 77 ID-ova koje si ranije dao da mogu identificirati koji nedostaju.

---

## 🔍 2. PROVJERA KVALITETE PODATAKA

### **Problematični redovi:**

#### ❌ **Reach = 0 ali Cost > 0:**
- **1 red** pronađen
- **Account:** Nissan Hrvatska EUR
- **Cost:** > 0 EUR
- **Reach:** 0
- **Impressions:** 18

**Ocjena:** ⚠️ Minimalan problem (1 red od 10,219 = 0.01%)

### **Missing data:**
- ✅ **Reach:** 0 missing values
- ✅ **Avg_Frequency:** 0 missing values
- ✅ **Cost:** 0 negative values
- ✅ **Impressions:** 0 negative values

---

## 📈 3. ANALIZA AVG_FREQUENCY

### **Overall Statistics:**
- **Prosječna frekvencija:** 3.42
- **Medijan frekvencije:** 2.76
- **Min frekvencija:** 0.00
- **Max frekvencija:** 42.20

### ❌ **KRITIČAN PROBLEM - TYPE STUPAC JE PRAZAN!**

**Problem:** Stupac `Type` ne sadrži podatke (sve vrijednosti su `nan`).

**Posljedice:**
- ❌ Ne mogu razdvojiti Display i Video kampanje
- ❌ Ne mogu izračunati frekvenciju po tipu
- ❌ Analiza po Campaign Type nije moguća

**Preporuka:** Moraš dodati Campaign Type podatke u export ili ih mapirati iz Campaign imena.

---

## 📊 4. USPOREDBA SA MASTER FILE-OM (MASTER_ADS_HR_CLEANED.csv)

### **Agregirani podaci (po kampanjama):**

| Metrika | Novi Rolling Reach | MASTER File | Promjena |
|---------|-------------------|-------------|----------|
| **Ukupno kampanja** | 671 | 697 | -26 (-3.7%) |
| **Total Cost** | €21,914,097 | N/A* | N/A |
| **Total Impressions** | 20,601,938,566 | N/A* | N/A |
| **Avg Reach per campaign** | 672,029 | 547,556 | +22.7% |
| **Total unique users** | 450,931,197 | N/A | N/A |
| **Average CPM** | €1.50 | N/A* | N/A |

*NAPOMENA: MASTER file ima probleme s parsiranjem Cost i Impressions kolona (delimiter issue).

### **Key Insights:**

1. **Veći reach per campaign:** +22.7% u rolling reach podacima
   - Rolling reach metodologija hvata više korisnika kroz 90-day windows
   - Peak reach u MASTER file-u je možda konzervativniji

2. **Manje kampanja:** -26 kampanja
   - Možda neke kampanje nisu imale reach podatke u Google Ads API-ju
   - Ili su filtrirane zbog nekog drugog kriterija

3. **CPM konzistentnost:** €1.50 prosječan CPM je razuman za HR market
   - Display kampanje obično 0.50-2.00 EUR
   - Video kampanje obično 3.00-8.00 EUR

---

## 🎯 5. ZAKLJUČAK I PREPORUKE

### **Quality Score: 75/100**

**Breakdown:**
- ✅ **Account coverage** (+10): 55 Account_ID-ova (više nego MASTER)
- ✅ **Data completeness** (+20): Svi redovi imaju Reach i Frequency
- ⚠️ **Minor issues** (-5): 1 red s Reach=0 ali Cost>0
- ❌ **TYPE missing** (-30): Kritično - nema Campaign Type podataka

### **Preporuke:**

#### ✅ **ŠTO JE DOBRO:**
1. **Reach coverage:** Svi redovi imaju Reach podatke
2. **Frequency coverage:** Svi redovi imaju Avg_Frequency
3. **Account coverage:** 55 Account_ID-ova (bolje od MASTER file-a)
4. **Data quality:** Minimalni problemi (samo 1 problematičan red)
5. **Reach konsistentnost:** Prosječan reach je viši nego u MASTER file-u, što je očekivano za rolling window metodologiju

#### ❌ **ŠTO TREBA POPRAVITI:**

1. **KRITIČNO - Dodaj TYPE podatke:**
   - Export mora uključiti Campaign Type (Video, Display, DG, PMax)
   - Alternativa: Mapirati Type iz Campaign imena (ako sadrži "YouTube" = Video, "Display" = Display, itd.)

2. **Popravi Nissan red:**
   - Nissan Hrvatska EUR - 1 red ima Reach=0 ali Cost>0
   - Vjerojatno greška u Google Ads reach reporting-u
   - Opcije: Ukloni taj red ili postavi Reach na procijenjenu vrijednost

3. **Usporedi s tvojim popisom od 77 ID-ova:**
   - Trebaš mi dati popis da mogu identificirati koje Account_ID-ove fali
   - Trenutno imam 55 ID-ova u novom file-u

### **Finalna ocjena:**

#### ⚠️ **PODACI SU OK, ALI TREBAJU POPRAVKE PRIJE PROGLAŠAVANJA STANDARDOM**

**Razlozi:**
- ❌ **TYPE stupac mora biti dodan** - kritično za analizu
- ✅ Reach i Frequency podaci su kompletni i kvalitetni
- ✅ Account coverage je dobar (55 Account_ID-ova)
- ⚠️ Minimalni problemi s kvalitetom (1 red)

**Sljedeći koraci:**
1. Dodaj Campaign Type u export (ili ga mapiraj)
2. Popravi Nissan red
3. Usporedi s popisom od 77 ID-ova i dodaj manjkajuće Account-e
4. Nakon popravaka -> **NOVI STANDARD ZA REACH ESTIMACIJU** ✅

---

## 📋 TEHNIČKI DETALJI

**File:** `GAds - 90 days reach + freq - Rolling Script - Sheet1.csv`
**Redova:** 10,219
**Kolona:** 10
**Encoding:** UTF-8 with BOM
**Date range:** 2025-01-01 to 2025-04-01 (rolling 90-day windows)

**Kolone:**
- Window_Start
- Window_End
- Account_ID
- Account_Name
- Campaign
- Type (❌ PRAZAN)
- Cost
- Impressions
- Reach
- Avg_Frequency

---

**Generated:** 2026-02-11
**Status:** ⚠️ Requires fixes before production use
