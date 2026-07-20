"""
Cliente HTTP simples para acesso direto ao Supabase via REST API.

Extraído de `src/main.py` para evitar duplicação e permitir reuso por
`src/services/energy_service.py` sem causar import circular (main.py já
importa energy_service no topo do arquivo).
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from src.utils.config import settings

logger = logging.getLogger(__name__)

# Configuração do Supabase (mesmos fallbacks hardcoded que já existiam em src/main.py)
SUPABASE_URL = getattr(
    settings,
    "supabase_url",
    "https://pqqrodiuuhckvdqawgeg.supabase.co",
)
SUPABASE_KEY = getattr(
    settings,
    "supabase_anon_key",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBxcXJvZGl1dWhja3ZkcWF3Z2VnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI0OTI0MTIsImV4cCI6MjA3ODA2ODQxMn0.ve7NIbFcZdTGa16O3Pttmpx2mxWgklvbPwwTSCHuDFs",
)


def get_supabase_data(
    endpoint: str, params: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    """Buscar dados do Supabase via REST API.

    Retorna sempre uma lista (vazia em caso de erro de rede ou status != 200),
    mantendo o mesmo comportamento da função original em src/main.py.
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao buscar {endpoint}: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
        return []


def save_to_supabase(endpoint: str, data: dict) -> bool:
    """Salvar dados no Supabase via REST API."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        logger.error(f"Erro ao salvar no Supabase: {str(e)}")
        return False
