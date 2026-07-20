import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from './api';

export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Executa `fetcher` sempre que `deps` mudar. Mantém o último dado renderizado
 * durante um refetch (sem tela em branco / flash), conforme a regra de
 * "refetch mantém o frame" da skill dataviz.
 */
export function useFetch<T>(fetcher: () => Promise<T>, deps: unknown[]): FetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const requestId = useRef(0);

  const run = useCallback(() => {
    const id = ++requestId.current;
    setLoading(true);
    setError(null);
    fetcher()
      .then((result) => {
        if (requestId.current !== id) return;
        setData(result);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (requestId.current !== id) return;
        const message =
          err instanceof ApiError
            ? err.message
            : 'Erro inesperado ao carregar dados.';
        setError(message);
        setLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run]);

  return { data, loading, error, refetch: run };
}
