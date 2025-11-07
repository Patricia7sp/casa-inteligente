"""
Dashboard Streamlit para Casa Inteligente - Versão Corrigida TP-Link Tapo
"""

import os
import json
import time
import math
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st


# Configuração da página
st.set_page_config(
    page_title="Casa Inteligente - TP-Link Tapo",
    page_icon="🔌",
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
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .stMetric label {
        color: #a0aec0 !important;
        font-size: 0.9rem;
        font-weight: 500;
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
    .plotly-chart {
        border-radius: 15px;
        overflow: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Configuração da API - Usar Supabase como fonte principal
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://pqqrodiuuhckvdqawgeg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs")

# Título da aplicação
st.markdown(
    """
<div style='text-align: center; padding: 20px;'>
    <h1 style='font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
               font-weight: 800; margin-bottom: 10px;'>
        🔌 TP-Link Tapo
    </h1>
    <p style='color: #a0aec0; font-size: 1.1rem;'>Painel de Monitoramento de Energia</p>
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

# Tarifa de energia
tariff = st.sidebar.number_input(
    "Tarifa Enel (R$/kWh)", min_value=0.0, value=0.862, step=0.01
)


# Funções para obter dados do Supabase
def get_supabase_data(endpoint, params=None):
    """Obter dados diretamente do Supabase"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter dados do Supabase: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com Supabase: {str(e)}")
        return None


def get_api_data(endpoint):
    """Obter dados da API local"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter dados da API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com API: {str(e)}")
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


def build_summary_cards(devices_data, readings_data):
    """Construir cards de resumo"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular métricas
    total_power = sum(d.get('current_power_watts', 0) for d in devices_data if d.get('is_active'))
    active_devices = sum(1 for d in devices_data if d.get('is_active'))
    total_devices = len(devices_data)
    
    # Última leitura
    last_reading = "N/A"
    if readings_data:
        last_timestamp = max(r.get('timestamp') for r in readings_data)
        if last_timestamp:
            time_diff = datetime.now() - pd.to_datetime(last_timestamp)
            last_reading = f"{max(time_diff.seconds // 60, 0)} min atrás"

    with col1:
        st.metric(
            label="⚡ Potência Total",
            value=format_power(total_power),
        )

    with col2:
        st.metric(
            label="🔌 Dispositivos Ativos",
            value=f"{active_devices}/{total_devices}",
        )

    with col3:
        status_icon = "🟢" if active_devices > 0 else "🔴"
        st.metric(label="📈 Status Sistema", value=f"{status_icon} {'Ativo' if active_devices > 0 else 'Inativo'}")

    with col4:
        st.metric(
            label="🕐 Última Atualização",
            value=last_reading,
        )


def create_power_gauge(value, title, max_value=100):
    """Criar gráfico gauge para potência"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': max_value * 0.8},
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "lightgray"},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
    )
    
    return fig


def create_consumption_chart(df, title):
    """Criar gráfico de consumo"""
    fig = px.line(
        df,
        x="timestamp",
        y="power_watts",
        color="device_name",
        title=title,
        markers=True,
        color_discrete_sequence=["#667eea", "#764ba2", "#f093fb", "#f5576c"],
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_traces(line=dict(width=3))
    
    return fig


def create_device_comparison_chart(devices_df):
    """Criar gráfico de comparação entre dispositivos"""
    fig = px.bar(
        devices_df,
        x="device_name",
        y="current_power_watts",
        color="device_name",
        title="Consumo Atual por Dispositivo",
        color_discrete_sequence=["#667eea", "#764ba2", "#f093fb", "#f5576c"],
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=False,
    )
    
    fig.update_traces(
        marker=dict(line=dict(color='rgba(255,255,255,0.2)', width=1)),
        texttemplate='%{y:.1f}W',
        textposition='outside'
    )
    
    return fig


def create_energy_pie_chart(devices_df):
    """Criar gráfico de pizza de distribuição de energia"""
    fig = px.pie(
        devices_df,
        values="current_power_watts",
        names="device_name",
        title="Distribuição de Consumo",
        color_discrete_sequence=["#667eea", "#764ba2", "#f093fb", "#f5576c"],
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=True,
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='rgba(255,255,255,0.2)', width=1))
    )
    
    return fig


def render_tapo_dashboard():
    """Renderizar dashboard principal TP-Link Tapo"""
    
    # Obter dados do Supabase
    devices_data = get_supabase_data("devices")
    readings_data = get_supabase_data("energy_readings", params={
        "order": "timestamp.desc",
        "limit": "100"
    })
    
    if not devices_data:
        st.error("❌ Não foi possível carregar os dispositivos do Supabase")
        st.info("🔍 Verificando conexão...")
        
        # Tentar API local como fallback
        realtime_data = get_api_data("/status/realtime")
        if realtime_data and "devices" in realtime_data:
            st.success("✅ Conectado via API local")
            devices_data = realtime_data["devices"]
        else:
            st.error("❌ Falha em todas as fontes de dados")
            return
    
    # Filtrar apenas dispositivos ativos
    active_devices = [d for d in devices_data if d.get('is_active')]
    
    if not active_devices:
        st.warning("⚠️ Nenhum dispositivo TAPO ativo encontrado")
        return
    
    # Converter para DataFrame
    devices_df = pd.DataFrame(active_devices)
    
    # Cards de resumo
    build_summary_cards(active_devices, readings_data or [])
    
    st.markdown("---")
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de consumo atual
        fig_comparison = create_device_comparison_chart(devices_df)
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with col2:
        # Gráfico de distribuição
        fig_pie = create_energy_pie_chart(devices_df)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Gráfico de histórico
    st.markdown("### 📊 Histórico de Consumo")
    
    if readings_data:
        # Preparar dados para o gráfico
        readings_df = pd.DataFrame(readings_data)
        
        # Join com dispositivos para obter nomes
        if not readings_df.empty:
            readings_with_devices = []
            for reading in readings_data:
                device = next((d for d in active_devices if d['id'] == reading['device_id']), None)
                if device:
                    reading['device_name'] = device['name']
                    readings_with_devices.append(reading)
            
            if readings_with_devices:
                history_df = pd.DataFrame(readings_with_devices)
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                
                fig_history = create_consumption_chart(
                    history_df, 
                    "Histórico de Consumo (Últimas 100 leituras)"
                )
                st.plotly_chart(fig_history, use_container_width=True)
    
    # Tabela de dispositivos
    st.markdown("### 📋 Detalhes dos Dispositivos")
    
    # Preparar dados para exibição
    display_df = devices_df.copy()
    display_df["Consumo Atual"] = display_df["current_power_watts"].apply(format_power)
    display_df["Status"] = display_df["is_active"].apply(lambda x: "🟢 Ativo" if x else "🔴 Inativo")
    
    if 'last_reading' in display_df.columns:
        display_df["Última Leitura"] = pd.to_datetime(display_df["last_reading"]).dt.strftime("%d/%m %H:%M")
    
    # Selecionar colunas para exibição
    display_columns = ["name", "ip_address", "location", "equipment_connected", "Consumo Atual", "Status"]
    available_columns = [col for col in display_columns if col in display_df.columns]
    
    st.dataframe(
        display_df[available_columns].rename(columns={
            "name": "Dispositivo",
            "ip_address": "IP",
            "location": "Local",
            "equipment_connected": "Equipamento",
        }),
        use_container_width=True,
    )
    
    # Projeções de consumo
    st.markdown("### 📈 Projeções de Consumo e Custo")
    
    projections = []
    for _, device in devices_df.iterrows():
        current_power = device.get('current_power_watts', 0)
        daily_energy = current_power * 24 / 1000
        weekly_energy = daily_energy * 7
        monthly_energy = daily_energy * 30
        monthly_cost = monthly_energy * tariff
        
        projections.append({
            "Dispositivo": device['name'],
            "Diário (kWh)": round(daily_energy, 2),
            "Semanal (kWh)": round(weekly_energy, 2),
            "Mensal (kWh)": round(monthly_energy, 2),
            "Custo Mensal (R$)": round(monthly_cost, 2),
        })
    
    projections_df = pd.DataFrame(projections)
    
    # Adicionar totais
    totals = projections_df.sum(numeric_only=True)
    totals["Dispositivo"] = "TOTAL"
    totals_df = pd.DataFrame([totals])
    
    final_df = pd.concat([projections_df, totals_df], ignore_index=True)
    
    st.dataframe(
        final_df.style.format({
            "Diário (kWh)": "{:.2f}",
            "Semanal (kWh)": "{:.2f}",
            "Mensal (kWh)": "{:.2f}",
            "Custo Mensal (R$)": "R$ {:.2f}",
        }).background_gradient(subset=["Custo Mensal (R$)"], cmap="Reds"),
        use_container_width=True,
    )
    
    # Alertas e anomalias
    st.markdown("### ⚠️ Monitoramento de Anomalias")
    
    if devices_df['current_power_watts'].max() > 0:
        avg_power = devices_df['current_power_watts'].mean()
        std_power = devices_df['current_power_watts'].std()
        threshold = avg_power + (std_power * 1.5 if std_power else avg_power * 0.5)
        
        outliers = devices_df[devices_df['current_power_watts'] > threshold]
        
        if not outliers.empty:
            for _, device in outliers.iterrows():
                st.warning(
                    f"🚨 **{device['name']}** com consumo elevado: "
                    f"{format_power(device['current_power_watts'])} "
                    f"(média: {format_power(avg_power)})"
                )
        else:
            st.success("✅ Nenhum pico de consumo detectado")
    
    # Status da conexão
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Fonte de Dados", "Supabase" if devices_data else "API Local")
    
    with col2:
        st.metric("🔄 Última Sincronização", datetime.now().strftime("%H:%M:%S"))
    
    with col3:
        st.metric("📈 Total de Leituras", len(readings_data) if readings_data else 0)


# Fluxo principal
render_tapo_dashboard()

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        🔌 TP-Link Tapo Dashboard | Casa Inteligente System
    </div>
    """,
    unsafe_allow_html=True,
)
