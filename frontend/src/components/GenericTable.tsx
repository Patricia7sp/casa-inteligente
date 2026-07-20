interface GenericTableProps {
  rows: Record<string, string | number>[];
}

// Tabela genérica para dados cujo shape de colunas vem direto do backend
// (ex: consumption_rank do SmartLife), preservando a ordem das chaves da 1ª linha.
export function GenericTable({ rows }: GenericTableProps) {
  if (rows.length === 0) {
    return <p className="py-10 text-center text-sm text-ink-muted">Sem dados de classificação.</p>;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[480px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-ink-muted">
            {columns.map((col, i) => (
              <th key={col} className={`py-2 font-medium ${i === 0 ? 'pr-3' : 'px-3'} ${i > 0 ? 'text-right' : ''}`}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-white/5 last:border-0">
              {columns.map((col, i) => (
                <td
                  key={col}
                  className={`tabular py-2.5 ${i === 0 ? 'pr-3 font-medium text-ink-primary' : 'px-3 text-right text-ink-secondary'}`}
                >
                  {row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
