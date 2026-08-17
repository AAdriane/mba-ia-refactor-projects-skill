```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] SQL Injection
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155-166, 174, 220, 279-281, 289-297
Description: Todas as funções de acesso a dados constroem SQL concatenando
             diretamente valores recebidos do cliente (nome, email, senha,
             termo de busca, categoria, ids) em vez de usar parâmetros (?).
Impact: Permite ler, alterar ou remover dados arbitrários (ex.: bypass de
        login com ' OR '1'='1 em login_usuario), comprometendo
        confidencialidade e integridade de todo o banco.
Recommendation: Reescrever todas as queries com placeholders parametrizados
                (cursor.execute(query, (params,))). Ver playbook #1.

[CRITICAL] Unauthenticated Sensitive/Destructive Endpoint
File: app.py:47-57, 59-78
Description: /admin/reset-db apaga todas as tabelas sem verificação de
             identidade; /admin/query executa qualquer SQL enviado no corpo
             da requisição via cursor.execute(query), também sem autenticação.
Impact: Qualquer cliente não autenticado tem controle administrativo total
        do banco, incluindo leitura de senhas e destruição completa dos dados.
Recommendation: Adicionar middleware/decorator de autenticação de admin antes
                desses handlers (ver playbook #4); remover /admin/query da
                API pública.

[CRITICAL] Hardcoded Credentials
File: app.py:7-8; controllers.py:285-289
Description: SECRET_KEY e DEBUG=True hardcoded em app.py; o endpoint /health
             retorna secret_key, debug e db_path em texto puro no JSON de
             resposta para qualquer chamador.
Impact: Segredo de assinatura de sessão exposto publicamente e versionado no
        repositório; permite forjar cookies/tokens assinados com essa chave.
Recommendation: Mover SECRET_KEY para variável de ambiente e remover campos
                sensíveis da resposta de /health. Ver playbook #2.

[HIGH] Fat Controller / Business Logic in HTTP Layer
File: controllers.py:24-96, 188-220
Description: Controllers concentram parsing de request, validação de negócio
             (faixas de preço/estoque, categorias válidas) e efeitos
             colaterais (simulação de envio de email/SMS/push via print) sem
             nenhuma camada de Service.
Impact: Regra de negócio não é reutilizável nem testável isoladamente da
        camada HTTP; endpoints que repetem a mesma regra duplicam código.
Recommendation: Extrair um Service (ex.: PedidoService) e um Validator
                reutilizável. Ver playbook #5 e #10.

[HIGH] Anemic Model / Model as Plain DAO
File: models.py (arquivo inteiro)
Description: models.py contém apenas funções que montam e executam SQL;
             nenhuma validação de invariante de domínio (preço/estoque
             não-negativos, status válido) vive no model — foi implementada
             (e duplicada) nos controllers.
Impact: Regras de negócio ficam espalhadas e podem divergir entre pontos de
        entrada diferentes que manipulam a mesma entidade.
Recommendation: Mover validações de invariante para métodos do Model/Entity.
                Ver playbook #6 e architecture-guidelines.md (seção Models).

[MEDIUM] N+1 Query Problem
File: models.py:171-233
Description: Para cada pedido é aberto um cursor para buscar itens, e para
             cada item mais um cursor para buscar o nome do produto
             (get_pedidos_usuario, get_todos_pedidos).
Impact: Uma listagem com N pedidos e M itens dispara 1 + N + N*M queries em
        vez de um JOIN, degradando performance conforme o volume cresce.
Recommendation: Substituir por uma única query com JOIN. Ver playbook #9.

[MEDIUM] Missing Transactional Atomicity
File: models.py:133-169
Description: criar_pedido faz múltiplos INSERT/UPDATE sequenciais (pedido,
             itens, baixa de estoque) com um único commit no final e nenhum
             rollback em caso de falha parcial.
Impact: Uma exceção no meio da operação (ex. após decrementar estoque de um
        item) deixa o banco em estado inconsistente.
Recommendation: Envolver as escritas em uma transação explícita com rollback
                em caso de exceção. Ver playbook #11.

[MEDIUM] Broad Exception Handling with Internal Leakage
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 163-164, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Description: Todo handler captura except Exception as e genérico e devolve
             str(e) diretamente na resposta JSON.
Impact: Mascara a causa real de erros e pode vazar detalhes internos
        (mensagens de driver de banco, nomes de tabela/coluna) ao cliente.
Recommendation: Tratar exceções específicas e usar um handler central de
                erro. Ver playbook #12.

[LOW] Unstructured Logging (print-driven)
File: controllers.py:8, 11, 57, 61, 106, 161, 164, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86
Description: print() é o único mecanismo de log usado em toda a aplicação,
             sem níveis, timestamps ou formato consistente.
Impact: Observabilidade em produção praticamente inexistente; impossível
        filtrar/desligar logs por ambiente.
Recommendation: Substituir por logging com logger configurável. Ver
                playbook #14.

[LOW] Insecure-by-Default Configuration
File: app.py:9
Description: flask-cors é aplicado via CORS(app) sem restrição de origem,
             liberando qualquer domínio a fazer requisições à API.
Impact: Amplia desnecessariamente a superfície de ataque.
Recommendation: Restringir origins explicitamente via config de ambiente.
                Ver playbook #15.

[LOW] Magic Numbers/Strings & Duplicated Constants
File: controllers.py:52, 242
Description: Listas de valores válidos (categorias de produto, status de
             pedido) são hardcoded como literais dentro dos handlers, e
             aplicadas de forma inconsistente (atualizar_produto não
             revalida categoria contra a lista).
Impact: Inconsistência entre criação/atualização de recursos; adicionar um
        novo valor válido exige lembrar de atualizar múltiplos locais.
Recommendation: Centralizar em um módulo de constantes. Ver playbook #16.

Deprecated API check: nenhuma API deprecated/EOL identificada — Flask
3.1.1 e flask-cors 5.0.1 são versões atuais, e o código não usa nenhuma
função de biblioteca marcada como deprecated.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
>
```
