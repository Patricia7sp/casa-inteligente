import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { DeviceOverview } from '../../types';
import { deviceColor } from '../../lib/colors';
import { formatWatts } from '../../lib/format';
import { ChartTooltip } from './ChartTooltip';
import { ChartLegend } from './ChartLegend';

interface DevicePieChartProps {
  devices: DeviceOverview[];
}

export function DevicePieChart({ devices }: DevicePieChartProps) {
  const total = devices.reduce((sum, d) => sum + Math.max(d.current_power_watts, 0), 0);
  const data = devices
    .filter((d) => d.current_power_watts > 0)
    .map((d, i) => ({
      key: String(d.id),
      name: d.display_name,
      value: d.current_power_watts,
      color: deviceColor(d.color, i),
    }));

  if (data.length === 0) {
    return <p className="py-16 text-center text-sm text-ink-muted">Sem potência ativa no momento.</p>;
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={0} outerRadius={95} paddingAngle={1.5}>
            {data.map((entry) => (
              <Cell key={entry.key} fill={entry.color} stroke="#1a1a19" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const p = payload[0];
              const row = p.payload as { name: string; value: number; color: string };
              const pct = total > 0 ? ((row.value / total) * 100).toFixed(1) : '0';
              return (
                <ChartTooltip
                  rows={[
                    { key: 'v', label: row.name, value: `${formatWatts(row.value)} · ${pct}%`, color: row.color },
                  ]}
                />
              );
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <ChartLegend items={data.map((d) => ({ key: d.key, label: d.name, color: d.color }))} />
    </div>
  );
}
