const fs = require('fs');
const Papa = require('papaparse');

function readCSV(path, delim) {
  let content = fs.readFileSync(path, 'utf-8');
  if (content.charCodeAt(0) === 0xFEFF) content = content.substring(1);
  return Papa.parse(content, { header: true, skipEmptyLines: true, delimiter: delim }).data;
}

// Load data
const metrics = readCSV('data - v2/campaign metrics - v2/campaign metrics - v2.csv', ';');
const location = readCSV('data - v2/campaign - location - v2/campaign - location - v2 - new.csv', ';');

// Get unique IDs
const locationIds = new Set(location.map(r => r['Campaign ID']).filter(id => id));

// Aggregate metrics by Campaign ID
const metricsAgg = new Map();
metrics.forEach(row => {
  const id = row['Campaign ID'];
  if (!id) return;

  const spend = parseFloat(row.Cost?.replace(/,/g, '') || 0);
  const impr = parseFloat(row['Impr.']?.replace(/,/g, '') || 0);
  const clicks = parseFloat(row.Clicks?.replace(/,/g, '') || 0);
  const format = row['Ad format'] || '';

  if (!metricsAgg.has(id)) {
    metricsAgg.set(id, {
      'Campaign ID': id,
      'Campaign Name': row.Campaign,
      'Spend': spend,
      'Impressions': impr,
      'Clicks': clicks,
      'Ad Formats': format
    });
  } else {
    const existing = metricsAgg.get(id);
    existing.Spend += spend;
    existing.Impressions += impr;
    existing.Clicks += clicks;
    if (!existing['Ad Formats'].includes(format)) {
      existing['Ad Formats'] += ' + ' + format;
    }
  }
});

// Filter campaigns without location data
const missingLocation = [];
metricsAgg.forEach((data, id) => {
  if (!locationIds.has(id)) {
    missingLocation.push(data);
  }
});

// Sort by spend descending
missingLocation.sort((a, b) => b.Spend - a.Spend);

// Convert to CSV
const csv = Papa.unparse(missingLocation, {
  delimiter: ';',
  header: true
});

// Save
fs.writeFileSync('data - v2/campaigns_missing_location.csv', csv, 'utf-8');

console.log('✅ CSV file kreiran!');
console.log('   File: data - v2/campaigns_missing_location.csv');
console.log('   Kampanja:', missingLocation.length);
console.log('   Total Spend:', missingLocation.reduce((sum, c) => sum + c.Spend, 0).toLocaleString('hr-HR', {minimumFractionDigits: 2}), '€');
