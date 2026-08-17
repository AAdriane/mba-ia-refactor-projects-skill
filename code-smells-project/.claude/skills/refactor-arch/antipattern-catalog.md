# Anti-pattern Catalog (Fase 2 — Auditoria)

Catálogo de anti-patterns que a skill `refactor-arch` deve procurar durante a
auditoria, independente de linguagem/framework. Cada item traz **sinais de
detecção** (o que procurar no código, de forma agnóstica de sintaxe) e a
**severidade** a ser usada no relatório (`audit-report-template.md`).

Escala de severidade:

- **CRITICAL** — falha grave de arquitetura ou segurança: expõe dados
  sensíveis, permite execução/acesso não autorizado, ou quebra completamente
  a separação de responsabilidades.
- **HIGH** — forte violação de MVC/SOLID que dificulta muito manutenção e
  testes: lógica de negócio pesada no lugar errado, acoplamento forte, estado
  global mutável.
- **MEDIUM** — duplicação de código, padronização ausente, gargalo de
  performance moderado.
- **LOW** — legibilidade, nomenclatura, magic numbers/strings, configuração
  insegura por padrão mas de baixo impacto isolado.

---

## 1. [CRITICAL] SQL/Query Injection

**Categoria:** Segurança.
**Sinais de detecção:** construção de query por concatenação/interpolação de
string com dado vindo de request (`"SELECT * WHERE id = " + id`, f-strings,
template literals, `%s` sem parametrização) em vez de placeholders (`?`, `$1`,
bind parameters do ORM). Também aplicável a queries NoSQL montadas por
concatenação de string/objeto não sanitizado.
**Impacto:** leitura/alteração/remoção de dados arbitrários, bypass de
autenticação, em casos extremos execução de comandos no servidor de banco.

## 2. [CRITICAL] Hardcoded Credentials / Secrets

**Categoria:** Segurança.
**Sinais de detecção:** strings literais para `SECRET_KEY`, senha de banco,
chave de API, chave de gateway de pagamento, credenciais SMTP diretamente no
código-fonte (não lidas de variável de ambiente/secret manager). Inclui
segredos retornados em respostas de API (ex.: endpoint de health-check
expondo config interna).
**Impacto:** qualquer pessoa com acesso ao repositório (ou a uma resposta de
API vazando config) compromete produção.

## 3. [CRITICAL] God Class / God File

**Categoria:** Arquitetura.
**Sinais de detecção:** um único arquivo/classe/módulo concentra: conexão de
banco, criação de schema, roteamento HTTP, regra de negócio de múltiplos
domínios e formatação de resposta. Sintomas quantitativos: arquivo com
centenas de linhas cobrindo mais de 2-3 responsabilidades distintas, ou uma
classe cujo construtor + métodos tocam banco, HTTP e regra de negócio ao
mesmo tempo.
**Impacto:** impossível testar em isolamento; qualquer mudança tem alto risco
de efeito colateral em partes não relacionadas.

## 4. [CRITICAL] Unauthenticated Sensitive/Destructive Endpoint

**Categoria:** Segurança.
**Sinais de detecção:** rotas que alteram/apagam dados em massa, executam
comandos arbitrários (ex.: SQL enviado no corpo da requisição) ou expõem
dados administrativos, sem nenhum middleware/decorator de autenticação ou
verificação de role antes do handler.
**Impacto:** qualquer cliente não autenticado pode destruir dados ou obter
acesso administrativo completo.

## 5. [HIGH] Fat Controller / Business Logic in HTTP Layer

**Categoria:** Arquitetura (violação de MVC/SRP).
**Sinais de detecção:** handler de rota/controller contendo regras de
negócio complexas (cálculos, decisões multi-etapa, orquestração de múltiplos
efeitos colaterais como notificações) misturadas com parsing de request e
formatação de resposta, sem delegar a uma camada de Service/Domain.
**Impacto:** regra de negócio não é reutilizável nem testável sem subir a
camada HTTP; duplicação entre endpoints que fazem operações parecidas.

## 6. [HIGH] Anemic Model / Model as Plain DAO

**Categoria:** Arquitetura.
**Sinais de detecção:** a camada nomeada "model" contém apenas
funções/métodos que montam e executam queries (CRUD puro), sem nenhuma regra
de validação de domínio, invariantes ou comportamento — toda decisão de
negócio vive fora do model, geralmente duplicada em cada controller/rota que
usa aquela entidade.
**Impacto:** regras de negócio ficam espalhadas e inconsistentes entre pontos
de entrada diferentes que manipulam a mesma entidade.

## 7. [HIGH] Insecure Credential Storage

**Categoria:** Segurança.
**Sinais de detecção:** senha de usuário armazenada/comparada em texto puro,
ou hasheada com algoritmo quebrado/inadequado para senha (MD5, SHA1 sem
salt, ou "hash" caseiro não criptográfico) em vez de um algoritmo com custo
ajustável (bcrypt, scrypt, Argon2).
**Impacto:** vazamento de banco expõe credenciais reais dos usuários,
permitindo reuso em outros sistemas (credential stuffing).

## 8. [HIGH] Uncontrolled Global Mutable State

