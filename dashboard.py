"""
Dashboard Streamlit para Casa Inteligente - Versão Corrigida TP-Link Tapo
"""

import os
import json
import time
import math
import importlib.util
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
SUPABASE_KEY = os.getenv(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs",
)

TAPO_DEVICE_PROFILES = {
    "purificador": {
        "label": "Purificador",
        "aliases": ["tomada inteligente - purificador"],
        "keywords": ["purificador"],
        "icon": "🌬️",
        "color": "#667eea",
    },
    "notebook": {
        "label": "Notebook",
        "aliases": ["tomada inteligente - notebook"],
        "keywords": ["notebook"],
        "icon": "💻",
        "color": "#764ba2",
    },
}

TAPO_COLOR_FALLBACK = "#f093fb"

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
            "Content-Type": "application/json",
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


def classify_tapo_device(device: dict) -> str | None:
    """Classificar dispositivo TAPO com base em nome/equipamento."""

    name = (device.get("name") or "").lower()
    equipment = (device.get("equipment_connected") or "").lower()

    for profile_key, profile in TAPO_DEVICE_PROFILES.items():
        # Verificar aliases exatos
        if any(alias in name for alias in profile.get("aliases", [])):
            return profile_key

        # Verificar palavras-chave em nome ou equipamento
        if any(keyword in name for keyword in profile.get("keywords", [])):
            return profile_key
        if any(keyword in equipment for keyword in profile.get("keywords", [])):
            return profile_key

    return None


def get_profile_color(profile_key: str) -> str:
    """Obter cor padrão para o perfil TAPO informado."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("color", TAPO_COLOR_FALLBACK)


def get_profile_label(profile_key: str, default: str) -> str:
    """Obter rótulo amigável para o perfil TAPO."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("label", default)


def get_profile_icon(profile_key: str) -> str:
    """Obter ícone representativo do perfil TAPO."""

    return TAPO_DEVICE_PROFILES.get(profile_key, {}).get("icon", "🔌")


def build_color_map(devices: list[dict]) -> dict[str, str]:
    """Construir mapa nome -> cor para gráficos."""

    color_map: dict[str, str] = {}
    for device in devices:
        name = (
            device.get("device_name")
            or device.get("display_name")
            or device.get("name")
        )
        profile_key = device.get("profile_key")
        if not name:
            continue
        color_map[name] = get_profile_color(profile_key)
    return color_map


def create_single_device_line(
    df: pd.DataFrame,
    y_col: str,
    title: str,
    color: str,
    yaxis_title: str,
) -> go.Figure:
    """Criar gráfico de linha para um único dispositivo."""

    if df.empty:
        return go.Figure()

    fig = px.line(
        df,
        x="timestamp",
        y=y_col,
        title=title,
        markers=True,
        color_discrete_sequence=[color],
    )

    fig.update_layout(
        height=320,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        yaxis_title=yaxis_title,
    )

    fig.update_traces(line=dict(width=3))

    return fig


def build_summary_cards(devices_data, readings_data):
    """Construir cards de resumo"""
    col1, col2, col3, col4 = st.columns(4)

    # Calcular métricas
    total_power = sum(
        d.get("current_power_watts", 0) for d in devices_data if d.get("is_active")
    )
    active_devices = sum(1 for d in devices_data if d.get("is_active"))
    total_devices = len(devices_data)

    # Última leitura
    last_reading = "N/A"
    if readings_data:
        last_timestamp = max(r.get("timestamp") for r in readings_data)
        if last_timestamp:
            try:
                time_diff = datetime.now() - pd.to_datetime(
                    last_timestamp, errors="coerce"
                )
                if pd.notna(time_diff):
                    last_reading = f"{max(time_diff.seconds // 60, 0)} min atrás"
            except:
                last_reading = "N/A"

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
        st.metric(
            label="📈 Status Sistema",
            value=f"{status_icon} {'Ativo' if active_devices > 0 else 'Inativo'}",
        )

    with col4:
        st.metric(
            label="🕐 Última Atualização",
            value=last_reading,
        )


