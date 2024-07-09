import pandas as pd
import re

# Read the original CSV file
original_csv_file = "apk_metadata.csv"
data = pd.read_csv(original_csv_file)

# Clean 'Number of Downloads' column
data['Number of Downloads'] = data['Number of Downloads'].str.replace(',', '')  # Remove commas
data['Number of Downloads'] = data['Number of Downloads'].apply(lambda x: re.sub(r'\D', '', x))  # Remove non-numeric characters

# Convert 'Number of Downloads' column to integers
data['Number of Downloads'] = data['Number of Downloads'].astype(int)

# Filter rows with Number of Downloads more than 100,000
filtered_data = data[data['Number of Downloads'] >= 100000]

# Specify the name for the new CSV file
filtered_csv_file = "apk_metadata_filtered.csv"

# Save the filtered data to a new CSV file
filtered_data.to_csv(filtered_csv_file, index=False)

print("Filtered data saved to:", filtered_csv_file)
