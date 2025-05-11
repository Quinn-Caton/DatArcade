import streamlit as st

# Page metadata
st.set_page_config(
    page_title="DatArcade",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="expanded"
)

background_url = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGphYmVscWNybzE2NzZwenNxODM3NmlpeGE5MnpjMWt5cXMzdnlqYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9Igqq02d80wIqUpy/giphy.gif"

# font loading
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)



#  Main style and title
st.markdown(f"""
    <style>

    html, body, [data-testid="stAppViewContainer"] {{
        background-image: url('{background_url}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        height: 100%;
        width: 100%;
        font-family: 'VT323', monospace !important;
        color: #00ffff;
    }}

    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: rgba(0, 0, 0, 0);
    }}

    .block-container {{
        background-color: rgba(0, 0, 0, 0.6);
        font-family: 'VT323', monospace !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    .arcade-title {{
        font-size: 3rem;
        color: #00ffff;
        text-shadow: 2px 2px #ff00ff;
        text-align: center;
        margin-top: 1rem;
    }}

    *,.stApp *,
    .stTextInput > div > div > input,
    .stSelectbox > div,
    .stDataFrame,
    .stSlider > div,
    .stMarkdown,
    .stCaption,
    .stSubheader,
    .stHeading {{
        font-family: 'VT323', monospace !important;
        color: #00ffff !important;
    }}

    /* 🔘 Buttons: Neon arcade style */
    .stButton > button {{
        background-color: #ff00ff;
        color: #00ffff;
        border: 2px solid #00ffff;
        font-family: 'VT323', monospace;
        font-size: 1.3rem;
        padding: 0.4em 1em;
        border-radius: 8px;
        box-shadow: 0 0 10px #00ffff;
        transition: 0.2s ease-in-out;
    }}
    .stButton > button:hover {{
        background-color: #00ffff;
        color: #000000;
        border: 2px solid #ff00ff;
        box-shadow: 0 0 12px #ff00ff, 0 0 20px #ff00ff;
    }}

    /* 🧩 Tabs (horizontal nav bar) */
    .stTabs [role="tablist"] {{
        border-bottom: 3px solid #ff00ff;
    }}
    .stTabs [role="tab"] {{
        font-family: 'VT323', monospace;
        font-size: 1.2rem;
        color: #00ffff;
        border: none !important;
        padding: 10px 18px;
    }}
    .stTabs [role="tab"]:hover {{
        color: #ff00ff;
        text-shadow: 0 0 8px #ff00ff;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #000000;
        border-bottom: 2px solid #00ffff;
        color: #ffffff !important;
    }}

    /* 💫 Glitchy hover on interactive blocks */
    .stMarkdown:hover, .stDataFrame:hover, .stCaption:hover {{
        animation: glow 1s ease-in-out infinite alternate;
    }}

    @keyframes glow {{
        from {{
            text-shadow: 0 0 5px #00ffff, 0 0 10px #ff00ff;
        }}
        to {{
            text-shadow: 0 0 20px #ff00ff, 0 0 30px #00ffff;
        }}
    }}

    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.responsive-title {
    font-family: 'VT323', monospace;
    font-size: clamp(1.5rem, 6vw, 3rem);
    color: #00ffff;
    text-shadow: 2px 2px #ff00ff;
    text-align: center;
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.responsive-title .title-line {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.responsive-title img {
    width: clamp(40px, 10vw, 75px);
    height: auto;
}
</style>

<div class="responsive-title">
    <div class="title-line">
        <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTA1aGEyOGVneHoyMmVtbXE3MHU1bXB6bW1kZ3MyYmZ1amgydGExMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/VNMpMCmV27eEBxFkUF/giphy.gif">
        <span>DAT&lt;A&gt;RCADE</span>
        <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTA1aGEyOGVneHoyMmVtbXE3MHU1bXB6bW1kZ3MyYmZ1amgydGExMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/VNMpMCmV27eEBxFkUF/giphy.gif">
    </div>
    <div>Gaming Trends with Retro Flare</div>
</div>
""", unsafe_allow_html=True)



