import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Manager Liquid", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Словарь эмодзи для ответственных
STAFF_EMOJI = {
    "Программист": "💻",
    "Дизайнер": "🎨",
    "SEO": "🔍",
    "Алина": "👩‍💼",
    "Все": "🌐"
}

# Дизайн: Каждая задача в отдельном "окне" (Glass Window)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f1f5f9;
    }

    /* Стиль отдельного окна для задачи */
    .task-window {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 30px; /* Большой отступ между окнами */
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }

    /* Заголовок задачи - крупный и четкий */
    .task-header-text {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    /* Информационная панель внизу окна */
    .task-info-bar {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: flex-start;
        gap: 35px;
        color: #94a3b8;
        font-size: 1.1rem;
    }

    .info-block { display: flex; align-items: center; gap: 8px; }
    .person-name { color: #ffffff; font-weight: 700; }
    .fire-status { color: #fb7185; font-weight: 800; }

    /* Исправление кнопок фильтра */
    div[data-testid="stSegmentedControl"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-size: 1rem !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: #3b82f6 !important;
        border-color: #60a5fa !important;
    }

    /* Кастомизация Popover (кнопка статуса) */
    div[data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.07) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            dt = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            dt = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - dt).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.markdown("# 🛸 Управление проектами")
    
    staff_list = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    tabs = st.tabs(["🔥 В работе", "⏳ В планах", "💎 Завершено"])
    status_list = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = status_list[i]
        with tab:
            # Горизонтальный фильтр с эмодзи
            filter_options = {p: f"{STAFF_EMOJI.get(p, '')} {p}" for p in staff_list}
            sel_person = st.segmented_control(
                "Фильтр команды:", 
                options=staff_list, 
                format_func=lambda x: filter_options[x],
                default="Все", 
                key=f"filter_{curr_status}"
            )
            
            st.write("") # Пространство
            
            tasks = df[df['Статус'] == curr_status]
            if sel_person != "Все":
                tasks = tasks[tasks['Ответственный'] == sel_person]
            
            if tasks.empty:
                st.info("В этом разделе пока нет задач")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    person = row['Ответственный']
                    emoji = STAFF_EMOJI.get(person, "👤")
                    
                    # Начало отдельного "Окна" задачи
                    st.markdown(f'<div class="task-window">', unsafe_allow_html=True)
                    
                    # Верхняя часть: Заголовок и кнопка
                    t_col1, t_col2 = st.columns([0.8, 0.2])
                    with t_col1:
                        st.markdown(f'<p class="task-header-text">{row["Задача"]}</p>', unsafe_allow_html=True)
                    with t_col2:
                        with st.popover(curr_status, use_container_width=True):
                            st.write("📍 Сменить этап:")
                            new_st = st.radio("Куда:", status_list, 
                                            index=status_list.index(curr_status),
                                            key=f"m_{idx}")
                            if new_st != curr_status:
                                df.at[idx, 'Статус'] = new_st
                                conn.update(data=df)
                                st.rerun()
                    
                    # Нижняя панель с мета-данными
                    time_html = f'<div class="info-block"><span class="fire-status">🔥 {days} дн. в работе</span></div>' if curr_status == "В работе" else f'<div class="info-block">📅 {row["Начало"]}</div>'
                    
                    st.markdown(f"""
                        <div class="task-info-bar">
                            <div class="info-block"><span style="font-size:1.4rem;">{emoji}</span> <span class="person-name">{person}</span></div>
                            <div class="info-block">📍 {row['Раздел сайта']}</div>
                            {time_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка чтения данных: {e}")

# Сайдбар
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("add_task", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Что нужно сделать?")
        f_who = st.selectbox("Кто ответственный?", staff_list[1:])
        if st.form_submit_button("Создать задачу ✨"):
            new_row = {
                "Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
