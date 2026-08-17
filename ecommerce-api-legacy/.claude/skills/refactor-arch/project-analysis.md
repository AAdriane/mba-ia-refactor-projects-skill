# Project Analysis — Heurísticas de Detecção (Fase 1)

Este documento define como a **Fase 1 (Análise)** da skill `refactor-arch` deve
identificar linguagem, framework, banco de dados e mapear a arquitetura atual de
**qualquer** projeto de backend, independente da stack. As heurísticas aqui são
agnósticas de tecnologia. Evite hardcodar caminhos ou nomes específicos de um
único projeto; use os sinais abaixo como regras gerais.

## 1. Detecção de linguagem

Ordem de prioridade: manifest de dependências > extensão de arquivo dominante.

| Sinal (arquivo de manifest presente na raiz) | Linguagem provável |
|---|---|
| `package.json` (+ `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml`) | JavaScript/TypeScript (Node.js) |
| `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py` | Python |
| `pom.xml`, `build.gradle`/`build.gradle.kts` | Java/Kotlin |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj`/`*.sln` | C#/.NET |

Se não houver manifest, contar a extensão de arquivo-fonte predominante no
repositório (excluindo `node_modules/`, `venv/`, `dist/`, `build/`, `.git/`).

## 2. Detecção de framework

1. Localizar o **arquivo de entrada** da aplicação:
   - Node: `main`/`scripts.start` do `package.json`, ou arquivo que chama
     `app.listen(...)`/`createServer(...)`.
   - Python: arquivo com `if __name__ == "__main__":` que chama `app.run(...)`,
     `uvicorn.run(...)`, ou `manage.py`/`asgi.py`/`wsgi.py`.
   - Java: classe com `public static void main` ou anotada `@SpringBootApplication`.
2. Inspecionar os `import`/`require` desse arquivo e do manifest de dependências.

| Sinal | Framework |
|---|---|
| `express` (dependência ou `require('express')`) | Express |
| `@nestjs/core` | NestJS |
| `fastify` | Fastify |
| `flask`, `from flask import Flask` | Flask |
| `django`, `manage.py` presente | Django |
| `fastapi` | FastAPI |
| `spring-boot-starter-*` | Spring Boot |
| `gin-gonic/gin` | Gin (Go) |
| `rails` no `Gemfile` | Ruby on Rails |

Registrar também **como as rotas são declaradas** (decorators, `Blueprint`,
`Router()`, `app.get/post`, anotações `@RestController`) — isso alimenta o
mapeamento de arquitetura do passo 4.

## 3. Detecção de banco de dados

| Sinal | Banco / Camada de acesso |
|---|---|
| Import de driver nativo (`sqlite3`, `pg`, `mysql2`, `psycopg2`, `PyMySQL`, `mongodb`) sem ORM por cima | Acesso direto via driver — maior risco de SQL bruto sem parametrização |
| ORM/Query builder (`SQLAlchemy`, `Sequelize`, `TypeORM`, `Prisma`, `Mongoose`, `Hibernate/JPA`, `ActiveRecord`) | Acesso via ORM — verificar se as queries N+1/raw SQL ainda existem apesar do ORM |
| String de conexão hardcoded no código-fonte (`"postgres://user:pass@host/db"`, credenciais literais) | **Anti-pattern de segurança** — ver `antipattern-catalog.md` |
| Arquivo `*.db`/`*.sqlite` versionado no repositório, ou `:memory:` na criação da conexão | SQLite (arquivo local ou efêmero em memória) |
| Pasta `migrations/`, `alembic/`, `prisma/migrations` | Existe controle de schema versionado |
| Ausência de migrations + `CREATE TABLE IF NOT EXISTS` disparado no boot | Schema gerenciado manualmente no código — sinal de projeto sem disciplina de versionamento de banco |

Também identificar **onde a conexão é aberta** (módulo dedicado vs. inline em
cada rota/controller) e se existe **singleton/pool** ou uma nova conexão por
requisição.

## 4. Mapeamento da arquitetura atual

Passo a passo, aplicável a qualquer linguagem:

1. **Inventariar arquivos por responsabilidade aparente** — nome de arquivo/pasta
   é o primeiro sinal (`models/`, `controllers/`, `routes/`, `services/`,
   `handlers/`, `views/`, `repository/`). Pastas ausentes indicam camadas ausentes.
2. **Seguir o fluxo de uma requisição típica de ponta a ponta** (ex.: um `POST`
   de criação de recurso do domínio principal): entrada HTTP → validação →
   regra de negócio → acesso a dado → resposta. Anotar em qual arquivo/função
   cada etapa realmente acontece (nem sempre bate com o nome da pasta).
3. **Verificar se existe camada de Service/Domain** entre a camada HTTP e o
   acesso a dados. Ausência é o sinal mais comum de "Fat Controller" — regra
   de negócio dentro do handler HTTP.
4. **Verificar se o "Model" é um DAO disfarçado** — se a camada nomeada
   `models` só contém SQL/queries e nenhuma regra de validação/negócio, é um
   Model anêmico.
5. **Contar responsabilidades por arquivo** — um único arquivo/classe que
   mistura roteamento, acesso a dado, regra de negócio e infraestrutura
   (conexão de banco, configuração, envio de e-mail) é sinal de God
   Class/God File.
6. **Registrar o que está ausente**: autenticação/autorização, validação
   centralizada, tratamento de erro padronizado, logging estruturado, testes,
   camada de configuração isolada (env vars vs. hardcoded).
7. **Medir o tamanho aproximado**: número de arquivos-fonte analisados e LOC
   total (ou por arquivo) — isso alimenta o cabeçalho do relatório de auditoria
   (`Files: N analyzed | ~X lines of code`).

## 5. Saída esperada da Fase 1

Ao final, produzir um resumo estruturado (impresso ao usuário) contendo:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework + versão, se identificável>
Dependencies:  <dependências relevantes>
Domain:        <domínio da aplicação inferido pelas rotas/entidades>
Architecture:  <resumo textual: monolítico sem camadas / camadas parciais / etc.>
Source files:  <N> files analyzed
DB tables:     <tabelas/coleções identificadas>
================================
```

Esse resumo alimenta diretamente a Fase 2 (comparação contra o catálogo de
anti-patterns em `antipattern-catalog.md` e preenchimento do template em
`audit-report-template.md`).
