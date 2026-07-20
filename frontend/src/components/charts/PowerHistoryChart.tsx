import { useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { DeviceHistorySeries } from '../../types';
import { colors, deviceColor } from '../../lib/colors';
import { formatDateTimeShort, formatWatts } from '../../lib/format';
import { ChartTooltip } from './ChartTooltip';
import { ChartLegend } from './ChartLegend';

interface PowerHistoryChartProps {
  series: DeviceHistorySeries[];
}

interface MergedPoint {
  timestamp: string;
  ts: number;
  [deviceKey: string]: number | string;
}

export function PowerHistoryChart({ series }: PowerHistoryChartProps) {
  const [hidden, setHidden] = useState<Set<string>>(new Set());

  const items = useMemo(
    () =>
      series.map((s, i) => ({
        key: `d${s.device_id}`,
        label: s.display_name,
        color: deviceColor(s.color, i),
      })),
    [series],
  );

  const data = useMemo<MergedPoint[]>(() => {
    const byTimestamp = new Map<string, MergedPoint>();
    series.forEach((s) => {
      const key = `d${s.device_id}`;
      s.points.forEach((p) => {
        const existing = byTimestamp.get(p.timestamp);
        const ts = new Date(p.timestamp).getTime();
        if (existing) {
          existing[key] = p.power_watts;
        } else {
          byTimestamp.set(p.timestamp, { timestamp: p.timestamp, ts, [key]: p.power_watts });
        }
      });
    });
    return Array.from(byTimestamp.values()).sort((a, b) => a.ts - b.ts);
  }, [series]);

  const toggle = (key: string) => {
    setHidden((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  if (data.length === 0) {
    return <p className="py-16 text-center text-sm text-ink-muted">Sem leituras de potência no período.</p>;
  }

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke={colors.grid} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={(v: string) => formatDateTimeShort(v)}
            tick={{ fill: colors.inkMuted, fontSize: 11 }}
            axisLine={{ stroke: colors.baseline }}
            tickLine={false}
            minTickGap={40}
          />
          <YAxis
            tick={{ fill: colors.inkMuted, fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={44}
            tickFormatter={(v: number) => `${v}W`}
          />
          <Tooltip
            cursor={{ stroke: colors.baseline, strokeWidth: 1 }}
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              const rows = items
                .filter((item) => !hidden.has(item.key))
                .map((item) => {
                  const entry = payload.find((p) => p.dataKey === item.key);
                  if (!entry || entry.value === undefined || entry.value === null) return null;
                  return {
                    key: item.key,
                    label: item.label,
                    value: formatWatts(entry.value as number),
                    color: item.color,
                  };
                })
                .filter((r): r is NonNullable<typeof r> => r !== null);
              if (rows.length === 0) return null;
              return <ChartTooltip title={formatDateTimeShort(label as string)} rows={rows} />;
            }}
          />
          {items.map((item) =>
            hidden.has(item.key) ? null : (
              <Line
                key={item.key}
                type="monotone"
                dataKey={item.key}
                name={item.label}
                stroke={item.color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5, strokeWidth: 2, stroke: colors.surface }}
                connectNulls
                isAnimationActive={false}
              />
            ),
          )}
        </LineChart>
      </ResponsiveContainer>
      <ChartLegend items={items} hidden={hidden} onToggle={toggle} />
    </div>
  );
}