def create_power_gauge(value, title, max_value=100):
    """Criar gráfico gauge para potência"""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            delta={"reference": max_value * 0.8},
            gauge={
                "axis": {"range": [None, max_value]},
                "bar": {"color": "#667eea"},
                "steps": [
                    {"range": [0, max_value * 0.5], "color": "lightgray"},
                    {"range": [max_value * 0.5, max_value * 0.8], "color": "gray"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": max_value * 0.9,
                },
            }, )
    )

    fig.update_layout(
        height=300,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
    )

    return fig


def aggregate_energy_data(df, freq='D'):
    """
    Agregar dados de energia por período (hora, dia, mês)
    
    Args:
        df: DataFrame com colunas timestamp, energy_today_kwh, device_id
        freq: Frequência de agregação ('H'=hora, 'D'=dia, 'M'=mês)
    
    Returns:
        DataFrame agregado com totais por período
    """
    if df.empty or 'timestamp' not in df.columns:
        return pd.DataFrame()
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
    # Agrupar por período e dispositivo
    df['period'] = df['timestamp'].dt.to_period(freq)
    
    # Calcular energia total por período
    # Usar o máximo de energy_today_kwh por dia (acumulado do dia)
    if 'energy_today_kwh' in df.columns:
        aggregated = df.groupby(['period', 'device_id']).agg({
            'energy_today_kwh': 'max',  # Máximo do dia (valor acumulado)
            'power_watts': 'mean',       # Média de potência
            'timestamp': 'first'
        }).reset_index()
    else:
        # Calcular energia a partir da potência (kWh = W * h / 1000)
        hours_in_period = {'H': 1, 'D': 24, 'M': 720}
        df['energy_kwh'] = df['power_watts'] * hours_in_period.get(freq, 24) / 1000
        aggregated = df.groupby(['period', 'device_id']).agg({
            'energy_kwh': 'sum',
            'power_watts': 'mean',
            'timestamp': 'first'
        }).reset_index()
    
    aggregated['period'] = aggregated['period'].dt.to_timestamp()
    return aggregated


