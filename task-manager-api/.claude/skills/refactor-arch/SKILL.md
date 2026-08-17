# refactor-arch — Auditoria e Refatoração de Arquitetura para MVC

Skill agnóstica de tecnologia que analisa um projeto de backend, audita sua
arquitetura contra um catálogo de anti-patterns, e o refatora para o padrão
MVC — sem assumir uma linguagem, framework ou banco de dados específico.

## Arquivos de referência

Antes de executar qualquer fase, carregue o arquivo de referência
correspondente (estão neste mesmo diretório). Eles contêm o conhecimento
que esta skill usa, não improvise heurísticas, catálogo, template ou
padrões de refatoração fora do que está documentado neles:

| Arquivo | Usado na fase | Conteúdo |
|---|---|---|
| `project-analysis.md` | Fase 1 | Heurísticas de detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| `antipattern-catalog.md` | Fase 2 | Catálogo de anti-patterns com sinais de detecção e severidade |
| `audit-report-template.md` | Fase 2 | Formato obrigatório do relatório de auditoria |
| `architecture-guidelines.md` | Fase 3 | Regras do padrão MVC alvo (Models, Views/Routes, Controllers) |
| `refactoring-playbook.md` | Fase 3 | Padrões de transformação com exemplos de código antes/depois |

## Escopo e diretório de trabalho

- Esta skill opera sobre o projeto localizado no diretório de trabalho atual
  (cwd) ou informado explicitamente pelo usuário, **nunca** sobre outro
  projeto do repositório sem confirmação.
- Nunca analise/modifique os arquivos da própria skill (`.claude/skills/**`)
  nem o `README.md` do desafio.
- As 3 fases são **sequenciais e obrigatórias nessa ordem**. Não pule uma
  fase, mesmo que o projeto pareça simples.

---

## Fase 1 — Project Analysis

**Objetivo:** detectar a stack e mapear a arquitetura atual, sem alterar
nenhum arquivo.

Passos:
1. Ler `project-analysis.md` e aplicar suas heurísticas para detectar:
   linguagem, framework (+ versão quando possível), gerenciador de
   dependências, banco de dados/ORM, e onde a conexão de banco é criada.
2. Localizar o arquivo de entrada da aplicação e seguir o fluxo de uma
   requisição típica ponta a ponta (ver seção 4 de `project-analysis.md`).
3. Identificar o domínio da aplicação a partir das rotas/entidades
   (ex.: "e-commerce", "task manager", "LMS/checkout").
4. Contar o número de arquivos-fonte analisados (excluindo
   dependências/`node_modules`/`venv`/build) e uma estimativa de linhas de
   código.
5. Mapear quais camadas já existem (models/routes/controllers/services) e
   quais estão ausentes.
6. Imprimir o resumo no formato abaixo e seguir automaticamente para a
   Fase 2 (esta fase não modifica arquivos, então não requer confirmação):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <dependências relevantes>
Domain:        <domínio inferido>
Architecture:  <resumo textual da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas/coleções identificadas>
================================
```

---

## Fase 2 — Architecture Audit

**Objetivo:** cruzar o código contra o catálogo de anti-patterns e gerar o
relatório de auditoria. **Não modifica nenhum arquivo.**

Passos:
1. Ler `antipattern-catalog.md` e, para cada anti-pattern do catálogo,
   procurar seus sinais de detecção no código do projeto analisado.
2. Para cada ocorrência encontrada, registrar: nome do anti-pattern (igual
   ao nome usado no catálogo), severidade, arquivo e linha(s) exatas,
   descrição específica do trecho, impacto concreto, e recomendação (
   referenciando o padrão correspondente do `refactoring-playbook.md`
   quando existir).
3. Verificar explicitamente uso de APIs/dependências deprecated ou EOL
   (ver item "Deprecated / End-of-Life API Usage" do catálogo) e incluir
   como findings quando aplicável.
4. Ordenar os findings por severidade, `CRITICAL → HIGH → MEDIUM → LOW`.
5. Montar o relatório **seguindo exatamente** o formato de
   `audit-report-template.md` (cabeçalho, `Summary`, `Findings`, `Total`).
6. Salvar o relatório também em `reports/audit-project-N.md` na raiz do
   repositório (pergunte ao usuário o número do projeto/nome do arquivo se
   não estiver claro pelo contexto da conversa).
7. Imprimir o relatório completo e, ao final, perguntar explicitamente:
   `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
8. **Parar e aguardar a resposta do usuário.** Só prosseguir para a Fase 3
   se a resposta for afirmativa (`y`/`sim`/equivalente). Qualquer outra
   resposta encerra a execução sem modificar nenhum arquivo.

Regras rígidas desta fase:
- Mínimo de 5 findings no relatório final (o projeto deve ter mais que
  isso na prática, não artificialmente inflar nem omitir achados reais).
