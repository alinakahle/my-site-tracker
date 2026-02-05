import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Системные настройки (Apple High Quality)
st.set_page_config(page_title="Task Flow 2026", layout="wide")

# 2. Подключение к твоим Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Конфигурация ролей и иконок
STAFF_CONFIG = {
    "Программист": "👨‍💻",
    "Дизайнер": "🎨",
    "SEO": "🔍",
    "Алина": "👩‍💼"
}

# 4. CSS (Senior UI/UX: Теневые боксы, Hover-эффекты, Bento-стиль)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; }
    
    /* Основной контейнер карточки */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #E0E6ED !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 20px rgba(0,0,0,0.08) !important;
    }

    /* Типографика */
    .task-title { font-size: 1.5rem; font-weight: 800; color: #1A1C1E; margin-bottom: 8px; }
    .meta-row { display: flex; align-items: center; gap: 15px; color: #64748B; font-size: 0.95rem; margin-bottom: 20px; }
    .role-badge { background: #F1F5F9; padding: 2px 8px; border-radius: 6px; font-weight: 600; }
    
    /* Прогресс-бар и чип времени */
    .progress-container { background: #E2E8F0; border-radius: 10px; height: 8px; flex-grow: 1; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; }
    .days-chip { padding: 4px 12px; border-radius: 100px; font-weight: 700; font-size: 0.85rem; }

    /* Цвета времени */
    .t-neutral { background: #F1F5F9; color: #475569; } .b-neutral { background: #94A3B8; }
    .t-yellow { background: #FEF3C7; color: #92400E; } .b-yellow { background: #F59E0B; }
    .t-orange { background: #FFEDD5; color: #9A3412; } .b-orange { background: #F97316; }
    .t-red { background: #FEE2E2; color: #991B1B; } .b-red { background: #EF4444; }

    /* Скрытие стандартных меток селекторов */
    .stSelectbox label { display: none !important; }
</style>
""", unsafe_allow_html=True)

def get_time_styles(days):
    if days <= 7: return "t-neutral", "b-neutral"
    elif days <= 14: return "t-yellow", "b-yellow"
    elif days <= 21: return "t-orange", "b-orange"
    return "t-red", "b-red"

try:
    # Чтение реальных данных
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🚀 Управление Task Flow 2026")

    # Сайдбар с фильтрами
    with st.sidebar:
        st.header("⚙️ Фильтры")
        f_assignee = st.selectbox("Кто делает?", ["Все"] + sorted(df['Ответственный'].unique().tolist()))
        f_status = st.selectbox("Статус", ["Все", "В работе", "Запланировано", "Готово"])
        f_urgent = st.checkbox("🔥 Только горящие (22+ дней)")

    # Фильтрация
    filtered_df = df.copy()
    if f_assignee != "Все": filtered_df = filtered_df[filtered_df['Ответственный'] == f_assignee]
    if f_status != "Все": filtered_df = filtered_df[filtered_df['Статус'] == f_status]

    # Рендер карточек
    status_options = ["В работе", "Запланировано", "Готово"]
    
    for idx, row in filtered_df.iterrows():
        # Считаем дни
        try:
            start_date = datetime.strptime(str(row['Начало']).strip(), "%d.%m.%Y").date()
            days = (date.today() - start_date).days
        except: days = 0
        
        if f_urgent and days < 22: continue

        chip_cls, bar_cls = get_time_styles(days)
        emoji = STAFF_CONFIG.get(row['Ответственный'], "👤")
        
        # Рендер бокса
        with st.container(border=True):
            # Строка 1: Название и Статус
            col_t1, col_t2 = st.columns([0.7, 0.3])
            with col_t1:
                st.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
            with col_t2:
                new_status = st.selectbox("Статус", status_options, 
                                          index=status_options.index(row['Статус']), 
                                          key=f"st_{idx}")
                if new_status != row['Статус']:
                    df.at[idx, 'Статус'] = new_status
                    conn.update(data=df)
                    st.rerun()

            # Строка 2: Исполнитель и Раздел
            st.markdown(f"""
                <div class="meta-row">
                    <span>{emoji} <b>{row['Ответственный']}</b></span>
                    <span class="role-badge">Раздел: {row['Раздел сайта']}</span>
                </div>
            """, unsafe_allow_html=True)

            # Строка 3: Дни и Прогресс-бар
            p_val = min((days / 30) * 100, 100)
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="days-chip {chip_cls}">⏱ {days if days <= 30 else '30+'} дн.</div>
                    <div class="progress-container">
                        <div class="progress-fill {bar_cls}" style="width: {p_val}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")
