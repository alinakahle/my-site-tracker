import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Настройка страницы
st.set_page_config(page_title="Site Manager Liquid", layout="wide")

# 2. Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Дизайн: Dark Liquid Glass
st.markdown("""
<style>
    /* Основной фон - темный глубокий градиент */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f1f5f9;
    }

    /* Эффект Liquid Glass для карточек */
    .task-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    
    .task-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Заголовок задачи */
    .task-title {
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
        line-height: 1.2;
    }

    /* Мета-данные (футер карточки) */
    .task-footer {
        display: flex;
        gap: 20px;
        font-size: 0.95rem;
        color: #94a3b8;
        align-items: center;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 15px;
    }

    /* Кастомная кнопка статуса (Popover) */
    div[data-testid="stPopover"] > button {
        background: rgba(59, 130, 246, 0.1) !important;
        color: #60a5fa !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: 0.3s !important;
    }
    
    div[data-testid="stPopover"] > button:hover {
        background: rgba(59, 130, 246, 0.2) !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
    }

    /* Счетчики и акценты */
    .days-badge {
        color: #fb7185;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* Тюнинг вкладок */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 10px 10px 0 0;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            start_dt = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            start_dt = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - start_dt).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.markdown("# 🌌 Project Dashboard")
    
    all_staff = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    tabs = st.tabs(["🔥 В работе", "⏳ План", "💎 Готово"])
    statuses = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = statuses[i]
        with tab:
            selected_person = st.segmented_control(
                "Фильтр по команде:", options=all_staff, default="Все", key=f"f_{curr_status}"
            )
            
            st.write("") 
            
            tasks = df[df['Статус'] == curr_status]
            if selected_person != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_person]
            
            if tasks.empty:
                st.info("Задач нет")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    
                    # Сама карточка
                    with st.container():
                        # Исправленная верстка: заголовок и кнопка в одной линии без перекосов
                        col_content, col_btn = st.columns([0.82, 0.18])
                        
                        with col_content:
                            # Начало карточки через markdown
                            st.markdown(f"""
                            <div class="task-card">
                                <div class="task-title">{row['Задача']}</div>
                            """, unsafe_allow_html=True)
                        
                        with col_btn:
                            # Кнопка смены статуса (стеклянный поповер)
                            with st.popover(curr_status, use_container_width=True):
                                st.write("💫 Этап задачи")
                                new_st = st.radio("Сменить на:", statuses, 
                                                index=statuses.index(curr_status),
                                                key=f"m_{idx}")
                                if new_st != curr_status:
                                    df.at[idx, 'Статус'] = new_st
                                    conn.update(data=df)
                                    st.rerun()

                        # Мета-данные задачи внизу
                        time_display = f'<div class="days-badge">🔥 {days} дн.</div>' if curr_status == "В работе" else f"📅 {row['Начало']}"
                        
                        st.markdown(f"""
                                <div class="task-footer">
                                    <div style="color:#ffffff">👤 <b>{row['Ответственный']}</b></div>
                                    <div>📍 {row['Раздел сайта']}</div>
                                    <div>{time_display}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Data error: {e}")

# Сайдбар для добавления задач
with st.sidebar:
    st.markdown("### 🛠 Новая задача")
    with st.form("new_task"):
        f_sec = st.text_input("Раздел")
        f_task = st.text_area("Суть задачи")
        f_who = st.selectbox("Кто", all_staff[1:])
        if st.form_submit_button("Создать ✨"):
            new = {"Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                   "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"}
            upd = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
