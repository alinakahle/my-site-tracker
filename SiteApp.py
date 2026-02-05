import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- Настройки страницы ---
st.set_page_config(page_title="Site Task Tracker", layout="wide")

# --- Ссылка на таблицу ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

# --- Защита паролем ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345": # Твой пароль
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Неверный пароль")
else:
    st.title("📱 Трекер задач сайта")

    # Подключение к Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Читаем данные (самый первый лист)
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df = df.dropna(how="all")
    except Exception as e:
        st.error("Ошибка подключения к Google. Проверь настройки Secrets!")
        st.stop()

    # Основная таблица
    st.subheader("Список задач")
    # Добавили ключевое слово key="main_editor", чтобы не было ошибки дубликата
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="main_editor")

    # Кнопка сохранения
    if st.button("💾 Сохранить все изменения"):
        conn.update(spreadsheet=url, data=edited_df)
        st.success("Данные в Google Таблице обновлены!")
