import streamlit as st
import pandas as pd
import plotly.express as px
import html

from studio_albums_10 import STUDIO_ALBUMS
from lyrics_service import fetch_lyrics, analyze_lyrics


DATA_PATH = "data/spotify_studio_tracks_10_artists.csv"


st.set_page_config(
    page_title="Spotify Studio Albums Explorer",
    page_icon="🎧",
    layout="wide",
)


st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(180deg, #FFFFFF 0%, #F6F7F8 45%, #EEF0F2 100%);
    color: #111111;
}

section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5E7EB;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: #111111 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid #1DB954 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #111111 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    color: #111111 !important;
}

h1, h2, h3 {
    color: #111111;
    font-weight: 800;
}

.main-title {
    font-size: 3.2rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
    color: #111111;
}

.subtitle {
    color: #555555;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

.green-pill {
    display: inline-block;
    background-color: #1DB954;
    color: #000000;
    font-weight: 800;
    border-radius: 999px;
    padding: 0.25rem 0.7rem;
    font-size: 0.78rem;
    margin-bottom: 0.8rem;
}

.warning-box {
    background-color: #FFF7D6;
    border: 1px solid #E3B341;
    color: #4A3700;
    padding: 1rem;
    border-radius: 14px;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0px 4px 16px rgba(0, 0, 0, 0.05);
}

div[data-testid="stMetricLabel"] {
    color: #555555 !important;
}

div[data-testid="stMetricValue"] {
    color: #111111 !important;
}

div[data-testid="stMarkdownContainer"] {
    color: #111111;
}

.song-card {
    display: flex;
    align-items: center;
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    margin-bottom: 0.75rem;
    overflow: hidden;
    min-height: 86px;
    box-shadow: 0px 4px 16px rgba(0, 0, 0, 0.04);
}

.song-card:hover {
    background-color: #F8FAFC;
    transition: 0.15s ease-in-out;
}

.song-bar {
    width: 9px;
    align-self: stretch;
}

.song-content {
    padding: 0.85rem 1rem;
    flex: 1;
}

.song-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #111111;
    margin-bottom: 0.2rem;
}

.song-meta {
    color: #555555;
    font-size: 0.9rem;
}

.song-value-box {
    text-align: right;
    padding: 0.85rem 1rem;
    min-width: 170px;
}

.song-value-label {
    color: #555555;
    font-size: 0.8rem;
    margin-bottom: 0.15rem;
}

.song-value {
    color: #111111;
    font-size: 1.5rem;
    font-weight: 900;
}

.song-level {
    font-size: 0.8rem;
    font-weight: 800;
    border-radius: 999px;
    padding: 0.2rem 0.55rem;
    display: inline-block;
    margin-top: 0.35rem;
    color: #000000;
}

.mini-progress-bg {
    width: 100%;
    height: 8px;
    background-color: #E5E7EB;
    border-radius: 999px;
    margin-top: 0.45rem;
    overflow: hidden;
}

.mini-progress-fill {
    height: 8px;
    border-radius: 999px;
}

.feature-row {
    margin-bottom: 0.8rem;
}

.feature-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.92rem;
    color: #111111;
    font-weight: 700;
}

.feature-bg {
    width: 100%;
    height: 10px;
    background-color: #E5E7EB;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 0.25rem;
}

.feature-fill {
    height: 10px;
    border-radius: 999px;
}

.lyrics-placeholder {
    background-color: #F8FAFC;
    border: 1px dashed #CBD5E1;
    border-radius: 16px;
    padding: 1rem;
    color: #334155;
    min-height: 220px;
}

.modal-hero {
    background: linear-gradient(135deg, #1DB954 0%, #E9F8EF 55%, #FFFFFF 100%);
    border-radius: 22px;
    padding: 1.4rem;
    border: 1px solid #D8F3E0;
    margin-bottom: 1rem;
}

.modal-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #111111;
    margin-bottom: 0.25rem;
}

