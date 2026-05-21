import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
import google.generativeai as genai

# Конфігурація 
st.set_page_config(page_title="Mail Retention Dashboard", layout="wide")

GEMINI_API_KEY = "реальний_ключ_АПІ"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Завантаження даних 
@st.cache_data
def load_data():
    df = pd.read_csv("Task_3/Tesk_Task___Mail_Retention.csv", sep=";")
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y")
    df["is_read"]    = df["read_ts"].notna().astype(int)
    df["is_clicked"] = df["click_ts"].notna().astype(int)
    df["is_buyer"]   = (df["buyer"] == "Buyer").astype(int)
    df["has_credits"]= df["not_free_credits"].notna().astype(int)
    return df

df = load_data()

# Навігація
st.sidebar.title("Mail Retention App")
page = st.sidebar.radio("Розділ", ["Моніторинг метрик", "A/B аналіз"])


# РОЗДІЛ 1 - МОНІТОРИНГ

if page == "Моніторинг метрик":
    st.title("Моніторинг email-метрик")

    # Фільтр дат
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Діапазон дат",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        mask = (df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])
        filtered = df[mask]
    else:
        filtered = df

    # Фільтр типу листа
    response_filter = st.sidebar.multiselect(
        "Тип листа",
        options=df["response"].unique().tolist(),
        default=df["response"].unique().tolist()
    )
    filtered = filtered[filtered["response"].isin(response_filter)]

    # KPI картки
    col1, col2, col3, col4 = st.columns(4)
    total = len(filtered)
    col1.metric("Відправлено", f"{total:,}")
    col2.metric("Read rate", f"{filtered['is_read'].mean()*100:.2f}%")
    col3.metric("Click rate", f"{filtered['is_clicked'].mean()*100:.2f}%")
    col4.metric("Credits rate", f"{filtered['has_credits'].mean()*100:.3f}%")

    st.divider()

    # Динаміка метрик
    daily = filtered.groupby("date").agg(
        sent=("user_id", "count"),
        read_rate=("is_read", "mean"),
        click_rate=("is_clicked", "mean"),
        credits_rate=("has_credits", "mean"),
    ).reset_index()
    daily[["read_rate","click_rate","credits_rate"]] *= 100

    metric_choice = st.selectbox(
        "Метрика для графіку",
        ["read_rate", "click_rate", "credits_rate"],
        format_func=lambda x: {"read_rate":"Read rate %","click_rate":"Click rate %","credits_rate":"Credits rate %"}[x]
    )

    # Аномалії - падіння >20% від середнього
    mean_val = daily[metric_choice].mean()
    daily["anomaly"] = daily[metric_choice] < mean_val * 0.8

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily[metric_choice],
        mode="lines+markers", name=metric_choice,
        line=dict(color="#4C72B0", width=2)
    ))
    fig.add_hline(
        y=mean_val, line_dash="dash",
        line_color="gray", annotation_text=f"Середнє: {mean_val:.2f}%"
    )
    anomalies = daily[daily["anomaly"]]
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["date"], y=anomalies[metric_choice],
            mode="markers", name="Аномалія",
            marker=dict(color="red", size=12, symbol="x")
        ))
    fig.update_layout(title=f"Динаміка {metric_choice}", height=400)
    st.plotly_chart(fig, use_container_width=True)

    if not anomalies.empty:
        st.warning(f"Виявлено {len(anomalies)} аномальних дні(в) - значення нижче 80% від середнього")

    # Розбивка по типу листа
    st.subheader("Метрики по типу листа")
    by_response = filtered.groupby("response").agg(
        sent=("user_id","count"),
        read_rate=("is_read","mean"),
        click_rate=("is_clicked","mean"),
    ).reset_index()
    by_response[["read_rate","click_rate"]] *= 100
    by_response = by_response.round(2)

    fig2 = px.bar(
        by_response, x="response",
        y=["read_rate","click_rate"],
        barmode="group",
        title="Read rate vs Click rate по типу листа",
        labels={"value":"%","response":"Тип листа"}
    )
    st.plotly_chart(fig2, use_container_width=True)

    # AI Summary
    st.subheader("AI Summary")
    if st.button("Згенерувати аналіз за обраний період"):
        with st.spinner("Gemini аналізує дані..."):
            summary_data = f"""
Період: {date_range[0]} - {date_range[1]}
Відправлено листів: {total:,}
Read rate: {filtered['is_read'].mean()*100:.2f}%
Click rate: {filtered['is_clicked'].mean()*100:.2f}%
Credits rate: {filtered['has_credits'].mean()*100:.3f}%
Buyer read rate: {filtered[filtered['is_buyer']==1]['is_read'].mean()*100:.2f}%
Not Buyer read rate: {filtered[filtered['is_buyer']==0]['is_read'].mean()*100:.2f}%
Аномальні дні: {len(anomalies)}
Найкращий тип листа по CTR: {by_response.loc[by_response['click_rate'].idxmax(), 'response']}
"""
            prompt = f"""
Ти - продуктовий аналітик email-каналу для dating-додатку.
Проаналізуй ці метрики і дай короткий інсайт (3-5 речень) що відбувається в каналі,
які є проблеми і що варто перевірити. Відповідай українською мовою.

Дані:
{summary_data}
"""
            response = model.generate_content(prompt)
            st.info(response.text)


