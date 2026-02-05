import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Tracker Pro", layout="wide")

# Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Стили для канбан-доски
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    /* Стиль карточки */
    .task-card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .task-title { font-weight: bold; font-size: 1.1em; color: #58a6ff; margin-bottom: 8px; }
    .task-meta { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
    /* Счетчик дней */
    .days-badge { 
        background: rgba(35, 134, 54, 0.2); 
        color: #3fb950; 
        padding: 2px 10px; 
        border-radius: 12px; 
        font-size: 0.8em; 
        float: right;
        border: 1px solid #238636;
    }
    h3 { border-bottom: 2px solid #30363d; padding-bottom: 10px; color: #f0f6fc; }
</style>
""", unsafe_allow_html=True)

# Функция расчета дней в работе
def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            start_date = start_val
        else:
            # Пытаемся распознать формат 06.10.2025
            start_date = datetime.strptime(str(start_val), "%d.%m.%Y").date()
        
        if isinstance(start_date, datetime):
            start_date = start_date.date()
            
        delta = (date.today() - start_date).days
        return max(0, delta)
    except:
        return 0

try:
    # Чтение данных из Google Таблицы
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🎯 Мониторинг задач (Kanban)")

    # Колонки канбана
    stages = ["Запланировано", "В работе", "Готово"]
    cols = st.columns(3)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"### {stage}")
            
            # Фильтруем по колонке "Статус"
            tasks = df[df['Статус'] == stage]
            
            for idx, row in tasks.iterrows():
                # Расчет дней только для тех, кто в работе
                days_html = ""
                if stage == "В работе":
                    d = get_days(row['Начало'])
                    days_html = f'<div class="days-badge">🔥 {d} дн.</div>'

                # Отрисовка карточки (ВАЖНО: unsafe_allow_html=True)
                st.markdown(f"""
                <div class="task-card">
                    {days_html}
                    <div class="task-title">{row['Задача']}</div>
                    <div class="task-meta">📍 {row['Раздел сайта']}</div>
                    <div class="task-meta">👤 {row['Ответственный']} | 📅 {row['Начало']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Кнопка изменения статуса (без передачи key в popover напрямую)
                with st.expander("⚙️ Изменить статус"):
                    new_status = st.selectbox(
                        "Переместить в:", 
                        stages, 
                        index=stages.index(stage), 
                        key=f"sel_{idx}"
                    )
                    if st.button("Подтвердить", key=f"btn_{idx}"):
                        if new_status != stage:
                            df.at[idx, 'Статус'] = new_status
                            conn.update(data=df)
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки: {e}")

# Боковая панель для новых задач
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("new_task_form", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Что сделать?")
        f_who = st.selectbox("Кто", ["Программист", "Дизайнер", "SEO", "Алина"])
        
        if st.form_submit_button("Создать задачу"):
            # Создаем новую строку по формату твоей таблицы (A-H)
            new_row = {
                "Раздел сайта": f_sec,
                "Задача": f_task,
                "Ответственный": f_who,
                "Начало": date.today().strftime("%d.%m.%Y"),
                "Дедлайн": "",
                "дней в работе": "",
                "Статус": "Запланировано"
            }
            # Совмещаем с существующим датафреймом
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()
