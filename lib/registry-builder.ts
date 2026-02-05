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

  // Ekstrakcija osnovnih informacija iz naziva
  const parts = originalName.split('_');

  // Pokušaj ekstrakcije brand-a
  let brand = 'Unknown';
  if (originalName.includes('McDonald')) brand = 'McDonald\'s';
  else if (originalName.includes('Nivea') || originalName.includes('NFC') || originalName.includes('NBD')) brand = 'Nivea';
  else if (originalName.includes('Rio Mare')) brand = 'Rio Mare';
  else if (originalName.includes('Oetker')) brand = 'Dr. Oetker';
  else if (originalName.includes('Bref')) brand = 'Bref';
  else if (originalName.includes('Schauma')) brand = 'Schauma';
  else if (originalName.includes('Belupo') || originalName.includes('Rinil')) brand = 'Belupo';
  else if (originalName.includes('Ahmad')) brand = 'Ahmad Tea';
  else if (originalName.includes('Bison')) brand = 'Bison';
  else if (originalName.includes('Loacker')) brand = 'Loacker';
  else if (originalName.includes('Porsche')) brand = 'Porsche';
  else if (originalName.includes('Saponia')) brand = 'Saponia';

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
