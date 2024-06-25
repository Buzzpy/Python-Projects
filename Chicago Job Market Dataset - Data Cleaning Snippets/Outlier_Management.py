# The full-script for cleaning this dataset is in the `main.py` file. 
# This file includes managing and visulaizing outliers in the dataset using Plotly and Pandas

import pandas as pd
import re
import plotly.express as px
df = pd.read_csv('Indeed_tech jobs_chicago_2024.csv') # loading the CSV file

# Specify the columns you want to keep
columns_to_keep = ['company', 'companyInfo/rating', 'description', 'jobType/0', 'location', 'positionName', 'postingDateParsed', 'salary']
# Keep only the columns you want
df = df[columns_to_keep] # updating the dataframe

# key = existing name
# value = new name
renamed_columns = {'companyInfo/rating': 'Company Rating',
        'jobType/0': 'Job Type',
        'postingDateParsed': 'Date Posted'}

# call rename () method
df.rename(columns=renamed_columns,
          inplace=True)
df['salary'] = df['salary'].astype(str)
# Removing all the texts, strings, chars and dollar sign in salary column
df['salary'] = df['salary'].apply(lambda x: re.sub(r'[^\d.-]', '', x))
# If the data points include a range with hyphen (-), calculate and update the value for avg of the range.
df['salary'] = df['salary'].apply(lambda x: sum(map(float, x.split('-')))/2 if '-' in x else float(x) if x != '' else 0)
# Checking whether the values in salary column data points are high or less than 100.
df['salary'] = df['salary'].apply(lambda x: x if x > 100 else x * 2000)
df['salary'] = df['salary'].apply(lambda x: None if x == 0.0 else x)
df = df.dropna(subset=['salary'])

#--------- Outlier detection ------------#

mean_salary = df['salary'].mean()
std_salary = df['salary'].std()
cutoff = std_salary * 3
#cut off mark is 3 times the standard deviation from the mean value
df['Outlier'] = df['salary'].apply(lambda x: abs(x - mean_salary) > cutoff)
#if the any datapoint is greater than its value minus mean slsary, it's an outlier

# Separate the outliers
outliers = df[df['Outlier']]
non_outliers = df[~df['Outlier']]

#--------- Plotting the data with Plotly----------#
fig = px.scatter(non_outliers, x='company', y='salary', title='Salaries of Job Positions with Outliers Highlighted', labels={'positionName': 'Job Position', 'salary': 'Salary'})
fig.add_scatter(x=outliers['positionName'], y=outliers['salary'], mode='markers', marker=dict(color='red'), name='Outliers')

fig.show()

# Print rows where 'Outlier' is True
outliers = df[df['Outlier']]
print(outliers)

# Identifying indices of rows with outliers
outlier_indices = df[df['Outlier']].index

# Removing these rows from the DataFrame
df.drop(index=outlier_indices, inplace=True)
# Removing the 'Outlier' column as it's no longer needed
df.drop(columns=['Outlier'], inplace=True)
