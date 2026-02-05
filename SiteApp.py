import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Конфигурация страницы ---
st.set_page_config(page_title="Site Manager", layout="wide")

# --- 2. Умный CSS (адаптация под устройство) ---
st.markdown("""
    <style>
    /* Базовые стили для мобильных карточек */
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
    /* Адаптация фона: темный для узких экранов, светлый для широких */
    @media (max-width: 800px) {
        .stApp { background-color: #0E1117 !important; color: white !important; }
    }
    @media (min-width: 801px) {
        .stApp { background-color: #FFFFFF !important; color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Подключение к Google Sheets ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 4. Авторизация ---
if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Неверный пароль")
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    st.title("🚀 МОНИТОРИНГ")

    # Форма добавления новой задачи (в расширяемом блоке)
    with st.expander("➕ НОВАЯ ЗАДАЧА"):
        with st.form("add_form", clear_on_submit=True):
            f_sec = st.text_input("Раздел")
            f_task = st.text_area("Что сделать?")
            f_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("СОХРАНИТЬ В ОБЛАКО"):
                # Создаем строку с учетом количества колонок в оригинале
                new_line = [f_sec, f_task, f_who, "", f_stat]
                while len(new_line) < len(df.columns):
                    new_line.append("")
                
                new_row = pd.DataFrame([new_line], columns=df.columns)
                updated = pd.concat([df, new_row], ignore
