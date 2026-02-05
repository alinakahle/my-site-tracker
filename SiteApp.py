import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Настройка для мобильных и светлая тема ---
st.set_page_config(page_title="Site App", layout="wide", initial_sidebar_state="collapsed")

# Вставляем CSS, чтобы исправить отображение на телефонах
st.markdown("""
    <style>
    /* Принудительный светлый фон и темный текст */
    .stApp { background-color: white !important; color: #1E1E1E !important; }
    h1, h2, h3, p { color: #1E1E1E !important; }
    
    /* Стилизация карточек статистики */
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #007BFF !important; }
    
    /* Делаем кнопки крупнее для телефона */
    .stButton>button {
        width: 100%;
        height: 3em;
        border-radius: 10px;
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border: none;
    }
    
    /* Убираем лишние отступы сверху на мобилках */
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Данные ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 3. Вход (крупные поля для телефона) ---
if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти в систему"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Ошибка")
else:
    # --- 4. Рабочая область ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all")

    st.header("📱 Трекер задач")

    # Компактная статистика
    c1, c2 = st.columns(2)
    c1.metric("Всего", len(df))
    c2.metric("Готово", len(df[df['Статус'] == 'Готово']))

    # --- 5. Добавление задачи через раскрывающийся блок (удобно для мобилок) ---
    with st.expander("➕ ДОБАВИТЬ НОВУЮ ЗАДАЧУ"):
        with st.form("mobile_form", clear_on_submit=True):
            resurs = st.text_input("Раздел")
            task_desc = st.text_area("Что сделать?")
            who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "СЕО", "Офис"])
            stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("СОЗДАТЬ"):
                if resurs and task_desc:
                    # Важно: названия колонок ниже должны быть ТАКИМИ ЖЕ как в твоей таблице
                    new_data = pd.DataFrame([{"Раздел": resurs, "Задача": task_desc, "Ответственный": who, "Статус": stat}])
                    updated = pd.concat([df, new_data], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated)
                    st.success("Добавлено!")
                    st.rerun()

    st.divider()

    # --- 6. Таблица с цветовой индикацией ---
    st.subheader("📝 Список")

    # Функция для раскраски строк (только для просмотра)
    def color_status(val):
        color = '#ffffff'
        if val == 'Готово': color = '#d4edda' # светло-зеленый
        elif val == 'В работе': color = '#fff3cd' # желтый
        elif val == 'На проверке': color = '#cce5ff' # голубой
        return f'background-color: {color}'

    # Используем data_editor для возможности правок
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="mobile_editor",
        column_config={
            "Статус": st.column_config.SelectboxColumn(options=["Запланировано", "В работе", "На проверке", "Готово"]),
            "Ответственный": st.column_config.SelectboxColumn(options=["Алина", "Программист", "Дизайнер", "СЕО", "Офис"])
        }
    )

    if st.button("💾 СОХРАНИТЬ ИЗМЕНЕНИЯ"):
        conn.update(spreadsheet=url, data=edited_df)
        st.toast("Обновлено в Google!")
