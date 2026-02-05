import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Системные настройки (Apple High Quality)
st.set_page_config(page_title="Task Core 2026", layout="wide")

# 2. Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Маппинг ответственных (Персонализация)
STAFF_CONFIG = {
    "Программист": {"emoji": "👨‍💻", "color": "#60a5fa"},
    "Дизайнер": {"emoji": "🎨", "color": "#f472b6"},
    "SEO": {"emoji": "🚀", "color": "#fbbf24"},
    "Алина": {"emoji": "👩‍🎨", "color": "#a78bfa"},
    "Все": {"emoji": "🌍", "color": "#ffffff"}
}

# 4. Премиальный CSS (Bento UI)
st.markdown("""
<style>
    /* Глубокий темный фон (OLED Black style) */
    .stApp {
        background-color: #000000;
        color: #e2e8f0;
    }

    /* Стилизация РОДНОГО контейнера под Бенто-бокс */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 24px !important;
        padding: 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 16px !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #444444 !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }

    /* Типографика Apple Style */
    .task-heading {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 12px;
    }

    .meta-label {
        color: #888888;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .meta-value {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Тюнинг вкладок и контролов */
    div[data-testid="stSegmentedControl"] button {
        border-radius: 12px !important;
        background: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #222222 !important;
    }
    
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Индикаторы времени */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-urgent { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    .badge-normal { background: rgba(255, 255, 255, 0.05); color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

def get_days_diff(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            d = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            d = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - d).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.markdown("### 🔘 Task Core Control")
    
    # Горизонтальный фильтр (Segmented Control)
    team = list(STAFF_CONFIG.keys())
    selected_team = st.segmented_control(
        "Команда", options=team, 
        format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}",
        default="Все"
    )

    tabs = st.tabs(["🔥 Активные", "⏳ Очередь", "✅ Архив"])
    statuses = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        with tab:
            curr_status = statuses[i]
            tasks = df[df['Статус'] == curr_status]
            if selected_team != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_team]

            if tasks.empty:
                st.write("---")
                st.caption("Задач в этой категории нет")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days_diff(row['Начало'])
                    person = row['Ответственный']
                    config = STAFF_CONFIG.get(person, STAFF_CONFIG["Все"])
                    
                    # МОНОЛИТНЫЙ БОКС (Bento Window)
                    with st.container(border=True):
                        # Сетка внутри карточки
                        c1, c2, c3, c4 = st.columns([0.45, 0.2, 0.15, 0.2])
                        
                        with c1:
                            st.markdown(f'<div class="task-heading">{row["Задача"]}</div>', unsafe_allow_html=True)
                            badge_class = "badge-urgent" if days > 7 else "badge-normal"
                            label = "дн. в работе" if curr_status == "В работе" else "старт"
                            st.markdown(f'<span class="status-badge {badge_class}">🕒 {days} {label}</span>', unsafe_allow_html=True)

                        with c2:
                            st.markdown('<div class="meta-label">Исполнитель</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="meta-value">{config["emoji"]} {person}</div>', unsafe_allow_html=True)
                        
                        with c3:
                            st.markdown('<div class="meta-label">Раздел</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="meta-value">📍 {row["Раздел сайта"]}</div>', unsafe_allow_html=True)

                        with c4:
                            # Управление статусом в стиле Apple Action Menu
                            st.markdown('<div class="meta-label">Действие</div>', unsafe_allow_html=True)
                            new_st = st.selectbox(
                                "Move to", statuses, 
                                index=statuses.index(curr_status),
                                key=f"act_{idx}",
                                label_visibility="collapsed"
                            )
                            if new_st != curr_status:
                                df.at[idx, 'Статус'] = new_st
                                conn.update(data=df)
                                st.rerun()

except Exception as e:
    st.error(f"System Link Error: {e}")

# Сайдбар (Добавление)
with st.sidebar:
    st.markdown("### ⊕ Create Task")
    with st.form("apple_form", clear_on_submit=True):
        f_task = st.text_input("Название задачи")
        f_sec = st.text_input("Раздел сайта")
        f_who = st.selectbox("Ответственный", [k for k in STAFF_CONFIG.keys() if k != "Все"])
        if st.form_submit_button("Подтвердить"):
            new_data = {
                "Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
