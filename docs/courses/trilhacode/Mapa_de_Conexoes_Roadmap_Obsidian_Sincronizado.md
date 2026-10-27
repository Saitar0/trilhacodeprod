---
title: Mapa de Conexões do Roadmap de Desenvolvimento
aliases:
  - Mapa de Conhecimentos
  - Conexões entre Tecnologias
tags:
  - estudos/roadmap
  - conexoes
  - desenvolvimento
status: em-construcao
---

# Mapa de Conexões do Roadmap de Desenvolvimento

> [!abstract] Objetivo
> Esta nota complementa o roadmap principal. Ela organiza as **conexões relevantes e úteis** entre os temas: pré-requisitos, conceitos compartilhados, dependências técnicas, aplicações práticas e evolução de complexidade.
>
> “Todas as conexões” não significa ligar artificialmente cada assunto a todos os outros. O objetivo é mapear as relações que ajudam a compreender, construir, depurar, testar, operar ou evoluir sistemas reais.

## Como ler este mapa

- **A → B**: A fornece base, contexto ou capacidade usada em B.
- **A ↔ B**: os temas se reforçam mutuamente ou precisam ser considerados juntos.
- **Revisita**: um conceito conhecido reaparece em contexto mais avançado.
- **Projeto**: combinação prática de vários temas.

---

# 1. Mapa geral: os grandes eixos

## 1.1 Código e execução

**Computação → sistema operacional/terminal → runtime → linguagem → módulos/dependências → aplicação**

Conexões:
- Sistema de arquivos ↔ módulos, imports e organização do código.
- Terminal ↔ instalação de ferramentas, scripts, Git, testes, build e deploy.
- Processos ↔ servidores web, workers, jobs e containers.
- Variáveis de ambiente ↔ configuração local, segredos, CI/CD e ambientes de produção.
- Logs ↔ depuração local, investigação de incidentes e observabilidade.
- Runtime ↔ event loop, processamento assíncrono, streams e comportamento de APIs.
- Documentação técnica ↔ escolha de ferramentas, leitura de erros e decisões arquiteturais.

## 1.2 Web e comunicação

**HTML/CSS/JavaScript → navegador/DOM → HTTP → API → backend → banco/cache/filas → infraestrutura**

Conexões:
- HTML semântico ↔ acessibilidade ↔ testes de interface.
- CSS responsivo ↔ experiência de usuário ↔ testes em diferentes tamanhos de tela.
- Eventos do navegador ↔ estado de interface ↔ formulários ↔ validação.
- JSON ↔ contratos de API ↔ TypeScript ↔ DTOs ↔ validação de entrada.
- HTTP ↔ métodos/status/headers ↔ autenticação ↔ CORS ↔ cache ↔ depuração de rede.
- Métodos/códigos HTTP ↔ semântica REST ↔ contratos de API ↔ documentação OpenAPI/Swagger.
- Cookies/sessões/tokens ↔ autenticação ↔ CORS ↔ armazenamento, renovação e expiração de credenciais.
- WebSocket/SSE (18.3) ↔ comunicação em tempo real ↔ reconexão, ordem e duplicidade de mensagens ↔ atualização da interface e streaming de IA.
- DNS ↔ domínio ↔ TLS/HTTPS ↔ proxy/entrada de tráfego ↔ deploy.
- Cliente-servidor ↔ latência ↔ falhas de rede ↔ retry ↔ timeout ↔ circuit breaker.
- Frontend ↔ backend: estados de loading, erro, vazio, sucesso, paginação e autenticação precisam concordar com o contrato da API.

## 1.3 Dados e consistência

**Domínio do problema → modelagem → SQL → transações/integridade → migrations → ORM → cache/índices → observabilidade**

Conexões:
- Entidades/atributos ↔ objetos e tipos da aplicação ↔ tabelas e colunas.
- Cardinalidade ↔ relacionamentos SQL ↔ JOINs ↔ modelagem de entidades no ORM.
- Chaves e constraints ↔ integridade referencial ↔ regras de negócio.
- Normalização ↔ redundância ↔ consistência ↔ decisões de leitura e escrita.
- SQL ↔ ORM: o ORM abstrai parte do acesso, mas não elimina a necessidade de entender consultas, índices e transações.
- Migrations ↔ Git ↔ revisão de código ↔ deploy ↔ compatibilidade entre versões.
- Índices ↔ EXPLAIN ↔ latência ↔ métricas ↔ decisão baseada em evidências.
- Transações ↔ isolamento e locks (12.2) ↔ concorrência ↔ idempotência (18.2) ↔ filas ↔ consistência em sistemas distribuídos.
- Busca textual no PostgreSQL (tsvector, GIN e pg_trgm, 12.1) ↔ índices ↔ EXPLAIN ↔ quando um motor de busca dedicado se justifica.
- Cache ↔ TTL ↔ invalidação ↔ dados obsoletos ↔ consistência.
- Backup/restore ↔ integridade do banco ↔ recuperação de falhas ↔ volumes e operação.
- ORM (19.1 e 19.2) ↔ SQL gerado; esses submódulos ficam fisicamente na Fase 5 (Módulo 19, após 18.1), enquanto a Fase 3 usa SQL puro.
- PostgreSQL ↔ Redis ↔ MongoDB: persistência relacional, acesso rápido/temporário e modelo documental respondem a necessidades diferentes; não são substitutos universais.

