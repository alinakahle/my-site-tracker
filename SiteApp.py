import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Настройки страницы ---
st.set_page_config(page_title="Site Manager", layout="wide")

# --- 2. Детектор мобильной версии и Стили ---
# Streamlit сам адаптирует layout, но мы добавим специфичный CSS
st.markdown("""
    <style>
    /* Общие стили для карточек (будут видны только на мобилках) */
    .task-card {
        background-color: #1A1C24;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #30363D;
        border-left: 10px solid #ddd;
    }
    .task-text { color: #FFFFFF; font-size: 18px; font-weight: 700; margin: 10px 0; }
    .section-title { color: #8B949E; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .status-badge {
        padding: 4px 12px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 900;
        float: right;
        color: #000;
    }
    /* Стили для десктопной таблицы, чтобы она не была темной, если не нужно */
    @media (min-width: 800px) {
        .stApp { background-color: #FFFFFF !important; color: black !important; }
    }
    @media (max-width: 799px) {
        .stApp { background-color: #0E1117 !important; color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Подключение к данным ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    # Определяем тип устройства через ширину (условно)
    # В Streamlit нет прямого детектора, но мы можем использовать колонки
    # Если колонки сжимаются слишком сильно, мы поймем, что это мобилка
    
    st.title("🚀 МОНИТОРИНГ")

    # Форма добавления (видна везде)
    with st.expander("➕ НОВАЯ ЗАДА
