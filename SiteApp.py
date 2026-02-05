import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Конфигурация
st.set_page_config(page_title="Site Manager", layout="wide")

# 2. Стили (Mobile vs Desktop)
st.markdown("""
<style>
.task-card {
    background-color: #1A1C24;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border-left: 8px solid #ddd;
}
.task-text { color: white; font-size: 16px; font-weight: 700; margin: 5px 0; }
.section-title { color: #8B949E; font-size: 11px; font-weight: bold; }
.status-badge {
    padding: 3px 10px; border-radius: 8px; font-size: 10px;
    font-weight: 900; float: right; color: black;
}
@media (max-width: 800px) {
    .stApp { background-color: #0E1117 !important; color: white !important; }
}
@media (min-width: 801px) {
    .stApp { background-color: white !important; color: black !important; }
}
</style>
""", unsafe_allow_html=True)

# 3. Данные
url = "https://docs.google.com/spreadsheets/d/1-Lj3g5ICKsELa1HBZNi2mdZ39WNkHNvFye0vJj3G06Y/edit"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Вход")
    p_v = st.text_input("Пароль:", type="password")
    if st.button("Войти"):
        if p_v == "12345":
            st.session_state.auth = True
            st.rerun()
else:
    # Соединение
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0).dropna(how="all").fillna("")

    st.title("🚀 МОНИТОРИНГ")

    with st.expander("➕ НОВАЯ ЗАДАЧА"):
        with st.form("add_task", clear_on_submit=True):
            f_s = st.text_input("Раздел")
            f_t = st.text_area("Задача")
            f_w = st.selectbox("Кто", ["Алина", "Программист", "Дизайнер", "SEO", "Офис"])
            f_st = st.selectbox("Статус", ["Запланировано", "В работе", "На проверке", "Готово"])
            if st.form_submit_button("СОХРАНИТЬ"):
                v = [f_s, f_t, f_w, "", f_st]
                while len(v) < len(df.columns): v.append("")
                new_row = pd.DataFrame([v], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(spreadsheet=url, data=df)
                st.success("ОК!")
                st.rerun()

    st.divider()

    colors = {"Готово": "#39FF14", "В работе": "#FFD700", "На проверке": "#00D4FF", "Запланировано": "#8E8E8E"}
    m_tab, d_tab = st.tabs(["📱 Мобильный вид", "💻 Таблица"])

    with m_tab:
        for i, r in df.iloc[::-1].iterrows():
            st_val = str(r.iloc[4]) if len(r) > 4 else "Запланировано"
            c_c = colors.get(st_val, "#FFFFFF")
            st.markdown(f"""
            <div class="task-card" style="border-left-color: {c_c}">
                <span class="status-badge" style="background-color: {c_c};">{st_val}</span>
                <div class="section-title">📍 {r.iloc[0]}</div>
                <div class="task-text">{r.iloc[1]}</div>
                <div style="color:#58A6FF; font-size:13px;">👤 {r.iloc[2]}</div>
            </div>
            """, unsafe_allow_html=True)
            with st.popover(f"Статус #{i}"):
                opt = ["Запланировано", "В работе", "На проверке", "Готово"]
                cur_idx = opt.index(st_val) if st_val in opt else 0
                new_v = st.radio("Статус:", opt, index=cur_idx, key=f"r{i}")
                if st.button("Обновить", key=f"b{i}"):
                    df.iat[i, 4] = new_v
                    conn.update(spreadsheet=url, data=df)
                    st.rerun()

    with d_tab:
        ed_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="d_ed")
        if st.button("💾 СОХРАНИТЬ ТАБЛИЦУ"):
            conn.update(spreadsheet=url, data=ed_df)
            st.success("Обновлено!")
