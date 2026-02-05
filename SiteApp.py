import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки
st.set_page_config(page_title="Site Tracker", layout="wide")

# Прямая ссылка на таблицу (убрали хвостик gid, чтобы он не мешал)
URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"
SHEET_NAME = "Tasks"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345":
            st.session_state.auth = True
            st.rerun()
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Пытаемся прочитать данные
    try:
        # Читаем именно лист Tasks
        df = conn.read(spreadsheet=URL, worksheet=SHEET_NAME, ttl=0).dropna(how="all").fillna("")
    except Exception as e:
        st.error(f"Ошибка: Лист '{SHEET_NAME}' не найден. Проверьте название вкладки в Google Таблице!")
        st.stop()

    # --- Боковая панель ---
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("add_task", clear_on_submit=True):
            f_sec = st.text_input("Раздел")
            f_task = st.text_area("Задача")
            f_who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить"):
                # Создаем новую строку, сопоставляя с колонками в Google
                new_row_dict = {df.columns[i]: val for i, val in enumerate([f_sec, f_task, f_who, "", f_stat]) if i < len(df.columns)}
                new_row_df = pd.DataFrame([new_row_dict])
                
                updated_df = pd.concat([df, new_row_df], ignore_index=True)
                conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=updated_df)
                st.success("Задача добавлена!")
                st.rerun()

    # --- Основной экран ---
    st.title("📋 Мониторинг задач")
    
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor")

    if st.button("💾 Сохранить всё"):
        conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=edited_df)
        st.success("Сохранено!")