.modal-subtitle {
    color: #333333;
    font-size: 1.05rem;
}

div[role="radiogroup"] label {
    color: #111111 !important;
}

small, .stCaptionContainer {
    color: #555555 !important;
}

/* Intento de modal grande. Si Streamlit cambia el DOM, se ignora sin romper la app. */
div[data-testid="stDialog"] div[role="dialog"] {
    width: 92vw !important;
    max-width: 1280px !important;
}
</style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def get_cached_lyrics(title, artist):
    return fetch_lyrics(title=title, artist=artist)


def format_duration(ms):
    if pd.isna(ms):
        return ""
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def value_color(value):
    if pd.isna(value):
        return "#777777", "Sin dato"

    if value < 0.33:
        return "#E91429", "Bajo"
    if value < 0.66:
        return "#FFD166", "Medio"
    return "#1DB954", "Alto"


def normalized_feature_bar(label, value):
    if pd.isna(value):
        value = 0
        value_text = "-"
    else:
        value = max(0, min(1, float(value)))
        value_text = f"{value:.2f}"

    color, level = value_color(value)
    percentage = round(value * 100, 1)

    bar_html = (
        f'<div class="feature-row">'
        f'<div class="feature-label"><span>{html.escape(label)}</span><span>{value_text} · {level}</span></div>'
        f'<div class="feature-bg">'
        f'<div class="feature-fill" style="width:{percentage}%; background-color:{color};"></div>'
        f'</div>'
        f'</div>'
    )

    st.markdown(bar_html, unsafe_allow_html=True)


