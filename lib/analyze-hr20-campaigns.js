const fs = require('fs');
const Papa = require('papaparse');

const csv = fs.readFileSync('data - v2/campaigns_missing_location.csv', 'utf-8');
const parsed = Papa.parse(csv, { header: true, skipEmptyLines: true, delimiter: ';' });

// Identificirane 20 HR kampanje
const hr20Names = [
  'Bison Bolton - October 2025 (YT) - Bumper',
  'Borotalco Pure June 2025 (CPV)',
  'Rio Mare Filodolio May - Jun 2025 (YT) - CPV',
  'UHU Super Glue Control April 2025 (YT) - Bumper - CPM',
  'Bison AirMax November 2025 (YT) - CPM',
  'Rio Mare Great Taste December 2025 (YT) - CPM',
  'LOC_HRV_HR_BAR_BLUE_NA_Always-on_AO_NA_2025-01-01_2025-12-31-Trueview',
  'Rio Mare For Oceans Jun 2025 (YT) - CPV',
  'Bison Poly Max May - Jun 2025 (YT) - Bumper - CPM',
  'Borotalco Men Aug - Sep 2025 (CPV) - VVC',
  'Rio Mare Sicily August 2025 (YT) - CPM',
  'Rio Mare Insalatissime Apr - May 2025 (YT) - CPM',
  'LOC_HRV_HR_BAR_PESS_NA_Pesto-March_PR_NA_2025-03-10_2025-03-30_NA',
  'Borotalco Pure June 2025 (Bumper)',
  'LOC_HRV_HR_BAR_BLUE_NA_Togetherness_PR_NA_2025-03-17_2025-04-13_NA',
  'Rio Mare Pate Mayo October 2025 (YT) - CPM - 2',
  'UHU BTS Aug - Sep 2025 (YT) - Bumper - CPM',
  'Borotalco Men Aug - Sep 2025 (CPM) - Bumper',
  'Rio Mare For Oceans Jun 2025 (YT) - Bumper',
  'Rio Mare Pate Mayo October 2025 (YT) - CPM'
];

const hr20Set = new Set(hr20Names);

// Filter kampanje s spend > 0 i iz 2025
const campaigns2025 = parsed.data.filter(row => {
  const spend = parseFloat(row.Spend || 0);
  const name = row['Campaign Name'] || '';
  return spend > 0 && name.includes('2025');
});

// Pronađi 20 HR kampanja
const hr20Campaigns = campaigns2025.filter(row => hr20Set.has(row['Campaign Name']));

const totalHr20Spend = hr20Campaigns.reduce((sum, row) => sum + parseFloat(row.Spend || 0), 0);

// Kampanje koje nisu 2025 (2024/2026)
const campaignsNot2025 = parsed.data.filter(row => {
  const name = row['Campaign Name'] || '';
  return !name.includes('2025');
});

// Kampanje s 0 spend
const campaignsZeroSpend = parsed.data.filter(row => {
  const spend = parseFloat(row.Spend || 0);
  return spend === 0;
});

console.log('═'.repeat(60));
console.log('🔍 ANALIZA MISSING LOCATION KAMPANJA\n');
console.log('📊 BREAKDOWN:\n');
console.log('Total kampanja u CSV-u:        ', parsed.data.length);
console.log('Kampanja iz 2025 (spend > 0):  ', campaigns2025.length);
console.log('Kampanja NOT 2025 (2024/2026): ', campaignsNot2025.length);
console.log('Kampanja s 0€ spend:           ', campaignsZeroSpend.length);
console.log('');
console.log('✅ 20 IDENTIFICIRANIH HR KAMPANJA:\n');
console.log('Pronađeno:', hr20Campaigns.length);
console.log('Total Spend:', totalHr20Spend.toLocaleString('hr-HR', {minimumFractionDigits: 2}), '€');
console.log('');
console.log('📋 LISTA:\n');
hr20Campaigns.forEach((row, idx) => {
  console.log(`${idx+1}. ${row['Campaign Name']}`);
  console.log(`   ID: ${row['Campaign ID']}`);
  console.log(`   Spend: ${parseFloat(row.Spend).toLocaleString('hr-HR', {minimumFractionDigits: 2})} €`);
  console.log('');
});
console.log('═'.repeat(60));

// Export samo 20 HR kampanja
const hr20CSV = Papa.unparse(hr20Campaigns, { delimiter: ';', header: true });
fs.writeFileSync('data - v2/hr_20_campaigns_to_add.csv', hr20CSV, 'utf-8');
console.log('\n✅ 20 HR kampanja izvezeno u: data - v2/hr_20_campaigns_to_add.csv\n');
