import azure.functions as func
import logging
import requests
import os
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp()

def get_secret(secret_name):
    key_vault_url = os.getenv("KEY_VAULT_URL")
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def fetch_data(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"Python timer trigger function started at {datetime.utcnow()}") 

    try:
        client_id = get_secret("IGDB_CLIENT_ID")
        client_secret = get_secret("IGDB_CLIENT_SECRET")
    except Exception as e:
        logging.error(f"Error fetching secrets: {e}")
        return
    try:
        token_url = "https://id.twitch.tv/oauth2/token"
        token_params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        token_response = requests.post(token_url, data=token_params)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        igdb_url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }
        query = """
        fields name, rating, rating_count, first_release_date, genres.name, platforms.name;
        where rating > 85 & rating_count > 75;
        sort rating desc;
        limit 10;
        """
        igdb_response = requests.post(igdb_url, headers=headers, data=query)
        igdb_response.raise_for_status()
        games = igdb_response.json()

        logging.info(f"Fetched {len(games)} games from IGDB.")
        for game in games:
            logging.info(f"Game: {game['name']}, Rating: {game['rating']}, Release Date: {datetime.fromtimestamp(game['first_release_date'])}")

    except Exception as e:
        logging.error(f"Error fetching data from IGDB: {e}")
        return

def get_igdb_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    res = requests.post(url, data=params)
    res.raise_for_status()
    return res.json()["access_token"]

def fetch_games(token):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    query = """
    fields name, rating, rating_count, first_release_date, genres.name, platforms.name;
    where rating > 85 & rating_count > 75 & first_release_date > 1420070400;
    sort rating desc;
    limit 25;
    """
    res = requests.post(url, headers=headers, data=query)
    res.raise_for_status()
    return res.json()

def clean_data(raw_data):
    df = pd.json_normalize(raw_data)
    df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s', errors='coerce')
    df['genres'] = df['genres'].apply(extract_names)
    df['platforms'] = df['platforms'].apply(extract_names)
    return df[['name', 'rating', 'rating_count', 'first_release_date', 'genres', 'platforms']]

def extract_names(column_data):
    if isinstance(column_data, list):
        return [item.get('name') if isinstance(item, dict) else item for item in column_data]
    return None

def store_data(df):
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='top_igdb_games' AND xtype='U')
    CREATE TABLE top_igdb_games (
        name NVARCHAR(255),
        rating FLOAT,
        rating_count INT,
        first_release_date DATETIME,
        genres NVARCHAR(MAX),
        platforms NVARCHAR(MAX)
    )
    """)
    
    # Insert data into the table
    for index, row in df.iterrows():
        cursor.execute("""
        INSERT INTO top_igdb_games (name, rating, rating_count, first_release_date, genres, platforms)
        VALUES (?, ?, ?, ?, ?, ?)
        """, row['name'], row['rating'], row['rating_count'], row['first_release_date'], ', '.join(row['genres']), ', '.join(row['platforms']))

    conn.commit()
    cursor.close()
    conn.close()