**Categoria:** Arquitetura.
**Sinais de detecção:** variáveis globais mutáveis compartilhadas entre
requisições (cache em memória de processo, contador, conexão singleton sem
gestão de ciclo de vida) usadas para guardar estado de negócio ou dados de
requisição.
**Impacto:** condição de corrida entre requisições concorrentes, estado que
"vaza" entre usuários, comportamento não determinístico difícil de depurar.

## 9. [MEDIUM] N+1 Query Problem

**Categoria:** Performance.
**Sinais de detecção:** loop sobre uma coleção de resultados que, a cada
iteração, dispara uma nova query para buscar dados relacionados (em vez de
`JOIN`, `include`/`eager loading` do ORM, ou uma query em lote com `IN (...)`).
**Impacto:** número de queries cresce linearmente (ou pior) com o volume de
dados, degradando latência sob carga.

## 10. [MEDIUM] Duplicated Validation / Business Logic (DRY Violation)

**Categoria:** Qualidade de código.
**Sinais de detecção:** o mesmo bloco de validação ou cálculo (ex.: regra de
"está atrasado", faixa de valores válidos, formatação de resposta) copiado e
colado em múltiplos handlers/arquivos em vez de extraído para uma função/
método reutilizável — inclusive quando já existe um método no model que
implementa a mesma regra e não é chamado.
**Impacto:** correções e mudanças de regra precisam ser replicadas
manualmente em cada cópia; alto risco de divergência silenciosa.

## 11. [MEDIUM] Missing Transactional Atomicity

**Categoria:** Banco de dados / Confiabilidade.
**Sinais de detecção:** operação que grava em múltiplas tabelas/coleções
como parte de uma única regra de negócio (ex.: criar pedido + baixar
estoque + registrar item) sem transação (`BEGIN/COMMIT/ROLLBACK`, unit of
work do ORM) — cada `INSERT`/`UPDATE` é feito de forma independente.
**Impacto:** falha no meio da operação deixa o banco em estado inconsistente
(ex.: estoque debitado sem pedido correspondente).

## 12. [MEDIUM] Broad Exception Handling with Internal Leakage

**Categoria:** Qualidade de código / Segurança.
**Sinais de detecção:** blocos `catch`/`except` genéricos (`except Exception`,
`catch (e)`, bare `except:`) que capturam qualquer erro e devolvem a mensagem
crua da exceção (stack trace, mensagem de driver de banco) diretamente na
resposta da API.
**Impacto:** mascara a causa real de bugs (dificulta debug) e pode vazar
detalhes de implementação (nomes de tabela, caminho de arquivo) para o
cliente.

## 13. [MEDIUM] Deprecated / End-of-Life API Usage

**Categoria:** Manutenibilidade / Segurança.
**Sinais de detecção:**
- Métodos/funções marcados como deprecated pela própria biblioteca (avisos de
  deprecation no changelog, docstring, ou warning em runtime/lint).
- Versão de linguagem/framework/dependência abaixo do suporte ativo (LTS
  expirado, versão major muito antiga no manifest de dependências).
- Uso de APIs substituídas por uma alternativa moderna e amplamente adotada
  (ex.: callback-based APIs quando a mesma biblioteca já oferece
  Promise/async-await; drivers de banco síncronos bloqueantes quando existe
  versão assíncrona oficial; funções de hashing/criptografia obsoletas).
**Como checar:** cruzar as dependências do manifest com a documentação oficial
de deprecation da biblioteca/framework identificado na Fase 1; procurar
comentários ou warnings de deprecation no próprio código.
**Impacto:** perda de suporte a correções de segurança, incompatibilidade
futura, comportamento não documentado ou removido em versões seguintes.

## 14. [LOW] Unstructured Logging (print/console.log Driven)

**Categoria:** Observabilidade.
**Sinais de detecção:** uso de `print`/`console.log`/equivalente espalhado
pelo código como único mecanismo de log, sem níveis (debug/info/warn/error),
timestamps ou formato consistente, e sem um logger configurável por ambiente.
**Impacto:** impossível filtrar, agregar ou desligar logs em produção;
observabilidade praticamente inexistente.

## 15. [LOW] Insecure-by-Default Configuration

**Categoria:** Segurança / Configuração.
**Sinais de detecção:** CORS liberado para qualquer origem sem necessidade
declarada, modo debug/verbose ligado por padrão, flags de desenvolvimento
ativas sem gate por variável de ambiente.
**Impacto:** superfície de ataque desnecessariamente ampliada; normalmente
baixo impacto isolado, mas agrava outros achados do relatório.

## 16. [LOW] Magic Numbers / Strings & Duplicated Constants

**Categoria:** Qualidade de código.
**Sinais de detecção:** listas de valores válidos (status, categorias, roles)
ou limites numéricos (tamanho mínimo/máximo) repetidos como literais em
múltiplos arquivos em vez de centralizados em uma constante/enum única.
**Impacto:** inconsistência quando um valor válido é adicionado/removido em
só um dos lugares; código menos autoexplicativo.

---

## Observação sobre severidade

A severidade acima é a **padrão sugerida**; ao aplicar em um projeto real, a
skill deve ajustar a severidade final considerando o **contexto** (ex.: um
`print` de debug isolado é LOW, mas se ele vazar dado sensível como senha ou
número de cartão, deve ser reclassificado para CRITICAL/HIGH combinando com o
item 2 deste catálogo).
