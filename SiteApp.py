import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Настройка премиального светлого интерфейса
st.set_page_config(page_title="Task Manager Studio", layout="wide")

# 2. Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Цветовая схема сотрудников (High Visibility)
STAFF_THEME = {
    "Программист": {"emoji": "👨‍💻", "bg": "#EBF5FF", "text": "#007AFF"},
    "Дизайнер": {"emoji": "🎨", "bg": "#FFF0F6", "text": "#D63384"},
    "SEO": {"emoji": "🔍", "bg": "#FFF9DB", "text": "#F59F00"},
    "Алина": {"emoji": "👩‍💼", "bg": "#F3F0FF", "text": "#7048E8"},
    "Все": {"emoji": "🌐", "bg": "#F8F9FA", "text": "#212529"}
}

# 4. CSS: Чистый светлый дизайн (Apple Style 2026)
st.markdown(f"""
<style>
    /* Фон приложения - мягкий светлый */
    .stApp {{
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
    }}

    /* СТИЛЬ КАРТОЧКИ: Белый монолит */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #D2D2D7 !important;
        border-radius: 18px !important;
        padding: 0px !important; /* Убираем падинги, чтобы сделать кастомные зоны */
        margin-bottom: 20px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        overflow: hidden !important;
    }}

    /* Внутренняя область контента */
    .card-content {{
        padding: 24px;
    }}

    /* Заголовок задачи */
    .task-title {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1D1D1F !important;
        margin-bottom: 16px !important;
        line-height: 1.3;
    }}

    /* Бейдж ответственного */
    .staff-badge {{
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        margin-right: 12px;
    }}

    /* Инфо-строка */
    .info-row {{
        display: flex;
        align-items: center;
        gap: 15px;
        color: #86868B;
        font-size: 0.9rem;
        margin-top: 10px;
    }}

    /* Зона управления (Нижняя часть карточки) */
    .control-zone {{
        background-color: #FBFBFD;
        border-top: 1px solid #D2D2D7;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    /* Тюнинг вкладок */
    .stTabs [data-baseweb="tab-list"] {{ background: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{
        font-weight: 600 !important;
        color: #86868B !important;
        border-bottom: 2px solid transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: #007AFF !important;
        border-bottom: 2px solid #007AFF !important;
    }}
    
    /* Скрываем лишние заголовки Streamlit внутри карточек */
    .stSelectbox label {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            d = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            d = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - d).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("📋 Управление проектами")

    # Фильтр команды
    staff_names = list(STAFF_THEME.keys())
    sel_staff = st.segmented_control(
        "Команда", options=staff_names,
        format_func=lambda x: f"{STAFF_THEME[x]['emoji']} {x}",
        default="Все"
    )

    tabs = st.tabs(["🕒 В работе", "📅 План", "✅ Готово"])
    st_options = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = st_options[i]
        with tab:
            tasks = df[df['Статус'] == curr_status]
            if sel_staff != "Все":
                tasks = tasks[tasks['Ответственный'] == sel_staff]

            if tasks.empty:
                st.info("В этой категории пока нет задач")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    person = row['Ответственный']
                    theme = STAFF_THEME.get(person, STAFF_THEME["Все"])
                    
                    # КОРПУС КАРТОЧКИ
                    with st.container(border=True):
                        # 1. Секция контента
                        st.markdown(f"""
                        <div class="card-content">
                            <div class="task-title">{row['Задача']}</div>
                            <div style="display: flex; align-items: center;">
                                <span class="staff-badge" style="background:{theme['bg']}; color:{theme['text']};">
                                    {theme['emoji']} {person}
                                </span>
                                <span style="color: #86868B; font-size: 0.9rem;">📍 {row['Раздел сайта']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # 2. Секция управления (Статус жестко привязан к карточке)
                        # Используем колонки Streamlit внутри контейнера для селектора
                        st.markdown("<div class='control-zone'>", unsafe_allow_html=True)
                        
                        c_info, c_select = st.columns([0.6, 0.4])
                        with c_info:
                            if curr_status == "В работе":
                                st.markdown(f"**🔥 {days} дн. в процессе**")
                            else:
                                st.markdown(f"📅 С: {row['Начало']}")
                        
                        with c_select:
                            # Селектор теперь физически находится ВНУТРИ белой рамки задачи
                            new_st = st.selectbox(
                                "Статус", st_options,
                                index=st_options.index(curr_status),
                                key=f"status_{idx}"
                            )
                            if new_st != curr_status:
                                df.at[idx, 'Статус'] = new_st
                                conn.update(data=df)
                                st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка системы: {e}")

# Сайдбар для ввода
with st.sidebar:
    st.header("✨ Создать задачу")
    with st.form("new_task"):
        f_task = st.text_input("Что нужно сделать?")
        f_sec = st.text_input("Раздел (например, Шапка)")
        f_who = st.selectbox("Кто исполнитель?", [k for k in STAFF_THEME.keys() if k != "Все"])
        if st.form_submit_button("Добавить в очередь"):
            new_data = {
                "Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who,
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
