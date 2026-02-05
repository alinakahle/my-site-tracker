import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Системные настройки
st.set_page_config(page_title="Task Flow Pro 2026", layout="wide")

# 2. Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Конфигурация команды
STAFF_CONFIG = {
    "Программист": {"emoji": "👨‍💻", "bg": "#EBF5FF", "text": "#007AFF"},
    "Дизайнер": {"emoji": "🎨", "bg": "#FFF0F6", "text": "#D63384"},
    "SEO": {"emoji": "🔍", "bg": "#FFF9DB", "text": "#F59F00"},
    "Алина": {"emoji": "👩‍💼", "bg": "#F3F0FF", "text": "#7048E8"},
    "Все": {"emoji": "🌐", "bg": "#F8F9FA", "text": "#212529"}
}

# 4. Премиальный CSS
st.markdown("""
<style>
    .stApp { background-color: #F5F5F7 !important; }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #D2D2D7 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
        border-color: #007AFF !important;
    }

    .task-title { font-size: 1.6rem; font-weight: 800; color: #1D1D1F; line-height: 1.2; margin-bottom: 12px; }
    .staff-badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 8px; font-weight: 600; font-size: 0.95rem; }
    .section-label { color: #86868B; font-size: 0.95rem; margin-left: 12px; font-weight: 500; }

    .days-chip { padding: 4px 14px; border-radius: 100px; font-weight: 700; font-size: 0.85rem; white-space: nowrap; }
    .progress-bg { background: #E2E8F0; border-radius: 10px; height: 10px; flex-grow: 1; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; transition: width 0.5s ease; }

    .t-neutral { background: #F1F5F9; color: #475569; } .b-neutral { background: #94A3B8; }
    .t-yellow { background: #FEF3C7; color: #92400E; } .b-yellow { background: #F59E0B; }
    .t-orange { background: #FFEDD5; color: #9A3412; } .b-orange { background: #F97316; }
    .t-red { background: #FEE2E2; color: #991B1B; } .b-red { background: #EF4444; }

    div[data-testid="stSegmentedControl"] button { background: white !important; border: 1px solid #D2D2D7 !important; }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] { background: #007AFF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

def get_time_styles(days):
    if days <= 7: return "t-neutral", "b-neutral"
    elif days <= 14: return "t-yellow", "b-yellow"
    elif days <= 21: return "t-orange", "b-orange"
    return "t-red", "b-red"

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    # --- SIDEBAR (Создание задачи с датой) ---
    with st.sidebar:
        st.markdown("## ✨ Новая задача")
        with st.form("add_task_form", clear_on_submit=True):
            new_title = st.text_input("Название задачи")
            new_sec = st.text_input("Раздел сайта")
            new_who = st.selectbox("Исполнитель", [k for k in STAFF_CONFIG.keys() if k != "Все"])
            
            # НОВОЕ ПОЛЕ: Выбор даты постановки задачи
            new_date = st.date_input("Когда поставлена?", value=date.today())
            
            submit = st.form_submit_button("Добавить в план", use_container_width=True)
            
            if submit and new_title:
                new_row = {
                    "Раздел сайта": new_sec, 
                    "Задача": new_title, 
                    "Ответственный": new_who,
                    "Начало": new_date.strftime("%d.%m.%Y"), # Сохраняем выбранную дату
                    "Статус": "Запланировано"
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=df)
                st.toast(f"Задача добавлена с {new_date.strftime('%d.%m.%Y')}", icon="✅")
                st.rerun()

    # --- MAIN UI ---
    st.markdown("# 🚀 Task Flow Control")

    staff_options = list(STAFF_CONFIG.keys())
    selected_staff = st.segmented_control(
        "Команда:", options=staff_options,
        format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}",
        default="Все"
    )

    tabs = st.tabs(["🔥 В работе", "⏳ В планах", "✅ Завершено"])
    status_list = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        current_status = status_list[i]
        with tab:
            filtered = df[df['Статус'] == current_status]
            if selected_staff != "Все":
                filtered = filtered[filtered['Ответственный'] == selected_staff]

            if filtered.empty:
                st.info(f"Задач в статусе '{current_status}' нет.")
            else:
                for idx, row in filtered.iterrows():
                    try:
                        start_dt = datetime.strptime(str(row['Начало']).strip(), "%d.%m.%Y").date()
                        days_count = (date.today() - start_dt).days
                    except: days_count = 0
                    
                    theme = STAFF_CONFIG.get(row['Ответственный'], STAFF_CONFIG["Все"])
                    chip_cls, bar_cls = get_time_styles(days_count)
                    progress_pct = min((days_count / 30) * 100, 100)

                    with st.container(border=True):
                        c_title, c_action = st.columns([0.7, 0.3])
                        with c_title:
                            st.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
                        with c_action:
                            new_val = st.selectbox(
                                "Статус", status_list, 
                                index=status_list.index(current_status),
                                key=f"move_{idx}", label_visibility="collapsed"
                            )
                            if new_val != current_status:
                                df.at[idx, 'Статус'] = new_val
                                conn.update(data=df)
                                st.rerun()

                        st.markdown(f"""
                            <div style="margin-bottom: 20px;">
                                <span class="staff-badge" style="background:{theme['bg']}; color:{theme['text']};">
                                    {theme['emoji']} {row['Ответственный']}
                                </span>
                                <span class="section-label">📍 {row['Раздел сайта']}</span>
                                <span style="margin-left:15px; font-size:0.85rem; color:#86868B;">📅 С {row['Начало']}</span>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <div class="days-chip {chip_cls}">⏱ {days_count} дн.</div>
                                <div class="progress-bg">
                                    <div class="progress-fill {bar_cls}" style="width: {progress_pct}%;"></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Системная ошибка: {e}")
