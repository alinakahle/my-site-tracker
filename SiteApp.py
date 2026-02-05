import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ... (твой блок с паролем остается без изменений) ...

# 1. Ссылка на твою таблицу
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit?gid=0#gid=0"

# 2. Создаем соединение
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Читаем данные. 
# ВНИМАНИЕ: Проверь, чтобы вкладка в Google Таблице называлась именно "Общая" (с большой буквы)
try:
    df = conn.read(spreadsheet=url, worksheet="Общая", ttl=0)
    df = df.dropna(how="all") # Убираем пустые строки
except Exception as e:
    st.error(f"Не удалось найти лист 'Общая'. Проверь название вкладки в Google Таблице!")
    st.stop()

# 4. Вывод таблицы
st.subheader("Список задач из Google")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

# 5. Кнопка сохранения
if st.button("💾 Сохранить изменения в облако"):
    conn.update(spreadsheet=url, worksheet="Общая", data=edited_df)
    st.success("Готово! Данные в Google Таблице обновлены.")
