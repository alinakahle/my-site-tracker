import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ... (твой блок с паролем остается без изменений) ...

# 1. Ссылка на твою таблицу
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

# 2. Создаем соединение
conn = st.connection("gsheets", type=GSheetsConnection)

# Читаем данные (добавили обработку ошибок и пробелов)
# --- Подключение к Google Sheets ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Читаем данные. Если не находим "Общая", берем самый первый лист в таблице
    df = conn.read(spreadsheet=url, ttl=0) 
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"Ошибка доступа к Google Таблице. Проверь ссылку в Secrets!")
    st.stop()

# --- Вывод таблицы ---
st.subheader("📋 Актуальные задачи")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

if st.button("💾 Сохранить изменения"):
    # Сохраняем в первый лист
    conn.update(spreadsheet=url, data=edited_df)
    st.success("Облако обновлено!")
# 4. Вывод таблицы
st.subheader("Список задач из Google")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

# 5. Кнопка сохранения
if st.button("💾 Сохранить изменения в облако"):
    conn.update(spreadsheet=url, worksheet="Общая", data=edited_df)
    st.success("Готово! Данные в Google Таблице обновлены.")
