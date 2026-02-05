import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# 1. Настройка страницы
st.set_page_config(page_title="Site Manager Pro", layout="wide")

# 2. Подключение (использует твои Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Стиль
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .card { 
        background: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 12px; 
    }
    .task-title { font-weight: bold; font-size: 1.1em; color: #f0f6fc; }
    .task-meta { font-size: 0.85em; color: #8b949e; margin-top: 5px; }
    .days-badge { 
        background: #238636; 
        color: white; 
        padding: 2px 8px; 
        border-radius: 5px; 
        font-size: 0.8em; 
        float: right;
    }
    h3 { color: #58a6ff !important; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Функция для расчета дней
def get_days_in_work(start_date_str):
    try:
        # Пытаемся распознать дату из таблицы (формат 06.10.2025)
        start_date = datetime.strptime(str(start_date_str), "%d.%m.%Y").date()
        delta = (date.today() - start_date).days
        return max(0, delta)
    except:
        return "?"

# 4. Загрузка данных
try:
    # Загружаем данные (без указания листа, чтобы взял первый активный)
    df = conn.read(ttl=0).dropna(how="all").fillna("")

    st.title("🎯 Мониторинг задач (Kanban)")

    # Определяем этапы
    stages = ["Запланировано", "В работе", "Готово"]
    cols = st.columns(3)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"### {stage}")
            
            # В твоей таблице Статус — это колонка H (индекс 7)
            # Но на всякий случай ищем колонку с названием 'Статус'
            status_col = "Статус" if "Статус" in df.columns else df.columns[7]
            tasks = df[df[status_col] == stage]
            
            for idx, row in tasks.iterrows():
                # Привязываемся к твоим названиям колонок
                task_name = row["Задача"]
                section = row["Раздел сайта"]
                who = row["Ответственный"]
                start_dt = row["Начало"]
                
                days_html = ""
                if stage == "В работе":
                    days = get_days_in_work(start_dt)
                    days_html = f'<div class="days-badge">🔥 {days} дн.</div>'

                with st.container():
                    st.markdown(f"""
                        <div class="card">
                            {days_html}
                            <div class="task-title">{task_name}</div>
                            <div class="task-meta">📍 {section}</div>
                            <div class="task-meta">👤 {who} | 📅 {start_dt}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Кнопка смены статуса
                    with st.popover("⚙️ Изменить статус"):
                        new_s = st.radio("Куда:", stages, index=stages.index(stage), key=f"btn_{idx}")
                        if new_s != stage:
                            df.at[idx, status_col] = new_s
                            conn.update(data=df)
                            st.rerun()

except Exception as e:
    st.error(f"Не удалось прочитать таблицу: {e}")

# 5. Боковая панель (Создание новой задачи)
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("new_task", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Что сделать?")
        f_who = st.selectbox("Ответственный", ["Программист", "Дизайнер", "SEO", "Алина"])
        
        if st.form_submit_button("Добавить"):
            # Создаем строку, соответствующую твоей таблице (A-H)
            new_row = {
                "Раздел сайта": f_sec,
                "Задача": f_task,
                "Ответственный": f_who,
                "Начало": date.today().strftime("%d.%m.%Y"),
                "Дедлайн": "",
                "дней в работе": "",
                "Статус": "Запланировано"
            }
            # Добавляем в конец
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Задача улетела в Google!")
            st.rerun()
