/**
 * DEEP AUDIT - DATA V2 SOURCE OF TRUTH
 *
 * Audit pipeline:
 * 1. Raw Total Spend (prije filtera)
 * 2. Location Filter (non-HR kampanje)
 * 3. McDonald's Worldwide Bug (3 kampanje)
 * 4. Finalni HR Spend
 */

import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';

// ============================================================================
// TIPOVI
// ============================================================================

interface MetricsRow {
  'Campaign ID': string;
  Campaign: string;
  'Ad format': string;
  Cost: string;
  'Impr.': string;
  Clicks: string;
  'TrueView views': string;
  Conversions: string;
}

interface LocationRow {
  'Campaign ID': string;
  Campaign: string;
  'Campaign type': string;
  'Country/Territory (User location)': string;
  Cost: string;
}

// ============================================================================
// HELPER
// ============================================================================

function parseNumber(value: string | undefined | null): number {
  if (!value) return 0;
  let cleaned = value.replace(/[^\d.,-]/g, '');
  cleaned = cleaned.replace(/,/g, '');
  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

function readCSV<T>(filePath: string, delimiter: string = ','): T[] {
  let content = fs.readFileSync(filePath, 'utf-8');
  // Remove BOM if present
  if (content.charCodeAt(0) === 0xFEFF) {
    content = content.substring(1);
  }
  const parsed = Papa.parse(content, {
    header: true,
    skipEmptyLines: true,
    delimiter
  });
  return parsed.data as T[];
}

function formatNumber(num: number): string {
  return num.toLocaleString('hr-HR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ============================================================================
// EXCLUSION LISTS
// ============================================================================

const WORLDWIDE_MCDONALD_BUGS = [
  "McDonald's IceCoffe June - August 2025 (YT) - CPV",
  "McDonald's Stripsi June - July 2025 (YT) - Bumper",
  "McDonald's Stripsi June - July 2025 (YT) - CPV"
];

// ============================================================================
// DEEP AUDIT
// ============================================================================

function deepAudit() {
  console.log('🔍 DEEP AUDIT - DATA V2 SOURCE OF TRUTH\n');
  console.log('═'.repeat(80) + '\n');

  const baseDir = path.join(process.cwd(), 'data - v2');

  // --------------------------------------------------------------------------
  // AUDIT 1: RAW TOTAL SPEND
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('📊 AUDIT 1: RAW TOTAL SPEND (prije filtera)\n');

  const metricsPath = path.join(baseDir, 'campaign metrics - v2', 'campaign metrics - v2.csv');
  const metricsData = readCSV<MetricsRow>(metricsPath, ';');

  console.log(`✅ Campaign Metrics V2 učitan: ${metricsData.length} redaka\n`);

  // Aggregate by Campaign ID
  const metricsAggregated = new Map<string, {
    name: string;
    spend: number;
    impressions: number;
    clicks: number;
    formats: Set<string>;
  }>();

  metricsData.forEach(row => {
    const id = row['Campaign ID'];
    const name = row.Campaign;
    const spend = parseNumber(row.Cost);
    const impressions = parseNumber(row['Impr.']);
    const clicks = parseNumber(row.Clicks);
    const format = row['Ad format'];

    if (!metricsAggregated.has(id)) {
      metricsAggregated.set(id, {
        name,
        spend,
        impressions,
        clicks,
        formats: new Set([format])
      });
    } else {
      const existing = metricsAggregated.get(id)!;
      existing.spend += spend;
      existing.impressions += impressions;
      existing.clicks += clicks;
      existing.formats.add(format);
    }
  });

  const rawTotalSpend = Array.from(metricsAggregated.values()).reduce((sum, c) => sum + c.spend, 0);

  console.log(`📈 RAW TOTALS (ABSOLUTE TRUTH):`);
  console.log(`   Total redaka u CSV-u:     ${metricsData.length}`);
  console.log(`   Unique Campaign IDs:      ${metricsAggregated.size}`);
  console.log(`   Multi-format kampanja:    ${Array.from(metricsAggregated.values()).filter(c => c.formats.size > 1).length}`);
  console.log(`   \n   💰 RAW TOTAL SPEND:      ${formatNumber(rawTotalSpend)} €\n`);

  // --------------------------------------------------------------------------
  // AUDIT 2: LOCATION FILTER (NON-HR CAMPAIGNS)
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('🌍 AUDIT 2: LOCATION FILTER (Non-HR kampanje)\n');

  const locationPath = path.join(baseDir, 'campaign - location - v2', 'campaign - location - v2 - new.csv');
  const locationData = readCSV<LocationRow>(locationPath, ';');

  console.log(`✅ Location data učitana: ${locationData.length} redaka\n`);

  // Identify campaigns by location
  const campaignLocations = new Map<string, {
    name: string;
    countries: Set<string>;
    totalSpend: number;
    hrSpend: number;
    nonHrSpend: number;
  }>();

  locationData.forEach(row => {
    const id = row['Campaign ID'];
    const name = row.Campaign;
    const country = row['Country/Territory (User location)'];
    const spend = parseNumber(row.Cost);

    if (!campaignLocations.has(id)) {
      campaignLocations.set(id, {
        name,
        countries: new Set([country]),
        totalSpend: spend,
        hrSpend: 0,
        nonHrSpend: 0
      });
    } else {
      const existing = campaignLocations.get(id)!;
      existing.countries.add(country);
      existing.totalSpend += spend;
    }

    // Classify spend
    const location = campaignLocations.get(id)!;
    if (country && (country.toLowerCase().includes('croatia') || country.toLowerCase().includes('hrvatska'))) {
      location.hrSpend += spend;
    } else {
      location.nonHrSpend += spend;
    }
  });

  // Find non-HR campaigns (0% HR spend)
  const nonHrCampaigns = Array.from(campaignLocations.entries())
    .filter(([_, data]) => data.hrSpend === 0)
    .map(([id, data]) => ({
      id,
      name: data.name,
      spend: data.totalSpend,
      countries: Array.from(data.countries)
    }));

  const totalNonHrSpend = nonHrCampaigns.reduce((sum, c) => sum + c.spend, 0);

  console.log(`📊 LOCATION ANALYSIS:`);
  console.log(`   Total kampanja u location data: ${campaignLocations.size}`);
  console.log(`   Non-HR kampanja (0% HR):         ${nonHrCampaigns.length}`);
  console.log(`   \n   💸 NON-HR SPEND:                ${formatNumber(totalNonHrSpend)} €\n`);

  if (nonHrCampaigns.length > 0) {
    console.log(`🚫 TOP 10 NON-HR KAMPANJA:\n`);
    nonHrCampaigns
      .sort((a, b) => b.spend - a.spend)
      .slice(0, 10)
      .forEach((c, idx) => {
        console.log(`${idx + 1}. ${c.name}`);
        console.log(`   ID: ${c.id}`);
        console.log(`   Spend: ${formatNumber(c.spend)} €`);
        console.log(`   Countries: ${c.countries.join(', ')}`);
        console.log();
      });
  }

  // --------------------------------------------------------------------------
  // AUDIT 3: McDONALD'S WORLDWIDE BUG
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('🍔 AUDIT 3: McDONALD\'S WORLDWIDE BUG (3 kampanje)\n');

  const worldwideMcCampaigns = Array.from(metricsAggregated.entries())
    .filter(([_, data]) => {
      const name = data.name.toLowerCase();
      return WORLDWIDE_MCDONALD_BUGS.some(bugName =>
        name.includes(bugName.toLowerCase())
      );
    })
    .map(([id, data]) => ({
      id,
      name: data.name,
      spend: data.spend
    }));

  const totalWorldwideMcSpend = worldwideMcCampaigns.reduce((sum, c) => sum + c.spend, 0);

  console.log(`🔍 WORLDWIDE McDONALD'S KAMPANJE:`);
  console.log(`   Pronađeno kampanja: ${worldwideMcCampaigns.length}`);
  console.log(`   \n   💸 WORLDWIDE McD SPEND: ${formatNumber(totalWorldwideMcSpend)} €\n`);

  if (worldwideMcCampaigns.length > 0) {
    console.log(`📋 LISTA:\n`);
    worldwideMcCampaigns.forEach((c, idx) => {
      console.log(`${idx + 1}. ${c.name}`);
      console.log(`   ID: ${c.id}`);
      console.log(`   Spend: ${formatNumber(c.spend)} €`);
      console.log();
    });
  }

  // --------------------------------------------------------------------------
  // AUDIT 4: FINALNI HR SPEND
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('✅ AUDIT 4: FINALNI HR SPEND\n');

  // Get list of excluded Campaign IDs
  const nonHrIds = new Set(nonHrCampaigns.map(c => c.id));
  const worldwideMcIds = new Set(worldwideMcCampaigns.map(c => c.id));

  // Calculate final HR campaigns
  const finalHrCampaigns = Array.from(metricsAggregated.entries())
    .filter(([id, _]) => {
      // Exclude if non-HR
      if (nonHrIds.has(id)) return false;
      // Exclude if Worldwide McD bug
      if (worldwideMcIds.has(id)) return false;
      return true;
    })
    .map(([id, data]) => ({
      id,
      name: data.name,
      spend: data.spend,
      impressions: data.impressions,
      clicks: data.clicks,
      formats: Array.from(data.formats)
    }));

  const finalHrSpend = finalHrCampaigns.reduce((sum, c) => sum + c.spend, 0);

  console.log(`📊 FINALNI HR PODACI:`);
  console.log(`   HR kampanja (nakon filtera): ${finalHrCampaigns.length}`);
  console.log(`   \n   💰 FINALNI HR SPEND:          ${formatNumber(finalHrSpend)} €\n`);

  // --------------------------------------------------------------------------
  // SUMMARY WATERFALL
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📈 WATERFALL ANALIZA: Od Raw do Final\n');

  console.log(`1️⃣  RAW TOTAL SPEND (Google Ads export):     ${formatNumber(rawTotalSpend)} €`);
  console.log(`    └─ Unique kampanja:                       ${metricsAggregated.size}\n`);

  console.log(`2️⃣  EXCLUDED: Non-HR Markets:                -${formatNumber(totalNonHrSpend)} €`);
  console.log(`    └─ Kampanja:                              ${nonHrCampaigns.length}\n`);

  console.log(`3️⃣  EXCLUDED: Worldwide McD Bug:             -${formatNumber(totalWorldwideMcSpend)} €`);
  console.log(`    └─ Kampanja:                              ${worldwideMcCampaigns.length}\n`);

  const afterExclusions = rawTotalSpend - totalNonHrSpend - totalWorldwideMcSpend;
  console.log(`4️⃣  AFTER EXCLUSIONS:                        ${formatNumber(afterExclusions)} €\n`);

  console.log(`✅  FINALNI HR SPEND:                         ${formatNumber(finalHrSpend)} €`);
  console.log(`    └─ HR kampanja:                           ${finalHrCampaigns.length}\n`);

  // Sanity check
  const diff = Math.abs(afterExclusions - finalHrSpend);
  if (diff < 0.01) {
    console.log(`✅ SANITY CHECK: PASS (razlika: ${formatNumber(diff)} €)\n`);
  } else {
    console.log(`⚠️  SANITY CHECK: FAIL (razlika: ${formatNumber(diff)} €)\n`);
  }

  // --------------------------------------------------------------------------
  // EXPORT RESULTS
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📤 EXPORT: Spremam rezultate...\n');

  const results = {
    audit: {
      timestamp: new Date().toISOString(),
      rawTotalSpend,
      nonHrSpend: totalNonHrSpend,
      worldwideMcSpend: totalWorldwideMcSpend,
      finalHrSpend,
      totalCampaigns: metricsAggregated.size,
      hrCampaigns: finalHrCampaigns.length,
      excludedCampaigns: nonHrCampaigns.length + worldwideMcCampaigns.length
    },
    nonHrCampaigns,
    worldwideMcCampaigns,
    waterfall: [
      { step: 'Raw Total', spend: rawTotalSpend, campaigns: metricsAggregated.size },
      { step: 'Excluded: Non-HR', spend: -totalNonHrSpend, campaigns: -nonHrCampaigns.length },
      { step: 'Excluded: Worldwide McD', spend: -totalWorldwideMcSpend, campaigns: -worldwideMcCampaigns.length },
      { step: 'Final HR', spend: finalHrSpend, campaigns: finalHrCampaigns.length }
    ]
  };

  const outputPath = path.join(process.cwd(), 'data - v2', 'deep_audit_v2_results.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2), 'utf-8');

  console.log(`✅ Rezultati spremljeni u: ${outputPath}\n`);

  console.log('═'.repeat(80));
  console.log('\n🎯 DEEP AUDIT ZAVRŠEN!\n');
  console.log(`RAW SPEND (Google Ads):  ${formatNumber(rawTotalSpend)} €`);
  console.log(`EXCLUDED TOTAL:          ${formatNumber(totalNonHrSpend + totalWorldwideMcSpend)} €`);
  console.log(`FINALNI HR SPEND:        ${formatNumber(finalHrSpend)} €\n`);
  console.log('═'.repeat(80));
  console.log();
}

// ============================================================================
// MAIN
// ============================================================================

deepAudit();
