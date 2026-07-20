import { useMemo } from 'react';
import { Activity, CalendarRange, Smartphone, TrendingUp } from 'lucide-react';
import { api } from '../lib/api';
import { useFetch } from '../lib/useFetch';
import { formatCurrency, formatDateShort, formatKwh } from '../lib/format';
import { seriesColors } from '../lib/colors';
import type { SmartLifeData } from '../types';
import { Card } from '../components/common/Card';
import { SectionHeader } from '../components/common/SectionHeader';
import { StatTile } from '../components/common/StatTile';
import { StatTileSkeleton, CardSkeleton } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import { SingleSeriesAreaChart } from '../components/charts/SingleSeriesAreaChart';
import { SingleSeriesBarChart } from '../components/charts/SingleSeriesBarChart';
import { GenericTable } from '../components/GenericTable';

function isSmartLifeData(data: unknown): data is SmartLifeData {
  return Boolean(data) && typeof data === 'object' && 'metrics' in (data as object);
}

export function SmartLifePage() {
  const { data, loading, error, refetch } = useFetch(() => api.getSmartLifeLatest(), []);

  const smartlife = isSmartLifeData(data) ? data : null;

  const weeklyData = useMemo(
    () =>
      (smartlife?.metrics.weekly_consumption_kwh ?? []).map((p) => ({
        x: p.date,
        y: p.consumption,
      })),
    [smartlife],
  );

  const runtimeData = useMemo(() => {
    const entries = Object.entries(smartlife?.metrics.runtime_hours ?? {});
    return entries.map(([periodo, horas]) => ({ x: periodo, y: horas }));
  }, [smartlife]);

  if (loading && !data) {
    return (
      <div className="flex flex-col gap-8">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <StatTileSkeleton key={i} />
          ))}
        </div>
        <CardSkeleton height={260} />
      </div>
    );
  }

  if (error && !data) {
    return <ErrorState message={error} onRetry={refetch} />;
  }

  if (!smartlife) {
    return (
      <EmptyState
        icon={Smartphone}
        title="Nenhum dado do SmartLife importado ainda"
        description={
          <>
            Os dados do app SmartLife são importados por e-mail. Rode{' '}
            <code className="rounded bg-white/10 px-1.5 py-0.5 text-ink-secondary">
              python scripts/gmail_polling.py
            </code>{' '}
            para buscar as importações mais recentes e depois recarregue esta página.
          </>
        }
      />
    );
  }

  const { metrics, recommendations } = smartlife;
  const statusLevel = metrics.status === 'normal' ? 'good' : 'warning';

  return (
    <div className="flex flex-col gap-8">
      <section>
        <SectionHeader title="Visão geral" subtitle="Dados importados do app SmartLife" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatTile
            label="Consumo diário médio"
            value={formatKwh(metrics.daily_average_kwh)}
            icon={Activity}
            accentClassName="text-series-energy"
          />
          <StatTile
            label="Custo mensal estimado"
            value={formatCurrency(metrics.estimated_monthly_cost_brl)}
            icon={CalendarRange}
            accentClassName="text-series-cost"
          />
          <StatTile
            label="Projeção mensal"
            value={formatKwh(metrics.monthly_projection_kwh)}
            icon={TrendingUp}
          />
          <StatTile
            label="Status"
            value={metrics.status}
            icon={Smartphone}
            trend={<StatusBadge level={statusLevel} text={metrics.status} />}
          />
        </div>
      </section>

      <section>
        <SectionHeader title="Consumo semanal" />
        <Card>
          <SingleSeriesAreaChart
            data={weeklyData}
            color={seriesColors.energy}
            seriesLabel="Consumo"
            xFormatter={formatDateShort}
            yFormatter={(v) => formatKwh(v)}
            emptyMessage="Sem histórico semanal disponível."
          />
        </Card>
      </section>

      <section>
        <SectionHeader title="Classificação do mês" />
        <Card>
          <GenericTable rows={metrics.consumption_rank} />
        </Card>
      </section>

      <section>
        <SectionHeader title="Tempo de uso (h)" />
        <Card>
          <SingleSeriesBarChart
            data={runtimeData}
            color={seriesColors.energy}
            seriesLabel="Horas"
            yFormatter={(v) => `${v.toLocaleString('pt-BR')} h`}
            emptyMessage="Sem dados de tempo de uso."
          />
        </Card>
      </section>

      <section>
        <SectionHeader title="Recomendações" />
        <Card>
          {recommendations.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-ink-secondary">
                  <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-series-energy" />
                  {rec}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-ink-muted">Nenhuma recomendação adicional no momento.</p>
          )}
        </Card>
      </section>
    </div>
  );
}
