---
title: "Fase 9 — Escala, mensageria e pluralidade de mercado"
aliases:
  - Fase 9
tags:
  - trilhas
  - fase
tipo: fase
ordem: 9
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 9 — Escala, mensageria e pluralidade de mercado

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Entender processamento assíncrono e sistemas distribuídos e ler outras stacks de mercado por comparação, sem reescrever o projeto desnecessariamente.

## Por que esta fase vem agora?
Mensageria e sistemas distribuídos só fazem sentido depois de dominar API, banco e operação; comparar stacks depois disso permite enxergar a equivalência dos conceitos.

## Pré-requisitos
Fases 5 e 8, em especial [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]] (mensageria: conceitos) e a operação com observabilidade.

## Competências
- Implementar produtor e consumidor com retry, DLQ e idempotência
- Comparar RabbitMQ, Kafka, SQS e Pub/Sub
- Avaliar quando microsserviços valem o custo
- Ler e comparar Python, PHP, C# e Java por modelo de execução, DI, ORM, testes e deploy, construindo uma delas
- Propor modernização gradual de sistemas legados

## Projeto incremental
Fila no projeto com produtor e consumidor, retry e DLQ; serviço extra via mensageria e comparação escrita com a stack escolhida. Detalhado em [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2 Projeto incremental da fase]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_9_Escala_Mensageria_e_Mercado#46.3 — Projeto de fase (Trilho B)|46.3 Projeto de fase (Trilho B)]].

## Critério de conclusão
Fila no projeto com produtor e consumidor, retry e DLQ funcionando, com decisões documentadas e comparação escrita com uma segunda stack.

## Ordem de estudo sugerida
Entre Python, PHP, C# e Java, escolha uma stack para construir e faça leitura guiada das demais.

## Estimativa de carga horária