def create_daily_consumption_timeline(df, color_map=None, tariff=0.862):
    """Criar gráfico de linha temporal com consumo diário acumulado"""
    
    if df.empty:
        return go.Figure()
    
    # Agregar por dia
    daily_data = aggregate_energy_data(df, freq='D')
    
    if daily_data.empty:
        return go.Figure()
    
    # Agrupar por dia (somar todos os dispositivos)
    daily_totals = daily_data.groupby('period').agg({
        'energy_today_kwh': 'sum' if 'energy_today_kwh' in daily_data.columns else 'sum',
        'power_watts': 'mean'
    }).reset_index()
    
    # Calcular custo
    daily_totals['cost'] = daily_totals.get('energy_today_kwh', daily_totals.get('energy_kwh', 0)) * tariff
    
    # Criar gráfico com duas linhas (energia e custo)
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Consumo Diário (kWh)', 'Custo Diário (R$)'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Linha de consumo
    fig.add_trace(
        go.Scatter(
            x=daily_totals['period'],
            y=daily_totals.get('energy_today_kwh', daily_totals.get('energy_kwh', 0)),
            mode='lines+markers',
            name='Consumo (kWh)',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ),
        row=1, col=1
    )
    
    # Linha de custo
    fig.add_trace(
        go.Scatter(
            x=daily_totals['period'],
            y=daily_totals['cost'],
            mode='lines+markers',
            name='Custo (R$)',
            line=dict(color='#f5576c', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(245, 87, 108, 0.2)'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        showlegend=True,
        title_text='📊 Consumo e Custo Diário ao Longo do Tempo',
        title_font_size=18
    )
    
    fig.update_xaxes(title_text='Data', row=2, col=1)
    fig.update_yaxes(title_text='kWh', row=1, col=1)
    fig.update_yaxes(title_text='R$', row=2, col=1)
    
    return fig


def create_monthly_totals_chart(df, color_map=None, tariff=0.862):
    """Criar gráfico de totais mensais para comparação ao longo do tempo"""
    
    if df.empty:
        return go.Figure()
    
    # Agregar por mês
    monthly_data = aggregate_energy_data(df, freq='M')
    
    if monthly_data.empty:
        return go.Figure()
    
    # Agrupar por mês (somar todos os dispositivos)
    monthly_totals = monthly_data.groupby('period').agg({
        'energy_today_kwh': 'sum' if 'energy_today_kwh' in monthly_data.columns else 'sum',
        'power_watts': 'mean'
    }).reset_index()
    
    # Calcular custo
    monthly_totals['cost'] = monthly_totals.get('energy_today_kwh', monthly_totals.get('energy_kwh', 0)) * tariff
    monthly_totals['month_label'] = monthly_totals['period'].dt.strftime('%b/%Y')
    
    # Criar gráfico de barras com duas séries
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Consumo Mensal (kWh)', 'Custo Mensal (R$)'),
        horizontal_spacing=0.12
    )
    
    # Barras de consumo
    fig.add_trace(
        go.Bar(
            x=monthly_totals['month_label'],
            y=monthly_totals.get('energy_today_kwh', monthly_totals.get('energy_kwh', 0)),
            name='Consumo (kWh)',
            marker_color='#667eea',
            text=monthly_totals.get('energy_today_kwh', monthly_totals.get('energy_kwh', 0)).round(2),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Barras de custo
    fig.add_trace(
        go.Bar(
            x=monthly_totals['month_label'],
            y=monthly_totals['cost'],
            name='Custo (R$)',
            marker_color='#f5576c',
            text=monthly_totals['cost'].round(2),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        showlegend=False,
        title_text='📅 Comparação Mensal de Consumo e Custo',
        title_font_size=18
    )
    
    fig.update_xaxes(title_text='Mês', row=1, col=1)
    fig.update_xaxes(title_text='Mês', row=1, col=2)
    fig.update_yaxes(title_text='kWh', row=1, col=1)
    fig.update_yaxes(title_text='R$', row=1, col=2)
    
    return fig


def create_consumption_chart(
    df,
    title,
    color_field="device_name",
    color_map=None,
):
    """Criar gráfico de consumo"""

    if color_field:
        fig = px.line(
            df,
            x="timestamp",
            y="power_watts",
            color=color_field,
            title=title,
            markers=True,
            color_discrete_map=color_map or {},
            color_discrete_sequence=["#667eea", "#764ba2", "#f093fb", "#f5576c"],
        )
    else:
        fig = px.line(
            df,
            x="timestamp",
            y="power_watts",
            title=title,
            markers=True,
            color_discrete_sequence=["#667eea"],
        )

    fig.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig.update_traces(line=dict(width=3))

    return fig


def create_device_comparison_chart(
    devices_df,
    label_field="device_name",
    color_map=None,
):
    """Criar gráfico de comparação entre dispositivos"""
    fig = px.bar(
        devices_df,
        x=label_field,
        y="current_power_watts",
        color=label_field,
        title="Consumo Atual por Dispositivo",
        color_discrete_map=color_map or {},
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
        marker=dict(line=dict(color="rgba(255,255,255,0.2)", width=1)),
        texttemplate="%{y:.1f}W",
        textposition="outside",
    )

    return fig


def create_energy_pie_chart(
    devices_df,
    label_field="device_name",
    color_map=None,
):
    """Criar gráfico de pizza de distribuição de energia"""
    fig = px.pie(
        devices_df,
        values="current_power_watts",
        names=label_field,
        title="Distribuição de Consumo",
        color_discrete_map=color_map or {},
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
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="rgba(255,255,255,0.2)", width=1)),
    )

    return fig


def render_tapo_dashboard():
    """Renderizar dashboard principal TP-Link Tapo"""

    # Obter dados do Supabase
    devices_data = get_supabase_data("devices")
    readings_data = get_supabase_data(
        "energy_readings", params={"order": "timestamp.desc", "limit": "100"}
    )

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

    # Filtrar apenas dispositivos TAPO relevantes
    tapo_devices = []
    for device in devices_data:
        # Aceitar dispositivos TAPO mesmo se is_active for None ou True
        is_active = device.get("is_active")
        if is_active is False:
            continue

        profile_key = classify_tapo_device(device)
        if profile_key:
            device = device.copy()
            profile_label = get_profile_label(
                profile_key, device.get("name", "Dispositivo TAPO")
            )
            icon = get_profile_icon(profile_key)

            device["profile_key"] = profile_key
            device["profile_label"] = profile_label
            device["display_name"] = f"{icon} {profile_label}"
            # Garantir que is_active seja True para compatibilidade
            if device.get("is_active") is None:
                device["is_active"] = True
            tapo_devices.append(device)

    if not tapo_devices:
        st.warning("⚠️ Nenhum dispositivo TAPO relevante encontrado")
        return

    # Converter para DataFrame
    devices_df = pd.DataFrame(tapo_devices)

    if devices_df.empty:
        st.warning("⚠️ Não há dados dos dispositivos para exibir.")
        return

    # Adicionar coluna device_name se não existir (compatibilidade)
    if "name" in devices_df.columns and "device_name" not in devices_df.columns:
        devices_df["device_name"] = devices_df["name"]

    # Garantir coluna de potência atual
    if "current_power_watts" not in devices_df.columns:
        devices_df["current_power_watts"] = 0.0

    # Se existirem leituras, utilizar última leitura por dispositivo
    if readings_data:
        readings_df_latest = (
            pd.DataFrame(readings_data)
            .sort_values("timestamp")
            .drop_duplicates("device_id", keep="last")
        )

        if not readings_df_latest.empty:
            readings_df_latest["timestamp"] = pd.to_datetime(
                readings_df_latest["timestamp"], errors="coerce"
            )

            readings_df_latest = readings_df_latest.rename(
                columns={
                    "device_id": "reading_device_id",
                    "power_watts": "reading_power_watts",
                }
            )

            devices_df = devices_df.merge(
                readings_df_latest[["reading_device_id", "reading_power_watts"]],
                how="left",
                left_on="id",
                right_on="reading_device_id",
            )

            devices_df["current_power_watts"] = devices_df[
                "reading_power_watts"
            ].fillna(devices_df["current_power_watts"])

            devices_df.drop(
                columns=[
                    col
                    for col in ["reading_device_id", "reading_power_watts"]
                    if col in devices_df.columns
                ],
                inplace=True,
            )

    devices_df["current_power_watts"] = pd.to_numeric(
        devices_df["current_power_watts"], errors="coerce"
    ).fillna(0.0)

    # Cards de resumo
    build_summary_cards(tapo_devices, readings_data or [])

    st.markdown("---")

    # Preparar rótulos e cores harmonizados
    if "display_name" not in devices_df.columns:
        devices_df["display_name"] = devices_df["device_name"]
    devices_df["display_label"] = devices_df["display_name"]
    color_map = build_color_map(tapo_devices)

    # Gráficos principais
    col1, col2 = st.columns(2)

    with col1:
        fig_comparison = create_device_comparison_chart(
            devices_df,
            label_field="display_label",
            color_map=color_map,
        )
        st.plotly_chart(fig_comparison, use_container_width=True)

    with col2:
        fig_pie = create_energy_pie_chart(
            devices_df,
            label_field="display_label",
            color_map=color_map,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Histórico consolidado
    st.markdown("### 📊 Histórico de Consumo")

    history_df = pd.DataFrame()
    if readings_data:
        tapo_ids = {device["id"] for device in tapo_devices}
        tapo_readings = [
            reading for reading in readings_data if reading.get("device_id") in tapo_ids
        ]

        if tapo_readings:
            history_df = pd.DataFrame(tapo_readings)
            history_df["timestamp"] = pd.to_datetime(
                history_df["timestamp"], errors="coerce"
            )
            history_df = history_df.dropna(subset=["timestamp"])
            history_df = history_df.sort_values("timestamp")

            start_time = datetime.now() - timedelta(days=time_range_days)
            history_df = history_df[history_df["timestamp"] >= start_time]

            display_map = {d["id"]: d["display_name"] for d in tapo_devices}
            profile_map = {d["id"]: d["profile_key"] for d in tapo_devices}
            history_df["display_label"] = history_df["device_id"].map(display_map)
            history_df["profile_key"] = history_df["device_id"].map(profile_map)
            history_df = history_df.dropna(subset=["display_label"])

    if not history_df.empty:
        # Gráfico de linha temporal original (potência instantânea)
        fig_history = create_consumption_chart(
            history_df,
            f"Histórico de Potência Instantânea (últimos {time_range_days} dia(s))",
            color_field="display_label",
            color_map=color_map,
        )
        st.plotly_chart(fig_history, use_container_width=True)
        
        st.markdown("---")
        
        # Novos gráficos de agregação
        st.markdown("### 📈 Análise de Consumo e Custo Agregados")
        
        # Gráfico de linha temporal diária (consumo acumulado por dia)
        fig_daily = create_daily_consumption_timeline(history_df, color_map, tariff)
        st.plotly_chart(fig_daily, use_container_width=True)
        
        st.markdown("---")
        
        # Gráfico de totais mensais
        fig_monthly = create_monthly_totals_chart(history_df, color_map, tariff)
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Tabela de resumo com totais agregados
        st.markdown("### 📊 Resumo de Totais Agregados")
        
        # Calcular totais por período
        col1, col2, col3 = st.columns(3)
        
        # Total diário (média dos últimos dias)
        daily_agg = aggregate_energy_data(history_df, freq='D')
        if not daily_agg.empty:
            daily_totals = daily_agg.groupby('period')['energy_today_kwh'].sum() if 'energy_today_kwh' in daily_agg.columns else daily_agg.groupby('period')['energy_kwh'].sum()
            avg_daily_kwh = daily_totals.mean()
            avg_daily_cost = avg_daily_kwh * tariff
            
            with col1:
                st.metric(
                    label="📅 Média Diária",
                    value=f"{avg_daily_kwh:.2f} kWh",
                    delta=f"R$ {avg_daily_cost:.2f}"
                )
        
        # Total semanal (última semana)
        last_7_days = history_df[history_df['timestamp'] >= (datetime.now() - timedelta(days=7))]
        if not last_7_days.empty:
            weekly_agg = aggregate_energy_data(last_7_days, freq='D')
            if not weekly_agg.empty:
                weekly_total = weekly_agg.groupby('period')['energy_today_kwh'].sum().sum() if 'energy_today_kwh' in weekly_agg.columns else weekly_agg.groupby('period')['energy_kwh'].sum().sum()
                weekly_cost = weekly_total * tariff
                
                with col2:
                    st.metric(
                        label="📅 Últimos 7 Dias",
                        value=f"{weekly_total:.2f} kWh",
                        delta=f"R$ {weekly_cost:.2f}"
                    )
        
        # Total mensal (último mês)
        last_30_days = history_df[history_df['timestamp'] >= (datetime.now() - timedelta(days=30))]
        if not last_30_days.empty:
            monthly_agg = aggregate_energy_data(last_30_days, freq='D')
            if not monthly_agg.empty:
                monthly_total = monthly_agg.groupby('period')['energy_today_kwh'].sum().sum() if 'energy_today_kwh' in monthly_agg.columns else monthly_agg.groupby('period')['energy_kwh'].sum().sum()
                monthly_cost = monthly_total * tariff
                
                with col3:
                    st.metric(
                        label="📅 Últimos 30 Dias",
                        value=f"{monthly_total:.2f} kWh",
                        delta=f"R$ {monthly_cost:.2f}"
                    )
        
    else:
        st.info(
            "Sem leituras recentes para os dispositivos TAPO no período selecionado."
        )

    # Tabela de dispositivos
    st.markdown("### 📋 Detalhes dos Dispositivos")

    display_df = devices_df.copy()
    display_df["Dispositivo"] = display_df["display_label"]
    display_df["Consumo Atual"] = display_df["current_power_watts"].apply(format_power)
    display_df["Status"] = display_df["is_active"].apply(
        lambda x: "🟢 Ativo" if x else "🔴 Inativo"
    )

    if "last_reading" in display_df.columns:
        display_df["Última Leitura"] = pd.to_datetime(
            display_df["last_reading"], errors="coerce"
        ).dt.strftime("%d/%m %H:%M")

    table_columns = [
        "Dispositivo",
        "ip_address",
        "location",
        "equipment_connected",
        "Consumo Atual",
        "Status",
    ]
    available_columns = [col for col in table_columns if col in display_df.columns]

    st.dataframe(
        display_df[available_columns].rename(
            columns={
                "ip_address": "IP",
                "location": "Local",
                "equipment_connected": "Equipamento",
            }
        ),
        use_container_width=True,
    )

    # Projeções de consumo e custo
    st.markdown("### 📈 Projeções de Consumo e Custo")

    projections = []
    for _, device in devices_df.iterrows():
        current_power = device.get("current_power_watts", 0)
        daily_energy = current_power * 24 / 1000
        weekly_energy = daily_energy * 7
        monthly_energy = daily_energy * 30
        monthly_cost = monthly_energy * tariff

        projections.append(
            {
                "Dispositivo": device["display_label"],
                "Diário (kWh)": round(daily_energy, 2),
                "Semanal (kWh)": round(weekly_energy, 2),
                "Mensal (kWh)": round(monthly_energy, 2),
                "Custo Mensal (R$)": round(monthly_cost, 2),
            }
        )

    projections_df = pd.DataFrame(projections)

    totals = projections_df.sum(numeric_only=True)
    totals["Dispositivo"] = "TOTAL"
    totals_df = pd.DataFrame([totals])

    final_df = pd.concat([projections_df, totals_df], ignore_index=True)

    style = final_df.style.format(
        {
            "Diário (kWh)": "{:.2f}",
            "Semanal (kWh)": "{:.2f}",
            "Mensal (kWh)": "{:.2f}",
            "Custo Mensal (R$)": "R$ {:.2f}",
        }
    )

    if importlib.util.find_spec("matplotlib"):
        style = style.background_gradient(subset=["Custo Mensal (R$)"], cmap="Reds")
    else:
        st.info(
            "ℹ️ Instale matplotlib para habilitar destaque de gradiente na tabela de projeções."
        )

    st.dataframe(style, use_container_width=True)

    # Monitoramento individual por dispositivo
    st.markdown("### 🔍 Monitoramento Individual por Dispositivo")

    anomaly_summaries = []
    if history_df.empty:
        st.info(
            "Sem leituras suficientes para detalhar os dispositivos TAPO no período selecionado."
        )
    else:
        for device in tapo_devices:
            device_id = device["id"]
            display_name = device.get("display_name") or device.get("name")
            profile_color = color_map.get(display_name, TAPO_COLOR_FALLBACK)

            device_history = history_df[history_df["device_id"] == device_id].copy()
            if device_history.empty:
                st.info(f"{display_name}: ainda sem leituras recentes.")
                continue

            device_history = device_history.sort_values("timestamp")
            device_history["power_watts"] = (
                pd.to_numeric(device_history["power_watts"], errors="coerce")
                .fillna(method="ffill")
                .fillna(0)
            )

            if "energy_today_kwh" in device_history.columns:
                device_history["energy_today_kwh"] = (
                    pd.to_numeric(device_history["energy_today_kwh"], errors="coerce")
                    .fillna(method="ffill")
                    .fillna(0)
                )
                device_history["custo_estimado"] = (
                    device_history["energy_today_kwh"] * tariff
                )
            else:
                device_history["custo_estimado"] = pd.Series(dtype=float)

            st.markdown(f"#### {display_name}")

            col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)

            current_power = device.get("current_power_watts", 0)
            col_metrics1.metric("Potência Atual", format_power(current_power))

            last_timestamp = device_history["timestamp"].iloc[-1]
            minutes_ago = max(
                int((datetime.now() - last_timestamp).total_seconds() // 60), 0
            )
            col_metrics2.metric("Última Leitura", f"{minutes_ago} min")

            energy_today = (
                device_history["energy_today_kwh"].iloc[-1]
                if "energy_today_kwh" in device_history.columns
                else float("nan")
            )
            if pd.notna(energy_today):
                col_metrics3.metric("Energia Hoje", f"{energy_today:.3f} kWh")
            else:
                col_metrics3.metric("Energia Hoje", "-")

            cost_today = (
                device_history["custo_estimado"].iloc[-1]
                if "custo_estimado" in device_history.columns
                and not device_history["custo_estimado"].isna().all()
                else float("nan")
            )
            if pd.notna(cost_today):
                col_metrics4.metric("Custo Estimado", format_cost(cost_today))
            else:
                col_metrics4.metric("Custo Estimado", "-")

            power_series = device_history["power_watts"]
            avg_power = power_series.mean()
            std_power = power_series.std()
            peak_power = power_series.max()
            threshold = avg_power + (std_power * 2 if std_power else avg_power * 0.5)
            spike_points = device_history[power_series > threshold]

            if not spike_points.empty:
                peak_time = spike_points["timestamp"].iloc[-1].strftime("%d/%m %H:%M")
                msg = (
                    f"{display_name}: {len(spike_points)} pico(s) acima de {threshold:.1f} W "
                    f"(máximo {peak_power:.1f} W às {peak_time})."
                )
                anomaly_summaries.append((True, msg))
                st.warning(f"⚠️ {msg}")
            else:
                msg = f"{display_name}: consumo estável (média {avg_power:.1f} W, pico {peak_power:.1f} W)."
                anomaly_summaries.append((False, msg))
                st.success(f"✅ {msg}")

            col_chart1, col_chart2 = st.columns(2)

            fig_power = create_single_device_line(
                device_history,
                "power_watts",
                "Potência Instantânea (W)",
                profile_color,
                "W",
            )
            col_chart1.plotly_chart(fig_power, use_container_width=True)

            if "energy_today_kwh" in device_history.columns:
                fig_energy = create_single_device_line(
                    device_history,
                    "energy_today_kwh",
                    "Energia acumulada no dia (kWh)",
                    profile_color,
                    "kWh",
                )
                col_chart2.plotly_chart(fig_energy, use_container_width=True)
            else:
                col_chart2.info("Sem dados de energia acumulada para este dispositivo.")

            if (
                "custo_estimado" in device_history.columns
                and not device_history["custo_estimado"].isna().all()
            ):
                fig_cost = create_single_device_line(
                    device_history,
                    "custo_estimado",
                    "Custo estimado acumulado (R$)",
                    profile_color,
                    "R$",
                )
                st.plotly_chart(fig_cost, use_container_width=True)

            st.markdown("---")

    # Resumo de anomalias
    st.markdown("### ⚠️ Monitoramento de Anomalias")
    if not anomaly_summaries:
        st.info("Sem leituras para análise de anomalias.")
    else:
        spikes = [msg for has_spike, msg in anomaly_summaries if has_spike]
        if spikes:
            for msg in spikes:
                st.warning(msg)
        else:
            st.success(
                "Nenhum pico de consumo detectado nos dispositivos TAPO no período selecionado."
            )

    # Status da conexão
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📊 Fonte de Dados", "Supabase" if devices_data else "API Local")

    with col2:
        st.metric("🔄 Última Sincronização", datetime.now().strftime("%H:%M:%S"))

    with col3:
        st.metric(
            "📈 Total de Leituras", len(history_df) if not history_df.empty else 0
        )


def load_smartlife_data() -> dict:
    """Carregar dados SmartLife"""
    smartlife_file = Path("data/smartlife/latest.json")
    if smartlife_file.exists():
        try:
            with open(smartlife_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Arquivo SmartLife inválido. Execute o polling novamente.")
    return {}


def render_smartlife_dashboard(smartlife_data: dict):
    """Renderizar dashboard SmartLife"""
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
        fig_week = px.line(
            df_week,
            x="date",
            y="consumption",
            markers=True,
            title="Consumo Diário (kWh)",
            color_discrete_sequence=["#667eea"],
        )
        fig_week.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
        )
        st.plotly_chart(fig_week, use_container_width=True)

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
        fig_runtime = px.bar(
            runtime_df,
            x="Período",
            y="Horas",
            title="Tempo de Uso (h)",
            color_discrete_sequence=["#764ba2"],
        )
        fig_runtime.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
        )
        st.plotly_chart(fig_runtime, use_container_width=True)

    st.markdown("### 📌 Recomendações")
    recommendations = smartlife_data.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            st.write(f"- {rec}")
    else:
        st.info("Nenhuma recomendação adicional no momento.")


def render_chat_assistant():
    """Renderizar assistente de IA com interface moderna"""
    # CSS customizado para chat moderno
    st.markdown(
        """
        <style>
        .chat-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        }
        .chat-title {
            color: white;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .chat-subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 1rem;
        }
        .stChatMessage {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            backdrop-filter: blur(10px);
        }
        .stChatMessage[data-testid="user-message"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stChatMessage[data-testid="assistant-message"] {
            background: rgba(30,30,30,0.8);
            border-left: 3px solid #667eea;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header do chat
    st.markdown(
        """
        <div class="chat-container">
            <div class="chat-title">🤖 Assistente Inteligente de Energia</div>
            <div class="chat-subtitle">Pergunte sobre consumo, custos e receba insights personalizados</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inicializar histórico
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Configurações em expander
    with st.expander("⚙️ Configurações do Assistente", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            provider = st.selectbox(
                "Modelo de IA",
                ["auto", "openai", "gemini"],
                index=0,
                help="Auto: tenta OpenAI primeiro, depois Gemini",
            )
        with col2:
            if st.button("🗑️ Limpar Conversa"):
                st.session_state.chat_history = []
                st.rerun()

    # Exibir histórico de mensagens
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(
            message["role"], avatar="👤" if message["role"] == "user" else "🤖"
        ):
            st.markdown(message["content"])

    # Input de mensagem com form (compatível com tabs)
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            prompt = st.text_input(
                "Digite sua pergunta:",
                placeholder="Como está meu consumo hoje?",
                label_visibility="collapsed",
            )
        with col2:
            submit = st.form_submit_button("📤 Enviar", use_container_width=True)

    if submit and prompt.strip():
        # Adicionar mensagem do usuário
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Fazer requisição ao assistente
        try:
            with st.spinner("🤖 Pensando..."):
                response = requests.post(
                    f"{API_BASE_URL}/ai/ask",
                    json={"question": prompt, "provider": provider},
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_response = data.get("response", "Sem resposta.")
                    provider_used = data.get("provider", "desconhecido")

                    # Adicionar resposta ao histórico
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": f"{assistant_response}\n\n*✨ Respondido por: {provider_used}*",
                        }
                    )

                else:
                    error_msg = "❌ Falha ao consultar o assistente. Tente novamente."
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

        except requests.exceptions.RequestException as exc:
            error_msg = f"❌ Erro de conexão: {str(exc)}"
            st.session_state.chat_history.append(
                {"role": "assistant", "content": error_msg}
            )

        # Recarregar para exibir nova mensagem
        st.rerun()

    # Sugestões de perguntas (se histórico vazio)
    if not st.session_state.chat_history:
        st.markdown("### 💡 Perguntas Sugeridas")
        col1, col2, col3 = st.columns(3)

        suggestions = [
            "📊 Como está meu consumo hoje?",
            "💰 Qual dispositivo gasta mais?",
            "⚡ Dê dicas de economia",
        ]

        for col, suggestion in zip([col1, col2, col3], suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state.chat_history.append(
                        {"role": "user", "content": suggestion}
                    )
                    st.rerun()


# Fluxo principal com tabs
smartlife_data = load_smartlife_data()

tab_tapo, tab_smartlife, tab_assistant = st.tabs(
    ["🔌 TP-Link Tapo", "📱 SmartLife", "🤖 Assistente"]
)

with tab_tapo:
    render_tapo_dashboard()

with tab_smartlife:
    render_smartlife_dashboard(smartlife_data)

with tab_assistant:
    render_chat_assistant()

# Auto refresh apenas na aba principal
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        🏠 Casa Inteligente Dashboard | Desenvolvido com ❤️ por Patricia Menezes
    </div>
    """,
    unsafe_allow_html=True,
)
