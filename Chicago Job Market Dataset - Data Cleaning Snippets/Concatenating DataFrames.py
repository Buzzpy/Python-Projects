import pandas as pd

# Sample data
data1 = {'ID': [1, 2, 3], 'Name': ['Dave', 'Nick', 'Barton']}
data2 = {'ID': [4, 5, 6], 'Name': ['Eric', 'Mark', 'Adam']}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Concatenate DataFrames vertically
concatenated_df_vertical = pd.concat([df1, df2], ignore_index=True)
