# DataShield QA Platform — Frontend

SPA em React + Vite + TypeScript, com Material UI e Axios. Consome a API do
backend (veja o [README raiz](../README.md)).

## Rodando

```
npm install
copy .env.example .env     # Windows: copy | Linux/Mac: cp
npm run dev                # http://localhost:5173
```

`VITE_API_URL` define a URL da API (padrão `http://localhost:8000`).

## Scripts

- `npm run dev` — servidor de desenvolvimento
- `npm run build` — checagem de tipos (`tsc -b`) e build de produção
- `npm run lint` — Oxlint

## Estrutura

- `src/pages/` — uma página por módulo (Dashboard, Importação, Descoberta,
  Mascaramento, Anonimização, Sintéticos, LGPD)
- `src/components/Layout.tsx` — layout com menu lateral
- `src/components/ProcessamentoColunasPage.tsx` — fluxo "escolher colunas →
  aplicar → ver preview → baixar", compartilhado por Mascaramento e
  Anonimização (cada página só informa rota e textos)
- `src/nav.tsx` — itens do menu
- `src/api/client.ts` — instância do Axios
