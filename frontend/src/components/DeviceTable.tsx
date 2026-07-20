import type { DeviceOverview } from '../types';
import { deviceColor } from '../lib/colors';
import { formatWatts } from '../lib/format';
import { StatusBadge } from './common/StatusBadge';

interface DeviceTableProps {
  devices: DeviceOverview[];
}

export function DeviceTable({ devices }: DeviceTableProps) {
  if (devices.length === 0) {
    return <p className="py-10 text-center text-sm text-ink-muted">Nenhum dispositivo cadastrado.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-ink-muted">
            <th className="py-2 pr-3 font-medium">Dispositivo</th>
            <th className="py-2 pr-3 font-medium">IP</th>
            <th className="py-2 pr-3 font-medium">Local</th>
            <th className="py-2 pr-3 font-medium">Equipamento</th>
            <th className="py-2 pr-3 text-right font-medium">Consumo</th>
            <th className="py-2 pl-3 text-right font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {devices.map((d, i) => (
            <tr key={d.id} className="border-b border-white/5 last:border-0">
              <td className="py-2.5 pr-3">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block size-2.5 shrink-0 rounded-full"
                    style={{ background: deviceColor(d.color, i) }}
                  />
                  <span className="font-medium text-ink-primary">{d.display_name}</span>
                </div>
              </td>
              <td className="py-2.5 pr-3 tabular text-ink-secondary">{d.ip_address ?? '—'}</td>
              <td className="py-2.5 pr-3 text-ink-secondary">{d.location ?? '—'}</td>
              <td className="py-2.5 pr-3 text-ink-secondary">{d.equipment_connected ?? '—'}</td>
              <td className="tabular py-2.5 pr-3 text-right font-medium text-ink-primary">
                {formatWatts(d.current_power_watts)}
              </td>
              <td className="py-2.5 pl-3 text-right">
                {d.is_active ? (
                  <StatusBadge level="good" text="Ativo" />
                ) : (
                  <StatusBadge level="neutral" text="Inativo" />
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
