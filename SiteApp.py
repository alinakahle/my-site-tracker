import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки страницы
st.set_page_config(page_title="Site Tracker", layout="wide")

# Прямая ссылка на таблицу
URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

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
    
    # Пытаемся прочитать ПЕРВЫЙ доступный лист (без указания имени)
    try:
        df = conn.read(spreadsheet=URL, ttl=0).dropna(how="all").fillna("")
    except Exception as e:
        st.error(f"Не удалось подключиться: {e}")
        st.stop()

    # --- БОКОВОЕ МЕНЮ (SideBar) ---
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("add_form", clear_on_submit=True):
            f_sec = st.text_input("Раздел сайта")
            f_task = st.text_area("Что сделать?")
            f_who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить в таблицу"):
                # Создаем пустую строку с колонками как в таблице
                new_data = {col: "" for col in df.columns}
                cols = df.columns.tolist()
                
                # Заполняем данными по порядку колонок (как на твоем скриншоте)
                if len(cols) > 1: new_data[cols[1]] = f_sec
                if len(cols) > 2: new_data[cols[2]] = f_task
                if len(cols) > 3: new_data[cols[3]] = f_who
                if len(cols) > 8: new_data[cols[8]] = f_stat
                
                new_row_df = pd.DataFrame([new_data])
                updated_df = pd.concat([df, new_row_df], ignore_index=True)
                
                # Сохраняем (тоже без указания имени листа, в первый попавшийся)
                conn.update(spreadsheet=URL, data=updated_df)
                st.success("Задача добавлена!")
                st.rerun()

    # --- ГЛАВНЫЙ ЭКРАН (Таблица) ---
    st.title("📋 Список задач")
    
    # Тот самый редактор таблицы, который тебе нравился
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        key="main_editor"
    )

    if st.button("💾 Сохранить все изменения"):
        conn.update(spreadsheet=URL, data=edited_df)
        st.success("Данные успешно синхронизированы!")
