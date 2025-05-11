import azure.functions as func
import logging
import os
import requests
import pandas as pd
import pyodbc
from datetime import datetime
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.keyvault.secrets import SecretClient
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError

app = func.FunctionApp()

# --- Key Vault Helper ---
def get_secret(name):
    key_vault_url = os.getenv("KEY_VAULT_URL")
    
    try:
        credential = AzureCliCredential()
        logging.info("Using AzureCliCredential.")
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        return client.get_secret(name).value
    except Exception as cli_error:
        logging.warning(f"AzureCliCredential failed: {cli_error}")
    
    try:
        credential = DefaultAzureCredential(additionally_allowed_tenants=["*"])
        logging.info("Falling back to DefaultAzureCredential.")
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        return client.get_secret(name).value
    except Exception as default_error:
        logging.error(f"DefaultAzureCredential failed: {default_error}")
        raise

# --- Clean IGDB data ---
def clean_igdb_data(raw):
    df = pd.json_normalize(raw)
    df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s', errors='coerce')
    df['genres'] = df['genres'].apply(lambda g: [genre['name'] for genre in g] if isinstance(g, list) else [])
    df['platforms'] = df['platforms'].apply(lambda p: [plat['name'] for plat in p] if isinstance(p, list) else [])
    df['cover_url'] = df['cover.image_id'].apply(
        lambda img_id: f"https://images.igdb.com/igdb/image/upload/t_cover_big/{img_id}.jpg" if pd.notnull(img_id) else None
    )
    df = df.dropna(subset=['name', 'rating', 'rating_count', 'first_release_date'])
    return df[['name', 'rating', 'rating_count', 'first_release_date', 'genres', 'platforms', 'cover_url']]

# --- Insert into Azure SQL ---
def insert_into_sql(df, user, password):
    server = "datarcade-sqlsrv2.database.windows.net"
    database = "datarcade_db"
    driver = "{ODBC Driver 18 for SQL Server}"

    conn_str = (
        f"DRIVER={driver};SERVER={server},1433;DATABASE={database};"
        f"UID={user};PWD={password};Encrypt=yes;"
        f"TrustServerCertificate=no;Connection Timeout=30;"
    )

    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT 1 FROM top_games WHERE name = ? AND first_release_date = ?
                )
                BEGIN
                    INSERT INTO top_games (name, rating, rating_count, first_release_date, genres, platforms, cover_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                END
            """, row['name'], row['first_release_date'],
                 row['name'], row['rating'], row['rating_count'],
                 row['first_release_date'], str(row['genres']), str(row['platforms']), row['cover_url'])

        conn.commit()

# --- Timer Trigger Function ---
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def fetch_data(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info(f"Python timer trigger function started at {datetime.utcnow()}")

    try:
        client_id = get_secret("IGDB-Client-ID")
        client_secret = get_secret("IGDB-Client-Secret")
        sql_user = get_secret("sql-user")
        sql_password = get_secret("sql-password")
        table_conn_str = get_secret("azure-storage-connection-string")
    except Exception as e:
        logging.error(f"Error fetching secrets: {e}")
        return

    # Initialize table client
    table_service = TableServiceClient.from_connection_string(conn_str=table_conn_str)
    table_name = "genreindex"
    table_client = table_service.get_table_client(table_name)

    # Load state
    try:
        genre_entity = table_client.get_entity(partition_key="genre", row_key="state")
        offset_entity = table_client.get_entity(partition_key="offset", row_key="state")
        genre_index = int(genre_entity["Index"])
        offset = int(offset_entity["Offset"])
    except ResourceNotFoundError:
        genre_index = 0
        offset = 0
        table_client.upsert_entity({"PartitionKey": "genre", "RowKey": "state", "Index": genre_index}, mode=UpdateMode.REPLACE)
        table_client.upsert_entity({"PartitionKey": "offset", "RowKey": "state", "Offset": offset}, mode=UpdateMode.REPLACE)

    genre_list = [
        "Role-playing (RPG)", "Shooter", "Adventure", "Platform", "Puzzle",
        "Simulator", "Strategy", "Fighting", "Racing", "Indie", "Arcade", "Card & Board Game",
        "Hack and slash/Beat 'em up", "MOBA", "Music", "Pinball", "Point-and-click", "Quiz/Trivia",
        "Racing", "Real Time Strategy (RTS)", "Sport", "Tactical", "Turn-based strategy (TBS)",
        "Visual Novel"
    ]
    selected_genre = genre_list[genre_index % len(genre_list)]
    logging.info(f"Fetching games for genre: {selected_genre}, offset={offset}")

    try:
        # Get Twitch access token
        token_url = "https://id.twitch.tv/oauth2/token"
        token_res = requests.post(token_url, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        })
        token_res.raise_for_status()
        token = token_res.json()["access_token"]

        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {token}"
        }

        # Queries
        queries = {
            "top_rated": f"""
                fields name, rating, rating_count, first_release_date, genres.name, platforms.name, cover.image_id;
                where rating > 50 & rating_count > 10 & first_release_date > 91514880 & genres.name = "{selected_genre}";
                sort rating desc;
                limit 100;
            """,
            "most_reviewed": f"""
                fields name, rating, rating_count, first_release_date, genres.name, platforms.name, cover.image_id;
                where rating_count > 100 & first_release_date > 91514880 & genres.name = "{selected_genre}";
                sort rating_count desc;
                limit 100;
            """
        }

        all_games = []

        for label, query in queries.items():
            res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
            res.raise_for_status()
            games = res.json()
            logging.info(f"{label}: Fetched {len(games)} games.")
            all_games.extend(games)

        if not all_games:
            logging.warning("No games returned from either query; skipping insert.")
        else:
            df = clean_igdb_data(all_games)
            insert_into_sql(df, sql_user, sql_password)

        # Update rotation index
        genre_index = (genre_index + 1) % len(genre_list)

        table_client.upsert_entity({"PartitionKey": "genre", "RowKey": "state", "Index": genre_index}, mode=UpdateMode.REPLACE)
        table_client.upsert_entity({"PartitionKey": "offset", "RowKey": "state", "Offset": offset}, mode=UpdateMode.REPLACE)

        logging.info("Genre + offset updated and data insertion complete.")

    except Exception as e:
        logging.error(f"Error during IGDB fetch or SQL insert: {e}")

