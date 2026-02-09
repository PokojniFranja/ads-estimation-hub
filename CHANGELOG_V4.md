# 📋 CHANGELOG - HR Prototype V4

## Verzija 1.1.0 (2026-02-09)

### ✨ NOVE FUNKCIONALNOSTI

#### 1. **Demografski Split - KRITIČNA PROMJENA**

**Prije:**
- Jedan filter: `Target (Age/Gender)` s kombiniranim vrijednostima
- Primjer: "18-65+ | All", "25-44 | F"

**Sada:**
- **Dva odvojena filtera:**
  - **Age Range:** 18-24, 25-34, 35-44, 45-54, 55-64, 65+, 18-65+, itd.
  - **Gender:** Male, Female, All, Unknown

**Tehnička implementacija:**
```python
# Parse Target column into Age_Range and Gender
def parse_target(target_str):
    # Split by pipe |
    # Extract age part (left side)
    # Extract gender part (right side)
    # Map gender: F → Female, M → Male, M/F → All, All → All
    return (age_part, gender)
```

**Novi stupci u dataframe-u:**
- `Age_Range` - izvučena dobna skupina
- `Gender` - izvučen spol (Male/Female/All/Unknown)

---

#### 2. **Promjena Naslova**

**Prije:**
```
Ads Estimation HUB
```

**Sada:**
```
Ads Estimation Hub - HR Prototype V4
```

Prikazano na:
- Page title (tab browsera)
- Main heading (naslov aplikacije)

---

#### 3. **Budget Transparency Note**

**Dodana žuta info box napomena** ispod ključnih metrika:

```
ℹ️ Napomena o podacima: Prikazani podaci temelje se na HR-only trošku
(očišćeno od worldwide grešaka i regionalnog spenda). Svi iznosi
odražavaju isključivo hrvatski market.
```

**Styling:**
- Žuta pozadina (#fff3cd)
- Narandžasta lijeva granica (#ffc107)
- Tamno žuti tekst (#856404)
- Rounded corners

**Lokacija:** Ispod tri velike metric kartice, prije Additional Visualizations sekcije

---

## 🎯 PRIMJERI KORIŠTENJA - NOVI FILTERI

### Test Case 1: Žene 25-34 godina

**Filteri:**
- Age Range: `25-34`
- Gender: `Female`

**Što radi:**
- Prikazuje sve kampanje koje targetiraju **25-34 | F** ili **25-34 | All**
- Također uključuje kampanje s širim rangom ako uključuju 25-34 (npr. "18-65+ | F")

---

### Test Case 2: Muška publika, sve dobi

**Filteri:**
- Age Range: `Svi` (sve dobi)
- Gender: `Male`

**Što radi:**
- Prikazuje sve kampanje koje ciljaju muškarce, bez obzira na dob
- Uključuje kampanje s "M" i "All" u Gender polju

---

### Test Case 3: Specifična dobna skupina, oba spola

**Filteri:**
- Age Range: `35-44`, `45-54`
- Gender: `All`

**Što radi:**
- Prikazuje kampanje koje targetiraju 35-54 godine starosti
- Uključuje kampanje koje ciljaju oba spola (M/F ili All)

---

### Test Case 4: Kombinirano s drugim filterima

**Filteri:**
- Brand: `Nivea`
- Ad Format: `YouTube Bumper`
- Age Range: `25-34`, `35-44`
- Gender: `Female`
- Quarter: `Q2 2025`

**Što radi:**
- Nivea Bumper kampanje
- Targetirane na žene 25-44 godina
- Iz Q2 2025 perioda

---

## 🔧 TEHNIČKI DETALJI

### Gender Mapping Logic

```python
if 'M/F' in gender_upper or 'ALL' in gender_upper:
    gender = 'All'
elif 'F' in gender_upper and 'M' not in gender_upper:
    gender = 'Female'
elif 'M' in gender_upper and 'F' not in gender_upper:
    gender = 'Male'
else:
    gender = 'Unknown'
```

**Mapiranje:**
- `F` → `Female`
- `M` → `Male`
- `M/F` → `All`
- `All` → `All`
- Ostalo → `Unknown`

### Age Range Ekstrakcija

**Input primjeri:**
- "18-24 | F" → Age_Range: `18-24`
- "25-34 | M" → Age_Range: `25-34`
- "18-65+ | All" → Age_Range: `18-65+`
- "65+ | F" → Age_Range: `65+`

**Zadržava se originalni format** dobne skupine kako se pojavljuje u Target stupcu.

---

## 📊 SIDEBAR LAYOUT - NOVO

**Redoslijed filtera:**

1. 🏢 **Brand** (multiselect)
2. 📺 **Ad Format** (multiselect)
3. 👶 **Age Range** (multiselect) ← NOVO
4. 👤 **Gender** (multiselect) ← NOVO
5. 💰 **Bid Strategy** (multiselect)
6. 📅 **Quarter** (multiselect)

---

## ✅ TESTIRANJE

### Provjeri sljedeće:

1. **Age Range filter radi:**
   - Odaberi "25-34" → trebalo bi filtrirati kampanje s tom dobnom skupinom
   - Odaberi "65+" → trebalo bi filtrirati kampanje s tom dobnom skupinom

2. **Gender filter radi:**
   - Odaberi "Female" → samo ženske kampanje
   - Odaberi "Male" → samo muške kampanje
   - Odaberi "All" → kampanje koje ciljaju oba spola

3. **Kombinacija filtera:**
   - Age: "25-34" + Gender: "Female" → samo 25-34 ženske kampanje
   - Age: "35-44", "45-54" + Gender: "Male" → 35-54 muške kampanje

4. **Budget transparency note je vidljiv:**
   - Žuta info box ispod metric kartica
   - Tekst o HR-only trošku

5. **Naslov je ispravan:**
   - Page title: "Ads Estimation Hub - HR Prototype V4"
   - Main heading također

---

## 🚀 DEPLOYMENT

Ispravljeni kod je spreman za korištenje. Nema potrebe za dodatnim dependencies ili promjenama.

**Pokretanje:**
```bash
streamlit run hub_app.py
```

---

## 📌 NOTES

- **Backwards compatible:** Sve postojeće funkcionalnosti rade isto
- **Performance:** Nema dodatnog performance impacta (parsing se događa pri učitavanju)
- **Data integrity:** Ne mijenja originalne podatke, samo dodaje dva nova privremena stupca

---

**Verzija:** 1.1.0
**Datum:** 2026-02-09
**Status:** ✅ Production Ready
