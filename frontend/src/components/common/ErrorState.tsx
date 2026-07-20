import { RefreshCw, WifiOff } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  compact?: boolean;
}

export function ErrorState({ message, onRetry, compact = false }: ErrorStateProps) {
  if (compact) {
    return (
      <div className="flex items-center justify-between gap-3 rounded-xl border border-status-critical/30 bg-status-critical/10 px-4 py-3 text-sm text-ink-secondary">
        <div className="flex items-center gap-2">
          <WifiOff size={16} className="shrink-0 text-status-critical" />
          <span>{message}</span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1 rounded-lg border border-white/10 px-2.5 py-1 text-xs font-medium text-ink-secondary hover:bg-white/5"
          >
            <RefreshCw size={12} />
            Tentar novamente
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-status-critical/20 bg-status-critical/5 px-6 py-14 text-center">
      <span className="grid size-12 place-items-center rounded-full bg-status-critical/10 text-status-critical">
        <WifiOff size={22} strokeWidth={1.75} />
      </span>
      <div>
        <p className="text-sm font-medium text-ink-secondary">Não foi possível carregar os dados</p>
        <p className="mt-1 max-w-md text-xs text-ink-muted">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-ink-secondary hover:bg-white/5"
        >
          <RefreshCw size={13} />
          Tentar novamente
        </button>
      )}
    </div>
  );
}
