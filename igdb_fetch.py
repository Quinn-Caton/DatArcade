import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")

# Step 1: Get Access Token
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

# Step 2: Fetch Data from IGDB
def fetch_games(token):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    query = """
    fields name, rating, rating_count, first_release_date, involved_companies.company.name, genres.name, platforms.name;
    where rating > 85 & rating_count > 75 & first_release_date > 1420070400;
    sort rating desc;
    limit 25;
    """

    res = requests.post(url, headers=headers, data=query)
    res.raise_for_status()
    return res.json()

# Step 3: Clean and Convert to DataFrame
def clean_data(raw_data):
    df = pd.json_normalize(raw_data)
    df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s', errors='coerce')
    return df[['name', 'involved_companies', 'rating', 'rating_count', 'first_release_date', 'genres', 'platforms']]

def extract_names(column_data):
    if isinstance(column_data, list):
        return [item.get('name') if isinstance(item, dict) else item for item in column_data]
    return None

def extract_company_names(company_list):
    if isinstance(company_list, list):
        return [c.get('company', {}).get('name') for c in company_list if 'company' in c]
    return None


if __name__ == "__main__":
    token = get_igdb_token()
    raw = fetch_games(token)
    df = clean_data(raw)
    df['involved_companies'] = df['involved_companies'].apply(extract_company_names)
    df['genres'] = df['genres'].apply(extract_names)
    print(df.head())
    df.to_csv("top_games.csv", index=False)
