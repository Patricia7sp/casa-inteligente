import type { LucideIcon } from 'lucide-react';
import { Inbox } from 'lucide-react';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: ReactNode;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon = Inbox, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-white/10 px-6 py-14 text-center">
      <span className="grid size-12 place-items-center rounded-full bg-white/5 text-ink-muted">
        <Icon size={22} strokeWidth={1.75} />
      </span>
      <div>
        <p className="text-sm font-medium text-ink-secondary">{title}</p>
        {description && <div className="mt-1 max-w-md text-xs text-ink-muted">{description}</div>}
      </div>
      {action}
    </div>
  );
}
