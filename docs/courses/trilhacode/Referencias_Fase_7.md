---
title: "Referências — Fase 7"
aliases:
  - Referências da Fase 7
tags:
  - trilhas
  - referencias
tipo: referencia
status: planejamento
---

# Referências — Fase 7

> [!abstract] Como usar
> Lista de referências selecionadas para a Fase 7. Cada item segue o padrão
> do [[Guia_de_Producao_de_Conteudo|guia de produção]]: **título + URL + o que cobre**.
> Antes de produzir cada unidade, confira a URL e a cobertura e registre a data da conferência no conteúdo; materiais secundários complementam, mas não substituem as fontes principais.
> Mínimo de 2 referências por submódulo obrigatório e 1 por repertório/opcional.

## 32.1 — Automação

- **GitHub Actions — Understanding workflows** · https://docs.github.com/en/actions/about-github-actions/understanding-github-actions · eventos, jobs, steps e runners.
- **GitHub Actions — Secure use** · https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions · permissões, segredos e cadeia de suprimentos.
- **Sonar Docs** · https://docs.sonarsource.com/sonarqube/ · análise estática (repertório).

## 32.2 — Entrega

- **GitHub Actions — Control deployments** · https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments · proteção de ambiente, concorrência e histórico.
- **GitHub Actions — Deploy to an environment** · https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/deploy-to-an-environment · associar job a ambiente.
- **GitHub Actions — OIDC in AWS** · https://docs.github.com/en/actions/security-for-github-actions/security-hardening-for-github-actions/configuring-openid-connect-in-amazon-web-services · credenciais temporárias federadas.

## 33.1 — Conceitos

- **Martin Fowler — Message Queue patterns** · https://martinfowler.com/articles/patterns-of-distributed-systems/ · filas, retries, DLQ e idempotência.
- **AWS — Message Queuing (What is a message queue?)** · https://aws.amazon.com/message-queue/ · conceitos de filas e tópicos.
- **Amazon SQS — At-least-once delivery** · https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html · duplicatas e consumidores idempotentes.
- **Amazon SQS — Dead-letter queues** · https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html · mensagens com falhas persistentes.

## 34.1 — Base de cloud

- **AWS IAM — Best practices** · https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html · roles, credenciais temporárias e MFA.
- **Amazon VPC — Route tables** · https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html · rotas e subnets.
- **Amazon EC2 — Getting started** · https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html · instâncias e operação.
- **Amazon S3 — Creating a general purpose bucket** · https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html · buckets e configuração inicial.
- **Amazon RDS — Getting started** · https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.html · banco relacional gerenciado.
- **Amazon Route 53 — What is Route 53?** · https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html · DNS e resolução de nomes.
- **AWS Certificate Manager — What is ACM?** · https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html · certificados TLS.
- **Elastic Load Balancing — What is a load balancer?** · https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html · balanceamento de tráfego.
- **AWS Billing — Budgets and cost management** · https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html · alertas e acompanhamento de custos.
- **AWS Pricing Calculator** · https://calculator.aws/ · estimativa por configuração e região.
- **AWS Free Tier** · https://aws.amazon.com/free/ · ofertas e elegibilidade vigentes; confirmar condições da conta.

## 35.1 — Serviços e eventos

- **AWS Lambda — Developer Guide** · https://docs.aws.amazon.com/lambda/latest/dg/welcome.html · funções orientadas a eventos.
- **Amazon API Gateway — Developer Guide** · https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html · APIs HTTP/WebSocket e integrações.
- **Amazon SQS — Developer Guide** · https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html · filas, redelivery e operação.
- **Amazon SNS — Developer Guide** · https://docs.aws.amazon.com/sns/latest/dg/welcome.html · tópicos e assinaturas.
- **Amazon EventBridge — What is EventBridge?** · https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html · barramento, regras e roteamento.
- **Amazon ElastiCache — What is ElastiCache?** · https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html · cache gerenciado e engines.

## 36.1 — Infra como código

- **Terraform Docs** · https://developer.hashicorp.com/terraform/docs · providers, state, módulos e variáveis.
- **Terraform Docs — Configuration language** · https://developer.hashicorp.com/terraform/language · HCL e recursos.
- **Terraform — State** · https://developer.hashicorp.com/terraform/language/state · mapeamento e sensibilidade do state.
- **Terraform — Use modules** · https://developer.hashicorp.com/terraform/language/modules/configuration · composição de módulos.

## 36.2 — Ambientes

- **Terraform Docs — Workspaces** · https://developer.hashicorp.com/terraform/cli/workspaces · múltiplos ambientes.
- **Terraform — Input variables** · https://developer.hashicorp.com/terraform/language/values/variables · configuração por ambiente.
- **GitHub Actions — OIDC in AWS** · https://docs.github.com/en/actions/security-for-github-actions/security-hardening-for-github-actions/configuring-openid-connect-in-amazon-web-services · identidade federada para implantação.
- **Terragrunt Docs** · https://terragrunt.gruntwork.io/docs/ · muitos ambientes/stacks (repertório).


