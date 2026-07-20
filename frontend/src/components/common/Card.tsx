import type { ReactNode } from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}

export function Card({ title, subtitle, actions, children, className = '', bodyClassName = '' }: CardProps) {
  return (
    <section
      className={`rounded-2xl border border-white/10 bg-surface shadow-[0_1px_0_rgba(255,255,255,0.04)_inset] ${className}`}
    >
      {(title || actions) && (
        <header className="flex items-start justify-between gap-4 px-5 pt-5">
          <div>
            {title && <h3 className="text-sm font-semibold text-ink-primary">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-ink-muted">{subtitle}</p>}
          </div>
          {actions && <div className="shrink-0">{actions}</div>}
        </header>
      )}
      <div className={`p-5 ${bodyClassName}`}>{children}</div>
    </section>
  );
}
