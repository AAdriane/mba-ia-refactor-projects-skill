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

*Próximas seções (Construção da Skill, Resultados, Como Executar) serão adicionadas conforme as próximas etapas do desafio forem concluídas.*
