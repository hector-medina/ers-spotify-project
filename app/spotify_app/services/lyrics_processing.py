import re
from collections import Counter


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
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(
        r"\s*-\s*(Remaster(?:ed)?|\d{4} Remaster(?:ed)?|Live|Mono|Stereo|Edit|Radio Edit|Acoustic|Demo|Version).*",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\s*(feat\.|ft\.).*$", "", title, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", title).strip()


def clean_artist_name(artist: str) -> str:
    """
    Limpia nombres de artista para la búsqueda.
    """
    if artist is None:
        return ""

    artist = str(artist).strip()
    artist = re.split(r"\s+(feat\.|ft\.|with)\s+", artist, flags=re.IGNORECASE)[0]

    return artist.strip()


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
