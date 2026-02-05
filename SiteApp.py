import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки страницы (делаем таблицу на весь экран)
st.set_page_config(page_title="Site Task Tracker", layout="wide")

# 2. Ссылка на твою таблицу
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit#gid=0"

# 3. Проверка пароля
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
            st.error("Неверный пароль")
else:
    # --- ОСНОВНОЙ ИНТЕРФЕЙС ---
    st.title("📱 Список задач")

    # Подключение к Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Читаем данные (самый первый лист)
    try:
        # Читаем таблицу, убираем пустые строки
        df = conn.read(spreadsheet=url, ttl=0)
        df = df.dropna(how="all")
    except Exception as e:
        st.error("Ошибка подключения к Google Таблице. Проверь права доступа (должен быть 'Редактор' для всех).")
        st.stop()

    # Отображаем таблицу как редактор
    # Здесь можно менять текст, выбирать статусы и добавлять строки
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        key="main_table_editor"
    )

    # Кнопка сохранения
    if st.button("💾 Сохранить изменения в Google Таблицу"):
        try:
            conn.update(spreadsheet=url, data=edited_df)
            st.success("Готово! Все изменения сохранены в облако.")
        except Exception as e:
            st.error(f"Не удалось сохранить: {e}")

    # Инструкция для мобильной версии
    st.info("💡 Если вы с телефона: таблицу можно двигать вправо-влево пальцем.")
    
