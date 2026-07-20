import { useEffect, useMemo, useState } from 'react';
import { Activity, CalendarClock, Gauge, Plug, Power, Zap } from 'lucide-react';
import { api } from '../lib/api';
import { useFetch } from '../lib/useFetch';
import { periodToDays, periodLabel } from '../lib/period';
import { formatCurrency, formatDateShort, formatKwh, formatMinutesAgo, formatWatts } from '../lib/format';
import { seriesColors } from '../lib/colors';
import type { Period } from '../types';
import { Card } from '../components/common/Card';
import { SectionHeader } from '../components/common/SectionHeader';
import { StatTile } from '../components/common/StatTile';
import { StatTileSkeleton, CardSkeleton } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { StatusBadge } from '../components/common/StatusBadge';
import { DevicePowerBarChart } from '../components/charts/DevicePowerBarChart';
import { DevicePieChart } from '../components/charts/DevicePieChart';
import { PowerHistoryChart } from '../components/charts/PowerHistoryChart';
import { SingleSeriesAreaChart } from '../components/charts/SingleSeriesAreaChart';
import { SingleSeriesBarChart } from '../components/charts/SingleSeriesBarChart';
import { DeviceTable } from '../components/DeviceTable';
import { ProjectionsTable } from '../components/ProjectionsTable';
import { DeviceMonitor } from '../components/DeviceMonitor';

interface DevicesPageProps {
  period: Period;
  tariff: number;
}

