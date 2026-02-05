import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройка страницы
st.set_page_config(page_title="Site Manager Pro", layout="wide")

# 2. Премиум Канбан CSS
st.markdown("""
    <style>
    .stApp { background-color: #0f1116; color: #ffffff; }
    
    /* Стили колонок канбана */
    .kanban-column {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 15px;
        min-height: 80vh;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .column-header {
        text-align: center;
        font-weight: 800;
        font-size: 1.1em;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid;
    }
    
    /* Стили карточек */
    .task-card {
        background: #1c1e26;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 5px solid;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: 0.3s;
    }
    .task-card:hover { transform: scale(1.02); }
    
    .task-title { font-weight: 700; color: #fff; margin-bottom: 8px; font-size: 1em; }
    .task-meta { color: #8b949e; font-size: 0.85em; }
    .task-user { color: #58a6ff; font-weight: 600; font-size: 0.85em; margin-top: 10px; }

    /* Боковая панель */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stButton>button { background: #238636; color: white; border: none; width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"
SHEET_NAME = "Tasks"

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
            st.session_state.df = conn.read(spreadsheet=URL, worksheet=SHEET_NAME, ttl=0).dropna(how="all").fillna("")
        except:
            st.error("Ошибка загрузки данных. Проверьте лист 'Tasks'")
            st.stop()
    
    df = st.session_state.df

    # --- БОКОВАЯ ПАНЕЛЬ (ДОБАВЛЕНИЕ) ---
    with st.sidebar:
        st.title("➕ Создать задачу")
        with st.form("new_task", clear_on_submit=True):
            f_sec = st.text_input("Раздел")
            f_task = st.text_area("Описание")
            f_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Этап", ["Запланировано", "В работе", "Готово"])
            
            if st.form_submit_button("ДОБАВИТЬ"):
                new_row = {df.columns[0]: f_sec, df.columns[1]: f_task, df.columns[2]: f_who, df.columns[4]: f_stat}
                st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=st.session_state.df)
                st.rerun()

    # --- КАНБАН ДОСКА ---
    st.title("🎯 Kanban Board")
    
    # Кнопка синхронизации
    if st.button("🔄 Обновить из Google"):
        del st.session_state.df
        st.rerun()

    # Разделяем на 3 колонки
    col1, col2, col3 = st.columns(3)

    stages = [
        {"name": "Запланировано", "color": "#6c757d", "column": col1},
        {"name": "В работе", "color": "#ffc107", "column": col2},
        {"name": "Готово", "color": "#28a745", "column": col3}
    ]

    for stage in stages:
        with stage["column"]:
            # Фильтруем задачи для текущей колонки
            tasks = df[df.iloc[:, 4] == stage["name"]]
            
            st.markdown(f"""
                <div class="column-header" style="border-color: {stage['color']}; color: {stage['color']};">
                    {stage['name'].upper()} ({len(tasks)})
                </div>
                """, unsafe_allow_html=True)
            
            for idx, row in tasks.iterrows():
                # Отрисовка карточки
                st.markdown(f"""
                    <div class="task-card" style="border-left-color: {stage['color']};">
                        <div class="task-title">{row.iloc[1]}</div>
                        <div class="task-meta">📍 {row.iloc[0]}</div>
                        <div class="task-user">👤 {row.iloc[2]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Кнопка смены статуса (компактная)
                with st.popover("Сменить этап", key=f"pop_{idx}"):
                    new_s = st.radio("Куда переместить?", ["Запланировано", "В работе", "Готово"], 
                                     index=["Запланировано", "В работе", "Готово"].index(stage["name"]),
                                     key=f"rad_{idx}")
                    if st.button("Переместить", key=f"btn_{idx}"):
                        st.session_state.df.iat[idx, 4] = new_s
                        conn.update(spreadsheet=URL, worksheet=SHEET_NAME, data=st.session_state.df)
                        st.rerun()

    st.divider()
    st.caption("Site Manager Pro v2.0 | Синхронизировано с Google Sheets")
