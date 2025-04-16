from sqlalchemy import create_engine
import urllib
import pandas as pd

server = 'datarcade-sqlsrv2.database.windows.net'
database = 'datarcade_db'
username = 'datarcadeadmin'
password = 'KingdomHearts2!'
driver = 'ODBC Driver 18 for SQL Server'

params = urllib.parse.quote_plus(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

engine = create_engine(f'mssql+pyodbc:///?odbc_connect={params}')

df = pd.read_sql("SELECT TOP 5 * FROM top_igdb_games", con=engine)
print(df.head())
print("Data fetched from SQL Server successfully.")