import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.gridspec import GridSpec

# Set style
plt.style.use('ggplot')
sns.set_palette("Set2")

# Connect to database
conn = sqlite3.connect('insurance_analytics.db')

# Query the views
loss_ratio_df = pd.read_sql_query("SELECT * FROM loss_ratio_by_type", conn)
regional_df = pd.read_sql_query("SELECT * FROM regional_performance", conn)
monthly_df = pd.read_sql_query("SELECT * FROM monthly_acquisition", conn)

# Create a pivot table for monthly acquisition
monthly_pivot = monthly_df.pivot_table(
    index='month',
    columns='policy_type',
    values='new_policies',
    fill_value=0
)

# Create the dashboard
fig = plt.figure(figsize=(20, 12))
gs = GridSpec(2, 2, figure=fig)

# 1. Loss Ratio by Policy Type
ax1 = fig.add_subplot(gs[0, 0])
bars = sns.barplot(x='policy_type', y='loss_ratio', data=loss_ratio_df, ax=ax1)
ax1.set_title('Loss Ratio by Policy Type', fontsize=16)
ax1.set_ylabel('Loss Ratio (%)')
ax1.set_xlabel('Policy Type')
for bar in bars.patches:
    bars.annotate(f"{bar.get_height():.1f}%",
                 (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                 ha='center', va='bottom')

# 2. State Performance
ax2 = fig.add_subplot(gs[0, 1])
regional_df_sorted = regional_df.sort_values('total_premiums', ascending=False).head(10)
bars = sns.barplot(x='state', y='total_premiums', data=regional_df_sorted, ax=ax2)
ax2.set_title('Premium Volume by State (Top 10)', fontsize=16)
ax2.set_ylabel('Total Premiums ($)')
ax2.set_xlabel('State')
ax2.tick_params(axis='y', labelsize=8)
for bar in bars.patches:
    bars.annotate(f"${bar.get_height():,.0f}",
                 (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                 ha='center', va='bottom', rotation=45, fontsize=9)

# 3. Monthly Policy Acquisition Trend
ax3 = fig.add_subplot(gs[1, :])
monthly_pivot.plot(kind='line', marker='o', ax=ax3)
ax3.set_title('Monthly Policy Acquisition Trend by Policy Type', fontsize=16)
ax3.set_ylabel('Number of New Policies')
ax3.set_xlabel('Month')
ax3.legend(title='Policy Type')
ax3.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('insurance_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

# First, let's check what tables are available in the database
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
available_tables = cursor.fetchall()
print("\nAvailable tables in the database:", [table[0] for table in available_tables])

# Modify the KPI queries based on what's in the policies table
# Let's first examine the structure of the policies table
cursor.execute("PRAGMA table_info(policies)")
policies_columns = cursor.fetchall()
print("\nColumns in the policies table:", [col[1] for col in policies_columns])

# Create a KPI summary table using only the policies table
kpi_data = {
    'KPI': ['Total Policies', 'Total Premium', 'Total Claims', 'Overall Loss Ratio', 'Claims Frequency'],
    'Value': [
        f"{len(pd.read_sql_query('SELECT * FROM policies', conn)):,}",
        f"${pd.read_sql_query('SELECT SUM(premium_amount) FROM policies', conn).iloc[0, 0]:,.2f}",
        f"${pd.read_sql_query('SELECT SUM(claim_amount) FROM policies', conn).iloc[0, 0]:,.2f}",
        f"{pd.read_sql_query('SELECT SUM(claim_amount)/SUM(premium_amount)*100 FROM policies', conn).iloc[0, 0]:.2f}%",
        f"{pd.read_sql_query('SELECT SUM(has_claim)*100.0/COUNT(*) FROM policies', conn).iloc[0, 0]:.2f}%"
    ]
}
kpi_df = pd.DataFrame(kpi_data).set_index('KPI')
print("\nInsurance KPI Summary:")
print(kpi_df)

# Save KPI data to CSV
kpi_df.to_csv('insurance_kpi_summary.csv')

conn.close()