# РОЗДІЛ 2 - A/B АНАЛІЗ

else:
    st.title("A/B тест аналіз")

    group_choice = st.selectbox(
        "Оберіть тест",
        ["group_1", "group_2", "group_3", "group_4"],
        format_func=lambda x: x.upper()
    )

    test_df  = df[df[group_choice] == "Test"]
    ctrl_df  = df[df[group_choice] == "Control"]

    # Таблиця метрик
    def get_metrics(subset):
        return {
            "Sent": len(subset),
            "Read rate %": round(subset["is_read"].mean()*100, 2),
            "Click rate %": round(subset["is_clicked"].mean()*100, 2),
            "Credits rate %": round(subset["has_credits"].mean()*100, 3),
            "Buyer share %": round(subset["is_buyer"].mean()*100, 2),
        }

    metrics_table = pd.DataFrame([
        {"Група": "Test",    **get_metrics(test_df)},
        {"Група": "Control", **get_metrics(ctrl_df)},
    ]).set_index("Група")

    st.subheader("Порівняння Test vs Control")
    st.dataframe(metrics_table, use_container_width=True)

    # Chi-square тести
    st.subheader("Статистична значущість (Chi-square)")

    def chi_test(metric_col):
        table = np.array([
            [test_df[metric_col].sum(),  len(test_df)  - test_df[metric_col].sum()],
            [ctrl_df[metric_col].sum(),  len(ctrl_df)  - ctrl_df[metric_col].sum()],
        ])
        chi2, p, _, _ = chi2_contingency(table)
        t_rate = test_df[metric_col].mean()*100
        c_rate = ctrl_df[metric_col].mean()*100
        lift   = ((t_rate - c_rate) / c_rate * 100) if c_rate > 0 else 0
        return {
            "Метрика": metric_col.replace("is_","").replace("has_","").replace("_"," ").title(),
            "Control %": round(c_rate, 2),
            "Test %": round(t_rate, 2),
            "Lift %": round(lift, 2),
            "p-value": round(p, 4),
            "Значущий": "✅" if p < 0.05 else "❌",
        }

    chi_results = pd.DataFrame([
        chi_test("is_read"),
        chi_test("is_clicked"),
        chi_test("has_credits"),
    ])
    st.dataframe(chi_results, use_container_width=True)

    # Візуалізація
    fig3 = px.bar(
        chi_results, x="Метрика", y=["Control %", "Test %"],
        barmode="group",
        title=f"{group_choice.upper()} - Test vs Control",
        color_discrete_map={"Test %":"#55A868","Control %":"#4C72B0"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Lift heatmap
    st.subheader("Lift % по метриках")
    lift_vals = chi_results[["Метрика","Lift %"]].set_index("Метрика").T
    fig4 = px.imshow(
        lift_vals,
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        title="Lift % (зелений = Test краще)",
        text_auto=".2f"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # AI Recommendation
    st.subheader("AI Рекомендація")
    if st.button("Отримати рекомендацію від Gemini"):
        with st.spinner("Gemini аналізує тест..."):
            test_summary = chi_results.to_string(index=False)
            prompt = f"""
Ти - продуктовий аналітик. Розглянь результати A/B тесту {group_choice.upper()} 
для email-каналу dating-додатку і дай конкретну рекомендацію:
запускати зміну на всіх юзерів чи ні, і чому.
Відповідай українською, коротко (3-4 речення).

Результати тесту:
{test_summary}
"""
            response = model.generate_content(prompt)
            st.success(response.text)