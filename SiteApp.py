import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки интерфейса
st.set_page_config(page_title="Site Tracker", layout="wide")

# Название листа теперь на латинице
SHEET_NAME = "Tasks" 
URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit#gid=0"

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- Вход ---
if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Неверный пароль")
else:
    # --- Работа с данными ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Читаем данные (указываем наш новый латинский лист)
    df = conn.read(spreadsheet=URL, worksheet=SHEET_NAME, ttl=0).dropna(how="all").fillna("")

    # --- Боковая панель для добавления ---
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("add_form", clear_on_submit=True):
            f_sec = st.text_input("Раздел сайта")
            f_task = st.text_area("Что сделать?")
            f_who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить"):
                # Создаем строку, привязываясь к колонкам твоей таблицы
                new_row = pd.DataFrame([{
                    df.columns[0]: f_sec,
                    df.columns[1]: f_task,
                    df.columns[2]: f_who,
                    df.columns[4]: f_stat # Обычно статус идет 5-й колонкой (индекс 4)
                }])
                
                # Объединяем и сохраняем
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=updated_df)
                st.success("Добавлено!")
                st.rerun()

    # --- Основная таблица ---
    st.title("📋 Мониторинг задач")
    
    # Редактор таблицы (как ты и просила — исходный вид)
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        key="main_editor"
    )

    if st.button("💾 Сохранить все изменения"):
        conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=edited_df)
        st.success("Синхронизировано с Google!")
