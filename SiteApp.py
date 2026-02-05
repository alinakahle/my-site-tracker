import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройка страницы
st.set_page_config(page_title="Site Manager Kanban", layout="wide")

# 2. Подключение к Google Sheets через секреты
# Название соединения должно совпадать с тем, что в Secrets: [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Стиль "Премиум Канбан"
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    h3 { color: #58a6ff !important; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
    .task-card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 8px; 
        padding: 15px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .task-card:hover { border-color: #58a6ff; }
    .task-title { font-weight: bold; font-size: 1.1em; color: #f0f6fc; }
    .task-desc { font-size: 0.9em; color: #8b949e; margin: 5px 0; }
    .task-who { font-size: 0.8em; color: #1f6feb; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 4. Загрузка данных (Лист должен называться "Tasks")
try:
    # Очищаем кэш принудительно, чтобы увидеть изменения
    df = conn.read(worksheet="Tasks", ttl=0).dropna(how="all").fillna("")
    
    st.title("🎯 Мониторинг задач (Kanban)")

    # Создаем 3 колонки для Канбана
    stages = ["Запланировано", "В работе", "Готово"]
    cols = st.columns(3)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"### {stage}")
            
            # Фильтруем задачи (Статус в 5-й колонке, индекс 4)
            # Если у тебя статус в другой колонке, поменяй цифру 4 ниже
            tasks = df[df.iloc[:, 4] == stage]
            
            for idx, row in tasks.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="task-card">
                        <div class="task-title">{row.iloc[1]}</div>
                        <div class="task-desc">📍 {row.iloc[0]}</div>
                        <div class="task-who">👤 {row.iloc[2]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Кнопка смены статуса
                    with st.popover("🚀 Сменить этап"):
                        new_status = st.radio(
                            "Переместить в:", 
                            stages, 
                            index=stages.index(stage),
                            key=f"move_{idx}"
                        )
                        if new_status != stage:
                            df.iat[idx, 4] = new_status
                            conn.update(worksheet="Tasks", data=df)
                            st.success("Перемещено!")
                            st.rerun()

    # --- БОКОВАЯ ПАНЕЛЬ ДЛЯ НОВЫХ ЗАДАЧ ---
    with st.sidebar:
        st.header("✨ Создать задачу")
        with st.form("add_task_form", clear_on_submit=True):
            new_sec = st.text_input("Раздел сайта")
            new_task = st.text_area("Что сделать?")
            new_who = st.selectbox("Ответственный", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            
            if st.form_submit_button("Добавить в Канбан"):
                # Создаем строку по формату таблицы (5 колонок)
                new_row = [new_sec, new_task, new_who, "", "Запланировано"]
                
                # Добавляем пустые ячейки, если колонок в Google больше
                while len(new_row) < len(df.columns):
                    new_row.append("")
                
                new_df = pd.DataFrame([new_row], columns=df.columns)
                updated_df = pd.concat([df, new_df], ignore_index=True)
                
                conn.update(worksheet="Tasks", data=updated_df)
                st.sidebar.success("Задача добавлена!")
                st.rerun()

except Exception as e:
    st.error(f"Ошибка связи с таблицей: {e}")
    st.info("Проверьте, что в Google Таблице есть лист с названием 'Tasks' и у сервисного аккаунта есть доступ 'Редактор'.")
