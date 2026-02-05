import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Настройка страницы и темы
st.set_page_config(page_title="Kanban Liquid Glass", layout="wide")

# 2. Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Словарь ответственных и их эмодзи
STAFF = {
    "Программист": "💻",
    "Дизайнер": "🎨",
    "SEO": "🔍",
    "Алина": "👩‍💼",
    "Все": "🌐"
}

# 3. CSS: Настоящий Liquid Glass и исправление читаемости
st.markdown("""
<style>
    /* Темный космический фон */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f1f5f9;
    }

    /* Стиль для каждого контейнера-задачи */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    /* Исправляем читаемость верхнего меню (segmented control) */
    div[data-testid="stSegmentedControl"] button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: #3b82f6 !important;
        font-weight: bold !important;
    }

    /* Заголовки задач внутри боксов */
    .task-title {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
        margin-bottom: 15px !important;
    }

    /* Нижняя панель внутри бокса */
    .task-meta {
        display: flex;
        gap: 20px;
        align-items: center;
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-top: 10px;
    }
    
    .fire-badge {
        background: rgba(251, 113, 133, 0.2);
        color: #fb7185;
        padding: 2px 10px;
        border-radius: 8px;
        font-weight: bold;
    }
    
    .done-badge {
        background: rgba(52, 211, 153, 0.2);
        color: #34d399;
        padding: 2px 10px;
        border-radius: 8px;
        font-weight: bold;
    }

    /* Убираем лишние отступы внутри колонок Streamlit */
    div[data-testid="column"] {
        gap: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

def calculate_days(date_val):
    try:
        if isinstance(date_val, (date, datetime)):
            start_date = date_val.date() if isinstance(date_val, datetime) else date_val
        else:
            start_date = datetime.strptime(str(date_val).strip(), "%d.%m.%Y").date()
        return (date.today() - start_date).days
    except: return 0

try:
    # Читаем данные
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🛸 Project Dashboard (Liquid)")

    # Горизонтальный фильтр по команде
    staff_names = list(STAFF.keys())
    selected_staff = st.segmented_control(
        "Кто в фокусе:", 
        options=staff_names, 
        format_func=lambda x: f"{STAFF[x]} {x}",
        default="Все", 
        key="team_filter"
    )

    tabs = st.tabs(["🔥 В работе", "⏳ План", "✅ Готово"])
    status_map = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = status_map[i]
        with tab:
            # Фильтрация данных
            tasks = df[df['Статус'] == curr_status]
            if selected_staff != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_staff]

            if tasks.empty:
                st.write("Пусто")
            else:
                for idx, row in tasks.iterrows():
                    days = calculate_days(row['Начало'])
                    person = row['Ответственный']
                    emoji = STAFF.get(person, "👤")
                    
                    # СОЗДАЕМ БОКС (Window)
                    with st.container(border=True):
                        # Внутри бокса две колонки: для задачи и для управления
                        col_text, col_ctrl = st.columns([0.8, 0.2])
                        
                        with col_text:
                            st.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
                            
                            # Мета-данные
                            time_tag = ""
                            if curr_status == "В работе":
                                time_tag = f'<span class="fire-badge">🔥 {days} дн.</span>'
                            elif curr_status == "Готово":
                                time_tag = f'<span class="done-badge">✅ Завершено</span>'
                            else:
                                time_tag = f'<span>📅 {row["Начало"]}</span>'

                            st.markdown(f"""
                                <div class="task-meta">
                                    <span style="color:white"><b>{emoji} {person}</b></span>
                                    <span>📍 {row['Раздел сайта']}</span>
                                    {time_tag}
                                </div>
                            """, unsafe_allow_html=True)

                        with col_ctrl:
                            # Смена статуса (принудительно сидит внутри бокса)
                            new_val = st.selectbox(
                                "Статус", status_map, 
                                index=status_map.index(curr_status),
                                key=f"st_{idx}",
                                label_visibility="collapsed"
                            )
                            if new_val != curr_status:
                                df.at[idx, 'Статус'] = new_val
                                conn.update(data=df)
                                st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки: {e}")

# Боковая панель для добавления
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("new_task", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Суть задачи")
        f_who = st.selectbox("Кто делает?", [k for k in STAFF.keys() if k != "Все"])
        if st.form_submit_button("Добавить в работу"):
            new_row = {
                "Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
