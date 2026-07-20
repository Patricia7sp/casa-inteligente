import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { colors } from '../../lib/colors';
import { ChartTooltip } from './ChartTooltip';

export interface SeriesDatum {
  x: string;
  y: number;
}

interface SingleSeriesAreaChartProps {
  data: SeriesDatum[];
  color: string;
  seriesLabel: string;
  xFormatter: (x: string) => string;
  yFormatter: (y: number) => string;
  yTickFormatter?: (y: number) => string;
  height?: number;
  emptyMessage?: string;
}

export function SingleSeriesAreaChart({
  data,
  color,
  seriesLabel,
  xFormatter,
  yFormatter,
  yTickFormatter,
  height = 220,
  emptyMessage = 'Sem dados no período.',
}: SingleSeriesAreaChartProps) {
  if (data.length === 0) {
    return <p className="py-16 text-center text-sm text-ink-muted">{emptyMessage}</p>;
  }

  const gradientId = `fill-${seriesLabel.replace(/\s+/g, '-').toLowerCase()}`;

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.22} />
            <stop offset="100%" stopColor={color} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke={colors.grid} />
        <XAxis
          dataKey="x"
          tickFormatter={xFormatter}
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={{ stroke: colors.baseline }}
          tickLine={false}
          minTickGap={30}
        />
        <YAxis
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={48}
          tickFormatter={yTickFormatter ?? yFormatter}
        />
        <Tooltip
          cursor={{ stroke: colors.baseline, strokeWidth: 1 }}
          content={({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            const value = payload[0]?.value;
            if (value === undefined || value === null) return null;
            return (
              <ChartTooltip
                title={xFormatter(label as string)}
                rows={[{ key: 's', label: seriesLabel, value: yFormatter(value as number), color }]}
              />
            );
          }}
        />
        <Area
          type="monotone"
          dataKey="y"
          name={seriesLabel}
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
          dot={false}
          activeDot={{ r: 5, strokeWidth: 2, stroke: colors.surface }}
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
