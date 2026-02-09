# ✅ FINAL TEST CHECKLIST - METRIC SELECTOR

## 🎯 PRE-LAUNCH PROVJERA

Prije pokretanja aplikacije, provjeri:

- [ ] `hub_app.py` je ažuriran (najnovija verzija)
- [ ] `ads_estimation_hub_HR_PROTOTYPE_V4_STANDARDIZED.csv` postoji
- [ ] `data - v3/age - gender - v3/campaign age - gender - version 3.csv` postoji
- [ ] Streamlit je instaliran: `pip install streamlit pandas numpy plotly`

---

## 🚀 POKRETANJE

```bash
cd "C:\Users\mturkalj\OneDrive - CroWP\Desktop\abandon all hope\ads-estimation-hub"
streamlit run hub_app.py
```

**Očekivano:**
- Aplikacija se otvara u browseru (http://localhost:8501)
- Sidebar prikazuje: "🔄 Calculating actual demographics from data..."
- Nakon par sekundi: "✅ Demographics corrected!"

---

## ✅ TEST 1: METRIC SELECTOR VIDLJIVOST

**Provjeri:**
1. Sidebar ima sekciju **"📊 Odaberi Vidljive Metrike"**
2. Dropdown "Odabrane Metrike:" je vidljiv
3. Default metrike su odabrane:
   - ☑ Cost (EUR)
   - ☑ Impressions
   - ☑ CPM (EUR)
   - ☑ Peak Reach
4. Ispod piše: "✅ Odabrano: 4 metrika"
5. Dva buttona: [🎯 Osnovne] [📈 Sve]

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 2: DODAVANJE METRIKA

**Koraci:**
1. Klikni na dropdown "Odabrane Metrike:"
2. Odaberi dodatne metrike:
   - ☑ Clicks
   - ☑ CTR (%)
3. Zatvorim dropdown (klikni izvan)

**Očekivano:**
- Sidebar piše: "✅ Odabrano: 6 metrika"
- Iznad tablice prikazuje: **Cost (EUR) · Impressions · CPM (EUR) · Peak Reach · Clicks · CTR (%)**
- Tablica sada ima **7 stupaca** (Campaign Name + 6 metrika)
- Clicks je formatiran s tisućama: "12,345"
- CTR je formatiran s postotkom: "2.45%"

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 3: UKLANJANJE METRIKA

**Koraci:**
1. Klikni na dropdown "Odabrane Metrike:"
2. Ukloni "Peak Reach" (klikni X pored toga)
3. Zatvorim dropdown

**Očekivano:**
- Sidebar piše: "✅ Odabrano: 5 metrika"
- Iznad tablice VIŠE NEMA **Peak Reach**
- Tablica sada ima **6 stupaca** (Campaign Name + 5 metrika)
- Peak Reach kolona je uklonjena iz tablice

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 4: SVE DOSTUPNE METRIKE

**Koraci:**
1. Klikni na dropdown "Odabrane Metrike:"
2. Ručno odaberi SVE 13 metrika:
   - Cost (EUR)
   - Impressions
   - CPM (EUR)
   - Peak Reach
   - Clicks
   - CTR (%)
   - Avg. CPC (EUR)
   - Avg. CPM (EUR)
   - TrueView Views
   - TrueView CPV (EUR)
   - Conversions
   - Conv. Rate (%)
   - Cost/Conv. (EUR)

**Očekivano:**
- Sidebar piše: "✅ Odabrano: 13 metrika"
- Tablica prikazuje **14 stupaca** (Campaign Name + 13 metrika)
- Scrollanje horizontalno radi
- Sve metrike su pravilno formatirane:
  - EUR metrike: €1,234.56
  - Postotci: 2.45%
  - Brojevi: 1,234,567

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 5: FORMATIRANJE METRIKA

**Provjeri svaku metriku:**

| Metrika | Format | Primjer | Status |
|---------|--------|---------|--------|
| Cost (EUR) | €X,XXX.XX | €11,234.56 | [ ] PASS |
| Impressions | X,XXX,XXX | 7,060,434 | [ ] PASS |
| CPM (EUR) | €X.XX | €1.59 | [ ] PASS |
| Peak Reach | X,XXX,XXX | 1,267,375 | [ ] PASS |
| Clicks | XX,XXX | 23,456 | [ ] PASS |
| CTR (%) | X.XX% | 0.33% | [ ] PASS |
| Avg. CPC (EUR) | €X.XX | €0.48 | [ ] PASS |
| Avg. CPM (EUR) | €X.XX | €1.59 | [ ] PASS |
| TrueView Views | XX,XXX | 45,678 | [ ] PASS |
| TrueView CPV (EUR) | €X.XX | €0.05 | [ ] PASS |
| Conversions | XX.XX | 123.45 | [ ] PASS |
| Conv. Rate (%) | X.XX% | 3.25% | [ ] PASS |
| Cost/Conv. (EUR) | €XX.XX | €25.50 | [ ] PASS |

---

## ✅ TEST 6: KOMBINACIJA S FILTERIMA

**Koraci:**
1. **Filteri:**
   - Brand: Nivea
   - Ad Format: YouTube Bumper
   - Age Group: 25-34
   - Gender: Female

2. **Metrike:**
   - Cost (EUR)
   - Impressions
   - Clicks
   - CTR (%)

**Očekivano:**
- Filteri rade zajedno s metric selectorom
- Tablica prikazuje samo Nivea Bumper kampanje za žene 25-34
- Prikazuje samo 5 stupaca (Campaign Name + 4 odabrane metrike)
- Weighted Average CPM u footeru je točan za filtriranu selekciju

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 7: PRESET BUTTONI

### **Test 7a: 🎯 Osnovne Button**

**Koraci:**
1. Odaberi neke custom metrike (npr. dodaj Clicks, CTR)
2. Klikni button **"🎯 Osnovne"**

**Očekivano:**
- App se restarta
- Vraća na default metrike: Cost, Impressions, CPM, Peak Reach
- Tablica prikazuje 5 stupaca

**Status:** [ ] PASS / [ ] FAIL

---

### **Test 7b: 📈 Sve Button**

**Koraci:**
1. Klikni button **"📈 Sve"**

**Očekivano:**
- App se restarta
- SVE 13 metrika su odabrane
- Tablica prikazuje 14 stupaca

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 8: NULA VRIJEDNOSTI

**Provjeri:**
- Kampanje koje nemaju podatke za neke metrike
- Npr. Display kampanje nemaju TrueView Views

**Očekivano:**
- EUR metrike s 0: **€0.00**
- Postotci s 0: **0.00%**
- Brojevi s 0: **0**
- Decimale s 0: **0.00**

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 9: SORTIRANJE

**Koraci:**
1. Odaberi metrike: Cost, Impressions, CPM, Clicks
2. Klikni na header kolone "Clicks"

**Očekivano:**
- Tablica se sortira po Clicks (ascending ili descending)
- Može sortirati po bilo kojoj koloni

**Status:** [ ] PASS / [ ] FAIL

---

## ✅ TEST 10: RESPONSIVENESS

**Provjeri:**
1. Smanjim browser window
2. Sidebar se automatski zatvara (hamburger menu)
3. Tablica ostaje scrollable

**Očekivano:**
- App radi i na malim ekranima
- Tablica se ne lomi
- Metric selector i dalje dostupan u sidebaru

**Status:** [ ] PASS / [ ] FAIL

---

## 🎯 FINALNA PROVJERA

**Ukupno testova:** 10
**Prošlo:** [ ] / 10
**Nije prošlo:** [ ] / 10

---

## 📊 REPORT

**Datum testiranja:** _______________
**Tester:** _______________

**Kritični bugovi:**
- [ ] Nema kritičnih bugova
- [ ] Bug 1: _______________
- [ ] Bug 2: _______________

**Manje greške:**
- [ ] Nema manjih grešaka
- [ ] Greška 1: _______________
- [ ] Greška 2: _______________

**Status:**
- [ ] ✅ READY FOR PRODUCTION
- [ ] ⚠️ NEEDS FIXES
- [ ] ❌ NOT READY

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] Svi testovi prolaze
- [ ] Dokumentacija kompletna (METRIC_SELECTOR_GUIDE.md)
- [ ] CSV datoteke dostupne
- [ ] Dependencies instalirani
- [ ] Performance je prihvatljiv (<5s load time)
- [ ] UI je intuitivan
- [ ] Nema console errors

**READY TO LAUNCH:** [ ] YES / [ ] NO

---

**Testiranje završeno!** 🎉

**Verzija:** 2.1.0
**Datum:** 2026-02-09
