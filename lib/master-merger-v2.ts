/**
 * MASTER DATABASE MERGER V2
 *
 * Arhitektura:
 * - Source of Truth: metrics.csv (financije)
 * - Safe Math: null za div by zero
 * - Top 10 interesi + coverage %
 * - Peak Reach (max) + isMultiQuarter flag
 * - Metadata: quarter i month
 */

import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

// ============================================================================
// TIPOVI
// ============================================================================

interface MetricsRow {
  'Ad format': string;
  Campaign: string;
  'Campaign ID': string;
  Clicks: string;
  'Impr.': string;
  CTR: string;
  'Avg. CPC': string;
  'Avg. CPM': string;
  'TrueView views': string;
  'TrueView avg. CPV': string;
  Conversions: string;
  'Cost / conv.': string;
  'Conv. rate': string;
  Cost: string;
}

interface AgeGenderRow {
  'Campaign ID': string;
  Campaign: string;
  Age: string;
  Gender: string;
  Cost: string;
  'Impr.': string;
  Clicks: string;
}

interface InterestRow {
  'Campaign ID': string;
  Campaign: string;
  'Audience segment': string;
  Cost: string;
  'Impr.': string;
  Clicks: string;
}

interface ReachRow {
  'Ad format': string;
  Campaign: string;
  'Campaign ID': string;
  'Avg. impr. freq. / user': string;
  'Unique users': string;
}

interface RegistryRow {
  'Campaign ID': string;
  'Original Name': string;
  'Standardized Name': string;
  'Start Date': string;
  'End Date': string;
}

interface DemographicBreakdown {
  age: string;
  gender: string;
  percentage: number; // % od total spend
}

interface InterestSegment {
  segment: string;
  cost: number;
  percentage: number; // % od total spend
}

interface CampaignMaster {
  campaignId: string;
  originalName: string;
  standardizedName: string;

  // Metadata
  startDate: string;
  endDate: string;
  quarter: string[];
  month: string[];

  // Financials (Source of Truth: metrics.csv)
  spend: number;
  impressions: number;
  clicks: number;
  trueViewViews: number | null;
  conversions: number;

  // Calculated Metrics (Safe Math)
  ctr: number | null;
  cpc: number | null;
  cpm: number | null;
  cpv: number | null;
  costPerConversion: number | null;
  conversionRate: number | null;

  // Reach & Frequency
  reach: number | null;
  frequency: number | null;
  isMultiQuarter: boolean;
  reachDisclaimer?: string;

  // Demographics (breakdown only, not spend source)
  demographics: DemographicBreakdown[];

  // Interests (Top 10 + coverage)
  interests: InterestSegment[];
  interestsCoverage: number; // % koliko Top 10 pokriva od total spend-a

