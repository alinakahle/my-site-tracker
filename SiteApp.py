import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Системные настройки
st.set_page_config(page_title="Pro Task Manager 2026", layout="wide")

# 2. Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Конфигурация команды
STAFF_CONFIG = {
    "Программист": "👨‍💻",
    "Дизайнер": "🎨",
    "SEO": "🔍",
    "Алина": "👩‍💼",
    "Все": "🌐"
}

# 4. Мощный CSS для UX и читаемости
st.markdown("""
<style>
    /* Фон приложения - глубокий черный */
    .stApp {
        background-color: #000000 !important;
    }

    /* СТИЛЬ КАРТОЧКИ (БОКСА) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1c1c1e !important; /* Цвет как в iOS dark mode */
        border: 1px solid #3a3a3c !important; /* Четкая граница */
        border-radius: 20px !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }

    /* Название задачи - Максимальный контраст */
    .task-title-main {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin-bottom: 15px !important;
        line-height: 1.2 !important;
    }

    /* Бейдж ответственного - чтобы сразу бросался в глаза */
    .person-pill {
        background: #2c2c2e;
        padding: 6px 14px;
        border-radius: 12px;
        border: 1px solid #48484a;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }

    /* Информационные метки */
    .label-text {
        color: #8e8e93; /* Цвет Apple Secondary Text */
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .value-text {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 500;
    }

    /* Бейдж времени */
    .time-badge {
        background: rgba(255, 69, 58, 0.15);
        color: #ff453a;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* Тюнинг вкладок и кнопок */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background: #1c1c1e !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        color: #8e8e93 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            d = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            d = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - d).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.markdown("# 🔘 Центр управления")

    # Фильтр команды (Segmented)
    staff_options = list(STAFF_CONFIG.keys())
    sel_staff = st.segmented_control(
        "Фильтр по команде:", 
        options=staff_options,
        format_func=lambda x: f"{STAFF_CONFIG[x]} {x}",
        default="Все"
    )

    tabs = st.tabs(["🔥 В работе", "⏳ План", "✅ Готово"])
    st_list = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_st = st_list[i]
        with tab:
            tasks = df[df['Статус'] == curr_st]
            if sel_staff != "Все":
                tasks = tasks[tasks['Ответственный'] == sel_staff]

            if tasks.empty:
                st.caption("Задач нет")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    person = row['Ответственный']
                    emoji = STAFF_CONFIG.get(person, "👤")
                    
                    # --- ГЛАВНЫЙ БОКС ЗАДАЧИ ---
                    with st.container(border=True):
                        # 1 ряд: Заголовок
                        st.markdown(f'<div class="task-title-main">{row["Задача"]}</div>', unsafe_allow_html=True)
                        
                        # 2 ряд: Основная информация
                        c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                        
                        with c1:
                            st.markdown('<p class="label-text">Ответственный</p>', unsafe_allow_html=True)
                            st.markdown(f'<div class="person-pill">{emoji} {person}</div>', unsafe_allow_html=True)
                        
                        with c2:
                            st.markdown('<p class="label-text">Раздел сайта</p>', unsafe_allow_html=True)
                            st.markdown(f'<p class="value-text">📍 {row["Раздел сайта"]}</p>', unsafe_allow_html=True)
                        
                        with c3:
                            st.markdown('<p class="label-text">Тайминг</p>', unsafe_allow_html=True)
                            if curr_st == "В работе":
                                st.markdown(f'<span class="time-badge">🔥 {days} дн. в работе</span>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<p class="value-text">📅 {row["Начало"]}</p>', unsafe_allow_html=True)

                        # 3 ряд: Кнопка смены статуса (выделена чертой)
                        st.markdown("<div style='margin-top:20px; border-top:1px solid #3a3a3c; padding-top:15px;'></div>", unsafe_allow_html=True)
                        
                        ctrl_col1, ctrl_col2 = st.columns([0.7, 0.3])
                        with ctrl_col2:
                            new_val = st.selectbox(
                                "Сменить статус:", st_list, 
                                index=st_list.index(curr_st),
                                key=f"sel_{idx}",
                                label_visibility="collapsed"
                            )
                            if new_val != curr_st:
                                df.at[idx, 'Статус'] = new_val
                                conn.update(data=df)
                                st.rerun()

except Exception as e:
    st.error(f"Ошибка связи: {e}")

# Сайдбар для новых задач
with st.sidebar:
    st.header("✚ Новая задача")
    with st.form("add_form"):
        nt_task = st.text_input("Название задачи")
        nt_sec = st.text_input("Раздел")
        nt_who = st.selectbox("Кто делает?", [k for k in STAFF_CONFIG.keys() if k != "Все"])
        if st.form_submit_button("Создать в Плане"):
            new_r = {
                "Раздел сайта": nt_sec, "Задача": nt_task, "Ответственный": nt_who, 
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_r])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
