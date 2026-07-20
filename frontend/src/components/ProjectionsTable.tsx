import type { EnergyProjections } from '../types';
import { deviceColor } from '../lib/colors';
import { formatCurrency, formatKwh } from '../lib/format';

interface ProjectionsTableProps {
  projections: EnergyProjections;
}

export function ProjectionsTable({ projections }: ProjectionsTableProps) {
  const { devices, total } = projections;

  if (devices.length === 0) {
    return <p className="py-10 text-center text-sm text-ink-muted">Sem dados suficientes para projeção.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[560px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-ink-muted">
            <th className="py-2 pr-3 font-medium">Dispositivo</th>
            <th className="py-2 pr-3 text-right font-medium">Diário</th>
            <th className="py-2 pr-3 text-right font-medium">Semanal</th>
            <th className="py-2 pr-3 text-right font-medium">Mensal</th>
            <th className="py-2 pl-3 text-right font-medium">Custo mensal</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((d, i) => (
            <tr key={d.device_id} className="border-b border-white/5">
              <td className="py-2.5 pr-3">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block size-2.5 shrink-0 rounded-full"
                    style={{ background: deviceColor(d.color, i) }}
                  />
                  <span className="font-medium text-ink-primary">{d.display_name}</span>
                </div>
              </td>
              <td className="tabular py-2.5 pr-3 text-right text-ink-secondary">{formatKwh(d.daily_kwh)}</td>
              <td className="tabular py-2.5 pr-3 text-right text-ink-secondary">{formatKwh(d.weekly_kwh)}</td>
              <td className="tabular py-2.5 pr-3 text-right text-ink-secondary">{formatKwh(d.monthly_kwh)}</td>
              <td className="tabular py-2.5 pl-3 text-right font-medium text-ink-primary">
                {formatCurrency(d.monthly_cost_brl)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t border-white/10">
            <td className="py-2.5 pr-3 font-semibold text-ink-primary">Total</td>
            <td className="tabular py-2.5 pr-3 text-right font-semibold text-ink-primary">
              {formatKwh(total.daily_kwh)}
            </td>
            <td className="tabular py-2.5 pr-3 text-right font-semibold text-ink-primary">
              {formatKwh(total.weekly_kwh)}
            </td>
            <td className="tabular py-2.5 pr-3 text-right font-semibold text-ink-primary">
              {formatKwh(total.monthly_kwh)}
            </td>
            <td className="tabular py-2.5 pl-3 text-right font-semibold text-ink-primary">
              {formatCurrency(total.monthly_cost_brl)}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
