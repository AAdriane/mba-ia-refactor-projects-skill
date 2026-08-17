# Architecture Guidelines — Target MVC Pattern (Fase 3)

Regras do padrão MVC alvo que a skill `refactor-arch` deve aplicar na Fase 3
(Refatoração), independente de linguagem/framework. O objetivo não é impor
nomes de pasta específicos de um framework, e sim garantir a **separação de
responsabilidades** descrita abaixo, adaptada à convenção idiomática da
stack detectada na Fase 1.

## Princípio central: direção única de dependência

```
Routes/Views  →  Controllers  →  Services (opcional/quando necessário)  →  Models  →  Database
```

- Uma camada só pode depender da camada imediatamente abaixo dela.
- Nunca o inverso: um Model não pode conhecer um Controller; um Controller
  não pode montar SQL diretamente; uma rota não pode conter regra de negócio.
- Camadas irmãs (ex.: dois Controllers) não devem se chamar diretamente —
  a orquestração entre domínios acontece na camada de Service ou em um
  Controller que compõe múltiplos Services.

## Camada: Models

**Responsabilidade:** representar as entidades do domínio, suas regras de
validação/invariantes e o acesso a dados dessa entidade.

Regras:
- Um Model conhece sua própria estrutura de dados e como persisti-la
  (via ORM/query builder ou uma camada de Repository interna), mas **não**
  conhece HTTP (não recebe `request`, não monta `response`, não sabe de
  status code).
- Toda query relacionada àquela entidade vive no Model (ou em um Repository
  associado a ele) — nunca dentro de um Controller/rota.
- Toda query usa **parâmetros/bind values**; concatenação de string com dado
  de entrada é proibida (ver `SQL/Query Injection` no catálogo).
- Regras de validação que são invariantes da entidade (ex.: "prioridade deve
  estar entre 1 e 5", "status deve ser um dos valores válidos") pertencem ao
  Model, não devem ser reescritas em cada Controller que usa a entidade.
- Operações que gravam em mais de uma tabela/coleção como parte de uma única
  regra de negócio devem ser executadas dentro de uma transação.
- Nenhum secret/config de infraestrutura hardcoded — conexão de banco vem de
  um módulo de configuração central alimentado por variáveis de ambiente.

## Camada: Views / Routes

**Responsabilidade:** traduzir uma requisição HTTP em uma chamada para o
Controller correto, e traduzir o retorno do Controller em uma resposta HTTP.
Em APIs (sem HTML server-side), essa camada é o *roteador* — o equivalente
mais próximo de "View" é o formato de resposta (JSON) padronizado.

Regras:
- A camada de rotas **não** contém regra de negócio, **não** acessa o banco
  diretamente, e **não** faz validação de negócio (validação de formato de
  payload básica — ex.: é JSON válido — é aceitável aqui; validação de regra
  de domínio pertence ao Controller/Model).
- Cada rota mapeia para exatamente um método de Controller.
- Formato de resposta é consistente em toda a API (mesmo envelope de sucesso/
  erro, mesmos nomes de campo) — definido uma vez, reutilizado por todas as
  rotas via helper/middleware, nunca remontado manualmente em cada handler.
- Middlewares de autenticação/autorização são declarados nesta camada
  (globalmente ou por rota), nunca verificados manualmente dentro de cada
  Controller.

## Camada: Controllers

**Responsabilidade:** orquestrar um caso de uso — receber dados já
parseados da camada de rota, chamar Model(s)/Service(s) na ordem certa,
tratar os resultados/erros, e devolver um objeto de resposta (não a resposta
HTTP final formatada — isso é papel da camada de rota, quando os dois forem
arquivos separados; em frameworks onde Controller e handler HTTP são a mesma
função, o Controller monta o corpo da resposta e delega o `status code`/envio
para o padrão único de resposta da aplicação).

Regras:
- Não contém SQL/query direta — sempre delega ao Model.
- Não duplica validação já existente no Model — chama o método de validação
  do Model em vez de reimplementar a regra.
- Efeitos colaterais que não são a operação principal (envio de notificação,
  log de auditoria, atualização de cache) devem ser extraídos para uma
  camada de Service quando houver mais de um efeito colateral ou quando o
  mesmo efeito for reutilizado por múltiplos Controllers — evita "Fat
  Controller".
- Tratamento de erro é específico por tipo de falha esperada (não encontrado,
  validação inválida, conflito) mapeado para o status HTTP correto — nunca um
  único `catch` genérico que devolve a mensagem crua da exceção para o
  cliente.
- Nenhum secret/config hardcoded dentro do Controller.

## Camada opcional: Services / Domain

Introduzir quando um Controller precisa orquestrar mais de um Model ou
executar lógica de negócio que não é uma simples validação de campo (ex.:
"processar checkout" = validar curso + criar/achar usuário + processar
pagamento + matricular + registrar auditoria + notificar). Um Service:
- Não conhece HTTP.
- Pode chamar múltiplos Models.
- É a unidade de reuso entre diferentes Controllers/rotas que precisam do
  mesmo fluxo de negócio.

## Configuração e segredos

- Toda credencial (banco, SMTP, chave de API/pagamento, secret key de
  assinatura) vem de variável de ambiente, carregada por um único módulo de
  configuração (`config.py`, `config/index.js`, etc.).
- Nenhum valor de configuração sensível é retornado em uma resposta de API
  (nem em endpoints de health-check/debug).
- Flags de debug/verbose só ficam ativas quando a variável de ambiente de
  ambiente (`ENV`/`NODE_ENV`/etc.) explicitamente indicar desenvolvimento.

## Tratamento de erros

- Erros esperados de negócio (não encontrado, validação, conflito, não
  autorizado) são tratados explicitamente e mapeados para o status HTTP
  correspondente (`400`, `401`, `403`, `404`, `409`).
- Erros inesperados são capturados por um handler central (middleware de
  erro) que loga o detalhe internamente e devolve ao cliente uma mensagem
  genérica — nunca o stack trace ou mensagem crua do driver de banco.
- Logging estruturado (nível, timestamp, contexto) substitui `print`/
  `console.log` soltos pelo código.

## Estrutura de diretórios de referência

A convenção exata de nomes de pasta segue o idioma do framework
detectado na Fase 1, mas a separação abaixo deve sempre existir:

```
src/
├── config/         # configuração central, leitura de env vars
├── models/         # entidades de domínio + acesso a dados
├── routes/         # (ou views/, controllers HTTP-only em alguns frameworks)
├── controllers/     # orquestração de casos de uso
├── services/        # (quando necessário) regra de negócio multi-entidade
├── middlewares/      # autenticação, tratamento de erro centralizado
└── app.py|index.js  # composition root — monta app, registra rotas/middlewares
```

Frameworks com convenção própria (ex.: Django com `apps/`, Rails com
`app/models|controllers|views`) devem ter sua convenção idiomática respeitada
— o que importa é a separação de responsabilidades, não o nome literal da
pasta.
