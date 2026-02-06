/**
 * GRAND TOTALS RECONCILIATION TEST
 *
 * Uspoređuje originalne CSV podatke s JSON master database-om
 * da osigura 100% integritet podataka.
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
  Cost: string;
}

interface MasterRecord {
  campaignId: string;
  spend: number;
  impressions: number;
  clicks: number;
}

// ============================================================================
// HELPER
// ============================================================================

function parseNumber(value: string | undefined | null): number {
  if (!value) return 0;
  let cleaned = value.replace(/[^\d.,-]/g, '');
  // Američki format: zarez = thousands separator, točka = decimal
  cleaned = cleaned.replace(/,/g, '');
  const num = parseFloat(cleaned);
  return isNaN(num) ? 0 : num;
}

function readCSV<T>(filePath: string): T[] {
  const content = fs.readFileSync(filePath, 'utf-8');
  const parsed = Papa.parse(content, {
    header: true,
    skipEmptyLines: true
  });
  return parsed.data as T[];
}

function formatNumber(num: number): string {
  return num.toLocaleString('hr-HR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatPercent(num: number): string {
  return num.toFixed(4) + '%';
}

// ============================================================================
// RECONCILIATION
// ============================================================================

function runReconciliation() {
  console.log('🔍 GRAND TOTALS RECONCILIATION TEST\n');
  console.log('═'.repeat(70) + '\n');

  const dataDir = path.join(process.cwd(), 'data');
  const rawDir = path.join(dataDir, 'raw');

  // --------------------------------------------------------------------------
  // 1. ORIGINAL CSV TOTALS
  // --------------------------------------------------------------------------
  console.log('📂 Učitavam originalni CSV...\n');

  const csvPath = path.join(rawDir, 'campaign_metrics', '2025_metrics.csv');
  const csvData = readCSV<MetricsRow>(csvPath);

  const csvCampaignIds = new Set<string>();
  let csvTotalCost = 0;
  let csvTotalImpressions = 0;
  let csvTotalClicks = 0;

  csvData.forEach(row => {
    csvCampaignIds.add(row['Campaign ID']);
    csvTotalCost += parseNumber(row.Cost);
    csvTotalImpressions += parseNumber(row['Impr.']);
    csvTotalClicks += parseNumber(row.Clicks);
  });

  console.log(`✅ CSV učitan:`);
  console.log(`   Redaka: ${csvData.length}`);
  console.log(`   Unique Campaign ID-jeva: ${csvCampaignIds.size}`);
  console.log(`   Total Cost:        ${formatNumber(csvTotalCost)} €`);
  console.log(`   Total Impressions: ${formatNumber(csvTotalImpressions)}`);
  console.log(`   Total Clicks:      ${formatNumber(csvTotalClicks)}`);
  console.log();

  // --------------------------------------------------------------------------
  // 2. JSON TOTALS
  // --------------------------------------------------------------------------
  console.log('📂 Učitavam JSON master database...\n');

  const jsonPath = path.join(dataDir, 'master_database_v2.json');
  const jsonData: MasterRecord[] = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  const jsonCampaignIds = new Set<string>();
  let jsonTotalSpend = 0;
  let jsonTotalImpressions = 0;
  let jsonTotalClicks = 0;

  jsonData.forEach(record => {
    jsonCampaignIds.add(record.campaignId);
    jsonTotalSpend += record.spend;
    jsonTotalImpressions += record.impressions;
    jsonTotalClicks += record.clicks;
  });

  console.log(`✅ JSON učitan:`);
  console.log(`   Kampanja: ${jsonData.length}`);
  console.log(`   Unique Campaign ID-jeva: ${jsonCampaignIds.size}`);
  console.log(`   Total Spend:       ${formatNumber(jsonTotalSpend)} €`);
  console.log(`   Total Impressions: ${formatNumber(jsonTotalImpressions)}`);
  console.log(`   Total Clicks:      ${formatNumber(jsonTotalClicks)}`);
  console.log();

  // --------------------------------------------------------------------------
  // 3. RECONCILIATION
  // --------------------------------------------------------------------------
  console.log('═'.repeat(70));
  console.log('\n🔎 RECONCILIATION REZULTATI\n');

  // COST/SPEND
  const costDiff = jsonTotalSpend - csvTotalCost;
  const costDiffPercent = (costDiff / csvTotalCost) * 100;

  console.log('💰 COST/SPEND:');
  console.log(`   CSV:        ${formatNumber(csvTotalCost)} €`);
  console.log(`   JSON:       ${formatNumber(jsonTotalSpend)} €`);
  console.log(`   Difference: ${formatNumber(Math.abs(costDiff))} € (${formatPercent(Math.abs(costDiffPercent))})`);
  console.log(`   Status:     ${Math.abs(costDiffPercent) < 0.01 ? '✅ MATCH' : '❌ MISMATCH'}`);
  console.log();

  // IMPRESSIONS
  const impressionsDiff = jsonTotalImpressions - csvTotalImpressions;
  const impressionsDiffPercent = (impressionsDiff / csvTotalImpressions) * 100;

  console.log('👁️  IMPRESSIONS:');
  console.log(`   CSV:        ${formatNumber(csvTotalImpressions)}`);
  console.log(`   JSON:       ${formatNumber(jsonTotalImpressions)}`);
  console.log(`   Difference: ${formatNumber(Math.abs(impressionsDiff))} (${formatPercent(Math.abs(impressionsDiffPercent))})`);
  console.log(`   Status:     ${Math.abs(impressionsDiffPercent) < 0.01 ? '✅ MATCH' : '❌ MISMATCH'}`);
  console.log();

  // CLICKS
  const clicksDiff = jsonTotalClicks - csvTotalClicks;
  const clicksDiffPercent = (clicksDiff / csvTotalClicks) * 100;

  console.log('🖱️  CLICKS:');
  console.log(`   CSV:        ${formatNumber(csvTotalClicks)}`);
  console.log(`   JSON:       ${formatNumber(jsonTotalClicks)}`);
  console.log(`   Difference: ${formatNumber(Math.abs(clicksDiff))} (${formatPercent(Math.abs(clicksDiffPercent))})`);
  console.log(`   Status:     ${Math.abs(clicksDiffPercent) < 0.01 ? '✅ MATCH' : '❌ MISMATCH'}`);
  console.log();

  // CAMPAIGN COUNT
  console.log('🔢 CAMPAIGN COUNT:');
  console.log(`   CSV Unique IDs:  ${csvCampaignIds.size}`);
  console.log(`   JSON Records:    ${jsonCampaignIds.size}`);
  console.log(`   Expected:        547`);
  console.log(`   Status:          ${jsonCampaignIds.size === 547 ? '✅ MATCH' : '❌ MISMATCH'}`);
  console.log();

  // CAMPAIGN ID MATCHING
  const inCsvNotJson = Array.from(csvCampaignIds).filter(id => !jsonCampaignIds.has(id));
  const inJsonNotCsv = Array.from(jsonCampaignIds).filter(id => !csvCampaignIds.has(id));

  console.log('🆔 CAMPAIGN ID MATCHING:');
  console.log(`   IDs in CSV but not JSON: ${inCsvNotJson.length}`);
  console.log(`   IDs in JSON but not CSV: ${inJsonNotCsv.length}`);

  if (inCsvNotJson.length > 0) {
    console.log(`   ⚠️  Missing in JSON: ${inCsvNotJson.slice(0, 5).join(', ')}${inCsvNotJson.length > 5 ? '...' : ''}`);
  }
  if (inJsonNotCsv.length > 0) {
    console.log(`   ⚠️  Extra in JSON: ${inJsonNotCsv.slice(0, 5).join(', ')}${inJsonNotCsv.length > 5 ? '...' : ''}`);
  }

  console.log(`   Status:          ${inCsvNotJson.length === 0 && inJsonNotCsv.length === 0 ? '✅ PERFECT MATCH' : '❌ MISMATCH'}`);
  console.log();

  // --------------------------------------------------------------------------
  // 4. FINAL VERDICT
  // --------------------------------------------------------------------------
  console.log('═'.repeat(70));
  console.log();

  const allMatch =
    Math.abs(costDiffPercent) < 0.01 &&
    Math.abs(impressionsDiffPercent) < 0.01 &&
    Math.abs(clicksDiffPercent) < 0.01 &&
    jsonCampaignIds.size === 547 &&
    inCsvNotJson.length === 0 &&
    inJsonNotCsv.length === 0;

  if (allMatch) {
    console.log('🎉 FINAL VERDICT: ✅ 100% INTEGRITY CONFIRMED');
    console.log('   Master Database V2 is READY FOR DASHBOARD! 🚀');
  } else {
    console.log('⚠️  FINAL VERDICT: ❌ INTEGRITY ISSUES DETECTED');
    console.log('   Review the mismatches above before proceeding.');
  }
  console.log();
}

// ============================================================================
// MAIN
// ============================================================================

runReconciliation();
