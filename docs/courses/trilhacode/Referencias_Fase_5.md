---
title: "Referências — Fase 5"
aliases:
  - Referências da Fase 5
tags:
  - trilhas
  - referencias
tipo: referencia
status: planejamento
---

# Referências — Fase 5

> [!abstract] Como usar
> Lista de referências selecionadas para a Fase 5. Cada item segue o padrão
> do [[Guia_de_Producao_de_Conteudo|guia de produção]]: **título + URL + o que cobre**.
> Antes de produzir cada unidade, confira a URL e a cobertura e registre a data da conferência no conteúdo; materiais secundários complementam, mas não substituem as fontes principais.
> Mínimo de 2 referências por submódulo obrigatório e 1 por repertório/opcional.

## 17.1 — Fundamentos

- **Node.js Docs — Event loop** · https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick · event loop e processamento assíncrono.
- **Node.js Docs — Streams** · https://nodejs.org/api/stream.html · streams.
- **Node.js Docs — Packages** · https://nodejs.org/api/packages.html · módulos ESM/CommonJS e configuração.

## 17.2 — Depuração no servidor

- **Node.js Docs — Debugging guide** · https://nodejs.org/en/learn/getting-started/debugging · inspector e breakpoints.
- **Node.js Docs — Console / diagnostics** · https://nodejs.org/api/console.html · logs úteis.
- **Node.js Docs — Inspector** · https://nodejs.org/api/inspector.html · interface do inspector.

## 18.1 — Estrutura

- **MDN — HTTP request methods e status codes** · https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods · semântica dos métodos e respostas.
- **Express Docs — Routing e middleware** · https://expressjs.com/en/guide/routing.html · rotas e organização dos handlers; ver também https://expressjs.com/en/guide/using-middleware/.

## 18.2 — Boas práticas

- **OpenAPI Specification** · https://spec.openapis.org/oas/latest.html · documentação com OpenAPI/Swagger.
- **RFC 9110 — HTTP Semantics** · https://www.rfc-editor.org/rfc/rfc9110.html · semântica e idempotência de métodos HTTP.
- **Stripe — Idempotent requests** · https://docs.stripe.com/api/idempotent_requests · exemplo de chave idempotente e repetição segura; implementação de referência, não padrão universal.

## 18.3 — Tempo real

- **MDN — WebSocket API** · https://developer.mozilla.org/docs/Web/API/WebSockets_API · WebSocket, salas e difusão.
- **MDN — Server-sent events** · https://developer.mozilla.org/docs/Web/API/Server-sent_events · SSE e reconexão.
- **OWASP — WebSocket Security Cheat Sheet** · https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html · autenticação e controles de segurança.

## 19.1 — ORM e acesso a dados

- **Prisma Docs** · https://www.prisma.io/docs · ORM, mapeamento e SQL gerado.
- **TypeORM Docs** · https://typeorm.io/ · alternativa de ORM.

## 19.2 — Regra de maturidade

- **Prisma Docs — Raw queries / generated SQL** · https://www.prisma.io/docs/orm/prisma-client/queries/raw-database-access/raw-queries · quando o ORM atrapalha.
- **PostgreSQL Docs — Queries (reuso)** · https://www.postgresql.org/docs/current/queries.html · SQL que o ORM abstrai.

## 20.1 — Autenticação

- **RFC 7519 — JSON Web Token** · https://www.rfc-editor.org/rfc/rfc7519.html · formato e claims de JWT.
- **RFC 9700 — OAuth 2.0 Security BCP** · https://www.rfc-editor.org/rfc/rfc9700.html · práticas atuais de segurança OAuth, PKCE e refresh tokens.
- **OpenID Connect Core 1.0** · https://openid.net/specs/openid-connect-core-1_0.html · camada de identidade sobre OAuth 2.0.
- **OWASP — Session Management** · https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html · sessão, cookies e credenciais.

## 20.2 — Segurança básica

- **OWASP — Password Storage** · https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html · hash adaptativo de senha e parâmetros.
- **OWASP — Top 10** · https://owasp.org/www-project-top-ten/ · riscos comuns e OWASP básico.
- **OWASP — SQL Injection Prevention Cheat Sheet** · https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html · prepared statements.
- **MDN — CORS** · https://developer.mozilla.org/docs/Web/HTTP/CORS · CORS.
- **OWASP — CSRF Prevention** · https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html · tokens CSRF e defesas em profundidade.
- **OWASP — Secrets Management** · https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · gestão de credenciais e segredos.

