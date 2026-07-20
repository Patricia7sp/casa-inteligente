import type { Period } from '../../types';

const OPTIONS: { value: Period; label: string }[] = [
  { value: 24, label: '24h' },
  { value: 7, label: '7 dias' },
  { value: 30, label: '30 dias' },
  { value: 90, label: '90 dias' },
];

interface PeriodSelectorProps {
  value: Period;
  onChange: (value: Period) => void;
}

export function PeriodSelector({ value, onChange }: PeriodSelectorProps) {
  return (
    <div className="inline-flex rounded-xl border border-white/10 bg-surface p-1" role="tablist" aria-label="Período">
      {OPTIONS.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            role="tab"
            aria-selected={active}
            onClick={() => onChange(option.value)}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              active ? 'bg-white/10 text-ink-primary' : 'text-ink-muted hover:text-ink-secondary'
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
