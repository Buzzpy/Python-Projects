import pandas as pd

# Sample data
data1 = {'ID': [1, 2, 3], 'Name': ['Dave', 'Nick', 'Barton']}
data2 = {'ID': [1, 2, 4], 'Age': [25, 30, 35]}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Merging DataFrames
merged_df = pd.merge(df1, df2, on='ID')
print(merged_df)
