// Tokens de cor da skill dataviz (references/palette.md). Mantidos aqui em
// hex puro porque Recharts (SVG) precisa de valores literais em `stroke`/`fill`,
// não das custom properties do Tailwind usadas no resto da UI.

export const colors = {
  bg: '#0d0d0d',
  surface: '#1a1a19',
  surfaceRaised: '#212120',
  inkPrimary: '#ffffff',
  inkSecondary: '#c3c2b7',
  inkMuted: '#898781',
  grid: '#2c2c2a',
  baseline: '#383835',
  border: 'rgba(255,255,255,0.10)',
} as const;

export const statusColors = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
} as const;

// Par validado energia (azul) vs custo (vermelho) para gráficos duplos.
export const seriesColors = {
  energy: '#3987e5',
  cost: '#e66767',
} as const;

// Paleta de fallback para dispositivos sem cor definida pela API.
export const deviceColorFallbacks = [
  '#3987e5',
  '#e66767',
  '#fab219',
  '#0ca30c',
  '#c084fc',
  '#ec835a',
];

export function deviceColor(color: string | null | undefined, index = 0): string {
  if (color && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(color)) return color;
  return deviceColorFallbacks[index % deviceColorFallbacks.length];
}
