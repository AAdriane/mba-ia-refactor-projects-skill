```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 2

Findings

[CRITICAL] Insecure Credential Storage
File: src/utils.js:17-23
Description: badCrypto() repete a codificação Base64 dos 2 primeiros
             caracteres da senha 10.000 vezes e corta o resultado em 10
             caracteres — não é um algoritmo de hashing criptográfico
             (determinístico, sem salt, espaço de saída minúsculo).
Impact: Colisões triviais; a "proteção" de senha é apenas aparente, senha
        real fica praticamente exposta a quem tiver o banco.
Recommendation: Substituir por bcrypt/argon2 com salt automático. Ver
                refactoring-playbook.md #7.

[CRITICAL] Unstructured Logging (dado sensível exposto)
File: src/AppManager.js:45
Description: console.log imprime o número completo do cartão de crédito
             (cc) e a chave do gateway de pagamento (config.paymentGatewayKey)
             em texto puro durante o checkout.
Impact: Violação direta de PCI-DSS (PAN de cartão em log) e vazamento
        adicional de credencial de gateway em qualquer sistema de
        agregação de logs. Severidade elevada de LOW para CRITICAL
        conforme a regra de reclassificação em antipattern-catalog.md
        (dado sensível em log = risco crítico, não apenas de observabilidade).
Recommendation: Remover completamente o log de dados sensíveis; usar logger
                estruturado sem PII/PCI. Ver refactoring-playbook.md #14.

[CRITICAL] Hardcoded Credentials
File: src/utils.js:1-7
Description: dbPass, paymentGatewayKey e smtpUser ficam hardcoded no objeto
             config exportado pelo módulo.
Impact: Chave de gateway de pagamento de produção e credenciais versionadas
        no repositório-fonte.
Recommendation: Mover para variáveis de ambiente. Ver
                refactoring-playbook.md #2.

[HIGH] God Class / God File
File: src/AppManager.js (arquivo inteiro, 141 linhas)
Description: AppManager concentra conexão com o banco, criação de schema,
             seed de dados e a lógica completa de checkout, relatório
             financeiro e exclusão de usuário — tudo em um único
             setupRoutes(). Não existe Model, Controller ou Service.
Impact: Impossível testar em isolamento; qualquer mudança em uma rota tem
        alto risco de efeito colateral nas demais.
Recommendation: Separar em Models, Controllers, Services e Routes por
                domínio. Ver refactoring-playbook.md #3.

[HIGH] Fat Controller / Business Logic in HTTP Layer
File: src/AppManager.js:28-78, 80-129
Description: Os handlers de /api/checkout e /api/admin/financial-report
             implementam toda a orquestração de negócio (validação,
             criação de usuário, processamento de pagamento, matrícula,
             auditoria; agregação de receita por curso) diretamente dentro
             do handler HTTP, com callbacks aninhados e contadores manuais
             de conclusão assíncrona (coursesPending--, enrPending--).
Impact: Regra de negócio não é reutilizável nem testável fora da camada
        HTTP; lógica frágil e propensa a condição de corrida caso um
        callback falhe silenciosamente.
Recommendation: Extrair um CheckoutService e um RelatorioFinanceiroService,
                usando async/await no lugar de callbacks aninhados. Ver
                refactoring-playbook.md #5.

[HIGH] Uncontrolled Global Mutable State
File: src/utils.js:9-15
Description: globalCache e totalRevenue são variáveis de módulo mutáveis,
             compartilhadas por todas as requisições, escritas via
             logAndCache() sem nenhum controle de ciclo de vida ou
             isolamento por requisição.
Impact: Estado pode "vazar" entre requisições concorrentes; totalRevenue
        nunca é atualizado de forma consistente, criando estado morto e
        enganoso.
Recommendation: Encapsular em uma instância de serviço injetável (ou cache
                externo). Ver refactoring-playbook.md #8.

[MEDIUM] Missing Transactional Atomicity
File: src/AppManager.js:37-77
Description: O checkout grava em users (opcional), enrollments, payments e
             audit_logs através de múltiplas chamadas db.run() sequenciais
             encadeadas por callback, sem transação nem rollback.
Impact: Uma falha no meio do fluxo (ex.: erro ao inserir audit_log) deixa
        matrícula/pagamento gravados sem o registro de auditoria
        correspondente, ou pior, sem consistência entre as tabelas.
Recommendation: Envolver as escritas em uma transação explícita
                (BEGIN/COMMIT/ROLLBACK) ou usar unit-of-work do driver. Ver
                refactoring-playbook.md #11.

[MEDIUM] N+1 Query Problem
File: src/AppManager.js:80-129
Description: /api/admin/financial-report busca todos os courses e, para
             cada curso, todas as enrollments; para cada enrollment, faz
             uma query de user e outra de payment — um loop dentro de loop
             disparando uma query por linha.
Impact: Uma base com N cursos e M matrículas por curso dispara
        1 + N + N*M*2 queries em vez de um JOIN/agregação, degradando
        performance com o crescimento dos dados.
Recommendation: Substituir por uma query agregada com JOIN entre courses,
                enrollments, users e payments. Ver
                refactoring-playbook.md #9.

[LOW] Insecure-by-Default Configuration
File: src/AppManager.js:68
Description: Quando o cliente não envia senha no checkout, o código usa
             silenciosamente o fallback "123456" (badCrypto(p || "123456"))
             para criar a conta do usuário, sem avisar nem exigir senha
             explícita.
Impact: Contas podem ser criadas com uma senha previsível e conhecida
        publicamente (está no próprio código-fonte).
Recommendation: Exigir senha explicitamente no cadastro, sem fallback
                hardcoded. Ver refactoring-playbook.md #15.

[LOW] Magic Numbers/Strings & Duplicated Constants
File: src/AppManager.js:21, 46, 48, 54, 92, 108
Description: Os literais de status de pagamento 'PAID'/'DENIED' são
             repetidos como strings soltas em múltiplos pontos do código
             (seed, verificação de bandeira do cartão, gravação do
             pagamento, agregação do relatório) em vez de uma constante
             única.
Impact: Divergência silenciosa caso um novo status seja adicionado e só
        parte dos pontos seja atualizada.
Recommendation: Centralizar em um módulo de constantes/enum. Ver
                refactoring-playbook.md #16.

Deprecated API check: nenhuma dependência com versão deprecated/EOL
detectada (Express 4.18.2 e sqlite3 5.1.6 são compatíveis com o Node.js
atual). A API do driver sqlite3 é exclusivamente baseada em callbacks (sem
suporte nativo a Promises) — não está formalmente deprecated, mas é o
principal fator técnico por trás do finding "Fat Controller / Business
Logic in HTTP Layer" acima (pyramid of callbacks). Ver
refactoring-playbook.md #13 para o padrão de migração para uma API
baseada em Promises/async-await.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
>
```
