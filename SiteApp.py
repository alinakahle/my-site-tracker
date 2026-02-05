import streamlit as st
import pandas as pd
import os
from datetime import date

# Настройки
st.set_page_config(page_title="Task Tracker", layout="wide")

# Проверка пароля
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        if pwd == "12345": # ТВОЙ ПАРОЛЬ
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Неверно")
else:
    # Основная программа
    st.title("📱 Трекер задач сайта")
    
    FILE = "my_tasks.csv"
    df = pd.read_csv(FILE) if os.path.exists(FILE) else pd.DataFrame(columns=["Раздел", "Задача", "Ответственный", "Дедлайн", "Статус"])

    # Добавление задачи
    with st.sidebar:
        st.header("➕ Новая задача")
        with st.form("add"):
            section = st.text_input("Раздел")
            task = st.text_area("Что сделать?")
            who = st.selectbox("Кто", ["Программист", "Дизайнер", "Алина", "Леша"])
            due = st.date_input("Дедлайн")
            status = st.selectbox("Статус", ["Запланировано", "В работе", "Готово"])
            if st.form_submit_button("Добавить"):
                new_data = pd.DataFrame([[section, task, who, due, status]], columns=df.columns)
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(FILE, index=False)
                st.rerun()

    # Таблица
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Сохранить изменения"):
        edited_df.to_csv(FILE, index=False)
        st.success("Сохранено!")
