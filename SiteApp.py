import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки страницы
st.set_page_config(page_title="Site Task Tracker", layout="wide")

# 2. Ссылка на таблицу
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit#gid=0"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345":
            st.session_state.auth = True
            st.rerun()
else:
    # Соединение с Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    # --- БОКОВАЯ ПАНЕЛЬ ДЛЯ ВВОДА ---
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("sidebar_form", clear_on_submit=True):
            new_sec = st.text_input("Раздел сайта")
            new_task = st.text_area("Что нужно сделать?")
            new_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            new_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить в список"):
                # Создаем новую строку
                new_data = [new_sec, new_task, new_who, "", new_stat]
                # Выравниваем количество колонок
                while len(new_data) < len(df.columns):
                    new_data.append("")
                
                new_row = pd.DataFrame([new_data], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Сохраняем и обновляем
                conn.update(spreadsheet=url, data=df)
                st.success("Задача добавлена!")
                st.rerun()

    # --- ОСНОВНАЯ ЧАСТЬ (ТАБЛИЦА) ---
    st.title("📋 Список задач из Google")

    # Редактор таблицы
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        key="main_table"
    )

    # Кнопка сохранения изменений в самой таблице
    if st.button("💾 Сохранить изменения в таблице"):
        conn.update(spreadsheet=url, data=edited_df)
        st.success("Изменения синхронизированы с Google!")

    st.info("💡 Таблица справа, а форма добавления — в выезжающем меню слева (Sidebar).")
