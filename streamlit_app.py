import streamlit as st
import pandas as pd

st.set_page_config(page_title="DatArcade", layout="wide")

# Load your data
df = pd.read_csv("top_games.csv")

# Title
st.title("🎮 DatArcade: Top-Rated Games Explorer")

# Filters
min_rating = st.slider("Minimum Rating", 0, 100, 85)
min_reviews = st.slider("Minimum # of User Ratings", 0, int(df["rating_count"].max()), 100)

filtered_df = df[(df["rating"] >= min_rating) & (df["rating_count"] >= min_reviews)]

# Show results
st.metric(label="Games Found", value=len(filtered_df))
st.dataframe(filtered_df)

# Optional: Chart
st.subheader("Rating Distribution")
st.bar_chart(filtered_df.sort_values("rating", ascending=False)[["name", "rating"]].set_index("name"))
