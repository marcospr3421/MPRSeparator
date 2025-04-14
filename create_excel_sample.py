import pandas as pd

# Read the CSV file
df = pd.read_csv('sample_data.csv')

# Save as Excel file
df.to_excel('sample_data.xlsx', index=False)

print("Excel file created successfully!") 