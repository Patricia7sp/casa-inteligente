import { Activity, Clock, Gauge, Zap } from 'lucide-react';
import { api } from '../lib/api';
import { useFetch } from '../lib/useFetch';
import { formatCurrency, formatKwh, formatMinutesAgo, formatTimeShort, formatWatts } from '../lib/format';
import type { Period } from '../types';
import { periodToDays } from '../lib/period';
import { CardSkeleton } from './common/LoadingState';
import { ErrorState } from './common/ErrorState';
import { StatusBadge } from './common/StatusBadge';
import { SingleSeriesAreaChart } from './charts/SingleSeriesAreaChart';
import { seriesColors } from '../lib/colors';

interface DeviceMonitorProps {
  deviceId: number;
  period: Period;
  tariff: number;
}

export function DeviceMonitor({ deviceId, period, tariff }: DeviceMonitorProps) {
  const days = periodToDays(period);
  const { data, loading, error, refetch } = useFetch(
    () => api.getDevice(deviceId, days, tariff),
    [deviceId, days, tariff],
  );

  if (loading && !data) {
    return (
      <div className="grid gap-4 lg:grid-cols-3">
        <CardSkeleton height={180} />
        <CardSkeleton height={180} />
        <CardSkeleton height={180} />
      </div>
    );
  }

  if (error && !data) {
    return <ErrorState message={error} onRetry={refetch} compact />;
  }

  if (!data) return null;

  const metrics = [
    { label: 'Potência atual', value: formatWatts(data.current_power_watts), icon: Zap },
    {
      label: 'Última leitura',
      value: formatMinutesAgo(data.last_reading_minutes_ago),
      icon: Clock,
    },
    { label: 'Energia hoje', value: formatKwh(data.energy_today_kwh ?? 0), icon: Activity },
    { label: 'Custo hoje', value: formatCurrency(data.cost_today_brl ?? 0), icon: Gauge },
    { label: 'Potência média', value: formatWatts(data.avg_power_watts), icon: Activity },
    { label: 'Pico de potência', value: formatWatts(data.peak_power_watts), icon: Zap },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-block size-2.5 rounded-full" style={{ background: data.color }} />
          <h4 className="text-sm font-semibold text-ink-primary">{data.display_name}</h4>
        </div>
        {data.anomaly.has_spike ? (
          <StatusBadge level="warning" text={data.anomaly.message} />
        ) : (
          <StatusBadge level="good" text={data.anomaly.message || 'Consumo dentro do esperado'} />
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-xl border border-white/10 bg-surface-raised p-3">
            <div className="flex items-center gap-1.5 text-ink-muted">
              <m.icon size={13} />
              <span className="text-[11px] uppercase tracking-wide">{m.label}</span>
            </div>
            <p className="tabular mt-1.5 text-sm font-semibold text-ink-primary">{m.value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-surface-raised p-4">
          <p className="mb-2 text-xs font-medium text-ink-secondary">Potência (W)</p>
          <SingleSeriesAreaChart
            data={data.power_series.map((p) => ({ x: p.timestamp, y: p.power_watts }))}
            color={data.color}
            seriesLabel="Potência"
            xFormatter={formatTimeShort}
            yFormatter={(v) => formatWatts(v)}
            yTickFormatter={(v) => `${v}W`}
            height={190}
          />
        </div>
        <div className="rounded-xl border border-white/10 bg-surface-raised p-4">
          <p className="mb-2 text-xs font-medium text-ink-secondary">Energia acumulada (kWh)</p>
          <SingleSeriesAreaChart
            data={data.energy_series.map((p) => ({ x: p.timestamp, y: p.energy_today_kwh }))}
            color={seriesColors.energy}
            seriesLabel="Energia"
            xFormatter={formatTimeShort}
            yFormatter={(v) => formatKwh(v)}
            height={190}
          />
        </div>
        <div className="rounded-xl border border-white/10 bg-surface-raised p-4">
          <p className="mb-2 text-xs font-medium text-ink-secondary">Custo acumulado (R$)</p>
          <SingleSeriesAreaChart
            data={data.cost_series.map((p) => ({ x: p.timestamp, y: p.cost_estimado }))}
            color={seriesColors.cost}
            seriesLabel="Custo"
            xFormatter={formatTimeShort}
            yFormatter={(v) => formatCurrency(v)}
            height={190}
          />
        </div>
      </div>
    </div>
  );
}
