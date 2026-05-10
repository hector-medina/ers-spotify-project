import plotly.express as px


def apply_light_layout(fig, **layout):
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#111111",
        **layout,
    )
    return fig


def make_music_map(view_df, selected_artist, x_feature, x_feature_label, y_feature, y_feature_label):
    fig = px.scatter(
        view_df,
        x=x_feature,
        y=y_feature,
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
        labels={
            x_feature: x_feature_label,
            y_feature: y_feature_label,
            "studio_album": "Álbum",
        },
    )

    return apply_light_layout(
        fig,
        legend_title_text="Álbum",
        xaxis_title=x_feature_label,
        yaxis_title=y_feature_label,
    )


def make_album_comparison(album_summary, selected_feature, selected_feature_label):
    fig = px.bar(
        album_summary,
        x="studio_album",
        y=selected_feature,
        hover_data=["tracks", "year"],
        title=f"{selected_feature_label} media por álbum",
        template="plotly_white",
    )

    return apply_light_layout(
        fig,
        xaxis_title="Álbum",
        yaxis_title=selected_feature_label,
    )


def make_top_words_chart(top_words_df):
    fig = px.bar(
        top_words_df,
        x="Palabra",
        y="Frecuencia",
        template="plotly_white",
        title="Top palabras de la letra",
    )

    return apply_light_layout(fig, margin=dict(l=10, r=10, t=50, b=10))
