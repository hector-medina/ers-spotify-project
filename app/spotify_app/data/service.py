import pandas as pd
import streamlit as st

from spotify_app.config.settings import DATA_PATH, NUMERIC_COLUMNS


@st.cache_data
def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    return coerce_numeric_columns(df)


def coerce_numeric_columns(df):
    result = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    return result


def get_present_albums(artist_df):
    return (
        artist_df[["studio_album", "year"]]
        .drop_duplicates()
        .sort_values(["year", "studio_album"])
    )


def filter_album(artist_df, selected_album, all_albums_label):
    if selected_album == all_albums_label:
        return artist_df.copy()

    return artist_df[artist_df["studio_album"] == selected_album].copy()


def build_album_summary(artist_df):
    return (
        artist_df
        .groupby("studio_album")
        .agg(
            tracks=("name", "count"),
            acousticness=("acousticness", "mean"),
            danceability=("danceability", "mean"),
            energy=("energy", "mean"),
            valence=("valence", "mean"),
            year=("year", "min"),
        )
        .reset_index()
        .sort_values("year")
    )


def add_duration_column(df, formatter):
    result = df.copy()

    if "duration_ms" in result.columns:
        result["duration"] = result["duration_ms"].apply(formatter)

    return result


def sort_tracks(df, sort_option, selected_feature, selected_feature_label):
    if sort_option == f"{selected_feature_label} alto a bajo":
        return df.sort_values(selected_feature, ascending=False)

    if sort_option == f"{selected_feature_label} bajo a alto":
        return df.sort_values(selected_feature, ascending=True)

    return df.sort_values(["year", "studio_album", "track_number", "name"])
