"use strict";
/**
 * MISSING LOCATION REPORT
 *
 * Identificira kampanje koje postoje u metrics CSV-u
 * ali NEMAJU location podataka.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const papaparse_1 = __importDefault(require("papaparse"));
// ============================================================================
// HELPER
// ============================================================================
function parseNumber(value) {
    if (!value)
        return 0;
    let cleaned = value.replace(/[^\d.,-]/g, '');
    cleaned = cleaned.replace(/,/g, '');
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
}
function readCSV(filePath, delimiter = ',') {
    let content = fs_1.default.readFileSync(filePath, 'utf-8');
    if (content.charCodeAt(0) === 0xFEFF) {
        content = content.substring(1);
    }
    const parsed = papaparse_1.default.parse(content, {
        header: true,
        skipEmptyLines: true,
        delimiter
    });
    return parsed.data;
}
function formatNumber(num) {
    return num.toLocaleString('hr-HR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
// ============================================================================
// MISSING LOCATION REPORT
// ============================================================================
function generateMissingLocationReport() {
    console.log('🔍 MISSING LOCATION REPORT\n');
    console.log('═'.repeat(80) + '\n');
    const baseDir = path_1.default.join(process.cwd(), 'data - v2');
    // --------------------------------------------------------------------------
    // 1. LOAD METRICS
    // --------------------------------------------------------------------------
    console.log('📂 Učitavam podatke...\n');
    const metricsPath = path_1.default.join(baseDir, 'campaign metrics - v2', 'campaign metrics - v2.csv');
    const metricsData = readCSV(metricsPath, ';');
    // Aggregate metrics by Campaign ID
    const metricsAggregated = new Map();
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
        }
        else {
            const existing = metricsAggregated.get(id);
            existing.spend += spend;
            existing.impressions += impressions;
            existing.clicks += clicks;
            existing.formats.add(format);
        }
    });
    console.log(`✅ Metrics: ${metricsAggregated.size} unique kampanja\n`);
    // --------------------------------------------------------------------------
    // 2. LOAD LOCATION
    // --------------------------------------------------------------------------
    const locationPath = path_1.default.join(baseDir, 'campaign - location - v2', 'campaign - location - v2 - new.csv');
    const locationData = readCSV(locationPath, ';');
    const locationIds = new Set();
    locationData.forEach(row => {
        locationIds.add(row['Campaign ID']);
    });
    console.log(`✅ Location: ${locationIds.size} unique kampanja\n`);
    // --------------------------------------------------------------------------
    // 3. FIND MISSING
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n🔍 KAMPANJE BEZ LOCATION PODATAKA\n');
    const missingLocation = Array.from(metricsAggregated.entries())
        .filter(([id, _]) => !locationIds.has(id))
        .map(([id, data]) => ({
        campaignId: id,
        name: data.name,
        spend: data.spend,
        impressions: data.impressions,
        clicks: data.clicks,
        formats: Array.from(data.formats)
    }))
        .sort((a, b) => b.spend - a.spend);
    const totalMissingSpend = missingLocation.reduce((sum, c) => sum + c.spend, 0);
    console.log(`⚠️  TOTAL MISSING: ${missingLocation.length} kampanja`);
    console.log(`💸 TOTAL SPEND:   ${formatNumber(totalMissingSpend)} €\n`);
    // --------------------------------------------------------------------------
    // 4. TOP 50 BY SPEND
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n💸 TOP 50 KAMPANJA BEZ LOCATION PODATAKA (po spend-u)\n');
    missingLocation.slice(0, 50).forEach((campaign, index) => {
        console.log(`${index + 1}. ${campaign.name}`);
        console.log(`   ID: ${campaign.campaignId}`);
        console.log(`   Spend: ${formatNumber(campaign.spend)} €`);
        console.log(`   Impressions: ${formatNumber(campaign.impressions)}`);
        console.log(`   Clicks: ${formatNumber(campaign.clicks)}`);
        console.log(`   Formats: ${campaign.formats.join(', ')}`);
        console.log();
    });
    // --------------------------------------------------------------------------
    // 5. BRAND ANALYSIS
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n📊 ANALIZA PO BRENDOVIMA (Top 10)\n');
    // Extract brand from campaign name (usually first word or before first separator)
    const brandSpend = new Map();
    missingLocation.forEach(campaign => {
        // Try to extract brand - look for common patterns
        let brand = 'Unknown';
        const name = campaign.name;
        // Pattern 1: McDonald's
        if (name.toLowerCase().includes("mcdonald")) {
            brand = "McDonald's";
        }
        // Pattern 2: T03_xxxxx_HR_BRAND
        else if (name.startsWith('T03_')) {
            const parts = name.split('_');
            if (parts.length > 3) {
                brand = parts[3];
            }
        }
        // Pattern 3: Brand at start before space or separator
        else {
            const parts = name.split(/[\s_\-\/]/);
            if (parts[0]) {
                brand = parts[0];
            }
        }
        if (!brandSpend.has(brand)) {
            brandSpend.set(brand, { count: 0, spend: 0 });
        }
        const existing = brandSpend.get(brand);
        existing.count++;
        existing.spend += campaign.spend;
    });
    const sortedBrands = Array.from(brandSpend.entries())
        .sort((a, b) => b[1].spend - a[1].spend)
        .slice(0, 10);
    sortedBrands.forEach(([brand, data], index) => {
        console.log(`${index + 1}. ${brand}`);
        console.log(`   Kampanja: ${data.count}`);
        console.log(`   Spend: ${formatNumber(data.spend)} €`);
        console.log();
    });
    // --------------------------------------------------------------------------
    // 6. SPEND DISTRIBUTION
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n📊 RASPODJELA TROŠKA\n');
    const over10k = missingLocation.filter(c => c.spend >= 10000);
    const between5k10k = missingLocation.filter(c => c.spend >= 5000 && c.spend < 10000);
    const between1k5k = missingLocation.filter(c => c.spend >= 1000 && c.spend < 5000);
    const under1k = missingLocation.filter(c => c.spend < 1000);
    console.log(`Spend > 10,000 €:       ${over10k.length} kampanja (${formatNumber(over10k.reduce((s, c) => s + c.spend, 0))} €)`);
    console.log(`Spend 5,000-10,000 €:   ${between5k10k.length} kampanja (${formatNumber(between5k10k.reduce((s, c) => s + c.spend, 0))} €)`);
    console.log(`Spend 1,000-5,000 €:    ${between1k5k.length} kampanja (${formatNumber(between1k5k.reduce((s, c) => s + c.spend, 0))} €)`);
    console.log(`Spend < 1,000 €:        ${under1k.length} kampanja (${formatNumber(under1k.reduce((s, c) => s + c.spend, 0))} €)`);
    console.log();
    // --------------------------------------------------------------------------
    // 7. EXPORT
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n📤 EXPORT: Spremam izvještaj...\n');
    const report = {
        summary: {
            totalMissing: missingLocation.length,
            totalSpend: totalMissingSpend,
            timestamp: new Date().toISOString()
        },
        campaigns: missingLocation,
        byBrand: Array.from(brandSpend.entries()).map(([brand, data]) => ({
            brand,
            count: data.count,
            spend: data.spend
        })).sort((a, b) => b.spend - a.spend),
        distribution: {
            over10k: { count: over10k.length, spend: over10k.reduce((s, c) => s + c.spend, 0) },
            between5k10k: { count: between5k10k.length, spend: between5k10k.reduce((s, c) => s + c.spend, 0) },
            between1k5k: { count: between1k5k.length, spend: between1k5k.reduce((s, c) => s + c.spend, 0) },
            under1k: { count: under1k.length, spend: under1k.reduce((s, c) => s + c.spend, 0) }
        }
    };
    const outputPath = path_1.default.join(process.cwd(), 'data', 'missing_location_report.json');
    fs_1.default.writeFileSync(outputPath, JSON.stringify(report, null, 2), 'utf-8');
    console.log(`✅ Izvještaj spremljen u: ${outputPath}\n`);
    console.log('═'.repeat(80));
    console.log();
}
// ============================================================================
// MAIN
// ============================================================================
generateMissingLocationReport();
