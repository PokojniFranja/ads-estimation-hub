/**
 * ADS ESTIMATION HUB - Data Importer
 *
 * Skripta za učitavanje, filtriranje, normalizaciju i spajanje
 * Google Ads kampanja za hrvatsko tržište.
 *
 * @author Claude - Google Ads Specialist
 * @version 1.0.0
 */

import * as fs from 'fs';
import * as path from 'path';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import * as iconv from 'iconv-lite';

// ============================================================================
// TIPOVI I INTERFACE-I
// ============================================================================

interface RawCampaignMetrics {
  'Ad format': string;
  'Campaign': string;
  'Campaign ID': string;
  'Clicks': string;
  'Impr.': string;
  'CTR': string;
  'Avg. CPC': string;
  'Avg. CPM': string;
  'TrueView views': string;
  'TrueView avg. CPV': string;
  'Conversions': string;
  'Cost / conv.': string;
  'Conv. rate': string;
  'Avg. impr. freq. / user': string;
  'Unique users': string;
  'Cost': string;
}

interface RawAgeGender {
  'Campaign': string;
  'Campaign ID': string;
  'Campaign type': string;
  'Age': string;
  'Gender': string;
  'Cost': string;
}

interface RawInterest {
  'Campaign': string;
  'Campaign ID': string;
  'Campaign type': string;
  'Audience segment': string;
  'Cost': string;
}

interface ProcessedCampaign {
  campaignId: string;
  originalName: string;
  standardizedName: string;
  brand: string;
  type: string;
  placements: string[];
  adFormats: string[];
  demographics: {
    ageGroups: string[];
    genders: string[];
    dominantAge: string;
    dominantGender: string;
  };
  language: string;
  market: string;
  bidding: string;
  metrics: {
    totalSpend: number;
    totalImpressions: number;
    totalClicks: number;
    totalViews: number;
    peakReach: number;
    weightedCPM: number;
    weightedCPC: number;
    weightedCPV: number;
    avgCTR: number;
    avgFrequency: number;
  };
  audienceSegments: string[];
  quarters: string[];
}

// ============================================================================
// KONSTANTE I EXCLUSION LISTE
// ============================================================================

// Market exclusion - ključne riječi za neHR kampanje
const MARKET_EXCLUSION_KEYWORDS = [
  'SI-SL',
  'RS-SR',
  'ME-ME',
  'SLO',
  'Slovenia',
  'Slovenija',
  'BiH',
  'Bosna',
  'Srbija',
  'Serbia',
  'Mison',
  'Elgrad',
  'AlwaysOnSLO',
  'AlwaysOnBiH',
  '_SLO_',
  '_BIH_',
  '_SRB_',
];

// Worldwide bug - specifične kampanje za isključiti (case-insensitive match)
const WORLDWIDE_BUG_CAMPAIGNS = [
  "McDonald's IceCoffe June - August 2025 (YT) - CPV",
  "McDonald's Stripsi June - July 2025 (YT) - Bumper",
  "McDonald's Stripsi June - July 2025 (YT) - CPV",
];

// Brand mapping - ekstrakcija branda iz imena kampanje
const BRAND_PATTERNS: [RegExp, string][] = [
  [/^Kaufland/i, 'KAUFLAND'],
  [/^Volkswagen/i, 'VOLKSWAGEN'],
  [/^VW/i, 'VOLKSWAGEN'],
  [/^[Šš]koda/i, 'ŠKODA'],
  [/^Cupra/i, 'CUPRA'],
  [/^Seat/i, 'SEAT'],
  [/^McDonald/i, "MCDONALD'S"],
  [/^Energycom/i, 'ENERGYCOM'],
  [/^Finish/i, 'FINISH'],
  [/^LG|^HR_/i, 'LG'],
  [/^Loacker/i, 'LOACKER'],
  [/^Ahmad/i, 'AHMAD TEA'],
  [/^Koestlin/i, 'KOESTLIN'],
  [/^Rio Mare/i, 'RIO MARE'],
  [/^Dr\. Oetker/i, 'DR. OETKER'],
  [/^BIC/i, 'BIC'],
  [/^Taft/i, 'TAFT'],
  [/^Palette/i, 'PALETTE'],
  [/^Borotalco/i, 'BOROTALCO'],
  [/^UHU/i, 'UHU'],
  [/^LOC_HRV.*BAR.*BLUE/i, 'BARILLA'],
  [/^LOC_HRV.*GRA/i, 'GRANCEREALE'],
  [/^LOC_HRV.*BAIO/i, 'BAIOCCHI'],
  [/^HGK/i, 'HGK'],
  [/^Panonski/i, 'PANONSKI FESTIVAL'],
  [/^YT-Cupra/i, 'CUPRA'],
  [/^DG_|^VID_/i, 'PHILIPS'], // OMD Philips kampanje
  [/^T03_/i, 'EUCERIN'], // Eucerin kampanje
];

