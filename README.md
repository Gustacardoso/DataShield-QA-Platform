# DataShield QA Platform

## Para que serve

Empresas costumam copiar o banco de dados de produção para usar em homologação,
desenvolvimento, testes automatizados e integração de sistemas. Essas cópias
carregam dados reais de clientes — CPF, nome, e-mail, telefone, endereço, dados
financeiros. Isso é um risco grande: vazamento de informação, exposição indevida
de gente real, e descumprimento da LGPD.

O DataShield QA Platform pega essa base de produção (ou qualquer arquivo CSV,
Excel ou JSON) e a transforma em algo seguro para usar em teste, sem perder
utilidade para quem precisa validar sistemas. Ele faz isso em algumas frentes:

1. **Importa** o arquivo (CSV, Excel, JSON, texto).
2. **Descobre** sozinho quais colunas têm dado sensível (CPF, RG, telefone,
   e-mail, nome, endereço, data de nascimento).
3. **Mascara** o que for sensível de forma reversível/parcial (ex: CPF vira
   `***.***.***-10`, e-mail vira `j*****@email.com`) — mantém o formato,
   esconde o conteúdo.
4. **Anonimiza** de forma definitiva quando não faz sentido nem manter um
   resquício (ex: nome vira `ANONIMO`).
5. **Gera dados sintéticos** — massa de teste fake, mas realista (nomes, CPFs,
   e-mails fictícios), para quando o time de dev só precisa de volume de dados
   e não de dados reais mascarados.
6. **Avalia conformidade LGPD** — dá uma nota de risco (Alto/Baixo) dizendo se
   ainda sobrou dado pessoal identificável na base.
7. **Dashboard** — acompanha tudo isso: quantos arquivos passaram pelo
   processo, quanto foi mascarado/anonimizado/gerado, e o índice geral de
   conformidade.

Quem usa isso e como, na prática:

- **Time de QA**: pega a base de produção → mascara → exporta → usa nos testes,
  sem expor dado de cliente real.
- **Time de Dev**: precisa de 10 mil clientes fake para testar → gera sintético
  → exporta → importa na aplicação.
- **Auditoria/Compliance**: verifica se ainda tem CPF/e-mail "vazando" numa base
  de homologação, e mede o quão conforme com a LGPD ela está.

Em resumo: é uma ferramenta de "higienização de dados de teste" — resolve o
conflito entre "precisamos de dados realistas para testar direito" e "não
podemos expor dados reais de clientes", comum em qualquer empresa que trata
dado pessoal e é regulada pela LGPD.

Veja o escopo completo do MVP em [docs/PRD.md](docs/PRD.md).

## Stack

- **Frontend**: React + Vite + TypeScript + Material UI + Axios
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Banco**: PostgreSQL

## Estrutura

```
backend/
  app/core/       configuração, banco (SQLAlchemy) e armazenamento de uploads
  app/models/     modelos ORM (arquivo_processado, coluna_classificada,
                  arquivo_mascarado, arquivo_anonimizado, arquivo_sintetico)
  app/modules/    um pacote por módulo (router + schemas + service):
                  importacao, descoberta, mascaramento, anonimizacao,
                  sinteticos, lgpd, dashboard
  alembic/        migrações do banco
  tests/          testes (pytest) — exigem o Postgres do docker compose no ar
frontend/
  src/pages/      uma página por módulo
  src/components/ Layout e ProcessamentoColunasPage (base compartilhada de
                  Mascaramento e Anonimização)
docs/             documentação de escopo (PRD)
```

O código comum aos módulos que operam sobre um arquivo importado (buscar o
arquivo, ler o DataFrame, escolher colunas-alvo, salvar a saída, preview e
download da última versão gerada) fica em
`backend/app/modules/importacao/helpers.py`.

## API

Todas as rotas ficam sob `/api` (detalhes em `/docs`, com a API rodando).

| Módulo        | Rotas                                                                                      |
| ------------- | ------------------------------------------------------------------------------------------ |
| Importação    | `POST /importacao/upload`, `GET /importacao/`, `GET /importacao/{id}`, `DELETE /importacao/` |
| Descoberta    | `POST /descoberta/{id}/analisar`, `GET /descoberta/{id}`                                   |
| Mascaramento  | `POST /mascaramento/{id}/aplicar`, `GET /mascaramento/{id}/download`                       |
| Anonimização  | `POST /anonimizacao/{id}/aplicar`, `GET /anonimizacao/{id}/download`                       |
| Sintéticos    | `POST /sinteticos/{id}/gerar`, `GET /sinteticos/{id}/download`                             |
| LGPD          | `GET /lgpd/{id}`                                                                           |
| Dashboard     | `GET /dashboard/summary`                                                                   |
| Health-check  | `GET /health`                                                                              |

## Configuração

Variáveis lidas de `backend/.env` (veja `backend/.env.example`):
`DATABASE_URL` (padrão: Postgres local do `docker-compose.yml`),
`CORS_ORIGINS`, `UPLOAD_DIR`, `MASKED_DIR`, `ANONYMIZED_DIR` e `SYNTHETIC_DIR`
(diretórios de saída em `storage/`). O frontend usa `VITE_API_URL`
(padrão `http://localhost:8000`).

## Rodando localmente

### 1. Banco de dados

```
docker compose up -d
```

### 2. Backend

```
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
copy .env.example .env         # Windows: copy | Linux/Mac: cp
alembic upgrade head
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Health-check: `GET /api/health`.
Documentação interativa: `http://localhost:8000/docs`.

### 3. Frontend

```
cd frontend
npm install
copy .env.example .env         # Windows: copy | Linux/Mac: cp
npm run dev
```

A aplicação sobe em `http://localhost:5173`.

### 4. Testes e checagens

Backend (o Postgres do passo 1 precisa estar rodando e migrado):

```
cd backend
.\venv\Scripts\pytest -q
```

Frontend:

```
cd frontend
npm run lint
npm run build      # roda tsc + build de produção
```
