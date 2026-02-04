# ADS ESTIMATION HUB

## 📋 OSNOVNE INFORMACIJE

**Naziv projekta:** Ads Estimation HUB
**Tehnologije:** Next.js (TypeScript) + Tailwind CSS
**Jezik komunikacije:** Hrvatski (isključivo)
**Asistent:** Claude - Google Ads Specialist

---

## 🎯 CILJ PROJEKTA

Razvoj alata za procjenu i analizu Google Ads kampanja specifično za hrvatsko tržište, s naprednim filterima, normalizacijom podataka i standardizacijom nomenclature.

---

## 📂 STRUKTURA PODATAKA

### Izvori podataka (data/raw/)
1. **Campaign Metrics Data** (po kvartalima)
   - Kolone: Campaign ID, Campaign, Format, Clicks, Impressions, CTR, Avg. CPC, Avg. CPM, TrueView views, Cost, Unique users, itd.

2. **Age Gender Data**
   - Kolone: Campaign ID, Campaign, Campaign type, Age, Gender, Cost

3. **Interest Audience Segments**
   - Kolone: Campaign ID, Campaign, Campaign type, Audience segment, Cost

### Ključ za spajanje
- **Campaign ID** - primarni ključ za povezivanje sva tri izvora

---

## 🔍 PRAVILA FILTRIRANJA

### ✅ MARKET FILTER - Samo Hrvatska (HR)
Zadržavamo isključivo kampanje za hrvatsko tržište.

### ❌ EXCLUSION LIST (Market)
Odmah odbaciti sve kampanje koje sadrže:
- `SI-SL` (Slovenija)
- `RS-SR` (Srbija)
- `ME-ME` (Crna Gora)
- `SLO` ili `Slovenia`
- `BiH` ili `Bosna`
- `Srbija`
- `Mison` (kampanje za druge regije)
- `Elgrad` (nedefinirano tržište)
- `AlwaysOnSLO`
- `AlwaysOnBiH`

### 🚫 EXCLUSION LIST (Worldwide Bug)
Eksplicitno ignorirati ove tri McDonald's kampanje jer su bile Worldwide:
1. `McDonald's IceCoffe June - August 2025 (YT) - CPV`
2. `McDonald's Stripsi June - July 2025 (YT) - Bumper`
3. `McDonald's Stripsi June - July 2025 (YT) - CPV`

---

## 🔧 LOGIKA SPAJANJA I NORMALIZACIJE

### Agregacija po kvartalima
- **Campaign ID** = ključ
- **Spend & Impressions** = zbroj (SUM)
- **Reach** = maksimalna (PEAK) vrijednost

### Data Sanitizer
- **Excel Date Bug:** `'2.ožu'` → `2.03`
- **Valute:** ukloniti simbole `€`, `HRK`
- **Encoding:** UTF-8 obrada za hrvatske znakove (č, ć, š, ž, đ)

---

## 📝 NOMENKLATURA (standardized_name)

### Format standardiziranog imena:
```
[BRAND] | [TYPE] | [PLACEMENTS] | [DEMO] | [LANGUAGE] | [MARKET] | [BIDDING]
```

### Komponente:

#### [TYPE]
- `YouTube` - Video kampanje (TrueView, Bumper, Shorts)
- `Demand Gen` - DG kampanje
- `PMax` - Performance Max
- `Display` - GDN

#### [PLACEMENTS]
- `In-Stream` / `Bumper` / `Shorts` / `In-Feed` / `GDN`

#### [DEMO]
- Izvuci iz Age Gender podataka: `18-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65+`
- Gender: `M` / `F` / `All`

#### [LANGUAGE]
- **Kaufland i slični multi-market brendovi:** prepoznaj `Polish`, `German`, `Hungarian` itd.
- **Ako nema specifičnog jezika:** koristi `Local` (= Hrvatski)

#### [MARKET]
- `HR` (Hrvatska)

#### [BIDDING]
- `CPV` / `CPM` / `CPC` / `CPE`

---

## 🎨 STILSKE SMJERNICE

- **Clean Code:** TypeScript strict mode
- **UI Framework:** Tailwind CSS
- **Komponente:** Modularno, reusable
- **Naming:** Deskriptivno, na engleskom (kod), na hrvatskom (UI/UX tekstovi)
- **Comments:** Hrvatski, objašnjavaju business logiku

---

## 📊 PLANIRANA FUNKCIONALNOST

1. **Import & Processing**
   - Upload CSV/XLSX datoteka
   - Automatsko filtriranje i čišćenje
   - Spajanje po Campaign ID

2. **Dashboard**
   - Pregled kampanja po brendovima
   - Vizualizacija troškova, reach-a, impressions-a
   - Filteri po datumu, brendu, tipu kampanje

3. **Export & Reporting**
   - Generiraj izvještaj (PDF/Excel)
   - Standardizirane nomenklature
   - Agregacija po kvartalima

---

## 🚀 ROADMAP

- [x] Inicijalizacija projekta
- [x] Analiza podataka i strukture
- [ ] Kreiranje data processing pipelines
- [ ] UI/UX dizajn
- [ ] Implementacija filtera
- [ ] Testiranje i debug
- [ ] Deploy

---

**Zadnje ažurirano:** 2026-02-04
**Verzija:** 0.1.0 - Initial Analysis
