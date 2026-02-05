import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Task Manager", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Современный лаконичный стиль
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #212529; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    
    /* Стили строк списка */
    .task-row {
        background: white;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #eee;
        transition: all 0.2s;
    }
    .task-row:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #d0d0d0; }
    
    .task-main { flex-grow: 1; }
    .task-title { font-weight: 600; font-size: 1.05rem; color: #1a1c1e; }
    .task-sub { font-size: 0.85rem; color: #6c757d; margin-top: 2px; }
    
    /* Индикаторы */
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .status-todo { background: #e9ecef; color: #495057; }
    .status-doing { background: #e7f5ff; color: #007bff; }
    .status-done { background: #ebfbee; color: #40c057; }
    
    .person-tag { 
        background: #f1f3f5; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-weight: 500; 
        color: #495057;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

def get_days(start_val):
    try:
        start_date = datetime.strptime(str(start_val), "%d.%m.%Y").date() if isinstance(start_val, str) else start_val
        return (date.today() - start_date).days
    except: return 0

try:
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("📋 Управление задачами")
    
    # Группировка по статусам
    tabs = st.tabs(["⚡ В работе", "⏳ Запланировано", "✅ Готово"])
    status_map = {"В работе": tabs[0], "Запланировано": tabs[1], "Готово": tabs[2]}
    styles = {"В работе": "doing", "Запланировано": "todo", "Готово": "done"}

    for status_name, tab in status_map.items():
        with tab:
            tasks = df[df['Статус'] == status_name]
            if tasks.empty:
                st.info(f"Задач в статусе '{status_name}' нет")
            
            for idx, row in tasks.iterrows():
                days = get_days(row['Начало'])
                time_info = f" • 🔥 {days} дн." if status_name == "В работе" else ""
                
                # Чистый вывод строки задачи
                col_text, col_action = st.columns([0.8, 0.2])
                
                with col_text:
                    st.markdown(f"""
                    <div class="task-row">
                        <div class="task-main">
                            <div class="task-title">{row['Задача']}</div>
                            <div class="task-sub">
                                📍 {row['Раздел сайта']} | 📅 {row['Начало']}{time_info}
                                <span class="person-tag">👤 {row['Ответственный']}</span>
                            </div>
                        </div>
                        <div class="status-pill status-{styles[status_name]}">{status_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_action:
                    # Удобное управление
                    next_status = st.selectbox("Сменить на:", ["Запланировано", "В работе", "Готово"], 
                                             index=["Запланировано", "В работе", "Готово"].index(status_name),
                                             key=f"sel_{idx}")
                    if next_status != status_name:
                        df.at[idx, 'Статус'] = next_status
                        conn.update(data=df)
                        st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")

# Боковая панель
with st.sidebar:
    st.header("➕ Новая задача")
    with st.form("add"):
        s = st.text_input("Раздел")
        t = st.text_input("Задача")
        p = st.selectbox("Кто", ["Программист", "Дизайнер", "SEO", "Алина"])
        if st.form_submit_button("Создать"):
            new = {"Раздел сайта": s, "Задача": t, "Ответственный": p, "Начало": date.today().strftime("%d.%m.%Y"), "Статус": "Запланировано"}
            updated = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            conn.update(data=updated)
            st.rerun()
