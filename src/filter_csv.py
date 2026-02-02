import pandas as pd

# Load the CSV file
input_file = "test2.csv"   # Replace with your actual file path
output_file = "filtered_output.csv"

# Read the CSV
df = pd.read_csv(input_file)

# Filter columns that do NOT contain ' - '
filtered_columns = [col for col in df.columns if " - " not in col]

# Create a new DataFrame with the filtered columns
filtered_df = df[filtered_columns]

# Save to a new CSV file
filtered_df.to_csv(output_file, index=False)

print(f"Filtered CSV saved to: {output_file}")
