"""
lyrics_service.py

Servicio pequeño para obtener letras usando lyrics.ovh.

Basado en la idea del ZIP lyrics_finder:
- consulta https://api.lyrics.ovh/v1/{artist}/{title}
- maneja errores
- limpia títulos problemáticos
- devuelve un diccionario fácil de usar desde Streamlit
"""

import re
from collections import Counter
from urllib.parse import quote

import requests


API_BASE_URL = "https://api.lyrics.ovh/v1"


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "while",
    "is", "are", "was", "were", "be", "been", "being",
    "i", "you", "he", "she", "it", "we", "they",
    "me", "my", "mine", "your", "yours", "his", "her", "hers", "our", "ours",
    "their", "theirs", "this", "that", "these", "those",
    "to", "of", "in", "on", "at", "for", "from", "by", "with", "about",
    "as", "into", "like", "through", "after", "over", "between", "out",
    "up", "down", "off", "again", "further",
    "do", "does", "did", "doing",
    "have", "has", "had", "having",
    "not", "no", "nor", "so", "too", "very",
    "can", "will", "just", "don", "should", "now",
    "im", "i'm", "youre", "you're", "dont", "don't", "cant", "can't",
    "oh", "ooh", "ah", "yeah", "yea", "la", "na",
}


def clean_song_title(title: str) -> str:
    """
    Limpia títulos de Spotify para mejorar la búsqueda de letras.

    Ejemplos:
        "Creep - 2021 Remaster" -> "Creep"
        "Song (Live at Wembley)" -> "Song"
        "Track - Remastered" -> "Track"
    """
    if title is None:
        return ""

    title = str(title).strip()

    # Quitar contenido entre paréntesis/corchetes.
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\[.*?\]", "", title)

    # Quitar sufijos típicos de versiones.
    title = re.sub(
        r"\s*-\s*(Remaster(?:ed)?|\\d{4} Remaster(?:ed)?|Live|Mono|Stereo|Edit|Radio Edit|Acoustic|Demo|Version).*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Quitar feat.
    title = re.sub(r"\s*(feat\\.|ft\\.).*$", "", title, flags=re.IGNORECASE)

    title = re.sub(r"\s+", " ", title).strip()

    return title


def clean_artist_name(artist: str) -> str:
    """
    Limpia nombres de artista para la búsqueda.
    """
    if artist is None:
        return ""

    artist = str(artist).strip()

    # Si hubiera colaboraciones, quedarnos con el principal.
    artist = re.split(r"\s+(feat\\.|ft\\.|with)\s+", artist, flags=re.IGNORECASE)[0]

    return artist.strip()


def fetch_lyrics(title: str, artist: str, timeout: int = 12) -> dict:
    """
    Consulta lyrics.ovh.

    Returns:
        {
            "status": True/False,
            "lyrics": "...",
            "artist_query": "...",
            "title_query": "...",
            "error": "..."
        }
    """
    title_query = clean_song_title(title)
    artist_query = clean_artist_name(artist)

    if len(title_query) < 2:
        return {
            "status": False,
            "lyrics": "",
            "artist_query": artist_query,
            "title_query": title_query,
            "error": "El título de la canción es demasiado corto.",
        }

    if len(artist_query) < 2:
        return {
            "status": False,
            "lyrics": "",
            "artist_query": artist_query,
            "title_query": title_query,
            "error": "El nombre del artista es demasiado corto.",
        }

    artist_url = quote(artist_query)
    title_url = quote(title_query)

    url = f"{API_BASE_URL}/{artist_url}/{title_url}"

    try:
        response = requests.get(url, timeout=timeout)

        if response.status_code == 200:
            data = response.json()
            lyrics = data.get("lyrics", "")

            if lyrics:
                return {
                    "status": True,
                    "lyrics": lyrics.strip(),
                    "artist_query": artist_query,
                    "title_query": title_query,
                    "error": "",
                }

            return {
                "status": False,
                "lyrics": "",
                "artist_query": artist_query,
                "title_query": title_query,
                "error": "La API respondió correctamente, pero no devolvió letra.",
            }

        if response.status_code == 404:
            return {
                "status": False,
                "lyrics": "",
                "artist_query": artist_query,
                "title_query": title_query,
                "error": "No se encontró letra para esta canción.",
            }

        return {
            "status": False,
            "lyrics": "",
            "artist_query": artist_query,
            "title_query": title_query,
            "error": f"Error consultando lyrics.ovh. Código HTTP: {response.status_code}",
        }

    except requests.exceptions.Timeout:
        return {
            "status": False,
            "lyrics": "",
            "artist_query": artist_query,
            "title_query": title_query,
            "error": "Timeout consultando lyrics.ovh.",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": False,
            "lyrics": "",
            "artist_query": artist_query,
            "title_query": title_query,
            "error": f"Error de red consultando lyrics.ovh: {exc}",
        }


def analyze_lyrics(lyrics: str) -> dict:
    """
    Calcula métricas simples de una letra.
    """
    if not lyrics:
        return {
            "line_count": 0,
            "word_count": 0,
            "unique_words": 0,
            "lexical_diversity": 0,
            "top_words": [],
        }

    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]

    words = re.findall(r"[a-zA-Z']+", lyrics.lower())
    words_clean = [
        word.strip("'")
        for word in words
        if len(word.strip("'")) > 2 and word.strip("'") not in STOPWORDS
    ]

    counter = Counter(words_clean)

    word_count = len(words)
    unique_words = len(set(words))
    lexical_diversity = unique_words / word_count if word_count else 0

    return {
        "line_count": len(lines),
        "word_count": word_count,
        "unique_words": unique_words,
        "lexical_diversity": lexical_diversity,
        "top_words": counter.most_common(10),
    }