## 20.3 — Segurança aplicada

- **OWASP — API Security Top 10** · https://owasp.org/www-project-api-security/ · riscos comuns em APIs.
- **OWASP — Authorization Cheat Sheet** · https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html · autorização e exposição de dados.
- **NestJS — Rate limiting** · https://docs.nestjs.com/security/rate-limiting · configuração e limites de taxa.
- **Lei nº 13.709/2018 — LGPD** · https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm · princípios e bases legais de tratamento.

## 21.1 — Base conceitual

- **Martin Fowler — Reducing Coupling (IEEE Software)** · https://www.martinfowler.com/ieeeSoftware/coupling.pdf · dependências entre módulos, acoplamento e seus trade-offs.
- **Martin Fowler — Layering Principles** · https://martinfowler.com/bliki/LayeringPrinciples.html · coesão, separação de responsabilidades e acoplamento entre camadas.

## 22.1 — Estrutura de framework

- **NestJS Docs — Modules** · https://docs.nestjs.com/modules · módulos, controllers e providers exportados.
- **NestJS Docs — Providers** · https://docs.nestjs.com/providers · providers e injeção de dependência.
- **NestJS Docs — Testing** · https://docs.nestjs.com/fundamentals/testing · substituição de providers em testes.

## 22.2 — Organização forte

- **NestJS Docs — Guards** · https://docs.nestjs.com/guards · proteção e autorização no contexto da rota.
- **NestJS Docs — Pipes** · https://docs.nestjs.com/pipes · transformação e validação de argumentos.
- **NestJS Docs — Validation** · https://docs.nestjs.com/techniques/validation · validação com DTO.

## 23.1 — Modelos

- **Clean Architecture (Robert C. Martin)** · https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html · Clean Architecture e Hexagonal.
- **Robert C. Martin — The Single Responsibility Principle** · https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html · princípio de responsabilidade única e organização de mudanças.
- **Robert C. Martin — The Open Closed Principle** · https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html · princípio aberto/fechado; complementar ao estudo comparativo dos princípios SOLID.
- **Alistair Cockburn — Hexagonal Architecture** · https://alistair.cockburn.us/hexagonal-architecture · artigo original sobre ports and adapters.

## 23.2 — Base de raciocínio

- **The Algorithm Design Manual (site de apoio)** · https://www.algorist.com/ · estruturas de dados e algoritmos.
- **VisuAlgo** · https://visualgo.net/ · visualização de estruturas e custo.

## 23.3 — Regra dura

- **Martin Fowler — Is Design Dead?** · https://martinfowler.com/articles/designDead.html · quando arquitetura/padrão prejudica a clareza.

## 24.1 — Tipos de teste

- **Jest Docs — Getting started** · https://jestjs.io/docs/getting-started · testes unitários.
- **Jest Docs — Mock Functions** · https://jestjs.io/docs/mock-function-api · mocks e spies.
- **Testing Library — Guiding Principles** · https://testing-library.com/docs/guiding-principles/ · foco em comportamento observável.

## 24.2 — Aplicação

- **Jest Docs — Testing async / mocks** · https://jestjs.io/docs/mock-functions · isolamento de dependências.
- **Supertest (para rotas)** · https://github.com/ladjs/supertest · testes de rotas.
- **NestJS — Testing** · https://docs.nestjs.com/fundamentals/testing · inicialização da aplicação e substituição de dependências.
- **PostgreSQL — Transaction Isolation** · https://www.postgresql.org/docs/current/transaction-iso.html · semântica de transações a exercitar em testes de integração.

## 24.3 — Projeto incremental da fase

- **NestJS Docs (reuso)** · https://docs.nestjs.com/ · API estruturada do projeto.
- **Docker Compose Docs (reuso)** · https://docs.docker.com/compose/ · app + banco + cache.

## 24.4 — Projeto de fase (Trilho B)

- **[[Guia_Projetos_e_Rotacao_de_Tipos|Guia de Projetos]]** · regras de rotação de tipos e escopo do projeto.
- **Jest Docs (reuso)** · https://jestjs.io/docs/getting-started · suíte de testes da entrega.