## 1.4 Qualidade e manutenção

**Requisitos → design → implementação → testes → revisão → CI → deploy → observabilidade → aprendizado**

Conexões:
- Funções pequenas ↔ coesão ↔ testes unitários ↔ reutilização.
- Separação de responsabilidades ↔ controllers/services/repositories ↔ Clean Architecture ↔ facilidade de testar.
- Interfaces/contratos ↔ mocks ↔ testes de integração ↔ evolução independente de componentes.
- Git diff ↔ code review ↔ qualidade ↔ rastreabilidade de decisões.
- Lint/build/testes ↔ quality gates ↔ pipeline de CI.
- Logs/métricas/traces ↔ diagnóstico ↔ causa raiz ↔ postmortem ↔ ações preventivas.
- ADRs ↔ decisões arquiteturais ↔ trade-offs ↔ manutenção futura.
- Débito técnico ↔ velocidade de mudança ↔ risco de regressão ↔ custo operacional.

## 1.5 Segurança

**Entrada não confiável → validação → autenticação → autorização → acesso a dados → logs/monitoramento**

Conexões:
- HTML/forms ↔ validação no cliente; backend continua responsável por validar a entrada.
- XSS, CSRF e armazenamento de token (27.4) ↔ autenticação (20.1) ↔ CORS e OWASP (20.2).
- JSON/API ↔ validação de schema ↔ DTOs/pipes ↔ tratamento de erros.
- Hash de senha ↔ armazenamento seguro de credenciais; hash não é criptografia reversível.
- Sessão/JWT/OAuth2 ↔ identidade ↔ autorização ↔ expiração/renovação ↔ armazenamento de tokens.
- CORS ↔ política de navegador; não substitui autenticação nem autorização.
- Variáveis de ambiente ↔ gestão de segredos ↔ CI/CD ↔ cloud IAM.
- Permissões Linux ↔ usuários de processo ↔ arquivos/volumes ↔ containers.
- OWASP ↔ APIs ↔ banco de dados ↔ dependências ↔ configuração de deploy.
- Rate limiting ↔ proteção contra abuso ↔ autorização ↔ métricas e observabilidade.
- `.gitignore`/segredos fora do Git ↔ variáveis de ambiente ↔ gestão de segredos ↔ CI/CD/IAM.
- Prompt injection ↔ agentes/ferramentas ↔ permissões ↔ dados recuperados ↔ prevenção de vazamento.
- Logs ↔ auditoria, mas também podem vazar tokens, senhas e dados pessoais se forem mal projetados.

## 1.6 Infraestrutura e operação

**Código → build → artefato/imagem → ambiente → rede/identidade → deploy → telemetria → operação**

Conexões:
- Terminal/Linux ↔ processos/serviços/logs ↔ diagnóstico em servidor.
- Dockerfile ↔ dependências/runtime ↔ imagem reproduzível.
- Volumes ↔ persistência de dados ↔ backups ↔ recuperação.
- Redes de containers ↔ DNS interno ↔ portas ↔ conectividade entre app, banco e cache.
- GitHub Actions ↔ build/test/lint ↔ registry/artefato ↔ deploy.
- Staging ↔ validação pré-produção ↔ rollback.
- Terraform ↔ providers/resources/state/modules/variables ↔ ambientes repetíveis.
- IAM ↔ menor privilégio ↔ acesso a serviços AWS.
- RDS/S3/EC2/VPC ↔ rede, identidade, custos, disponibilidade e segurança.
- ECS/EKS/Kubernetes ↔ containers, rede, configuração, health checks, escala e observabilidade.
- OpenTelemetry ↔ traces/metrics/logs ↔ Prometheus/Grafana/New Relic ↔ investigação de incidentes.
- SLI/SLO/SLA ↔ métricas operacionais ↔ priorização de confiabilidade ↔ decisões de produto.
- Domínio/DNS ↔ TLS/HTTPS ↔ reverse proxy/load balancer ↔ entrada segura de tráfego.
- Alertas de orçamento ↔ custo da cloud ↔ destruição dos recursos de laboratório com Terraform (`destroy`).
- CDN (repertório) ↔ cache de borda ↔ latência e distribuição de conteúdo.

---

# 2. Conexões por fase

## Fase 1 — Base técnica e alfabetização de desenvolvimento

### Computação, web e execução
- Programa ↔ processo: código é executado por um runtime/sistema e passa a consumir recursos.
- Frontend ↔ backend ↔ banco: responsabilidades distintas que formam uma aplicação.
- Cliente-servidor ↔ requisição/resposta ↔ HTTP ↔ APIs.
- Navegador ↔ DNS ↔ endereço do servidor ↔ conexão web.
- Aplicação local ↔ aplicação web: diferenças de ambiente, rede, acesso e distribuição.

