import streamlit as st


def apply_global_styles():
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

section[data-testid="stSidebar"] div[data-baseweb="select"] span,
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

div[data-testid="stMetricValue"],
div[data-testid="stMarkdownContainer"] {
    color: #111111 !important;
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

.mini-progress-bg,
.feature-bg {
    width: 100%;
    background-color: #E5E7EB;
    border-radius: 999px;
    overflow: hidden;
}

.mini-progress-bg {
    height: 8px;
    margin-top: 0.45rem;
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
    height: 10px;
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
