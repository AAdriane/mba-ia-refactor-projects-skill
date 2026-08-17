# Refatoração Arquitetural Automatizada — Skill `refactor-arch`

> Este README documenta o processo do desafio: análise manual dos 3 projetos legados, construção da skill `refactor-arch` e os resultados da sua execução.

## Análise Manual

Antes de construir a skill, os 3 projetos fornecidos foram lidos por completo para levantar os problemas reais que a skill precisa detectar e corrigir. Os achados abaixo estão ordenados por severidade em cada projeto e servem de base para o catálogo de anti-patterns da skill.

Escala de severidade usada:
- **CRITICAL** — falha grave de arquitetura/segurança, expõe dados sensíveis ou quebra totalmente a separação de responsabilidades.
- **HIGH** — forte violação de MVC/SOLID que dificulta muito manutenção e testes.
- **MEDIUM** — duplicação de código, padronização ausente ou gargalo de performance moderado.
- **LOW** — legibilidade, nomenclatura, magic numbers/strings.

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

| # | Severidade | Problema |
|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado — toda query é montada por concatenação de string, sem parâmetros (`?`) |
| 2 | **CRITICAL** | Endpoint `/admin/query` executa qualquer SQL enviado no corpo da requisição, sem autenticação |
| 3 | **HIGH** | Senhas armazenadas e comparadas em texto puro (sem hash) |
| 4 | **HIGH** | Secrets hardcoded no código-fonte e expostos publicamente pelo próprio endpoint de health-check |
| 5 | **MEDIUM** | Ausência de camada de serviço / regra de negócio e validação duplicadas no Controller |
| 6 | **MEDIUM** | Consultas N+1 ao montar pedidos com seus itens |
| 7 | **MEDIUM** | Criação de pedido sem transação atômica |
| 8 | **LOW** | Uso de `print()` como mecanismo de logging |
| 9 | **LOW** | CORS liberado sem nenhuma restrição de origem |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS API com checkout)

| # | Severidade | Problema |
|---|---|---|
| 1 | **CRITICAL** | "Hash" de senha fake e reversível (`badCrypto`) |
| 2 | **CRITICAL** | Número completo do cartão de crédito logado em texto puro |
| 3 | **HIGH** | God Object, uma única classe concentra banco, schema, seed e todas as rotas/regras de negócio |
| 4 | **MEDIUM** | "Pyramid of doom" com contadores manuais de callbacks assíncronos |
| 5 | **MEDIUM** | Exclusão de usuário deixa dados órfãos (sem integridade referencial) |
| 6 | **LOW** | Configuração e segredos hardcoded no código-fonte |
| 7 | **LOW** | Banco SQLite inteiramente em memória |

### Projeto 3 — `task-manager-api` (Python/Flask, API de Task Manager)

| # | Severidade | Problema |
|---|---|---|
| 1 | **HIGH** | Senhas hasheadas com MD5, sem salt |
| 2 | **HIGH** | Autenticação "fake", token estático, sem verificação em nenhuma rota |
| 3 | **MEDIUM** | Lógica de negócio duplicada em vez de reaproveitar o Model (cálculo de "overdue" repetido em 4 lugares) |
| 4 | **MEDIUM** | Consultas N+1 na geração de relatórios |
| 5 | **LOW** | Credenciais hardcoded no código-fonte |
| 6 | **LOW** | Uso de `except:` genérico (bare except) escondendo a causa real dos erros |

---

## Construção da Skill

A skill `refactor-arch` foi implementada como `SKILL.md` + 5 arquivos de referência em Markdown, seguindo a estrutura padrão do Claude Code (`.claude/skills/refactor-arch/`). O `SKILL.md` funciona como orquestrador das 3 fases (Analysis → Audit → Refactoring) e delega todo o conhecimento de domínio, heurísticas, catálogo, template, guidelines e playbook aos arquivos de referência, que são carregados pela skill em cada fase específica.