def render_song_card(row, selected_feature, selected_feature_label):
    value = row.get(selected_feature, None)
    color, level = value_color(value)

    if pd.isna(value):
        value_text = "-"
        percentage = 0
    else:
        value = max(0, min(1, float(value)))
        value_text = f"{value:.2f}"
        percentage = round(value * 100, 1)

    song_name = html.escape(str(row.get("name", "")))
    album = html.escape(str(row.get("studio_album", "")))
    year = row.get("year", "")
    duration = html.escape(str(row.get("duration", "")))
    feature_label = html.escape(selected_feature_label)
    year_text = "" if pd.isna(year) else str(int(year))

    card_html = (
        f'<div class="song-card">'
        f'<div class="song-bar" style="background-color:{color};"></div>'
        f'<div class="song-content">'
        f'<div class="song-title">{song_name}</div>'
        f'<div class="song-meta">{album} · {year_text} · {duration}</div>'
        f'<div class="mini-progress-bg">'
        f'<div class="mini-progress-fill" style="width:{percentage}%; background-color:{color};"></div>'
        f'</div>'
        f'</div>'
        f'<div class="song-value-box">'
        f'<div class="song-value-label">{feature_label}</div>'
        f'<div class="song-value">{value_text}</div>'
        f'<div class="song-level" style="background-color:{color};">{level}</div>'
        f'</div>'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def render_song_detail_content(song_data, selected_feature, selected_feature_label):
    song_row = pd.Series(song_data)

    song_name = html.escape(str(song_row.get("name", "")))
    album = html.escape(str(song_row.get("studio_album", "")))
    artist = html.escape(str(song_row.get("primary_artist", "")))
    year = song_row.get("year", "")
    track_number = song_row.get("track_number", "")
    duration = html.escape(str(song_row.get("duration", "")))
    explicit = song_row.get("explicit", "")

    year_text = "" if pd.isna(year) else str(int(year))
    track_text = "" if pd.isna(track_number) else str(int(track_number))

    selected_value = song_row.get(selected_feature, None)
    selected_color, selected_level = value_color(selected_value)

    if pd.isna(selected_value):
        selected_value_text = "-"
    else:
        selected_value_text = f"{float(selected_value):.2f}"

    st.markdown(
        f"""
<div class="modal-hero">
    <div class="modal-title">{song_name}</div>
    <div class="modal-subtitle">{artist} · {album} · {year_text}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("Álbum", album)
    m2.metric("Año", year_text)
    m3.metric("Track", track_text)
    m4.metric("Duración", duration)
    m5.metric(selected_feature_label, selected_value_text)

    st.markdown(
        f"""
<div style="margin-top: 0.5rem; margin-bottom: 1rem;">
    <span class="song-level" style="background-color:{selected_color};">{selected_feature_label}: {selected_level}</span>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.25])

    with left:
        st.markdown("### Características musicales")

        normalized_feature_bar("Acousticness", song_row.get("acousticness", None))
        normalized_feature_bar("Danceability", song_row.get("danceability", None))
        normalized_feature_bar("Energy", song_row.get("energy", None))
        normalized_feature_bar("Valence", song_row.get("valence", None))
        normalized_feature_bar("Instrumentalness", song_row.get("instrumentalness", None))
        normalized_feature_bar("Liveness", song_row.get("liveness", None))
        normalized_feature_bar("Speechiness", song_row.get("speechiness", None))

        st.markdown("### Información adicional")

        info_rows = {
            "Tempo": f"{song_row.get('tempo', '-'):.1f} BPM" if pd.notna(song_row.get("tempo", None)) else "-",
            "Loudness": f"{song_row.get('loudness', '-'):.2f} dB" if pd.notna(song_row.get("loudness", None)) else "-",
            "Key": song_row.get("key", "-"),
            "Mode": song_row.get("mode", "-"),
            "Time signature": song_row.get("time_signature", "-"),
            "Explicit": "Sí" if explicit is True or str(explicit).lower() == "true" else "No",
        }

        for key, value in info_rows.items():
            st.write(f"**{key}:** {value}")

    with right:
        st.markdown("### Letra de la canción")

        with st.spinner("Buscando letra en lyrics.ovh..."):
            lyrics_result = get_cached_lyrics(
                title=str(song_row.get("name", "")),
                artist=str(song_row.get("primary_artist", "")),
            )

        if lyrics_result["status"]:
            lyrics = lyrics_result["lyrics"]
            lyrics_stats = analyze_lyrics(lyrics)

            st.success(
                f"Letra encontrada usando: "
                f"{lyrics_result['artist_query']} - {lyrics_result['title_query']}"
            )

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Líneas", lyrics_stats["line_count"])
            k2.metric("Palabras", lyrics_stats["word_count"])
            k3.metric("Únicas", lyrics_stats["unique_words"])
            k4.metric("Diversidad", f"{lyrics_stats['lexical_diversity']:.2f}")

            st.text_area(
                "Letra",
                value=lyrics,
                height=320,
                disabled=True,
                label_visibility="collapsed",
            )

            if lyrics_stats["top_words"]:
                st.markdown("#### Palabras más frecuentes")

                top_words_df = pd.DataFrame(
                    lyrics_stats["top_words"],
                    columns=["Palabra", "Frecuencia"],
                )

                fig_words = px.bar(
                    top_words_df,
                    x="Palabra",
                    y="Frecuencia",
                    template="plotly_white",
                    title="Top palabras de la letra",
                )

                fig_words.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font_color="#111111",
                    margin=dict(l=10, r=10, t=50, b=10),
                )

                st.plotly_chart(fig_words, width="stretch")

        else:
            st.warning(lyrics_result["error"])
            st.markdown(
                f"""
<div class="lyrics-placeholder">
<b>No se pudo obtener la letra automáticamente.</b><br><br>
Consulta intentada:<br>
Artista: <code>{html.escape(lyrics_result.get("artist_query", ""))}</code><br>
Título: <code>{html.escape(lyrics_result.get("title_query", ""))}</code><br><br>
Aquí se mostrará la letra cuando la API devuelva resultados.
</div>
                """,
                unsafe_allow_html=True,
            )