// Tipovi kampanja
const CAMPAIGN_TYPE_PATTERNS: [RegExp, string][] = [
  [/\(YT\)|\(YouTube\)|YouTube|TrueView|Bumper|In-stream|video/i, 'YouTube'],
  [/\(DG\)|Demand Gen|DG_/i, 'Demand Gen'],
  [/\(DN\)|Display|GDN|\(GDN\)/i, 'Display'],
  [/PMax|Performance Max/i, 'PMax'],
];

// Bidding strategije
const BIDDING_PATTERNS: [RegExp, string][] = [
  [/CPV|VVC|TrueView/i, 'CPV'],
  [/CPM|Bumper|Reach/i, 'CPM'],
  [/CPC|Click/i, 'CPC'],
  [/CPE/i, 'CPE'],
];

// Excel date bug mapping (hrvatski mjeseci)
const EXCEL_DATE_FIX: Record<string, string> = {
  'sij': '01', 'velj': '02', 'ožu': '03', 'tra': '04',
  'svi': '05', 'lip': '06', 'srp': '07', 'kol': '08',
  'ruj': '09', 'lis': '10', 'stu': '11', 'pro': '12',
};

// ============================================================================
// UTILITY FUNKCIJE
// ============================================================================

/**
 * Čisti UTF-8 BOM i popravlja encoding probleme
 */
function sanitizeEncoding(text: string): string {
  // Ukloni BOM
  let cleaned = text.replace(/^\uFEFF/, '');

  // Popravi ceste encoding probleme za hrvatske znakove
  // Koristimo unicode escape sekvence da izbjegnemo encoding probleme u source kodu
  const encodingFixes: Record<string, string> = {
    '\u00C5\u00A1': '\u0161',  // Å¡ -> š
    '\u00C5\u00A0': '\u0160',  // Å  -> Š
    '\u00C4\u008D': '\u010D',  // Ä -> č
    '\u00C4\u008C': '\u010C',  // Ä -> Č
    '\u00C4\u0087': '\u0107',  // Ä‡ -> ć
    '\u00C4\u0086': '\u0106',  // Ä† -> Ć
    '\u00C5\u00BE': '\u017E',  // Å¾ -> ž
    '\u00C5\u00BD': '\u017D',  // Å½ -> Ž
    '\u00C4\u0091': '\u0111',  // Ä' -> đ
    '\u00C4\u0090': '\u0110',  // Ä -> Đ
    '`k': '\u0160k',           // `k -> Šk (bug za Skoda)
  };

  for (const [wrong, correct] of Object.entries(encodingFixes)) {
    cleaned = cleaned.split(wrong).join(correct);
  }

  // Ukloni null karaktere
  cleaned = cleaned.replace(/\x00/g, '');

  return cleaned;
}

/**
 * Popravlja Excel date bug (npr. '2.ožu' -> '2.03')
 */
function fixExcelDateBug(text: string): string {
  let fixed = text;
  for (const [monthName, monthNum] of Object.entries(EXCEL_DATE_FIX)) {
    const regex = new RegExp(`(\\d+)\\.${monthName}`, 'gi');
    fixed = fixed.replace(regex, `$1.${monthNum}`);
  }
  return fixed;
}

/**
 * Čisti simbole valuta i parsira broj
 */