### Decisões de design

- **Separação entre orquestração e conhecimento.** O `SKILL.md` descreve *o quê* fazer em cada fase e *quando* parar para confirmação, mas nunca embute heurísticas de detecção, nomes de anti-patterns ou exemplos de código diretamente, tudo isso está nos 5 arquivos de referência. Isso permite atualizar o catálogo de anti-patterns ou o playbook sem tocar na lógica das 3 fases.
- **Nomenclatura rastreável ponta a ponta.** Cada anti-pattern tem um nome único usado de forma idêntica no catálogo, no relatório de auditoria (Fase 2) e na recomendação de refatoração (Fase 3) por exemplo, "N+1 Query Problem" aparece com esse nome exato nos 3 lugares. Isso permite conferir, ao final da Fase 3, que todo finding CRITICAL/HIGH do relatório foi de fato endereçado.
- **Template de relatório fixo e literal.** O formato do `ARCHITECTURE AUDIT REPORT` (cabeçalho, `Summary` por severidade, `Findings` com `File`/`Description`/`Impact`/`Recommendation`, confirmação `[y/n]`) é tratado como contrato obrigatório, não como sugestão, isso garante que os 3 relatórios gerados (`reports/audit-project-{1,2,3}.md`) sejam comparáveis entre si mesmo vindo de stacks diferentes.
- **Confirmação como gate obrigatório, não como formalidade.** A Fase 2 sempre para e aguarda resposta explícita antes de qualquer escrita em disco, isso foi verificado nas 3 execuções (o agente aguardou o "y" do usuário antes de tocar em qualquer arquivo dos projetos).
- **Playbook com exemplos em duas linguagens.** Cada padrão de transformação no playbook traz exemplo em Python e em JavaScript/TypeScript lado a lado, para deixar explícito que a transformação é conceitual (ex.: "trocar SQL concatenado por parametrizado") e não uma receita de copiar/colar amarrada a uma sintaxe.
- **Camada de Service como extensão, não obrigação.** As guidelines de arquitetura definem Models/Views-Routes/Controllers como as 3 camadas obrigatórias do MVC alvo, com Services como camada opcional introduzida quando um Controller precisa orquestrar mais de uma entidade ou efeito colateral — isso evitou over-engineering em partes simples dos projetos e, ao mesmo tempo, deu um lugar correto para lógica como notificação e emissão de token que não pertence nem ao Model nem ao Controller.

### Anti-patterns incluídos no catálogo e por quê

O catálogo tem 16 anti-patterns escolhidos para cobrir as categorias que efetivamente apareceram na análise manual dos 3 projetos, e não como uma lista genérica de livro-texto:

- **Segurança** (SQL Injection, Hardcoded Credentials, Unauthenticated Sensitive Endpoint, Insecure Credential Storage, Insecure-by-Default Configuration) — porque os 3 projetos tinham pelo menos um problema crítico de segurança real (SQL injection, senha em texto puro/MD5/hash falso, endpoint administrativo sem autenticação), então a skill precisava reconhecer essa família de problemas de forma confiável antes de qualquer outra coisa.
- **Arquitetura/MVC** (God Class/God File, Fat Controller, Anemic Model, Uncontrolled Global Mutable State) — para capturar tanto o caso "zero camadas" (`ecommerce-api-legacy`, um `AppManager` monolítico) quanto o caso mais sutil "camadas existem mas a responsabilidade está no lugar errado" (`task-manager-api`, que já tinha `models/routes/services/utils` mas com toda a regra de negócio dentro das rotas).
- **Performance/Banco de dados** (N+1 Query Problem, Missing Transactional Atomicity) — apareceram nos 3 projetos de formas diferentes (loop de queries em Python vs. SQL bruto, checkout sem transação, listagem de pedidos sem JOIN), então precisavam de uma definição agnóstica de ORM/driver.
- **Qualidade de código** (Duplicated Validation/Business Logic, Broad Exception Handling, Magic Numbers/Strings) — o achado mais recorrente entre os 3 projetos foi duplicação de validação/regra de negócio (categoria de produto, cálculo de "overdue", status válido), então esse anti-pattern precisava de destaque próprio em vez de ser tratado como nota de rodapé.
- **Observabilidade** (Unstructured Logging) — todos os 3 projetos usavam `print`/`console.log` como único mecanismo de log; o catálogo inclui uma regra explícita de reclassificação de severidade quando o log vaza dado sensível (usada na prática no Projeto 2, onde um log continha número de cartão de crédito e foi elevado de LOW para CRITICAL).
- **Manutenibilidade** (Deprecated/End-of-Life API Usage) — exigido pelo enunciado; a skill não assume uma lista fixa de APIs deprecated, e sim uma heurística (cruzar versão de dependência com suporte ativo, procurar warnings de deprecation) — na prática isso detectou `datetime.utcnow()` no Projeto 3, que não é uma dependência desatualizada, mas uma API da própria stdlib do Python marcada como deprecated desde a 3.12.

