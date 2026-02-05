import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Task Manager Pro", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Улучшенный "Clean & Bold" дизайн
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; color: #1e1e1e; }
    
    /* Заголовки групп ответственных */
    .person-header {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0e1117;
        margin: 25px 0 15px 0;
        padding-left: 10px;
        border-left: 5px solid #58a6ff;
    }

    /* Карточка задачи */
    .task-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #e6e8eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .task-title { 
        font-size: 1.3rem; 
        font-weight: 700; 
        color: #1a1c1e;
        line-height: 1.3;
        margin-bottom: 10px;
    }
    
    .task-details {
        font-size: 1rem;
        color: #5f6368;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }

    .info-item { display: flex; align-items: center; gap: 5px; }

    /* Метки */
    .status-badge {
        font-size: 0.85rem;
        font-weight: 700;
        padding: 5px 15px;
        border-radius: 30px;
    }
    .badge-doing { background: #e7f5ff; color: #007bff; border: 1px solid #b3d7ff; }
    .badge-todo { background: #f8f9fa; color: #5f6368; border: 1px solid #dadce0; }
    .badge-done { background: #e6ffed; color: #2da44e; border: 1px solid #acf2bd; }
    
    .days-count { color: #d73a49; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        start_date = datetime.strptime(str(start_val), "%d.%m.%Y").date() if isinstance(start_val, str) else start_val
        return (date.today() - start_date).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🚀 Панель управления проектом")
    
    tabs = st.tabs(["🔥 В работе", "📅 План", "✅ Завершено"])
    statuses = ["В работе", "Запланировано", "Готово"]
    styles = {"В работе": "doing", "Запланировано": "todo", "Готово": "done"}

    for i, tab in enumerate(tabs):
        current_status = statuses[i]
        with tab:
            tasks = df[df['Статус'] == current_status]
            
            if tasks.empty:
                st.write("Пока здесь пусто")
            else:
                # Группируем задачи по ответственным
                for person in tasks['Ответственный'].unique():
                    st.markdown(f'<div class="person-header">👤 {person}</div>', unsafe_allow_html=True)
                    
                    person_tasks = tasks[tasks['Ответственный'] == person]
                    
                    for idx, row in person_tasks.iterrows():
                        days = get_days(row['Начало'])
                        time_text = f'<span class="days-count">🔥 {days} дн.</span>' if current_status == "В работе" else ""
                        
                        # Контейнер задачи
                        c1, c2 = st.columns([0.8, 0.2])
                        with c1:
                            st.markdown(f"""
                            <div class="task-card">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div class="task-title">{row['Задача']}</div>
                                    <div class="status-badge badge-{styles[current_status]}">{current_status}</div>
                                </div>
                                <div class="task-details">
                                    <div class="info-item">📍 {row['Раздел сайта']}</div>
                                    <div class="info-item">📅 Старт: {row['Начало']}</div>
                                    <div class="info-item">{time_text}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with c2:
                            st.write("") # Отступ
                            new_st = st.selectbox("Смена статуса", statuses, 
                                                index=statuses.index(current_status),
                                                key=f"st_{idx}")
                            if new_st != current_status:
                                df.at[idx, 'Статус'] = new_st
                                conn.update(data=df)
                                st.rerun()

except Exception as e:
    st.error(f"Ошибка при загрузке данных: {e}")

# Боковая панель для добавления
with st.sidebar:
    st.header("✨ Создать задачу")
    with st.form("add_new"):
        sec = st.text_input("Раздел сайта")
        tsk = st.text_area("Описание задачи")
        who = st.selectbox("Исполнитель", ["Программист", "Дизайнер", "SEO", "Алина"])
        if st.form_submit_button("Добавить в список"):
            new_data = {
                "Раздел сайта": sec, 
                "Задача": tsk, 
                "Ответственный": who, 
                "Начало": date.today().strftime("%d.%m.%Y"), 
                "Статус": "Запланировано"
            }
            # Совмещаем с таблицей
            upd = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
