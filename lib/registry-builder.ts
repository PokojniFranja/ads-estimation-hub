#!/usr/bin/env node
/**
 * Campaign Registry Builder
 *
 * Spaja podatke iz:
 * - data/raw/campaign_metrics/2025_metrics.csv (Campaign ID + Original Name)
 * - data/raw/campaign_durations.csv (Original Name + Start/End Date)
 *
 * Generira: data/campaign_registry.csv
 */

import * as fs from 'fs';
import * as path from 'path';
import Papa from 'papaparse';

// Tipovi
interface MetricsCampaign {
  'Campaign ID': string;
  'Campaign': string;
  'Ad format': string;
}

interface DurationEntry {
  'Campaign name': string;
  'Campaign start': string;
  'Campaign end': string;
}

interface RegistryEntry {
  campaignId: string;
  originalName: string;
  standardizedName: string;
  startDate: string;
  endDate: string;
  isAlwaysOn: boolean;
}

// Putanje
const METRICS_FILE = path.join(process.cwd(), 'data/raw/campaign_metrics/2025_metrics.csv');
const DURATIONS_FILE = path.join(process.cwd(), 'data/raw/campaign_duration_new.csv');
const OUTPUT_FILE = path.join(process.cwd(), 'data/campaign_registry.csv');

// Always On default datumi
const ALWAYS_ON_START = '01.01.2025.';
const ALWAYS_ON_END = '31.12.2025.';

/**
 * Normalizira naziv kampanje za fuzzy matching
 * - Lowercase
 * - Uklanja razmake, underscore, dash, slash
 * - Uklanja posebne znakove
 */
