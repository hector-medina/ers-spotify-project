# ers-spotify-project

## Ejecutar la app

```bash
streamlit run app/app.py
```

## Preparar datos

```bash
python data/prepare_data.py
```

## Estructura

- `app/app.py`: entrypoint de Streamlit.
- `app/spotify_app/config`: configuración y constantes.
- `app/spotify_app/data`: carga y preparación de datos para la app.
- `app/spotify_app/domain`: datos de dominio, como la discografía de referencia.
- `app/spotify_app/services`: integración con APIs y lógica de letras.
- `app/spotify_app/ui`: componentes, estilos y formateadores visuales.
- `app/spotify_app/visualization`: gráficos Plotly.
- `data/tracks_features.csv`: dataset original.
- `data/spotify_studio_tracks_10_artists.csv`: dataset reducido que consume la app.
- `data/prepare_data.py`: script para regenerar el dataset reducido.
