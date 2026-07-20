import { colors } from '../../lib/colors';

export interface TooltipRow {
  key: string;
  label: string;
  value: string;
  color: string;
}

interface ChartTooltipProps {
  title?: string;
  rows: TooltipRow[];
}

// Tooltip compartilhado: valor em destaque (Strong), nome da série secundário,
// identidade por "line key" (traço colorido) em vez de caixa preenchida.
export function ChartTooltip({ title, rows }: ChartTooltipProps) {
  if (rows.length === 0) return null;
  return (
    <div
      className="min-w-[9rem] rounded-lg border px-3 py-2 text-xs shadow-xl"
      style={{ background: colors.surfaceRaised, borderColor: colors.border }}
    >
      {title && <div className="mb-1.5 font-medium text-ink-muted">{title}</div>}
      <div className="flex flex-col gap-1">
        {rows.map((row) => (
          <div key={row.key} className="flex items-center gap-2">
            <span className="h-[2px] w-3 shrink-0 rounded-full" style={{ background: row.color }} />
            <span className="flex-1 truncate text-ink-secondary">{row.label}</span>
            <span className="tabular font-semibold text-ink-primary">{row.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
