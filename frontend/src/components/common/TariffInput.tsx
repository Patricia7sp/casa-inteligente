import { useState } from 'react';

interface TariffInputProps {
  value: number;
  onChange: (value: number) => void;
}

export function TariffInput({ value, onChange }: TariffInputProps) {
  const [draft, setDraft] = useState(value.toString());

  const commit = () => {
    const parsed = Number(draft.replace(',', '.'));
    if (Number.isFinite(parsed) && parsed > 0) {
      onChange(parsed);
    } else {
      setDraft(value.toString());
    }
  };

  return (
    <label className="flex items-center gap-2 rounded-xl border border-white/10 bg-surface px-3 py-1.5">
      <span className="text-xs font-medium text-ink-muted">R$/kWh</span>
      <input
        type="text"
        inputMode="decimal"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.currentTarget.blur();
          }
        }}
        className="tabular w-16 bg-transparent text-sm font-medium text-ink-primary outline-none"
        aria-label="Tarifa de energia em reais por kWh"
      />
    </label>
  );
}