import pandas as pd
import pyodbc
import os
import json
import matplotlib.pyplot as plt

# --- SQL Connection Setup ---
server = "datarcade-sqlsrv2.database.windows.net"
database = "datarcade_db"
username = os.getenv("SQL_USER")
password = os.getenv("SQL_PASSWORD")
driver = "{ODBC Driver 18 for SQL Server}"

conn_str = (
    f"DRIVER={driver};SERVER={server},1433;DATABASE={database};"
    f"UID={username};PWD={password};Encrypt=yes;"
    f"TrustServerCertificate=no;Connection Timeout=30;"
)

import ast  # use this instead of json for safer literal parsing

def safe_parse(val):
    try:
        return ast.literal_eval(val) if pd.notnull(val) and isinstance(val, str) else []
    except Exception:
        return []

# Load Data
@st.cache_data
def load_data():
    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql("SELECT * FROM top_games ORDER BY rating DESC", conn)

    df['genres'] = df['genres'].apply(safe_parse)
    df['platforms'] = df['platforms'].apply(safe_parse)
    df['year'] = pd.to_datetime(df['first_release_date'], errors='coerce').dt.year
    return df


df = load_data()

# --- Header ---
st.caption("Live data from IGDB via Azure Cloud (SQL + Functions)")

# --- Tabs ---
tabs = st.tabs([
    "Top 10 by Genre",
    "Most Reviewed Games",
    "All-Time Best Games",
    "Platform Distribution",
    "Release Trends",
    "Genre Ratings",
    "Filter Explorer",
    "About",
    "Genre Debugger"
])

# --- Tab 1: Top 10 by Genre ---
with tabs[0]:
    genre_list = sorted({g for sub in df['genres'] for g in sub})
    genre = st.selectbox("Select a genre", genre_list)
    subset = df[(df['genres'].apply(lambda x: genre in x)) & (df['rating_count'] > 25)].nlargest(10, "rating")

    st.subheader(f"Top 10 Games in {genre}")

    for _, row in subset.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            cover = row.get("cover_url")
            if cover and isinstance(cover, str) and cover.startswith("http"):
                st.markdown(f"""
                    <img src="{cover}" style="width:80px; height:auto; object-fit:contain; border-radius:5px;">
                """, unsafe_allow_html=True)
            else:
                st.markdown("🎮")


        with col2:
            st.markdown(f"""
            **{row['name']}**  
            ⭐ Rating: {row['rating']:.1f}  
            🗳️ Reviews: {int(row['rating_count'])}  
            🗓️ Released: {row['first_release_date'].date()}
            """)
        st.markdown("---")


# --- Tab 2: Most Reviewed Games ---
with tabs[1]:
    st.subheader("Most Reviewed Games")
    top_reviewed = df[df['rating_count'] > 25].nlargest(10, "rating_count")

    for _, row in top_reviewed.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            if row.get('cover_url'):
                st.image(row['cover_url'], width=80)
        with col2:
            st.markdown(f"""
            **{row['name']}**  
            🗳️ Reviews: {int(row['rating_count'])}  
            ⭐ Rating: {row['rating']:.1f}  
            🗓️ Released: {row['first_release_date'].date()}
            """)
        st.markdown("---")


# --- Tab 3: All-Time Best Games ---
with tabs[2]:
    st.subheader("All-Time Highest Rated Games")
    top_rated = df[df['rating_count'] > 25].nlargest(10, "rating")

    for _, row in top_rated.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            if row.get('cover_url'):
                st.image(row['cover_url'], width=80)
        with col2:
            st.markdown(f"""
            **{row['name']}**  
            ⭐ Rating: {row['rating']:.1f}  
            🗳️ Reviews: {int(row['rating_count'])}  
            🗓️ Released: {row['first_release_date'].date()}
            """)
        st.markdown("---")


