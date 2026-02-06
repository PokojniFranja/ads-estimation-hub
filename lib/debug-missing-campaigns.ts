/**
 * DEBUG REPORT: MISSING CAMPAIGNS
 *
 * Pronalazi kampanje koje postoje u CSV-u ali ne u JSON-u
 * i identificira razlog zašto su ispale.
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

interface RegistryRow {
  'Campaign ID': string;
  'Original Name': string;
  'Standardized Name': string;
  'Start Date': string;
  'End Date': string;
}

interface MasterRecord {
  campaignId: string;
  originalName: string;
  spend: number;
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

// ============================================================================
// DEBUG MISSING CAMPAIGNS
// ============================================================================

function debugMissingCampaigns() {
  console.log('🚨 DEBUG REPORT: MISSING CAMPAIGNS\n');
  console.log('═'.repeat(80) + '\n');

  const dataDir = path.join(process.cwd(), 'data');
  const rawDir = path.join(dataDir, 'raw');

  // --------------------------------------------------------------------------
  // 1. LOAD ALL DATA SOURCES
  // --------------------------------------------------------------------------
  console.log('📂 Učitavam podatke...\n');

  // Metrics CSV
  const metricsPath = path.join(rawDir, 'campaign_metrics', '2025_metrics.csv');
  const metricsData = readCSV<MetricsRow>(metricsPath);
  console.log(`✅ Metrics CSV: ${metricsData.length} redaka`);

  // Registry
  const registryPath = path.join(dataDir, 'campaign_registry.csv');
  const registryData = readCSV<RegistryRow>(registryPath);
  const registryIds = new Set(registryData.map(r => r['Campaign ID']));
  console.log(`✅ Registry: ${registryData.length} kampanja`);

  // JSON Master Database
  const jsonPath = path.join(dataDir, 'master_database_v2.json');
  const jsonData: MasterRecord[] = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const jsonIds = new Set(jsonData.map(r => r.campaignId));
  console.log(`✅ JSON Master: ${jsonData.length} kampanja\n`);

  // --------------------------------------------------------------------------
  // 2. AGGREGATE METRICS BY CAMPAIGN ID
  // --------------------------------------------------------------------------
  console.log('🔄 Agregiram metrics po Campaign ID...\n');

  const metricsAggregated = new Map<string, { name: string, spend: number, rows: number }>();

  metricsData.forEach(row => {
    const id = row['Campaign ID'];
    const name = row.Campaign;
    const spend = parseNumber(row.Cost);

    if (!metricsAggregated.has(id)) {
      metricsAggregated.set(id, { name, spend, rows: 1 });
    } else {
      const existing = metricsAggregated.get(id)!;
      existing.spend += spend;
      existing.rows++;
    }
  });

  const multiFormatCampaigns = Array.from(metricsAggregated.entries())
    .filter(([_, data]) => data.rows > 1);

  console.log(`✅ Agregacija gotova:`);
  console.log(`   Unique Campaign IDs u CSV-u: ${metricsAggregated.size}`);
  console.log(`   Kampanja s multiple ad formatima: ${multiFormatCampaigns.length}`);
  console.log();

  // --------------------------------------------------------------------------
  // 3. FIND MISSING CAMPAIGNS
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n🔍 PRONALAZIM IZGUBLJENE KAMPANJE\n');

  const missingInJson: Array<{
    id: string;
    name: string;
    spend: number;
    inRegistry: boolean;
    reason: string;
  }> = [];

  metricsAggregated.forEach((data, id) => {
    if (!jsonIds.has(id)) {
      const inRegistry = registryIds.has(id);
      let reason = 'UNKNOWN';

      if (!inRegistry) {
        reason = 'NOT IN REGISTRY (filtered out as non-HR or excluded brand)';
      } else {
        reason = 'IN REGISTRY BUT MISSING FROM JSON (bug in merger?)';
      }

      missingInJson.push({
        id,
        name: data.name,
        spend: data.spend,
        inRegistry,
        reason
      });
    }
  });

  console.log(`⚠️  TOTAL MISSING: ${missingInJson.length} kampanja\n`);

  const totalMissingSpend = missingInJson.reduce((sum, c) => sum + c.spend, 0);
  console.log(`💰 TOTAL IZGUBLJENI SPEND: ${formatNumber(totalMissingSpend)} €\n`);

  // --------------------------------------------------------------------------
  // 4. TOP 10 MISSING BY SPEND
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n💸 TOP 10 IZGUBLJENIH KAMPANJA (po spend-u)\n');

  const top10Missing = [...missingInJson]
    .sort((a, b) => b.spend - a.spend)
    .slice(0, 10);

  top10Missing.forEach((campaign, index) => {
    console.log(`${index + 1}. ${campaign.name}`);
    console.log(`   Campaign ID: ${campaign.id}`);
    console.log(`   Spend:       ${formatNumber(campaign.spend)} €`);
    console.log(`   In Registry: ${campaign.inRegistry ? '✅ YES' : '❌ NO'}`);
    console.log(`   Reason:      ${campaign.reason}`);
    console.log();
  });

  // --------------------------------------------------------------------------
  // 5. BREAKDOWN BY REASON
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📊 BREAKDOWN PO RAZLOGU GUBITKA\n');

  const notInRegistry = missingInJson.filter(c => !c.inRegistry);
  const inRegistryButMissing = missingInJson.filter(c => c.inRegistry);

  console.log(`❌ NOT IN REGISTRY (filtriran kao non-HR ili excluded brand):`);
  console.log(`   Count: ${notInRegistry.length}`);
  console.log(`   Total Spend: ${formatNumber(notInRegistry.reduce((sum, c) => sum + c.spend, 0))} €`);
  console.log();

  console.log(`⚠️  IN REGISTRY BUT MISSING FROM JSON (BUG!):`);
  console.log(`   Count: ${inRegistryButMissing.length}`);
  console.log(`   Total Spend: ${formatNumber(inRegistryButMissing.reduce((sum, c) => sum + c.spend, 0))} €`);
  console.log();

  if (inRegistryButMissing.length > 0) {
    console.log(`   🚨 KRITIČAN BUG: Ove kampanje su u Registry-ju ali nisu u JSON-u!`);
    console.log(`   Lista:`);
    inRegistryButMissing.forEach((c, idx) => {
      console.log(`   ${idx + 1}. ${c.name} (${c.id}) - ${formatNumber(c.spend)} €`);
    });
    console.log();
  }

  // --------------------------------------------------------------------------
  // 6. CHECK: MULTI-FORMAT AGGREGATION
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n🔧 PROVJERA: Multi-format agregacija\n');

  console.log(`Kampanja s više ad formata u CSV-u: ${multiFormatCampaigns.length}\n`);
  console.log(`Top 5 primjera (provjera da li se zbrajaju troškovi):\n`);

  multiFormatCampaigns.slice(0, 5).forEach(([id, data], index) => {
    const inJson = jsonIds.has(id);
    const jsonSpend = inJson ? jsonData.find(j => j.campaignId === id)?.spend : null;

    console.log(`${index + 1}. ${data.name}`);
    console.log(`   Campaign ID: ${id}`);
    console.log(`   CSV rows: ${data.rows}`);
    console.log(`   CSV Total Spend: ${formatNumber(data.spend)} €`);
    console.log(`   JSON Spend: ${jsonSpend !== null ? formatNumber(jsonSpend) + ' €' : 'NOT IN JSON'}`);
    console.log(`   Match: ${jsonSpend !== null && Math.abs(data.spend - jsonSpend) < 0.01 ? '✅' : '❌'}`);
    console.log();
  });

  // --------------------------------------------------------------------------
  // 7. MCDONALD'S SPECIFIC CHECK
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n🍔 MCDONALD\'S SPECIFIC CHECK\n');

  const mcdonaldsCsv = Array.from(metricsAggregated.entries())
    .filter(([_, data]) => data.name.toLowerCase().includes('mcdonald'));

  const mcdonaldsJson = jsonData.filter(c =>
    c.originalName.toLowerCase().includes('mcdonald')
  );

  const mcdonaldsMissing = mcdonaldsCsv.filter(([id, _]) => !jsonIds.has(id));

  console.log(`McDonald's u CSV-u: ${mcdonaldsCsv.length} kampanja`);
  console.log(`McDonald's u JSON-u: ${mcdonaldsJson.length} kampanja`);
  console.log(`McDonald's MISSING: ${mcdonaldsMissing.length} kampanja\n`);

  const mcCsvSpend = mcdonaldsCsv.reduce((sum, [_, data]) => sum + data.spend, 0);
  const mcJsonSpend = mcdonaldsJson.reduce((sum, c) => sum + c.spend, 0);
  const mcDiff = mcCsvSpend - mcJsonSpend;

  console.log(`CSV Total Spend: ${formatNumber(mcCsvSpend)} €`);
  console.log(`JSON Total Spend: ${formatNumber(mcJsonSpend)} €`);
  console.log(`DIFFERENCE: ${formatNumber(Math.abs(mcDiff))} € (${mcDiff > 0 ? 'MISSING' : 'EXTRA'})\n`);

  if (mcdonaldsMissing.length > 0) {
    console.log(`Izgubljene McDonald's kampanje:`);
    mcdonaldsMissing.forEach(([id, data]) => {
      const inRegistry = registryIds.has(id);
      console.log(`   - ${data.name} (${id})`);
      console.log(`     Spend: ${formatNumber(data.spend)} € | In Registry: ${inRegistry ? 'YES' : 'NO'}`);
    });
    console.log();
  }

  // --------------------------------------------------------------------------
  // SUMMARY
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📋 SUMMARY\n');
  console.log(`Total kampanja u CSV-u: ${metricsAggregated.size}`);
  console.log(`Total kampanja u JSON-u: ${jsonData.length}`);
  console.log(`MISSING kampanja: ${missingInJson.length}`);
  console.log(`Missing Spend: ${formatNumber(totalMissingSpend)} €\n`);
  console.log(`Razlog #1: Not in Registry (${notInRegistry.length}) - ${formatNumber(notInRegistry.reduce((s, c) => s + c.spend, 0))} €`);
  console.log(`Razlog #2: Bug in Merger (${inRegistryButMissing.length}) - ${formatNumber(inRegistryButMissing.reduce((s, c) => s + c.spend, 0))} €\n`);
  console.log('═'.repeat(80));
  console.log();
}

// ============================================================================
// MAIN
// ============================================================================

debugMissingCampaigns();
