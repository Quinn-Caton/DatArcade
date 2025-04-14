import streamlit as st
import pandas as pd

df = pd.read_csv("top_games.csv")
st.title("Top IGDB-Rated Games")
st.dataframe(df)