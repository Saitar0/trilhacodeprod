---
arquivo_id: "f9-43-2-90-integracao-p01-pratica"
parent_key: "43.2"
tipo_arquivo: "practice"
assuntos: ["01_slim_http_composicao", "03_comparacao_trabalho_completo"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Compare a composição de uma API
**Contexto:** uma equipe quer expor `GET /clientes/{id}`. O serviço precisa autenticar, validar parâmetro, consultar PostgreSQL e devolver JSON. A equipe já usa Laravel, mas considera Slim para um serviço menor.

**Instruções:** trace quais componentes Laravel oferece por convenção e o que a equipe precisa adicionar/configurar no Slim. Para Slim, indique onde ficam rota, middleware, request/response PSR-7, acesso a dados e tratamento de erro. Registre uma dependência que verificaria antes de adotá-lo e um motivo que justificaria manter Laravel.

**Entrega:** tabela de responsabilidades e recomendação de até 120 palavras, com uma fonte oficial para o comportamento PSR.

**Dica gradual:** separe a camada HTTP das decisões de autenticação, validação e persistência; não marque “incluído pelo framework” sem conferir documentação/pacotes instalados.