### Terminal, sistema e SSH
- Pastas/caminhos ↔ organização de projeto ↔ imports e scripts.
- Permissões/usuários ↔ segurança de arquivos ↔ execução de serviços.
- Processos/serviços ↔ servidores web, workers e containers estudados mais tarde.
- `grep`/`tail` ↔ busca e acompanhamento de logs ↔ troubleshooting em produção.
- SSH/chaves ↔ acesso remoto ↔ servidores cloud ↔ deploy e administração.
- Chaves SSH ↔ autenticação de Git remoto; são distintas de tokens de aplicação.

### Git e GitHub
- `status`/`diff` ↔ compreensão das mudanças ↔ code review.
- `commit`/`log` ↔ rastreabilidade ↔ diagnóstico de regressões.
- `branch`/`merge`/`rebase`/conflitos ↔ colaboração ↔ integração de código.
- Pull request ↔ revisão ↔ testes automatizados ↔ quality gates.
- README ↔ documentação de execução ↔ onboarding ↔ reprodutibilidade.
- Git ↔ migrations, Dockerfile, Terraform, testes e configuração versionada.
- Dotfiles/setup versionados ↔ ambientes consistentes ↔ automação futura.
- `WSL` ↔ ambiente Linux no Windows ↔ terminal ↔ containers e scripts reproduzíveis.
- Pipes (`|`) ↔ composição de comandos ↔ `grep`/`tail` ↔ leitura de logs.
- `.gitignore` ↔ segredos fora do repositório ↔ variáveis de ambiente ↔ CI/CD/IAM.
- Commits, README e issues em inglês ↔ documentação técnica e portfólio profissional.

**Projeto integrador:** setup documentado e versionado; em 3.5, escolher a ideia do Trilho A (troca permitida uma vez, até o fim da Fase 4) (gestor de tarefas/projetos, loja virtual ou base de conhecimento colaborativa), que será evoluída até o projeto final. O repositório de estudos continua sendo o espaço de documentação e aprendizado.

## Fase 2 — Base da web: HTML e CSS

### HTML, CSS e acessibilidade
- HTML semântico ↔ significado do conteúdo ↔ leitores de tela ↔ navegação acessível.
- Labels ↔ formulários ↔ testes de interação ↔ qualidade da experiência.
- `alt` ↔ imagens informativas ↔ acessibilidade.
- Hierarquia de títulos ↔ estrutura do documento ↔ navegação e manutenção.
- Box model ↔ espaçamento ↔ composição de layouts.
- Flexbox ↔ alinhamento em uma dimensão; Grid ↔ organização em duas dimensões; podem ser combinados.
- Medidas relativas/media queries ↔ responsividade ↔ mobile first.
- CSS organizado ↔ componentes reutilizáveis ↔ manutenção futura no React.
- Tailwind CSS (repertório) ↔ abordagem utility-first ↔ organização visual e componentes React.

## Fase 3 — Base da web: JavaScript, TypeScript e Node.js

### JavaScript e lógica
- Variáveis/tipos/operadores ↔ condicionais/laços ↔ algoritmos.
- Funções/parâmetros/retorno ↔ composição ↔ reutilização ↔ testes unitários.
- Arrays ↔ listas de dados ↔ `map`/`filter`/transformações ↔ renderização de listas.
- Objetos ↔ entidades ↔ JSON ↔ contratos de API.
- Escopo ↔ closures ↔ hooks e callbacks estudados depois.
- DOM/eventos ↔ estado de interface ↔ formulários e validação.
- Módulos ↔ separação de arquivos ↔ organização em componentes e camadas.
- Promises/async-await ↔ `fetch` ↔ latência de rede ↔ estados de loading/erro.
- Tratamento de erros ↔ UX ↔ logs ↔ diagnóstico.
- DevTools/Network ↔ HTTP ↔ API ↔ depuração de frontend/backend.

- Stack trace ↔ leitura de erros ↔ depuração no Node e em testes.
- O(n) ↔ manipulação de arrays ↔ custo de processamento ↔ performance.
- Pilha/fila ↔ estruturas de dados ↔ execução de tarefas e mensageria.

### TypeScript
- Tipos/interfaces ↔ contratos de dados ↔ JSON ↔ frontend/backend.
- Unions/narrowing ↔ estados possíveis ↔ tratamento explícito de erro/loading/sucesso.
- Generics ↔ funções/componentes reutilizáveis ↔ respostas paginadas e estruturas genéricas.
- `tsconfig`/compilação ↔ build ↔ CI.
- Migração JS → TS ↔ redução gradual de risco ↔ legado.
- Tipos estáticos não substituem validação de dados recebidos em runtime.

**Projeto integrador (8.5):** interface estática da ideia do Trilho A escolhida em 3.5, acessível, responsiva, organizada em módulos, com interação, tipagem e hospedagem/deploy estático. O projeto de fase 8.6 é uma entrega separada do Trilho B (escopo mínimo) e participa da rotação de tipos.

> [!success] Alinhamento resolvido
> O 8.5 agora entrega a tela principal da ideia escolhida em 3.5; a página de currículo do 4.1 é só um extra de portfólio. A Fase 3 ganhou o submódulo 6.4 (Node.js e npm) e o submódulo 8.4 foi aposentado, com o conteúdo incorporado ao 27.3 e ao 18.1.

## Fase 4 — Dados e bancos

