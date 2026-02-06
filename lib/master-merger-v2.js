"use strict";
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const papaparse_1 = __importDefault(require("papaparse"));
// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
function parseNumber(value) {
    if (!value)
        return 0;
    // Ukloni sve osim brojeva, točaka, zareza i minusa
    let cleaned = value.replace(/[^\d.,-]/g, '');
    // AMERIČKI FORMAT (Google Ads CSV export):
    // Zarez (,) = thousands separator → UKLONI: "1,256,267" → "1256267"
    // Točka (.) = decimal separator → OSTAVI: "2860.6" → "2860.6"
    cleaned = cleaned.replace(/,/g, '');
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
}
function safeDiv(numerator, denominator) {
    if (denominator === 0)
        return null;
    return numerator / denominator;
}
function extractQuarter(dateStr) {
    // Format: DD.MM.YYYY. (npr. "01.09.2025.")
    const match = dateStr.match(/\d{2}\.(\d{2})\./);
    if (!match)
        return 'Q?';
    const month = parseInt(match[1]);
    if (month >= 1 && month <= 3)
        return 'Q1';
    if (month >= 4 && month <= 6)
        return 'Q2';
    if (month >= 7 && month <= 9)
        return 'Q3';
    if (month >= 10 && month <= 12)
        return 'Q4';
    return 'Q?';
}
function extractMonth(dateStr) {
    const match = dateStr.match(/\d{2}\.(\d{2})\./);
    if (!match)
        return '?';
    return match[1];
}
function getQuartersAndMonths(startDate, endDate) {
    const quarters = new Set();
    const months = new Set();
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
function readCSV(filePath) {
    const content = fs_1.default.readFileSync(filePath, 'utf-8');
    const parsed = papaparse_1.default.parse(content, {
        header: true,
        skipEmptyLines: true
    });
    return parsed.data;
}
// ============================================================================
// MAIN MERGER LOGIC
// ============================================================================
function mergeMasterDatabase() {
    const dataDir = path_1.default.join(process.cwd(), 'data');
    const rawDir = path_1.default.join(dataDir, 'raw');
    console.log('📂 Učitavam podatke...\n');
    // 1. REGISTRY (standardized names)
    const registry = readCSV(path_1.default.join(dataDir, 'campaign_registry.csv'));
    const registryMap = new Map(registry.map(r => [r['Campaign ID'], r]));
    console.log(`✅ Registry: ${registry.length} kampanja`);
    // 2. METRICS (source of truth) - AGGREGATE BY CAMPAIGN ID
    const metricsRaw = readCSV(path_1.default.join(rawDir, 'campaign_metrics', '2025_metrics.csv'));
    const metricsMap = new Map();
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
        }
        else {
            const existing = metricsMap.get(id);
            if (!existing.formats.includes(format))
                existing.formats.push(format);
            existing.spend += spend;
            existing.impressions += impressions;
            existing.clicks += clicks;
            existing.views += views;
            existing.conversions += conversions;
        }
    });
    console.log(`✅ Metrics: ${metricsRaw.length} redaka → ${metricsMap.size} kampanja`);
    // 3. AGE GENDER
    const ageGender = readCSV(path_1.default.join(rawDir, 'age_gender_clean.csv'));
    const ageGenderByCampaign = new Map();
    ageGender.forEach(row => {
        const id = row['Campaign ID'];
        if (!ageGenderByCampaign.has(id))
            ageGenderByCampaign.set(id, []);
        ageGenderByCampaign.get(id).push(row);
    });
    console.log(`✅ Demographics: ${ageGender.length} redaka`);
    // 4. INTERESTS
    const interests = readCSV(path_1.default.join(rawDir, 'interests_clean.csv'));
    const interestsByCampaign = new Map();
    interests.forEach(row => {
        const id = row['Campaign ID'];
        if (!interestsByCampaign.has(id))
            interestsByCampaign.set(id, []);
        interestsByCampaign.get(id).push(row);
    });
    console.log(`✅ Interests: ${interests.length} redaka`);
    // 5. REACH (po kvartalima) - Peak Reach
    const reachFiles = ['Q1_2025.csv', 'Q2_2025.csv', 'Q3_2025.csv', 'Q4_2025.csv'];
    const reachByCampaign = new Map();
    reachFiles.forEach(file => {
        const filePath = path_1.default.join(rawDir, 'campaign_reach_frequency', file);
        if (!fs_1.default.existsSync(filePath))
            return;
        const reachData = readCSV(filePath);
        reachData.forEach(row => {
            const id = row['Campaign ID'];
            const reach = parseNumber(row['Unique users']);
            const freq = parseNumber(row['Avg. impr. freq. / user']);
            if (!reachByCampaign.has(id)) {
                reachByCampaign.set(id, { reach, frequency: freq, count: 1 });
            }
            else {
                const existing = reachByCampaign.get(id);
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
    const masterData = [];
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
        const demographics = [];
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
        const interestSegments = interestRows.map(row => {
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
        const master = {
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
    const outputPath = path_1.default.join(process.cwd(), 'data', 'master_database_v2.json');
    fs_1.default.writeFileSync(outputPath, JSON.stringify(masterData, null, 2), 'utf-8');
    console.log('═'.repeat(60));
    console.log(`\n✅ GOTOVO! Master database spremljena u:\n   ${outputPath}\n`);
    console.log(`📊 Total kampanja: ${masterData.length}\n`);
    // Stats
    const totalSpend = masterData.reduce((sum, c) => sum + c.spend, 0);
    const withReach = masterData.filter(c => c.reach !== null).length;
    const multiQuarter = masterData.filter(c => c.isMultiQuarter).length;
    console.log('📈 Statistika:');
    console.log(`   💰 Total Spend: ${totalSpend.toLocaleString('hr-HR')} €`);
    console.log(`   👥 Kampanja s Reach: ${withReach} (${Math.round(withReach / masterData.length * 100)}%)`);
    console.log(`   📅 Multi-quarter kampanje: ${multiQuarter}`);
    console.log(`   ⚠️  Peak Reach disclaimer: ${multiQuarter} kampanja\n`);
}
main();