**Total estimado da fase:** 31,5–53 h (referência de planejamento: 42 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 40 — Mensageria na prática: RabbitMQ e Kafka|Módulo 40 — Mensageria na prática: RabbitMQ e Kafka]]
- [[#Módulo 41 — Arquitetura distribuída|Módulo 41 — Arquitetura distribuída]]
- [[#Módulo 42 — Python e ecossistema web|Módulo 42 — Python e ecossistema web]]
- [[#Módulo 43 — PHP e Laravel|Módulo 43 — PHP e Laravel]]
- [[#Módulo 44 — C# e .NET|Módulo 44 — C# e .NET]]
- [[#Módulo 45 — Java e Spring|Módulo 45 — Java e Spring]]
- [[#Módulo 46 — Realidade de mercado e projeto da fase|Módulo 46 — Realidade de mercado e projeto da fase]]

---

## Módulo 40 — Mensageria na prática: RabbitMQ e Kafka

**Objetivo:** Implementar produtor e consumidor RabbitMQ com roteamento, ack/nack, prefetch e dead-lettering, explicando o comportamento em falhas.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#40.1 — RabbitMQ|40.1 RabbitMQ]] · [[Fase_9_Escala_Mensageria_e_Mercado#40.2 — Kafka|40.2 Kafka]] · [[Fase_9_Escala_Mensageria_e_Mercado#40.3 — Comparação|40.3 Comparação]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 40.1 — RabbitMQ

**Classificação:** `solo` · `obrigatorio` · `media` · #arquitetura #infra

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Implementar produtor e consumidor RabbitMQ com roteamento, ack/nack, prefetch e dead-lettering, explicando o comportamento em falhas.

**Pré-requisitos:** Pré-requisito 33.1. RabbitMQ é o broker aprofundado para projeto 46.2; compara-se com Kafka em 40.2 e 40.3.

**Tópicos:**
- [ ] filas e exchanges
- [ ] bindings e roteamento
- [ ] ack e nack
- [ ] prefetch e consumo concorrente
- [ ] DLQ no RabbitMQ

**Atividade prática:** Com broker local descartável, publique pedido, consuma com ack manual, limite prefetch e crie DLX. Desligue consumidor antes do ack e observe redelivery; provoque erro permanente e verifique DLQ; processe duplicata e prove que a chave de negócio não duplica efeito. Registre topologia, retry, confirms, durabilidade e comportamento de cada falha.

**Critério de conclusão:** Explicar mensagem da publicação ao ack, comparar ack/nack e demonstrar redelivery e DLQ sem efeito duplicado nem loop ilimitado.

**Relações:** Relacionado: [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]], [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2]], [[Fase_9_Escala_Mensageria_e_Mercado#40.2 — Kafka|40.2]], [[Fase_9_Escala_Mensageria_e_Mercado#40.3 — Comparação|40.3]]

### 40.2 — Kafka

**Classificação:** `solo` · `repertorio` · `repertorio` · #arquitetura #infra

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Interpretar producers, consumers, partições, grupos, offsets e retenção num experimento curto de Kafka.

**Tópicos:**
- [ ] producers
- [ ] consumers
- [ ] partições
- [ ] grupos
- [ ] offsets
- [ ] retenção de mensagens

**Critério de conclusão:** Explicar como três partições e dois consumers no mesmo grupo distribuem trabalho, onde ordenação existe e como offset pode ser repetido.

**Relações:** Revisita: [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]], [[Fase_9_Escala_Mensageria_e_Mercado#40.3 — Comparação|40.3]], [[Fase_9_Escala_Mensageria_e_Mercado#45.1 — Stack: Java e Spring|45.1]]

### 40.3 — Comparação

**Classificação:** `integrado` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Escolher entre Kafka, SQS e Pub/Sub para um cenário, comparando semântica, operação e custo, sem tratá-los como equivalentes.

**Tópicos:**

**Atividade prática:** Preencha cenário “processar pedidos com replay de eventos e três consumidores” e outro “executar tarefas de e-mail com baixa operação”. Para cada opção, registre ordem, retenção/replay, duplicatas, consumidores, DLQ, gestão, custo/driver e risco operacional. Escolha uma por cenário e cite evidência dos experimentos/documentos.

**Critério de conclusão:** O quadro recomenda serviço para cada cenário e justifica por semântica, custo e operação; identifica pelo menos uma limitação da opção escolhida.

**Relações:** Revisita: [[Fase_7_Infra_Deploy_e_Cloud#35.1 — Serviços e eventos|35.1]], [[Fase_8_Infra_Operacao#37.3 — GCP: noções|37.3]], [[Fase_9_Escala_Mensageria_e_Mercado#40.2 — Kafka|40.2]], [[Fase_9_Escala_Mensageria_e_Mercado#40.1 — RabbitMQ|40.1]]

---

## Módulo 41 — Arquitetura distribuída

**Objetivo:** Escolher comunicação síncrona ou assíncrona e aplicar timeout, retry limitado, circuit breaker, saga e outbox com consciência de consistência.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#41.1 — Arquitetura distribuída|41.1 Arquitetura distribuída]] · [[Fase_9_Escala_Mensageria_e_Mercado#41.2 — Regra dura|41.2 Regra dura]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 41.1 — Arquitetura distribuída

**Classificação:** `integrado` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Escolher comunicação síncrona ou assíncrona e aplicar timeout, retry limitado, circuit breaker, saga e outbox com consciência de consistência.

**Tópicos:**
- [ ] comunicação síncrona
- [ ] comunicação assíncrona
- [ ] saga
- [ ] outbox
- [ ] resiliência
- [ ] circuit breaker
- [ ] tolerância a falhas

**Atividade prática:** Para “criar pedido e reservar estoque em serviço separado”, desenhe versão síncrona e assíncrona. Defina timeout, retry e breaker; mostre outbox e idempotency key; desenhe saga com compensação de reserva e falha durante compensação. Discuta estados visíveis ao usuário e monitoramento. Depois compare com manter um módulo transacional no mesmo banco.

**Critério de conclusão:** Escolher comunicação para cenário concreto e explicar efeito sobre consistência; propor timeout/retry/breaker e fluxos outbox/saga com tratamento de duplicatas/falhas.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.2 — Boas práticas|18.2]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]], [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

### 41.2 — Regra dura

**Classificação:** `integrado` · `obrigatorio` · `media` · #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Decidir se vale separar um sistema em microsserviços, justificando os custos operacionais e os limites da arquitetura atual.

**Tópicos:**

**Atividade prática:** Para um sistema de pedidos hipotético, compare manter monólito modular com extrair notificações em serviço. Liste um benefício mensurável, dois custos operacionais e um sinal que justificaria a extração. Registre também qual observação faria voltar atrás. A conclusão pode ser manter ou dividir; avalia-se a justificativa, não a preferência.

**Critério de conclusão:** Justificar por escrito por que manter (ou dividir) um sistema hipotético, com benefícios esperados, custo adicional e evidência que faria rever a decisão.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#41.1 — Arquitetura distribuída|41.1]], [[Fase_9_Escala_Mensageria_e_Mercado#46.1 — Realidade de mercado|46.1]]

---

## Módulo 42 — Python e ecossistema web

**Objetivo:** Reconhecer a estrutura de uma API Django/DRF e compará-la com a arquitetura Node já estudada; construir apenas se esta for a stack escolhida.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#42.1 — Base: Python, Django e DRF|42.1 Base: Python, Django e DRF]] · [[Fase_9_Escala_Mensageria_e_Mercado#42.2 — Ecossistema Python|42.2 Ecossistema Python]] · [[Fase_9_Escala_Mensageria_e_Mercado#42.3 — Noções: FastAPI e Flask|42.3 Noções: FastAPI e Flask]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 42.1 — Base: Python, Django e DRF

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer a estrutura de uma API Django/DRF e compará-la com a arquitetura Node já estudada; construir apenas se esta for a stack escolhida.

**Tópicos:**
- [ ] fundamentos de Python: sintaxe, tipos e pacotes (só se for a stack construída)
- [ ] Django
- [ ] DRF
- [ ] ORM
- [ ] migrations

**Critério de conclusão:** Ler uma requisição do router à resposta e mapear modelos, migrations, validação e permissões para conceitos já vistos em Node.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]]

### 42.2 — Ecossistema Python

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Explicar papéis de Celery, pytest e Poetry e relacioná-los a filas, testes e gerenciamento de dependências conhecidos em Node.

**Tópicos:**
- [ ] Celery
- [ ] pytest
- [ ] Poetry

**Critério de conclusão:** Escolher ferramenta para um caso (worker, teste, dependência) e explicar seu equivalente aproximado e uma diferença importante em Node.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#42.1 — Base: Python, Django e DRF|42.1]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]]

### 42.3 — Noções: FastAPI e Flask

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Comparar o escopo e as convenções de FastAPI e Flask com a estrutura mais integrada de Django.

**Tópicos:**
- [ ] FastAPI
- [ ] Flask

**Critério de conclusão:** Comparar escopo, validação/schema, dependências e convenções de dois frameworks com Django para cenário especificado.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#42.1 — Base: Python, Django e DRF|42.1]]

---

## Módulo 43 — PHP e Laravel

**Objetivo:** Ler uma API PHP/Laravel e relacionar routing, Eloquent, filas e autenticação a conceitos de Node; construir apenas se for a stack escolhida.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#43.1 — Stack: PHP e Laravel|43.1 Stack: PHP e Laravel]] · [[Fase_9_Escala_Mensageria_e_Mercado#43.2 — Noções: Slim e Phalcon|43.2 Noções: Slim e Phalcon]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 43.1 — Stack: PHP e Laravel

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Ler uma API PHP/Laravel e relacionar routing, Eloquent, filas e autenticação a conceitos de Node; construir apenas se for a stack escolhida.

**Tópicos:**
- [ ] fundamentos de PHP 7.4+ e Composer (só se for a stack construída)
- [ ] Laravel
- [ ] Eloquent
- [ ] filas
- [ ] APIs
- [ ] autenticação

**Critério de conclusão:** Mapear route/controller, validação, ORM/migration, queue e auth para Node; se construiu, evidenciar API mínima usando PHP/Laravel em versão suportada.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]]

### 43.2 — Noções: Slim e Phalcon

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer Slim e Phalcon como opções do ecossistema PHP e comparar seus níveis de abstração com Laravel.

**Tópicos:**
- [ ] Slim
- [ ] Phalcon

**Critério de conclusão:** Comparar Slim e Phalcon com Laravel em abstração, componentes integrados, extensibilidade e operação.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#43.1 — Stack: PHP e Laravel|43.1]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]]

---

## Módulo 44 — C# e .NET

**Objetivo:** Ler uma API ASP.NET Core e comparar DI, EF Core, Dapper e testes com a experiência Node; construir apenas se esta for a stack escolhida.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#44.1 — Stack: C# e .NET|44.1 Stack: C# e .NET]] · [[Fase_9_Escala_Mensageria_e_Mercado#44.2 — Legado .NET: WebForms|44.2 Legado .NET: WebForms]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 44.1 — Stack: C# e .NET

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Ler uma API ASP.NET Core e comparar DI, EF Core, Dapper e testes com a experiência Node; construir apenas se esta for a stack escolhida.

**Tópicos:**
- [ ] fundamentos de C# e NuGet (só se for a stack construída)
- [ ] ASP.NET Core
- [ ] EF Core
- [ ] Dapper
- [ ] xUnit
- [ ] SQL Server

**Critério de conclusão:** Mapear route/controller, DI, acesso a dados e testes para equivalentes aproximados em Node; identificar quando escolher EF Core ou Dapper.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]]

### 44.2 — Legado .NET: WebForms

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer WebForms em sistemas legados e distingui-lo de ASP.NET Core moderno.

**Tópicos:**
- [ ] WebForms

**Critério de conclusão:** Ao abrir uma página de exemplo, identificar code-behind, lifecycle, postback e ViewState e explicar duas implicações de manutenção/migração.

**Relações:** Relacionado: [[Fase_9_Escala_Mensageria_e_Mercado#44.1 — Stack: C# e .NET|44.1]], [[Fase_9_Escala_Mensageria_e_Mercado#46.1 — Realidade de mercado|46.1]]

---

## Módulo 45 — Java e Spring

**Objetivo:** Ler ou construir uma API Java com Spring, DI, JPA, testes e Kafka e mapear esses conceitos a Node.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#45.1 — Stack: Java e Spring|45.1 Stack: Java e Spring]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 45.1 — Stack: Java e Spring

**Classificação:** `solo` · `repertorio` · `repertorio` · #mercado

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Ler ou construir uma API Java com Spring, DI, JPA, testes e Kafka e mapear esses conceitos a Node.

**Tópicos:**
- [ ] fundamentos de Java e Maven ou Gradle (só se for a stack construída)
- [ ] Spring
- [ ] injeção de dependência
- [ ] JPA
- [ ] testes
- [ ] integração com Kafka

**Critério de conclusão:** Mapear controller/service/repository/DI/testes/Kafka para Node e explicar limite de um teste com mock de repository.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#19.1 — ORM e acesso a dados|19.1]], [[Fase_9_Escala_Mensageria_e_Mercado#40.2 — Kafka|40.2]]

---

## Módulo 46 — Realidade de mercado e projeto da fase

**Objetivo:** Propor modernização gradual de sistema legado e reconhecer quando débito técnico ou volumetria justifica mudança arquitetural.

**Submódulos:** [[Fase_9_Escala_Mensageria_e_Mercado#46.1 — Realidade de mercado|46.1 Realidade de mercado]] · [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2 Projeto incremental da fase]] · [[Fase_9_Escala_Mensageria_e_Mercado#46.3 — Projeto de fase (Trilho B)|46.3 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 46.1 — Realidade de mercado

**Classificação:** `integrado` · `obrigatorio` · `media` · #mercado

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Propor modernização gradual de sistema legado e reconhecer quando débito técnico ou volumetria justifica mudança arquitetural.

**Tópicos:**
- [ ] estratégias de modernização
- [ ] strangler pattern
- [ ] débito técnico
- [ ] alta volumetria

**Atividade prática:** Para legado hipotético de vendas, desenhe dependências e riscos; escolha um endpoint de baixo risco para extrair atrás de fachada. Registre contratos, fonte de verdade, estratégia de tráfego, métrica de sucesso, rollback e condição de aposentadoria. Liste dois débitos com evidência/impacto e compare otimização vertical vs particionar quando latência/volume medidos ultrapassarem requisito.

**Critério de conclusão:** Proposta apresenta sequência incremental, redução de risco, plano de dados/rollback e evidências que justificam dívida e volumetria.

**Relações:** Relacionado: [[Fase_9_Escala_Mensageria_e_Mercado#44.2 — Legado .NET: WebForms|44.2]], [[Fase_9_Escala_Mensageria_e_Mercado#41.2 — Regra dura|41.2]]

### 46.2 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 12 h–18 h (referência: 15 h).

**Objetivo:** Evoluir o Trilho A com produtor, consumidor, fila RabbitMQ, retry, DLQ e idempotência, acrescentar serviço extra via mensageria e comparar a stack escolhida com uma segunda stack.

**Tópicos:**
- [ ] fila no projeto: produtor e consumidor com retry e DLQ
- [ ] serviço extra via mensageria + comparação escrita com a stack escolhida

**Atividade prática:** No projeto Trilho A, produza evento de uma operação de negócio e consuma para uma tarefa lateral. Simule falha antes/depois do efeito, duplicata, broker indisponível e poison message; prove que repetição não duplica efeito. Implemente API mínima do serviço extra na stack escolhida. **Rubrica:** contrato claro, entrega/efeito confiáveis, DLQ utilizável, observabilidade e comparação apoiada em código/execução.

**Critério de conclusão:** Fila com produtor/consumidor, retry e DLQ funcionando; consumidor idempotente demonstrado; serviço extra via mensageria e comparação com segunda stack documentados.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#40.1 — RabbitMQ|40.1]], [[Fase_9_Escala_Mensageria_e_Mercado#41.1 — Arquitetura distribuída|41.1]], [[Fase_1_Base_Tecnica#3.5 — Projeto incremental da fase|3.5]]

### 46.3 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #arquitetura

**Carga horária estimada:** 10 h–16 h (referência: 13 h).

**Objetivo:** Escolher uma ideia de Trilho B e demonstrar sua regra técnica central com fila, retry, DLQ, idempotência e ADR em escopo mínimo local.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Implemente menor fluxo vertical que prove o tipo e injete falha antes/depois do efeito. Capture resultado da duplicata, contagem de retries e mensagem na DLQ; reprocese com correção controlada. **Rubrica:** cobertura válida, requisito central testável, proteção idempotente, operação explicada, ADR comparativo e escopo enxuto.

**Critério de conclusão:** Variante local de tipo pendente (ou projeto livre se cobertura completa) demonstra fila, retry, DLQ e idempotência e registra decisões em ADR; só marcar tipo novo quando aceite cumprir a regra de cobertura.

**Relações:** Complementar: [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2]]
