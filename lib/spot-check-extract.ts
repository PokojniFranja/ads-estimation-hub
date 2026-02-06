/**
 * SPOT-CHECK DATA EXTRACTION
 *
 * Izvlači ključne podatke za ručnu validaciju u Google Ads sučelju
 */

import fs from 'fs';
import path from 'path';

// ============================================================================
// TIPOVI
// ============================================================================

interface DemographicBreakdown {
  age: string;
  gender: string;
  percentage: number;
}

interface InterestSegment {
  segment: string;
  cost: number;
  percentage: number;
}

interface CampaignMaster {
  campaignId: string;
  originalName: string;
  standardizedName: string;
  startDate: string;
  endDate: string;
  quarter: string[];
  month: string[];
  spend: number;
  impressions: number;
  clicks: number;
  trueViewViews: number | null;
  conversions: number;
  ctr: number | null;
  cpc: number | null;
  cpm: number | null;
  cpv: number | null;
  costPerConversion: number | null;
  conversionRate: number | null;
  reach: number | null;
  frequency: number | null;
  isMultiQuarter: boolean;
  reachDisclaimer?: string;
  demographics: DemographicBreakdown[];
  interests: InterestSegment[];
  interestsCoverage: number;
  adFormat: string;
}

// ============================================================================
// HELPER
// ============================================================================