# --- Tab 4: Platform Distribution ---
with tabs[3]:
    st.subheader("Distribution of Top Games by Platform")
    platform_counts = {}
    for platforms in df['platforms']:
        for p in platforms:
            platform_counts[p] = platform_counts.get(p, 0) + 1
    pc = pd.Series(platform_counts).sort_values(ascending=False)
    st.bar_chart(pc.head(15))

# --- Tab 5: Release Trends ---
with tabs[4]:
    st.subheader("Release Volume Over Time")
    yearly = df['year'].value_counts().sort_index()
    yearly.index = yearly.index.astype(str)  # Convert year index to string to remove comma formatting
    st.line_chart(yearly)


# --- Tab 6: Genre Ratings ---
with tabs[5]:
    st.subheader("Average Rating by Genre")
    genre_ratings = []
    for g in genre_list:
        subset = df[df['genres'].apply(lambda x: g in x)]
        if not subset.empty:
            genre_ratings.append((g, subset['rating'].mean()))

    if genre_ratings:
        genre_ratings.sort(key=lambda x: x[1], reverse=True)
        genres, ratings = zip(*genre_ratings)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(genres, ratings)
        ax.invert_yaxis()
        ax.set_xlabel("Average Rating")
        ax.set_title("Genre vs. Avg. Rating")
        st.pyplot(fig)
    else:
        st.warning("No genre data available to display ratings.")


# --- Tab 7: Filter Explorer ---
with tabs[6]:
    st.subheader("🔎 Explore by Filter")
    genre_filter = st.multiselect("Filter by genre", genre_list)
    platform_filter = st.multiselect("Filter by platform", sorted({p for sub in df['platforms'] for p in sub}))
    year_range = st.slider("Select release year range", int(df['year'].min()), int(df['year'].max()), (2015, 2024))

    filtered = df.copy()
    if genre_filter:
        filtered = filtered[filtered['genres'].apply(lambda x: any(g in x for g in genre_filter))]
    if platform_filter:
        filtered = filtered[filtered['platforms'].apply(lambda x: any(p in x for p in platform_filter))]
    filtered = filtered[filtered['year'].between(*year_range)]

    for _, row in filtered.iterrows():
        col1, col2 = st.columns([1, 4])
        with col1:
            if row.get('cover_url'):
                st.image(row['cover_url'], width=80)
        with col2:
            st.markdown(f"""
            **{row['name']}**  
            ⭐ Rating: {row['rating']:.1f}  
            🗳️ Reviews: {int(row['rating_count'])}  
            🗓️ Released: {row['first_release_date'].date()}  
            🎮 Platforms: {", ".join(row['platforms'])}  
            🧬 Genres: {", ".join(row['genres'])}
            """)
        st.markdown("---")

# --- Tab 8: About ---
with tabs[7]:
    st.markdown("""
    ### 🕹️ About DatArcade
    **DatArcade** is a cloud-powered data platform that fetches, cleans, stores, and visualizes gaming data from IGDB (via Twitch Developer API).
    
    - **Backend**: Python + Azure Functions + Azure SQL
    - **Frontend**: Streamlit + Docker
    - **ETL Pipeline**: Automated on a timer (every 5 mins)
    
    Built by Quinn Caton for a cloud computing final project — and a love for games + data!
    """)

# --- Footer / External Links ---
st.markdown("""
<hr style="border: 1px solid #ff00ff; margin-top: 2rem;">

<div style="text-align: center; font-family: 'VT323', monospace; font-size: 1.3rem; color: #00ffff;">
    <p>🕹️ Explore more games at <a href="https://www.igdb.com/" target="_blank" style="color:#ff00ff;">IGDB</a></p>
    <p>Built with ❤️ by Quinn Caton · <a href="https://github.com/Quinn-Caton" target="_blank" style="color:#ff00ff;">GitHub</a></p>
    <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnc0ZjBvZG5ycWl3NW8yeWR6NXVibW1nenBvbDlndm0zaDJqaHZxZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/8gWzY7qwqguqVf7Nhz/giphy.gif" width="200">
</div>
""", unsafe_allow_html=True)