function parseNumber(value: string | number | undefined): number {
  if (value === undefined || value === null || value === '') return 0;
  if (typeof value === 'number') return value;

  // Ukloni simbole valuta, razmake i postotke
  let cleaned = value
    .replace(/[€$HRK%\s]/g, '')
    .replace(/,/g, '') // Ukloni tisućice separator
    .trim();

  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

/**
 * Čisti Campaign ID (uklanja razmake i posebne znakove)
 */
function cleanCampaignId(id: string | number): string {
  if (!id) return '';
  return String(id).replace(/[\s\x00]/g, '').trim();
}

/**
 * Provjerava je li kampanja za isključiti (ne-HR tržište)
 */
function shouldExcludeCampaign(campaignName: string): boolean {
  const normalizedName = campaignName.toUpperCase();

  // Provjeri market exclusion keywords
  for (const keyword of MARKET_EXCLUSION_KEYWORDS) {
    if (normalizedName.includes(keyword.toUpperCase())) {
      return true;
    }
  }

  // Provjeri worldwide bug kampanje
  for (const worldwideCampaign of WORLDWIDE_BUG_CAMPAIGNS) {
    if (normalizedName.includes(worldwideCampaign.toUpperCase())) {
      return true;
    }
  }

  return false;
}

/**
 * Ekstrahira brand iz imena kampanje
 */
function extractBrand(campaignName: string): string {
  for (const [pattern, brand] of BRAND_PATTERNS) {
    if (pattern.test(campaignName)) {
      return brand;
    }
  }

  // Fallback: uzmi prvu riječ
  const firstWord = campaignName.split(/[\s_-]/)[0];
  return firstWord.toUpperCase();
}

/**
 * Određuje tip kampanje
 */
function determineCampaignType(campaignName: string, adFormat: string): string {
  // Prvo provjeri ad format
  if (adFormat) {
    const formatLower = adFormat.toLowerCase();
    if (formatLower.includes('in-stream') || formatLower.includes('bumper') || formatLower.includes('shorts') || formatLower.includes('in-feed')) {
      return 'YouTube';
    }
    if (formatLower.includes('display')) {
      return 'Display';
    }
  }

  // Zatim provjeri ime kampanje
  for (const [pattern, type] of CAMPAIGN_TYPE_PATTERNS) {
    if (pattern.test(campaignName)) {
      return type;
    }
  }

  return 'Other';
}

/**
 * Određuje bidding strategiju
 */
function determineBidding(campaignName: string): string {
  for (const [pattern, bidding] of BIDDING_PATTERNS) {
    if (pattern.test(campaignName)) {
      return bidding;
    }
  }
  return 'CPM'; // Default
}

/**
 * Određuje jezik kampanje
 */
function determineLanguage(campaignName: string): string {
  const nameLower = campaignName.toLowerCase();

  if (nameLower.includes('polish') || nameLower.includes('poland') || nameLower.includes('_pl_')) {
    return 'Polish';
  }
  if (nameLower.includes('german') || nameLower.includes('deutschland') || nameLower.includes('_de_')) {
    return 'German';
  }
  if (nameLower.includes('hungarian') || nameLower.includes('hungary') || nameLower.includes('_hu_')) {
    return 'Hungarian';
  }
  if (nameLower.includes('english') || nameLower.includes('_en_')) {
    return 'English';
  }

  return 'Local'; // Hrvatski
}

/**
 * Određuje kvartal iz imena datoteke
 */
function extractQuarter(filename: string): string {
  const lower = filename.toLowerCase();
  if (lower.includes('jan') && lower.includes('mar')) return 'Q1';
  if (lower.includes('apr') && lower.includes('jun')) return 'Q2';
  if (lower.includes('jul') && lower.includes('sep')) return 'Q3';
  if (lower.includes('oct') && lower.includes('dec')) return 'Q4';
  return 'Unknown';
}

/**
 * Generira standardizirano ime kampanje
 */
function generateStandardizedName(campaign: Partial<ProcessedCampaign>): string {
  const brand = campaign.brand || 'UNKNOWN';
  const type = campaign.type || 'Other';
  const placements = campaign.placements?.length ? campaign.placements.join('+') : 'Mixed';
  const demo = `${campaign.demographics?.dominantAge || 'All'} ${campaign.demographics?.dominantGender || 'All'}`;
  const language = campaign.language || 'Local';
  const market = campaign.market || 'HR';
  const bidding = campaign.bidding || 'CPM';

  return `${brand} | ${type} | ${placements} | ${demo} | ${language} | ${market} | ${bidding}`;
}

// ============================================================================
// FILE PARSING FUNKCIJE
// ============================================================================

/**
 * Učitava i parsira CSV datoteku
 */
function parseCSV<T>(filePath: string): T[] {
  try {
    // Pročitaj kao buffer za detekciju encodinga
    const buffer = fs.readFileSync(filePath);

    // Pokušaj dekodirati kao UTF-16 LE (Excel default za CSV s posebnim znakovima)
    let content: string;
    if (buffer[0] === 0xFF && buffer[1] === 0xFE) {
      content = iconv.decode(buffer, 'utf-16le');
    } else if (buffer[0] === 0xFE && buffer[1] === 0xFF) {
      content = iconv.decode(buffer, 'utf-16be');
    } else {
      // Pokušaj UTF-8
      content = buffer.toString('utf-8');
    }

    // Sanitiziraj encoding
    content = sanitizeEncoding(content);
    content = fixExcelDateBug(content);

    // Parsiraj CSV
    const result = Papa.parse<T>(content, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (header: string) => sanitizeEncoding(header).trim(),
      transform: (value: string) => sanitizeEncoding(value).trim(),
    });

    return result.data;
  } catch (error) {
    console.error(`Greška pri parsiranju CSV-a: ${filePath}`, error);
    return [];
  }
}

