import { AlertTriangle, CheckCircle2, Info, OctagonAlert } from 'lucide-react';

export type StatusLevel = 'good' | 'warning' | 'serious' | 'critical' | 'neutral';

const CONFIG: Record<StatusLevel, { icon: typeof CheckCircle2; color: string; bg: string }> = {
  good: { icon: CheckCircle2, color: 'text-status-good', bg: 'bg-status-good/10' },
  warning: { icon: AlertTriangle, color: 'text-status-warning', bg: 'bg-status-warning/10' },
  serious: { icon: AlertTriangle, color: 'text-status-serious', bg: 'bg-status-serious/10' },
  critical: { icon: OctagonAlert, color: 'text-status-critical', bg: 'bg-status-critical/10' },
  neutral: { icon: Info, color: 'text-ink-secondary', bg: 'bg-white/5' },
};

interface StatusBadgeProps {
  level: StatusLevel;
  text: string;
  className?: string;
}

// Nunca comunica só por cor: ícone + texto sempre juntos.
export function StatusBadge({ level, text, className = '' }: StatusBadgeProps) {
  const { icon: Icon, color, bg } = CONFIG[level];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${color} ${bg} ${className}`}
    >
      <Icon size={13} strokeWidth={2.25} />
      {text}
    </span>
  );
}
