import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate sample data
n_records = 1000
policy_types = ['Auto', 'Home', 'Life', 'Commercial']
states = ['CA', 'TX', 'NY', 'FL', 'IL', 'OH', 'MI', 'PA', 'GA', 'NC']

# Create random dates
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 3, 1)
days_between = (end_date - start_date).days

# Generate the dataset
np.random.seed(42)
data = {
    'policy_id': range(1001, 1001 + n_records),
    'policy_type': [random.choice(policy_types) for _ in range(n_records)],
    'state': [random.choice(states) for _ in range(n_records)],
    'customer_age': np.random.randint(18, 85, n_records),
    'premium_amount': np.round(np.random.uniform(500, 5000, n_records), 2),
    'issue_date': [(start_date + timedelta(days=random.randint(0, days_between))).strftime('%Y-%m-%d') for _ in range(n_records)],
    'has_claim': np.random.choice([0, 1], n_records, p=[0.8, 0.2]),
}

# Add claim amount only for policies with claims
data['claim_amount'] = [round(np.random.uniform(100, data['premium_amount'][i]*1.5), 2) if data['has_claim'][i] == 1 else 0 for i in range(n_records)]

# Create DataFrame
insurance_df = pd.DataFrame(data)

# Save to CSV
insurance_df.to_csv('insurance_data.csv', index=False)

print("Dataset successfully created with", n_records, "records")