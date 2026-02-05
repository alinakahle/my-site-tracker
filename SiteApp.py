import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройка страницы
st.set_page_config(page_title="Премиум Мониторинг Задач", layout="wide")

# 2. Премиум CSS
st.markdown("""
    <style>
    /* Общий фон: темный градиент для премиум вида */
    .stApp {
        background: linear-gradient(to right, #1a1a2e, #16213e);
        color: #e0e0e0; /* Светлый текст */
    }
    /* Заголовки */
    h1, h2, h3, .st-emotion-cache-nahz7x {
        color: #e0e0e0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
    }
    /* Карточки задач */
    .task-card {
        background-color: #2a3950; /* Темно-синий фон */
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3); /* Глубокая тень */
        border-left: 6px solid; /* Цветная полоска слева */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .task-card:hover {
        transform: translateY(-3px); /* Эффект при наведении */
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
    }
    /* Заголовок в карточке */
    .card-title {
        font-size: 1.2em;
        font-weight: 600;
        color: #ffffff; /* Белый текст */
        margin-bottom: 8px;
    }
    /* Детали в карточке */
    .card-detail {
        font-size: 0.9em;
        color: #a0a0a0; /* Более светлый текст для деталей */
        margin-bottom: 4px;
    }
    /* Стиль для статуса */
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
        color: #1a1a2e; /* Темный текст на ярком фоне */
        margin-top: 10px;
        float: right; /* Статус справа */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #2a3950, #16213e); /* Градиент */
        color: #e0e0e0;
        padding: 20px;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3);
    }
    .stSidebar h2 { color: #ffffff !important; }
    .stSidebar .stSelectbox label, .stSidebar .stTextInput label, .stSidebar .stTextArea label {
        color: #a0a0a0 !important;
    }
    .stSidebar .stButton>button {
        background-color: #00bcd4; /* Яркая кнопка */
        color: #1a1a2e;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        transition: background-color 0.2s;
    }
    .stSidebar .stButton>button:hover { background-color: #00acc1; }
    </style>
    """, unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345":
            st.session_state.auth = True
            st.rerun()
else:
    # 3. Загрузка данных
    conn = st.connection("gsheets", type=GSheetsConnection)
    if "df" not in st.session_state:
        try:
            st.session_state.df = conn.read(spreadsheet=URL, ttl=0).dropna(how="all").fillna("")
        except:
            st.error("Ошибка загрузки данных из Google.")
            st.stop()
    df = st.session_state.df

    # --- БОКОВАЯ ПАНЕЛЬ (ПРЕМИУМ) ---
    with st.sidebar:
        st.title("✨ Новая задача")
        st.markdown("---") # Разделитель
        
        with st.form("sidebar_form", clear_on_submit=True):
            f_sec = st.text_input("Раздел сайта")
            f_task = st.text_area("Что сделать?")
            f_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("Добавить задачу"):
                new_row = {col: "" for col in df.columns}
                cols = df.columns.tolist()
                
                # Заполняем по порядку колонок (предполагая, что они в таком порядке)
                if len(cols) > 0: new_row[cols[0]] = f_sec
                if len(cols) > 1: new_row[cols[1]] = f_task
                if len(cols) > 2: new_row[cols[2]] = f_who
                if len(cols) > 4: new_row[cols[4]] = f_stat # Индекс 4 для "Статус"
                
                new_df = pd.DataFrame([new_row])
                st.session_state.df = pd.concat([df, new_df], ignore_index=True)
                
                try:
                    conn.update(spreadsheet=URL, data=st.session_state.df)
                    st.success("Задача добавлена и сохранена!")
                except Exception as e:
                    st.warning(f"Ошибка сохранения в Google: {e}. Задача добавлена только в приложение.")
                st.rerun()

    # --- ГЛАВНЫЙ ЭКРАН (ПРЕМИУМ КАРТОЧКИ) ---
    st.title("🌟 Мониторинг Задач")
    
    # Кнопка обновления из Google
    if st.button("🔄 Обновить из Google"):
        del st.session_state.df
        st.rerun()

    st.markdown("---") # Разделитель
    
    # Цвета для статусов (яркие)
    status_colors = {
        "Готово": "#28a745",       # Зеленый
        "В работе": "#ffc107",     # Желтый
        "На проверке": "#007bff",  # Синий
        "Запланировано": "#6c757d" # Серый
    }

    # Отображение данных в виде карточек
    for index, row in st.session_state.df.iloc[::-1].iterrows(): # Сортируем от новых к старым
        # Убедимся, что индексы существуют
        section = str(row.iloc[0]) if len(row) > 0 else "N/A"
        task = str(row.iloc[1]) if len(row) > 1 else "N/A"
        who = str(row.iloc[2]) if len(row) > 2 else "N/A"
        status_val = str(row.iloc[4]) if len(row) > 4 else "Запланировано" # Предполагаем, что статус 5-я колонка (индекс 4)
        
        # Получаем цвет для статуса
        color = status_colors.get(status_val, "#f8f9fa")

        st.markdown(f"""
            <div class="task-card" style="border-left-color: {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="card-title">{task}</div>
                    <span class="status-badge" style="background-color: {color};">{status_val}</span>
                </div>
                <div class="card-detail">📍 **Раздел:** {section}</div>
                <div class="card-detail">👤 **Ответственный:** {who}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Инструменты для редактирования статуса (внутри popover)
        with st.popover(f"⚙️ Изменить статус"):
            new_s = st.radio("Новый статус:", 
                             ["Запланировано", "В работе", "На проверке", "Готово"], 
                             index=["Запланировано", "В работе", "На проверке", "Готово"].index(status_val) if status_val in status_colors else 0,
                             key=f"popover_status_{index}")
            if st.button("Обновить", key=f"update_btn_{index}"):
                st.session_state.df.iat[index, 4] = new_s # Обновляем 5-ю колонку
                
                try:
                    conn.update(spreadsheet=URL, data=st.session_state.df)
                    st.success("Статус обновлен и сохранен!")
                except Exception as e:
                    st.warning(f"Ошибка сохранения статуса в Google: {e}. Обновлено только в приложении.")
                st.rerun()

    st.markdown("---")
    st.caption("Данные обновляются из Google при входе и сохранении.")
