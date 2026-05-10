"""
Servicio para obtener letras usando lyrics.ovh.

La limpieza de texto y el análisis de métricas viven en lyrics_processing.py para
mantener este módulo centrado en la llamada HTTP.
"""

from urllib.parse import quote

import requests

from spotify_app.services.lyrics_processing import analyze_lyrics, clean_artist_name, clean_song_title


API_BASE_URL = "https://api.lyrics.ovh/v1"


def error_response(error, artist_query="", title_query=""):
    return {
        "status": False,
        "lyrics": "",
        "artist_query": artist_query,
        "title_query": title_query,
        "error": error,
    }


def success_response(lyrics, artist_query, title_query):
    return {
        "status": True,
        "lyrics": lyrics.strip(),
        "artist_query": artist_query,
        "title_query": title_query,
        "error": "",
    }


def fetch_lyrics(title: str, artist: str, timeout: int = 12) -> dict:
    """
    Consulta lyrics.ovh y devuelve un diccionario fácil de consumir desde Streamlit.
    """
    title_query = clean_song_title(title)
    artist_query = clean_artist_name(artist)

    validation_error = validate_query(artist_query, title_query)
    if validation_error:
        return error_response(validation_error, artist_query, title_query)

    url = build_lyrics_url(artist_query, title_query)

    try:
        response = requests.get(url, timeout=timeout)
        return parse_lyrics_response(response, artist_query, title_query)

    except requests.exceptions.Timeout:
        return error_response("Timeout consultando lyrics.ovh.", artist_query, title_query)

    except requests.exceptions.RequestException as exc:
        return error_response(
            f"Error de red consultando lyrics.ovh: {exc}",
            artist_query,
            title_query,
        )


def validate_query(artist_query, title_query):
    if len(title_query) < 2:
        return "El título de la canción es demasiado corto."

    if len(artist_query) < 2:
        return "El nombre del artista es demasiado corto."

    return ""


def build_lyrics_url(artist_query, title_query):
    artist_url = quote(artist_query)
    title_url = quote(title_query)

    return f"{API_BASE_URL}/{artist_url}/{title_url}"


def parse_lyrics_response(response, artist_query, title_query):
    if response.status_code == 200:
        lyrics = response.json().get("lyrics", "")

        if lyrics:
            return success_response(lyrics, artist_query, title_query)

        return error_response(
            "La API respondió correctamente, pero no devolvió letra.",
            artist_query,
            title_query,
        )

    if response.status_code == 404:
        return error_response(
            "No se encontró letra para esta canción.",
            artist_query,
            title_query,
        )

    return error_response(
        f"Error consultando lyrics.ovh. Código HTTP: {response.status_code}",
        artist_query,
        title_query,
    )
