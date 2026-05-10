import streamlit as st

st.set_page_config(
    page_title="Spotify Studio Albums Explorer",
    page_icon="🎧",
    layout="wide",
)

from spotify_app.config.settings import ALL_ALBUMS_LABEL, FEATURE_OPTIONS, SCATTER_X_OPTIONS
from spotify_app.data.service import (
    add_duration_column,
    build_album_summary,
    filter_album,
    get_present_albums,
    load_data,
    sort_tracks,
)
from spotify_app.domain.studio_albums import STUDIO_ALBUMS
from spotify_app.ui.components import (
    render_album_cards,
    render_dataset_note,
    render_header,
    render_reference_discography,
    render_song_list,
    render_summary_metrics,
)
from spotify_app.ui.formatters import format_duration
from spotify_app.ui.styles import apply_global_styles
from spotify_app.visualization.charts import make_album_comparison, make_music_map

apply_global_styles()


df = load_data()


# ---------- Sidebar ----------
st.sidebar.markdown("## 🎧 Spotify Explorer")

artists = sorted(df["primary_artist"].dropna().unique())
selected_artist = st.sidebar.selectbox(
    "Selecciona un artista",
    artists,
    index=0,
    key="selected_artist",
)

artist_df = df[df["primary_artist"] == selected_artist].copy()
present_albums = get_present_albums(artist_df)
album_options = [ALL_ALBUMS_LABEL] + present_albums["studio_album"].tolist()

selected_album = st.sidebar.selectbox(
    "Selecciona un álbum",
    album_options,
    index=0,
    key="selected_album",
)
selected_feature_label = st.sidebar.selectbox(
    "Métrica para comparar álbumes y canciones",
    list(FEATURE_OPTIONS.keys()),
    index=0,
    key="selected_feature",
)
selected_feature = FEATURE_OPTIONS[selected_feature_label]
view_df = filter_album(artist_df, selected_album, ALL_ALBUMS_LABEL)
view_albums = get_present_albums(view_df)


# ---------- Header y métricas ----------
render_header(selected_artist)
render_summary_metrics(view_df, selected_feature)

reference_albums = STUDIO_ALBUMS.get(selected_artist, [])
found_albums = present_albums["studio_album"].tolist()
missing_albums = [album for album in reference_albums if album not in found_albums]

if missing_albums:
    render_dataset_note(reference_albums, found_albums)


# ---------- Álbumes ----------
render_album_cards(view_albums, view_df, selected_feature, selected_feature_label)
render_reference_discography(reference_albums, missing_albums)

st.divider()


# ---------- Sección 1: Exploración musical ----------
st.markdown("## Exploración musical")

scatter_x_options = {
    label: column
    for label, column in SCATTER_X_OPTIONS.items()
    if column != selected_feature
}
default_x_index = (
    list(scatter_x_options.keys()).index("Valence")
    if "Valence" in scatter_x_options
    else 0
)
selected_x_label = st.selectbox(
    "Variable del eje X",
    list(scatter_x_options.keys()),
    index=default_x_index,
    key="scatter_x_feature",
)
selected_x_feature = scatter_x_options[selected_x_label]

st.markdown(f"### {selected_x_label} vs {selected_feature_label}")

if view_df.empty:
    st.warning("No hay datos para mostrar.")
else:
    st.plotly_chart(
        make_music_map(
            view_df,
            selected_artist,
            selected_x_feature,
            selected_x_label,
            selected_feature,
            selected_feature_label,
        ),
        width="stretch",
        config={"responsive": True},
    )

st.divider()


# ---------- Sección 2: Comparación por álbum ----------
st.markdown("## Comparación por álbum")
st.markdown(f"### {selected_feature_label} media por álbum")

if view_df.empty:
    st.warning("No hay datos para mostrar.")
else:
    album_summary = build_album_summary(view_df)
    st.plotly_chart(
        make_album_comparison(album_summary, selected_feature, selected_feature_label),
        width="stretch",
        config={"responsive": True},
    )

    summary_to_show = album_summary[
        ["studio_album", "year", "tracks", selected_feature]
    ].rename(
        columns={
            "studio_album": "Álbum",
            "year": "Año",
            "tracks": "Canciones",
            selected_feature: selected_feature_label,
        }
    )

    st.dataframe(summary_to_show, width="stretch", hide_index=True)

st.divider()


# ---------- Sección 3: Canciones ----------
st.markdown("## Canciones")
st.markdown(f"### Canciones ordenadas por {selected_feature_label}")

if view_df.empty:
    st.warning("No hay canciones para mostrar.")
else:
    table_df = add_duration_column(view_df, format_duration)

    sort_option = st.radio(
        "Ordenar canciones",
        [
            "Orden original del álbum",
            f"{selected_feature_label} alto a bajo",
            f"{selected_feature_label} bajo a alto",
        ],
        horizontal=True,
    )

    table_df = sort_tracks(table_df, sort_option, selected_feature, selected_feature_label)

    st.caption("Rojo: < 0.33 · Amarillo: 0.33 - 0.66 · Verde: ≥ 0.66")
    render_song_list(table_df, selected_feature, selected_feature_label)