/**
 * Učitava i parsira XLSX datoteku
 */
function parseXLSX<T>(filePath: string): T[] {
  try {
    const workbook = XLSX.readFile(filePath);
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];

    const jsonData = XLSX.utils.sheet_to_json<T>(worksheet, {
      raw: false,
      defval: '',
    });

    // Sanitiziraj sve stringove
    return jsonData.map(row => {
      const sanitizedRow: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(row as Record<string, unknown>)) {
        const sanitizedKey = sanitizeEncoding(key);
        sanitizedRow[sanitizedKey] = typeof value === 'string'
          ? fixExcelDateBug(sanitizeEncoding(value))
          : value;
      }
      return sanitizedRow as T;
    });
  } catch (error) {
    console.error(`Greška pri parsiranju XLSX-a: ${filePath}`, error);
    return [];
  }
}

// ============================================================================
// GLAVNA PROCESSING LOGIKA
// ============================================================================

/**
 * Glavna funkcija za obradu podataka
 */
async function processAllData(): Promise<void> {
  console.log('\n========================================');
  console.log('  ADS ESTIMATION HUB - Data Importer');
  console.log('========================================\n');

  const baseDir = path.resolve(__dirname, '../data/raw');
  const outputDir = path.resolve(__dirname, '../data');

  // Mapa za agregaciju kampanja po ID-u
  const campaignMap = new Map<string, ProcessedCampaign>();

  // Brojači za izvještaj
  let totalRawCampaigns = 0;
  let excludedMarket = 0;
  let excludedWorldwide = 0;
  const excludedWorldwideNames: string[] = [];

  // ------------------------------------------
  // 1. UČITAJ CAMPAIGN METRICS DATA
  // ------------------------------------------
  console.log('📊 Učitavam Campaign Metrics Data...\n');

  const metricsDir = path.join(baseDir, 'campaign metrics data');
  const metricsFiles = fs.readdirSync(metricsDir).filter(f => f.endsWith('.csv') || f.endsWith('.xlsx'));

  for (const file of metricsFiles) {
    const filePath = path.join(metricsDir, file);
    const quarter = extractQuarter(file);
    console.log(`  📁 ${file} (${quarter})`);

    const data = file.endsWith('.xlsx')
      ? parseXLSX<RawCampaignMetrics>(filePath)
      : parseCSV<RawCampaignMetrics>(filePath);

    console.log(`     → Pronađeno ${data.length} redova`);

    for (const row of data) {
      totalRawCampaigns++;

      const campaignName = sanitizeEncoding(row['Campaign'] || '');
      const campaignId = cleanCampaignId(row['Campaign ID']);

      if (!campaignId || !campaignName) continue;

      // Provjeri exclusion
      if (shouldExcludeCampaign(campaignName)) {
        // Provjeri je li worldwide bug
        const isWorldwide = WORLDWIDE_BUG_CAMPAIGNS.some(
          wc => campaignName.toUpperCase().includes(wc.toUpperCase())
        );

        if (isWorldwide) {
          excludedWorldwide++;
          if (!excludedWorldwideNames.includes(campaignName)) {
            excludedWorldwideNames.push(campaignName);
          }
        } else {
          excludedMarket++;
        }
        continue;
      }

      // Parsiraj metrike
      const spend = parseNumber(row['Cost']);
      const impressions = parseNumber(row['Impr.']);
      const clicks = parseNumber(row['Clicks']);
      const views = parseNumber(row['TrueView views']);
      const reach = parseNumber(row['Unique users']);
      const frequency = parseNumber(row['Avg. impr. freq. / user']);
      const ctr = parseNumber(row['CTR']);
      const adFormat = sanitizeEncoding(row['Ad format'] || '');

      // Dohvati ili kreiraj kampanju
      if (!campaignMap.has(campaignId)) {
        const brand = extractBrand(campaignName);
        const type = determineCampaignType(campaignName, adFormat);
        const bidding = determineBidding(campaignName);
        const language = determineLanguage(campaignName);

        campaignMap.set(campaignId, {
          campaignId,
          originalName: campaignName,
          standardizedName: '', // Generirat ćemo kasnije
          brand,
          type,
          placements: [],
          adFormats: [],
          demographics: {
            ageGroups: [],
            genders: [],
            dominantAge: '',
            dominantGender: '',
          },
          language,
          market: 'HR',
          bidding,
          metrics: {
            totalSpend: 0,
            totalImpressions: 0,
            totalClicks: 0,
            totalViews: 0,
            peakReach: 0,
            weightedCPM: 0,
            weightedCPC: 0,
            weightedCPV: 0,
            avgCTR: 0,
            avgFrequency: 0,
          },
          audienceSegments: [],
          quarters: [],
        });
      }

      const campaign = campaignMap.get(campaignId)!;

      // Agregiraj metrike
      campaign.metrics.totalSpend += spend;
      campaign.metrics.totalImpressions += impressions;
      campaign.metrics.totalClicks += clicks;
      campaign.metrics.totalViews += views;
      campaign.metrics.peakReach = Math.max(campaign.metrics.peakReach, reach);
      campaign.metrics.avgFrequency = Math.max(campaign.metrics.avgFrequency, frequency);

      // Dodaj ad format ako nije već dodan
      if (adFormat && !campaign.adFormats.includes(adFormat)) {
        campaign.adFormats.push(adFormat);

        // Mapiranje ad formata u placements
        const formatLower = adFormat.toLowerCase();
        let placement = '';
        if (formatLower.includes('in-stream') || formatLower.includes('skippable') || formatLower.includes('non-skippable')) {
          placement = 'In-Stream';
        } else if (formatLower.includes('bumper')) {
          placement = 'Bumper';
        } else if (formatLower.includes('shorts')) {
          placement = 'Shorts';
        } else if (formatLower.includes('in-feed')) {
          placement = 'In-Feed';
        } else if (formatLower.includes('display')) {
          placement = 'GDN';
        }

        if (placement && !campaign.placements.includes(placement)) {
          campaign.placements.push(placement);
        }
      }

      // Dodaj kvartal
      if (quarter && !campaign.quarters.includes(quarter)) {
        campaign.quarters.push(quarter);
      }
    }
  }

  // ------------------------------------------
  // 2. UČITAJ AGE GENDER DATA
  // ------------------------------------------
  console.log('\n👥 Učitavam Age Gender Data...\n');

  const ageGenderDir = path.join(baseDir, 'age gender');
  const ageGenderFiles = fs.readdirSync(ageGenderDir).filter(f => f.endsWith('.csv') || f.endsWith('.xlsx'));

  // Mapa za praćenje demografskih podataka po kampanjama
  const demoData = new Map<string, { ages: Map<string, number>; genders: Map<string, number> }>();

  for (const file of ageGenderFiles) {
    const filePath = path.join(ageGenderDir, file);
    console.log(`  📁 ${file}`);

    const data = file.endsWith('.xlsx')
      ? parseXLSX<RawAgeGender>(filePath)
      : parseCSV<RawAgeGender>(filePath);

    console.log(`     → Pronađeno ${data.length} redova`);

    for (const row of data) {
      const campaignId = cleanCampaignId(row['Campaign ID']);
      const campaignName = sanitizeEncoding(row['Campaign'] || '');

      if (!campaignId || shouldExcludeCampaign(campaignName)) continue;

      const age = sanitizeEncoding(row['Age'] || '');
      const gender = sanitizeEncoding(row['Gender'] || '');
      const cost = parseNumber(row['Cost']);

      if (!demoData.has(campaignId)) {
        demoData.set(campaignId, { ages: new Map(), genders: new Map() });
      }

      const demo = demoData.get(campaignId)!;

      // Agregiraj po age group
      if (age) {
        demo.ages.set(age, (demo.ages.get(age) || 0) + cost);
      }

      // Agregiraj po gender
      if (gender) {
        demo.genders.set(gender, (demo.genders.get(gender) || 0) + cost);
      }
    }
  }

  // Primijeni demografske podatke na kampanje
  for (const [campaignId, demo] of demoData) {
    const campaign = campaignMap.get(campaignId);
    if (!campaign) continue;

    // Sortiraj po spendu i odredi dominantne
    const sortedAges = [...demo.ages.entries()].sort((a, b) => b[1] - a[1]);
    const sortedGenders = [...demo.genders.entries()].sort((a, b) => b[1] - a[1]);

    campaign.demographics.ageGroups = sortedAges.map(([age]) => age);
    campaign.demographics.genders = sortedGenders.map(([gender]) => gender);

    // Top 2 age groups za dominantnu demografiju - izvuci min/max dob
    if (sortedAges.length >= 2) {
      // Parsiraj dobi iz oba age rangea (npr. "25 - 34" i "35 - 44" -> "25-44")
      const ageRanges = sortedAges.slice(0, 2).map(([age]) => age);
      const allAges: number[] = [];
      for (const range of ageRanges) {
        const matches = range.match(/(\d+)/g);
        if (matches) {
          allAges.push(...matches.map(Number));
        }
      }
      if (allAges.length > 0) {
        const minAge = Math.min(...allAges);
        const maxAge = Math.max(...allAges);
        campaign.demographics.dominantAge = minAge === maxAge ? `${minAge}+` : `${minAge}-${maxAge}`;
      } else {
        campaign.demographics.dominantAge = ageRanges.join('/');
      }
    } else if (sortedAges.length === 1) {
      campaign.demographics.dominantAge = sortedAges[0][0].replace(/\s*-\s*/g, '-');
    }

    // Dominantni gender
    if (sortedGenders.length > 0) {
      const topGender = sortedGenders[0][0];
      campaign.demographics.dominantGender = topGender === 'Male' ? 'M' : topGender === 'Female' ? 'F' : 'All';
    }
  }

  // ------------------------------------------
  // 3. UČITAJ INTEREST AUDIENCE SEGMENTS
  // ------------------------------------------
  console.log('\n🎯 Učitavam Interest Audience Segments...\n');

  const interestDir = path.join(baseDir, 'interest audience segments');
  const interestFiles = fs.readdirSync(interestDir).filter(f => f.endsWith('.csv') || f.endsWith('.xlsx'));

  for (const file of interestFiles) {
    const filePath = path.join(interestDir, file);
    console.log(`  📁 ${file}`);

    const data = file.endsWith('.xlsx')
      ? parseXLSX<RawInterest>(filePath)
      : parseCSV<RawInterest>(filePath);

    console.log(`     → Pronađeno ${data.length} redova`);

    for (const row of data) {
      const campaignId = cleanCampaignId(row['Campaign ID']);
      const segment = sanitizeEncoding(row['Audience segment'] || '');

      if (!campaignId || !segment) continue;

      const campaign = campaignMap.get(campaignId);
      if (campaign && !campaign.audienceSegments.includes(segment)) {
        campaign.audienceSegments.push(segment);
      }
    }
  }

  // ------------------------------------------
  // 4. IZRAČUNAJ WEIGHTED METRIKE
  // ------------------------------------------
  console.log('\n📐 Računam weighted metrike...\n');

  for (const campaign of campaignMap.values()) {
    const { totalSpend, totalImpressions, totalClicks, totalViews } = campaign.metrics;

    // Weighted CPM = (Total Spend / Total Impressions) * 1000
    if (totalImpressions > 0) {
      campaign.metrics.weightedCPM = (totalSpend / totalImpressions) * 1000;
    }

    // Weighted CPC = Total Spend / Total Clicks
    if (totalClicks > 0) {
      campaign.metrics.weightedCPC = totalSpend / totalClicks;
    }

    // Weighted CPV = Total Spend / Total Views
    if (totalViews > 0) {
      campaign.metrics.weightedCPV = totalSpend / totalViews;
    }

    // Avg CTR = Total Clicks / Total Impressions
    if (totalImpressions > 0) {
      campaign.metrics.avgCTR = (totalClicks / totalImpressions) * 100;
    }

    // Generiraj standardizirano ime
    campaign.standardizedName = generateStandardizedName(campaign);
  }

  // ------------------------------------------
  // 5. PRIPREMI FINALNI OUTPUT
  // ------------------------------------------
  console.log('📦 Pripremam finalni output...\n');

  const finalData = {
    metadata: {
      generatedAt: new Date().toISOString(),
      version: '1.0.0',
      market: 'HR',
      totalCampaigns: campaignMap.size,
      dataSource: 'Google Ads Export',
    },
    campaigns: Array.from(campaignMap.values()).map(c => ({
      ...c,
      // Zaokruži brojeve na 2 decimale
      metrics: {
        ...c.metrics,
        totalSpend: Math.round(c.metrics.totalSpend * 100) / 100,
        weightedCPM: Math.round(c.metrics.weightedCPM * 100) / 100,
        weightedCPC: Math.round(c.metrics.weightedCPC * 100) / 100,
        weightedCPV: Math.round(c.metrics.weightedCPV * 100) / 100,
        avgCTR: Math.round(c.metrics.avgCTR * 100) / 100,
        avgFrequency: Math.round(c.metrics.avgFrequency * 10) / 10,
      },
    })),
  };

  // Spremi JSON
  const outputPath = path.join(outputDir, 'agency_master_2025.json');
  fs.writeFileSync(outputPath, JSON.stringify(finalData, null, 2), 'utf-8');

  // ------------------------------------------
  // 6. GENERIRAJ IZVJEŠTAJ
  // ------------------------------------------
  console.log('\n========================================');
  console.log('  📋 IZVJEŠTAJ O OBRADI');
  console.log('========================================\n');

  console.log(`📊 STATISTIKE:`);
  console.log(`   • Ukupno učitanih redova: ${totalRawCampaigns}`);
  console.log(`   • Isključeno (ne-HR market): ${excludedMarket}`);
  console.log(`   • Isključeno (Worldwide bug): ${excludedWorldwide}`);
  console.log(`   ────────────────────────────────`);
  console.log(`   ✅ JEDINSTVENIH HR KAMPANJA: ${campaignMap.size}`);

  console.log(`\n🚫 WORLDWIDE BUG KAMPANJE (uspješno izbačene):`);
  if (excludedWorldwideNames.length > 0) {
    for (const name of excludedWorldwideNames) {
      console.log(`   ✓ ${name}`);
    }
  } else {
    console.log(`   (Niti jedna od 3 McDonald's Worldwide kampanja nije pronađena u podacima)`);
  }

  // Provjeri jesu li sve 3 McDonald's kampanje bile isključene
  const mcDonaldsCheck = WORLDWIDE_BUG_CAMPAIGNS.every(wc =>
    excludedWorldwideNames.some(name => name.toUpperCase().includes(wc.split(' ').slice(0, 3).join(' ').toUpperCase()))
  );

  console.log(`\n📁 OUTPUT LOKACIJA:`);
  console.log(`   ${outputPath}`);

  console.log(`\n🎯 SAMPLE STANDARDIZIRANIH IMENA (prvih 5):`);
  const sampleCampaigns = Array.from(campaignMap.values()).slice(0, 5);
  for (const c of sampleCampaigns) {
    console.log(`   • ${c.standardizedName}`);
  }

  console.log('\n========================================');
  console.log('  ✅ OBRADA ZAVRŠENA USPJEŠNO');
  console.log('========================================\n');
}

// Pokreni ako je direktno pozvan
processAllData().catch(console.error);
