import pyodbc
import pandas as pd
import json
import os
from datetime import datetime
import xlwings as xw

# Connect to the database
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PSS\CHDData;DATABASE=ImageLoader;Trusted_Connection=yes;')

# Execute the SQL query and store the results in a pandas dataframe
query = """SELECT ISS.Name, ISF.Filename,  ISF.DateRun, ISFS.Status,  ISF.ExceptionMessage,
                    ISF.FilesInZip, ISF.FilesProcessed, ISF.DocsLoaded, ISF.Errors, ISF.ScanID, ISS.IndexID as CountyIndexId
                      FROM [ImageLoader].[dbo].[ImageSet] ISS
                            inner join [ImageLoader].[dbo].[ImageSetFile] ISF
                                on ISS.ID = ISF.ImageSetID
                            inner Join [ImageLoader].[dbo].[ImageSetFileStatus] ISFS
                                on ISF.StatusID = ISFS.ID
                            --where ISF.ExceptionMessage is not null
                            where ISF.DateRun >= DateAdd(Day, -14, GETDATE()) --Gets the last 14 days of runs
                      order by ISF.DateRun desc
                      """
df1 = pd.read_sql_query(query, conn)

json_file_path = "C:\\Users\\rtorok\\PythonProgram\\county_config.json"

# Load JSON data into a dictionary
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

conn.close() # close the connection


#---This is the MAX Filedate dataframe
# Read the JSON file
with open('county_config.json') as file:
    data = json.load(file)

# Connect to the SQL Server database
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=PSC\CHDData;DATABASE=ImageLoader;Trusted_Connection=yes;')

# Create an empty DataFrame
df2 = pd.DataFrame()
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
    df_temp = pd.DataFrame.from_records(results, columns=[column[0] for column in cursor.description])
    df_temp['County'] = county
    df_temp['CountyIndexId'] = county_index_id

    # Concatenate the temporary DataFrame with the main DataFrame
    df2 = pd.concat([df2, df_temp])

cursor.close()
conn.close() # close the connection
#print(df1)
#print(df2)
#---

data_join = pd.merge(df1, df2, on = 'CountyIndexId', how = 'left')
print(data_join)

# Export the dataframe to a Excel file
# data_join.to_excel('ZipandFiledates.xlsx', index=False, header=True)


# get current date and time
date = datetime.now().strftime('%Y%m%d')
myFileName = f'imagesloadedExcel-{date}.xlsx'
path = '\\\\SMB.dc2isilon.na.drillinginfo.com\\Fileserver1\\UserData\\rtorok\\Image Load Logs\\'

# data_join.to_excel(os.path.join(path, myFileName), engine='openpyxl', index=False)

# auto fit columns for Excel
wb = xw.Book()

# select the first sheet
sheet = wb.sheets[0]

# write the DataFrame to the sheet
sheet.range('A1').value = data_join

# auto-fit the columns
sheet.autofit()

# set column headings color to light blue
sheet.range('A1..N1').color = (0, 255, 255)

# save the workbook
wb.save(os.path.join(path, myFileName))

# close the workbook
wb.close()