function formatNumber(num: number): string {
  return num.toLocaleString('hr-HR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatInteger(num: number): string {
  return Math.round(num).toLocaleString('hr-HR');
}

// ============================================================================
// SPOT-CHECK EXTRACTION
// ============================================================================

function extractSpotCheckData() {
  console.log('🔍 SPOT-CHECK DATA EXTRACTION\n');
  console.log('═'.repeat(80) + '\n');

  const dataDir = path.join(process.cwd(), 'data');
  const jsonPath = path.join(dataDir, 'master_database_v2.json');
  const data: CampaignMaster[] = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));

  console.log(`📂 Master Database učitana: ${data.length} kampanja\n`);

  // ==========================================================================
  // 1. TOP 3 KAMPANJE PO SPEND-U
  // ==========================================================================
  console.log('═'.repeat(80));
  console.log('💰 TOP 3 KAMPANJE PO SPEND-U\n');

  const top3BySpend = [...data]
    .sort((a, b) => b.spend - a.spend)
    .slice(0, 3);

  top3BySpend.forEach((campaign, index) => {
    console.log(`${index + 1}. ${campaign.originalName}`);
    console.log(`   Campaign ID:     ${campaign.campaignId}`);
    console.log(`   Spend:           ${formatNumber(campaign.spend)} €`);
    console.log(`   Impressions:     ${formatInteger(campaign.impressions)}`);
    console.log(`   Peak Reach:      ${campaign.reach ? formatInteger(campaign.reach) : 'N/A'}`);
    console.log(`   Ad Format:       ${campaign.adFormat}`);
    console.log(`   Period:          ${campaign.startDate} - ${campaign.endDate}`);
    console.log();
  });

  // ==========================================================================
  // 2. BRAND TOTAL (McDonald's)
  // ==========================================================================
  console.log('═'.repeat(80));
  console.log('🍔 BRAND TOTAL: McDonald\'s\n');

  const mcdonaldsCampaigns = data.filter(c =>
    c.originalName.toLowerCase().includes('mcdonald') ||
    c.standardizedName.toLowerCase().includes('mcdonald')
  );

  const mcdonaldsTotalSpend = mcdonaldsCampaigns.reduce((sum, c) => sum + c.spend, 0);
  const mcdonaldsTotalImpressions = mcdonaldsCampaigns.reduce((sum, c) => sum + c.impressions, 0);
  const mcdonaldsTotalClicks = mcdonaldsCampaigns.reduce((sum, c) => sum + c.clicks, 0);

  console.log(`   Total Campaigns:   ${mcdonaldsCampaigns.length}`);
  console.log(`   Total Spend:       ${formatNumber(mcdonaldsTotalSpend)} €`);
  console.log(`   Total Impressions: ${formatInteger(mcdonaldsTotalImpressions)}`);
  console.log(`   Total Clicks:      ${formatInteger(mcdonaldsTotalClicks)}`);
  console.log();

  console.log('   📋 Lista McDonald\'s kampanja:');
  mcdonaldsCampaigns
    .sort((a, b) => b.spend - a.spend)
    .forEach((campaign, index) => {
      console.log(`   ${index + 1}. ${campaign.originalName}`);
      console.log(`      Spend: ${formatNumber(campaign.spend)} € | ID: ${campaign.campaignId}`);
    });
  console.log();

  // ==========================================================================
  // 3. DEMOGRAFSKI TEST - KAMPANJA S NAJVEĆIM REACH-OM
  // ==========================================================================
  console.log('═'.repeat(80));
  console.log('🎯 DEMOGRAFSKI TEST: Kampanja s najvećim Peak Reach-om\n');

  const campaignWithMaxReach = [...data]
    .filter(c => c.reach !== null)
    .sort((a, b) => (b.reach || 0) - (a.reach || 0))[0];

  if (campaignWithMaxReach) {
    console.log(`   Kampanja: ${campaignWithMaxReach.originalName}`);
    console.log(`   Campaign ID: ${campaignWithMaxReach.campaignId}`);
    console.log(`   Peak Reach: ${formatInteger(campaignWithMaxReach.reach!)}`);
    console.log(`   Period: ${campaignWithMaxReach.startDate} - ${campaignWithMaxReach.endDate}`);
    console.log();
    console.log('   📊 Top 3 dobne skupine:');

    // Grupiraj po dobi (zbroj svih gendera)
    const ageGroups = new Map<string, number>();
    campaignWithMaxReach.demographics.forEach(demo => {
      const age = demo.age;
      const current = ageGroups.get(age) || 0;
      ageGroups.set(age, current + demo.percentage);
    });

    const top3Ages = Array.from(ageGroups.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    top3Ages.forEach(([age, percentage], index) => {
      console.log(`   ${index + 1}. ${age.padEnd(15)} → ${percentage.toFixed(2)}%`);
    });
    console.log();

    console.log('   📋 Detaljni demografski breakdown (svi segmenti):');
    campaignWithMaxReach.demographics
      .slice(0, 10)
      .forEach((demo, index) => {
        console.log(`   ${index + 1}. ${demo.age} / ${demo.gender.padEnd(10)} → ${demo.percentage.toFixed(2)}%`);
      });
    console.log();
  } else {
    console.log('   ⚠️  Nema kampanja s reach podacima!\n');
  }

  // ==========================================================================
  // 4. QUARTERLY SPEND - Q3 2025
  // ==========================================================================
  console.log('═'.repeat(80));
  console.log('📅 QUARTERLY SPEND: Q3 2025\n');

  const q3Campaigns = data.filter(c => c.quarter.includes('Q3'));
  const q3TotalSpend = q3Campaigns.reduce((sum, c) => sum + c.spend, 0);
  const q3TotalImpressions = q3Campaigns.reduce((sum, c) => sum + c.impressions, 0);
  const q3TotalClicks = q3Campaigns.reduce((sum, c) => sum + c.clicks, 0);

  console.log(`   Total Campaigns:   ${q3Campaigns.length}`);
  console.log(`   Total Spend:       ${formatNumber(q3TotalSpend)} €`);
  console.log(`   Total Impressions: ${formatInteger(q3TotalImpressions)}`);
  console.log(`   Total Clicks:      ${formatInteger(q3TotalClicks)}`);
  console.log();

  console.log('   📋 Top 10 Q3 kampanja po spend-u:');
  q3Campaigns
    .sort((a, b) => b.spend - a.spend)
    .slice(0, 10)
    .forEach((campaign, index) => {
      console.log(`   ${index + 1}. ${campaign.originalName}`);
      console.log(`      Spend: ${formatNumber(campaign.spend)} € | Reach: ${campaign.reach ? formatInteger(campaign.reach) : 'N/A'}`);
    });
  console.log();

  // ==========================================================================
  // SUMMARY FOR VALIDATION
  // ==========================================================================
  console.log('═'.repeat(80));
  console.log('\n📋 VALIDATION CHECKLIST\n');
  console.log('□ Top 3 kampanje po spend-u → Provjeri u Google Ads filtriranjem po Cost');
  console.log('□ McDonald\'s total spend → Provjeri u Ads filtriranjem brenda "McDonald\'s"');
  console.log('□ Demografski breakdown → Provjeri u Insights tabu za kampanju s max reach-om');
  console.log('□ Q3 2025 spend → Provjeri u Ads s date range 01.07.2025 - 30.09.2025');
  console.log();
  console.log('═'.repeat(80));
  console.log('\n✅ Spot-check podaci ekstrahirani! Spremno za validaciju u Google Ads.\n');
}

// ============================================================================
// MAIN
// ============================================================================

extractSpotCheckData();
