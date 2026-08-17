```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1160 lines of code

Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 4 | LOW: 2

Findings

[CRITICAL] Hardcoded Credentials
File: app.py:13; services/notification_service.py:9-10
Description: SECRET_KEY hardcoded como 'super-secret-key-123' em app.py; o
             NotificationService também tem email_user e email_password
             ('senha123') hardcoded, apesar de python-dotenv estar listado
             em requirements.txt e nunca ser usado para carregar essas
             variáveis de um .env.
Impact: Segredo de assinatura da aplicação e credencial SMTP de produção
        versionados no repositório-fonte.
Recommendation: Carregar via variáveis de ambiente com python-dotenv (já é
                dependência do projeto). Ver refactoring-playbook.md #2.

[CRITICAL] Unauthenticated Sensitive/Destructive Endpoint
File: routes/user_routes.py:185-211 (login); routes/task_routes.py:225-238
      (delete_task); routes/user_routes.py:134-151 (delete_user);
      routes/report_routes.py:211-223 (delete_category)
Description: O login retorna um token estático ('fake-jwt-token-' +
             user.id) que nunca é validado em nenhuma outra rota — na
             prática, todos os endpoints da API, incluindo os DELETE de
             task/usuário/categoria, são publicamente acessíveis sem
             qualquer autenticação real.
Impact: Qualquer cliente não autenticado pode ler, alterar ou apagar
        qualquer task, usuário ou categoria do sistema.
Recommendation: Implementar verificação real de token (JWT assinado) em um
                middleware aplicado às rotas sensíveis. Ver
                refactoring-playbook.md #4.

[HIGH] Insecure Credential Storage
File: models/user.py:27-32
Description: set_password/check_password usam hashlib.md5 sem salt para
             armazenar e comparar a senha do usuário.
Impact: MD5 é criptograficamente quebrado; vazamento do banco expõe senhas
        a ataques de força bruta/rainbow table triviais.
Recommendation: Substituir por werkzeug.security.generate_password_hash /
                check_password_hash. Ver refactoring-playbook.md #7.

[HIGH] Fat Controller / Business Logic in HTTP Layer
File: routes/task_routes.py:85-154 (create_task); routes/user_routes.py:42-90
      (create_user); services/notification_service.py:27-36
Description: As rotas manipulam db.session e executam toda a validação de
             negócio diretamente no handler HTTP, sem nenhuma camada de
             Service/Controller intermediária, apesar de já existir a
             pasta services/. O próprio NotificationService.notify_task_assigned
             existe especificamente para notificar atribuição de task, mas
             nunca é chamado por create_task nem por nenhuma outra rota.
Impact: Regra de negócio não reutilizável nem testável isoladamente da
        camada HTTP; funcionalidade de notificação já implementada fica
        morta por falta de integração.
Recommendation: Extrair TaskService/UserService chamados pelas rotas, e
                integrar NotificationService a esse Service. Ver
                refactoring-playbook.md #5.

[MEDIUM] Duplicated Validation / Business Logic (DRY Violation)
File: routes/task_routes.py:30-39, 71-80; routes/user_routes.py:171-180;
      routes/report_routes.py:33-37
Description: O cálculo de "task atrasada" é reescrito de forma idêntica em
             4 lugares diferentes, embora Task.is_overdue() já implemente
             exatamente essa regra em models/task.py:50-60 e nunca seja
             chamado. Da mesma forma, utils/helpers.process_task_data()
             (utils/helpers.py:57-108) centraliza validação de task mas
             nunca é importado pelas rotas, que duplicam a mesma validação
             inline em create_task e update_task.
Impact: Risco de divergência silenciosa se a regra mudar em só um dos
        pontos; código de validação já escrito e testável fica sem uso.
Recommendation: Chamar Task.is_overdue() e utils.helpers.process_task_data()
                a partir das rotas em vez de duplicar a lógica. Ver
                refactoring-playbook.md #6 e #10.

[MEDIUM] N+1 Query Problem
File: routes/report_routes.py:53-68 (summary_report); routes/task_routes.py:41-57
      (get_tasks)
Description: summary_report dispara uma query Task.query.filter_by(user_id=...)
             por usuário dentro de um loop Python; get_tasks dispara uma
             query User.query.get(...) e outra Category.query.get(...) por
             task dentro do loop de serialização.
Impact: Ambos os endpoints escalam o número de queries linearmente com o
        volume de usuários/tasks em vez de usar JOIN/eager loading.
Recommendation: Usar joinedload do SQLAlchemy ou uma query agregada com
                JOIN/GROUP BY. Ver refactoring-playbook.md #9.

[MEDIUM] Broad Exception Handling
File: routes/task_routes.py:62; routes/report_routes.py:186-188, 207-209, 221-223
Description: get_tasks, create_category, update_category e delete_category
             usam except: genérico (bare except) sem tipo, retornando uma
             mensagem de erro fixa e descartando a exceção real.
Impact: Mascara a causa real de bugs de programação, dificultando debug em
        produção (ex.: um AttributeError passa despercebido como se fosse
        erro esperado de negócio).
Recommendation: Capturar exceções específicas e logar a exceção original
                antes de responder genericamente. Ver
                refactoring-playbook.md #12.

[MEDIUM] Deprecated / End-of-Life API Usage
File: models/task.py:15-16, 52; routes/task_routes.py:31, 72;
      routes/user_routes.py:172; routes/report_routes.py:35, 42, 45, 48, 50, 71;
      services/notification_service.py:35
Description: datetime.utcnow() é usado extensivamente em todo o projeto;
             esse método está deprecated desde o Python 3.12 em favor de
             datetime.now(timezone.utc), por retornar um datetime "naive"
             que pode causar bugs de fuso horário.
Impact: Warnings de deprecation em versões recentes do Python e risco de
        remoção completa da API em versões futuras.
Recommendation: Substituir por datetime.now(timezone.utc) em todos os
                pontos. Ver refactoring-playbook.md #13.

[LOW] Insecure-by-Default Configuration
File: app.py:15
Description: CORS(app) é aplicado sem restrição de origem, liberando
             qualquer domínio a fazer requisições à API.
Impact: Amplia desnecessariamente a superfície de ataque.
Recommendation: Restringir origins explicitamente via variável de
                ambiente. Ver refactoring-playbook.md #15.

[LOW] Magic Numbers/Strings & Duplicated Constants
File: routes/task_routes.py:110, 113-114, 177, 182-183; utils/helpers.py:75, 84, 110-116
Description: A lista de status válidos ['pending','in_progress','done','cancelled']
             e a faixa de prioridade (1-5) são repetidas como literais em
             create_task e update_task, mesmo já existindo as constantes
             VALID_STATUSES/MIN_TITLE_LENGTH/DEFAULT_PRIORITY em
             utils/helpers.py:110-116 — que nunca são importadas por
             nenhuma rota.
Impact: Divergência silenciosa se um novo status/faixa válida for
        adicionado e só parte dos pontos for atualizada.
Recommendation: Importar e reutilizar as constantes já existentes em
                utils/helpers.py. Ver refactoring-playbook.md #16.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
>
```
