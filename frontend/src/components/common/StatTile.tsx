import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface StatTileProps {
  label: string;
  value: string;
  hint?: string;
  icon?: LucideIcon;
  accentClassName?: string;
  trend?: ReactNode;
}

export function StatTile({ label, value, hint, icon: Icon, accentClassName, trend }: StatTileProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-surface p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-muted">{label}</span>
        {Icon && (
          <span
            className={`grid size-8 shrink-0 place-items-center rounded-lg bg-white/5 ${accentClassName ?? 'text-ink-secondary'}`}
          >
            <Icon size={16} strokeWidth={2} />
          </span>
        )}
      </div>
      <div className="mt-2 flex items-end justify-between gap-2">
        <span className="tabular text-2xl font-semibold text-ink-primary">{value}</span>
        {trend}
      </div>
      {hint && <p className="mt-1 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}
