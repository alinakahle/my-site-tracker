import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- Настройки ---
st.set_page_config(page_title="Site Tasks", layout="wide")

# CSS для красивых карточек
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6 !important; }
    .task-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 6px solid #ddd;
    }
    .status-badge {
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        float: right;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Читаем данные
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all")
    
    # Очистка данных от "NaN" (чтобы не было надписей nan в карточках)
    df = df.fillna("")

    st.title("🚀 Site Tasks")

    # Форма добавления
    with st.expander("➕ НОВАЯ ЗАДАЧА"):
        with st.form("add"):
            c1, c2 = st.columns(2)
            # Берем названия колонок прямо из твоей таблицы
            cols = df.columns.tolist()
            f_sec = st.text_input(cols[0] if len(cols)>0 else "Раздел")
            f_task = st.text_area(cols[1] if len(cols)>1 else "Задача")
            f_who = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("СОЗДАТЬ"):
                new_row = pd.DataFrame([[f_sec, f_task, f_who, "", f_stat]], columns=df.columns)
                updated = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=url, data=updated)
                st.success("Добавлено!")
                st.rerun()

    st.subheader("📋 Список задач")

    colors = {"Готово": "#D4EDDA", "В работе": "#FFF3CD", "На проверке": "#CCE5FF", "Запланировано": "#E2E3E5"}

    # Отображение карточек
    for index, row in df.iloc[::-1].iterrows():
        # Берем данные по порядку колонок: 0 - Раздел, 1 - Задача, 2 - Кто, 4 - Статус
        # Используем .iloc для надежности, чтобы не зависеть от имен
        r_sec = row.iloc[0] if len(row) > 0 else ""
        r_task = row.iloc[1] if len(row) > 1 else ""
        r_who = row.iloc[2] if len(row) > 2 else ""
        r_stat = row.iloc[4] if len(row) > 4 else "Запланировано"
        
        card_color = colors.get(r_stat, "#FFFFFF")

        st.markdown(f"""
            <div class="task-card" style="border-left-color: {card_color}">
                <span class="status-badge" style="background-color: {card_color};">{r_stat}</span>
                <div style="color: #888; font-size: 12px; font-weight: bold;">📍 {r_sec}</div>
                <div style="margin: 8px 0; font-size: 15px; color: #333;">{r_task}</div>
                <div style="font-size: 13px; color: #555;">👤 {r_who}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.popover("Изменить статус"):
            new_s = st.radio("Статус:", ["Запланировано", "В работе", "На проверке", "Готово"], 
                             index=["Запланировано", "В работе", "На проверке", "Готово"].index(r_stat) if r_stat in ["Запланировано", "В работе", "На проверке", "Готово"] else 0,
                             key=f"st_{index}")
            if st.button("Обновить", key=f"btn_{index}"):
                # Обновляем именно в той колонке, где лежит статус (обычно 4-я или 5-я)
                df.iat[index, 4] = new_s 
                conn.update(spreadsheet=url, data=df)
                st.rerun()
