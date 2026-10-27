---
arquivo_id: "f9-42-3-01-api-validacao-documentacao-01-teoria"
parent_key: "42.3"
tipo_arquivo: "theory"
assunto: "01_api_validacao_documentacao"
ordem: 1
itens_origem: ["### 1. API, validação e documentação"]
---


### 1. API, validação e documentação
**FastAPI** organiza operações HTTP usando declarações Python e modelos de dados. Type hints e modelos Pydantic ajudam a interpretar parâmetros, validar/serializar dados e gerar um schema OpenAPI com documentação interativa. Esse fluxo reduz repetição em APIs orientadas a contratos, mas não define sozinho regra de negócio, autorização, persistência, limites de uso ou testes. Um campo com tipo correto não prova que o usuário pode alterar aquele recurso.

**Flask** oferece rotas e ciclo de requisição com um núcleo pequeno. Validação, schema OpenAPI, ORM, autenticação e outras funções costumam vir de bibliotecas/extensões escolhidas pela aplicação. A equipe ganha liberdade para montar a composição, assumindo decisões de compatibilidade, integração, atualização e segurança.

**Django com DRF**, da unidade 42.1, oferece um conjunto mais integrado e convencionado: apps, ORM, migrations, serializers, views/routers e controles de acesso. Para API pequena, isso pode ser mais estrutura do que o caso precisa; para uma aplicação com persistência, administração e convenções comuns, pode evitar escolhas dispersas.

**Checagem:** geração de OpenAPI ou serializer valida autorização? Não. Validação descreve/limita dados; autorização decide quem pode realizar qual ação.