- Entidades ↔ objetos do domínio ↔ modelos da aplicação.
- Atributos ↔ campos de objetos ↔ colunas.
- Cardinalidade ↔ chaves estrangeiras ↔ JOINs ↔ relacionamentos ORM.
- Normalização ↔ duplicação ↔ consistência ↔ desenho de escrita/leitura.
- `SELECT`/`WHERE` ↔ filtros de UI ↔ parâmetros de API ↔ paginação.
- `ORDER BY`/`LIMIT` ↔ paginação estável ↔ índices e performance.
- `GROUP BY`/`HAVING` ↔ relatórios ↔ métricas de negócio.
- Subqueries ↔ consultas compostas ↔ alternativas de JOIN; comparar plano e legibilidade.
- Constraints ↔ invariantes de negócio ↔ prevenção de dados inválidos.
- Transações ↔ atomicidade ↔ falhas parciais ↔ consistência.
- Migrations ↔ histórico Git ↔ deploy compatível ↔ evolução de schema.
- EXPLAIN ↔ índices ↔ cardinalidade ↔ gargalos reais.
- ORM ↔ produtividade ↔ SQL gerado ↔ risco de consultas ineficientes.
- Prisma/TypeORM ↔ TypeScript ↔ modelos e contratos da aplicação.
- Docker/Compose (Módulo 10, antecipado para esta fase) ↔ bancos reproduzíveis ↔ mesmo ambiente em qualquer máquina.
- MySQL/PostgreSQL/SQL Server/Oracle ↔ conceitos relacionais compartilhados e diferenças específicas de dialeto/recursos.
- MongoDB ↔ documentos ↔ agregações ↔ modelagem orientada aos padrões de acesso.
- Redis ↔ cache ↔ TTL ↔ invalidação ↔ redução de latência.
- Redis/filas ↔ coordenação e processamento; não confundir cache com fonte de verdade.
- Elasticsearch ↔ busca textual e indexação; sincronização com o banco primário exige desenho explícito.
- DynamoDB/Firestore ↔ modelos gerenciados e padrões de acesso diferentes do SQL tradicional.

**Projeto integrador (16.2):** persistir o projeto principal em PostgreSQL, medir uma consulta e adicionar cache Redis; usar MongoDB quando houver um caso documental justificado. O ORM (19.1/19.2) fica para a Fase 5 (Módulo 19), após 18.1. Os bancos sobem em containers (Módulo 10, antecipado para esta fase). O projeto 16.3 é o Trilho B: modelo relacional, migrations, relatórios e consulta medida com EXPLAIN.

## Fase 5 — Backend e arquitetura

### Node e APIs
- Runtime ↔ event loop ↔ operações I/O ↔ concorrência e latência.
- Promises/async-await ↔ acesso ao banco/API ↔ erros assíncronos.
- Streams ↔ processamento de grandes volumes ↔ uso de memória.
- Jobs ↔ tarefas demoradas ↔ filas e workers.
- Rotas ↔ controllers ↔ serviços ↔ persistência: separar transporte, regra de negócio e acesso a dados quando isso trouxer clareza.
- Middlewares ↔ autenticação, logging, correlação, tratamento de erros.
- Validação ↔ DTOs ↔ contratos ↔ proteção do domínio.
- Versionamento/paginação/respostas padronizadas ↔ compatibilidade com frontend e clientes externos.
- Inspector/stack traces/logs ↔ depuração do servidor ↔ observabilidade.
- Métodos/status HTTP ↔ semântica REST ↔ contratos de API ↔ OpenAPI/Swagger.
- WebSocket/SSE ↔ API ↔ autenticação/autorização da conexão ↔ streaming de respostas.
- Cookies/sessões/tokens ↔ autenticação ↔ expiração/renovação ↔ armazenamento seguro.
- Rate limiting ↔ rotas sensíveis ↔ proteção contra abuso ↔ métricas e logs.
- Tipos de teste (24.1) estudados logo após 18.1 ↔ testes de autorização antes do Módulo 20.
- ORM (19.1 e 19.2, Módulo 19 desta fase) estudado após 18.1 ↔ SQL gerado ↔ migrations ↔ testes com banco.

### Segurança e arquitetura
- Sessão/JWT/OAuth2 ↔ autenticação; autorização define o que cada identidade pode fazer.
- Hash de senha ↔ armazenamento de credenciais ↔ fluxo de cadastro/login.
- CORS ↔ navegador ↔ frontend/backend; não protege API contra clientes não-browser.
- Segredos/env ↔ deploy ↔ CI/CD ↔ IAM.
- OWASP ↔ validação ↔ autorização ↔ queries ↔ dependências ↔ configuração.
- Coesão ↔ responsabilidade única ↔ módulos ↔ testes.
- Acoplamento ↔ dependências ↔ facilidade de trocar banco, framework ou serviço.
- NestJS/módulos/controllers/providers/DI ↔ organização modular ↔ testabilidade.
- DTOs/pipes/guards ↔ validação, autenticação e autorização.
- SOLID ↔ design patterns ↔ decisões locais; não são objetivos independentes de um problema real.
- Clean Architecture/Hexagonal ↔ regras de negócio protegidas de detalhes externos ↔ ports/adapters ↔ testes.
- Estruturas de dados/algoritmos ↔ custo de execução ↔ decisões de performance.
- Testes unitários ↔ integração ↔ mocks ↔ cobertura: cada tipo responde a riscos diferentes.
- Testes com banco ↔ transações/migrations ↔ isolamento e previsibilidade.

