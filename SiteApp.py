import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки
st.set_page_config(page_title="Site Tracker", layout="wide")

# Укажи здесь точное название своего листа в Google Таблице (внизу на вкладке)
SHEET_NAME = "Общая" 
URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit#gid=0"

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
    # Соединение
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Читаем данные
    df = conn.read(spreadsheet=URL, worksheet=SHEET_NAME, ttl=0).dropna(how="all").fillna("")

    # --- БОКОВАЯ ПАНЕЛЬ ---
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("add_form", clear_on_submit=True):
            f_sec = st.text_input("Раздел сайта")
            f_task = st.text_area("Что нужно сделать?")
            f_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить в список"):
                # Создаем пустую строку по размеру твоей таблицы
                new_row_data = {col: "" for col in df.columns}
                
                # Заполняем только те поля, что ввели (привязка по названиям колонок)
                # Если названия колонок в Google другие, код подстроится под порядок
                col_list = df.columns.tolist()
                if len(col_list) > 1: new_row_data[col_list[1]] = f_sec  # Раздел сайта
                if len(col_list) > 2: new_row_data[col_list[2]] = f_task # Задача
                if len(col_list) > 3: new_row_data[col_list[3]] = f_who  # Ответственный
                if len(col_list) > 7: new_row_data[col_list[7]] = f_stat # Статус
                
                new_row_df = pd.DataFrame([new_row_data])
                updated_df = pd.concat([df, new_row_df], ignore_index=True)
                
                # Сохранение с явным указанием листа
                conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=updated_df)
                st.success("Задача добавлена в таблицу!")
                st.rerun()

    # --- ОСНОВНАЯ ТАБЛИЦА ---
    st.title("📋 Список задач")
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        key="editor"
    )

    if st.button("💾 Сохранить все изменения таблицы"):
        conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=edited_df)
        st.success("Все изменения сохранены!")
