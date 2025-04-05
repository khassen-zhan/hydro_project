import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import math

st.set_page_config(page_title="Гидромодуль – расчёт и прогноз", layout="wide")

st.markdown("# 🌿 **Информационная система расчёта гидромодуля**")
st.markdown("---")

# === Справочники ===
kc_values = {
    "Пшеница": [0.3, 1.15, 0.35],
    "Кукуруза": [0.4, 1.20, 0.6],
    "Хлопок": [0.4, 1.25, 0.6],
    "Рис": [1.1, 1.20, 0.9],
    "Картофель": [0.5, 1.15, 0.8],
    "Томаты": [0.6, 1.15, 0.8],
    "Огурцы": [0.6, 1.05, 0.8],
    "Арбуз": [0.5, 0.85, 0.65],
    "Дыня": [0.4, 0.85, 0.65],
    "Соя": [0.4, 1.15, 0.5],
    "Люцерна": [0.4, 1.10, 0.9],
    "Лук": [0.7, 1.10, 0.85],
    "Подсолнечник": [0.3, 1.15, 0.45],
    "Сахарная свекла": [0.4, 1.20, 0.8],
    "Виноград": [0.3, 0.80, 0.5]
}
kpd_dict = {
    "Поверхностное": 0.6,
    "Дождевание": 0.8,
    "Капельное": 0.95
}
if "history" not in st.session_state:
    st.session_state.history = []

# === Ряд с двумя формами ===
col_form1, col_form2 = st.columns(2)

with col_form1:
    with st.form("form_input"):
        st.subheader("📌 **Исходные данные**")
        culture = st.selectbox("**Культура**", list(kc_values.keys()))
        phase = st.radio("**Фаза роста**", ["Начальная", "Средняя", "Поздняя"])
        irrigation_type = st.selectbox("**Тип орошения**", list(kpd_dict.keys()))
        start_date = st.date_input("**Начало прогноза**", value=datetime.date.today())
        days_forecast = st.slider("**Дней в прогнозе**", 1, 30, 3)
        submitted = st.form_submit_button("Применить")

if "form_values" not in st.session_state or submitted:
    st.session_state.form_values = {
        "culture": culture,
        "phase": phase,
        "irrigation_type": irrigation_type,
        "start_date": start_date,
        "days_forecast": days_forecast
    }

form_data = st.session_state.form_values
culture = form_data["culture"]
phase = form_data["phase"]
irrigation_type = form_data["irrigation_type"]
start_date = form_data["start_date"]
days_forecast = form_data["days_forecast"]

kc = kc_values[culture][{"Начальная": 0, "Средняя": 1, "Поздняя": 2}[phase]]
kpd = kpd_dict[irrigation_type]

# === Вторая форма: География и климат ===
with col_form2:
    with st.form("form_climate"):
        st.subheader("🌍 **География и климат**")
        col_geo = st.columns(2)
        latitude = col_geo[0].number_input("**Широта**", value=42.616328, format="%.6f")
        longitude = col_geo[1].number_input("**Долгота**", value=69.549866, format="%.6f")

        st.markdown("### 📊 **ET₀ и осадки по дням**")
        st.markdown("ℹ️ **Формула:** ET₀ = 3.5 + 2.0 × |sin(широта)| × sin(2π × (DOY − 80) / 365)")

        date_list = [start_date + datetime.timedelta(days=i) for i in range(days_forecast)]
        et0_list = []
        precip_list = []

        for i in range(days_forecast):
            day_of_year = date_list[i].timetuple().tm_yday
            et0 = 3.5 + 2.0 * abs(math.sin(math.radians(latitude))) * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            et0 = round(et0, 2)
            et0_list.append(et0)

            row = st.columns([1, 1, 1.5, 2])
            row[0].markdown(f"**ET₀:** {et0} мм")
            row[1].markdown("**Осадки:**")
            row[2].markdown(f"**{date_list[i].strftime('%d.%m.%Y')}**")
            precip = row[3].number_input("Осадки", key=f"prec_{i}", value=0.0, step=0.1, label_visibility="collapsed")
            precip_list.append(precip)

        st.form_submit_button("Рассчитать")

# === Расчёт гидромодуля ===
q_values = [max((et0_list[i] * kc - precip_list[i]) / kpd, 0) for i in range(days_forecast)]
avg_q = round(np.mean(q_values), 2)

# === График ===
st.markdown("### 📈 **Прогноз водоподачи**")
st.success(f"📌 **Средний гидромодуль: {avg_q} мм/день**")
st.markdown("**Формула:** q = (ET₀ × Kc - осадки) / КПД")

fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(date_list, q_values, marker='o', linestyle='-', color='teal')

# Уменьшенные шрифты, без подписей
ax.set_xlabel("Дата", fontsize=9)
ax.set_ylabel("Гидромодуль, мм", fontsize=9)
ax.set_title("Динамика водоподачи", fontsize=10)
ax.tick_params(axis='both', labelsize=8)
ax.tick_params(axis='x', rotation=30)
ax.set_xticks(date_list)
ax.set_xticklabels([d.strftime("%d.%m") for d in date_list], rotation=30, ha='right')
fig.tight_layout()
st.pyplot(fig)

# === Экспорт и история ===
record = {
    "Дата": datetime.date.today().isoformat(),
    "Культура": culture,
    "Фаза": phase,
    "Тип орошения": irrigation_type,
    "Kc": kc,
    "КПД": kpd,
    "Широта": latitude,
    "Долгота": longitude,
    "Средний гидромодуль": avg_q
}
st.session_state.history.append(record)

df_result = pd.DataFrame({
    "Дата": date_list,
    "ET₀": et0_list,
    "Осадки": precip_list,
    "Гидромодуль": q_values
})

st.download_button(
    label="📥 Скачать прогноз в Excel",
    data=df_result.to_csv(index=False).encode('utf-8-sig'),
    file_name="гидромодуль_прогноз.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("### 📜 **История расчётов за сессию**")
df_history = pd.DataFrame(st.session_state.history)
st.dataframe(df_history, use_container_width=True)

st.markdown("---")
st.caption("Разработано для дипломного проекта по гидромодулю")
