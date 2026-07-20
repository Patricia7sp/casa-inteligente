import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { DeviceOverview } from '../../types';
import { colors, deviceColor } from '../../lib/colors';
import { formatWatts } from '../../lib/format';
import { ChartTooltip } from './ChartTooltip';

interface DevicePowerBarChartProps {
  devices: DeviceOverview[];
}

export function DevicePowerBarChart({ devices }: DevicePowerBarChartProps) {
  const data = devices.map((d, i) => ({
    name: d.display_name,
    value: d.current_power_watts,
    color: deviceColor(d.color, i),
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} barCategoryGap="30%" margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke={colors.grid} strokeDasharray="0" />
        <XAxis
          dataKey="name"
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={{ stroke: colors.baseline }}
          tickLine={false}
          interval={0}
          angle={data.length > 5 ? -20 : 0}
          textAnchor={data.length > 5 ? 'end' : 'middle'}
          height={data.length > 5 ? 46 : 28}
        />
        <YAxis
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={44}
          tickFormatter={(v: number) => `${v}W`}
        />
        <Tooltip
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const p = payload[0];
            const row = p.payload as { name: string; value: number; color: string };
            return (
              <ChartTooltip
                rows={[{ key: 'v', label: row.name, value: formatWatts(row.value), color: row.color }]}
              />
            );
          }}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={24}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
