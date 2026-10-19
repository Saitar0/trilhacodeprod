---
title: "Fase 8 — Orquestração, observabilidade e operação"
aliases:
  - Fase 8
tags:
  - trilhas
  - fase
tipo: fase
ordem: 8
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 8 — Orquestração, observabilidade e operação

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Operar a aplicação publicada: orquestração gerenciada, observabilidade e resposta madura a incidentes.

## Por que esta fase vem agora?
Publicar não é operar; observabilidade e resposta a incidentes fecham o ciclo de operar, aprender e registrar decisões.

## Pré-requisitos
Fase 7 (pipeline, cloud e Terraform).

## Competências
- Reconhecer ECS, EKS e Kubernetes básico
- Instrumentar com logs, métricas e traces
- Conduzir análise de causa raiz e postmortem

## Projeto incremental
Tracing e métricas em dashboard e postmortem simulado de um incidente, sobre o deploy da Fase 7. Detalhado em [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2 Projeto incremental da fase]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_8_Infra_Operacao#39.3 — Projeto de fase (Trilho B)|39.3 Projeto de fase (Trilho B)]].

## Critério de conclusão
Deploy observado com dashboard de métricas e traces e um postmortem simulado de incidente.

## Estimativa de carga horária

**Total estimado da fase:** 23–39,5 h (referência de planejamento: 31 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 37 — Orquestração gerenciada e outras clouds|Módulo 37 — Orquestração gerenciada e outras clouds]]
- [[#Módulo 38 — Observabilidade|Módulo 38 — Observabilidade]]
- [[#Módulo 39 — Operação madura e projeto da fase|Módulo 39 — Operação madura e projeto da fase]]

---

## Módulo 37 — Orquestração gerenciada e outras clouds

**Objetivo:** Comparar ECS e EKS por nível de abstração, controle, operação e custo, reconhecendo que ambos deixam responsabilidades ao time.

**Submódulos:** [[Fase_8_Infra_Operacao#37.1 — Serviços gerenciados|37.1 Serviços gerenciados]] · [[Fase_8_Infra_Operacao#37.2 — Kubernetes básico|37.2 Kubernetes básico]] · [[Fase_8_Infra_Operacao#37.3 — GCP: noções|37.3 GCP: noções]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 37.1 — Serviços gerenciados

**Classificação:** `solo` · `repertorio` · `repertorio` · #infra

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Comparar ECS e EKS por nível de abstração, controle, operação e custo, reconhecendo que ambos deixam responsabilidades ao time.

**Tópicos:**
- [ ] ECS
- [ ] EKS

**Critério de conclusão:** Comparar ECS e EKS em quatro dimensões (operação, portabilidade, custo total e expertise) para um workload de API containerizada.

**Relações:** Complementar: [[Fase_8_Infra_Operacao#37.2 — Kubernetes básico|37.2]], [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]]

### 37.2 — Kubernetes básico

**Classificação:** `solo` · `repertorio` · `repertorio` · #infra

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Explicar ciclo de vida básico de Pod, função de Deployment e descoberta/acesso a Pods por Service.

**Tópicos:**
- [ ] pods
- [ ] deployments
- [ ] services

**Critério de conclusão:** Desenhar Pod → Deployment/ReplicaSet → Service e explicar o que acontece quando Pod é substituído e quando readiness está falsa.

**Relações:** Complementar: [[Fase_8_Infra_Operacao#37.1 — Serviços gerenciados|37.1]], [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]]

### 37.3 — GCP: noções

**Classificação:** `solo` · `repertorio` · `repertorio` · #infra

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer Cloud Run, Pub/Sub e GKE e compará-los a serviços AWS sem presumir equivalência perfeita.

**Tópicos:**
- [ ] Cloud Run
- [ ] Pub/Sub
- [ ] GKE

**Critério de conclusão:** Montar quadro AWS ↔ GCP com Cloud Run, mensageria e Kubernetes e escrever pelo menos dois limites da equivalência para o mesmo caso de uso.

**Relações:** Relacionado: [[Fase_7_Infra_Deploy_e_Cloud#35.1 — Serviços e eventos|35.1]], [[Fase_8_Infra_Operacao#37.1 — Serviços gerenciados|37.1]]

---

## Módulo 38 — Observabilidade

**Objetivo:** Distinguir logs, métricas e traces e instrumentar uma requisição com contexto que permita correlacionar os sinais.

**Submódulos:** [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1 Sinais operacionais]] · [[Fase_8_Infra_Operacao#38.2 — Ferramentas|38.2 Ferramentas]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 38.1 — Sinais operacionais

**Classificação:** `solo` · `obrigatorio` · `media` · #infra #qualidade

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Distinguir logs, métricas e traces e instrumentar uma requisição com contexto que permita correlacionar os sinais.

**Tópicos:**
- [ ] logs estruturados
- [ ] métricas
- [ ] tracing

**Atividade prática:** Converta logs de texto de API em campos estruturados: timestamp, service, env, route template, status, duration e trace_id. Gere uma requisição que falha, encontre sua métrica e trace associado. Remova token/corpo e explique quais campos serão enviados e por quanto tempo.

**Critério de conclusão:** A pessoa explica qual pergunta cada sinal responde e percorre uma requisição correlacionando log, métrica e trace sem expor dados sensíveis.

**Relações:** Revisita: [[Fase_5_Backend_e_Arquitetura#17.2 — Depuração no servidor|17.2]], [[Fase_3_Base_da_Web_JS_TS_Node#7.5 — Depuração no navegador|7.5]], [[Fase_8_Infra_Operacao#38.2 — Ferramentas|38.2]]

### 38.2 — Ferramentas

**Classificação:** `pratica` · `obrigatorio` · `media` · #ferramentas #infra

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Instrumentar uma aplicação com OpenTelemetry, coletar métricas com Prometheus e criar dashboard investigável no Grafana; reconhecer New Relic como opção gerenciada.

**Pré-requisitos:** Pré-requisito 38.1. Complementa projeto incremental em 39.2.

**Tópicos:**
- [ ] OpenTelemetry
- [ ] Prometheus
- [ ] Grafana
- [ ] New Relic — *opcional*

**Atividade prática:** Com compose local, instrumente endpoint HTTP para request count/duration/error e trace de chamada ao banco. Exponha métricas a Prometheus e conecte-o ao Grafana. Monte dashboard com volume, erro, p95 e uma navegação para trace; provoque uma lentidão controlada e localize o span. Documente labels, sampling, retenção e dados excluídos. New Relic pode ser explorado em conta de teste, sem dados sensíveis.

**Critério de conclusão:** Dashboard mostra métricas e a pessoa usa uma anomalia para localizar a causa no trace, explica o pipeline de telemetria e controla cardinalidade/dados sensíveis.

**Relações:** Relacionado: [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]], [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2]]

---

## Módulo 39 — Operação madura e projeto da fase

**Objetivo:** Conduzir análise de causa raiz sem culpabilização e registrar SLI/SLO/SLA, runbook, postmortem e ADR acionáveis.

**Submódulos:** [[Fase_8_Infra_Operacao#39.1 — Operação madura|39.1 Operação madura]] · [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2 Projeto incremental da fase]] · [[Fase_8_Infra_Operacao#39.3 — Projeto de fase (Trilho B)|39.3 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 39.1 — Operação madura

**Classificação:** `integrado` · `obrigatorio` · `media` · #infra #qualidade

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Conduzir análise de causa raiz sem culpabilização e registrar SLI/SLO/SLA, runbook, postmortem e ADR acionáveis.

**Tópicos:**
- [ ] análise de causa raiz
- [ ] postmortem
- [ ] SLA
- [ ] SLO
- [ ] runbooks
- [ ] ADRs

**Atividade prática:** Use incidente simulado: deploy aumenta erros 5xx por configuração. Escreva timeline, impacto, detecção, mitigação, fatores contribuintes e ações com owner/data/evidência; crie runbook com query, rollback e escalonamento; registre um ADR para estratégia de rollout. Defina um SLI e SLO simples para disponibilidade ou latência, explicitando janela e exclusões. Faça revisão sem dados reais.

**Critério de conclusão:** Postmortem tem narrativa verificável e ações atribuídas; runbook permite reproduzir resposta; ADR compara alternativas; SLI/SLO/SLA são distinguidos corretamente.

**Relações:** Relacionado: [[Fase_7_Infra_Deploy_e_Cloud#32.2 — Entrega|32.2]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]], [[Fase_5_Backend_e_Arquitetura#23.3 — Regra dura|23.3]]

### 39.2 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #infra

**Carga horária estimada:** 10 h–16 h (referência: 13 h).

**Objetivo:** Operar o projeto principal do Trilho A, acrescentando traces, métricas em dashboard e um postmortem simulado sobre o deploy da Fase 7.

**Tópicos:**
- [ ] deploy automatizado do projeto na AWS com Terraform e pipeline
- [ ] tracing e métricas em dashboard + postmortem simulado de um incidente

**Atividade prática:** Injete atraso controlado em um endpoint de staging, gere tráfego de teste, localize degradação em painel, abra trace relacionado e identifique span responsável. Restaure o serviço e escreva postmortem com evidências e uma ação preventiva testável. **Rubrica:** vínculo métrica→trace reproduzível, sinal útil, sem exposição sensível, mitigação demonstrada e ações claras.

**Critério de conclusão:** Deploy observado com dashboard de métricas e traces e um postmortem simulado completo, com causa/fatores e ações verificáveis.

**Relações:** Complementar: [[Fase_7_Infra_Deploy_e_Cloud#32.2 — Entrega|32.2]], [[Fase_7_Infra_Deploy_e_Cloud#36.1 — Infra como código|36.1]], [[Fase_8_Infra_Operacao#38.2 — Ferramentas|38.2]]

### 39.3 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #infra

**Carga horária estimada:** 8 h–14 h (referência: 11 h).

**Objetivo:** Escolher tipo pendente do Trilho B e implantar sua fatia vertical em container, pipeline e observabilidade básica que evidencie o problema central.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Construa menor entrega que prove o critério do tipo escolhido e provoque falha controlada para validar o sinal. **Rubrica:** base correta, artefato/pipeline reproduzível, deploy protegido, observabilidade suficiente, critério central comprovado, custo/risco documentado e recursos de laboratório removidos.

**Critério de conclusão:** Versão da Fase 8 implantada com container e pipeline; logs/métrica adequada evidenciam problema central, a entrega cumpre rotação e o tipo é registrado somente após prova de aceite.

**Relações:** Complementar: [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2]]
