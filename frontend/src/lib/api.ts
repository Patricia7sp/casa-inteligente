import type {
  AskRequest,
  AskResponse,
  EnergyDaily,
  EnergyHistory,
  EnergyMonthly,
  EnergyOverview,
  EnergyProjections,
  DeviceDetail,
  SmartLifeResponse,
} from '../types';

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') ||
  'http://localhost:8000';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new ApiError(
      'Não foi possível conectar à API. Verifique se o backend está em execução.',
      0,
    );
  }

  if (!res.ok) {
    let detail = `Erro ${res.status} ao consultar a API.`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // corpo não era JSON, mantém mensagem padrão
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return (await res.json()) as T;
}

export const api = {
  getOverview: (tariff: number) =>
    request<EnergyOverview>(`/energy/overview?tariff=${tariff}`),

  getHistory: (days: number) => request<EnergyHistory>(`/energy/history?days=${days}`),

  getDaily: (days: number, tariff: number) =>
    request<EnergyDaily>(`/energy/daily?days=${days}&tariff=${tariff}`),

  getMonthly: (tariff: number) => request<EnergyMonthly>(`/energy/monthly?tariff=${tariff}`),

  getProjections: (tariff: number) =>
    request<EnergyProjections>(`/energy/projections?tariff=${tariff}`),

  getDevice: (deviceId: number, days: number, tariff: number) =>
    request<DeviceDetail>(`/energy/devices/${deviceId}?days=${days}&tariff=${tariff}`),

  getSmartLifeLatest: () => request<SmartLifeResponse>('/smartlife/latest'),

  askAssistant: (payload: AskRequest) =>
    request<AskResponse>('/ai/ask', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

export { API_BASE_URL };
