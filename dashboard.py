"""
Dashboard Streamlit para Casa Inteligente
"""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Casa Inteligente Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuração da API
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Título da aplicação
st.title("🏠 Casa Inteligente Dashboard")
st.markdown("---")

# Sidebar com informações e controles
st.sidebar.markdown("## 📊 Controles")

# Refresh automático
auto_refresh = st.sidebar.checkbox("Auto Refresh (10s)", value=True)
refresh_interval = 10 if auto_refresh else 0

# Seletor de período
time_range = st.sidebar.selectbox(
    "Período de Análise", ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias"], index=0
)


# Funções para obter dados da API
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


# Layout principal
col1, col2, col3, col4 = st.columns(4)

# Obter status em tempo real
if "realtime_data" not in st.session_state or auto_refresh:
    realtime_data = get_api_data("/status/realtime")
    if realtime_data:
        st.session_state.realtime_data = realtime_data
else:
    realtime_data = st.session_state.get("realtime_data", {})

if realtime_data and "error" not in realtime_data:
    # Cards principais
    with col1:
        st.metric(
            label="⚡ Potência Total",
            value=format_power(realtime_data.get("total_current_power_watts", 0)),
            delta=None,
        )

    with col2:
        st.metric(
            label="🔌 Dispositivos Ativos",
            value=realtime_data.get("active_devices", 0),
            delta=None,
        )

    with col3:
        st.metric(
            label="📈 Status Sistema",
            value="🟢 Online" if realtime_data.get("devices") else "🔴 Offline",
            delta=None,
        )

    with col4:
        last_update = realtime_data.get("timestamp", datetime.now())
        time_diff = datetime.now() - pd.to_datetime(last_update)
        st.metric(
            label="🕐 Última Atualização",
            value=f"{time_diff.seconds // 60} min atrás",
            delta=None,
        )

