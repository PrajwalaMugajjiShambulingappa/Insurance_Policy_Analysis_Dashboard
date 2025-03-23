import sqlite3
import pandas as pd

# Load data
data = pd.read_csv('./insurance_data.csv')
insurance_df = pd.DataFrame(data)

# Create connection
conn = sqlite3.connect('insurance_analytics.db')

# Save DataFrame to SQL table
insurance_df.to_sql('policies', conn, if_exists='replace', index=False)

# Create a few analytical views
cursor = conn.cursor()

# View 1: Loss ratio by policy type
cursor.execute('''
CREATE VIEW IF NOT EXISTS loss_ratio_by_type AS
SELECT
    policy_type,
    COUNT(*) as total_policies,
    SUM(premium_amount) as total_premiums,
    SUM(claim_amount) as total_claims,
    CASE
        WHEN SUM(premium_amount) > 0
        THEN ROUND(SUM(claim_amount) / SUM(premium_amount) * 100, 2)
        ELSE 0
    END as loss_ratio
FROM policies
GROUP BY policy_type
ORDER BY loss_ratio DESC;
''')

# View 2: Regional performance
cursor.execute('''
CREATE VIEW IF NOT EXISTS regional_performance AS
SELECT
    state,
    COUNT(*) as total_policies,
    SUM(premium_amount) as total_premiums,
    SUM(claim_amount) as total_claims,
    ROUND(AVG(premium_amount), 2) as avg_premium,
    CASE
        WHEN SUM(premium_amount) > 0
        THEN ROUND(SUM(claim_amount) / SUM(premium_amount) * 100, 2)
        ELSE 0
    END as loss_ratio
FROM policies
GROUP BY state
ORDER BY total_premiums DESC;
''')

# View 3: Monthly policy acquisition trend
cursor.execute('''
CREATE VIEW IF NOT EXISTS monthly_acquisition AS
SELECT
    strftime('%Y-%m', issue_date) as month,
    COUNT(*) as new_policies,
    SUM(premium_amount) as new_premiums,
    policy_type
FROM policies
GROUP BY month, policy_type
ORDER BY month;
''')

# Execute queries on the views and print results
print("\n=== Loss Ratio by Policy Type ===")
loss_ratio_df = pd.read_sql_query("SELECT * FROM loss_ratio_by_type", conn)
print(loss_ratio_df)

print("\n=== Regional Performance ===")
regional_df = pd.read_sql_query("SELECT * FROM regional_performance", conn)
print(regional_df)

print("\n=== Monthly Acquisition Trends ===")
monthly_df = pd.read_sql_query("SELECT * FROM monthly_acquisition", conn)
print(monthly_df)

conn.commit()
conn.close()