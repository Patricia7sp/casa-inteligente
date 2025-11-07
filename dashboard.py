"""
Dashboard Streamlit para Casa Inteligente
"""

import os
import json
import time
import math
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# Configuração da página
st.set_page_config(
    page_title="Casa Inteligente Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado para tema escuro elegante
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-image: 
            url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80'),
            linear-gradient(135deg, rgba(15,12,41,0.95) 0%, rgba(48,43,99,0.95) 50%, rgba(36,36,62,0.95) 100%);
        background-blend-mode: overlay;
        background-size: cover;
        background-attachment: fixed;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .stMetric label {
        color: #a0aec0 !important;
        font-size: 0.9rem;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem;
        font-weight: 600;
    }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px 20px;
        color: #a0aec0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Configuração da API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Título da aplicação
st.markdown(
    """
<div style='text-align: center; padding: 20px;'>
    <h1 style='font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
               font-weight: 800; margin-bottom: 10px;'>
        🏠 Casa Inteligente
    </h1>
    <p style='color: #a0aec0; font-size: 1.1rem;'>Monitoramento Inteligente de Energia</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar com informações e controles
st.sidebar.markdown("## 📊 Controles")

# Refresh automático
auto_refresh = st.sidebar.checkbox("Auto Refresh (10s)", value=True)
refresh_interval = 10 if auto_refresh else 0

# Seletor de período
time_range_options = {
    "Últimas 24h": 1,
    "Últimos 7 dias": 7,
    "Últimos 30 dias": 30,
    "Últimos 90 dias": 90,
}
time_range_label = st.sidebar.selectbox(
    "Período de Análise", list(time_range_options.keys()), index=2
)

if st.sidebar.button("🔄 Aplicar Filtro", type="primary"):
    st.session_state.time_range_days = time_range_options[time_range_label]
    st.rerun()

if "time_range_days" not in st.session_state:
    st.session_state.time_range_days = time_range_options[time_range_label]

time_range_days = st.session_state.time_range_days


# Funções utilitárias
def get_api_data(endpoint):
    """Obter dados da API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter dados: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None


def format_power(value):
    """Formatar valor de potência"""
    if value >= 1000:
        return f"{value/1000:.2f} kW"
    else:
        return f"{value:.1f} W"


def format_energy(value):
    """Formatar valor de energia"""
    return f"{value:.3f} kWh"


def format_cost(value):
    """Formatar valor de custo"""
    return f"R$ {value:.2f}"


def load_smartlife_data() -> dict:
    smartlife_file = Path("data/smartlife/latest.json")
    if smartlife_file.exists():
        try:
            with open(smartlife_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Arquivo SmartLife inválido. Execute o polling novamente.")
    return {}


def calculate_tariff_values(energy_kwh: float, tariff_per_kwh: float = 0.862) -> float:
    return round(energy_kwh * tariff_per_kwh, 2)


def build_summary_cards_tapo(realtime_data: dict):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="⚡ Potência Total",
            value=format_power(realtime_data.get("total_current_power_watts", 0)),
        )

    with col2:
        st.metric(
            label="🔌 Dispositivos Ativos",
            value=realtime_data.get("active_devices", 0),
        )

    with col3:
        status_icon = "🟢" if realtime_data.get("devices") else "🔴"
        st.metric(label="📈 Status Sistema", value=f"{status_icon} Ativo")

    with col4:
        last_update = realtime_data.get("timestamp", datetime.now())
        time_diff = datetime.now() - pd.to_datetime(last_update)
        st.metric(
            label="🕐 Última Atualização",
            value=f"{max(time_diff.seconds // 60, 0)} min atrás",
        )


def render_tapo_dashboard(realtime_data: dict):
    if not realtime_data or "devices" not in realtime_data:
        st.warning(
            "⚠️ Sem dados recentes dos dispositivos Tapo. Verifique a conexão com a API."
        )
        with st.expander("🔍 Diagnóstico"):
            st.code(f"API URL: {API_BASE_URL}/status/realtime")
            st.info(
                "Certifique-se de que a API está rodando e o banco de dados está acessível."
            )
        return

    devices_df = pd.DataFrame(realtime_data["devices"])
    if devices_df.empty:
        st.info("Nenhum dispositivo Tapo ativo no momento.")
        return

    build_summary_cards_tapo(realtime_data)

    # Adicionar gráficos históricos
    st.markdown("### 📊 Histórico de Consumo")

    if len(devices_df) > 0:
        selected_device_id = st.selectbox(
            "Selecione um dispositivo para ver histórico",
            options=devices_df["device_id"].tolist(),
            format_func=lambda x: devices_df[devices_df["device_id"] == x][
                "device_name"
            ].iloc[0],
        )

        col1, col2 = st.columns(2)

        with col1:
            weeks = max(1, math.ceil(time_range_days / 7))
            weekly_data = get_api_data(
                f"/devices/{selected_device_id}/weekly?weeks={weeks}"
            )
            if weekly_data and "data" in weekly_data:
                df_week = pd.DataFrame(weekly_data["data"])
                fig_week = px.line(
                    df_week,
                    x="date",
                    y="consumption_kwh",
                    title="Consumo Semanal (kWh)",
                    markers=True,
                    color_discrete_sequence=["#667eea"],
                )
                fig_week.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#ffffff",
                )
                st.plotly_chart(fig_week, use_container_width=True)

        with col2:
            monthly_data = get_api_data(f"/devices/{selected_device_id}/monthly")
            if monthly_data:
                st.metric(
                    "💰 Custo Mensal", f"R$ {monthly_data.get('total_cost_brl', 0):.2f}"
                )
                st.metric(
                    "⚡ Consumo Mensal",
                    f"{monthly_data.get('total_energy_kwh', 0):.2f} kWh",
                )
                st.metric(
                    "⏱️ Tempo de Uso", f"{monthly_data.get('runtime_hours', 0):.1f} h"
                )

    # Ranking de dispositivos
    st.markdown(f"### 🏆 Ranking de Consumo ({time_range_label})")
    ranking_data = get_api_data(f"/devices/ranking?period_days={time_range_days}")
    if ranking_data and "ranking" in ranking_data:
        df_rank = pd.DataFrame(ranking_data["ranking"])
        fig_rank = px.bar(
            df_rank,
            x="device_name",
            y="consumption_kwh",
            color="cost_brl",
            title="Consumo por Dispositivo",
            color_continuous_scale="Viridis",
        )
        fig_rank.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    devices_df["Consumo Atual (W)"] = devices_df["current_power_watts"]
    devices_df["Consumo Atual"] = devices_df["Consumo Atual (W)"].apply(format_power)
    devices_df["Status"] = devices_df["is_active"].apply(
        lambda x: "🟢 Ativo" if x else "🔴 Inativo"
    )
    devices_df["Última Leitura"] = pd.to_datetime(
        devices_df["last_reading"]
    ).dt.strftime("%d/%m %H:%M")

    display_columns = [
        "device_name",
        "location",
        "equipment_connected",
        "Consumo Atual",
        "Status",
        "Última Leitura",
    ]
    st.markdown("### 📋 Dispositivos Monitorados")
    st.dataframe(
        devices_df[display_columns].rename(
            columns={
                "device_name": "Dispositivo",
                "location": "Local",
                "equipment_connected": "Equipamento",
            }
        ),
        use_container_width=True,
    )

    fig_trend = px.area(
        devices_df,
        x="device_name",
        y="Consumo Atual (W)",
        color="device_name",
        title="Consumo Atual por Dispositivo",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    energy_estimates = []
    tariff = st.sidebar.number_input(
        "Tarifa Enel (R$/kWh)", min_value=0.0, value=0.862, step=0.01
    )
    for _, row in devices_df.iterrows():
        energy_daily = row["Consumo Atual (W)"] * 24 / 1000
        energy_week = energy_daily * 7
        energy_month = energy_daily * 30
        energy_estimates.append(
            {
                "Dispositivo": row["device_name"],
                "Diário (kWh)": energy_daily,
                "Semanal (kWh)": energy_week,
                "Mensal (kWh)": energy_month,
                "Custo Mensal (R$)": calculate_tariff_values(energy_month, tariff),
            }
        )

    st.markdown("### 📈 Projeções de Consumo e Custo")
    projections_df = pd.DataFrame(energy_estimates)
    st.dataframe(
        projections_df.style.format(
            {
                "Diário (kWh)": "{:.2f}",
                "Semanal (kWh)": "{:.2f}",
                "Mensal (kWh)": "{:.2f}",
                "Custo Mensal (R$)": "R$ {:.2f}",
            }
        ),
        use_container_width=True,
    )

    with st.expander("⚠️ Picos e Outliers"):
        avg_consumption = devices_df["Consumo Atual (W)"].mean()
        std_consumption = devices_df["Consumo Atual (W)"].std()
        threshold = avg_consumption + (std_consumption * 2 if std_consumption else 0)
        outliers = devices_df[
            devices_df["Consumo Atual (W)"] > max(threshold, avg_consumption * 1.5)
        ]
        if not outliers.empty:
            for _, row in outliers.iterrows():
                st.warning(
                    f"{row['device_name']} está consumindo {row['Consumo Atual (W)']:.1f} W."
                )
        else:
            st.success("Nenhum pico de consumo detectado agora.")


def render_smartlife_dashboard(smartlife_data: dict):
    if not smartlife_data:
        st.info(
            "📧 Aguardando dados SmartLife. Execute `python scripts/gmail_polling.py`."
        )
        return

    metrics = smartlife_data.get("metrics", {})

    st.markdown("### 🔍 Visão Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⚡ Consumo Diário", f"{metrics.get('daily_average_kwh', 0):.2f} kWh")
    col2.metric(
        "💰 Custo Mensal Estimado",
        f"R$ {metrics.get('estimated_monthly_cost_brl', 0):.2f}",
    )
    col3.metric(
        "📆 Projeção Mensal", f"{metrics.get('monthly_projection_kwh', 0):.1f} kWh"
    )
    status = metrics.get("status", "normal")
    col4.metric("🚦 Status", "🟢 Normal" if status == "normal" else "⚠️ Atenção")

    st.markdown("### 📊 Consumo Semanal")
    weekly_data = metrics.get("weekly_consumption_kwh", [])
    if weekly_data:
        df_week = pd.DataFrame(weekly_data)
        st.plotly_chart(
            px.line(
                df_week,
                x="date",
                y="consumption",
                markers=True,
                title="Consumo Diário (kWh)",
            ),
            use_container_width=True,
        )

    st.markdown("### 🏷️ Classificação do Mês")
    consumption_rank = metrics.get("consumption_rank", [])
    if consumption_rank:
        st.dataframe(pd.DataFrame(consumption_rank), use_container_width=True)

    st.markdown("### 🕒 Duração do Dispositivo")
    runtime_info = metrics.get("runtime_hours", {})
    if runtime_info:
        runtime_df = pd.DataFrame(
            [
                {
                    "Período": period,
                    "Horas": hours,
                }
                for period, hours in runtime_info.items()
            ]
        )
        st.plotly_chart(
            px.bar(runtime_df, x="Período", y="Horas", title="Tempo de Uso (h)"),
            use_container_width=True,
        )

    st.markdown("### 📌 Recomendações")
    recommendations = smartlife_data.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            st.write(f"- {rec}")
    else:
        st.info("Nenhuma recomendação adicional no momento.")


def render_chat_assistant():
    st.markdown("### 🤖 Assistente de Energia")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    provider = st.selectbox("Modelo", ["auto", "openai", "gemini"], index=0)
    question = st.text_input(
        "Pergunte sobre seu consumo ou custos", "Como foi meu consumo hoje?"
    )

    if st.button("Enviar pergunta", type="primary"):
        if question.strip():
            st.session_state.chat_history.append({"role": "user", "content": question})
            try:
                response = requests.post(
                    f"{API_BASE_URL}/ai/ask",
                    json={"question": question, "provider": provider},
                    timeout=60,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": data.get("response", "Sem resposta."),
                        }
                    )
                else:
                    st.error("Falha ao consultar o assistente.")
            except requests.exceptions.RequestException as exc:
                st.error(f"Erro ao conectar ao assistente: {exc}")

    for message in st.session_state.chat_history[-10:]:
        with st.chat_message(message["role"]):
            st.write(message["content"])


# Fluxo principal
if "realtime_data" not in st.session_state or auto_refresh:
    realtime_data = get_api_data("/status/realtime")
    if realtime_data:
        st.session_state.realtime_data = realtime_data
else:
    realtime_data = st.session_state.get("realtime_data", {})

smartlife_data = load_smartlife_data()

tab_tapo, tab_smartlife, tab_assistant = st.tabs(
    ["TP-Link Tapo", "SmartLife", "Assistente"]
)

with tab_tapo:
    render_tapo_dashboard(realtime_data)

    # Seções adicionais somente na aba Tapo
    st.markdown("---")
    st.markdown("## 📈 Relatórios e Análises")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Relatório Diário")
        report_date = st.date_input(
            "Data do Relatório",
            value=datetime.now().date(),
            max_value=datetime.now().date(),
        )

        if st.button("Gerar Relatório"):
            with st.spinner("Gerando relatório..."):
                report_data = get_api_data(f"/reports/daily?date={report_date}")
                if report_data and "error" not in report_data:
                    st.success("Relatório gerado com sucesso!")

                    st.markdown("#### 📊 Resumo do Dia")
                    st.write(
                        f"**Consumo Total:** {format_energy(report_data.get('total_energy_kwh', 0))}"
                    )
                    st.write(
                        f"**Custo Total:** {format_cost(report_data.get('total_cost', 0))}"
                    )
                    st.write(f"**Dispositivos:** {len(report_data.get('devices', []))}")

                    if report_data.get("anomalies"):
                        st.markdown("#### ⚠️ Anomalias Detectadas")
                        for anomaly in report_data["anomalies"]:
                            st.warning(anomaly.get("description", "Anomalia detectada"))

                    if st.button("📧 Enviar Relatório por Email/Telegram"):
                        send_result = requests.post(
                            f"{API_BASE_URL}/reports/daily/send?date={report_date}"
                        )
                        if send_result.status_code == 200:
                            st.success("Relatório enviado com sucesso!")
                        else:
                            st.error("Erro ao enviar relatório")

    with col2:
        st.markdown("### 🔌 Controle de Dispositivos")

        if realtime_data and "devices" in realtime_data:
            devices = realtime_data["devices"]
            device_names = [d["device_name"] for d in devices]

            if device_names:
                selected_device = st.selectbox(
                    "Selecione um dispositivo:", device_names
                )

                if selected_device:
                    device_info = next(
                        d for d in devices if d["device_name"] == selected_device
                    )

                    st.write(f"**IP:** {device_info.get('ip_address', 'N/A')}")
                    st.write(f"**Local:** {device_info.get('location', 'N/A')}")
                    st.write(
                        f"**Status:** {'🟢 Ativo' if device_info.get('is_active') else '🔴 Inativo'}"
                    )

                    col_on, col_off = st.columns(2)

                    with col_on:
                        if st.button("🟢 Ligar", key=f"on_{selected_device}"):
                            device_id = device_info.get("device_id")
                            result = requests.post(
                                f"{API_BASE_URL}/devices/{device_id}/control?action=on"
                            )
                            if result.status_code == 200:
                                st.success("Comando de ligar enviado!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Erro ao enviar comando")

                    with col_off:
                        if st.button("🔴 Desligar", key=f"off_{selected_device}"):
                            device_id = device_info.get("device_id")
                            result = requests.post(
                                f"{API_BASE_URL}/devices/{device_id}/control?action=off"
                            )
                            if result.status_code == 200:
                                st.success("Comando de desligar enviado!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("Erro ao enviar comando")

    # Seção de configurações
    st.markdown("---")
    st.markdown("## ⚙️ Configurações do Sistema")

    with st.expander("🔧 Configurações da API"):
        st.code(
            f"""
        API Base URL: {API_BASE_URL}
        Status: {'🟢 Online' if realtime_data else '🔴 Offline'}
        Auto Refresh: {'Ativado' if auto_refresh else 'Desativado'}
        """
        )

    with st.expander("📱 Testar Notificações"):
        if st.button("🧪 Testar Notificações"):
            with st.spinner("Testando configurações..."):
                test_result = get_api_data("/notifications/test")
                if test_result:
                    st.json(test_result)
                else:
                    st.error("Falha ao testar notificações")

    # Auto refresh apenas na aba principal
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            🏠 Casa Inteligente Dashboard | Desenvolvido com ❤️ por Patricia Menezes
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_smartlife:
    render_smartlife_dashboard(smartlife_data)

with tab_assistant:
    render_chat_assistant()
