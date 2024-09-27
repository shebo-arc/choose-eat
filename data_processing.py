import pandas as pd

# Function to convert the "cal_per_serving" and "kj_per_serving" columns to float
def clean_nutritional_values(value):
    # Extract the float value from the string
    return float(value.split()[0])  # Get the number before the unit

# Load the CSV file
file_path = 'calorie_data.csv'  # Change this to your file path
df = pd.read_csv(file_path)

# Clean the cal_per_serving and kj_per_serving columns
df['cal_per_serving'] = df['cal_per_serving'].apply(clean_nutritional_values)
df['kj_per_serving'] = df['kj_per_serving'].apply(clean_nutritional_values)

# Remove rows where cal_per_serving or kj_per_serving is 0
df_filtered = df[(df['cal_per_serving'] != 0) & (df['kj_per_serving'] != 0)]

# Save the filtered DataFrame to a new CSV file
df_filtered.to_csv('filtered_food_data.csv', index=False)

# Optionally, you can also save the rows that were removed
removed_rows = df[(df['cal_per_serving'] == 0) | (df['kj_per_serving'] == 0)]
removed_rows.to_csv('removed_food_data.csv', index=False)

# Extract unique values from the food_category column
unique_categories = df['food_category'].unique()

# Save unique values to a text file
with open('unique_food_categories.txt', 'w') as file:
    for category in unique_categories:
        file.write(f"{category}\n")

print("Unique food categories have been saved to unique_food_categories.txt")