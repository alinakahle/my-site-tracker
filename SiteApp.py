import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Task Manager Pro", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Дизайн "Premium Management"
st.markdown("""
<style>
    .stApp { background-color: #f4f7f9; color: #1e1e1e; }
    
    /* Стили для карточки */
    .task-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    .task-title { 
        font-size: 1.4rem; 
        font-weight: 700; 
        color: #1a1c1e;
        margin-bottom: 12px;
    }
    
    .task-details {
        font-size: 1.1rem;
        color: #606770;
        display: flex;
        gap: 30px;
        flex-wrap: wrap;
    }

    /* Бейджи */
    .status-badge {
        font-size: 0.9rem;
        font-weight: 700;
        padding: 6px 18px;
        border-radius: 40px;
        text-transform: uppercase;
    }
    .badge-doing { background: #eef6ff; color: #007bff; border: 1px solid #cce5ff; }
    .badge-todo { background: #f8f9fa; color: #5f6368; border: 1px solid #dee2e6; }
    .badge-done { background: #eafff0; color: #2da44e; border: 1px solid #bef5cb; }
    
    .days-count { color: #d73a49; font-weight: 800; font-size: 1.1rem; }
    
    /* Убираем лишние отступы у колонок */
    [data-testid="column"] { display: flex; align-items: center; }
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
    
    # Список всех ответственных (фиксированный, чтобы никто не пропадал)
    all_staff = ['Все', 'Программист', 'Дизайнер', 'SEO', 'Алина']
    
    tabs = st.tabs(["🔥 В работе", "📅 План", "✅ Завершено"])
    statuses = ["В работе", "Запланировано", "Готово"]
    styles = {"В работе": "doing", "Запланировано": "todo", "Готово": "done"}

    for i, tab in enumerate(tabs):
        current_status = statuses[i]
        with tab:
            # 1. Горизонтальное меню выбора ответственного
            selected_person = st.segmented_control(
                "Кто выполняет:", 
                options=all_staff, 
                default="Все",
                key=f"filter_{current_status}"
            )
            
            st.write("---") # Разделитель
            
            # Фильтруем данные
            tasks = df[df['Статус'] == current_status]
            if selected_person != "Все":
                tasks = tasks[tasks['Ответственный'] == selected_person]
            
            if tasks.empty:
                st.info(f"У сотрудника {selected_person} нет задач в этом разделе")
            else:
                for idx, row in tasks.iterrows():
                    days = get_days(row['Начало'])
                    time_text = f'<span class="days-count">🔥 {days} дн. в работе</span>' if current_status == "В работе" else ""
                    
                    # Макет карточки
                    col_info, col_action = st.columns([0.75, 0.25])
                    
                    with col_info:
                        st.markdown(f"""
                        <div class="task-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                                <div class="task-title">{row['Задача']}</div>
                                <div class="status-badge badge-{styles[current_status]}">{current_status}</div>
                            </div>
                            <div class="task-details">
                                <div>👤 <b>{row['Ответственный']}</b></div>
                                <div>📍 {row['Раздел сайта']}</div>
                                <div>📅 {row['Начало']}</div>
                                <div>{time_text}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_action:
                        # Селектор смены статуса прямо в строке
                        new_st = st.selectbox("Переместить:", statuses, 
                                            index=statuses.index(current_status),
                                            key=f"move_{idx}")
                        if new_st != current_status:
                            df.at[idx, 'Status'] = new_st # Обновляем статус
                            conn.update(data=df)
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка загрузки: {e}")

# Боковая панель
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("add_task_form", clear_on_submit=True):
        sec = st.text_input("Раздел сайта")
        tsk = st.text_area("Что сделать?")
        who = st.selectbox("Ответственный", ['Программист', 'Дизайнер', 'SEO', 'Алина'])
        if st.form_submit_button("Создать задачу"):
            new_row = {
                "Раздел сайта": sec, "Задача": tsk, "Ответственный": who, 
                "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"
            }
            upd = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=upd)
            st.rerun()
