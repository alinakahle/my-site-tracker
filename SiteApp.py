import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Site Tracker Pro", layout="wide")

# Подключение
conn = st.connection("gsheets", type=GSheetsConnection)

# Стилизация (улучшенная)
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .task-card { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 12px;
        min-height: 110px;
    }
    .task-title { font-weight: bold; font-size: 1.1em; color: #58a6ff; margin-bottom: 5px; line-height: 1.2; }
    .task-meta { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
    .badge { 
        background: rgba(56, 139, 253, 0.1); color: #58a6ff; 
        padding: 2px 8px; border-radius: 6px; font-size: 0.8em; 
        float: right; border: 1px solid rgba(56, 139, 253, 0.3);
    }
    .badge-done { 
        background: rgba(45, 196, 77, 0.1); color: #7ee787; 
        border: 1px solid rgba(45, 196, 77, 0.3);
    }
    h3 { border-bottom: 2px solid #30363d; padding-bottom: 10px; color: #f0f6fc; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

def calculate_days(start_val):
    try:
        # Пытаемся обработать разные форматы дат
        if isinstance(start_val, (date, datetime)):
            start_date = start_val.date() if isinstance(start_val, datetime) else start_val
        else:
            start_date = datetime.strptime(str(start_val).strip(), "%d.%m.%Y").date()
        
        delta = (date.today() - start_date).days
        return max(0, delta)
    except:
        return None

try:
    # Чтение данных
    df = conn.read(ttl=0).dropna(how="all").fillna("")
    
    st.title("🎯 Мониторинг задач (Kanban)")

    stages = ["Запланировано", "В работе", "Готово"]
    cols = st.columns(3)

    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"### {stage}")
            
            # Фильтруем задачи
            tasks = df[df['Статус'] == stage]
            
            for idx, row in tasks.iterrows():
                # Логика бейджа времени
                time_badge = ""
                days = calculate_days(row['Начало'])
                
                if stage == "В работе" and days is not None:
                    time_badge = f'<span class="badge">🔥 {days} дн. в работе</span>'
                elif stage == "Готово" and days is not None:
                    time_badge = f'<span class="badge badge-done">✅ за {days} дн.</span>'
                
                # РЕНДЕРИНГ (теперь абсолютно одинаковый для всех стадий)
                st.markdown(f"""
                <div class="task-card">
                    {time_badge}
                    <div class="task-title">{row['Задача']}</div>
                    <div class="task-meta">📍 {row['Раздел сайта']}</div>
                    <div class="task-meta">👤 {row['Ответственный']} | 📅 {row['Начало']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Кнопка смены статуса
                with st.expander("⚙️ Изменить статус"):
                    new_status = st.selectbox(
                        "Переместить в:", 
                        stages, 
                        index=stages.index(stage), 
                        key=f"status_{idx}"
                    )
                    if st.button("Сохранить", key=f"save_{idx}"):
                        if new_status != stage:
                            df.at[idx, 'Статус'] = new_status
                            conn.update(data=df)
                            st.rerun()

except Exception as e:
    st.error(f"Ошибка данных: {e}")

# Боковая панель
with st.sidebar:
    st.header("✨ Новая задача")
    with st.form("new_task_form", clear_on_submit=True):
        f_sec = st.text_input("Раздел сайта")
        f_task = st.text_area("Задача")
        f_who = st.selectbox("Ответственный", ["Программист", "Дизайнер", "SEO", "Алина"])
        
        if st.form_submit_button("Создать"):
            new_row = {
                "Раздел сайта": f_sec,
                "Задача": f_task,
                "Ответственный": f_who,
                "Начало": date.today().strftime("%d.%m.%Y"),
                "Дедлайн": "",
                "дней в работе": "",
                "Статус": "Запланировано"
            }
            updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            conn.update(data=updated_df)
            st.rerun()