### Como garanti que a skill é agnóstica de tecnologia

- Nenhum arquivo de referência menciona um framework ou linguagem específicos como pré-condição, as heurísticas de `project-analysis.md` são tabelas de sinais (manifest de dependências, padrão de import, convenção de rota) que cobrem Python/Node/Java/Go/Ruby/PHP/.NET, não só as 3 stacks fornecidas.
- O catálogo e o playbook descrevem sinais de detecção e transformações em termos conceituais ("SQL montado por concatenação de string" em vez de "`+` em Python"), com exemplos em mais de uma linguagem para reforçar que o padrão não é sintaticamente amarrado.
- A prova de fogo foi rodar a mesma skill, sem nenhuma alteração no `SKILL.md` nem nos 5 arquivos de referência, em 3 combinações diferentes de linguagem/framework/nível de organização: Python+Flask sem nenhuma camada (`code-smells-project`), Node.js+Express também sem camadas mas com um paradigma assíncrono totalmente diferente (`ecommerce-api-legacy`), e Python+Flask com camadas parciais já existentes (`task-manager-api`). Nos 3 casos a Fase 1 detectou corretamente stack e domínio, a Fase 2 encontrou 10-11 findings reais e específicos (arquivo + linha) usando o mesmo catálogo, e a Fase 3 produziu uma estrutura MVC (com Services quando fazia sentido) sem reescrever funcionalidade do zero.

### Desafios encontrados

- **Corrigir sem quebrar contrato, mas sem preservar bugs óbvios.** As guidelines dizem para preservar o comportamento externo da API a menos que o próprio finding CRITICAL justifique a mudança. Isso gerou decisões caso a caso: no Projeto 2, a exclusão de usuário que deixava matrícula/pagamento órfãos foi corrigida (mesmo não sendo um finding formal do relatório) porque o próprio código já reconhecia o problema na mensagem de resposta; no Projeto 3, adicionar autenticação real a todos os endpoints de escrita mudou o contrato (agora exige header `Authorization`), mudança justificada explicitamente pela severidade CRITICAL do finding correspondente.
- **Evitar dependências novas para corrigir segurança.** Hashing de senha (Projeto 2) e geração de token assinado (Projeto 3) normalmente puxariam bibliotecas como `bcrypt` ou `PyJWT`, mas adicionar dependências com build nativo ou não previamente presentes no ambiente aumentava o risco de a Fase 3 falhar na validação. A solução foi usar o que já estava disponível: `crypto.scrypt` nativo do Node para hashing, e `itsdangerous` (dependência transitiva do Flask) para token assinado com expiração — nenhuma dependência nova foi adicionada em nenhum dos 3 projetos.

---

## Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — `code-smells-project` | Python + Flask | 4 | 3 | 2 | 3 | 3 | **11** |
| 2 — `ecommerce-api-legacy` | Node.js + Express | 3 | 3 | 3 | 2 | 2 | **10** |
| 3 — `task-manager-api` | Python + Flask (camadas parciais) | 15 | 2 | 2 | 4 | 2 | **10** |

Relatórios completos: [reports/audit-project-1.md](reports/audit-project-1.md), [reports/audit-project-2.md](reports/audit-project-2.md), [reports/audit-project-3.md](reports/audit-project-3.md).

Nos 3 casos a skill encontrou mais findings do que os documentados na Análise Manual (mínimo de 5 por projeto), com severidade distribuída em pelo menos 1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW, confirmando os achados manuais e adicionando findings adicionais (ex.: N+1 Query Problem, Deprecated API Usage) que só ficaram evidentes na varredura sistemática contra o catálogo.

### Comparação antes/depois da estrutura

**Projeto 1 — `code-smells-project`**
```
Antes                          Depois
app.py (rotas + admin)         app.py (composition root)
controllers.py (tudo)          config.py, constants.py, errors.py
models.py (SQL bruto)          models/{produto,usuario,pedido}.py
database.py                    controllers/{produto,usuario,pedido,admin,health}_controller.py
                                routes/{produto,usuario,pedido,report,admin,health}_routes.py
                                services/{pedido,notification}_service.py
                                middlewares/{auth,error_handler}.py
4 arquivos, ~780 linhas         21 arquivos, camadas MVC completas
```

**Projeto 2 — `ecommerce-api-legacy`**
```
Antes                          Depois
src/app.js (entry point)       src/app.js (composition root)
src/AppManager.js (God Object) src/config.js, constants.js, errors.js, logger.js, database.js
src/utils.js (config+cache)    src/models/{user,course,enrollment,payment,auditLog,report}Model.js
                                src/services/{checkout,financialReport,password,cache}Service.js
                                src/controllers/{checkout,admin,user}Controller.js
                                src/routes/{checkout,admin,user}Routes.js
                                src/middlewares/errorHandler.js
3 arquivos, ~180 linhas         22 arquivos, camadas MVC completas
```

**Projeto 3 — `task-manager-api`**
```
Antes                                  Depois
app.py                                 app.py (composition root)
models/{task,user,category}.py         config.py, constants.py, errors.py (novos)
routes/{task,user,report}_routes.py    models/{task,user,category}.py (corrigidos)
  (regra de negócio duplicada          services/{task,user,category,report,auth,notification}_service.py (novo)
   dentro das rotas)                   controllers/{task,user,category,report}_controller.py (novo)
services/notification_service.py        routes/*.py (agora finas, protegidas por @require_auth)
  (nunca chamado)                      middlewares/{auth,error_handler}.py (novo)
utils/helpers.py
  (validação central nunca usada)
15 arquivos, ~1160 linhas               29 arquivos, Controllers e Services introduzidos,
                                         validação/notificação já existentes finalmente reaproveitadas
```

### Checklist de Validação preenchido

