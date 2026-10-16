---
title: "Fase 7 — Infraestrutura, deploy e cloud"
aliases:
  - Fase 7
tags:
  - trilhas
  - fase
tipo: fase
ordem: 7
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 7 — Infraestrutura, deploy e cloud

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Automatizar a entrega da aplicação e provisionar infraestrutura em nuvem com CI/CD, cloud e infraestrutura como código.

## Por que esta fase vem agora?
Com uma aplicação testada, falta fazê-la rodar de forma reproduzível fora da máquina local: pipeline, cloud e Terraform.

## Pré-requisitos
Fase 1 (terminal, SSH e Git), Fase 4 (dados e containers) e Fase 5 (API e testes).

## Competências
- Levar containers do ambiente local ao pipeline e ao deploy
- Automatizar build, testes e deploy
- Provisionar infraestrutura na AWS com Terraform
- Aplicar IAM e rede com menor privilégio

## Projeto incremental
Deploy automatizado do projeto na AWS com Terraform e pipeline. Detalhado em [[Fase_7_Infra_Deploy_e_Cloud#36.2 — Ambientes|36.2 Ambientes]].

> [!note] Trilho B na Fase 8
> O projeto de fase (Trilho B) desta trilha de infraestrutura fica na [[Fase_8_Infra_Operacao#39.3 — Projeto de fase (Trilho B)|Fase 8]], junto com o postmortem e a observabilidade.

## Critério de conclusão
Deploy automatizado do projeto na AWS com Terraform e pipeline, com recursos destruídos ao fim do laboratório.

## Ordem de estudo sugerida
O Docker (Módulo 10) já foi estudado na Fase 4; aqui ele é levado ao pipeline e ao deploy.

## Estimativa de carga horária

**Total estimado da fase:** 13–26 h (referência de planejamento: 20 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 32 — CI/CD e entrega|Módulo 32 — CI/CD e entrega]]
- [[#Módulo 33 — Mensageria: conceitos|Módulo 33 — Mensageria: conceitos]]
- [[#Módulo 34 — Fundamentos de cloud (AWS)|Módulo 34 — Fundamentos de cloud (AWS)]]
- [[#Módulo 35 — AWS: serviços sob demanda e eventos|Módulo 35 — AWS: serviços sob demanda e eventos]]
- [[#Módulo 36 — Infraestrutura como código|Módulo 36 — Infraestrutura como código]]

---

## Módulo 32 — CI/CD e entrega

**Objetivo:** Criar workflow de CI com GitHub Actions que executa lint, build e testes em pull requests e bloqueia integração quando algum quality gate falha.

**Submódulos:** [[Fase_7_Infra_Deploy_e_Cloud#32.1 — Automação|32.1 Automação]] · [[Fase_7_Infra_Deploy_e_Cloud#32.2 — Entrega|32.2 Entrega]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 32.1 — Automação

**Classificação:** `solo` · `obrigatorio` · `media` · #infra #qualidade

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Criar workflow de CI com GitHub Actions que executa lint, build e testes em pull requests e bloqueia integração quando algum quality gate falha.

**Tópicos:**
- [ ] GitHub Actions
- [ ] build
- [ ] teste
- [ ] lint
- [ ] quality gates
- [ ] Sonar — *repertorio*

**Atividade prática:** Adicione workflow para PR com lint, build e testes da aplicação. Faça um job falhar deliberadamente em branch de exercício, confirme que o merge é bloqueado pela regra configurada e restaure o workflow. Revise permissões, versions de Actions, logs e uso de secrets. Documente Sonar como opção, incluindo limite do score.

**Critério de conclusão:** PR executa os três checks, falha visível bloqueia integração e política de branch os marca obrigatórios; permissões e segredos são revisados.

**Relações:** Revisita: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]], [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]], [[Fase_6_Frontend_Moderno#29.2 — Integração e borda|29.2]], [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1]]

### 32.2 — Entrega

**Classificação:** `integrado` · `obrigatorio` · `media` · #infra

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Publicar automaticamente uma versão em staging, promover mudanças com controle e executar rollback de aplicação sem perder dados.

**Tópicos:**
- [ ] deploy automatizado
- [ ] staging
- [ ] rollback

**Atividade prática:** Configure ambiente staging no GitHub e deploy automático após merge; publique uma versão anterior e uma nova. Introduza defeito de saúde, detecte-o e volte ao artefato anterior. Simule uma migração aditiva compatível e descreva como tratar remoção de coluna. Revise credenciais, regra de aprovação, concorrência e smoke check.

**Critério de conclusão:** Deploy automatizado alcança staging e a pessoa demonstra rollback de aplicação reproduzível, explicando limites para dados/migrações e verificação pós-deploy.

**Relações:** Relacionado: [[Fase_7_Infra_Deploy_e_Cloud#32.1 — Automação|32.1]], [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2]], [[Fase_5_Backend_e_Arquitetura#18.2 — Boas práticas|18.2]]

---

## Módulo 33 — Mensageria: conceitos

**Objetivo:** Desenhar produtor, broker, consumidor, retry e DLQ e explicar idempotência em processamento assíncrono.

**Submódulos:** [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1 Conceitos]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 33.1 — Conceitos

**Classificação:** `solo` · `obrigatorio` · `media` · #infra #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Desenhar produtor, broker, consumidor, retry e DLQ e explicar idempotência em processamento assíncrono.

**Tópicos:**
- [ ] filas
- [ ] tópicos
- [ ] DLQ
- [ ] idempotência
- [ ] retries

**Atividade prática:** Desenhe fluxo de pedido: API produz evento, worker reserva/processa, confirma; introduza falha antes e depois do efeito, retry e DLQ. Indique chave idempotente, transação/registro que impede duplicação, limites e alerta. Explique qual consistência o cliente observa durante processamento.

**Critério de conclusão:** Diagrama mostra produtor → broker → consumidor, confirmação, retry limitado e DLQ; a pessoa explica como uma redelivery não repete o efeito de negócio.

**Relações:** Revisita: [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#18.2 — Boas práticas|18.2]], [[Fase_7_Infra_Deploy_e_Cloud#35.1 — Serviços e eventos|35.1]], [[Fase_9_Escala_Mensageria_e_Mercado#40.1 — RabbitMQ|40.1]]

---

## Módulo 34 — Fundamentos de cloud (AWS)

**Objetivo:** Descrever o caminho de uma requisição em uma VPC e os limites de IAM, compute, storage, database, DNS/TLS e custo em um laboratório AWS.

**Submódulos:** [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1 Base de cloud]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 34.1 — Base de cloud

**Classificação:** `solo` · `obrigatorio` · `media` · #infra #seguranca

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Descrever o caminho de uma requisição em uma VPC e os limites de IAM, compute, storage, database, DNS/TLS e custo em um laboratório AWS.

**Tópicos:**
- [ ] IAM
- [ ] EC2
- [ ] S3
- [ ] RDS
- [ ] VPC básica
- [ ] domínio e DNS na prática
- [ ] TLS/HTTPS
- [ ] reverse proxy e load balancer
- [ ] custos
- [ ] free tier
- [ ] alertas de orçamento
- [ ] destruir recursos ao fim do estudo
- [ ] CDN — *repertorio*

**Atividade prática:** Desenhe VPC com subnets públicas/privadas, load balancer, EC2 e RDS; acompanhe DNS→TLS→proxy→app→DB e identifique regras mínimas. Em conta/lab autorizado, crie bucket privado e compute mínimo com role, configure alerta e estimate regional; destrua tudo depois, confirme recursos remanescentes e custos. Se não houver conta, use diagrama e calculator sem provisionar.

**Critério de conclusão:** Explica caminho de rede e escopo IAM, identifica exposição indevida e produz estimativa mensal com região, hipóteses, alertas e plano de destruição.

**Relações:** Revisita: [[Fase_1_Base_Tecnica#2.3 — Acesso remoto|2.3]], [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1]], [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]], [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_7_Infra_Deploy_e_Cloud#35.1 — Serviços e eventos|35.1]], [[Fase_7_Infra_Deploy_e_Cloud#36.1 — Infra como código|36.1]]

---

## Módulo 35 — AWS: serviços sob demanda e eventos

**Objetivo:** Escolher entre Lambda/API Gateway, SQS, SNS, EventBridge e ElastiCache para compor um fluxo gerenciado adequado.

**Submódulos:** [[Fase_7_Infra_Deploy_e_Cloud#35.1 — Serviços e eventos|35.1 Serviços e eventos]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 35.1 — Serviços e eventos

**Classificação:** `solo` · `obrigatorio` · `media` · #infra

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Escolher entre Lambda/API Gateway, SQS, SNS, EventBridge e ElastiCache para compor um fluxo gerenciado adequado.

**Tópicos:**
- [ ] Lambda
- [ ] API Gateway
- [ ] SQS
- [ ] SNS
- [ ] EventBridge
- [ ] ElastiCache

**Atividade prática:** Desenhe API Gateway → Lambda produtora → SQS → Lambda consumidora; inclua idempotência, DLQ e alarmes. Proponha quando SNS faria fan-out e quando EventBridge filtraria por tipo de evento. Acrescente cache em leitura com TTL/invalidação e indique comportamento na falha. Implemente apenas em sandbox autorizado; caso contrário faça o diagrama sem provisionar.

**Critério de conclusão:** A pessoa explica quando escolher SQS, SNS ou EventBridge, descreve comportamento de redelivery e identifica papel/limites do cache no fluxo.

**Relações:** Revisita: [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]], [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]]

---

## Módulo 36 — Infraestrutura como código

**Objetivo:** Descrever recursos AWS com Terraform, revisar plano e explicar providers, state, módulos e variáveis.

**Submódulos:** [[Fase_7_Infra_Deploy_e_Cloud#36.1 — Infra como código|36.1 Infra como código]] · [[Fase_7_Infra_Deploy_e_Cloud#36.2 — Ambientes|36.2 Ambientes]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 36.1 — Infra como código

**Classificação:** `solo` · `obrigatorio` · `media` · #infra

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Descrever recursos AWS com Terraform, revisar plano e explicar providers, state, módulos e variáveis.

**Tópicos:**
- [ ] providers
- [ ] state
- [ ] módulos
- [ ] variáveis

**Atividade prática:** Em sandbox, defina provider AWS, variável de região e bucket privado com tags. Execute `fmt`, `validate`, `plan`; explique cada criação/alteração e não aplique até revisar. Para laboratório descartável, aplique só se autorizado, modifique tag, revise segundo plan e destrua explicitamente ao encerrar. Inspecione onde state fica e confirme exclusão/segurança; nunca use credenciais de produção.

**Critério de conclusão:** A pessoa explica provider, módulo, variável e state; interpreta plano com create/update/destroy e identifica risco de segredo ou destruição antes de apply.

**Relações:** Revisita: [[Fase_1_Base_Tecnica#3.1 — Git local|3.1]], [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]], [[Fase_7_Infra_Deploy_e_Cloud#34.1 — Base de cloud|34.1]]

### 36.2 — Ambientes

**Classificação:** `solo` · `obrigatorio` · `media` · #infra

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Entregar o projeto da Fase 7: automatizar o deploy AWS com Terraform e pipeline, separar ambientes, limitar permissões e destruir os recursos ao fim do laboratório.

**Tópicos:**
- [ ] múltiplos ambientes com tfvars e workspaces
- [ ] provisionamento de stack
- [ ] Terragrunt — *repertorio*

**Atividade prática:** Parametrize nome, tamanho e tags de um recurso. Crie `dev.tfvars` e `staging.tfvars`, use states segregados e mostre que o plan de cada um não altera o outro. Confirme workspace/backend/credenciais antes de qualquer apply. Documente como destruir cada ambiente separadamente e qual proteção impede alcançar produção.

**Critério de conclusão:** Deploy do Trilho A na AWS é automatizado por pipeline com Terraform; a pessoa instancia dev/staging com variáveis e state separados, demonstra gate e health check, explica limite de workspaces e decisão sobre Terragrunt, e destrói os recursos de laboratório ao encerrar.

**Relações:** Complementar: [[Fase_7_Infra_Deploy_e_Cloud#36.1 — Infra como código|36.1]]
