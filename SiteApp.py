import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Task Manager Pro", layout="wide")

# Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Финальный "Clean UI" дизайн
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #1e1e1e; }
    
    /* Карточка на всю ширину */
    .task-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 12px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
    }
    
    .task-title { 
        font-size: 1.5rem; 
        font-weight: 700; 
        color: #1a1c1e;
        flex: 1;
        margin-right: 20px;
    }
    
    .task-footer {
        font-size: 1.1rem;
        color: #606770;
        display: flex;
        gap: 25px;
        align-items: center;
    }

    /* Стили для кастомных кнопок статуса внутри popover */
    div[data-testid="stPopover"] > button {
        border-radius: 40px !important;
        padding: 4px 16px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
    }
    
    .days-badge { color: #d73a49; font-weight: 800; font-size: 1.1rem; }
    
    /* Убираем лишние отступы Streamlit */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        if isinstance(start_val, (date, datetime)):
            start_date = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            start_date = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        return (date.today() - start_date).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🚀 Панель управления проектом")
    
    # Список сотрудников (всегда отображаются)
    all_staff = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    
    tabs = st.tabs(["🔥 В работе", "📅 План", "✅ Завершено"])
    statuses = ["В работе", "Запланировано", "Готово"]
    
    # Цветовая схема для кнопок статуса
    status_colors = {
        "В работе": "primary", 
        "Запланировано": "secondary", 
        "Готово": "success"
    }

    for i, tab in enumerate(tabs):
        current_status = statuses[i]
        with tab:
            # Горизонтальный переключатель ответственных
            selected_person = st.segmented_control(
                "Кто выполняет:", 
                options=all_staff, 
                default="Все",
                key=f"filter_{current_status}"
            )
            
            st.write("") # Пробел
            
            # Фильтрация
            tasks = df[df['Статус'] == current_status]
            if selected_person != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_person]
            
            if tasks.empty:
                st.info(f"У сотрудника {selected_person} сейчас нет задач в этом разделе")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    
                    # Создаем контейнер карточки
                    with st.container():
                        st.markdown(f'<div class="task-card">', unsafe_allow_html=True)
                        
                        # Верхняя часть: Заголовок и кнопка смены статуса
                        header_col, status_col = st.columns([0.8, 0.2])
                        
                        with header_col:
                            st.markdown(f'<div class="task-title">{row["Задача"]}</div>', unsafe_allow_html=True)
                        
                        with status_col:
                            # Поповер вместо выпадающего списка справа
                            with st.popover(current_status, use_container_width=True):
                                st.write("📝 Сменить этап:")
                                new_st = st.radio(
                                    "Переместить в:", 
                                    statuses, 
                                    index=statuses.index(current_status),
                                    key=f"move_{idx}",
                                    label_visibility="collapsed"
                                )
                                if new_st != current_status:
                                    df.at[idx, 'Статус'] = new_st
                                    conn.update(data=df)
                                    st.rerun()
                        
                        # Нижняя часть: Мета-данные
                        time_html = f'<span class="days-badge">🔥 {days} дн. в работе</span>' if current_status == "В работе" else f"📅 Старт: {row['Начало']}"
                        
                        st.markdown(f"""
                            <div class="task-footer">
                                <div>👤 <b>{row['Ответственный']}</b></div>
                                <div>📍 {row['Раздел сайта']}</div>
                                <div>{time_html}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("") # Для визуального разделения карточек

except Exception as e:
    st.error(f"Не удалось обновить данные: {e}")

# Боковая панель для создания задач
with st.sidebar:
    st.header("✨ Создать задачу")
    with st.form("new_task_form", clear_on_submit=True):
        sec = st.text_input("Раздел сайта")
        tsk = st.text_area("Что нужно сделать?")
        who = st.selectbox("Ответственный", ['Программист', 'Дизайнер', 'SEO', 'Алина'])
        
        if st.form_submit_button("Добавить в работу"):
            new_row = {
                "Раздел сайта": sec, 
                "Задача": tsk, 
                "Ответственный": who, 
                "Начало": date.today().strftime("%d.%m.%Y"), 
                "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
