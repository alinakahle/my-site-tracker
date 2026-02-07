import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Config
st.set_page_config(page_title="D² DOM Development", layout="wide")

# 2. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Staff Configuration
STAFF_CONFIG = {
    "Программист": {"emoji": "👨‍💻", "bg": "#EBF5FF", "text": "#007AFF"},
    "Дизайнер": {"emoji": "🎨", "bg": "#FFF0F6", "text": "#D63384"},
    "SEO": {"emoji": "🔍", "bg": "#FFF9DB", "text": "#F59F00"},
    "Алина": {"emoji": "👩‍💼", "bg": "#F3F0FF", "text": "#7048E8"},
    "Лёша": {"emoji": "👨‍🔧", "bg": "#E7F5E9", "text": "#2E7D32"},
    "Все": {"emoji": "🌐", "bg": "#F8F9FA", "text": "#212529"}
}

def normalize_name(name):
    n = str(name).strip().lower()
    if not n or n in ["none", "nan", ""]: return "Все"
    if "леш" in n or "лёш" in n: return "Лёша"
    if "дизайн" in n: return "Дизайнер"
    if "програм" in n: return "Программист"
    if "seo" in n: return "SEO"
    if "алин" in n: return "Алина"
    return "Все"

# 4. Global CSS
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA !important; }
    
    /* Card Styling */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }

    /* Task Typography */
    .task-header { font-size: 1.75rem; font-weight: 800; color: #111827; line-height: 1.2; margin-bottom: 8px; }
    .staff-row { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
    .staff-name { font-weight: 600; font-size: 1.05rem; }
    
    /* Meta Info */
    .meta-text { color: #9CA3AF; font-size: 0.85rem; font-weight: 400; }
    .meta-icon { font-size: 0.8rem; vertical-align: middle; }

    /* Time Badges */
    .time-chip { padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; display: inline-flex; align-items: center; gap: 4px; }
    .t-0-7 { background: #F3F4F6; color: #4B5563; }
    .t-8-14 { background: #FEF3C7; color: #92400E; }
    .t-15-21 { background: #FFEDD5; color: #9A3412; }
    .t-22plus { background: #FEE2E2; color: #B91C1C; }

    /* Mini Progress Bars */
    .mini-bar-container { width: 100%; height: 6px; background: #E5E7EB; border-radius: 10px; margin-top: 4px; overflow: hidden; }
    .mini-bar-fill { height: 100%; background: #9CA3AF; border-radius: 10px; }
    .load-row { margin-bottom: 12px; }

    /* Main Progress Bar */
    .main-progress-bg { background: #F3F4F6; border-radius: 4px; height: 4px; flex-grow: 1; overflow: hidden; margin-top: 2px; }
    .main-progress-fill { height: 100%; border-radius: 4px; }
    .fill-0-7 { background: #9CA3AF; }
    .fill-8-14 { background: #FBBF24; }
    .fill-15-21 { background: #F97316; }
    .fill-22plus { background: #EF4444; }

    /* Fix selectbox visibility */
    div[data-testid="stSelectbox"] label { display: none !important; }
</style>
""", unsafe_allow_html=True)

def get_task_styles(days):
    if days <= 7: return "t-0-7", "fill-0-7", ""
    elif days <= 14: return "t-8-14", "fill-8-14", ""
    elif days <= 21: return "t-15-21", "fill-15-21", ""
    return "t-22plus", "fill-22plus", "🔥 "

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    if not df.empty:
        df['Ответственный'] = df['Ответственный'].apply(normalize_name)

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### ✨ Новая задача")
        with st.form("add_task", clear_on_submit=True):
            n_title = st.text_input("Название")
            n_sec = st.text_input("Раздел")
            n_who = st.selectbox("Исполнитель", [k for k in STAFF_CONFIG.keys() if k != "Все"])
            n_date = st.date_input("Дата", value=date.today())
            if st.form_submit_button("Создать", use_container_width=True) and n_title:
                new_row = {"Раздел сайта": n_sec, "Задача": n_title, "Ответственный": n_who, "Начало": n_date.strftime("%d.%m.%Y"), "Статус": "Запланировано"}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=df)
                st.rerun()

        st.markdown("---")
        st.markdown("### ⚡ Загрузка (задач в работе)")
        active_in_work = df[df['Статус'] == "В работе"]
        if not active_in_work.empty:
            counts = active_in_work['Ответственный'].value_counts()
            max_val = counts.max()
            for name, val in counts.items():
                pct = (val / max_val) * 100
                st.markdown(f"""
                <div class="load-row">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                        <span>{STAFF_CONFIG[name]['emoji']} {name}</span>
                        <span style="font-weight: 700;">{val}</span>
                    </div>
                    <div class="mini-bar-container">
