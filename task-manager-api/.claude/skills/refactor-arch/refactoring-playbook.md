# Refactoring Playbook (Fase 3)

Padrões concretos de transformação, um por anti-pattern do
`antipattern-catalog.md`. Cada padrão traz a ideia geral (agnóstica de
linguagem) e um exemplo antes/depois. Os exemplos usam Python e
JavaScript/TypeScript como ilustração — aplique a mesma transformação
conceitual na sintaxe da linguagem real do projeto analisado.

Este playbook cobre **16 padrões de transformação** (mínimo exigido: 8).

---

## 1. SQL/Query Injection → Parameterized Queries

**Ideia:** nunca concatenar dado de entrada na string da query; sempre usar
placeholders/bind parameters (nativo do driver) ou métodos do ORM.

```python
# Antes
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

# Depois
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

```javascript
// Antes
db.get(`SELECT * FROM users WHERE email = '${email}'`);

// Depois
db.get("SELECT * FROM users WHERE email = ?", [email]);
```

## 2. Hardcoded Credentials → Environment-based Config

**Ideia:** extrair todo secret para variável de ambiente, lida por um único
módulo de configuração; nunca retornar secrets em respostas de API.

```python
# Antes
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"

# Depois — config.py
import os
SECRET_KEY = os.environ["SECRET_KEY"]   # falha explicitamente se não setado

# app.py
app.config["SECRET_KEY"] = config.SECRET_KEY
```

```javascript
// Antes — utils.js
const config = { paymentGatewayKey: "pk_live_1234567890abcdef" };

// Depois — config.js
const config = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
};
if (!config.paymentGatewayKey) throw new Error("PAYMENT_GATEWAY_KEY não definido");
```

## 3. God Class / God File → Split by Responsibility

**Ideia:** dividir por domínio (entidade) e por camada (rota, controller,
model, service), cada arquivo com uma única razão para mudar.

```
# Antes
models.py            # produtos + usuários + pedidos + relatório, tudo junto

# Depois
models/produto.py     # entidade Produto + acesso a dados de produto
models/usuario.py     # entidade Usuario + acesso a dados de usuário
models/pedido.py       # entidade Pedido + acesso a dados de pedido
controllers/produto_controller.py
controllers/pedido_controller.py
services/relatorio_service.py
```

```javascript
// Antes: AppManager.js concentra DB + rotas + regra de negócio

// Depois
// models/courseModel.js     -> queries de courses
// models/enrollmentModel.js -> queries de enrollments/payments
// services/checkoutService.js -> orquestra o fluxo de checkout
// controllers/checkoutController.js -> chama checkoutService, monta resposta
// routes/checkoutRoutes.js  -> declara a rota e chama o controller
```

## 4. Unauthenticated Sensitive Endpoint → Auth Middleware/Guard

**Ideia:** extrair verificação de identidade/role para um middleware
reutilizável, aplicado explicitamente às rotas sensíveis.

```python
# Antes
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    ...  # sem verificação de quem está chamando

# Depois
from functools import wraps
from flask import request, abort

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not is_valid_admin_token(token):
            abort(401)
        return f(*args, **kwargs)
    return wrapper

@app.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    ...
```

## 5. Fat Controller → Extract Service Layer

**Ideia:** mover orquestração de múltiplos passos/efeitos colaterais para um
Service; o Controller passa a apenas chamar o Service e formatar a resposta.

```python
# Antes — dentro do controller
def criar_pedido():
    dados = request.get_json()
    resultado = models.criar_pedido(dados["usuario_id"], dados["itens"])
    print("ENVIANDO EMAIL...")
    print("ENVIANDO SMS...")
    return jsonify(resultado), 201

# Depois
# services/pedido_service.py
class PedidoService:
    def __init__(self, pedido_model, notification_service):
        self.pedido_model = pedido_model
        self.notification_service = notification_service

    def criar_pedido(self, usuario_id, itens):
        pedido = self.pedido_model.criar(usuario_id, itens)
        self.notification_service.notificar_pedido_criado(pedido)
        return pedido

# controllers/pedido_controller.py
def criar_pedido():
    dados = request.get_json()
    pedido = pedido_service.criar_pedido(dados["usuario_id"], dados["itens"])
    return jsonify(pedido), 201
```

## 6. Anemic Model → Move Domain Rules into the Model

**Ideia:** mover validações/invariantes duplicadas nos controllers para
métodos do próprio Model, e passar a chamá-los em vez de reimplementar.

```python
# Antes — regra duplicada em rota após rota
if t.due_date and t.due_date < datetime.utcnow() and t.status not in ("done", "cancelled"):
    overdue = True
else:
    overdue = False

# Depois — já existe no Model, só falta ser usado
class Task(db.Model):
    def is_overdue(self):
        if not self.due_date:
            return False
        return self.due_date < datetime.utcnow() and self.status not in ("done", "cancelled")

# em qualquer rota
task_data["overdue"] = task.is_overdue()
```

## 7. Insecure Credential Storage → Strong Hashing Algorithm

**Ideia:** substituir armazenamento em texto puro (ou MD5/SHA1 sem salt) por
um algoritmo de hash com custo ajustável e salt automático.

```python
# Antes
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()

# Depois
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

## 8. Uncontrolled Global Mutable State → Encapsulated/Injected State

**Ideia:** remover variáveis globais mutáveis; encapsular estado em uma
instância gerenciada (injeção de dependência) ou substituir por um cache
externo (Redis) quando o estado precisa sobreviver entre instâncias.

```javascript
// Antes — utils.js
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }

// Depois — cacheService.js
class CacheService {
  constructor() { this._store = new Map(); }
  set(key, value) { this._store.set(key, value); }
  get(key) { return this._store.get(key); }
}
module.exports = new CacheService(); // instância única, controlada e testável
```

