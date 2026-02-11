import pandas as pd

# Check V3 original
df_v3 = pd.read_csv('data - v3/campaign - metrics - v3/campaign metrics - version 3 - no segmentation - all campaigns.csv',
                     delimiter=';', encoding='utf-8')
accounts_v3 = sorted(df_v3['Account'].dropna().unique().tolist())

# Check MASTER
df_master = pd.read_csv('MASTER_ADS_HR_CLEANED.csv', delimiter=';', encoding='utf-8')
accounts_master = sorted(df_master['Account'].dropna().unique().tolist())

print("=" * 70)
print("V3 ORIGINAL (835 campaigns) - ALL ACCOUNTS")
print("=" * 70)
print(f"Total unique accounts: {len(accounts_v3)}\n")
for i, acc in enumerate(accounts_v3, 1):
    print(f"{i:2d}. {acc}")

print("\n" + "=" * 70)
print("MASTER HR CLEANED (697 campaigns) - ACCOUNTS")
print("=" * 70)
print(f"Total unique accounts: {len(accounts_master)}\n")

# Show which accounts were removed
removed = set(accounts_v3) - set(accounts_master)
if removed:
    print(f"\nACCOUNTS REMOVED (filtering to HR only): {len(removed)}")
    for acc in sorted(removed):
        print(f"  - {acc}")
