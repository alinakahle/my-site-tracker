import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Настройки страницы и стилей ---
st.set_page_config(page_title="Site Task Tracker", layout="wide", page_icon="📝")

# Добавим немного красоты через CSS (цвета для статусов в таблице)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Ссылка и подключение ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

# --- 3. Защита паролем ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход в систему")
    pwd = st.text_input("Введите пароль компании:", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Доступ запрещен")
else:
    # --- ОСНОВНОЕ ПРИЛОЖЕНИЕ ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Загрузка данных
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df = df.dropna(how="all")
    except:
        st.error("Ошибка подключения к Google Sheets")
        st.stop()

    # --- 4. Боковая панель: Создание новой задачи ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4345/4345573.png", width=100)
        st.header("➕ Новая задача")
        
        with st.form("task_form", clear_on_submit=True):
            new_section = st.text_input("Раздел сайта", placeholder="Напр: Главная")
            new_task = st.text_area("Что нужно сделать?", placeholder="Описание задачи...")
            
            new_who = st.selectbox("Ответственный", 
                                  ["Алина", "Программист", "Дизайнер", "СЕО", "Офис"])
            
            new_status = st.selectbox("Статус", 
                                     ["Запланировано", "В работе", "На проверке", "Готово"])
            
            submit = st.form_submit_button("Создать задачу")
            
            if submit:
                if new_section and new_task:
                    # Создаем новую строку (колонки должны совпадать с Google Таблицей)
                    new_row = pd.DataFrame([{
                        "Раздел сайта": new_section, 
                        "Задача": new_task, 
                        "Ответственный": new_who, 
                        "Статус": new_status
                    }])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.success("Задача добавлена!")
                    st.rerun()
                else:
                    st.warning("Заполните раздел и описание!")

    # --- 5. Основная область: Таблица ---
    st.title("📊 Мониторинг работ")
    
    # Считаем краткую статистику
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего", len(df))
    with col2:
        st.metric("В работе", len(df[df['Статус'] == 'В работе']))
    with col3:
        st.metric("Готово ✅", len(df[df['Статус'] == 'Готово']))

    st.divider()

    # Настраиваем отображение таблицы (цвета и списки)
    st.subheader("Список всех задач")
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="main_editor",
        column_config={
            "Статус": st.column_config.SelectboxColumn(
                "Статус задачи",
                options=["Запланировано", "В работе", "На проверке", "Готово"],
                required=True,
            ),
            "Ответственный": st.column_config.SelectboxColumn(
                "Кто делает",
                options=["Алина", "Программист", "Дизайнер", "СЕО", "Офис"],
                required=True,
            ),
            "Раздел сайта": st.column_config.TextColumn("Раздел", width="medium"),
            "Задача": st.column_config.TextColumn("Описание задачи", width="large"),
        }
    )

    # Кнопка сохранения изменений, сделанных прямо в таблице
    if st.button("💾 Сохранить изменения в таблице"):
        conn.update(spreadsheet=url, data=edited_df)
        st.toast("Данные успешно синхронизированы!")
