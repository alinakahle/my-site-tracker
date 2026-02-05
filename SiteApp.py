import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- Настройки страницы ---
st.set_page_config(page_title="Site Manager", layout="wide")

# Улучшенный контрастный CSS
st.markdown("""
    <style>
    /* Фон всей страницы - спокойный серый для контраста */
    .stApp { background-color: #E5E7EB !important; }
    
    /* Карточка: белая, с четкой тенью и жирным шрифтом */
    .task-card {
        background: white;
        padding: 18px;
        border-radius: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Более глубокая тень */
        border-left: 10px solid #ddd;
    }
    
    /* Текст внутри карточки */
    .section-title { color: #555; font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
    .task-text { color: #000000; font-size: 17px; font-weight: 600; margin: 8px 0; line-height: 1.3; }
    .who-text { color: #333; font-size: 14px; font-weight: 500; }
    
    /* Статусы - делаем их очень яркими */
    .status-badge {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 900;
        float: right;
        color: #000; /* Черный текст на ярком фоне для читаемости */
    }
    
    /* Делаем заголовки Streamlit черными */
    h1, h2, h3 { color: #000000 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Введите пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345": 
            st.session_state.auth = True
            st.rerun()
else:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    st.title("🚀 ЗАДАЧИ ПО САЙТУ")

    # Форма стала более заметной
    with st.expander("➕ ДОБАВИТЬ НОВУЮ ЗАДАЧУ"):
        with st.form("add_task_form"):
            cols_names = df.columns.tolist()
            f_sec = st.text_input("Раздел сайта (например, Главная)")
            f_task = st.text_area("Что нужно сделать?")
            f_who = st.selectbox("Исполнитель", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_stat = st.selectbox("Текущий статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            
            if st.form_submit_button("СОХРАНИТЬ В ТАБЛИЦУ"):
                new_row = pd.DataFrame([[f_sec, f_task, f_who, "", f_stat]], columns=df.columns)
                updated = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=url, data=updated)
                st.success("Сохранено!")
                st.rerun()

    st.markdown("---")

    # Цвета стали более насыщенными (не пастельными)
    colors = {
        "Готово": "#2ECC71",       # Насыщенный зеленый
        "В работе": "#F1C40F",     # Яркий желтый
        "На проверке": "#3498DB",  # Яркий синий
        "Запланировано": "#BDC3C7" # Глубокий серый
    }

    # Вывод карточек
    for index, row in df.iloc[::-1].iterrows():
        r_sec = row.iloc[0]
        r_task = row.iloc[1]
        r_who = row.iloc[2]
        r_stat = row.iloc[4] if len(row) > 4 else "Запланировано"
        
        card_color = colors.get(r_stat, "#FFFFFF")

        st.markdown(f"""
            <div class="task-card" style="border-left-color: {card_color}">
                <span class="status-badge" style="background-color: {card_color};">
                    {r_stat}
                </span>
                <div class="section-title">📍 {r_sec}</div>
                <div class="task-text">{r_task}</div>
                <div class="who-text">👤 <b>{r_who}</b></div>
