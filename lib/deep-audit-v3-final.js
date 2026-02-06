"use strict";
/**
 * DEEP AUDIT V3 - FINAL
 *
 * Uključuje 20 HR kampanja koje nemaju location podatke
 * ali su pokrenute u Hrvatskoj u 2025.
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
// 20 HR KAMPANJA BEZ LOCATION PODATAKA (identificirano ručno)
// ============================================================================
const HR_20_CAMPAIGN_IDS = [
    '23077707730', // Bison Bolton
    '22714966255', // Borotalco Pure June
    '22524793110', // Rio Mare Filodolio
    '22424964895', // UHU Super Glue Control
    '23219213253', // Bison AirMax
    '23345854229', // Rio Mare Great Taste
    '22183805418', // Barilla Always-on
    '22629192638', // Rio Mare For Oceans
    '22579539314', // Bison Poly Max
    '22919079036', // Borotalco Men VVC
    '22857496712', // Rio Mare Sicily
    '22422142785', // Rio Mare Insalatissime
    '22306320697', // Barilla Pesto
    '22711295453', // Borotalco Pure Bumper
    '22309984514', // Barilla Togetherness
    '23151406242', // Rio Mare Pate Mayo 2
    '22914435242', // UHU BTS
    '22928971609', // Borotalco Men Bumper
    '22623027750', // Rio Mare For Oceans Bumper
    '23125923104' // Rio Mare Pate Mayo
];
const WORLDWIDE_MCDONALD_IDS = [
    '22739124367', // McDonald's Stripsi CPV
    '22739104237', // McDonald's Stripsi Bumper
    '22738910359' // McDonald's IceCoffe CPV
];
// ============================================================================
// DEEP AUDIT V3
// ============================================================================
function deepAuditV3() {
    console.log('🔍 DEEP AUDIT V3 - FINAL (s 20 HR kampanja)\n');
    console.log('═'.repeat(80) + '\n');
    const baseDir = path_1.default.join(process.cwd(), 'data - v2');
    // --------------------------------------------------------------------------
    // 1. LOAD METRICS
    // --------------------------------------------------------------------------
    console.log('📂 Učitavam podatke...\n');
    const metricsPath = path_1.default.join(baseDir, 'campaign metrics - v2', 'campaign metrics - v2.csv');
    const metricsData = readCSV(metricsPath, ';');
    const metricsAgg = new Map();
    metricsData.forEach(row => {
        const id = row['Campaign ID'];
        const name = row.Campaign;
        const spend = parseNumber(row.Cost);
        if (!metricsAgg.has(id)) {
            metricsAgg.set(id, { name, spend });
        }
        else {
            metricsAgg.get(id).spend += spend;
        }
    });
    const rawTotalSpend = Array.from(metricsAgg.values()).reduce((sum, c) => sum + c.spend, 0);
    console.log(`✅ Metrics: ${metricsAgg.size} kampanja`);
    console.log(`   Raw Total Spend: ${formatNumber(rawTotalSpend)} €\n`);
    // --------------------------------------------------------------------------
    // 2. LOAD LOCATION
    // --------------------------------------------------------------------------
    const locationPath = path_1.default.join(baseDir, 'campaign - location - v2', 'campaign - location - v2 - new.csv');
    const locationData = readCSV(locationPath, ';');
    const campaignLocations = new Map();
    locationData.forEach(row => {
        const id = row['Campaign ID'];
        const name = row.Campaign;
        const country = row['Country/Territory (User location)'];
        const spend = parseNumber(row.Cost);
        if (!campaignLocations.has(id)) {
            campaignLocations.set(id, { name, hrSpend: 0, nonHrSpend: 0, isHR: false });
        }
        const location = campaignLocations.get(id);
        if (country && (country.toLowerCase().includes('croatia') || country.toLowerCase().includes('hrvatska'))) {
            location.hrSpend += spend;
        }
        else {
            location.nonHrSpend += spend;
        }
    });
    // Classify HR vs Non-HR
    campaignLocations.forEach((data, id) => {
        data.isHR = data.hrSpend > 0 && data.nonHrSpend === 0;
    });
    console.log(`✅ Location: ${campaignLocations.size} kampanja\n`);
    // --------------------------------------------------------------------------
    // 3. CLASSIFY CAMPAIGNS
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n🔍 KLASIFIKACIJA KAMPANJA\n');
    const hr20Set = new Set(HR_20_CAMPAIGN_IDS);
    const mcdBugSet = new Set(WORLDWIDE_MCDONALD_IDS);
    let hrWithLocation = 0;
    let hrWithLocationSpend = 0;
    let nonHr = 0;
    let nonHrSpend = 0;
    let hr20 = 0;
    let hr20Spend = 0;
    let mcdBug = 0;
    let mcdBugSpend = 0;
    metricsAgg.forEach((data, id) => {
        // McDonald's Bug
        if (mcdBugSet.has(id)) {
            mcdBug++;
            mcdBugSpend += data.spend;
            return;
        }
        // 20 HR kampanja bez location
        if (hr20Set.has(id)) {
            hr20++;
            hr20Spend += data.spend;
            return;
        }
        // Kampanje s location podacima
        if (campaignLocations.has(id)) {
            const location = campaignLocations.get(id);
            if (location.isHR) {
                hrWithLocation++;
                hrWithLocationSpend += data.spend;
            }
            else {
                nonHr++;
                nonHrSpend += data.spend;
            }
        }
        // Kampanje bez location podataka (ignored - 2024/2026)
    });
    console.log(`✅ HR kampanje (s location):         ${hrWithLocation} (${formatNumber(hrWithLocationSpend)} €)`);
    console.log(`✅ HR kampanje (20 bez location):    ${hr20} (${formatNumber(hr20Spend)} €)`);
    console.log(`❌ Non-HR kampanje:                  ${nonHr} (${formatNumber(nonHrSpend)} €)`);
    console.log(`❌ McDonald's Worldwide Bug:         ${mcdBug} (${formatNumber(mcdBugSpend)} €)`);
    console.log();
    const finalHrCampaigns = hrWithLocation + hr20;
    const finalHrSpend = hrWithLocationSpend + hr20Spend;
    // --------------------------------------------------------------------------
    // 4. WATERFALL
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n📈 WATERFALL ANALIZA\n');
    console.log(`1️⃣  RAW TOTAL SPEND:                   ${formatNumber(rawTotalSpend)} €`);
    console.log(`    └─ Kampanja: ${metricsAgg.size}\n`);
    console.log(`2️⃣  EXCLUDED: Non-HR Markets:          -${formatNumber(nonHrSpend)} €`);
    console.log(`    └─ Kampanja: ${nonHr}\n`);
    console.log(`3️⃣  EXCLUDED: Worldwide McD Bug:       -${formatNumber(mcdBugSpend)} €`);
    console.log(`    └─ Kampanja: ${mcdBug}\n`);
    console.log(`4️⃣  INCLUDED: 20 HR (no location):     +${formatNumber(hr20Spend)} €`);
    console.log(`    └─ Kampanja: ${hr20}\n`);
    console.log(`─`.repeat(80));
    console.log(`✅  FINALNI HR SPEND:                   ${formatNumber(finalHrSpend)} €`);
    console.log(`    └─ Kampanja: ${finalHrCampaigns}\n`);
    // Validation
    const calculated = rawTotalSpend - nonHrSpend - mcdBugSpend;
    const diff = Math.abs(calculated - finalHrSpend);
    console.log(`📊 VALIDATION:`);
    console.log(`   Raw - Non-HR - McD Bug = ${formatNumber(calculated)} €`);
    console.log(`   Final HR Spend         = ${formatNumber(finalHrSpend)} €`);
    console.log(`   Razlika                = ${formatNumber(diff)} €`);
    console.log(`   Status: ${diff < 1 ? '✅ PASS' : '⚠️  Note: includes 20 HR without location'}\n`);
    // --------------------------------------------------------------------------
    // 5. EXPORT
    // --------------------------------------------------------------------------
    console.log('═'.repeat(80));
    console.log('\n📤 EXPORT\n');
    const results = {
        timestamp: new Date().toISOString(),
        raw: {
            campaigns: metricsAgg.size,
            spend: rawTotalSpend
        },
        excluded: {
            nonHr: { campaigns: nonHr, spend: nonHrSpend },
            mcdBug: { campaigns: mcdBug, spend: mcdBugSpend }
        },
        included: {
            hrWithLocation: { campaigns: hrWithLocation, spend: hrWithLocationSpend },
            hr20NoLocation: { campaigns: hr20, spend: hr20Spend }
        },
        final: {
            campaigns: finalHrCampaigns,
            spend: finalHrSpend
        }
    };
    const outputPath = path_1.default.join(baseDir, 'deep_audit_v3_final.json');
    fs_1.default.writeFileSync(outputPath, JSON.stringify(results, null, 2), 'utf-8');
    console.log(`✅ Rezultati: ${outputPath}\n`);
    console.log('═'.repeat(80));
    console.log();
}
// ============================================================================
// MAIN
// ============================================================================
deepAuditV3();
