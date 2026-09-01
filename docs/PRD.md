# DataShield QA Platform — Escopo do Projeto

## Nome

DataShield QA Platform — plataforma para gerenciamento seguro de dados de teste em
conformidade com a LGPD.

## Problema de Negócio

Muitas empresas utilizam cópias da base produtiva em:

- Homologação
- Desenvolvimento
- Testes automatizados
- Integração de sistemas

Essas bases frequentemente contêm dados como CPF, nome completo, e-mail, telefone,
endereço e dados financeiros. Isso gera riscos de vazamento de informações, não
conformidade com a LGPD e exposição indevida de clientes.

## Objetivo da Solução

Criar uma plataforma capaz de:

1. Identificar dados sensíveis.
2. Aplicar mascaramento.
3. Aplicar anonimização.
4. Gerar dados sintéticos.
5. Validar conformidade LGPD.
6. Disponibilizar dados seguros para testes.

## Escopo Funcional (MVP)

### Módulo 1 — Importação de Dados

Receber arquivos nos formatos: Texto plano, CSV, Excel (XLSX) e JSON.

Exemplo: `clientes.csv`

### Módulo 2 — Descoberta de Dados Sensíveis

A aplicação analisa o arquivo automaticamente e detecta: CPF, RG, Telefone, Email,
Nome, Endereço e Data de nascimento.

Exemplo:

```
Coluna CPF    → Sensível
Coluna Nome   → Sensível
Coluna Cidade → Não Sensível
```

### Módulo 3 — Mascaramento

Aplicação de regras configuráveis.

**CPF**

- Antes: `123.456.789-10`
- Depois: `***.***.***-10`

**Email**

- Antes: `joao@email.com`
- Depois: `j*****@email.com`

### Módulo 4 — Anonimização

Remoção definitiva da identificação.

- Antes: `João Silva`
- Depois: `ANONIMO`

### Módulo 5 — Dados Sintéticos

Geração automática de massa de testes.

```json
{
  "nome": "Ana Lima",
  "cpf": "111.222.333-44",
  "email": "ana@teste.com"
}
```

### Módulo 6 — Avaliação LGPD

Motor de análise que informa o nível de risco e os dados encontrados.

Antes do tratamento:

```
Nível de risco: Alto

Dados encontrados:
✓ CPF
✓ E-mail
✓ Telefone
```

Após tratamento:

```
Nível de risco: Baixo
```

### Módulo 7 — Dashboard

Indicadores:

- Arquivos processados
- Dados mascarados
- Dados anonimizados
- Dados sintéticos gerados
- Índice de conformidade LGPD

## Casos de Uso Reais

### Caso 1 — Time de QA

Recebe uma base de produção. Antes de utilizá-la: Upload → Mascaramento →
Exportação → Testes.

### Caso 2 — Time de Desenvolvimento

Necessita de 10.000 clientes para testes. Processo: Gerar Dados Sintéticos →
Exportar CSV → Importar na aplicação.

### Caso 3 — Auditoria de LGPD

Verifica se há dados pessoais na homologação.

Resultado exemplo: 85 CPFs encontrados, 62 Emails encontrados, Conformidade parcial.

## Arquitetura

```
React
  │
  ▼
FastAPI (Python)
  │
  ├── Engine de Mascaramento
  ├── Engine de Anonimização
  ├── Gerador de Dados Sintéticos
  ├── Validador LGPD
  │
  ▼
PostgreSQL
```

## Tecnologias

### Frontend

- React
- Vite
- TypeScript
- Material UI
- Axios

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy + Alembic
- Pandas (parsing de CSV/XLSX/JSON)
- Presidio (detecção e anonimização de PII)
- Faker (geração de dados sintéticos)

> Nota: o escopo original previa Java 21 + Spring Boot no backend. A stack foi
> trocada para Python + FastAPI para aproveitar bibliotecas maduras do próprio
> domínio do problema (Presidio, Faker, Pandas), reduzindo a quantidade de lógica
> de detecção/mascaramento/geração escrita manualmente.

### Banco

- PostgreSQL (via Docker Compose em desenvolvimento)
