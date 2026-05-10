import streamlit as st
import pandas as pd
import plotly.express as px
import html

from studio_albums_10 import STUDIO_ALBUMS


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
    background: linear-gradient(180deg, #191414 0%, #121212 45%, #000000 100%);
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 1px solid #242424;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
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
    color: #FFFFFF;
    font-weight: 800;
}

.main-title {
    font-size: 3.2rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
    color: #FFFFFF;
}

.subtitle {
    color: #B3B3B3;
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
    background-color: #332500;
    border: 1px solid #b8860b;
    color: #f5d57a;
    padding: 1rem;
    border-radius: 14px;
    margin-top: 1rem;
    margin-bottom: 1rem;
}

div[data-testid="stMetric"] {
    background-color: #181818;
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid #282828;
}

div[data-testid="stMetricLabel"] {
    color: #B3B3B3 !important;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

div[data-testid="stTabs"] button {
    color: #FFFFFF !important;
}

.song-card {
    display: flex;
    align-items: center;
    background-color: #181818;
    border: 1px solid #282828;
    border-radius: 16px;
    margin-bottom: 0.75rem;
    overflow: hidden;
    min-height: 86px;
}

.song-card:hover {
    background-color: #202020;
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
    color: #FFFFFF;
    margin-bottom: 0.2rem;
}

.song-meta {
    color: #B3B3B3;
    font-size: 0.9rem;
}

.song-value-box {
    text-align: right;
    padding: 0.85rem 1rem;
    min-width: 170px;
}

.song-value-label {
    color: #B3B3B3;
    font-size: 0.8rem;
    margin-bottom: 0.15rem;
}

.song-value {
    color: #FFFFFF;
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
    background-color: #333333;
    border-radius: 999px;
    margin-top: 0.45rem;
    overflow: hidden;
}

.mini-progress-fill {
    height: 8px;
    border-radius: 999px;
}
</style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


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

    # Importante:
    # Este HTML se genera sin indentación inicial.
    # Si se indenta con 4 espacios, Streamlit/Markdown lo puede mostrar como código.
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


df = load_data()

numeric_cols = [
    "danceability",
    "energy",
    "acousticness",
    "valence",
    "tempo",
    "duration_ms",
    "year",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


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


st.markdown(
    """
<div class="main-title">Spotify Studio Albums Explorer</div>
<div class="subtitle">Análisis visual de canciones pertenecientes a álbumes de estudio.</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(f'<span class="green-pill">{selected_artist}</span>', unsafe_allow_html=True)

st.markdown(f"## {selected_artist}")


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


tab1, tab2, tab3 = st.tabs(
    [
        "Exploración musical",
        "Comparación por álbum",
        "Canciones",
    ]
)


with tab1:
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
            template="plotly_dark",
        )

        fig.update_layout(
            paper_bgcolor="#121212",
            plot_bgcolor="#121212",
            font_color="#FFFFFF",
            legend_title_text="Álbum",
        )

        st.plotly_chart(fig, width="stretch")


with tab2:
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
            template="plotly_dark",
        )

        fig_bar.update_layout(
            paper_bgcolor="#121212",
            plot_bgcolor="#121212",
            font_color="#FFFFFF",
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


with tab3:
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
            render_song_card(row, selected_feature, selected_feature_label)
