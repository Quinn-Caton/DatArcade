import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=datarcade-sqlsrv2.database.windows.net;'
    'DATABASE=datarcade_db;'
    'UID=datarcadeadmin;'
    'PWD=KingdomHearts2!'
)
print("Connected to SQL Server")