**Projeto integrador (24.3):** API autenticada com PostgreSQL, cache e testes de rotas/serviços. A execução com Docker Compose usa o Módulo 10, estudado na Fase 4. Ordem sugerida: 17 → 18 → 24.1 → Módulo 19 (19.1/19.2) → 20 → 21 → 22 → 23 → 24.2 → 24.3 → 24.4. O projeto 24.4 é o Trilho B.

## Fase 6 — Frontend moderno

- HTML/CSS/JS ↔ JSX/componentes React: fundamentos continuam válidos, mas a composição passa a ser declarativa.
- Componentes ↔ funções ↔ props ↔ reutilização e contratos.
- State ↔ eventos ↔ renderização condicional ↔ formulários.
- Listas ↔ arrays ↔ keys estáveis ↔ atualização previsível da interface.
- `useEffect` ↔ efeitos externos; não é substituto genérico para qualquer cálculo.
- `useRef` ↔ valores persistentes sem renderização ↔ referências DOM.
- `useMemo`/`useCallback` ↔ identidade de valores/funções ↔ otimização medida, não automática.
- Context ↔ estado compartilhado ↔ risco de acoplamento.
- Hooks customizados ↔ composição de lógica ↔ testes e reutilização.
- REST/HTTP ↔ JSON ↔ TypeScript ↔ contratos de resposta.
- Token/headers ↔ autenticação ↔ renovação/expiração ↔ tratamento de falhas.
- Paginação ↔ API ↔ estado da interface ↔ ordenação/filtros.
- Loading/retry/erro/vazio/sucesso ↔ estados explícitos ↔ experiência de usuário.
- Zustand ↔ estado global de UI; TanStack Query ↔ estado remoto/cache de servidor: responsabilidades diferentes.
- Cache/invalidação ↔ mutações ↔ consistência da interface com o backend.
- Vitest/Jest ↔ testes de lógica; Testing Library ↔ comportamento percebido pelo usuário; Playwright ↔ fluxos integrados.
- Mocks de API ↔ isolamento; testes reais de integração continuam necessários.
- Lazy loading/code splitting ↔ custo inicial ↔ rede ↔ métricas de performance.
- Virtualização ↔ listas grandes ↔ custo de renderização.
- Next.js ↔ React + renderização/rotas no servidor ↔ trade-offs de SSR/SSG/deploy.
- Vue/Angular ↔ comparação de modelos de componentes, reatividade, DI e organização.
- React Native ↔ reutilização de conceitos React, mas com plataforma e componentes nativos diferentes.

**Projeto integrador (31.4):** frontend React tipado do projeto principal, conectado à API real da Fase 5, com os cinco estados de interface, testes de comportamento e medição de performance. A API real é a construída na Fase 5. O projeto 31.5 é o Trilho B.

## Fase 7 — Infraestrutura, deploy e cloud

- Dockerfile ↔ runtime/dependências ↔ build reproduzível.
- Imagem ↔ container ↔ processo ↔ logs ↔ sinais de encerramento.
- Volumes ↔ persistência ↔ backup/restore.
- Redes ↔ DNS/portas ↔ conectividade entre serviços.
- Compose (Módulo 10, estudado na Fase 4) ↔ app + banco + cache ↔ ambiente local próximo da composição real, agora levado ao pipeline.
- GitHub Actions ↔ lint/build/test ↔ artefatos ↔ deploy.
- Quality gates ↔ feedback rápido ↔ prevenção de regressões.
- Staging ↔ validação ↔ rollout ↔ rollback.
- Filas ↔ retry ↔ DLQ ↔ idempotência ↔ falhas transitórias e mensagens duplicadas.
- IAM ↔ menor privilégio ↔ acesso a EC2, S3, RDS, filas e serviços.
- VPC ↔ sub-redes/rotas/firewalls ↔ exposição de serviços.
- RDS ↔ banco gerenciado ↔ backups, conectividade, custos e segurança.
- S3 ↔ objetos/arquivos ↔ permissões ↔ políticas de retenção.
- Lambda/API Gateway ↔ execução sob demanda ↔ limites, latência e modelo operacional.
- SQS/SNS/EventBridge ↔ padrões distintos de fila, publicação/assinatura e eventos.
- ElastiCache ↔ Redis gerenciado ↔ cache e latência.
- Terraform ↔ recursos declarativos ↔ state ↔ módulos ↔ revisão de mudanças.
- Variáveis e workspaces do Terraform ↔ múltiplos ambientes; Terragrunt (repertório) ↔ organização de muitos ambientes/stacks.
## Fase 8 — Orquestração, observabilidade e operação