- Todo finding precisa de arquivo e linha exatos, nunca reportar um
  achado vago sem localização.
- **Nenhum arquivo do projeto é criado, editado ou apagado nesta fase.**

---

## Fase 3 — MVC Refactoring

**Objetivo:** reestruturar o projeto para o padrão MVC e validar que ele
continua funcionando. Só executa após confirmação explícita na Fase 2.

Passos:
1. Ler `architecture-guidelines.md` para saber a separação de
   responsabilidades alvo (Models / Views-Routes / Controllers / Services
   opcional) e a convenção de diretórios a aplicar, adaptada à stack
   detectada na Fase 1.
2. Ler `refactoring-playbook.md` e aplicar o padrão de transformação
   correspondente a **cada** finding do relatório da Fase 2, começando
   pelos de maior severidade (`CRITICAL` primeiro).
3. Criar a nova estrutura de diretórios (`models/`, `routes/` ou `views/`,
   `controllers/`, `services/` quando necessário, `config/`,
   `middlewares/`), movendo/reescrevendo o código existente — não
   reescreva do zero funcionalidades que já existem, apenas reorganize e
   corrija.
4. Extrair toda configuração/segredo hardcoded para um módulo de config
   central alimentado por variáveis de ambiente (criar `.env.example` com
   as chaves esperadas, sem valores reais).
5. Centralizar tratamento de erro (handler/middleware único), remover
   `print`/`console.log` soltos em favor de logging estruturado, e
   parametrizar toda query SQL identificada como vulnerável na Fase 2.
6. Manter o **entry point** claro (um único arquivo que monta a aplicação,
   registra rotas/middlewares e sobe o servidor).
7. **Validar o resultado:**
   - Instalar dependências se necessário e iniciar a aplicação
     (equivalente a `python app.py` / `npm start` / etc.).
   - Confirmar que ela sobe sem erro (sem exceptions no boot).
   - Chamar os endpoints originais mapeados na Fase 1 (ex.: via `curl` ou
     o `api.http`/coleção de exemplos do projeto, se existir) e confirmar
     que respondem com o mesmo contrato de entrada/saída de antes da
     refatoração.
   - Se algo quebrar, corrigir antes de declarar a fase concluída — nunca
     entregar um estado que não builda/não sobe.
8. Imprimir o resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  <✓ ou ✗> Application boots without errors
  <✓ ou ✗> All endpoints respond correctly
  <✓ ou ✗> <N>/<N> CRITICAL/HIGH findings resolved
================================
```

---

## Guidelines gerais (todas as fases)

- **Agnosticismo de tecnologia:** nunca hardcode um nome de framework/
  linguagem específico na lógica da skill. Toda decisão de "o que é MVC
  aqui" vem das heurísticas de `project-analysis.md` e das regras de
  `architecture-guidelines.md`, aplicadas ao que foi detectado na Fase 1.
- **Rastreabilidade:** o nome de cada anti-pattern deve ser idêntico entre
  o catálogo, o relatório e a recomendação de refatoração, isso é o que
  permite ao usuário conferir que cada finding da Fase 2 foi endereçado na
  Fase 3.
- **Não silenciar risco:** se um finding CRITICAL/HIGH não puder ser
  totalmente corrigido de forma segura (ex.: exigiria trocar tecnologia de
  banco), refatore o máximo possível e declare explicitamente no resumo
  final o que ficou pendente e por quê, nunca marque como resolvido algo
  que não foi.
- **Não avançar sem confirmação:** a pausa entre Fase 2 e Fase 3 é
  obrigatória mesmo em execuções não interativas — se não houver como
  perguntar, pare e relate que a confirmação é necessária.
- **Preservar comportamento externo:** a refatoração muda a organização
  interna do código, não o contrato público da API (rotas, payloads,
  status codes), a menos que o próprio finding exija a mudança (ex.: um
  endpoint administrativo destrutivo sem autenticação passa a exigir
  autenticação — uma mudança de contrato justificada pela severidade
  CRITICAL do achado).

## Instruções de execução

Invocação (Claude Code):

```bash
cd <diretório do projeto a analisar>   # ex.: code-smells-project/
claude "/refactor-arch"
```

A skill deve ser copiada (pasta `.claude/skills/refactor-arch/` completa,
incluindo os 5 arquivos de referência) para dentro de cada projeto-alvo
antes de ser invocada nele, já que ela opera sobre o diretório de trabalho
atual.

Fluxo esperado de uma execução completa:
1. Fase 1 roda automaticamente e imprime o resumo de análise.
2. Fase 2 roda automaticamente em seguida, imprime o relatório completo e
   pausa perguntando `[y/n]`.
3. Somente com `y`, a Fase 3 executa a refatoração e termina imprimindo o
   resumo de validação.

## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido em `audit-report-template.md`
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
