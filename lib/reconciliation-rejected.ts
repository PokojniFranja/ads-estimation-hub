/**
 * RECONCILIATION: REJECTED CAMPAIGNS
 *
 * Pronalazi sve kampanje iz metrics CSV-a koje NISU ušle u master database
 * i identificira razlog odbacivanja.
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

interface RejectedCampaign {
  campaignId: string;
  originalName: string;
  spend: number;
  reason: string;
  isMcDonalds: boolean;
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
// EXCLUSION LIST CHECKER
// ============================================================================

function checkExclusionReason(campaignName: string): string | null {
  const name = campaignName.toLowerCase();

  // Market exclusions
  if (name.includes('si-sl') || name.includes('slovenia') || name.includes('slo')) {
    return 'EXCLUDED MARKET: Slovenia (SI-SL)';
  }
  if (name.includes('rs-sr') || name.includes('srbija') || name.includes('serbia')) {
    return 'EXCLUDED MARKET: Serbia (RS-SR)';
  }
  if (name.includes('me-me') || name.includes('crna gora') || name.includes('montenegro')) {
    return 'EXCLUDED MARKET: Montenegro (ME-ME)';
  }
  if (name.includes('bih') || name.includes('bosna') || name.includes('bosnia')) {
    return 'EXCLUDED MARKET: Bosnia (BiH)';
  }
  if (name.includes('mison')) {
    return 'EXCLUDED MARKET: Mison (multi-region)';
  }
  if (name.includes('elgrad')) {
    return 'EXCLUDED MARKET: Elgrad (undefined)';
  }
  if (name.includes('alwaysonslo')) {
    return 'EXCLUDED MARKET: AlwaysOnSLO';
  }
  if (name.includes('alwaysonbih')) {
    return 'EXCLUDED MARKET: AlwaysOnBiH';
  }

  // Worldwide bug - specific McDonald's campaigns
  if (name.includes("mcdonald's icecoffee june - august 2025 (yt) - cpv")) {
    return 'WORLDWIDE BUG: Excluded worldwide campaign';
  }
  if (name.includes("mcdonald's stripsi june - july 2025 (yt)")) {
    return 'WORLDWIDE BUG: Excluded worldwide campaign';
  }

  return null;
}

// ============================================================================
// RECONCILIATION
// ============================================================================

function reconcileRejectedCampaigns() {
  console.log('💰 RECONCILIATION: REJECTED CAMPAIGNS\n');
  console.log('═'.repeat(80) + '\n');

  const dataDir = path.join(process.cwd(), 'data');
  const rawDir = path.join(dataDir, 'raw');

  // --------------------------------------------------------------------------
  // 1. LOAD DATA
  // --------------------------------------------------------------------------
  console.log('📂 Učitavam podatke...\n');

  // Metrics CSV (ABSOLUTE TRUTH)
  const metricsPath = path.join(rawDir, 'campaign_metrics', '2025_metrics.csv');
  const metricsData = readCSV<MetricsRow>(metricsPath);
  console.log(`✅ Metrics CSV: ${metricsData.length} redaka`);

  // Aggregate by Campaign ID
  const metricsAggregated = new Map<string, { name: string, spend: number }>();
  metricsData.forEach(row => {
    const id = row['Campaign ID'];
    const name = row.Campaign;
    const spend = parseNumber(row.Cost);

    if (!metricsAggregated.has(id)) {
      metricsAggregated.set(id, { name, spend });
    } else {
      metricsAggregated.get(id)!.spend += spend;
    }
  });

  const csvTotalSpend = Array.from(metricsAggregated.values()).reduce((sum, c) => sum + c.spend, 0);
  console.log(`   Unique Campaign IDs: ${metricsAggregated.size}`);
  console.log(`   ABSOLUTE TOTAL SPEND: ${formatNumber(csvTotalSpend)} €\n`);

  // Registry
  const registryPath = path.join(dataDir, 'campaign_registry.csv');
  const registryData = readCSV<RegistryRow>(registryPath);
  const registryIds = new Set(registryData.map(r => r['Campaign ID']));
  console.log(`✅ Registry: ${registryData.length} kampanja`);
  const registrySpend = Array.from(metricsAggregated.entries())
    .filter(([id, _]) => registryIds.has(id))
    .reduce((sum, [_, data]) => sum + data.spend, 0);
  console.log(`   Registry Total Spend: ${formatNumber(registrySpend)} €\n`);

  // JSON Master
  const jsonPath = path.join(dataDir, 'master_database_v2.json');
  const jsonData: MasterRecord[] = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  const jsonIds = new Set(jsonData.map(r => r.campaignId));
  const jsonTotalSpend = jsonData.reduce((sum, c) => sum + c.spend, 0);
  console.log(`✅ JSON Master: ${jsonData.length} kampanja`);
  console.log(`   JSON Total Spend: ${formatNumber(jsonTotalSpend)} €\n`);

  // --------------------------------------------------------------------------
  // 2. FIND REJECTED CAMPAIGNS
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n🔍 PRONALAZIM ODBAČENE KAMPANJE\n');

  const rejectedCampaigns: RejectedCampaign[] = [];

  metricsAggregated.forEach((data, id) => {
    if (!jsonIds.has(id)) {
      const inRegistry = registryIds.has(id);
      let reason = 'UNKNOWN';

      if (!inRegistry) {
        // Check exclusion list
        const exclusionReason = checkExclusionReason(data.name);
        if (exclusionReason) {
          reason = exclusionReason;
        } else {
          reason = 'NOT IN REGISTRY (reason unclear - check registry-builder.ts logic)';
        }
      } else {
        reason = 'IN REGISTRY BUT NOT IN JSON (merger bug?)';
      }

      rejectedCampaigns.push({
        campaignId: id,
        originalName: data.name,
        spend: data.spend,
        reason,
        isMcDonalds: data.name.toLowerCase().includes('mcdonald')
      });
    }
  });

  const totalRejectedSpend = rejectedCampaigns.reduce((sum, c) => sum + c.spend, 0);

  console.log(`⚠️  TOTAL REJECTED: ${rejectedCampaigns.length} kampanja`);
  console.log(`💸 TOTAL REJECTED SPEND: ${formatNumber(totalRejectedSpend)} €\n`);

  console.log(`📊 Breakdown:`);
  console.log(`   CSV Absolute Total:  ${formatNumber(csvTotalSpend)} €`);
  console.log(`   JSON Master Total:   ${formatNumber(jsonTotalSpend)} €`);
  console.log(`   DIFFERENCE:          ${formatNumber(csvTotalSpend - jsonTotalSpend)} €\n`);

  // --------------------------------------------------------------------------
  // 3. MCDONALD'S REJECTED CAMPAIGNS
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n🍔 ODBAČENE McDONALD\'S KAMPANJE\n');

  const mcRejected = rejectedCampaigns.filter(c => c.isMcDonalds);
  const mcRejectedSpend = mcRejected.reduce((sum, c) => sum + c.spend, 0);

  console.log(`Total odbačenih McDonald's kampanja: ${mcRejected.length}`);
  console.log(`Total odbačeni spend: ${formatNumber(mcRejectedSpend)} €\n`);

  if (mcRejected.length > 0) {
    console.log(`📋 LISTA ODBAČENIH McDONALD'S KAMPANJA:\n`);
    mcRejected
      .sort((a, b) => b.spend - a.spend)
      .forEach((campaign, index) => {
        console.log(`${index + 1}. ${campaign.originalName}`);
        console.log(`   Campaign ID: ${campaign.campaignId}`);
        console.log(`   Spend:       ${formatNumber(campaign.spend)} €`);
        console.log(`   Reason:      ${campaign.reason}`);
        console.log();
      });
  } else {
    console.log(`✅ Nema odbačenih McDonald's kampanja!\n`);
  }

  // --------------------------------------------------------------------------
  // 4. TOP 20 REJECTED BY SPEND
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n💸 TOP 20 ODBAČENIH KAMPANJA (po spend-u)\n');

  const top20Rejected = [...rejectedCampaigns]
    .sort((a, b) => b.spend - a.spend)
    .slice(0, 20);

  top20Rejected.forEach((campaign, index) => {
    const mcFlag = campaign.isMcDonalds ? '🍔' : '';
    console.log(`${index + 1}. ${mcFlag} ${campaign.originalName}`);
    console.log(`   Campaign ID: ${campaign.campaignId}`);
    console.log(`   Spend:       ${formatNumber(campaign.spend)} €`);
    console.log(`   Reason:      ${campaign.reason}`);
    console.log();
  });

  // --------------------------------------------------------------------------
  // 5. BREAKDOWN BY REASON
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📊 BREAKDOWN PO RAZLOGU ODBACIVANJA\n');

  const reasonGroups = new Map<string, { count: number, spend: number, campaigns: RejectedCampaign[] }>();

  rejectedCampaigns.forEach(campaign => {
    const reason = campaign.reason;
    if (!reasonGroups.has(reason)) {
      reasonGroups.set(reason, { count: 0, spend: 0, campaigns: [] });
    }
    const group = reasonGroups.get(reason)!;
    group.count++;
    group.spend += campaign.spend;
    group.campaigns.push(campaign);
  });

  const sortedReasons = Array.from(reasonGroups.entries())
    .sort((a, b) => b[1].spend - a[1].spend);

  sortedReasons.forEach(([reason, data]) => {
    console.log(`${reason}`);
    console.log(`   Count: ${data.count} kampanja`);
    console.log(`   Spend: ${formatNumber(data.spend)} €`);
    console.log(`   Top 3 primjera:`);
    data.campaigns
      .sort((a, b) => b.spend - a.spend)
      .slice(0, 3)
      .forEach(c => {
        console.log(`   - ${c.originalName.substring(0, 70)}...`);
        console.log(`     ${formatNumber(c.spend)} €`);
      });
    console.log();
  });

  // --------------------------------------------------------------------------
  // 6. EXPORT REJECTED LIST
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📤 EXPORT: Spremam listu odbačenih kampanja\n');

  const outputPath = path.join(dataDir, 'rejected_campaigns_analysis.json');
  fs.writeFileSync(
    outputPath,
    JSON.stringify(
      {
        summary: {
          totalRejected: rejectedCampaigns.length,
          totalRejectedSpend,
          csvTotalSpend,
          jsonTotalSpend,
          difference: csvTotalSpend - jsonTotalSpend
        },
        mcdonalds: {
          count: mcRejected.length,
          spend: mcRejectedSpend,
          campaigns: mcRejected
        },
        top20: top20Rejected,
        byReason: Array.from(reasonGroups.entries()).map(([reason, data]) => ({
          reason,
          count: data.count,
          spend: data.spend,
          campaigns: data.campaigns
        })),
        allRejected: rejectedCampaigns
      },
      null,
      2
    ),
    'utf-8'
  );

  console.log(`✅ Rejected campaigns analysis spremljena u:`);
  console.log(`   ${outputPath}\n`);

  // --------------------------------------------------------------------------
  // SUMMARY
  // --------------------------------------------------------------------------
  console.log('═'.repeat(80));
  console.log('\n📋 FINALNI SUMMARY\n');
  console.log(`CSV Absolute Total:      ${formatNumber(csvTotalSpend)} €`);
  console.log(`JSON Master Total:       ${formatNumber(jsonTotalSpend)} €`);
  console.log(`REJECTED Total:          ${formatNumber(totalRejectedSpend)} €\n`);
  console.log(`Total kampanja u CSV-u:  ${metricsAggregated.size}`);
  console.log(`Total kampanja u JSON-u: ${jsonData.length}`);
  console.log(`REJECTED kampanja:       ${rejectedCampaigns.length}\n`);
  console.log(`McDonald's rejected:     ${mcRejected.length} kampanja (${formatNumber(mcRejectedSpend)} €)\n`);
  console.log('═'.repeat(80));
  console.log();
}

// ============================================================================
// MAIN
// ============================================================================

reconcileRejectedCampaigns();
