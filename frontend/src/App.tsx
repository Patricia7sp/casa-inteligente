import { useState } from 'react';
import { Bot, Home, Plug, Smartphone } from 'lucide-react';
import type { Period } from './types';
import { PeriodSelector } from './components/common/PeriodSelector';
import { TariffInput } from './components/common/TariffInput';
import { DevicesPage } from './pages/DevicesPage';
import { SmartLifePage } from './pages/SmartLifePage';
import { AssistantPage } from './pages/AssistantPage';

type Tab = 'devices' | 'smartlife' | 'assistant';

const NAV: { id: Tab; label: string; icon: typeof Home }[] = [
  { id: 'devices', label: 'Dispositivos', icon: Plug },
  { id: 'smartlife', label: 'SmartLife', icon: Smartphone },
  { id: 'assistant', label: 'Assistente', icon: Bot },
];

function App() {
  const [tab, setTab] = useState<Tab>('devices');
  const [period, setPeriod] = useState<Period>(30);
  const [tariff, setTariff] = useState(0.862);

  return (
    <div className="min-h-screen bg-bg text-ink-primary lg:flex">
      {/* Sidebar (desktop) */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-white/10 bg-surface px-4 py-6 lg:flex">
        <div className="mb-8 flex items-center gap-2 px-2">
          <span className="grid size-9 place-items-center rounded-xl bg-series-energy/15 text-series-energy">
            <Home size={18} />
          </span>
          <div>
            <p className="text-sm font-semibold leading-tight text-ink-primary">Casa Inteligente</p>
            <p className="text-xs text-ink-muted">Painel de energia</p>
          </div>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV.map((item) => {
            const active = tab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                  active ? 'bg-white/10 text-ink-primary' : 'text-ink-muted hover:bg-white/5 hover:text-ink-secondary'
                }`}
              >
                <item.icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {tab === 'devices' && (
          <div className="mt-8 flex flex-col gap-3 border-t border-white/10 pt-6">
            <p className="px-1 text-xs font-medium uppercase tracking-wide text-ink-muted">Período</p>
            <PeriodSelector value={period} onChange={setPeriod} />
            <p className="mt-2 px-1 text-xs font-medium uppercase tracking-wide text-ink-muted">Tarifa</p>
            <TariffInput value={tariff} onChange={setTariff} />
          </div>
        )}
      </aside>

      {/* Mobile top bar */}
      <div className="sticky top-0 z-10 flex flex-col gap-3 border-b border-white/10 bg-surface/95 px-4 py-3 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded-lg bg-series-energy/15 text-series-energy">
              <Home size={16} />
            </span>
            <p className="text-sm font-semibold">Casa Inteligente</p>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto">
          {NAV.map((item) => {
            const active = tab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                className={`inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  active ? 'bg-white/10 text-ink-primary' : 'text-ink-muted hover:text-ink-secondary'
                }`}
              >
                <item.icon size={14} />
                {item.label}
              </button>
            );
          })}
        </nav>
        {tab === 'devices' && (
          <div className="flex flex-wrap items-center gap-2">
            <PeriodSelector value={period} onChange={setPeriod} />
            <TariffInput value={tariff} onChange={setTariff} />
          </div>
        )}
      </div>

      {/* Content */}
      <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        <div className="mx-auto max-w-7xl">
          {tab === 'devices' && <DevicesPage period={period} tariff={tariff} />}
          {tab === 'smartlife' && <SmartLifePage />}
          {tab === 'assistant' && <AssistantPage />}
        </div>
      </main>
    </div>
  );
}

export default App;