  // Raw format
  adFormat: string;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function parseNumber(value: string | undefined | null): number {
  if (!value) return 0;

  // Ukloni sve osim brojeva, točaka, zareza i minusa
  let cleaned = value.replace(/[^\d.,-]/g, '');

  // AMERIČKI FORMAT (Google Ads CSV export):
  // Zarez (,) = thousands separator → UKLONI: "1,256,267" → "1256267"
  // Točka (.) = decimal separator → OSTAVI: "2860.6" → "2860.6"
  cleaned = cleaned.replace(/,/g, '');

  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

function safeDiv(numerator: number, denominator: number): number | null {
  if (denominator === 0) return null;
  return numerator / denominator;
}

function extractQuarter(dateStr: string): string {
  // Format: DD.MM.YYYY. (npr. "01.09.2025.")
  const match = dateStr.match(/\d{2}\.(\d{2})\./);
  if (!match) return 'Q?';

  const month = parseInt(match[1]);
  if (month >= 1 && month <= 3) return 'Q1';
  if (month >= 4 && month <= 6) return 'Q2';
  if (month >= 7 && month <= 9) return 'Q3';
  if (month >= 10 && month <= 12) return 'Q4';
  return 'Q?';
}

function extractMonth(dateStr: string): string {
  const match = dateStr.match(/\d{2}\.(\d{2})\./);
  if (!match) return '?';
  return match[1];
}

function getQuartersAndMonths(startDate: string, endDate: string): { quarters: string[], months: string[] } {
  const quarters = new Set<string>();
  const months = new Set<string>();

  quarters.add(extractQuarter(startDate));
  quarters.add(extractQuarter(endDate));

  months.add(extractMonth(startDate));
  months.add(extractMonth(endDate));

  return {
    quarters: Array.from(quarters).sort(),
    months: Array.from(months).sort()
  };
}

// ============================================================================
// CSV READERS
// ============================================================================

function readCSV<T>(filePath: string): T[] {
  const content = fs.readFileSync(filePath, 'utf-8');
  const parsed = Papa.parse(content, {
    header: true,
    skipEmptyLines: true
  });
  return parsed.data as T[];
}

// ============================================================================
// MAIN MERGER LOGIC
// ============================================================================

function mergeMasterDatabase(): CampaignMaster[] {
  const dataDir = path.join(process.cwd(), 'data');
  const rawDir = path.join(dataDir, 'raw');

  console.log('📂 Učitavam podatke...\n');

  // 1. REGISTRY (standardized names)
  const registry = readCSV<RegistryRow>(path.join(dataDir, 'campaign_registry.csv'));
  const registryMap = new Map(registry.map(r => [r['Campaign ID'], r]));
  console.log(`✅ Registry: ${registry.length} kampanja`);

  // 2. METRICS (source of truth) - AGGREGATE BY CAMPAIGN ID
  const metricsRaw = readCSV<MetricsRow>(path.join(rawDir, 'campaign_metrics', '2025_metrics.csv'));
  const metricsMap = new Map<string, { formats: string[], spend: number, impressions: number, clicks: number, views: number, conversions: number }>();

  metricsRaw.forEach(row => {
    const id = row['Campaign ID'];
    const spend = parseNumber(row.Cost);
    const impressions = parseNumber(row['Impr.']);
    const clicks = parseNumber(row.Clicks);
    const views = parseNumber(row['TrueView views']);
    const conversions = parseNumber(row.Conversions);
    const format = row['Ad format'];

    if (!metricsMap.has(id)) {
      metricsMap.set(id, {
        formats: [format],
        spend,
        impressions,
        clicks,
        views,
        conversions
      });
    } else {
      const existing = metricsMap.get(id)!;
      if (!existing.formats.includes(format)) existing.formats.push(format);
      existing.spend += spend;
      existing.impressions += impressions;
      existing.clicks += clicks;
      existing.views += views;
      existing.conversions += conversions;
    }
  });

  console.log(`✅ Metrics: ${metricsRaw.length} redaka → ${metricsMap.size} kampanja`);

  // 3. AGE GENDER
  const ageGender = readCSV<AgeGenderRow>(path.join(rawDir, 'age_gender_clean.csv'));
  const ageGenderByCampaign = new Map<string, AgeGenderRow[]>();
  ageGender.forEach(row => {
    const id = row['Campaign ID'];
    if (!ageGenderByCampaign.has(id)) ageGenderByCampaign.set(id, []);
    ageGenderByCampaign.get(id)!.push(row);
  });
  console.log(`✅ Demographics: ${ageGender.length} redaka`);

  // 4. INTERESTS
  const interests = readCSV<InterestRow>(path.join(rawDir, 'interests_clean.csv'));
  const interestsByCampaign = new Map<string, InterestRow[]>();
  interests.forEach(row => {
    const id = row['Campaign ID'];
    if (!interestsByCampaign.has(id)) interestsByCampaign.set(id, []);
    interestsByCampaign.get(id)!.push(row);
  });
  console.log(`✅ Interests: ${interests.length} redaka`);

  // 5. REACH (po kvartalima) - Peak Reach
  const reachFiles = ['Q1_2025.csv', 'Q2_2025.csv', 'Q3_2025.csv', 'Q4_2025.csv'];
  const reachByCampaign = new Map<string, { reach: number, frequency: number, count: number }>();

  reachFiles.forEach(file => {
    const filePath = path.join(rawDir, 'campaign_reach_frequency', file);
    if (!fs.existsSync(filePath)) return;

    const reachData = readCSV<ReachRow>(filePath);
    reachData.forEach(row => {
      const id = row['Campaign ID'];
      const reach = parseNumber(row['Unique users']);
      const freq = parseNumber(row['Avg. impr. freq. / user']);

      if (!reachByCampaign.has(id)) {
        reachByCampaign.set(id, { reach, frequency: freq, count: 1 });
      } else {
        const existing = reachByCampaign.get(id)!;
        // Peak Reach = MAX
        existing.reach = Math.max(existing.reach, reach);
        // Frequency = average
        existing.frequency = ((existing.frequency * existing.count) + freq) / (existing.count + 1);
        existing.count++;
      }
    });
  });
  console.log(`✅ Reach: ${reachByCampaign.size} kampanja s reach podacima\n`);

  // ============================================================================
  // MERGE
  // ============================================================================

  console.log('🔄 Merging podataka...\n');

  const masterData: CampaignMaster[] = [];

  registry.forEach(reg => {
    const id = reg['Campaign ID'];
    const met = metricsMap.get(id);

    if (!met) {
      console.warn(`⚠️  Kampanja ${id} nema metrics podatke - preskačem`);
      return;
    }

    // -------------------------------------------------------------------------
    // FINANCIALS (metrics.csv = source of truth - AGGREGATED)
    // -------------------------------------------------------------------------
    const spend = met.spend;
    const impressions = met.impressions;
    const clicks = met.clicks;
    const trueViewViews = met.views > 0 ? met.views : null;
    const conversions = met.conversions;

    // Safe Math
    const ctr = safeDiv(clicks, impressions);
    const cpc = safeDiv(spend, clicks);
    const cpm = safeDiv(spend, impressions / 1000);
    const cpv = trueViewViews ? safeDiv(spend, trueViewViews) : null;
    const costPerConversion = safeDiv(spend, conversions);
    const conversionRate = safeDiv(conversions, clicks);

    // -------------------------------------------------------------------------
    // DEMOGRAPHICS (breakdown only)
    // -------------------------------------------------------------------------
    const demographics: DemographicBreakdown[] = [];
    const demoRows = ageGenderByCampaign.get(id) || [];
    const totalDemoCost = demoRows.reduce((sum, row) => sum + parseNumber(row.Cost), 0);

    demoRows.forEach(row => {
      const cost = parseNumber(row.Cost);
      const percentage = totalDemoCost > 0 ? (cost / totalDemoCost) * 100 : 0;

      demographics.push({
        age: row.Age,
        gender: row.Gender,
        percentage: Math.round(percentage * 100) / 100 // 2 decimale
      });
    });

    // Sort by percentage desc
    demographics.sort((a, b) => b.percentage - a.percentage);

    // -------------------------------------------------------------------------
    // INTERESTS (Top 10 + coverage)
    // -------------------------------------------------------------------------
    const interestRows = interestsByCampaign.get(id) || [];
    const totalInterestCost = interestRows.reduce((sum, row) => sum + parseNumber(row.Cost), 0);

    const interestSegments: InterestSegment[] = interestRows.map(row => {
      const cost = parseNumber(row.Cost);
      const percentage = totalInterestCost > 0 ? (cost / totalInterestCost) * 100 : 0;

      return {
        segment: row['Audience segment'],
        cost,
        percentage: Math.round(percentage * 100) / 100
      };
    });

    // Sort by cost desc
    interestSegments.sort((a, b) => b.cost - a.cost);

    // Top 10
    const top10 = interestSegments.slice(0, 10);
    const top10Coverage = top10.reduce((sum, seg) => sum + seg.percentage, 0);

    // -------------------------------------------------------------------------
    // REACH (Peak Reach)
    // -------------------------------------------------------------------------
    const reachData = reachByCampaign.get(id);
    const reach = reachData?.reach || null;
    const frequency = reachData?.frequency || null;
    const isMultiQuarter = (reachData?.count || 0) > 1;
    const reachDisclaimer = isMultiQuarter
      ? 'Peak Reach prikazan (maksimalna vrijednost kroz kvartale) - može biti netočan kod cross-quarter kampanja'
      : undefined;

    // -------------------------------------------------------------------------
    // METADATA
    // -------------------------------------------------------------------------
    const { quarters, months } = getQuartersAndMonths(reg['Start Date'], reg['End Date']);

    // -------------------------------------------------------------------------
    // BUILD MASTER RECORD
    // -------------------------------------------------------------------------
    const master: CampaignMaster = {
      campaignId: id,
      originalName: reg['Original Name'],
      standardizedName: reg['Standardized Name'],

      startDate: reg['Start Date'],
      endDate: reg['End Date'],
      quarter: quarters,
      month: months,

      spend,
      impressions,
      clicks,
      trueViewViews,
      conversions,

      ctr,
      cpc,
      cpm,
      cpv,
      costPerConversion,
      conversionRate,

      reach,
      frequency,
      isMultiQuarter,
      reachDisclaimer,

      demographics,

      interests: top10,
      interestsCoverage: Math.round(top10Coverage * 100) / 100,

      adFormat: met.formats.join(' + ')
    };

    masterData.push(master);
  });

  console.log(`✅ Merged: ${masterData.length} kampanja\n`);

  return masterData;
}

// ============================================================================
// MAIN
// ============================================================================

function main() {
  console.log('🚀 MASTER DATABASE MERGER V2\n');
  console.log('═'.repeat(60) + '\n');

  const masterData = mergeMasterDatabase();

  // Save
  const outputPath = path.join(process.cwd(), 'data', 'master_database_v2.json');
  fs.writeFileSync(outputPath, JSON.stringify(masterData, null, 2), 'utf-8');

  console.log('═'.repeat(60));
  console.log(`\n✅ GOTOVO! Master database spremljena u:\n   ${outputPath}\n`);
  console.log(`📊 Total kampanja: ${masterData.length}\n`);

  // Stats
  const totalSpend = masterData.reduce((sum, c) => sum + c.spend, 0);
  const withReach = masterData.filter(c => c.reach !== null).length;
  const multiQuarter = masterData.filter(c => c.isMultiQuarter).length;

  console.log('📈 Statistika:');
  console.log(`   💰 Total Spend: ${totalSpend.toLocaleString('hr-HR')} €`);
  console.log(`   👥 Kampanja s Reach: ${withReach} (${Math.round(withReach/masterData.length*100)}%)`);
  console.log(`   📅 Multi-quarter kampanje: ${multiQuarter}`);
  console.log(`   ⚠️  Peak Reach disclaimer: ${multiQuarter} kampanja\n`);
}

main();
