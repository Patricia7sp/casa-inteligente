import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { colors } from '../../lib/colors';
import { ChartTooltip } from './ChartTooltip';

export interface BarDatum {
  x: string;
  y: number;
}

interface SingleSeriesBarChartProps {
  data: BarDatum[];
  color: string;
  seriesLabel: string;
  xFormatter?: (x: string) => string;
  yFormatter: (y: number) => string;
  yTickFormatter?: (y: number) => string;
  height?: number;
  emptyMessage?: string;
}

export function SingleSeriesBarChart({
  data,
  color,
  seriesLabel,
  xFormatter = (x) => x,
  yFormatter,
  yTickFormatter,
  height = 220,
  emptyMessage = 'Sem dados no período.',
}: SingleSeriesBarChartProps) {
  if (data.length === 0) {
    return <p className="py-16 text-center text-sm text-ink-muted">{emptyMessage}</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} barCategoryGap="25%" margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke={colors.grid} />
        <XAxis
          dataKey="x"
          tickFormatter={xFormatter}
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={{ stroke: colors.baseline }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: colors.inkMuted, fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={48}
          tickFormatter={yTickFormatter ?? yFormatter}
        />
        <Tooltip
          cursor={{ fill: 'rgba(255,255,255,0.04)' }}
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
        <Bar dataKey="y" name={seriesLabel} fill={color} radius={[4, 4, 0, 0]} maxBarSize={24} />
      </BarChart>
    </ResponsiveContainer>
  );
}
