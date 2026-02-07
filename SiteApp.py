import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Системные настройки
st.set_page_config(page_title="D² DOM Development", layout="wide")

# 2. Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Единый стандарт команды (Используем эти ключи для сопоставления)
STAFF_CONFIG = {
    "Программист": {"emoji": "👨‍💻", "bg": "#EBF5FF", "text": "#007AFF"},
    "Дизайнер": {"emoji": "🎨", "bg": "#FFF0F6", "text": "#D63384"},
    "SEO": {"emoji": "🔍", "bg": "#FFF9DB", "text": "#F59F00"},
    "Алина": {"emoji": "👩‍💼", "bg": "#F3F0FF", "text": "#7048E8"},
    "Лёша": {"emoji": "👨‍🔧", "bg": "#E7F5E9", "text": "#2E7D32"},
    "Все": {"emoji": "🌐", "bg": "#F8F9FA", "text": "#212529"}
}

# Функция для исправления имен из таблицы
def normalize_name(name):
    name = str(name).strip().lower()
    if "дизайн" in name: return "Дизайнер"
    if "лёша" in name or "леша" in name: return "Лёша"
    if "программист" in name: return "Программист"
    if "seo" in name: return "SEO"
    if "алина" in name: return "Алина"
    return "Все"

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
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
    }
    .task-title { font-size: 1.5rem; font-weight: 800; color: #1D1D1F; }
    .staff-badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; }
    .progress-bg { background: #E2E8F0; border-radius: 10px; height: 10px; flex-grow: 1; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; }
    .t-neutral { background: #F1F5F9; color: #475569; } .b-neutral { background: #94A3B8; }
    .t-yellow { background: #FEF3C7; color: #92400E; } .b-yellow { background: #F59E0B; }
    .t-orange { background: #FFEDD5; color: #9A3412; } .b-orange { background: #F97316; }
    .t-red { background: #FEE2E2; color: #991B1B; } .b-red { background: #EF4444; }
</style>
""", unsafe_allow_html=True)

def get_time_styles(days):
    if days <= 7: return "t-neutral", "b-neutral"
    elif days <= 14: return "t-yellow", "b-yellow"
    elif days <= 21: return "t-orange", "b-orange"
    return "t-red", "b-red"

try:
    # Загрузка и ГЛУБОКАЯ ЧИСТКА данных
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    if not df.empty:
        # Применяем нормализацию ко всей колонке ответственных
        df['Ответственный'] = df['Ответственный'].apply(normalize_name)

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("## ✨ Новая задача")
        with st.form("add_task_form", clear_on_submit=True):
            n_title = st.text_input("Название задачи")
            n_sec = st.text_input("Раздел сайта")
            n_who = st.selectbox("Исполнитель", [k for k in STAFF_CONFIG.keys() if k not in ["Все"]])
            n_date = st.date_input("Дата постановки", value=date.today())
            if st.form_submit_button("Добавить в план", use_container_width=True) and n_title:
                new_row = {
                    "Раздел сайта": n_sec, "Задача": n_title, "Ответственный": n_who,
                    "Начало": n_date.strftime("%d.%m.%Y"), "Статус": "Запланировано"
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=df)
                st.rerun()

        st.markdown("---")
        # СТАТИСТИКА
        active_df = df[df['Статус'] != "Архив"]
        
        st.markdown("## 📊 Статистика D² DOM")
        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric("🔥 В работе", len(active_df[active_df['Статус'] == "В работе"]))
            m1.metric("✅ Готово", len(active_df[active_df['Статус'] == "Готово"]))
            m2.metric("⏳ План", len(active_df[active_df['Статус'] == "Запланировано"]))
            m2.metric("📦 Всего", len(active_df))

        st.markdown("### ⚡ Загрузка (Задач в работе)")
        work_counts = active_df[active_df['Статус'] == "В работе"]['Ответственный'].value_counts()
        for member in [k for k in STAFF_CONFIG.keys() if k != "Все"]:
            count = work_counts.get(member, 0)
            st.write(f"{STAFF_CONFIG[member]['emoji']} **{member}**: {count}")

    # --- MAIN UI ---
    st.markdown("# 🚀 разработка сайта D² DOM")

    sel_staff = st.segmented_control(
        "Команда:", options=list(STAFF_CONFIG.keys()),
        format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}",
        default="Все"
    )

    tabs = st.tabs(["🔥 В работе", "⏳ Очередь", "✅ Выполнено", "📁 Архив"])
    st_list = ["В работе", "Запланировано", "Готово", "Архив"]

    for i, tab in enumerate(tabs):
        curr_st = st_list[i]
        with tab:
            filtered = df[df['Статус'] == curr_st]
            if sel_staff != "Все":
                filtered = filtered[filtered['Ответственный'] == sel_staff]

            if filtered.empty:
                st.info(f"Задач нет.")
            else:
                for idx, row in filtered.iterrows():
                    try:
                        d_start = datetime.strptime(str(row['Начало']).strip(), "%d.%m.%Y").date()
                        days = (date.today() - d_start).days
                    except: days = 0
                    
                    theme = STAFF_CONFIG.get(row['Ответственный'], STAFF_CONFIG["Все"])
                    chip_c, bar_c = get_time_styles(days)
                    pct = min((days / 30) * 100, 100)

                    with st.container(border=True):
                        h1, h2, h3 = st.columns([0.65, 0.25, 0.1])
                        h1.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
                        
                        # Выбор статуса
                        new_status = h2.selectbox("Статус", st_list, index=st_list.index(curr_st), key=f"s_{idx}", label_visibility="collapsed")
                        if new_status != curr_st:
                            df.at[idx, 'Статус'] = new_status
                            conn.update(data=df)
                            st.rerun()
                        
                        # Архив
                        if h3.button("🗑", key=f"del_{idx}"):
                            df.at[idx, 'Статус'] = "Архив"
                            conn.update(data=df)
                            st.rerun()

                        st.markdown(f"""
                            <div style="margin: 10px 0 20px 0;">
                                <span class="staff-badge" style="background:{theme['bg']}; color:{theme['text']};">
                                    {theme['emoji']} {row['Ответственный']}
                                </span>
                                <span style="margin-left:15px; color:#86868B;">📍 {row['Раздел сайта']}</span>
                                <span style="margin-left:15px; font-size:0.85rem; color:#86868B;">📅 С {row['Начало']}</span>
                            </div>
                        """, unsafe_allow_html=True)

                        if curr_st != "Архив":
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 15px;">
                                    <div class="days-chip {chip_c}">⏱ {days} дн.</div>
                                    <div class="progress-bg"><div class="progress-fill {bar_c}" style="width: {pct}%;"></div></div>
                                </div>
                            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")