function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[\s_\-\/\\]+/g, '') // Ukloni razmake, _, -, /, \
    .replace(/[(){}[\]]/g, '') // Ukloni zagrade
    .replace(/[.,;:'"]/g, '') // Ukloni interpunkciju
    .trim();
}

/**
 * Ekstrahira datume iz imena kampanje (npr. "Jan25_Feb25" -> start: 01.01.2025., end: 28.02.2025.)
 */
function extractDatesFromCampaignName(name: string): { start: string; end: string } | null {
  // Pattern: MonYY_MonYY (npr. Jan25_Feb25, Sep25_Oct25)
  const datePattern = /([A-Z][a-z]{2})(\d{2})_([A-Z][a-z]{2})(\d{2})/i;
  const match = name.match(datePattern);

  if (!match) return null;

  const [, startMonth, startYear, endMonth, endYear] = match;

  // Mapiranje mjeseci na brojeve
  const monthMap: { [key: string]: number } = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
  };

  const startMonthNum = monthMap[startMonth.toLowerCase()];
  const endMonthNum = monthMap[endMonth.toLowerCase()];

  if (!startMonthNum || !endMonthNum) return null;

  const fullStartYear = 2000 + parseInt(startYear);
  const fullEndYear = 2000 + parseInt(endYear);

  // Prvi dan prvog mjeseca
  const startDate = new Date(fullStartYear, startMonthNum - 1, 1);

  // Zadnji dan drugog mjeseca
  const endDate = new Date(fullEndYear, endMonthNum, 0); // 0 = zadnji dan prethodnog mjeseca

  // Format: DD.MM.YYYY.
  const formatDate = (date: Date) => {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}.`;
  };

  return {
    start: formatDate(startDate),
    end: formatDate(endDate)
  };
}

/**
 * Konvertira datum iz DD/MM/YYYY u DD.MM.YYYY. format
 */
function formatDate(date: string): string {
  if (!date) return '';
  // Iz "13/01/2025" u "13.01.2025."
  const parts = date.split('/');
  if (parts.length === 3) {
    return `${parts[0]}.${parts[1]}.${parts[2]}.`;
  }
  return date;
}

/**
 * Generira standardizirano ime prema taksonomiji:
 * [BRAND] | [TYPE] | [PLACEMENTS] | [DEMO] | [LANGUAGE] | [MARKET] | [BIDDING]
 */
function generateStandardizedName(originalName: string, adFormat: string): string {
  // Placeholder - za sada vraćam Original Name
  // TODO: Implementirati puno parsiranje prema taksonomiji

  // Case-insensitive matching - konvertiraj u lowercase za provjeru
  const lowerName = originalName.toLowerCase();

  // Pokušaj ekstrakcije brand-a (case-insensitive)
  let brand = 'Unknown';

  // ═══════════════════════════════════════════════════════════════════════
  // ELECTRONICS & APPLIANCES
  // ═══════════════════════════════════════════════════════════════════════

  // LG
  if (lowerName.startsWith('hr_') && (lowerName.includes('_oth_') || lowerName.includes('_he_') || lowerName.includes('_ha_'))) brand = 'LG';
  else if (lowerName.includes('lg.com') || lowerName.includes('elipso.hr')) brand = 'LG';

  // Bosch
  // NAPOMENA: 'detox' je specifično za ovaj dataset (Bosch Detox kampanja)
  else if (lowerName.includes('bosch') || lowerName.includes('mum6') || lowerName.includes('mum5') ||
           lowerName.includes('_mda_') || lowerName.includes('_sda_') ||
           (lowerName.includes('detox') && lowerName.includes('homeappliances'))) brand = 'Bosch';

  // Philips
  // VAŽNO: NE koristiti 'demand gen' kao marker - to je TYPE!
  // Markeri: Philips ime, OMD kodovi, Versuni, PH sufiks, specifični proizvodi
  else if (lowerName.includes('philips') ||
           // OMD Agency kodovi
           lowerName.includes('omd_hr-hr_gb_') || lowerName.includes('omd_ba-bs_gb_') ||
           lowerName.includes('omd_hr-hr_all_') || lowerName.includes('omd_hr-hr_ohc_') ||
           // Personal Care proizvodi
           lowerName.includes('oneblade') || lowerName.includes('sonicare') || lowerName.includes('lumea') ||
           lowerName.includes('avent') || lowerName.includes('_mcc_') || lowerName.includes('_ohc_') ||
           // Domestic Appliances - Versuni
           lowerName.includes('versuni') ||
           // Philips Domestic Appliances - specifični proizvodi
           lowerName.includes('airfryer') || lowerName.includes('unlimited') ||
           lowerName.includes('indoorcleaning') || lowerName.includes('vacuumcleaners') ||
           lowerName.includes('laundrycare') || lowerName.includes('washingmachines') ||
           lowerName.includes('cookingrange') ||
           // Philips PH sufiks ili KeyVisuals/Webshop kampanje
           lowerName.endsWith(' - ph') || lowerName.includes('keyvisuals - ph') ||
           (lowerName.includes('croatia') && (lowerName.includes('keyvisuals') || lowerName.includes('webshop')))) brand = 'Philips';

  // Automotive
  else if (lowerName.includes('škoda') || lowerName.includes('skoda')) brand = 'Škoda';
  else if (lowerName.includes('volkswagen') || lowerName.includes('vw ')) brand = 'Volkswagen';
  else if (lowerName.includes('audi')) brand = 'Audi';
  else if (lowerName.includes('seat')) brand = 'Seat';
  else if (lowerName.includes('cupra')) brand = 'Cupra';
  else if (lowerName.includes('porsche')) brand = 'Porsche';
  else if (lowerName.includes('nissan')) brand = 'Nissan';

  // Food & Beverage
  else if (lowerName.includes('mcdonald')) brand = 'McDonald\'s';
  else if (lowerName.includes('kaufland')) brand = 'Kaufland';
  else if (lowerName.includes('rio mare')) brand = 'Rio Mare';
  else if (lowerName.includes('oetker')) brand = 'Dr. Oetker';
  else if (lowerName.includes('ahmad')) brand = 'Ahmad Tea';
  else if (lowerName.includes('loacker')) brand = 'Loacker';
  else if (lowerName.includes('zott')) brand = 'Zott';

  // Henkel Group
  else if (lowerName.includes('bref')) brand = 'Bref';
  else if (lowerName.includes('schauma')) brand = 'Schauma';
  else if (lowerName.includes('syoss')) brand = 'Syoss';
  else if (lowerName.includes('gliss')) brand = 'Gliss';
  else if (lowerName.includes('persil')) brand = 'Persil';
  else if (lowerName.includes('perwoll')) brand = 'Perwoll';
  else if (lowerName.includes('somat')) brand = 'Somat';
  else if (lowerName.includes('weisser riese') || lowerName.includes('weisserriese')) brand = 'Weisser Riese';

  // Schwarzkopf
  else if (lowerName.includes('palette')) brand = 'Palette';
  else if (lowerName.includes('taft')) brand = 'Taft';
  else if (lowerName.includes('got2b')) brand = 'Got2b';

  // Reckitt
  else if (lowerName.includes('finish')) brand = 'Finish';

  // ═══════════════════════════════════════════════════════════════════════
  // BEIERSDORF GROUP
  // ═══════════════════════════════════════════════════════════════════════

  // Nivea - različite kategorije
  else if (lowerName.includes('nivea') || lowerName.includes('_nfc_') || lowerName.includes('_nbd_') ||
           lowerName.includes('_nme_') || lowerName.includes('_ndo_') || lowerName.includes('_nfl_') ||
           lowerName.includes('_nsu_') || lowerName.includes('_ncr_') || lowerName.includes('_niv_')) brand = 'Nivea';

  // Eucerin - dermokozmetika
  // Kodovi: ESU (Eucerin Sun), EFC (Eucerin Face Care), EBD (Eucerin Body), ECN (Eucerin)
  else if (lowerName.includes('eucerin') || lowerName.includes('_esu_') ||
           lowerName.includes('_efc_') || lowerName.includes('_ebd_') || lowerName.includes('_ecn_')) brand = 'Eucerin';

  // Bolton Group
  else if (lowerName.includes('borotalco')) brand = 'Borotalco';

  // Barilla (tjestenine, umaci)
  else if (lowerName.includes('barilla') || lowerName.includes('_bar_') || lowerName.includes('_baio_') ||
           lowerName.includes('_mul_') || lowerName.includes('_gra_') || lowerName.includes('_pess_')) brand = 'Barilla';

  // Logistics & Delivery
  else if (lowerName.includes('boxnow')) brand = 'BoxNow';

  // ═══════════════════════════════════════════════════════════════════════
  // PHARMA & HEALTH
  // ═══════════════════════════════════════════════════════════════════════

  else if (lowerName.includes('belupo') || lowerName.includes('rinil')) brand = 'Belupo';
  else if (lowerName.includes('jgl') || lowerName.includes('muzej farmacije')) brand = 'JGL';
  else if (lowerName.includes('reflustat')) brand = 'Reflustat';
  else if (lowerName.includes('meralys')) brand = 'Meralys';
  else if (lowerName.includes('prolife')) brand = 'Prolife';
  else if (lowerName.includes('vizols')) brand = 'Vizols';
  else if (lowerName.includes('lactogyn')) brand = 'Lactogyn';
  else if (lowerName.includes('fungilac')) brand = 'Fungilac';
  else if (lowerName.includes('hidra')) brand = 'Hidra';

  // ═══════════════════════════════════════════════════════════════════════
  // PERSONAL CARE & HYGIENE
  // ═══════════════════════════════════════════════════════════════════════

  else if (lowerName.includes('bic')) brand = 'BIC';

  // ═══════════════════════════════════════════════════════════════════════
  // OSTALO
  // ═══════════════════════════════════════════════════════════════════════

  else if (lowerName.includes('bison')) brand = 'Bison';
  else if (lowerName.includes('saponia')) brand = 'Saponia';
  else if (lowerName.includes('uhu')) brand = 'UHU';
  else if (lowerName.includes('energycom')) brand = 'Energycom';

  // TYPE (iz ad format ili naziva)
  let type = 'YouTube';
  if (originalName.includes('Demand Gen') || originalName.includes('DG')) type = 'Demand Gen';
  else if (originalName.includes('PMax')) type = 'PMax';
  else if (originalName.includes('Display') || originalName.includes('GDN')) type = 'Display';

  // PLACEMENTS (iz ad format)
  let placements = 'Mixed';
  if (adFormat.includes('Skippable in-stream')) placements = 'In-Stream';
  else if (adFormat.includes('Non-skippable in-stream')) placements = 'In-Stream';
  else if (adFormat.includes('Bumper')) placements = 'Bumper';
  else if (adFormat.includes('Shorts')) placements = 'Shorts';
  else if (adFormat.includes('In-feed')) placements = 'In-Feed';

  // MARKET
  const market = 'HR';

  // BIDDING (iz naziva)
  let bidding = 'CPM';
  if (originalName.includes('CPV')) bidding = 'CPV';
  else if (originalName.includes('CPC')) bidding = 'CPC';
  else if (originalName.includes('CPE')) bidding = 'CPE';

  // DEMO & LANGUAGE - TODO: trebaju dodatni podaci
  const demo = 'All';
  const language = 'Local';

  return `${brand} | ${type} | ${placements} | ${demo} | ${language} | ${market} | ${bidding}`;
}

/**
 * Učitava metrics podatke
 */
async function loadMetrics(): Promise<Map<string, { id: string; adFormat: string }>> {
  return new Promise((resolve, reject) => {
    const campaigns = new Map<string, { id: string; adFormat: string }>();

    Papa.parse(fs.createReadStream(METRICS_FILE), {
      header: true,
      delimiter: '\t', // Metrics fajl koristi TAB separator
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data as MetricsCampaign[];

        for (const row of data) {
          const campaignName = row['Campaign']?.trim();
          const campaignId = row['Campaign ID']?.toString().trim();
          const adFormat = row['Ad format']?.trim() || '';

          if (campaignName && campaignId) {
            // Uzimamo prvi format koji nađemo (kasnije ćemo agregirati)
            if (!campaigns.has(campaignName)) {
              campaigns.set(campaignName, { id: campaignId, adFormat });
            }
          }
        }

        console.log(`✓ Učitano ${campaigns.size} jedinstvenih kampanja iz metrics fajla`);
        resolve(campaigns);
      },
      error: (error) => reject(error)
    });
  });
}

/**
 * Učitava durations podatke (sa exact i fuzzy matching mapama)
 */
async function loadDurations(): Promise<{
  exact: Map<string, { start: string; end: string }>;
  fuzzy: Map<string, { originalName: string; start: string; end: string }>;
}> {
  return new Promise((resolve, reject) => {
    const exactMap = new Map<string, { start: string; end: string }>();
    const fuzzyMap = new Map<string, { originalName: string; start: string; end: string }>();

    Papa.parse(fs.createReadStream(DURATIONS_FILE), {
      header: true,
      delimiter: ';', // Durations fajl koristi semicolon separator
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data as DurationEntry[];

        for (const row of data) {
          const campaignName = row['Campaign name']?.trim();
          const startDate = row['Campaign start']?.trim();
          const endDate = row['Campaign end']?.trim();

          if (campaignName && startDate && endDate) {
            const dates = {
              start: formatDate(startDate),
              end: formatDate(endDate)
            };

            // Exact match map
            exactMap.set(campaignName, dates);

            // Fuzzy match map (normalizirani naziv)
            const normalizedName = normalizeName(campaignName);
            fuzzyMap.set(normalizedName, {
              originalName: campaignName,
              ...dates
            });
          }
        }

        console.log(`✓ Učitano ${exactMap.size} kampanja s datumima iz durations fajla`);
        resolve({ exact: exactMap, fuzzy: fuzzyMap });
      },
      error: (error) => reject(error)
    });
  });
}

/**
 * Generira registry
 */
async function buildRegistry() {
  console.log('🚀 Pokrećem Campaign Registry Builder...\n');

  // 1. Učitaj metrics
  const metricsMap = await loadMetrics();

  // 2. Učitaj durations (exact i fuzzy)
  const { exact: exactDurations, fuzzy: fuzzyDurations } = await loadDurations();

  // 3. Generiraj registry sa exact, fuzzy i extracted matchingom
  const registry: RegistryEntry[] = [];
  const unmatchedCampaigns: string[] = [];
  let exactMatches = 0;
  let fuzzyMatches = 0;
  let extractedMatches = 0;

  for (const [campaignName, { id, adFormat }] of metricsMap.entries()) {
    let duration: { start: string; end: string } | undefined;
    let matchType = '';

    // Prvo pokušaj exact match
    duration = exactDurations.get(campaignName);
    if (duration) {
      exactMatches++;
      matchType = 'exact';
    } else {
      // Ako nema exact match, pokušaj fuzzy match
      const normalizedName = normalizeName(campaignName);
      const fuzzyMatch = fuzzyDurations.get(normalizedName);
      if (fuzzyMatch) {
        duration = { start: fuzzyMatch.start, end: fuzzyMatch.end };
        fuzzyMatches++;
        matchType = 'fuzzy';
      } else {
        // Ako ni fuzzy ne uspije, pokušaj izvući datume iz imena kampanje
        const extractedDates = extractDatesFromCampaignName(campaignName);
        if (extractedDates) {
          duration = extractedDates;
          extractedMatches++;
          matchType = 'extracted';
        }
      }
    }

    const entry: RegistryEntry = {
      campaignId: id,
      originalName: campaignName,
      standardizedName: generateStandardizedName(campaignName, adFormat),
      startDate: duration ? duration.start : ALWAYS_ON_START,
      endDate: duration ? duration.end : ALWAYS_ON_END,
      isAlwaysOn: !duration
    };

    registry.push(entry);

    if (!duration) {
      unmatchedCampaigns.push(campaignName);
    }
  }

  const totalMatched = exactMatches + fuzzyMatches + extractedMatches;

  console.log(`\n✓ Generirano ${registry.length} registarskih zapisa`);
  console.log(`✓ Exact matches (iz durations): ${exactMatches}`);
  console.log(`✓ Fuzzy matches (iz durations): ${fuzzyMatches}`);
  console.log(`✓ Extracted matches (iz imena kampanja): ${extractedMatches}`);
  console.log(`✓ Ukupno uparenih: ${totalMatched} (${(totalMatched / registry.length * 100).toFixed(1)}%)`);
  console.log(`⚠️  Always On kampanja: ${unmatchedCampaigns.length} (${(unmatchedCampaigns.length / registry.length * 100).toFixed(1)}%)\n`);

  // 4. Spremi u CSV
  const csvContent = [
    'Campaign ID,Original Name,Standardized Name,Start Date,End Date',
    ...registry.map(entry =>
      `${entry.campaignId},"${entry.originalName}","${entry.standardizedName}",${entry.startDate},${entry.endDate}`
    )
  ].join('\n');

  fs.writeFileSync(OUTPUT_FILE, csvContent, 'utf-8');
  console.log(`✓ Spremljeno u: ${OUTPUT_FILE}\n`);

  // 5. Izvještaj o neuparerim kampanjama
  if (unmatchedCampaigns.length > 0) {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📋 IZVJEŠTAJ - Kampanje bez datuma (Always On):');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

    unmatchedCampaigns.forEach((name, index) => {
      console.log(`${index + 1}. ${name}`);
      console.log(`   └─ Označeno kao: Always On (${ALWAYS_ON_START} - ${ALWAYS_ON_END})\n`);
    });

    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  } else {
    console.log('✓ Sve kampanje su uspješno uparene!\n');
  }
}

// Pokreni
buildRegistry().catch(error => {
  console.error('❌ Greška:', error);
  process.exit(1);
});
