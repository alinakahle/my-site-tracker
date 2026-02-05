import streamlit as st
import pandas as pd

# 1. Настройка страницы
st.set_page_config(page_title="Site Manager Pro", layout="wide")

# 2. ПРЯМАЯ ССЫЛКА (Важно: замени /edit на /export?format=csv)
# Твоя ссылка: https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit
# Превращаем её в ссылку для прямого скачивания данных:
SHEET_ID = "1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 3. Стильный Канбан CSS
st.markdown("""
    <style>
    .stApp { background-color: #0f1116; color: #ffffff; }
    .kanban-column { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 15px; min-height: 70vh; }
    .column-header { text-align: center; font-weight: 800; border-bottom: 2px solid; margin-bottom: 20px; padding-bottom: 10px; }
    .task-card { background: #1c1e26; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 5px solid; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .task-title { font-weight: 700; color: #fff; margin-bottom: 5px; }
    .task-meta { color: #8b949e; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# 4. Загрузка данных (Простой способ без секретов)
@st.cache_data(ttl=10) # Обновление каждые 10 секунд
def load_data():
    return pd.read_csv(CSV_URL).dropna(how="all").fillna("")

try:
    df = load_data()
    
    st.title("🎯 Kanban Board")

    # Разделяем на 3 колонки
    col1, col2, col3 = st.columns(3)

    # Определяем этапы (проверь, чтобы названия в таблице были такими же!)
    stages = [
        {"name": "Запланировано", "color": "#6c757d", "column": col1},
        {"name": "В работе", "color": "#ffc107", "column": col2},
        {"name": "Готово", "color": "#28a745", "column": col3}
    ]

    for stage in stages:
        with stage["column"]:
            st.markdown(f'<div class="column-header" style="border-color: {stage["color"]}; color: {stage["color"]};">{stage["name"].upper()}</div>', unsafe_allow_html=True)
            
            # Фильтруем (Статус должен быть в 5-й колонке по счету)
            # Если в таблице колонки называются иначе, поменяй df.columns[4]
            tasks = df[df[df.columns[4]] == stage["name"]]
            
            for idx, row in tasks.iterrows():
                st.markdown(f"""
                    <div class="task-card" style="border-left-color: {stage['color']};">
                        <div class="task-title">{row.iloc[1]}</div>
                        <div class="task-meta">📍 {row.iloc[0]}</div>
                        <div style="color: #58a6ff; font-weight: 600; font-size: 0.85em; margin-top: 5px;">👤 {row.iloc[2]}</div>
                    </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error("Пока не удалось подгрузить данные. Проверь, что в Google Таблице включен доступ 'Все, у кого есть ссылка - Редактор'.")
    st.info("Также убедись, что твоя таблица не пустая.")

st.sidebar.info("Этот режим работает только на просмотр, так как мы используем упрощенный доступ без паролей и ключей.")
