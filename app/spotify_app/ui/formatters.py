import pandas as pd


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
