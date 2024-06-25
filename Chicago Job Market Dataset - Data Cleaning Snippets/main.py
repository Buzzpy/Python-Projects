import pandas as pd
import re
import plotly.express as px

df = pd.read_csv('Indeed_tech jobs_chicago_2024.csv') # loading the CSV file

# Specify the columns you want to keep
columns_to_keep = ['company', 'companyInfo/rating', 'description', 'jobType/0', 'location', 'positionName', 'postingDateParsed', 'salary']

df = df[columns_to_keep] # updating the dataframe

# key = existing name
# value = new name
renamed_columns = {'companyInfo/rating': 'Company Rating',
        'jobType/0': 'Job Type',
        'postingDateParsed': 'Date Posted'}

# call rename () method
df.rename(columns=renamed_columns,
          inplace=True)

print("Duplicates not removed: ", df.shape)
df = df.drop_duplicates()
print("Duplicates removed:",df.shape)

df['salary'] = df['salary'].astype(str)
# Removing all the texts, strings, chars and dollar sign in salary column
df['salary'] = df['salary'].apply(lambda x: re.sub(r'[^\d.-]', '', x))
# If the data points include a range with hyphen (-), calculate and update the value for avg of the range.
df['salary'] = df['salary'].apply(lambda x: sum(map(float, x.split('-')))/2 if '-' in x else float(x) if x != '' else 0)
# Checking whether the values in salary column data points are high or less than 100.
df['salary'] = df['salary'].apply(lambda x: x if x > 100 else x * 2000)

df['Company Rating'].fillna("N/A", inplace=True)
df['Job Type'].fillna("N/A", inplace=True)

print("before deleting null values: ", df.shape)
# Replace 0.0 float values with None
df['salary'] = df['salary'].apply(lambda x: None if x == 0.0 else x)
df = df.dropna(subset=['salary'])
print("after deleting null values: ",df.shape)


df['Date Posted'] = df['Date Posted'].astype(str) # Because the split() function only works in strings
df['Date Posted'] = df['Date Posted'].apply(lambda x: x.split('T')[0])
#Split the text by T and then remove it.


df = df.map(lambda x: x.strip() if isinstance(x, str) else x) # Removing whitespaces
df = df.map(lambda x: x.lower() if isinstance(x, str) else x) # Converting text to lowercase

# Outlier detection
mean_salary = df['salary'].mean()
std_salary = df['salary'].std()
cutoff = std_salary * 3
df['Outlier'] = df['salary'].apply(lambda x: abs(x - mean_salary) > cutoff)
# Print rows where 'Outlier' is True
outliers = df[df['Outlier']]
print(outliers)

print("before removing outliers: ", df.shape)

# Identifying indices of rows with outliers
outlier_indices = df[df['Outlier']].index

# Removing these rows from the DataFrame
df.drop(index=outlier_indices, inplace=True)

# Removing the 'Outlier' column as it's no longer needed
df.drop(columns=['Outlier'], inplace=True)
print("after removing outliers: ", df.shape)
print(df)


print(df)


