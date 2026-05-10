#!/usr/bin/env python3
"""
prepare_data.py

Este script prepara un dataset pequeño para desplegar la app en Streamlit.

Entrada:
    tracks_features.csv

Salida:
    data/spotify_studio_tracks_10_artists.csv

Qué hace:
    1. Carga el dataset grande de Spotify.
    2. Extrae el artista principal desde la columna artists.
    3. Limpia el nombre de los álbumes.
    4. Filtra solo los 10 artistas definidos en studio_albums_10.py.
    5. Filtra solo canciones pertenecientes a álbumes de estudio.
    6. Elimina duplicados.
    7. Guarda un CSV pequeño para usar en Streamlit.

Uso:
    python3 prepare_data.py

Requisitos:
    - tracks_features.csv debe estar en la raíz del proyecto.
    - studio_albums_10.py debe estar en la raíz del proyecto.
"""

import ast
import os
import re
from pathlib import Path

import pandas as pd

from studio_albums_10 import STUDIO_ALBUMS, normalize_text


INPUT_CSV = "tracks_features.csv"
OUTPUT_DIR = Path("data")
OUTPUT_CSV = OUTPUT_DIR / "spotify_studio_tracks_10_artists.csv"


USE_COLUMNS = [
    "id",
    "name",
    "album",
    "album_id",
    "artists",
    "artist_ids",
    "track_number",
    "disc_number",
    "explicit",
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
    "time_signature",
    "year",
    "release_date",
]


def parse_artists(artists_value):
    """
    Convierte la columna artists en una lista real de Python.

    En el CSV suele venir así:
        "['Radiohead']"

    Y queremos convertirlo en:
        ['Radiohead']
    """
    if pd.isna(artists_value):
        return []

    try:
        parsed = ast.literal_eval(str(artists_value))
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    return []


def get_primary_artist(artists_value):
    """
    Devuelve el primer artista de la lista.
    """
    artists = parse_artists(artists_value)

    if not artists:
        return None

    return artists[0]


def clean_album_name(album_name):
    """
    Crea un nombre de álbum más limpio para comparar con STUDIO_ALBUMS.

    Ejemplos:
        "OK Computer (OKNOTOK 1997 2017)" -> "OK Computer"
        "The Bends (Deluxe Edition)" -> "The Bends"
    """
    if pd.isna(album_name):
        return ""

    album_name = str(album_name).strip()

    # Quitar texto entre paréntesis o corchetes.
    album_name = re.sub(r"\(.*?\)", "", album_name)
    album_name = re.sub(r"\[.*?\]", "", album_name)

    # Quitar sufijos comunes después de guion.
    album_name = re.sub(
        r"\s*-\s*(Deluxe|Expanded|Remastered|Remaster|Special Edition|Anniversary).*",
        "",
        album_name,
        flags=re.IGNORECASE,
    )

    album_name = re.sub(r"\s+", " ", album_name).strip()

    return album_name


def build_allowed_album_table():
    """
    Construye una tabla con:
        artist
        studio_album
        studio_album_normalized

    A partir del diccionario STUDIO_ALBUMS.
    """
    rows = []

    for artist, albums in STUDIO_ALBUMS.items():
        for album in albums:
            rows.append(
                {
                    "primary_artist": artist,
                    "studio_album": album,
                    "studio_album_normalized": normalize_text(album),
                }
            )

    return pd.DataFrame(rows)


def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(
            f"No se encuentra {INPUT_CSV}. "
            "Pon tracks_features.csv en la raíz del proyecto antes de ejecutar este script."
        )

    print("Cargando dataset grande...")
    df = pd.read_csv(INPUT_CSV, usecols=USE_COLUMNS)

    print(f"Filas originales: {len(df):,}")

    print("Extrayendo artista principal...")
    df["primary_artist"] = df["artists"].apply(get_primary_artist)

    print("Limpiando nombres de álbumes...")
    df["short_album_name"] = df["album"].apply(clean_album_name)
    df["album_normalized"] = df["short_album_name"].apply(normalize_text)

    selected_artists = list(STUDIO_ALBUMS.keys())

    print("Filtrando los 10 artistas seleccionados...")
    df = df[df["primary_artist"].isin(selected_artists)].copy()

    print(f"Filas tras filtrar artistas: {len(df):,}")

    allowed_albums = build_allowed_album_table()

    print("Filtrando álbumes de estudio...")
    df = df.merge(
        allowed_albums,
        left_on=["primary_artist", "album_normalized"],
        right_on=["primary_artist", "studio_album_normalized"],
        how="inner",
    )

    print(f"Filas tras filtrar álbumes de estudio: {len(df):,}")

    print("Eliminando duplicados...")
    df = df.sort_values(
        by=[
            "primary_artist",
            "year",
            "studio_album",
            "disc_number",
            "track_number",
            "name",
        ]
    )

    df = df.drop_duplicates(
        subset=[
            "primary_artist",
            "studio_album",
            "name",
        ],
        keep="first",
    )

    print(f"Filas finales: {len(df):,}")

    final_columns = [
        "id",
        "name",
        "primary_artist",
        "artists",
        "artist_ids",
        "album",
        "short_album_name",
        "studio_album",
        "track_number",
        "disc_number",
        "explicit",
        "year",
        "release_date",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "time_signature",
    ]

    df = df[final_columns].reset_index(drop=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Guardando CSV final en: {OUTPUT_CSV}")
    df.to_csv(OUTPUT_CSV, index=False)

    print()
    print("Resumen por artista:")
    summary = (
        df.groupby("primary_artist")
        .agg(
            tracks=("name", "count"),
            albums=("studio_album", "nunique"),
            first_year=("year", "min"),
            last_year=("year", "max"),
        )
        .sort_values("primary_artist")
    )

    print(summary)

    print()
    print("Proceso terminado correctamente.")


if __name__ == "__main__":
    main()