@st.dialog("Detalle de canción", width="large")
def song_detail_dialog(song_data, selected_feature, selected_feature_label):
    render_song_detail_content(song_data, selected_feature, selected_feature_label)

    st.write("")
    if st.button("Cerrar", type="primary"):
        st.rerun()


df = load_data()

numeric_cols = [
    "danceability",
    "energy",
    "acousticness",
    "valence",
    "tempo",
    "duration_ms",
    "year",
    "instrumentalness",
    "liveness",
    "speechiness",
    "loudness",
    "key",
    "mode",
    "time_signature",
    "track_number",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# ---------- Sidebar ----------
st.sidebar.markdown("## 🎧 Spotify Explorer")

artists = sorted(df["primary_artist"].dropna().unique())

selected_artist = st.sidebar.selectbox(
    "Selecciona un artista",
    artists,
    index=0,
)

artist_df = df[df["primary_artist"] == selected_artist].copy()

present_albums = (
    artist_df[["studio_album", "year"]]
    .drop_duplicates()
    .sort_values(["year", "studio_album"])
)

album_options = ["Todos los álbumes"] + present_albums["studio_album"].tolist()

selected_album = st.sidebar.selectbox(
    "Selecciona un álbum",
    album_options,
    index=0,
)

if selected_album != "Todos los álbumes":
    view_df = artist_df[artist_df["studio_album"] == selected_album].copy()
else:
    view_df = artist_df.copy()


feature_options = {
    "Acousticness": "acousticness",
    "Danceability": "danceability",
    "Energy": "energy",
    "Valence": "valence",
}

selected_feature_label = st.sidebar.selectbox(
    "Métrica para comparar álbumes y canciones",
    list(feature_options.keys()),
    index=0,
)

selected_feature = feature_options[selected_feature_label]


# ---------- Header ----------
st.markdown(
    """
<div class="main-title">Spotify Studio Albums Explorer</div>
<div class="subtitle">Análisis visual de canciones pertenecientes a álbumes de estudio.</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(f'<span class="green-pill">{selected_artist}</span>', unsafe_allow_html=True)

st.markdown(f"## {selected_artist}")


# ---------- Métricas ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Canciones en el dataset", len(view_df))
col2.metric("Álbumes encontrados", view_df["studio_album"].nunique())

if not view_df.empty:
    col3.metric("Años", f"{int(view_df['year'].min())} - {int(view_df['year'].max())}")
    col4.metric("Valor medio", f"{view_df[selected_feature].mean():.2f}")
else:
    col3.metric("Años", "-")
    col4.metric("Valor medio", "-")


reference_albums = STUDIO_ALBUMS.get(selected_artist, [])
found_albums = present_albums["studio_album"].tolist()
missing_albums = [album for album in reference_albums if album not in found_albums]

if missing_albums:
    st.markdown(
        f"""
<div class="warning-box">
<b>Nota sobre el dataset:</b><br>
La discografía de referencia contiene {len(reference_albums)} álbumes de estudio,
pero en el CSV reducido solo se han encontrado {len(found_albums)} para este artista.
Por eso el contador muestra únicamente los álbumes presentes en los datos disponibles.
</div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Álbumes ----------
st.markdown("## Álbumes encontrados en el dataset")

if present_albums.empty:
    st.warning("No se encontraron álbumes para este artista en el dataset.")
else:
    album_rows = list(present_albums.itertuples(index=False))

    for i in range(0, len(album_rows), 3):
        cols = st.columns(3)

        for col, row in zip(cols, album_rows[i:i + 3]):
            album_name = row.studio_album
            year = row.year

            album_df = artist_df[artist_df["studio_album"] == album_name]

            tracks = len(album_df)
            avg_selected = album_df[selected_feature].mean()

            with col:
                with st.container(border=True):
                    st.markdown(f"### {album_name}")
                    st.caption(f"{int(year) if pd.notna(year) else 'Sin año'}")
                    st.write(f"**{tracks} canciones**")
                    st.write(f"{selected_feature_label}: `{avg_selected:.2f}`")


with st.expander("Ver discografía de estudio usada como referencia"):
    st.write(reference_albums)

    if missing_albums:
        st.markdown("**Álbumes de referencia que no aparecen en el dataset reducido:**")
        st.write(missing_albums)


st.divider()


# ---------- Sección 1: Exploración musical ----------
st.markdown("## Exploración musical")
st.markdown("### Valence vs Acousticness")

if view_df.empty:
    st.warning("No hay datos para mostrar.")
else:
    fig = px.scatter(
        view_df,
        x="valence",
        y="acousticness",
        color="studio_album",
        size="duration_ms",
        hover_name="name",
        hover_data={
            "studio_album": True,
            "year": True,
            "energy": ":.2f",
            "danceability": ":.2f",
            "tempo": ":.1f",
            "duration_ms": False,
        },
        title=f"Mapa musical de {selected_artist}",
        template="plotly_white",
    )

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#111111",
        legend_title_text="Álbum",
    )

    st.plotly_chart(fig, width="stretch")


st.divider()


# ---------- Sección 2: Comparación por álbum ----------
st.markdown("## Comparación por álbum")
st.markdown(f"### {selected_feature_label} media por álbum")

if view_df.empty:
    st.warning("No hay datos para mostrar.")
else:
    album_summary = (
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

    fig_bar = px.bar(
        album_summary,
        x="studio_album",
        y=selected_feature,
        hover_data=["tracks", "year"],
        title=f"{selected_feature_label} media por álbum",
        template="plotly_white",
    )

    fig_bar.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#111111",
        xaxis_title="Álbum",
        yaxis_title=selected_feature_label,
    )

    st.plotly_chart(fig_bar, width="stretch")

    summary_to_show = album_summary[
        [
            "studio_album",
            "year",
            "tracks",
            selected_feature,
        ]
    ].rename(
        columns={
            "studio_album": "Álbum",
            "year": "Año",
            "tracks": "Canciones",
            selected_feature: selected_feature_label,
        }
    )

    st.dataframe(
        summary_to_show,
        width="stretch",
        hide_index=True,
    )


st.divider()


# ---------- Sección 3: Canciones ----------
st.markdown("## Canciones")
st.markdown(f"### Canciones ordenadas por {selected_feature_label}")

if view_df.empty:
    st.warning("No hay canciones para mostrar.")
else:
    table_df = view_df.copy()

    if "duration_ms" in table_df.columns:
        table_df["duration"] = table_df["duration_ms"].apply(format_duration)

    sort_option = st.radio(
        "Ordenar canciones",
        [
            "Orden original del álbum",
            f"{selected_feature_label} alto a bajo",
            f"{selected_feature_label} bajo a alto",
        ],
        horizontal=True,
    )

    if sort_option == f"{selected_feature_label} alto a bajo":
        table_df = table_df.sort_values(selected_feature, ascending=False)
    elif sort_option == f"{selected_feature_label} bajo a alto":
        table_df = table_df.sort_values(selected_feature, ascending=True)
    else:
        table_df = table_df.sort_values(["year", "studio_album", "track_number", "name"])

    st.caption("Rojo: < 0.33 · Amarillo: 0.33 - 0.66 · Verde: ≥ 0.66")

    for _, row in table_df.iterrows():
        song_id = str(row["id"])

        c1, c2 = st.columns([8, 1.4])

        with c1:
            render_song_card(row, selected_feature, selected_feature_label)

        with c2:
            st.write("")
            st.write("")
            if st.button("Ver detalle", key=f"detail_{song_id}", width="stretch"):
                song_data = row.to_dict()
                song_detail_dialog(song_data, selected_feature, selected_feature_label)