# Gráficos e detalhes
if realtime_data and "devices" in realtime_data:
    st.markdown("## 📊 Dispositivos Monitorados")

    # Tabela de dispositivos
    devices_df = pd.DataFrame(realtime_data["devices"])

    if not devices_df.empty:
        # Formatar colunas
        devices_df["Consumo Atual"] = devices_df["current_power_watts"].apply(
            format_power
        )
        devices_df["Status"] = devices_df["is_active"].apply(
            lambda x: "🟢 Ativo" if x else "🔴 Inativo"
        )

        # Reordenar colunas
        display_columns = [
            "device_name",
            "location",
            "equipment_connected",
            "Consumo Atual",
            "Status",
            "last_reading",
        ]
        devices_df = devices_df[display_columns]

        # Renomear colunas
        devices_df.columns = [
            "Dispositivo",
            "Local",
            "Equipamento",
            "Consumo Atual",
            "Status",
            "Última Leitura",
        ]

        st.dataframe(devices_df, use_container_width=True)

        # Gráfico de consumo por dispositivo
        st.markdown("### ⚡ Consumo Atual por Dispositivo")

        fig_pie = px.pie(
            realtime_data["devices"],
            values="current_power_watts",
            names="device_name",
            title="Distribuição de Consumo Atual",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Gráfico de barras
        col1, col2 = st.columns(2)

        with col1:
            fig_bar = px.bar(
                realtime_data["devices"],
                x="device_name",
                y="current_power_watts",
                title="Consumo por Dispositivo",
                labels={
                    "current_power_watts": "Potência (W)",
                    "device_name": "Dispositivo",
                },
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Gráfico de status
            status_counts = devices_df["Status"].value_counts()
            fig_status = go.Figure(
                data=[
                    go.Bar(
                        x=status_counts.index,
                        y=status_counts.values,
                        marker_color=["green", "red"],
                    )
                ]
            )
            fig_status.update_layout(
                title="Status dos Dispositivos",
                xaxis_title="Status",
                yaxis_title="Quantidade",
            )
            st.plotly_chart(fig_status, use_container_width=True)

# Seção SmartLife (Geladeira Nova Digital)
st.markdown("---")
st.markdown("## 🧊 Geladeira Nova Digital (SmartLife)")

# Carregar dados do SmartLife
smarlife_file = Path("data/smartlife/latest.json")

if smartlife_file.exists():
    try:
        with open(smartlife_file, "r", encoding="utf-8") as f:
            smartlife_data = json.load(f)

        # Cards de métricas
        col1, col2, col3, col4 = st.columns(4)

        metrics = smartlife_data.get("metrics", {})

        with col1:
            st.metric(
                label="⚡ Consumo Diário",
                value=f"{metrics.get('daily_average_kwh', 0):.2f} kWh",
                delta=None,
            )

        with col2:
            st.metric(
                label="📊 Projeção Mensal",
                value=f"{metrics.get('monthly_projection_kwh', 0):.1f} kWh",
                delta=None,
            )

        with col3:
            st.metric(
                label="💰 Custo Estimado",
                value=f"R$ {metrics.get('estimated_monthly_cost_brl', 0):.2f}/mês",
                delta=None,
            )

        with col4:
            status = metrics.get("status", "unknown")
            status_emoji = "🟢" if status == "normal" else "⚠️"
            st.metric(
                label="📈 Status", value=f"{status_emoji} {status.title()}", delta=None
            )

        # Informações adicionais
        with st.expander("📋 Detalhes do Relatório SmartLife"):
            st.write(f"**Fonte:** {smartlife_data.get('source', 'N/A')}")
            st.write(f"**Dispositivo:** {smartlife_data.get('device_name', 'N/A')}")
            st.write(
                f"**Última Atualização:** {smartlife_data.get('timestamp', 'N/A')}"
            )
            st.write(f"**Data do Email:** {smartlife_data.get('email_date', 'N/A')}")

            if smartlife_data.get("html_file"):
                st.write(f"**Relatório HTML:** {smartlife_data.get('html_file')}")

            # Mostrar dados brutos
            if st.checkbox("Mostrar dados brutos"):
                st.json(smartlife_data)

        # Gráfico de consumo
        st.markdown("### 📊 Análise de Consumo")

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de comparação
            consumption_data = {
                "Categoria": [
                    "Consumo Atual",
                    "Média Normal (Min)",
                    "Média Normal (Max)",
                ],
                "kWh/dia": [
                    metrics.get("daily_average_kwh", 0),
                    0.8,  # Mínimo normal para geladeira
                    2.5,  # Máximo normal para geladeira
                ],
            }

            fig_comparison = px.bar(
                consumption_data,
                x="Categoria",
                y="kWh/dia",
                title="Consumo vs. Faixa Normal",
                color="Categoria",
                color_discrete_map={
                    "Consumo Atual": "#FF6B6B",
                    "Média Normal (Min)": "#4ECDC4",
                    "Média Normal (Max)": "#95E1D3",
                },
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

        with col2:
            # Gráfico de projeção de custo
            cost_data = {
                "Período": ["Diário", "Semanal", "Mensal", "Anual"],
                "Custo (R$)": [
                    metrics.get("daily_average_kwh", 0) * 0.85,
                    metrics.get("daily_average_kwh", 0) * 0.85 * 7,
                    metrics.get("estimated_monthly_cost_brl", 0),
                    metrics.get("estimated_monthly_cost_brl", 0) * 12,
                ],
            }

            fig_cost = px.line(
                cost_data,
                x="Período",
                y="Custo (R$)",
                title="Projeção de Custos",
                markers=True,
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        # Recomendações
        if metrics.get("daily_average_kwh", 0) > 2.5:
            st.warning(
                "⚠️ **Atenção:** Consumo acima do normal para geladeiras. Verifique:"
            )
            st.markdown(
                """
            - 🚪 Vedação da porta
            - 🧹 Limpeza das serpentinas
            - 🌡️ Temperatura configurada (ideal: 3-5°C)
            - 📦 Organização interna (não bloquear circulação de ar)
            """
            )
        elif metrics.get("daily_average_kwh", 0) < 0.8:
            st.info(
                "ℹ️ Consumo abaixo do esperado. Verifique se a geladeira está funcionando corretamente."
            )
        else:
            st.success("✅ Consumo dentro da faixa normal para geladeiras!")

    except Exception as e:
        st.error(f"Erro ao carregar dados do SmartLife: {e}")
else:
    st.info(
        "📧 Aguardando dados do SmartLife. Execute o polling para processar emails: `python scripts/gmail_polling.py`"
    )

# Seção de relatórios
st.markdown("---")
st.markdown("## 📈 Relatórios e Análises")

col1, col2 = st.columns(2)

with col1:
    # Gerar relatório diário
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

                # Mostrar resumo
                st.markdown("#### 📊 Resumo do Dia")
                st.write(
                    f"**Consumo Total:** {format_energy(report_data.get('total_energy_kwh', 0))}"
                )
                st.write(
                    f"**Custo Total:** {format_cost(report_data.get('total_cost', 0))}"
                )
                st.write(f"**Dispositivos:** {len(report_data.get('devices', []))}")

                # Mostrar anomalias se houver
                if report_data.get("anomalies"):
                    st.markdown("#### ⚠️ Anomalias Detectadas")
                    for anomaly in report_data["anomalies"]:
                        st.warning(anomaly.get("description", "Anomalia detectada"))

                # Botão para enviar relatório
                if st.button("📧 Enviar Relatório por Email/Telegram"):
                    send_result = requests.post(
                        f"{API_BASE_URL}/reports/daily/send?date={report_date}"
                    )
                    if send_result.status_code == 200:
                        st.success("Relatório enviado com sucesso!")
                    else:
                        st.error("Erro ao enviar relatório")

with col2:
    # Controle de dispositivos
    st.markdown("### 🔌 Controle de Dispositivos")

    if realtime_data and "devices" in realtime_data:
        devices = realtime_data["devices"]
        device_names = [d["device_name"] for d in devices]

        selected_device = st.selectbox("Selecione um dispositivo:", device_names)

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

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        🏠 Casa Inteligente Dashboard | Desenvolvido com ❤️ por Patricia Menezes
    </div>
    """,
    unsafe_allow_html=True,
)
