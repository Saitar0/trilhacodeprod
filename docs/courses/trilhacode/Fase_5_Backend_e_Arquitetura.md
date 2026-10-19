---
title: "Fase 5 — Backend e arquitetura"
aliases:
  - Fase 5
tags:
  - trilhas
  - fase
tipo: fase
ordem: 5
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 5 — Backend e arquitetura

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Construir APIs seguras, testáveis e bem organizadas em Node.js, aplicando princípios de arquitetura de forma proporcional ao problema.

## Por que esta fase vem agora?
Depois de saber como os dados são persistidos e antes de construir a interface, constrói-se a camada que une as duas; autenticação, validação e testes se tornam inevitáveis aqui.

## Pré-requisitos
Fase 3 (JavaScript, TypeScript e Node/npm) e Fase 4 (dados e Docker).

## Competências
- Estruturar APIs REST com validação e tratamento de erros
- Implementar autenticação e autorização
- Aplicar acoplamento, coesão e padrões com critério
- Organizar o backend de forma modular com NestJS
- Testar rotas, serviços e acesso a banco

## Projeto incremental
API com autenticação persistindo no PostgreSQL, com cache e suíte de testes cobrindo rotas e serviços, executável com Docker Compose (Módulo 10, estudado na Fase 4). Detalhado em [[Fase_5_Backend_e_Arquitetura#24.3 — Projeto incremental da fase|24.3 Projeto incremental da fase]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_5_Backend_e_Arquitetura#24.4 — Projeto de fase (Trilho B)|24.4 Projeto de fase (Trilho B)]].

## Critério de conclusão
API autenticada, persistida em PostgreSQL, com suíte de testes cobrindo rotas e serviços e executável por um comando.

## Ordem de estudo sugerida
1. Módulo 17 (Node e execução no servidor)
2. Módulo 18 (APIs REST)
3. [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1 Tipos de teste]] (tipos de teste, antecipado)
4. [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1 ORM e acesso a dados]] e [[Fase_5_Backend_e_Arquitetura#19.2 — Regra de maturidade|19.2 Regra de maturidade]] (Módulo 19, ORM, movido da Fase 4)
5. Módulo 20 (autenticação e segurança)
6. Módulos 21 e 22 (design e NestJS)
7. Módulo 23 (arquitetura)
8. [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2 Aplicação]], [[Fase_5_Backend_e_Arquitetura#24.3 — Projeto incremental da fase|24.3 Projeto incremental da fase]] e [[Fase_5_Backend_e_Arquitetura#24.4 — Projeto de fase (Trilho B)|24.4 Projeto de fase (Trilho B)]]

## Estimativa de carga horária

**Total estimado da fase:** 45–79 h (referência de planejamento: 62 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 17 — Node.js e execução no servidor|Módulo 17 — Node.js e execução no servidor]]
- [[#Módulo 18 — APIs REST|Módulo 18 — APIs REST]]
- [[#Módulo 19 — ORM e acesso a dados (movido da Fase 4)|Módulo 19 — ORM e acesso a dados (movido da Fase 4)]]
- [[#Módulo 20 — Autenticação e segurança de APIs|Módulo 20 — Autenticação e segurança de APIs]]
- [[#Módulo 21 — Princípios de design de software|Módulo 21 — Princípios de design de software]]
- [[#Módulo 22 — NestJS e organização modular|Módulo 22 — NestJS e organização modular]]
- [[#Módulo 23 — Arquitetura de software e raciocínio de design|Módulo 23 — Arquitetura de software e raciocínio de design]]
- [[#Módulo 24 — Testes de backend|Módulo 24 — Testes de backend]]

---

## Módulo 17 — Node.js e execução no servidor

**Objetivo:** Explicar o runtime Node.js, o event loop, módulos e processamento assíncrono, usando streams para arquivos grandes.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#17.1 — Fundamentos|17.1 Fundamentos]] · [[Fase_5_Backend_e_Arquitetura#17.2 — Depuração no servidor|17.2 Depuração no servidor]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 17.1 — Fundamentos

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Explicar o runtime Node.js, o event loop, módulos e processamento assíncrono, usando streams para arquivos grandes.

**Tópicos:**
- [ ] runtime JavaScript no servidor
- [ ] event loop
- [ ] módulos
- [ ] npm
- [ ] scripts
- [ ] jobs
- [ ] streams
- [ ] processamento assíncrono

**Atividade prática:** Conte linhas de um arquivo grande com stream, trate erros com `pipeline` e compare memória conceitual com leitura integral. Explique que parsing correto de CSV precisa lidar com aspas, quebras e encoding.

**Critério de conclusão:** Explique o caminho de uma operação de I/O e implemente processamento assíncrono em stream sem acumular o arquivo todo.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_5_Backend_e_Arquitetura#24.4 — Projeto de fase (Trilho B)|24.4]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]]

### 17.2 — Depuração no servidor

**Classificação:** `pratica` · `obrigatorio` · `media` · #ferramentas #qualidade

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Usar inspector e breakpoints para seguir execução, interpretar stack traces e registrar logs úteis.

**Tópicos:**
- [ ] inspector e breakpoints no Node
- [ ] leitura de erros e stack traces do servidor
- [ ] logs úteis durante o desenvolvimento

**Atividade prática:** Crie uma rota local com bug reproduzível, pause em breakpoint, siga a stack trace e corrija a causa. Adicione log de erro com contexto não sensível.

**Critério de conclusão:** Localize a causa de erro de servidor usando stack trace, breakpoint e logs.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#7.5 — Depuração no navegador|7.5]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

---

## Módulo 18 — APIs REST

**Objetivo:** Projetar rotas HTTP por recurso e separar controller, middleware, validação e tratamento de erros.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1 Estrutura]] · [[Fase_5_Backend_e_Arquitetura#18.2 — Boas práticas|18.2 Boas práticas]] · [[Fase_5_Backend_e_Arquitetura#18.3 — Tempo real|18.3 Tempo real]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 18.1 — Estrutura

**Classificação:** `integrado` · `obrigatorio` · `alta` · #web #arquitetura

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Projetar rotas HTTP por recurso e separar controller, middleware, validação e tratamento de erros.

**Tópicos:**
- [ ] métodos HTTP e códigos de status
- [ ] semântica REST: recursos e verbos
- [ ] Express como base do NestJS (noção)
- [ ] rotas
- [ ] controllers
- [ ] middlewares
- [ ] validação
- [ ] tratamento de erros
- [ ] tipos e DTOs do contrato conferidos com o frontend (revisita do 27.3)

**Atividade prática:** Implemente CRUD de recurso com rotas, controller, middleware e validação. Teste payload inválido, ausente, conflito e erro interno. Defina DTO compartilhado e validação executada no servidor. **Rubrica:** método/status coerentes; contrato explícito; rejeição runtime; erro sem vazamento.

**Critério de conclusão:** Rejeite entrada inválida de forma consistente e mostre contrato tipado nas camadas, explicando que tipo não substitui validação.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]], [[Fase_6_Frontend_Moderno#27.3 — Contrato de dados|27.3]], [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]]

### 18.2 — Boas práticas

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Evoluir APIs com paginação, versionamento, respostas consistentes, OpenAPI e idempotência de escrita.

**Tópicos:**
- [ ] versionamento
- [ ] paginação
- [ ] padronização de resposta
- [ ] documentação com OpenAPI/Swagger
- [ ] organização de camadas
- [ ] idempotência em endpoints de escrita (Idempotency-Key)

**Atividade prática:** Adicione paginação cursor, OpenAPI e endpoint de criação idempotente. Simule retry após resposta perdida e duas requisições concorrentes com a mesma chave. **Rubrica:** sem duplicar efeito, resultado repetível, paginação ordenada e contrato verificável.

**Critério de conclusão:** Evolua API sem quebrar contrato anterior na mudança escolhida e demonstre retry que não duplica efeito.

**Relações:** Complementar: [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]], [[Fase_7_Infra_Deploy_e_Cloud#32.2 — Entrega|32.2]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]]

### 18.3 — Tempo real

**Classificação:** `solo` · `obrigatorio` · `media` · #web #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Comparar polling, SSE e WebSocket e implementar canal autenticado com reconexão e estado compartilhado básico.

**Tópicos:**
- [ ] polling, SSE e WebSocket: diferenças e quando usar cada um
- [ ] autenticação na conexão
- [ ] salas ou canais e difusão (broadcast)
- [ ] reconexão com backoff e retomada a partir do último evento
- [ ] mensagens duplicadas e fora de ordem
- [ ] estado compartilhado: last-write-wins e resolução de conflitos (OT e CRDT, noção)
- [ ] limites da escala horizontal (noção; retomado na Fase 9)

**Atividade prática:** Crie canal para vários clientes observarem o mesmo recurso; autentique ao conectar, reconecte com backoff e retome a partir de ID quando disponível. Escreva teste com dois clientes. **Rubrica:** acesso autorizado, estado demonstrável, duplicatas tratadas, limitação de retenção explicada.

**Critério de conclusão:** Explique duplicidade/ordem e demonstre recuperação de queda sem assumir entrega exatamente uma vez.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#18.2 — Boas práticas|18.2]], [[Fase_9_Escala_Mensageria_e_Mercado#41.1 — Arquitetura distribuída|41.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#48.2 — Operação|48.2]]

---

## Módulo 19 — ORM e acesso a dados (movido da Fase 4)

**Objetivo:** Entender mapeamento objeto-relacional e usar Prisma ou TypeORM observando schema, SQL gerado e limites.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1 ORM e acesso a dados]] · [[Fase_5_Backend_e_Arquitetura#19.2 — Regra de maturidade|19.2 Regra de maturidade]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 19.1 — ORM e acesso a dados

**Classificação:** `solo` · `obrigatorio` · `media` · #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Entender mapeamento objeto-relacional e usar Prisma ou TypeORM observando schema, SQL gerado e limites.

**Tópicos:**
- [ ] o que é ORM
- [ ] vantagem e limite de ORM
- [ ] mapeamento objeto-relacional
- [ ] Prisma ou TypeORM

**Atividade prática:** Mapeie duas entidades do projeto em Prisma, crie migration, faça uma leitura com relação e observe SQL/contagem de consultas. Reescreva uma consulta adequada em SQL direto e compare clareza/custo.

**Critério de conclusão:** Mostre SQL gerado por uma operação e explique mapeamento, custo e uma limitação.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#19.2 — Regra de maturidade|19.2]]

### 19.2 — Regra de maturidade

**Classificação:** `integrado` · `obrigatorio` · `media` · #dados #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Escolher ORM ou SQL direto com base na consulta, domínio e evidência, preservando entendimento do banco.

**Tópicos:**

**Atividade prática:** No projeto, documente um uso em que ORM reduz repetição e outro em que consulta SQL explícita melhora controle/clareza. Inclua código/SQL e risco residual.

**Critério de conclusão:** Dê exemplo contextual em que ORM ajuda e outro em que atrapalha.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]]

---

## Módulo 20 — Autenticação e segurança de APIs

**Objetivo:** Desenhar login, renovação e logout, comparando sessão e token sem confundir JWT com OAuth.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1 Autenticação]] · [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2 Segurança básica]] · [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3 Segurança aplicada]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 20.1 — Autenticação

**Classificação:** `solo` · `obrigatorio` · `alta` · #seguranca

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Desenhar login, renovação e logout, comparando sessão e token sem confundir JWT com OAuth.

**Tópicos:**
- [ ] JWT
- [ ] refresh token
- [ ] OAuth2
- [ ] sessão vs token
- [ ] cookies e armazenamento de tokens

**Atividade prática:** Desenhe fluxo de login, access token, refresh rotation e logout para uma aplicação web. Marque armazenamento, validações, expiração, revogação e ameaça de replay/CSRF. Implemente usando biblioteca mantida; não escreva primitivas criptográficas próprias.

**Critério de conclusão:** Explique fluxo, expiração, armazenamento e risco de cada abordagem e demonstre logout/revogação coerente.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]], [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_1_Base_Tecnica#2.3 — Acesso remoto|2.3]]

### 20.2 — Segurança básica

**Classificação:** `solo` · `obrigatorio` · `alta` · #seguranca

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Proteger senhas, consultas, configuração e requisições cross-origin com controles adequados ao risco.

**Tópicos:**
- [ ] hash de senha
- [ ] CORS
- [ ] SQL injection e prepared statements
- [ ] CSRF no backend (tokens e SameSite)
- [ ] segredos
- [ ] variáveis de ambiente
- [ ] OWASP básico

**Atividade prática:** Migre um exemplo inseguro para hash Argon2id via biblioteca, substitua SQL concatenado por parâmetros, restrinja CORS e remova segredo de configuração versionada. Para cookies, desenhe defesa CSRF. **Rubrica:** comportamento legítimo preservado, input tratado como dado, credenciais não expostas, limitações explicitadas.

**Critério de conclusão:** Explique hash versus criptografia, o que CORS não protege e por que parâmetros previnem injection.

**Relações:** Revisita: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]], [[Fase_6_Frontend_Moderno#27.4 — Segurança no navegador|27.4]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]]

### 20.3 — Segurança aplicada

**Classificação:** `integrado` · `obrigatorio` · `media` · #seguranca

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Aplicar autorização por recurso, reduzir exposição de dados e proteger endpoints contra abuso.

**Tópicos:**
- [ ] riscos comuns em APIs
- [ ] autorização
- [ ] exposição de dados
- [ ] proteção de credenciais
- [ ] rate limiting
- [ ] dados pessoais e LGPD (noções): minimização, base legal e retenção

**Atividade prática:** Implemente recurso que só o dono pode ler/alterar e escreva teste negativo tentando acessar ID de outra pessoa. Aplique rate limit a rota de login. Faça lista dos dados pessoais usados no exemplo, finalidade didática, retenção e campos que não serão logados. **Rubrica:** teste bloqueia acesso horizontal, dados mínimos retornados, limite demonstrável, pressupostos de privacidade explícitos.

**Critério de conclusão:** Teste reproduzível bloqueia acesso indevido e você explica exposição, proteção de credenciais e limites do rate limiting.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]], [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1]], [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1]]

---

## Módulo 21 — Princípios de design de software

**Objetivo:** Identificar acoplamento, coesão e responsabilidades em um módulo e refatorá-lo para facilitar mudança e teste.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#21.1 — Base conceitual|21.1 Base conceitual]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 21.1 — Base conceitual

**Classificação:** `solo` · `obrigatorio` · `media` · #arquitetura #fundamentos

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Identificar acoplamento, coesão e responsabilidades em um módulo e refatorá-lo para facilitar mudança e teste.

**Tópicos:**
- [ ] acoplamento
- [ ] coesão
- [ ] separação de responsabilidades

**Atividade prática:** Refatore um módulo que valida pedido, salva no banco e envia e-mail. Separe regra da entrega HTTP e da integração, mantendo fluxo simples. **Rubrica:** fronteiras claras, regra testável, dependência explícita, complexidade resultante justificada.

**Critério de conclusão:** Identifique acoplamento e baixa coesão num trecho e explique como a refatoração facilita um teste específico.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#7.2 — Organização do código|7.2]], [[Fase_5_Backend_e_Arquitetura#23.1 — Modelos|23.1]]

---

## Módulo 22 — NestJS e organização modular

**Objetivo:** Organizar uma API NestJS com módulos, controllers, providers e injeção de dependência.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#22.1 — Estrutura de framework|22.1 Estrutura de framework]] · [[Fase_5_Backend_e_Arquitetura#22.2 — Organização forte|22.2 Organização forte]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 22.1 — Estrutura de framework

**Classificação:** `solo` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Organizar uma API NestJS com módulos, controllers, providers e injeção de dependência.

**Tópicos:**
- [ ] módulos
- [ ] controllers
- [ ] providers
- [ ] injeção de dependência

**Atividade prática:** Migre uma rota Express para módulo Nest, controller e provider; injete repository e substitua-o no teste. **Rubrica:** fluxo entendível, dependências registradas, regra fora do controller, teste exercita comportamento.

**Critério de conclusão:** Explique como DI facilita substituir dependência num teste e mostre fronteira de módulo.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#21.1 — Base conceitual|21.1]], [[Fase_5_Backend_e_Arquitetura#22.2 — Organização forte|22.2]]

### 22.2 — Organização forte

**Classificação:** `solo` · `obrigatorio` · `media` · #arquitetura #seguranca

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Validar DTOs em runtime com pipes e controlar acesso a rotas usando guards.

**Tópicos:**
- [ ] DTOs
- [ ] pipes
- [ ] guards
- [ ] arquitetura mais estruturada

**Atividade prática:** Crie DTO de criação com validação, rejeite campo não declarado e proteja rota com guard de autenticação e autorização. Teste payload inválido, sem token, papel insuficiente e acesso a objeto alheio. **Rubrica:** cada camada tem responsabilidade clara, teste cobre negações, resposta não revela segredo.

**Critério de conclusão:** Mostre onde validação e autorização ocorrem no ciclo da requisição e prove falhas com testes.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_5_Backend_e_Arquitetura#22.1 — Estrutura de framework|22.1]]

---

## Módulo 23 — Arquitetura de software e raciocínio de design

**Objetivo:** Reconhecer Clean Architecture, ports and adapters, SOLID e padrões e aplicar uma fronteira útil ao projeto.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#23.1 — Modelos|23.1 Modelos]] · [[Fase_5_Backend_e_Arquitetura#23.2 — Base de raciocínio|23.2 Base de raciocínio]] · [[Fase_5_Backend_e_Arquitetura#23.3 — Regra dura|23.3 Regra dura]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 23.1 — Modelos

**Classificação:** `solo` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Reconhecer Clean Architecture, ports and adapters, SOLID e padrões e aplicar uma fronteira útil ao projeto.

**Tópicos:**
- [ ] Clean Architecture
- [ ] Hexagonal
- [ ] SOLID
- [ ] design patterns

**Atividade prática:** Isole acesso ao repositório do serviço de reserva com uma porta e adaptador PostgreSQL. Adicione teste da regra com fake e justifique se abstração vale o custo. **Rubrica:** dependência apontada, regra isolável, adapter concreto, trade-off discutido.

**Critério de conclusão:** Justifique um padrão aplicado por um problema concreto e mostre como a fronteira altera uma dependência.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#21.1 — Base conceitual|21.1]], [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2]]

### 23.2 — Base de raciocínio

**Classificação:** `solo` · `obrigatorio` · `media` · #fundamentos #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Escolher estruturas de dados e algoritmos simples a partir de operações, volume e custo de mudança.

**Tópicos:**
- [ ] estruturas de dados
- [ ] algoritmos básicos
- [ ] escolha de estrutura
- [ ] custo conceitual

**Atividade prática:** Compare busca repetida de ID em array versus Map para N itens; descreva tempo de construção, busca e complexidade para N pequeno e grande. Escolha estrutura e explique custo conceitual.

**Critério de conclusão:** Explique a estrutura escolhida e seu custo relevante para o cenário.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_3_Base_da_Web_JS_TS_Node#7.4 — Revisita de lógica|7.4]], [[Fase_6_Frontend_Moderno#30.1 — Otimização|30.1]]

### 23.3 — Regra dura

**Classificação:** `integrado` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Reconhecer quando uma abstração ou arquitetura aumenta complexidade sem resolver uma necessidade presente.

**Tópicos:**

**Atividade prática:** Encontre um padrão aplicado em trecho simples que aumentou indirection. Remova ou mantenha após explicar contexto, impacto em leitura/teste e alternativa menor.

**Critério de conclusão:** Dê um exemplo em que padrão piorou clareza e identifique a opção mais simples.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#23.1 — Modelos|23.1]]

---

## Módulo 24 — Testes de backend

**Objetivo:** Distinguir testes unitários e de integração, usar mocks com critério e interpretar cobertura.

**Submódulos:** [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1 Tipos de teste]] · [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2 Aplicação]] · [[Fase_5_Backend_e_Arquitetura#24.3 — Projeto incremental da fase|24.3 Projeto incremental da fase]] · [[Fase_5_Backend_e_Arquitetura#24.4 — Projeto de fase (Trilho B)|24.4 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 24.1 — Tipos de teste

**Classificação:** `solo` · `obrigatorio` · `alta` · #qualidade

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Distinguir testes unitários e de integração, usar mocks com critério e interpretar cobertura.

**Tópicos:**
- [ ] unitários
- [ ] integração
- [ ] mocks
- [ ] cobertura

**Atividade prática:** Teste serviço com dependência mockada para sucesso e falha; identifique qual risco permanece sem integração. Planeje o teste de integração da rota protegida.

**Critério de conclusão:** Explique qual risco cada tipo cobre e justifique onde usar mock.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2]]

### 24.2 — Aplicação

**Classificação:** `pratica` · `obrigatorio` · `alta` · #qualidade

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Testar serviços e rotas e verificar persistência em banco com dependências isoladas e estado repetível.

**Tópicos:**
- [ ] testes em serviços
- [ ] testes em rotas
- [ ] testes com banco
- [ ] isolamento de dependências

**Atividade prática:** Teste serviço de criação, rota com entrada válida/inválida e integração que persiste registro em banco isolado após migrations. Faça teste de duplicidade/constraint. **Rubrica:** repetível, isolado, cobre sucesso/erro, verifica efeito real no caso de integração.

**Critério de conclusão:** Suíte de serviços e rotas roda repetidamente e cobre fluxo de persistência sem depender de banco compartilhado.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]], [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2]]

### 24.3 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #qualidade #infra

**Carga horária estimada:** 8 h–12 h (referência: 10 h).

**Objetivo:** Evoluir o projeto principal do Trilho A para uma API autenticada em PostgreSQL, com cache e testes, executável via Compose.

**Tópicos:**
- [ ] API com autenticação persistindo no PostgreSQL
- [ ] Docker Compose subindo app + banco + cache
- [ ] suíte de testes cobrindo rotas e serviços

**Atividade prática:** Escolha uma fatia vertical do projeto: criar/consultar recurso autenticado, persistir, cachear leitura repetida e cobrir fluxo com testes. Recrie banco de teste pelas migrations. **Aceite:** comando documentado inicia dependências; teste verifica recurso persistido e usuário sem permissão não acessa.

**Critério de conclusão:** API autenticada persiste no PostgreSQL; suíte cobre rotas e serviços; conjunto roda com Compose.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2]], [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]], [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1]], [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2]], [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]]

### 24.4 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #qualidade

**Carga horária estimada:** 12 h–18 h (referência: 15 h).

**Objetivo:** Construir uma API autenticada e persistida para uma ideia elegível do Trilho B, demonstrando o problema técnico do tipo com testes.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Implemente a menor API capaz de provar a regra do tipo selecionado. Configure banco de teste isolado e cenários negativos (retry/concorrência, cruzamento de tenant, queda/reconexão, paginação incorreta ou falha de job). **Rubrica:** critério central exercitado, teste detectaria regressão, nenhuma credencial real, escopo enxuto e decisão explicada.

**Critério de conclusão:** API autenticada e persistida com testes de rota/serviço; cenário reproduzível prova requisito específico do tipo e é registrado no guia de cobertura.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#24.3 — Projeto incremental da fase|24.3]]
