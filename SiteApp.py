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

# 4. Global CSS (Максимальная плотность)
st.markdown("""
<style>
    .stApp { background-color: #F8F9FA !important; }
    
    /* Компактная карточка */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        margin-bottom: 0.4rem !important;
    }

    .task-header { 
        font-size: 1.3rem; 
        font-weight: 800; 
        color: #111827; 
        line-height: 1.1; 
        margin-bottom: 4px;
    }

    .staff-row { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; }
    .staff-name { font-weight: 600; font-size: 0.9rem; }
    .meta-container { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; color: #9CA3AF; font-size: 0.7rem; opacity: 0.8; }
    
    /* Полоска прогресса */
    .main-progress-bg { background: #F3F4F6; border-radius: 10px; height: 3px; flex-grow: 1; }
    .main-progress-fill { height: 100%; border-radius: 10px; }
    
    /* Стилизация микро-кнопок */
    .stButton button {
        padding: 0px 5px !important;
        height: 26px !important;
        min-height: 26px !important;
        line-height: 26px !important;
        border: 1px solid #F3F4F6 !important;
        background: transparent !important;
        font-size: 13px !important;
    }
    .stButton button:hover { border-color: #D1D5DB !important; background: #F9FAFB !important; }

    /* Скрываем лишние отступы и подписи */
    div[data-testid="stSelectbox"] label { display: none !important; }
    div[data-testid="stSelectbox"] > div > div { min-height: 26px !important; height: 26px !important; }
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
            staff_list = [k for k in STAFF_CONFIG.keys() if k != "Все"]
            n_who = st.selectbox("Исполнитель", options=staff_list, format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}")
            n_date = st.date_input("Дата", value=date.today())
            if st.form_submit_button("Создать", use_container_width=True) and n_title:
                new_row = {"Раздел сайта": n_sec, "Задача": n_title, "Ответственный": n_who, "Начало": n_date.strftime("%d.%m.%Y"), "Статус": "В работе"}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(data=df)
                st.rerun()

    # --- MAIN UI ---
    st.markdown("# 🚀 разработка сайта D² DOM")
    
    sel_staff = st.segmented_control("Команда", options=list(STAFF_CONFIG.keys()), format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}", default="Все")

    tabs = st.tabs(["🔥 В работе", "⏳ Очередь", "✅ Выполнено", "📁 Архив"])
    status_map = ["В работе", "Запланировано", "Готово", "Архив"]

    if 'edit_idx' not in st.session_state: st.session_state.edit_idx = None

    for i, tab in enumerate(tabs):
        curr_status = status_map[i]
        with tab:
            view_df = df[df['Статус'] == curr_status]
            if sel_staff != "Все": 
                view_df = view_df[view_df['Ответственный'] == sel_staff]

            if view_df.empty:
                st.info("Пусто")
            else:
                for idx, row in view_df.iterrows():
                    
                    if st.session_state.edit_idx == idx:
                        # Режим редактирования (мини-форма)
                        with st.container(border=True):
                            e_title = st.text_input("Название", value=row['Задача'], key=f"et_{idx}")
                            e_sec = st.text_input("Раздел", value=row['Раздел сайта'], key=f"es_{idx}")
                            e_who = st.selectbox("Кто", options=staff_list, 
                                               index=staff_list.index(row['Ответственный']) if row['Ответственный'] in staff_list else 0,
                                               format_func=lambda x: f"{STAFF_CONFIG[x]['emoji']} {x}", key=f"ew_{idx}")
                            c1, c2 = st.columns(2)
                            if c1.button("✅ OK", key=f"sv_{idx}", use_container_width=True):
                                df.at[idx, 'Задача'] = e_title
                                df.at[idx, 'Раздел сайта'] = e_sec
                                df.at[idx, 'Ответственный'] = e_who
                                conn.update(data=df)
                                st.session_state.edit_idx = None
                                st.rerun()
                            if c2.button("❌", key=f"cn_{idx}", use_container_width=True):
                                st.session_state.edit_idx = None
                                st.rerun()
                    else:
                        # Обычный вид
                        try:
                            dt = datetime.strptime(str(row['Начало']).strip(), "%d.%m.%Y").date()
                            days = (date.today() - dt).days
                        except: days = 0
                        
                        role = STAFF_CONFIG.get(row['Ответственный'], STAFF_CONFIG["Все"])
                        chip_cls, fill_cls, fire = get_task_styles(days)
                        pct = min((days / 30) * 100, 100)

                        with st.container(border=True):
                            # ВЕРХНЯЯ СТРОКА: Заголовок + Микро-управление
                            h_col, ctrl_col = st.columns([0.6, 0.4])
                            h_col.markdown(f'<div class="task-header">{row["Задача"]}</div>', unsafe_allow_html=True)
                            
                            with ctrl_col:
                                # Микро-колонки для кнопок в один ряд
                                b1, b2, b3 = st.columns([0.6, 0.2, 0.2])
                                b1.selectbox("St", status_map, index=status_map.index(curr_status), key=f"s_{idx}")
                                if b2.button("✏️", key=f"ed_{idx}"):
                                    st.session_state.edit_idx = idx
                                    st.rerun()
                                if b3.button("🗑", key=f"dl_{idx}"):
                                    df.at[idx, 'Статус'] = "Архив"
                                    conn.update(data=df)
                                    st.rerun()

                            # ИНФО-СТРОКА
                            st.markdown(f"""
                            <div class="staff-row">
                                <span style="font-size:1.1rem;">{role['emoji']}</span>
                                <span class="staff-name" style="color:{role['text']};">{row['Ответственный']}</span>
                            </div>
                            <div class="meta-container">
                                <span>{row['Раздел сайта']}</span>
                                <span style="color:#D1D5DB;">•</span>
                                <span>{row['Начало']}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            # ТАЙМЕР
                            if curr_status != "Архив":
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div class="time-chip {chip_cls}">{fire}{days}д</div>
                                    <div class="main-progress-bg"><div class="main-progress-fill {fill_cls}" style="width: {pct}%;"></div></div>
                                </div>
                                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")
