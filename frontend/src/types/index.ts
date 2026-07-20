// Tipos alinhados ao contrato fixo da API FastAPI (ver spec no README do backend).

export type Period = 24 | 7 | 30 | 90;

// ---------- /energy/overview ----------

export interface EnergySummary {
  total_power_watts: number;
  active_devices: number;
  total_devices: number;
  last_reading_minutes_ago: number | null;
  source: 'supabase' | 'unavailable';
}

export interface DeviceOverview {
  id: number;
  name: string;
  display_name: string;
  profile_key: 'purificador' | 'notebook' | null;
  icon: string;
  color: string;
  location: string | null;
  equipment_connected: string | null;
  ip_address: string | null;
  is_active: boolean;
  current_power_watts: number;
}

export interface EnergyOverview {
  summary: EnergySummary;
  devices: DeviceOverview[];
}

// ---------- /energy/history ----------

export interface HistoryPoint {
  timestamp: string;
  power_watts: number;
}

export interface DeviceHistorySeries {
  device_id: number;
  display_name: string;
  color: string;
  points: HistoryPoint[];
}

export interface EnergyHistory {
  days: number;
  series: DeviceHistorySeries[];
}

// ---------- /energy/daily ----------

export interface DailyPoint {
  date: string;
  energy_kwh: number;
  cost_brl: number;
}

export interface DailyTotals {
  avg_daily_kwh: number;
  avg_daily_cost_brl: number;
  last7_kwh: number;
  last7_cost_brl: number;
  last30_kwh: number;
  last30_cost_brl: number;
}

export interface EnergyDaily {
  daily: DailyPoint[];
  totals: DailyTotals;
}

// ---------- /energy/monthly ----------

export interface MonthlyPoint {
  month: string;
  label: string;
  energy_kwh: number;
  cost_brl: number;
}

export interface EnergyMonthly {
  monthly: MonthlyPoint[];
}

// ---------- /energy/projections ----------

export interface DeviceProjection {
  device_id: number;
  display_name: string;
  color: string;
  daily_kwh: number;
  weekly_kwh: number;
  monthly_kwh: number;
  monthly_cost_brl: number;
}

export interface ProjectionTotal {
  daily_kwh: number;
  weekly_kwh: number;
  monthly_kwh: number;
  monthly_cost_brl: number;
}

export interface EnergyProjections {
  devices: DeviceProjection[];
  total: ProjectionTotal;
}

// ---------- /energy/devices/{id} ----------

export interface DeviceAnomaly {
  has_spike: boolean;
  message: string;
}

export interface EnergySeriesPoint {
  timestamp: string;
  energy_today_kwh: number;
}

export interface CostSeriesPoint {
  timestamp: string;
  cost_estimado: number;
}

export interface DeviceDetail {
  device_id: number;
  display_name: string;
  color: string;
  current_power_watts: number;
  last_reading_minutes_ago: number | null;
  energy_today_kwh: number | null;
  cost_today_brl: number | null;
  avg_power_watts: number;
  peak_power_watts: number;
  anomaly: DeviceAnomaly;
  power_series: HistoryPoint[];
  energy_series: EnergySeriesPoint[];
  cost_series: CostSeriesPoint[];
}

// ---------- /smartlife/latest ----------

export interface WeeklyConsumptionPoint {
  date: string;
  consumption: number;
}

// Linha da tabela de classificação — shape flexível pois vem direto do backend.
export type ConsumptionRankRow = Record<string, string | number>;

export interface SmartLifeMetrics {
  daily_average_kwh: number;
  estimated_monthly_cost_brl: number;
  monthly_projection_kwh: number;
  status: string;
  weekly_consumption_kwh: WeeklyConsumptionPoint[];
  consumption_rank: ConsumptionRankRow[];
  runtime_hours: Record<string, number>;
}

export interface SmartLifeData {
  metrics: SmartLifeMetrics;
  recommendations: string[];
}

// A API pode retornar {} quando não há dados importados ainda.
export type SmartLifeResponse = SmartLifeData | Record<string, never>;

// ---------- /ai/ask ----------

export type AiProvider = 'auto' | 'openai' | 'gemini';

export interface AskRequest {
  question: string;
  provider: AiProvider;
}

export interface AskResponse {
  response: string;
  provider: string;
}

export interface ApiErrorBody {
  detail: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  provider?: string;
  isError?: boolean;
}
