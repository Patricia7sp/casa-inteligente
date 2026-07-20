import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Bot, Send, Sparkles, Trash2, User } from 'lucide-react';
import { api, ApiError } from '../lib/api';
import type { AiProvider, ChatMessage } from '../types';
import { Card } from '../components/common/Card';

const SUGGESTIONS = ['Como está meu consumo hoje?', 'Qual dispositivo gasta mais?', 'Dê dicas de economia'];

const PROVIDERS: { value: AiProvider; label: string }[] = [
  { value: 'auto', label: 'Auto' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'gemini', label: 'Gemini' },
];

function uid(): string {
  return Math.random().toString(36).slice(2, 10);
}

export function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState<AiProvider>('auto');
  const [thinking, setThinking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    });
  };

  const send = async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || thinking) return;

    const userMessage: ChatMessage = { id: uid(), role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setThinking(true);
    scrollToBottom();

    try {
      const res = await api.askAssistant({ question: trimmed, provider });
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: 'assistant', content: res.response || 'Sem resposta.', provider: res.provider },
      ]);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Erro de conexão ao consultar o assistente.';
      setMessages((prev) => [...prev, { id: uid(), role: 'assistant', content: message, isError: true }]);
    } finally {
      setThinking(false);
      scrollToBottom();
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void send(input);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-series-energy/15 via-surface to-surface p-6 text-center">
        <div className="mx-auto mb-2 grid size-11 place-items-center rounded-full bg-white/10 text-ink-primary">
          <Bot size={22} />
        </div>
        <h2 className="text-lg font-semibold text-ink-primary">Assistente inteligente de energia</h2>
        <p className="mt-1 text-sm text-ink-muted">
          Pergunte sobre consumo, custos e receba insights personalizados
        </p>
      </div>

      <Card
        title="Conversa"
        actions={
          <div className="flex items-center gap-2">
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as AiProvider)}
              className="rounded-lg border border-white/10 bg-surface-raised px-2.5 py-1.5 text-xs text-ink-primary outline-none"
              aria-label="Provedor de IA"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
            <button
              onClick={() => setMessages([])}
              disabled={messages.length === 0}
              className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-2.5 py-1.5 text-xs font-medium text-ink-secondary hover:bg-white/5 disabled:opacity-40"
            >
              <Trash2 size={13} />
              Limpar conversa
            </button>
          </div>
        }
        bodyClassName="p-0"
      >
        <div ref={scrollRef} className="max-h-[28rem] min-h-[16rem] overflow-y-auto px-5 py-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center gap-4 py-6 text-center">
              <p className="flex items-center gap-1.5 text-xs font-medium text-ink-muted">
                <Sparkles size={13} />
                Perguntas sugeridas
              </p>
              <div className="grid w-full gap-2 sm:grid-cols-3">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => void send(s)}
                    className="rounded-xl border border-white/10 bg-surface-raised px-3 py-2.5 text-left text-xs text-ink-secondary transition-colors hover:border-white/20 hover:text-ink-primary"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {messages.map((m) => (
                <div key={m.id} className={`flex gap-2.5 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <span
                    className={`grid size-7 shrink-0 place-items-center rounded-full ${
                      m.role === 'user' ? 'bg-series-energy/20 text-series-energy' : 'bg-white/10 text-ink-secondary'
                    }`}
                  >
                    {m.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                  </span>
                  <div
                    className={`max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm whitespace-pre-wrap ${
                      m.role === 'user'
                        ? 'bg-series-energy/15 text-ink-primary'
                        : m.isError
                          ? 'border border-status-critical/30 bg-status-critical/10 text-ink-secondary'
                          : 'bg-surface-raised text-ink-secondary'
                    }`}
                  >
                    {m.content}
                    {m.provider && (
                      <p className="mt-1.5 text-[11px] italic text-ink-muted">Respondido por: {m.provider}</p>
                    )}
                  </div>
                </div>
              ))}
              {thinking && (
                <div className="flex items-center gap-2.5">
                  <span className="grid size-7 shrink-0 place-items-center rounded-full bg-white/10 text-ink-secondary">
                    <Bot size={14} />
                  </span>
                  <div className="flex items-center gap-1.5 rounded-2xl bg-surface-raised px-3.5 py-2.5">
                    <span className="animate-pulse-soft text-xs text-ink-muted">Pensando…</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <form onSubmit={onSubmit} className="flex items-center gap-2 border-t border-white/10 px-4 py-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Como está meu consumo hoje?"
            className="flex-1 rounded-xl border border-white/10 bg-surface-raised px-3.5 py-2.5 text-sm text-ink-primary outline-none placeholder:text-ink-muted focus:border-white/20"
          />
          <button
            type="submit"
            disabled={!input.trim() || thinking}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-series-energy px-4 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            <Send size={14} />
            Enviar
          </button>
        </form>
      </Card>
    </div>
  );
}
