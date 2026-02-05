import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# Настройка страницы
st.set_page_config(page_title="Site Manager Liquid", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Улучшенный Liquid Glass Дизайн
st.markdown("""
<style>
    /* Глубокий темный фон */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f1f5f9;
    }

    /* Монолитная карточка Liquid Glass */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px) saturate(180%);
        -webkit-backdrop-filter: blur(15px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }

    /* Заголовок теперь всегда внутри и белый */
    .task-title-inner {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 15px;
        line-height: 1.3;
    }

    /* Нижняя панель внутри карточки */
    .task-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .meta-info {
        display: flex;
        gap: 20px;
        color: #cbd5e1;
        font-size: 1rem;
    }

    /* Стиль для счетчика дней */
    .fire-days {
        color: #fb7185;
        font-weight: 800;
        text-shadow: 0 0 10px rgba(251, 113, 133, 0.3);
    }

    /* Исправление отображения Popover кнопок */
    div[data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Убираем стандартные белые рамки вокруг элементов Streamlit внутри карточки */
    .stVerticalBlock { gap: 0rem; }
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
    
    st.markdown("# 🚀 Project Dashboard")
    
    all_staff = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    tabs = st.tabs(["🔥 В работе", "⏳ План", "💎 Готово"])
    statuses = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = statuses[i]
        with tab:
            selected_person = st.segmented_control(
                "Фильтр по команде:", options=all_staff, default="Все", key=f"filter_{curr_status}"
            )
            
            tasks = df[df['Статус'] == curr_status]
            if selected_person != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_person]
            
            if tasks.empty:
                st.write("Пусто")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    
                    # Генерируем HTML карточки
                    # Мы открываем DIV здесь, а закрываем в конце блока
                    st.markdown(f"""
                    <div class="glass-card">
                        <div class="task-title-inner">{row['Задача']}</div>
                    """, unsafe_allow_html=True)
                    
                    # Строка с мета-инфо и кнопкой
                    # Используем колонки Streamlit внутри, чтобы кнопка работала
                    m_col1, m_col2 = st.columns([0.8, 0.2])
                    
                    with m_col1:
                        time_label = f'<span class="fire-days">🔥 {days} дн.</span>' if curr_status == "В работе" else f"📅 {row['Начало']}"
                        st.markdown(f"""
                            <div class="meta-info">
                                <span>👤 <b>{row['Ответственный']}</b></span>
                                <span>📍 {row['Раздел сайта']}</span>
                                <span>{time_label}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with m_col2:
                        with st.popover(curr_status, use_container_width=True):
                            new_st = st.radio("Сменить статус:", statuses, 
                                            index=statuses.index(curr_status),
                                            key=f"move_{idx}")
                            if new_st != curr_status:
                                df.at[idx, 'Статус'] = new_st
                                conn.update(data=df)
                                st.rerun()
                    
                    # Закрываем основной контейнер карточки
                    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")

# Сайдбар
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("add_form", clear_on_submit=True):
        f_sec = st.text_input("Раздел")
        f_task = st.text_area("Задача")
        f_who = st.selectbox("Кто", all_staff[1:])
        if st.form_submit_button("Создать"):
            new = {"Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                   "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"}
            upd = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
