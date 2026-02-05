import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Настройки (стандартный светлый вид)
st.set_page_config(page_title="Site Tracker", layout="wide")

# Подключение к таблице
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- Вход ---
if not st.session_state.auth:
    st.title("🔐 Вход")
    pwd = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if pwd == "12345":
            st.session_state.auth = True
            st.rerun()
else:
    # --- Основной экран ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    st.title("🚀 Мониторинг задач")

    # Вкладки: отдельно для профи (таблица) и для телефона (список)
    tab_table, tab_mobile = st.tabs(["💻 Таблица (ПК)", "📱 Мобильный вид"])

    with tab_table:
        st.info("Редактируйте ячейки и нажмите кнопку сохранения ниже")
        # Таблица в исходном виде
        edited_df = st.data_editor(
            df, 
            use_container_width=True, 
            num_rows="dynamic",
            key="desktop_editor"
        )
        if st.button("💾 Сохранить изменения в Google"):
            conn.update(spreadsheet=url, data=edited_df)
            st.success("Данные в Google Таблице обновлены!")
            st.rerun()

    with tab_mobile:
        st.subheader("Список задач")
        # Цвета статусов
        colors = {"Готово": "🟢", "В работе": "🟡", "На проверке": "🔵", "Запланировано": "⚪"}
        
        for i, r in df.iloc[::-1].iterrows():
            st_val = str(r.iloc[4]) if len(r) > 4 else "Запланировано"
            icon = colors.get(st_val, "🔘")
            
            # Простой и чистый вид карточки без лишнего CSS, который ломает цвета
            with st.container(border=True):
                st.markdown(f"**{icon} {st_val}**")
                st.markdown(f"**Раздел:** {r.iloc[0]}")
                st.markdown(f"**Задача:** {r.iloc[1]}")
                st.markdown(f"👤 {r.iloc[2]}")
                
                # Кнопка смены статуса
                with st.popover("Изменить статус"):
                    new_s = st.radio(
                        "Выберите статус", 
                        ["Запланировано", "В работе", "На проверке", "Готово"],
                        index=["Запланировано", "В работе", "На проверке", "Готово"].index(st_val) if st_val in ["Запланировано", "В работе", "На проверке", "Готово"] else 0,
                        key=f"status_{i}"
                    )
                    if st.button("Обновить", key=f"btn_{i}"):
                        df.iat[i, 4] = new_s
                        conn.update(spreadsheet=url, data=df)
                        st.rerun()

    # Форма добавления новой задачи (снизу)
    with st.expander("➕ Добавить новую задачу"):
        with st.form("new_task"):
            f_s = st.text_input("Раздел")
            f_t = st.text_area("Задача")
            f_w = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_st = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            if st.form_submit_button("Создать"):
                v = [f_s, f_t, f_w, "", f_st]
                while len(v) < len(df.columns): v.append("")
                new_row = pd.DataFrame([v], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=url, data=df)
                st.rerun()