**Projeto 1 — `code-smells-project`**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce: produtos/usuários/pedidos)
- [x] Número de arquivos analisados condiz com a realidade (4)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (11)
- [x] Detecção de APIs deprecated incluída (nenhuma encontrada — Flask/flask-cors atuais)
- [x] Skill pausou e pediu confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config.py` + `.env.example` (sem hardcoded)
- [x] Models criados (`models/produto.py`, `usuario.py`, `pedido.py`)
- [x] Routes separadas para roteamento (`routes/*.py`)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`app.py`)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

**Projeto 2 — `ecommerce-api-legacy`**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS: cursos/matrículas/pagamentos/checkout)
- [x] Número de arquivos analisados condiz com a realidade (3)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (10)
- [x] Detecção de APIs deprecated incluída (nenhuma dependência deprecated; API callback-only do driver sqlite3 anotada)
- [x] Skill pausou e pediu confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config.js` + `.env.example` (sem hardcoded)
- [x] Models criados (`models/{user,course,enrollment,payment,auditLog,report}Model.js`)
- [x] Routes separadas para roteamento (`routes/*.js`)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/errorHandler.js`)
- [x] Entry point claro (`src/app.js`)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

**Projeto 3 — `task-manager-api`**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0 + Flask-SQLAlchemy 3.1.1)
- [x] Domínio da aplicação descrito corretamente (Task Manager: tasks/usuários/categorias/relatórios)
- [x] Número de arquivos analisados condiz com a realidade (15)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (10)
- [x] Detecção de APIs deprecated incluída (`datetime.utcnow()`, deprecated desde Python 3.12)
- [x] Skill pausou e pediu confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config.py` + `.env.example` (sem hardcoded)
- [x] Models corrigidos (`models/task.py`, `user.py`, `category.py`)
- [x] Routes separadas para roteamento, agora finas (`routes/*.py`)
- [x] Controllers concentram o fluxo da aplicação (novos — não existiam antes)
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro (`app.py`)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

### Logs das aplicações rodando após a refatoração

**Projeto 1 — boot + endpoints:**
```
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'app'
 * Debug mode: off

$ curl /health
{"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}
# secret_key / debug / db_path não são mais expostos (finding CRITICAL corrigido)

$ curl -X POST /admin/reset-db                          -> 401 (sem token)
$ curl -X POST /admin/reset-db -H "X-Admin-Token: ..."   -> 200 {"mensagem":"Banco de dados resetado","sucesso":true}
$ curl -X POST /admin/query                              -> 404 (endpoint removido, executava SQL arbitrário)
$ curl "/produtos/busca?q=' OR '1'='1"                    -> {"dados":[],"sucesso":true,"total":0}  (sem SQL injection)
```

**Projeto 2 — boot + checkout + relatório:**
```
[INFO] 2026-08-17T22:35:48.430Z Frankenstein LMS rodando na porta 3000...

$ curl -X POST /api/checkout {"card":"4111..."}
{"msg":"Sucesso","enrollment_id":2}

$ curl /api/admin/financial-report
[{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},
 {"course":"Docker","revenue":497,"students":[{"student":"Guilherme","paid":497}]}]

$ grep -i "cartão\|paymentGatewayKey" app.log
NENHUM DADO SENSÍVEL NO LOG   (finding CRITICAL corrigido)

$ curl -X DELETE /api/users/2
Usuário deletado, matrículas e pagamentos relacionados também foram removidos.
# relatório pós-delete confirma: curso "Docker" volta a revenue:0, students:[] (sem dado órfão)
```

**Projeto 3 — boot + auth gate:**
```
2026-08-17 19:53:24 [INFO] werkzeug: Running on http://127.0.0.1:5000

$ curl -X POST /login {"email":"joao@email.com","password":"1234"}
{"message":"Login realizado com sucesso","user":{...},"token":"eyJ1c2VyX2lkIjoxfQ...."}
# token assinado com expiração (itsdangerous), não mais 'fake-jwt-token-1'

$ curl -X POST /tasks {"title":"Nova task via API",...}          -> 401 (sem token)
$ curl -X POST /tasks -H "Authorization: Bearer ..." {...}       -> 201 (criada, dispara NotificationService)
[WARNING] services.notification_service: Erro ao enviar email... (535 auth) — falha graciosa, não derruba a requisição

$ curl /reports/summary
{"user_productivity":[...]}  # agregações via GROUP BY em vez de 1 query por usuário
```

> Screenshots não foram anexados porque toda a validação foi feita via `curl` em processo `Flask`/`Express` local — os logs acima são a saída real capturada durante a execução da Fase 3 de cada projeto, incluindo os casos negativos (401 sem token, 404 do endpoint removido, ausência de dado sensível nos logs).

### Observações sobre o comportamento da skill em stacks diferentes

- A mesma skill, sem nenhuma edição, produziu estruturas MVC idiomaticamente diferentes por stack: Blueprints + `app.register_blueprint` nos dois projetos Flask, e `express.Router()` + `app.use('/api', router)` no projeto Node, a convenção de "Routes" da guideline foi respeitada sem forçar um único padrão sintático.
- No projeto com camadas parciais (Projeto 3), a Fase 2 não se limitou a validar o que já existia, encontrou que duas peças de código já escritas (`Task.is_overdue()` e `utils.helpers.process_task_data()`) nunca eram chamadas, e a Fase 3 corrigiu isso reaproveitando-as em vez de duplicar a lógica de novo.
- No projeto sem nenhuma camada (Projeto 2), a Fase 3 precisou introduzir tanto Models quanto Services do zero a partir de um único arquivo — mais trabalho de reestruturação, mas o resultado final seguiu a mesma guideline de dependência unidirecional Routes → Controllers → Services → Models dos outros dois.

---

## Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (`claude` disponível no terminal) — foi a ferramenta usada neste desafio, com a skill em `.claude/skills/refactor-arch/`.
- **Python 3.10+** e **pip** — para `code-smells-project` e `task-manager-api`.
- **Node.js 18+** e **npm** — para `ecommerce-api-legacy`.
- Nenhuma dependência externa adicional é necessária: os 3 projetos refatorados usam apenas bibliotecas já presentes no `requirements.txt`/`package.json` original (hashing de senha via `werkzeug.security`/`crypto` nativo do Node, token assinado via `itsdangerous`, que já vem com o Flask).

### Comandos para executar a skill em cada projeto

A skill é a mesma nos 3 projetos (`SKILL.md` + 5 arquivos de referência em `.claude/skills/refactor-arch/`), copiada sem alteração para dentro de cada um.

**Projeto 1 — `code-smells-project`**
```bash
cd code-smells-project
claude "/refactor-arch"
# Fase 1 e Fase 2 rodam automaticamente e imprimem o relatório de auditoria
# Ao final da Fase 2, responda "y" para prosseguir com a refatoração (Fase 3)
```

**Projeto 2 — `ecommerce-api-legacy`**
```bash
cd ecommerce-api-legacy
claude "/refactor-arch"
```

**Projeto 3 — `task-manager-api`**
```bash
cd task-manager-api
claude "/refactor-arch"
```

Em qualquer um dos 3, o relatório da Fase 2 também fica salvo em `reports/audit-project-N.md` na raiz do repositório, e a Fase 3 só altera arquivos após a confirmação `[y/n]`.

### Como validar que a refatoração funcionou

Após a Fase 3 de cada projeto, rode a aplicação refatorada e confirme que os endpoints originais continuam respondendo:

**Projeto 1 — `code-smells-project`**
```bash
cd code-smells-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
SECRET_KEY=meu-secret ADMIN_TOKEN=meu-admin-token python app.py
# em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl -X POST http://localhost:5000/admin/reset-db          # -> 401 sem token
curl -X POST http://localhost:5000/admin/reset-db -H "X-Admin-Token: meu-admin-token"  # -> 200
```

**Projeto 2 — `ecommerce-api-legacy`**
```bash
cd ecommerce-api-legacy
npm install
npm start
# em outro terminal (exemplos também em api.http):
curl -X POST http://localhost:3000/api/checkout -H "Content-Type: application/json" \
  -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","c_id":2,"card":"4111222233334444"}'
curl http://localhost:3000/api/admin/financial-report
```

**Projeto 3 — `task-manager-api`**
```bash
cd task-manager-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py    # popula tasks.db — necessário antes do primeiro boot
SECRET_KEY=meu-secret python app.py
# em outro terminal:
curl http://localhost:5000/tasks
TOKEN=$(curl -s -X POST http://localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" -d '{"title":"Nova task"}'   # -> 201
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" \
  -d '{"title":"Sem token"}'                                    # -> 401
```
