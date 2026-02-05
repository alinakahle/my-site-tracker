import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. Настройки интерфейса ---
st.set_page_config(page_title="SiteManager", layout="wide", initial_sidebar_state="collapsed")

# Кастомный CSS для «дорогого» вида мобильного приложения
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6 !important; }
    .task-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 8px solid #ddd;
    }
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    /* Крупные кнопки для пальцев */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #007BFF;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Логика данных ---
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Читаем данные и ПЕРЕИМЕНОВЫВАЕМ для кода, чтобы не было ошибок KeyError
    raw_df = conn.read(spreadsheet=url, ttl=0).dropna(how="all")
    
    # Магия: приводим любые названия колонок к нашим стандартам для работы кода
    df = raw_df.copy()
    # Предполагаем порядок: 0-Раздел, 1-Задача, 2-Ответственный, 3-Дедлайн, 4-Статус
    standard_cols = ["Раздел", "Задача", "Кто", "Срок", "Статус"]
    # Переименовываем только те, что есть физически
    mapping = {df.columns[i]: standard_cols[i] for i in range(min(len(df.columns), len(standard_cols)))}
    df = df.rename(columns=mapping)

    st.title("🚀 Site Tasks")

    # --- 3. Форма добавления (Аккордеон) ---
    with st.expander("➕ СОЗДАТЬ НОВУЮ ЗАДАЧУ"):
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            with col1:
                f_sec = st.text_input("Где (Раздел)?")
                f_who = st.selectbox("Кто делает?", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            with col2:
                f_date = st.date_input("Дедлайн")
                f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            f_desc = st.text_area("Что конкретно сделать?")
            
            if st.form_submit_button("ОТПРАВИТЬ В ОБЛАКО"):
                # Собираем строку в оригинальных названиях таблицы
                new_row = pd.DataFrame([[f_sec, f_desc, f_who, str(f_date), f_stat]], columns=raw_df.columns)
                updated = pd.concat([raw_df, new_row], ignore_index=True)
                conn.update(spreadsheet=url, data=updated)
                st.success("Задача улетела в Google!")
                st.rerun()

    st.divider()

    # --- 4. Список задач в виде КАРТОЧЕК ---
    st.subheader("Текущий план")

    colors = {
        "Готово": "#D4EDDA",      # Зеленый
        "В работе": "#FFF3CD",    # Желтый
        "На проверке": "#CCE5FF", # Синий
        "Запланировано": "#E2E3E5" # Серый
    }

    # Идем по задачам с конца (самые новые сверху)
    for index, row in df.iloc[::-1].iterrows():
        status = str(row.get("Статус", "Запланировано"))
        card_color = colors.get(status, "#FFFFFF")
        
        # Рендерим карточку
        st.markdown(f"""
            <div class="task-card" style="border-left-color: {card_color}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6c757d; font-size: 0.8em; font-weight: bold;">📍 {row.get('Раздел', '---')}</span>
                    <span class="status-pill" style="background-color: {card_color};">{status}</span>
                </div>
                <div style="margin: 10px 0; font-size: 1.1em; line-height: 1.4;">{row.get('Задача', 'Без описания')}</div>
                <div style="color: #495057; font-size: 0.9em;">👤 <b>{row.get('Кто', 'Не назначен')}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Кнопка быстрой смены статуса (для мобилки)
        with st.popover(f"Изменить статус"):
            new_s = st.radio("Новый статус:", ["Запланировано", "В работе", "На проверке", "Готово"], 
                             index=["Запланировано", "В работе", "На проверке", "Готово"].index(status) if status in ["Запланировано", "В работе", "На проверке", "Готово"] else 0,
                             key=f"rad_{index}")
            if st.button("Обновить", key=f"btn_{index}"):
                raw_df.iat[index, -1] = new_s # Меняем в последней колонке