export function DevicesPage({ period, tariff }: DevicesPageProps) {
  const days = periodToDays(period);

  const overview = useFetch(() => api.getOverview(tariff), [tariff]);
  const history = useFetch(() => api.getHistory(days), [days]);
  const daily = useFetch(() => api.getDaily(Math.max(days, 30), tariff), [days, tariff]);
  const monthly = useFetch(() => api.getMonthly(tariff), [tariff]);
  const projections = useFetch(() => api.getProjections(tariff), [tariff]);

  const [selectedDeviceId, setSelectedDeviceId] = useState<number | null>(null);

  const devices = useMemo(() => overview.data?.devices ?? [], [overview.data]);
  const firstDeviceId = devices[0]?.id ?? null;

  useEffect(() => {
    if (firstDeviceId !== null && selectedDeviceId === null) {
      setSelectedDeviceId(firstDeviceId);
    }
  }, [firstDeviceId, selectedDeviceId]);

  const summary = overview.data?.summary;

  const dailyChartData = useMemo(
    () => (daily.data?.daily ?? []).map((d) => ({ x: d.date, y: d.energy_kwh })),
    [daily.data],
  );
  const costChartData = useMemo(
    () => (daily.data?.daily ?? []).map((d) => ({ x: d.date, y: d.cost_brl })),
    [daily.data],
  );
  const monthlyKwhData = useMemo(
    () => (monthly.data?.monthly ?? []).map((m) => ({ x: m.label, y: m.energy_kwh })),
    [monthly.data],
  );
  const monthlyCostData = useMemo(
    () => (monthly.data?.monthly ?? []).map((m) => ({ x: m.label, y: m.cost_brl })),
    [monthly.data],
  );

  return (
    <div className="flex flex-col gap-8">
      {/* Resumo */}
      <section>
        <SectionHeader title="Visão geral" subtitle="Estado atual das tomadas TP-Link Tapo" />
        {overview.loading && !overview.data ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <StatTileSkeleton key={i} />
            ))}
          </div>
        ) : overview.error && !overview.data ? (
          <ErrorState message={overview.error} onRetry={overview.refetch} />
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatTile
              label="Potência total"
              value={formatWatts(summary?.total_power_watts ?? 0)}
              icon={Zap}
              accentClassName="text-series-energy"
            />
            <StatTile
              label="Dispositivos ativos"
              value={`${summary?.active_devices ?? 0} / ${summary?.total_devices ?? 0}`}
              icon={Plug}
              accentClassName="text-status-good"
            />
            <StatTile
              label="Status do sistema"
              value={summary?.source === 'supabase' ? 'Online' : 'Indisponível'}
              icon={Power}
              accentClassName={summary?.source === 'supabase' ? 'text-status-good' : 'text-status-critical'}
              trend={
                summary?.source === 'supabase' ? (
                  <StatusBadge level="good" text="Conectado" />
                ) : (
                  <StatusBadge level="critical" text="Sem conexão" />
                )
              }
            />
            <StatTile
              label="Última atualização"
              value={formatMinutesAgo(summary?.last_reading_minutes_ago ?? null)}
              icon={CalendarClock}
            />
          </div>
        )}
      </section>

      {/* Potência por dispositivo */}
      {overview.data && devices.length > 0 && (
        <section className="grid gap-4 lg:grid-cols-2">
          <Card title="Potência atual por dispositivo" subtitle="Comparativo instantâneo em watts">
            <DevicePowerBarChart devices={devices} />
          </Card>
          <Card title="Distribuição de potência" subtitle="Participação de cada dispositivo no total">
            <DevicePieChart devices={devices} />
          </Card>
        </section>
      )}

      {/* Histórico de potência */}
      <section>
        <SectionHeader title="Histórico de potência" subtitle={`Todas as leituras ${periodLabel(period)}`} />
        <Card>
          {history.loading && !history.data ? (
            <CardSkeleton height={300} />
          ) : history.error && !history.data ? (
            <ErrorState message={history.error} onRetry={history.refetch} compact />
          ) : (
            <PowerHistoryChart series={history.data?.series ?? []} />
          )}
        </Card>
      </section>

      {/* Consumo diário */}
      <section>
        <SectionHeader
          title="Consumo diário"
          subtitle="Energia e custo por dia — gráficos separados (nunca eixo duplo)"
        />
        {daily.loading && !daily.data ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : daily.error && !daily.data ? (
          <ErrorState message={daily.error} onRetry={daily.refetch} compact />
        ) : (
          <>
            <div className="grid gap-4 lg:grid-cols-2">
              <Card title="Energia diária (kWh)">
                <SingleSeriesAreaChart
                  data={dailyChartData}
                  color={seriesColors.energy}
                  seriesLabel="Energia"
                  xFormatter={formatDateShort}
                  yFormatter={(v) => formatKwh(v)}
                />
              </Card>
              <Card title="Custo diário (R$)">
                <SingleSeriesAreaChart
                  data={costChartData}
                  color={seriesColors.cost}
                  seriesLabel="Custo"
                  xFormatter={formatDateShort}
                  yFormatter={(v) => formatCurrency(v)}
                />
              </Card>
            </div>

            {daily.data?.totals && (
              <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <StatTile label="Média diária" value={formatKwh(daily.data.totals.avg_daily_kwh)} icon={Activity} />
                <StatTile
                  label="Custo médio/dia"
                  value={formatCurrency(daily.data.totals.avg_daily_cost_brl)}
                  icon={Gauge}
                />
                <StatTile label="Últimos 7 dias" value={formatKwh(daily.data.totals.last7_kwh)} icon={Activity} />
                <StatTile label="Últimos 30 dias" value={formatKwh(daily.data.totals.last30_kwh)} icon={Activity} />
              </div>
            )}
          </>
        )}
      </section>

      {/* Totais mensais */}
      <section>
        <SectionHeader title="Totais mensais" />
        {monthly.loading && !monthly.data ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : monthly.error && !monthly.data ? (
          <ErrorState message={monthly.error} onRetry={monthly.refetch} compact />
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="Energia mensal (kWh)">
              <SingleSeriesBarChart
                data={monthlyKwhData}
                color={seriesColors.energy}
                seriesLabel="Energia"
                yFormatter={(v) => formatKwh(v)}
              />
            </Card>
            <Card title="Custo mensal (R$)">
              <SingleSeriesBarChart
                data={monthlyCostData}
                color={seriesColors.cost}
                seriesLabel="Custo"
                yFormatter={(v) => formatCurrency(v)}
              />
            </Card>
          </div>
        )}
      </section>

      {/* Tabela de dispositivos */}
      <section>
        <SectionHeader title="Dispositivos" />
        <Card>
          {overview.loading && !overview.data ? (
            <CardSkeleton height={160} />
          ) : overview.error && !overview.data ? (
            <ErrorState message={overview.error} onRetry={overview.refetch} compact />
          ) : (
            <DeviceTable devices={devices} />
          )}
        </Card>
      </section>

      {/* Projeções */}
      <section>
        <SectionHeader title="Projeções" subtitle="Estimativas diária / semanal / mensal por dispositivo" />
        <Card>
          {projections.loading && !projections.data ? (
            <CardSkeleton height={160} />
          ) : projections.error && !projections.data ? (
            <ErrorState message={projections.error} onRetry={projections.refetch} compact />
          ) : (
            <ProjectionsTable projections={projections.data!} />
          )}
        </Card>
      </section>

      {/* Monitoramento individual */}
      <section>
        <SectionHeader
          title="Monitoramento individual"
          subtitle="Métricas, histórico e detecção de anomalia por dispositivo"
          actions={
            devices.length > 0 && (
              <select
                value={selectedDeviceId ?? ''}
                onChange={(e) => setSelectedDeviceId(Number(e.target.value))}
                className="rounded-lg border border-white/10 bg-surface px-3 py-1.5 text-sm text-ink-primary outline-none"
              >
                {devices.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.display_name}
                  </option>
                ))}
              </select>
            )
          }
        />
        <Card>
          {devices.length === 0 ? (
            <p className="py-10 text-center text-sm text-ink-muted">Nenhum dispositivo disponível para monitorar.</p>
          ) : selectedDeviceId !== null ? (
            <DeviceMonitor deviceId={selectedDeviceId} period={period} tariff={tariff} />
          ) : null}
        </Card>
      </section>
    </div>
  );
}
