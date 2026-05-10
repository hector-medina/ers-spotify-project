"""
studio_albums_10.py

Lista cerrada de álbumes de estudio para 10 artistas presentes en tracks_features.csv.

Uso en notebook:

    from studio_albums_10 import STUDIO_ALBUMS, get_studio_albums, filter_studio_albums

    get_studio_albums("Radiohead")

    df_studio = filter_studio_albums(
        df,
        artist_name="Radiohead",
        artist_col="primary_artist",
        album_col="short_album_name"
    )

Idea:
- STUDIO_ALBUMS es un diccionario clave-valor.
- clave = artista
- valor = lista de álbumes de estudio
"""

import re
import unicodedata
import pandas as pd


STUDIO_ALBUMS = {
    "Radiohead": [
        "Pablo Honey",
        "The Bends",
        "OK Computer",
        "Kid A",
        "Amnesiac",
        "Hail to the Thief",
        "In Rainbows",
        "The King of Limbs",
        "A Moon Shaped Pool",
    ],

    "The Smiths": [
        "The Smiths",
        "Meat Is Murder",
        "The Queen Is Dead",
        "Strangeways, Here We Come",
    ],

    "Rage Against The Machine": [
        "Rage Against the Machine",
        "Evil Empire",
        "The Battle of Los Angeles",
        "Renegades",
    ],

    "Nirvana": [
        "Bleach",
        "Nevermind",
        "In Utero",
    ],

    "Metallica": [
        "Kill 'Em All",
        "Ride the Lightning",
        "Master of Puppets",
        "...And Justice for All",
        "Metallica",
        "Load",
        "Reload",
        "St. Anger",
        "Death Magnetic",
        "Hardwired... to Self-Destruct",
        "72 Seasons",
    ],

    "Coldplay": [
        "Parachutes",
        "A Rush of Blood to the Head",
        "X&Y",
        "Viva la Vida or Death and All His Friends",
        "Mylo Xyloto",
        "Ghost Stories",
        "A Head Full of Dreams",
        "Everyday Life",
        "Music of the Spheres",
        "Moon Music",
    ],

    "Daft Punk": [
        "Homework",
        "Discovery",
        "Human After All",
        "Random Access Memories",
    ],

    "Arctic Monkeys": [
        "Whatever People Say I Am, That's What I'm Not",
        "Favourite Worst Nightmare",
        "Humbug",
        "Suck It and See",
        "AM",
        "Tranquility Base Hotel & Casino",
        "The Car",
    ],

    "Red Hot Chili Peppers": [
        "The Red Hot Chili Peppers",
        "Freaky Styley",
        "The Uplift Mofo Party Plan",
        "Mother's Milk",
        "Blood Sugar Sex Magik",
        "One Hot Minute",
        "Californication",
        "By the Way",
        "Stadium Arcadium",
        "I'm with You",
        "The Getaway",
        "Unlimited Love",
        "Return of the Dream Canteen",
    ],

    "Pink Floyd": [
        "The Piper at the Gates of Dawn",
        "A Saucerful of Secrets",
        "More",
        "Ummagumma",
        "Atom Heart Mother",
        "Meddle",
        "Obscured by Clouds",
        "The Dark Side of the Moon",
        "Wish You Were Here",
        "Animals",
        "The Wall",
        "The Final Cut",
        "A Momentary Lapse of Reason",
        "The Division Bell",
        "The Endless River",
    ],
}


def normalize_text(text):
    """
    Normaliza texto para comparar nombres de álbumes aunque tengan:
    - mayúsculas/minúsculas distintas
    - acentos
    - signos raros
    - paréntesis con Deluxe Edition / Remastered, etc.
    """
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # Quitar texto entre paréntesis o corchetes
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"\[.*?\]", " ", text)

    # Quitar palabras típicas de reediciones
    words_to_remove = [
        "deluxe",
        "edition",
        "expanded",
        "anniversary",
        "remaster",
        "remastered",
        "version",
    ]

    for word in words_to_remove:
        text = re.sub(rf"\b{word}\b", " ", text)

    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_studio_albums(artist_name):
    """
    Devuelve la lista de álbumes de estudio de un artista.

    Ejemplo:
        get_studio_albums("Radiohead")
    """
    if artist_name not in STUDIO_ALBUMS:
        available = ", ".join(STUDIO_ALBUMS.keys())
        raise ValueError(
            f"Artista no disponible: {artist_name}. "
            f"Artistas disponibles: {available}"
        )

    return STUDIO_ALBUMS[artist_name]


def get_studio_albums_normalized(artist_name):
    """
    Devuelve los álbumes de estudio normalizados.
    """
    return {normalize_text(album) for album in get_studio_albums(artist_name)}


def filter_studio_albums(df, artist_name, artist_col="primary_artist", album_col="short_album_name"):
    """
    Filtra un DataFrame para dejar solo canciones de álbumes de estudio.

    Parámetros:
        df:
            DataFrame original.

        artist_name:
            Nombre del artista. Debe existir en STUDIO_ALBUMS.

        artist_col:
            Columna donde está el artista.
            En el notebook puedes crearla a partir de artists.

        album_col:
            Columna donde está el nombre limpio del álbum.
            En el notebook suele ser short_album_name.

    Devuelve:
        DataFrame filtrado.
    """
    allowed_albums = get_studio_albums_normalized(artist_name)

    result = df.copy()
    result["_artist_normalized"] = result[artist_col].apply(normalize_text)
    result["_album_normalized"] = result[album_col].apply(normalize_text)

    artist_normalized = normalize_text(artist_name)

    result = result[
        (result["_artist_normalized"] == artist_normalized)
        & (result["_album_normalized"].isin(allowed_albums))
    ].copy()

    result = result.drop(columns=["_artist_normalized", "_album_normalized"])

    return result


def available_artists():
    """
    Devuelve los artistas disponibles en el diccionario.
    """
    return list(STUDIO_ALBUMS.keys())
