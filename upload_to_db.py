from sqlalchemy import create_engine
import urllib
import pandas as pd

df = pd.read_csv("top_games.csv")

server = 'datarcade-sqlsrv2.database.windows.net'
database = 'datarcade_db'
username = 'datarcadeadmin'
password = 'KingdomHearts2!'
driver = 'ODBC Driver 18 for SQL Server'

params = urllib.parse.quote_plus(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)

engine = create_engine(f'mssql+pyodbc:///?odbc_connect={params}')

df.to_sql('top_igdb_games', con=engine, if_exists='append', index=False)
print("Data uploaded to SQL Server successfully.")