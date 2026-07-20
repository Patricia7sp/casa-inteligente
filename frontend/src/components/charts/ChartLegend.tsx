interface LegendItem {
  key: string;
  label: string;
  color: string;
}

interface ChartLegendProps {
  items: LegendItem[];
  hidden?: Set<string>;
  onToggle?: (key: string) => void;
}

// Legenda sempre presente quando há >=2 séries. Quando `onToggle` é passado,
// funciona como toggle-to-isolate (clique esconde/mostra a série no gráfico).
export function ChartLegend({ items, hidden, onToggle }: ChartLegendProps) {
  if (items.length < 2) return null;
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5 pt-3">
      {items.map((item) => {
        const isHidden = hidden?.has(item.key) ?? false;
        const interactive = Boolean(onToggle);
        const Tag = interactive ? 'button' : 'div';
        return (
          <Tag
            key={item.key}
            type={interactive ? 'button' : undefined}
            onClick={interactive ? () => onToggle?.(item.key) : undefined}
            className={`flex items-center gap-1.5 text-xs ${
              isHidden ? 'text-ink-muted opacity-50' : 'text-ink-secondary'
            } ${interactive ? 'cursor-pointer hover:text-ink-primary' : ''}`}
          >
            <span
              className="inline-block h-2.5 w-2.5 shrink-0 rounded-sm"
              style={{ background: item.color }}
            />
            <span className="truncate max-w-[10rem]">{item.label}</span>
          </Tag>
        );
      })}
    </div>
  );
}
