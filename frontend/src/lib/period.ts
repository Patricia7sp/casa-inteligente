import type { Period } from '../types';

/**
 * A UI oferece 24h / 7d / 30d / 90d, mas os endpoints `days` da API só aceitam
 * dias inteiros. 24h mapeia para 1 dia (a menor granularidade suportada).
 */
export function periodToDays(period: Period): number {
  return period === 24 ? 1 : period;
}

export function periodLabel(period: Period): string {
  return period === 24 ? 'nas últimas 24 horas' : `nos últimos ${period} dias`;
}
