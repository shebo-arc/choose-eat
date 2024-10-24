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
df = df[(df['cal_per_serving'] != 0) & (df['kj_per_serving'] != 0)]

# Remove rows where 'food_category' is ___
df = df[df['food_category'] != 'Baking Ingredients']
df = df[df['food_category'] != 'Candy & Sweets']
df = df[df['food_category'] != 'Cream Cheese']
df = df[df['food_category'] != 'Canned Fruit']
df = df[df['food_category'] != 'Cheese']
df = df[df['food_category'] != 'Herbs & Spices']
df = df[df['food_category'] != 'Candy & Sweets']
df = df[df['food_category'] != 'Nuts & Seeds']
df = df[df['food_category'] != 'Oatmeal, Muesli & Cereals']
df = df[df['food_category'] != 'Offal & Giblets']
df = df[df['food_category'] != 'Oils & Fats']
df = df[df['food_category'] != 'Sauces & Dressings']
df = df[df['food_category'] != 'Sliced Cheese']
df = df[df['food_category'] != 'Spreads']
df = df[df['food_category'] != 'Vegetable Oils']
df = df[df['food_category'] != 'Vegetables']
df = df[df['food_category'] != 'Sausage']
df = df[df['food_category'] != 'Soda & Soft Drinks']
df = df[df['food_category'] != 'Yogurt']

# Save the filtered DataFrame to a new CSV file
df.to_csv('filtered_food_data.csv', index=False)

# Extract unique values from the food_category column
unique_categories = df['food_category'].unique()

# Save unique values to a text file
with open('unique_food_categories.txt', 'w') as file:
    for category in unique_categories:
        file.write(f"{category}\n")

print("Unique food categories have been saved to unique_food_categories.txt")