import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Настройки и стиль ---
st.set_page_config(page_title="Site Manager", layout="wide")

st.markdown("""
    <style>
    /* Принудительный светлый стиль */
    .stApp { background-color: #F5F7F9 !important; color: #1E1E1E !important; }
    
    /* Стиль карточки задачи */
    .task-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #007BFF;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-badge {
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        float: right;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Подключение ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- 3. Вход ---
if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
else:
    # --- 4. Загрузка данных ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all")

    st.header("📱 Задачи проекта")

    # Быстрая форма добавления
    with st.expander("➕ Новая задача"):
        with st.form("add_task"):
            sec = st.text_input("Раздел")
            tsk = st.text_area("Описание")
            who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "СЕО", "Офис"])
            stt = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            if st.form_submit_button("Создать"):
                new_data = pd.DataFrame([{"Раздел": sec, "Задача": tsk, "Ответственный": who, "Статус": stt}])
                updated = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=url, data=updated)
                st.success("Добавлено!")
                st.rerun()

    st.divider()

    # --- 5. Отображение задач (Карточки вместо таблицы) ---
    
    # Цвета для статусов
    status_colors = {
        "Запланировано": "#E0E0E0",
        "В работе": "#FFF3CD",
        "На проверке": "#CCE5FF",
        "Готово": "#D4EDDA"
    }

    # Выводим задачи в виде списка карточек
    for index, row in df.iterrows():
        bg_color = status_colors.get(row['Статус'], "#FFFFFF")
        
        # Создаем блок карточки
        with st.container():
            st.markdown(f"""
            <div class="task-card" style="border-left-color: {bg_color}">
                <span class="status-badge" style="background-color: {bg_color};">{row['Статус']}</span>
                <b style="font-size: 14px; color: #666;">{row['Раздел']}</b>< brutal />
                <div style="margin-top: 8px; font-size: 16px;">{row['Задача']}</div>
                <div style="margin-top: 10px; font-size: 13px; color: #555;">👤 {row['Ответственный']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопка быстрой смены статуса прямо под карточкой
            new_stat = st.selectbox(f"Изменить статус для задачи {index}", 
                                    ["Запланировано", "В работе", "На проверке", "Готово"], 
                                    index=["Запланировано", "В работе", "На проверке", "Готово"].index(row['Статус']),
                                    key=f"select_{index}", label_visibility="collapsed")
            
            if new_stat != row['Статус']:
                df.at[index, 'Статус'] = new_stat
                conn.update(spreadsheet=url, data=df)
                st.rerun()
