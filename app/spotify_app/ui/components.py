import html

import pandas as pd
import streamlit as st

from spotify_app.services.lyrics_service import analyze_lyrics, fetch_lyrics
from spotify_app.ui.formatters import value_color
from spotify_app.visualization.charts import make_top_words_chart


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def get_cached_lyrics(title, artist):
    return fetch_lyrics(title=title, artist=artist)


def render_header(selected_artist):
    st.markdown(
        """
<div class="main-title">Spotify Studio Albums Explorer</div>
<div class="subtitle">Análisis visual de canciones pertenecientes a álbumes de estudio.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<span class="green-pill">{html.escape(selected_artist)}</span>', unsafe_allow_html=True)
    st.markdown(f"## {selected_artist}")


def render_dataset_note(reference_albums, found_albums):
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


def render_summary_metrics(view_df, selected_feature):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Canciones en el dataset", len(view_df))
    col2.metric("Álbumes encontrados", view_df["studio_album"].nunique())

    if view_df.empty:
        col3.metric("Años", "-")
        col4.metric("Valor medio", "-")
        return

    col3.metric("Años", f"{int(view_df['year'].min())} - {int(view_df['year'].max())}")
    col4.metric("Valor medio", f"{view_df[selected_feature].mean():.2f}")


def render_album_cards(present_albums, artist_df, selected_feature, selected_feature_label):
    st.markdown("## Álbumes encontrados en el dataset")

    if present_albums.empty:
        st.warning("No se encontraron álbumes para este artista en el dataset.")
        return

    album_rows = list(present_albums.itertuples(index=False))

    for i in range(0, len(album_rows), 3):
        cols = st.columns(3)

        for col, row in zip(cols, album_rows[i:i + 3]):
            album_df = artist_df[artist_df["studio_album"] == row.studio_album]
            avg_selected = album_df[selected_feature].mean()

            with col:
                with st.container(border=True):
                    st.markdown(f"### {row.studio_album}")
                    st.caption(f"{int(row.year) if pd.notna(row.year) else 'Sin año'}")
                    st.write(f"**{len(album_df)} canciones**")
                    st.write(f"{selected_feature_label}: `{avg_selected:.2f}`")


def render_reference_discography(reference_albums, missing_albums):
    with st.expander("Ver discografía de estudio usada como referencia"):
        st.write(reference_albums)

        if missing_albums:
            st.markdown("**Álbumes de referencia que no aparecen en el dataset reducido:**")
            st.write(missing_albums)


def normalized_feature_bar(label, value):
    if pd.isna(value):
        normalized_value = 0
        value_text = "-"
    else:
        normalized_value = max(0, min(1, float(value)))
        value_text = f"{normalized_value:.2f}"

    color, level = value_color(normalized_value)
    percentage = round(normalized_value * 100, 1)

    st.markdown(
        (
            f'<div class="feature-row">'
            f'<div class="feature-label"><span>{html.escape(label)}</span><span>{value_text} &middot; {level}</span></div>'
            f'<div class="feature-bg">'
            f'<div class="feature-fill" style="width:{percentage}%; background-color:{color};"></div>'
            f'</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


def render_song_card(row, selected_feature, selected_feature_label):
    value = row.get(selected_feature, None)
    color, level = value_color(value)

    if pd.isna(value):
        value_text = "-"
        percentage = 0
    else:
        normalized_value = max(0, min(1, float(value)))
        value_text = f"{normalized_value:.2f}"
        percentage = round(normalized_value * 100, 1)

    song_name = html.escape(str(row.get("name", "")))
    album = html.escape(str(row.get("studio_album", "")))
    year = row.get("year", "")
    duration = html.escape(str(row.get("duration", "")))
    feature_label = html.escape(selected_feature_label)
    year_text = "" if pd.isna(year) else str(int(year))

    st.markdown(
        (
            f'<div class="song-card">'
            f'<div class="song-bar" style="background-color:{color};"></div>'
            f'<div class="song-content">'
            f'<div class="song-title">{song_name}</div>'
            f'<div class="song-meta">{album} &middot; {year_text} &middot; {duration}</div>'
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
        ),
        unsafe_allow_html=True,
    )


def render_song_list(table_df, selected_feature, selected_feature_label):
    for _, row in table_df.iterrows():
        song_id = str(row["id"])
        c1, c2 = st.columns([8, 1.4])

        with c1:
            render_song_card(row, selected_feature, selected_feature_label)

        with c2:
            st.write("")
            st.write("")
            if st.button("Ver detalle", key=f"detail_{song_id}", width="stretch"):
                song_detail_dialog(row.to_dict(), selected_feature, selected_feature_label)


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
    selected_value_text = "-" if pd.isna(selected_value) else f"{float(selected_value):.2f}"

    st.markdown(
        f"""
<div class="modal-hero">
    <div class="modal-title">{song_name}</div>
    <div class="modal-subtitle">{artist} &middot; {album} &middot; {year_text}</div>
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
        render_song_features(song_row)

    with right:
        render_song_lyrics(song_row)


def render_song_features(song_row):
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
        "Explicit": "Sí" if explicit_value(song_row.get("explicit", "")) else "No",
    }

    for key, value in info_rows.items():
        st.write(f"**{key}:** {value}")


def explicit_value(value):
    return value is True or str(value).lower() == "true"


def render_song_lyrics(song_row):
    st.markdown("### Letra de la canción")

    with st.spinner("Buscando letra en lyrics.ovh..."):
        lyrics_result = get_cached_lyrics(
            title=str(song_row.get("name", "")),
            artist=str(song_row.get("primary_artist", "")),
        )

    if not lyrics_result["status"]:
        render_missing_lyrics(lyrics_result)
        return

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
        top_words_df = pd.DataFrame(lyrics_stats["top_words"], columns=["Palabra", "Frecuencia"])
        st.plotly_chart(make_top_words_chart(top_words_df), width="stretch")


def render_missing_lyrics(lyrics_result):
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