- ECS/EKS ↔ containers ↔ deploy, rede, health checks, escala e operação.
- Kubernetes pods/deployments/services ↔ ciclo de vida e descoberta de serviços.
- GCP Cloud Run/Pub/Sub/GKE ↔ comparação de conceitos cloud, sem presumir equivalência exata entre serviços.
- Logs estruturados ↔ métricas ↔ traces ↔ correlação de requisições.
- OpenTelemetry ↔ instrumentação ↔ backend de observabilidade.
- Prometheus/Grafana/New Relic ↔ coleta, visualização e análise operacional.
- SLA/SLO ↔ indicadores ↔ alertas ↔ decisões de confiabilidade.
- Runbooks ↔ resposta operacional; postmortems ↔ aprendizagem; ADRs ↔ registro das decisões.

**Projeto integrador (39.2):** pipeline e deploy em AWS via Terraform, dashboard de métricas/traces e incidente simulado com análise de causa raiz. Inclui alerta de orçamento e destruição de recursos ao fim do laboratório; 39.3 é o Trilho B.

## Fase 9 — Escala, mensageria e pluralidade de mercado

### Mensageria e sistemas distribuídos
- Comunicação síncrona ↔ acoplamento temporal ↔ latência e disponibilidade.
- Comunicação assíncrona ↔ filas/eventos ↔ consistência eventual e processamento posterior.
- RabbitMQ ↔ filas e roteamento de mensagens.
- Kafka ↔ log distribuído, partições, produtores/consumidores e grupos.
- SQS ↔ fila gerenciada; SNS ↔ pub/sub; Pub/Sub ↔ mensageria gerenciada. Comparar sem presumir semântica idêntica.
- Producer/consumer ↔ ack ↔ retry ↔ duplicidade ↔ idempotência.
- DLQ ↔ mensagens que falharam repetidamente ↔ inspeção e reprocessamento controlado.
- Outbox ↔ transação no banco + publicação confiável de evento.
- Saga ↔ coordenação de etapas distribuídas ↔ compensações.
- Circuit breaker ↔ falhas em dependências ↔ proteção contra cascatas.
- Resiliência ↔ timeouts ↔ retries com limites/backoff ↔ observabilidade.
- Partições/grupos ↔ paralelismo ↔ ordenação ↔ capacidade de processamento.
- Alta volumetria ↔ índices/cache ↔ filas ↔ backpressure ↔ métricas de saturação.
- Microsserviços ↔ deploy independente ↔ fronteiras de domínio ↔ custo operacional; não são upgrade automático de monólito.
- RabbitMQ: exchanges/filas ↔ bindings/roteamento ↔ ack/nack ↔ prefetch ↔ DLQ.
- Kafka (repertório, com experimento curto): producers/consumers ↔ partições/grupos ↔ offsets/retenção ↔ reprocessamento; o RabbitMQ é o broker aprofundado.
- Uma stack de construção (Python, PHP, C# ou Java) ↔ prática aprofundada; as demais ↔ leitura guiada e quadro de equivalências com Node. A stack construída entrega uma API pequena, depois de uma etapa de fundamentos da linguagem.

### Comparação de stacks
- Python/Django/DRF ↔ APIs, ORM, migrations, validação e testes.
- Celery ↔ workers/jobs ↔ broker ↔ retries ↔ monitoramento de tarefas.
- FastAPI/Flask ↔ alternativas de estrutura e escopo no ecossistema Python.
- PHP/Laravel/Eloquent ↔ rotas, middleware, ORM, migrations, filas e autenticação.
- C#/ASP.NET Core/EF Core/Dapper/xUnit ↔ APIs, DI, persistência e testes.
- SQL Server ↔ ecossistema .NET em muitos ambientes; conceitos SQL continuam transferíveis.
- Java/Spring/DI/JPA ↔ serviços, persistência, testes e integração com Kafka.
- Strangler pattern ↔ modernização gradual ↔ APIs/contratos ↔ coexistência entre legado e novo.
- Débito técnico ↔ custo de mudança ↔ estratégia de migração ↔ risco operacional.
- Comparar stacks por modelo de execução, DI, ORM, testes, observabilidade, deploy e ecossistema — não só por sintaxe.

**Projeto integrador (46.2):** produtor/consumidor, retry, DLQ, idempotência e documentação das decisões; implementar o serviço extra na stack escolhida e compará-la com Node. As demais stacks são leitura guiada. O projeto 46.3 segue as regras do Trilho B, podendo ser livre quando a cobertura T1–T5 já estiver completa.

## Fase 10 — IA aplicada, fechamento técnico e posicionamento

### IA e aplicação
- Assistentes/agentes de código ↔ Git diff ↔ testes ↔ code review ↔ responsabilidade por código gerado.
- Prompting ↔ especificação de requisitos ↔ exemplos ↔ critérios de aceitação ↔ avaliação.
- Provedores de modelos ↔ APIs ↔ autenticação ↔ limites ↔ custo ↔ latência ↔ streaming.
- Streaming ↔ UX ↔ cancelamento ↔ tratamento de erro ↔ telemetria.
- Embeddings ↔ representação vetorial ↔ busca semântica ↔ recuperação de contexto.
- Chunking ↔ tamanho de contexto ↔ qualidade de recuperação ↔ custo/latência.
- Banco vetorial ↔ metadados/permissões ↔ filtragem de resultados ↔ governança.
- RAG ↔ ingestão de documentos ↔ chunking ↔ embeddings ↔ retrieval ↔ geração ↔ avaliação.
- Avaliação ↔ conjunto de casos ↔ relevância/factualidade ↔ regressão de prompts/modelos.
- Function calling ↔ contratos tipados ↔ validação ↔ autorização ↔ execução controlada de ações.
- LangChain/LangGraph/Semantic Kernel/CrewAI ↔ abstrações/orquestração; selecionar conforme necessidade, não apenas por popularidade.
- MCP ↔ conexão padronizada com ferramentas/contextos ↔ permissões ↔ confiança na origem dos dados.
- Prompt injection ↔ conteúdo não confiável ↔ ferramentas ↔ isolamento de privilégios ↔ validação de ações.
- Guardrails ↔ validação de entrada/saída ↔ autorização ↔ monitoramento; não garantem segurança sozinhos.
- Governança de dados ↔ retenção ↔ privacidade ↔ logs ↔ provedores externos.
- Upload/ingestão de documentos ↔ chunking ↔ embeddings ↔ busca semântica ↔ RAG.
- SSE no navegador ↔ streaming ↔ cancelamento e estados de interface ↔ custo/latência medidos.

### Projeto final
- O projeto final (52.1) expande o Trilho A; seus critérios de aceitação são checklists do projeto, não tópicos de estudo. O 52.2 entrega T6 (IA aplicada) obrigatoriamente. Tipos T1–T5 ainda pendentes devem ser recuperados segundo as regras do guia; a conclusão exige os seis tipos.
- React ↔ estados de interface ↔ streaming ↔ acessibilidade.
- Backend ↔ autenticação/autorização ↔ contratos ↔ chamadas ao provedor.
- Banco relacional ↔ usuários, permissões, histórico e metadados.
- Banco vetorial ↔ embeddings/documentos, se houver necessidade real de RAG.
- Cache ↔ resultados reutilizáveis ↔ TTL ↔ cuidado com dados por usuário.
- Fila ↔ ingestão/embeddings/processamentos longos ↔ retry/DLQ.
- Docker ↔ execução reproduzível ↔ CI/CD ↔ testes.
- AWS/Terraform ↔ identidade, rede, segredos, custos e deploy.
- Observabilidade ↔ latência/custo por chamada ↔ erros do provedor ↔ traces ponta a ponta.
- README ↔ setup ↔ decisões arquiteturais ↔ diagrama ↔ demonstração do projeto.
- Projeto acumulado ↔ evidência de evolução ↔ portfólio/GitHub ↔ entrevistas.
- System design ↔ requisitos ↔ trade-offs ↔ escalabilidade ↔ segurança ↔ custo ↔ confiabilidade.

---

# 3. Conexões transversais que voltam em várias fases

## 3.1 Contratos de dados
HTML forms → objetos JavaScript → JSON → TypeScript interfaces/types → DTOs → validação → banco/ORM → eventos de fila → schemas de IA/function calling.

**Pergunta recorrente:** quem produz o dado, quem o consome, como é validado e como mudanças compatíveis são feitas?

## 3.2 Tratamento de erros
JavaScript try/catch → fetch/API → erros HTTP → middleware backend → transações → retry de fila → DLQ → logs/traces → postmortem.

**Pergunta recorrente:** o erro é recuperável? Deve ser mostrado ao usuário, repetido, registrado ou encaminhado para intervenção?

## 3.3 Identidade e permissões
Permissões do sistema operacional → chaves SSH/Git → login da aplicação → sessão/JWT/OAuth2 → autorização por recurso → IAM cloud → credenciais de serviços e agentes.

**Pergunta recorrente:** quem está fazendo a ação, com qual permissão e sobre qual recurso?

## 3.4 Estado e consistência
Estado React → cache de dados remotos → estado do banco → cache Redis → eventos/filas → projeções de leitura/search → estado de execução de agente.

**Pergunta recorrente:** qual é a fonte de verdade, quando os dados podem ficar desatualizados e como reconciliar divergências?

## 3.5 Performance
Complexidade de algoritmo → renderização React → rede/HTTP → consultas SQL/índices → cache → filas/backpressure → infraestrutura → latência de IA.

**Pergunta recorrente:** onde está o gargalo medido e qual é o custo de melhorá-lo?

## 3.6 Reprodutibilidade
README/setup → versões de runtime → lockfiles → Git → testes → Docker → CI → Terraform → ambientes → runbooks.

**Pergunta recorrente:** outra pessoa ou máquina consegue reproduzir, validar e operar o sistema?

## 3.7 Evolução segura
Git/migrations → contratos de API → testes de regressão → deploy gradual → compatibilidade entre versões → rollback → observabilidade → postmortem.

**Pergunta recorrente:** como mudar sem quebrar usuários, dados ou serviços dependentes?

## 3.8 Observabilidade e depuração
DevTools → logs de aplicação → logs estruturados → correlação de requisições → métricas/traces → alertas → causa raiz → ADR/runbook.

**Pergunta recorrente:** como provar onde o problema ocorre em vez de apenas tentar soluções aleatórias?

---

# 4. Projeto acumulado: como as fases se conectam

## 4.1 Trilhos A e B

- **Trilho A — projeto principal acumulado:** escolher uma ideia no submódulo 3.5 e evoluí-la até o projeto final 52.1. Opções do guia: gestor de tarefas/projetos em equipe, loja virtual ou base de conhecimento colaborativa.
- **Trilho B — projeto de fase:** escolher uma ideia entre as três oferecidas em cada fase, conforme a rotação do guia. Os submódulos são 8.6, 16.3, 24.4, 31.5, 39.3, 46.3 e 52.2; a Fase 10 garante o tipo T6. Cada projeto é uma fatia mínima e autocontida (regras 9 e 10 do guia).
- **Cobertura de tipos:** transacional, SaaS multiempresa, tempo real/colaboração, conteúdo/feed/busca, dados/processamento assíncrono e IA aplicada. O curso só fecha quando os seis tipos tiverem sido concluídos.
- **Regra de execução:** o projeto principal acumula capacidades; o Trilho B cobre problemas técnicos variados. Não recomeçar a aplicação principal do zero e não adicionar tecnologia só para marcar um item.
- Detalhes, ideias, disponibilidade por fase e tabela de cobertura: [[Guia_Projetos_e_Rotacao_de_Tipos]].

## 4.2 Evolução por fase

| Fase | Trilho A — projeto principal acumulado | Submódulo A | Trilho B — projeto de fase | Submódulo B |
|---|---|---|---|---|
| 1 | Setup/dotfiles e repositório de estudos; escolha da ideia principal | 3.5 | Ainda não há projeto de rotação | — |
| 2 | Sem projeto dedicado; o HTML/CSS é aplicado no 8.5 (Fase 3) | — | Ainda não há projeto de rotação | — |
| 3 | Interface estática da ideia escolhida em 3.5 (HTML/CSS/JS/TS) com deploy estático | 8.5 | Uma ideia do tipo pendente, na versão sem framework | 8.6 |
| 4 | Persistência em PostgreSQL, consulta medida, cache Redis e caso documental justificado | 16.2 | Modelagem relacional, migrations, relatórios e EXPLAIN | 16.3 |
| 5 | API autenticada, PostgreSQL, cache, testes e Compose | 24.3 | API da ideia escolhida, autenticada, persistida e testada | 24.4 |
| 6 | Frontend React tipado sobre a API real, cinco estados, testes e medição de performance | 31.4 | Interface React sobre a API real, cinco estados e testes | 31.5 |
| 7 | Deploy automatizado na AWS com Terraform e pipeline | 36.2 | Projeto de infraestrutura fica na Fase 8 | — |
| 8 | Tracing e métricas em dashboard + postmortem simulado | 39.2 | Ideia escolhida publicada com pipeline e observabilidade | 39.3 |
| 9 | Produtor/consumidor com retry e DLQ; serviço extra na stack escolhida | 46.2 | Projeto rotativo; pode ser livre se T1–T5 cobertos | 46.3 |
| 10 | Aplicação full stack com IA, testes, CI/CD, deploy, observabilidade e documentação | 52.1 | T6 — IA aplicada, obrigatório; recuperar tipos pendentes | 52.2 |

> [!important] Regra do projeto acumulado
> Não adicione uma tecnologia apenas para marcar um tópico. Adicione-a quando o projeto demonstrar um problema que ela resolve, ou construa um experimento isolado para aprender o conceito sem complicar o sistema principal.

---

# 5. Perguntas para descobrir conexões novas durante o estudo

Ao terminar cada tópico, responda:

- [ ] De quais conceitos anteriores ele depende?
- [ ] Que problema real ele resolve?
- [ ] Que outros componentes precisam interagir com ele?
- [ ] Que dados entram e saem? Qual é o contrato?
- [ ] O que acontece quando falha, fica lento ou recebe dados inválidos?
- [ ] Como testar seu comportamento isoladamente?
- [ ] Como testar a integração com os outros componentes?
- [ ] Como observar seu comportamento em execução?
- [ ] Que risco de segurança ele introduz?
- [ ] Que trade-off existe entre simplicidade, custo, desempenho e confiabilidade?
- [ ] Em quais fases futuras esse conhecimento será reutilizado?
- [ ] Qual exemplo concreto do projeto acumulado demonstra essa conexão?

---

# 6. Como manter este mapa útil no Obsidian

Crie notas próprias para os grandes hubs e conecte-as com links internos:

- [[HTTP e APIs]]
- [[Contratos e validação de dados]]
- [[Modelagem de dados e SQL]]
- [[Autenticação e autorização]]
- [[Testes e qualidade]]
- [[Tratamento de erros]]
- [[Performance e cache]]
- [[Filas e processamento assíncrono]]
- [[Docker e ambientes reproduzíveis]]
- [[CI-CD e deploy]]
- [[Infraestrutura como código]]
- [[Observabilidade e depuração]]
- [[Segurança de aplicações]]
- [[Arquitetura e trade-offs]]
- [[IA aplicada e RAG]]

Use backlinks para descobrir conexões inesperadas: ao estudar um tema novo, ligue-o aos conceitos antigos que ele reutiliza. Revise o mapa depois de cada projeto incremental, quando as relações deixam de ser apenas teóricas e passam a ter exemplos reais.
