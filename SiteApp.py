import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Manager Liquid", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Словарь эмодзи
STAFF_EMOJI = {"Программист": "💻", "Дизайнер": "🎨", "SEO": "🔍", "Алина": "👩‍💼", "Все": "🌐"}

# Дизайн: Исправленные монолитные окна
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
        color: #f1f5f9;
    }

    /* Монолитное окно - теперь это ОДИН контейнер */
    .task-window {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .task-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 20px;
        line-height: 1.2;
    }

    .task-footer {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 25px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
        font-size: 1.1rem;
    }

    .person-tag {
        background: rgba(255, 255, 255, 0.1);
        padding: 5px 15px;
        border-radius: 12px;
        color: #fff;
        font-weight: 600;
    }

    .fire-status { color: #fb7185; font-weight: 800; }

    /* Исправление отображения фильтров */
    div[data-testid="stSegmentedControl"] button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: #3b82f6 !important;
    }
    
    /* Стилизация выпадающего списка выбора статуса, чтобы он не ломал верстку */
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
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
    
    st.markdown("# 🛸 Project Dashboard")
    
    staff_list = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    tabs = st.tabs(["🔥 В работе", "⏳ План", "💎 Готово"])
    status_list = ["В работе", "Запланировано", "Готово"]

    for i, tab in enumerate(tabs):
        curr_status = status_list[i]
        with tab:
            # Горизонтальный фильтр
            sel_person = st.segmented_control(
                "Фильтр:", options=staff_list, 
                format_func=lambda x: f"{STAFF_EMOJI.get(x, '')} {x}",
                default="Все", key=f"f_{curr_status}"
            )
            
            tasks = df[df['Статус'] == curr_status]
            if sel_person != "Все":
                tasks = tasks[tasks['Ответственный'] == sel_person]
            
            for idx, row in tasks.iterrows():
                days = get_days(row['Начало'])
                person = row['Ответственный']
                emoji = STAFF_EMOJI.get(person, "👤")
                
                # ЧТОБЫ НИЧЕГО НЕ ВЫЛЕТАЛО:
                # Мы создаем контейнер и ВСЁ содержимое пишем внутри него через columns
                with st.container():
                    # Вот это и есть наше "Стеклянное окно"
                    # Мы имитируем его через markdown ПЕРЕД контентом и ПОСЛЕ
                    st.markdown(f'<div class="task-window">', unsafe_allow_html=True)
                    
                    # Разделяем на заголовок и кнопку смены статуса
                    col_title, col_action = st.columns([0.75, 0.25])
                    
                    with col_title:
                        st.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
                    
                    with col_action:
                        # Используем компактный selectbox вместо popover для стабильности
                        new_st = st.selectbox(
                            "Изменить статус:", status_list, 
                            index=status_list.index(curr_status),
                            key=f"move_{idx}",
                            label_visibility="collapsed"
                        )
                        if new_st != curr_status:
                            df.at[idx, 'Статус'] = new_st
                            conn.update(data=df)
                            st.rerun()

                    # Футер с данными
                    time_html = f'<span class="fire-status">🔥 {days} дн.</span>' if curr_status == "В работе" else f"📅 {row['Начало']}"
                    
                    st.markdown(f"""
                        <div class="task-footer">
                            <div class="person-tag">{emoji} {person}</div>
                            <div>📍 {row['Раздел сайта']}</div>
                            <div>{time_html}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Ошибка: {e}")

# Сайдбар
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("add"):
        f_sec = st.text_input("Раздел")
        f_task = st.text_area("Задача")
        f_who = st.selectbox("Кто", staff_list[1:])
        if st.form_submit_button("Создать"):
            new = {"Раздел сайта": f_sec, "Задача": f_task, "Ответственный": f_who, 
                   "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"}
            upd = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
