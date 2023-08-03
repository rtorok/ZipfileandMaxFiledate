import pandas as pd
import pyodbc
import json

# Read the JSON file
with open('jscounty_config.json') as file:
    data = json.load(file)

# Create an empty DataFrame
df2 = pd.DataFrame()

# Connect to the SQL Server database
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PSC\CHDData;DATABASE=ImageLoader;Trusted_Connection=yes;')

# Iterate over each item in the JSON data
for item in data:
    county = item['county']
    county_index_id = item['countyindexid']
    sql_statement = item['sql']

    # Execute the SQL statement
    cursor = conn.cursor()
    cursor.execute(sql_statement)

    # Fetch the results and add them to the DataFrame
    results = cursor.fetchall()
    df_temp = pd.DataFrame(results, columns=[column[0] for column in cursor.description])
    df_temp['County'] = county
    df_temp['CountyIndexId'] = county_index_id

    # Concatenate the temporary DataFrame with the main DataFrame
    df2 = pd.concat([df2, df_temp])

# Close the database connection
conn.close()

# Print the final DataFrame
df2.to_csv('date.csv', index=False, date_format='%m/%d/%Y %H:%M')
#print(df2)