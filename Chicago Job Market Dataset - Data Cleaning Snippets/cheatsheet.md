
# Data Cleaning with Python/Pandas Cheatsheet

## Step 1: Import Libraries

```python
import pandas as pd
import numpy as np
```

## Step 2: Load Your Dataset

```python
# Assuming your dataset is in a CSV file
df = pd.read_csv('your_dataset.csv')
```

## Step 3: Initial Exploration

```python
# Display the first few rows
df.head()

# Check the dimensions of the DataFrame
df.shape

# Summary statistics
df.describe()

# Data types of columns
df.dtypes

# Check for missing values
df.isnull().sum()

```
## Step 4: Cleaning Columns
### Select/Remove Columns
```python
#selection of columns
columns_to_keep = ['column 1', 'column 2', 'column 3']
df = df[columns_to_keep]

#deletion of unwanted columns
df.drop(['column 1', 'column 1'], inplace=True)
```
### Rename Columns
```python
df.rename(columns={'old_name1': 'new_name1', 'old_name2': 'new_name2'}, inplace=True)
```

## Step 5: Handle Missing Data

```python
# Drop rows with missing values
df.dropna()

# Fill missing values with a specific value
df.fillna(value)

# Fill missing values with mean, median, or mode
df.fillna(df.mean())
df.fillna(df.median())
df.fillna(df.mode().iloc[0])
```

## Step 6: Handle Duplicates

```python
# Drop duplicates
df.drop_duplicates()

# Count duplicates
df.duplicated().sum()
```

## Step 7: Correct Data Types

```python
# Convert a column to numeric
df['column'] = pd.to_numeric(df['column'], errors='coerce')

# Convert a column to datetime
df['date_column'] = pd.to_datetime(df['date_column'])

# Convert categorical data
df['category_column'] = df[‘category_column'].astype('category')
```

## Step 8: Handle Outliers
Method I: For datasets with a variety of data with no connections between datapoints.
```python
mean_salary = df['column'].mean() #Find the mean
std_salary = df['column'].std() #Find standard deviation
cutoff = std_salary * 3 #determining the cutoff
df['Outlier'] = df['column'].apply(lambda x: abs(x - mean_salary) > cutoff)
#Creates a new column to 

# Print rows where 'Outlier' is True
outliers = df[df['Outlier']]
print(outliers)
```
Method II:
```python
# Identify and handle outliers (e.g., replace with median or mean)
Q1 = df['column'].quantile(0.25)
Q3 = df['column'].quantile(0.75)
IQR = Q3 - Q1
df = df[(df['column'] >= Q1 - 1.5 * IQR) & (df['column'] <= Q3 + 1.5 * IQR)]
```


## Step 9: Text Cleaning (if applicable)

```python
# Convert text to lowercase
df['text_column'] = df['text_column'].str.lower()

# Remove leading/trailing whitespaces
df['text_column'] = df['text_column'].str.strip()

# Remove special characters
df['text_column'] = df['text_column'].str.replace('[^a-zA-Z0-9]', ' ‘)

```

## Step 10: Feature Engineering (if applicable)

```python
# Create new columns from existing ones
df['new_column'] = df['existing_column'].apply(lambda x: function(x))
```

## Step 11: Combining DataFrames (if applicable)
### Merging Dataframes
```python
merged_df = pd.merge(df1, df2, on='column')
```
### Concatenating DataFrames
```python
# Vertically (adding columns)
concatenated_df_vertical = pd.concat([df1, df2], ignore_index=True)

# Hoizontally (adding rows)
concatenated_df_horizontal = pd.concat([df1, df2], axis=1)

```

## Step 12: Save Cleaned Data

```python
# Save cleaned dataset to a new CSV file
df.to_csv('cleaned_dataset.csv', index=False)

# Save to Excel
df.to_excel('cleaned_data.xlsx', index=False)

# Save to JSON
df.to_json('cleaned_data.json', orient='records', lines=True)
```


## Best Practices / Tips
- Always make a copy of your original dataset before cleaning (`df_original = df.copy()`).
- Document your steps and transformations for reproducibility.
- Consult Pandas documentation and community forums for advanced techniques and specific issues.
