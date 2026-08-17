# Audit Report Template (Fase 2)

Este é o formato **obrigatório e literal** do relatório de auditoria impresso
ao final da Fase 2. Ele deve ser gerado independente da linguagem/framework do
projeto analisado, apenas os valores entre `<...>` mudam.

## Formato

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <Linguagem + Framework>
Files:   <N> analyzed | ~<X> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[<SEVERITY>] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo de linhas>
Description: <descrição objetiva do que foi encontrado, específica ao trecho
             de código, não uma definição genérica do anti-pattern>
Impact: <consequência concreta se não for corrigido>
Recommendation: <ação de refatoração recomendada, referenciando o padrão do
                refactoring-playbook.md quando aplicável>

[<SEVERITY>] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo de linhas>
Description: ...
Impact: ...
Recommendation: ...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> 
```

## Regras de preenchimento

1. **Cabeçalho (`Project`/`Stack`/`Files`)** — vem diretamente do resumo
   produzido na Fase 1 (`project-analysis.md`). `Files` é o número de
   arquivos-fonte efetivamente analisados; `lines of code` é aproximado
   (arredondar para a centena mais próxima é aceitável, ex.: `~800`).
2. **Summary** — contagem de findings por severidade, na ordem fixa
   `CRITICAL | HIGH | MEDIUM | LOW`, mesmo quando algum valor for `0`.
3. **Findings — ordenação obrigatória**: sempre do mais severo para o menos
   severo (`CRITICAL` → `HIGH` → `MEDIUM` → `LOW`). Dentro da mesma
   severidade, ordenar pela ordem em que os arquivos aparecem no projeto.
4. **Nome do anti-pattern** — usar o nome exato listado em
   `antipattern-catalog.md` (ex.: `God Class / God Method`,
   `Hardcoded Credentials`, `SQL Injection`, `N+1 Query Problem`) para manter
   rastreabilidade entre o catálogo e o relatório.
5. **`File`** — sempre arquivo **e** linha(s) exatas do trecho encontrado.
   Nunca reportar um finding sem localização precisa. Se o anti-pattern se
   repete no mesmo arquivo em pontos não contíguos, listar as linhas
   principais (ex.: `models.py:28, 47-50, 92`) ou abrir um finding por
   ocorrência quando a severidade/descrição diferir.
6. **`Description`** — específica ao código real encontrado (cite nomes de
   função/variável quando ajudar), não repita apenas a definição genérica do
   catálogo.
7. **`Impact`** — consequência concreta e prática (ex.: "permite apagar todos
   os pedidos sem autenticação", não apenas "problema de segurança").
8. **`Recommendation`** — ação objetiva de refatoração, referenciando o
   padrão correspondente do `refactoring-playbook.md` quando existir um.
9. **Total** — igual à soma de todos os itens do `Summary`.
10. **Confirmação obrigatória** — o relatório sempre termina perguntando
    `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e a skill
    **deve aguardar a resposta do usuário** antes de iniciar qualquer
    modificação de arquivo na Fase 3. Resposta diferente de "sim"/`y` cancela
    a Fase 3 sem alterar nenhum arquivo.

## Exemplo preenchido (ilustrativo)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

Findings

[CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL,
             validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

[CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'.
Impact: Compromete a assinatura de sessão/cookies em produção caso o
        repositório vaze.
Recommendation: Mover para variável de ambiente e carregar via config
                dedicado (ver refactoring-playbook.md).

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```
