import pandas as pd

df = pd.read_csv('MISSING_ROLLING_CAMPAIGNS_DETAILED.csv', encoding='utf-8-sig')

print('MISSING CAMPAIGNS - FORMAT BREAKDOWN')
print('=' * 70)

# Count by format
format_counts = df.groupby('Ad_Format').agg({
    'Campaign ID': 'count',
    'Cost_Parsed': 'sum'
}).reset_index()
format_counts.columns = ['Format', 'Count', 'Total_Cost']
format_counts['Cost_Pct'] = (format_counts['Total_Cost'] / format_counts['Total_Cost'].sum() * 100)
format_counts = format_counts.sort_values('Total_Cost', ascending=False)

print('\nALL FORMATS:')
for idx, row in format_counts.iterrows():
    fmt = str(row['Format'])[:20]
    print(f'{fmt:20s} | Count: {int(row["Count"]):3d} | Cost: EUR {row["Total_Cost"]:>10.2f} ({row["Cost_Pct"]:5.2f}%)')

print()
print('CRITICAL vs NON-CRITICAL')
print('=' * 70)

critical_formats = ['YouTube In-Stream', 'YouTube Bumper', 'YouTube Non-Skip', 'YouTube Shorts', 'Display']
df['Is_Critical'] = df['Ad_Format'].isin(critical_formats)

critical_count = int(df['Is_Critical'].sum())
non_critical_count = int((~df['Is_Critical']).sum())

critical_cost = df[df['Is_Critical']]['Cost_Parsed'].sum()
non_critical_cost = df[~df['Is_Critical']]['Cost_Parsed'].sum()
total_cost = df['Cost_Parsed'].sum()

print(f'\nCRITICAL (YouTube/Display):')
print(f'  Count: {critical_count}/{len(df)} ({critical_count/len(df)*100:.1f}%)')
print(f'  Cost: EUR {critical_cost:,.2f} ({critical_cost/total_cost*100:.2f}%)')

print(f'\nNON-CRITICAL (PMax/Demand Gen/Search):')
print(f'  Count: {non_critical_count}/{len(df)} ({non_critical_count/len(df)*100:.1f}%)')
print(f'  Cost: EUR {non_critical_cost:,.2f} ({non_critical_cost/total_cost*100:.2f}%)')

# Show critical campaigns if any
if critical_count > 0:
    print()
    print('CRITICAL CAMPAIGNS LIST:')
    print('-' * 70)
    df_critical = df[df['Is_Critical']].sort_values('Cost_Parsed', ascending=False)
    for idx, row in df_critical.iterrows():
        print(f'{str(row["Campaign"])[:60]}')
        print(f'  Brand: {row["Brand"]:15s} | Format: {row["Ad_Format"]:20s} | Cost: EUR {row["Cost_Parsed"]:>8.2f}')
