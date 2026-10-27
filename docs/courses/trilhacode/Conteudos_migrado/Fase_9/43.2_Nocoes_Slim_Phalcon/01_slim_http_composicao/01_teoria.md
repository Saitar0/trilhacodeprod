---
arquivo_id: "f9-43-2-01-slim-http-composicao-01-teoria"
parent_key: "43.2"
tipo_arquivo: "theory"
assunto: "01_slim_http_composicao"
ordem: 1
itens_origem: ["### 1. Slim: HTTP e composição de componentes"]
---


### 1. Slim: HTTP e composição de componentes
Slim é um microframework PHP para aplicações web e APIs. No Slim 4, a aplicação declara rotas e encadeia middleware sobre objetos de requisição e resposta PSR-7. A rota recebe request/response e deve devolver uma resposta compatível com PSR-7. Middleware pode atuar antes e depois do handler; a ordem de registro e a posição dos middlewares de roteamento/erro importam.

PSR-7 define interfaces comuns para mensagens HTTP; PSR-15 padroniza interfaces de middleware e handlers. Isso facilita combinar bibliotecas PHP que implementam os padrões, mas não significa que banco, ORM, validação, autenticação ou documentação OpenAPI venham automaticamente. A equipe escolhe as dependências, configura sua integração e acompanha versões e segurança.

**Checagem:** Slim é uma implementação completa de backend de negócio por si só? Não; fornece infraestrutura HTTP enxuta, e a aplicação seleciona e conecta outras partes conforme necessário.

