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
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        margin-bottom: 1rem !important;
    }
    .task-header { font-size: 1.85rem; font-weight: 800; color: #111827; line-height: 1.2; margin-bottom: 12px; }
    .staff-row { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
    .staff-name { font-weight: 600; font-size: 1.1rem; }
    .meta-container { display: flex; gap: 24px; margin-bottom: 24px; }
    .meta-text { color: #9CA3AF; font-size: 0.85rem; font-weight: 400; display: flex; align-items: center; gap: 6px; }
    .time-chip { padding: 6px 14px; border-radius: 100px; font-weight: 800; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 6px; }
    .t-0-7 { background: #F3F4F6; color: #4B5563; }
    .t-8-14 { background: #FEF3C7; color: #92400E; }
    .t-15-21 { background: #FFEDD5; color: #9A3412; }
    .t-22plus { background: #FEE2E2; color: #B91C1C; }
    .mini-bar-container { width: 100%; height: 6px; background: #E5E7EB; border-radius: 10px; margin-top: 6px; overflow: hidden; }
    .mini-bar-fill { height: 100%; background: #9CA3AF; border-radius: 10px; }
    .main-progress-bg { background: #F3F4F6; border-radius: 10px; height: 5px; flex-grow: 1; overflow: hidden; }
    .main-progress-fill { height: 100%; border-radius: 10px; }
    .fill-0-7 { background: #D1D5DB; }
    .fill-8-14 { background: #FBBF24; }
    .fill-15-21 { background: #F97316; }
    .fill-22plus { background: #EF4444; }
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
            if st.form_submit_button("Добавить", use_container_width=True) and n_title:
                new_row = {"Раздел сайта": n_sec, "Задача": n_title, "Ответственный": n_who, "Начало": n_date.strftime("%d.%m.%Y"), "Статус": "Запланировано"}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=df)
                st.rerun()

        st.markdown("---")
        
        # СТАТИСТИКА ПРОЕКТА
        active_df = df[df['Статус'] != "Архив"]
        st.markdown("### 📊 Общая статистика")
        c1, c2 = st.columns(2)
        c1.metric("🔥 В работе", len(active_df[active_df['Статус'] == "В работе"]))
        c1.metric("✅ Готово", len(active_df[active_df['Статус'] == "Готово"]))
        c2.metric("⏳ План", len(active_df[active_df['Статус'] == "Запланировано"]))
        c2.metric("📦 Всего", len(active_df))

        st.markdown("---")
        
        # ЗАГРУЗКА КОМАНДЫ (С БАРАМИ)
        st.markdown("### ⚡ Загрузка (задач в работе)")
        work_df = active_df[active_df['Статус'] == "В работе"]
        if not work_df.empty:
            load_data = work_df['Ответственный'].value_counts().sort_values(ascending=False)
            max_load = load_data.max()
            for name, count in load_data.items():
                pct = (count / max_load) * 100
                st.markdown(f"""
                <div style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                        <span>{STAFF_CONFIG[name]['emoji']} {name}</span>
                        <span style="font-weight: 700;">{count}</span>
                    </div>
                    <div class="mini-bar-container">
                        <div class="mini-bar-fill" style="width: {pct}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- MAIN UI ---
    st.markdown("# 🚀 разработка сайта D² DOM")
    
    sel_staff = st.segmented_control(
        "Команда", options=list(STAFF_CONFIG.keys()),
        format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}", default="Все"
    )

    tabs = st.tabs(["🔥 В работе", "⏳ Очередь", "✅ Выполнено", "📁 Архив"])
    status_map = ["В работе", "Запланировано", "Готово", "Архив"]

    for i, tab in enumerate(tabs):
        curr_status = status_map[i]
        with tab:
            view_df = df[df['Статус'] == curr_status]
            if sel_staff != "Все":
                view_df = view_df[view_df['Ответственный'] == sel_staff]

            if view_df.empty:
                st.info("Нет задач")
            else:
                for idx, row in view_df.iterrows():
                    try:
                        dt = datetime.strptime(str(row['Начало']).strip(), "%d.%m.%Y").date()
                        days = (date.today() - dt).days
                    except: days = 0
                    
                    role = STAFF_CONFIG.get(row['Ответственный'], STAFF_CONFIG["Все"])
                    chip_cls, fill_cls, fire = get_task_styles(days)
                    pct = min((days / 30) * 100, 100)

                    with st.container(border=True):
                        col_t, col_s = st.columns([0.72, 0.28])
                        col_t.markdown(f'<div class="task-header">{row["Задача"]}</div>', unsafe_allow_html=True)
                        new_val = col_s.selectbox("Status", status_map, index=status_map.index(curr_status), key=f"s_{idx}")
                        if new_val != curr_status:
                            df.at[idx, 'Статус'] = new_val
                            conn.update(data=df)
                            st.rerun()

                        st.markdown(f"""
                        <div class="staff-row">
                            <span style="font-size: 1.5rem;">{role['emoji']}</span>
                            <span class="staff-name" style="color: {role['text']};">{row['Ответственный']}</span>
                        </div>
                        <div class="meta-container">
                            <span class="meta-text">📍 {row['Раздел сайта']}</span>
                            <span class="meta-text">📅 {row['Начало']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        if curr_status != "Архив":
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <div class="time-chip {chip_cls}">{fire}{days} дн.</div>
                                <div class="main-progress-bg">
                                    <div class="main-progress-fill {fill_cls}" style="width: {pct}%;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")
