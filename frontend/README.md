# Casa Inteligente — Frontend

SPA em React + Vite + TypeScript + Tailwind CSS que substitui o antigo dashboard em
Streamlit (`dashboard.py`), consumindo a API FastAPI descrita no backend do projeto.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # ajuste VITE_API_BASE_URL se o backend não estiver em localhost:8000
npm run dev
```

Abra http://localhost:5173. Sem o backend rodando (ou sem dados no Supabase), as telas
mostram estados de erro/vazio dedicados em vez de quebrar.

## Variáveis de ambiente

| Variável             | Padrão                    | Descrição                            |
| --------------------- | -------------------------- | -------------------------------------- |
| `VITE_API_BASE_URL`   | `http://localhost:8000`   | Base URL da API FastAPI do backend.    |

## Scripts

- `npm run dev` — servidor de desenvolvimento com HMR.
- `npm run build` — type-check (`tsc -b`) + build de produção em `dist/`.
- `npm run preview` — serve o build de produção localmente.
- `npm run lint` — lint com oxlint.

## Estrutura

```
src/
  components/        componentes de UI (tabelas, chat) e components/charts (Recharts)
  components/common/ primitivas genéricas: Card, StatTile, EmptyState, ErrorState, etc.
  lib/                cliente HTTP (api.ts), hook de fetch (useFetch.ts), formatação, cores, período
  pages/              as 3 abas: DevicesPage, SmartLifePage, AssistantPage
  types/              tipos alinhados ao contrato da API
```

## Design

Dark theme seguindo os tokens da skill `dataviz` (superfícies, tinta primária/secundária/muted,
paleta de status com ícone+texto, par energia=azul / custo=vermelho, cor por dispositivo vinda
da API). Nenhum gráfico usa eixo Y duplo; consumo e custo diários são sempre dois gráficos
separados e empilhados.