## 9. N+1 Query Problem → Batch Fetch / Join / Eager Loading

**Ideia:** substituir uma query por item do loop por uma única query que traz
tudo de uma vez (JOIN, `WHERE id IN (...)`, ou eager loading do ORM).

```python
# Antes
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido.id,))
    for item in itens:
        produto = db.execute("SELECT nome FROM produtos WHERE id = ?", (item.produto_id,))

# Depois
rows = db.execute("""
    SELECT p.id AS pedido_id, ip.produto_id, ip.quantidade, pr.nome AS produto_nome
    FROM pedidos p
    JOIN itens_pedido ip ON ip.pedido_id = p.id
    JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.id IN (?, ?, ?)
""", pedido_ids)
# agrupar rows em memória por pedido_id
```

```python
# Depois (com ORM/SQLAlchemy)
pedidos = Pedido.query.options(
    db.joinedload(Pedido.itens).joinedload(ItemPedido.produto)
).all()
```

## 10. Duplicated Validation Logic → Shared Validator/Schema

**Ideia:** extrair a validação repetida para uma função/schema único,
reutilizado por todos os pontos de entrada que recebem aquele payload.

```python
# Antes — bloco repetido em criar_produto e atualizar_produto
if preco < 0: return jsonify({"erro": "Preço não pode ser negativo"}), 400
if estoque < 0: return jsonify({"erro": "Estoque não pode ser negativo"}), 400

# Depois — validators/produto_validator.py
def validar_produto(dados):
    erros = []
    if dados.get("preco", 0) < 0:
        erros.append("Preço não pode ser negativo")
    if dados.get("estoque", 0) < 0:
        erros.append("Estoque não pode ser negativo")
    return erros

# usado em criar_produto E atualizar_produto
erros = validar_produto(dados)
if erros:
    return jsonify({"erro": erros}), 400
```

## 11. Missing Transactional Atomicity → Explicit Transaction Boundary

**Ideia:** agrupar todas as escritas de uma mesma operação de negócio em uma
transação com rollback automático em caso de exceção.

```python
# Antes — cada execute com commit implícito separado, sem rollback

# Depois
def criar_pedido(usuario_id, itens):
    try:
        db.session.begin()
        pedido = Pedido(usuario_id=usuario_id, total=calcular_total(itens))
        db.session.add(pedido)
        for item in itens:
            db.session.add(ItemPedido(pedido=pedido, **item))
            baixar_estoque(item, db.session)
        db.session.commit()
        return pedido
    except Exception:
        db.session.rollback()
        raise
```

## 12. Broad Exception Handling → Specific Errors + Central Handler

**Ideia:** capturar tipos de erro específicos e delegar o desconhecido a um
handler central que não vaza detalhe interno ao cliente.

```python
# Antes
try:
    ...
except Exception as e:
    return jsonify({"erro": str(e)}), 500

# Depois
class NotFoundError(Exception): pass
class ValidationError(Exception): pass

try:
    ...
except NotFoundError as e:
    return jsonify({"erro": str(e)}), 404
except ValidationError as e:
    return jsonify({"erro": str(e)}), 400

# app.py — handler central para o resto
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    logger.exception("Erro não tratado")
    return jsonify({"erro": "Erro interno"}), 500
```

## 13. Deprecated/EOL API Usage → Modern Equivalent

**Ideia:** identificar a API/versão deprecated (via changelog/documentação
oficial da dependência detectada na Fase 1) e migrar para o substituto
recomendado, mantendo o mesmo comportamento externo.

```javascript
// Antes — API de callback deprecated em favor de Promises/async-await
db.get(sql, params, function (err, row) { /* ... */ });

// Depois — usando driver/wrapper com suporte a Promises
const row = await db.getAsync(sql, params);
```

```python
# Antes — datetime.utcnow() é deprecated a partir do Python 3.12
created_at = datetime.utcnow()

# Depois
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

## 14. Unstructured Logging → Structured Logger

**Ideia:** substituir `print`/`console.log` por um logger configurável com
níveis e formato consistente.

```python
# Antes
print("ERRO ao criar produto: " + str(e))

# Depois
import logging
logger = logging.getLogger(__name__)
logger.error("Erro ao criar produto", exc_info=e)
```

## 15. Insecure-by-Default Configuration → Explicit, Environment-driven Config

**Ideia:** tornar configurações sensíveis explícitas e dependentes do
ambiente, nunca abertas por padrão.

```python
# Antes
CORS(app)  # libera qualquer origem
app.config["DEBUG"] = True

# Depois
CORS(app, origins=os.environ.get("ALLOWED_ORIGINS", "").split(","))
app.config["DEBUG"] = os.environ.get("FLASK_ENV") == "development"
```

## 16. Magic Numbers/Strings → Centralized Constants/Enum

**Ideia:** extrair listas de valores válidos e limites numéricos repetidos
para um único módulo de constantes/enum, referenciado por todo o código.

```python
# Antes — repetido em múltiplos arquivos
if categoria not in ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]:
    ...

# Depois — constants.py
class Categoria:
    VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

# uso
if categoria not in Categoria.VALIDAS:
    ...
```

---

## Validação pós-refatoração (checklist mínimo da Fase 3)

Após aplicar os padrões acima, a skill deve validar:
1. A aplicação sobe sem erro (`npm start`/`python app.py`/equivalente).
2. Os endpoints originais (mapeados na Fase 1) continuam respondendo com o
   mesmo contrato de entrada/saída.
3. Nenhum anti-pattern CRITICAL do relatório da Fase 2 permanece sem
   tratamento.
4. A nova estrutura de diretórios segue `architecture-guidelines.md`.
