import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Tracker Pro", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Стиль
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 10px;
    }
    .task-title { font-weight: bold; font-size: 1.1em; color: #58a6ff; margin-bottom: 5px; }
    .task-meta { font-size: 0.85em; color: #8b949e; display: flex; align-items: center; gap: 5px; }
    .badge { 
        background: #238636; color: white; padding: 2px 8px; 
        border-radius: 5px; font-size: 0.8em; float: right; 
    }
    h3 { border-bottom: 2px solid #30363d; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

def calculate_days(start_val):
    try:
        if isinstance(start_val, datetime):
            start_date = start_val.date()
        else:
            start_date = datetime.strptime(str(start_val), "%d.%m.%Y").date()
        return (date.today() - start_date).days
    except:
        return 0

try:
    # Читаем данные
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🎯 Мониторинг задач (Kanban)")

    stages = ["Запланировано", "В работе", "Готово"]
    cols = st.columns(3)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"### {stage}")
            
            # Фильтруем по твоей колонке "Статус" (H)
            tasks = df[df['Статус'] == stage]
            
            for idx, row in tasks.iterrows():
                # Расчет дней для колонки "В работе"
                days_label = ""
                if stage == "В работе":
                    d = calculate_days(row['Начало'])
                    days_label = f'<span class="badge">🔥 {d} дн.</span>'

                # ВЫВОД КАРТОЧКИ (Важно: unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card">
                    {days_label}
                    <div class="task-title">{row['Задача']}</div>
                    <div class="task-meta">🌐 {row['Раздел сайта']}</div>
                    <div class="task-meta">👤 {row['Ответственный']} | 📅 {row['Начало']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Управление статусом
                with st.popover("⚙️ Изменить статус", key=f"pop_{idx}"):
                    new_status = st.radio("Куда:", stages, index=stages.index(stage), key=f"rad_{idx}")
                    if new_status != stage:
                        df.at[idx, 'Статус'] = new_status
                        conn.update(data=df)
                        st.rerun()

except Exception as e:
    st.error(f"Ошибка: {e}")

# Боковая панель
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("add_form", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Что сделать?")
        f_who = st.selectbox("Ответственный", ["Программист", "Дизайнер", "SEO", "Алина"])
        
        if st.form_submit_button("Добавить"):
            new_row = {
                "Раздел сайта": f_sec,
                "Задача": f_task,
                "Ответственный": f_who,
                "Начало": date.today().strftime("%d.%m.%Y"),
                "Дедлайн": "",
                "дней в работе": "",
                "Статус": "Запланировано"
            }
            # Убеждаемся, что все колонки из таблицы присутствуют
            for col in df.columns:
                if col not in new_row: new_row[col] = ""
                
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()
