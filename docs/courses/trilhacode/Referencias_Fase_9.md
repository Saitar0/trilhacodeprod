---
title: "Referências — Fase 9"
aliases:
  - Referências da Fase 9
tags:
  - trilhas
  - referencias
tipo: referencia
status: planejamento
---

# Referências — Fase 9

> [!abstract] Como usar
> Lista de referências selecionadas para a Fase 9. Cada item segue o padrão
> do [[Guia_de_Producao_de_Conteudo|guia de produção]]: **título + URL + o que cobre**.
> Antes de produzir cada unidade, confira a URL e a cobertura e registre a data da conferência no conteúdo; materiais secundários complementam, mas não substituem as fontes principais.
> Mínimo de 2 referências por submódulo obrigatório e 1 por repertório/opcional.

## 40.1 — RabbitMQ

- **RabbitMQ Docs — Tutorials** · https://www.rabbitmq.com/docs/tutorials · filas, exchanges, bindings e work queues.
- **RabbitMQ — Acknowledgements and confirms** · https://www.rabbitmq.com/docs/confirms · ack/nack, prefetch, redelivery e publisher confirms.
- **RabbitMQ Docs — Dead letter exchanges** · https://www.rabbitmq.com/docs/dlx · DLQ.

## 40.2 — Kafka

- **Apache Kafka 4.2 — Documentation** · https://kafka.apache.org/documentation/ · tópicos, partições, grupos, offsets e retenção.
- **Apache Kafka 4.2 — Consumer configurations** · https://kafka.apache.org/42/configuration/consumer-configs/ · configuração atual do consumer.
- **Confluent — Kafka intro** · https://developer.confluent.io/what-is-apache-kafka/ · conceitos de Kafka.

## 40.3 — Comparação

- **AWS — SQS Docs (reuso)** · https://docs.aws.amazon.com/sqs/ · SQS.
- **GCP — Pub/Sub Docs (reuso)** · https://cloud.google.com/pubsub/docs · Pub/Sub.
- **Apache Kafka — Documentation (reuso)** · https://kafka.apache.org/documentation/ · log, partições, retenção e grupos de consumidores.
- **Amazon SQS — Pricing** · https://aws.amazon.com/sqs/pricing/ · drivers de preço do serviço gerenciado.
- **Google Cloud Pub/Sub — Pricing** · https://cloud.google.com/pubsub/pricing · custos por uso e região.
- **Amazon MSK — Pricing** · https://aws.amazon.com/msk/pricing/ · exemplo de Kafka gerenciado; o custo de Kafka autogerenciado depende da infraestrutura/operação escolhida.

## 41.1 — Arquitetura distribuída

- **Microservices.io — Saga pattern** · https://microservices.io/patterns/data/saga.html · saga e comunicação entre serviços.
- **Microservices.io — Transactional outbox** · https://microservices.io/patterns/data/transactional-outbox.html · outbox.
- **Martin Fowler — Circuit Breaker** · https://martinfowler.com/bliki/CircuitBreaker.html · circuit breaker e resiliência.

## 41.2 — Regra dura

- **Martin Fowler — Microservices** · https://martinfowler.com/articles/microservices.html · quando (não) dividir em serviços.
- **Martin Fowler — Monolith First** · https://martinfowler.com/bliki/MonolithFirst.html · descobrir fronteiras antes de distribuir.

## 42.1 — Base (Python/Django)

- **Django Docs** · https://docs.djangoproject.com/ · Django, ORM e migrations.
- **Django REST Framework Docs** · https://www.django-rest-framework.org/ · DRF.

## 42.2 — Ecossistema

- **Celery Docs** · https://docs.celeryq.dev/ · Celery.
- **pytest Docs** · https://docs.pytest.org/ · pytest.
- **Poetry Docs** · https://python-poetry.org/docs/ · Poetry.

## 42.3 — Noções

- **FastAPI Docs** · https://fastapi.tiangolo.com/ · FastAPI.
- **Flask Docs** · https://flask.palletsprojects.com/ · Flask.

## 43.1 — Stack (PHP/Laravel)

- **Laravel Docs** · https://laravel.com/docs · Laravel, Eloquent, filas e autenticação.
- **PHP — Supported Versions** · https://www.php.net/supported-versions.php · versões mantidas para construir projetos novos.
- **PHP — Unsupported Branches** · https://www.php.net/eol.php · PHP 7.4 como legado fora de suporte.

## 43.2 — Noções

- **Slim Framework Docs** · https://www.slimframework.com/docs/ · Slim.
- **Phalcon Docs** · https://docs.phalcon.io/ · Phalcon.

## 44.1 — Stack (C#/.NET)

- **ASP.NET Core Docs** · https://learn.microsoft.com/aspnet/core/ · ASP.NET Core.
- **EF Core Docs** · https://learn.microsoft.com/ef/core/ · EF Core e migrations.
- **Dapper — Repository** · https://github.com/DapperLib/Dapper · SQL parametrizado e mapeamento leve.
- **xUnit Docs** · https://xunit.net/ · xUnit.

## 44.2 — Legado

- **ASP.NET Web Forms Docs** · https://learn.microsoft.com/aspnet/web-forms/ · WebForms.

## 45.1 — Stack (Java/Spring)

- **Spring Framework Reference** · https://docs.spring.io/spring-framework/reference/ · Spring e injeção de dependência.
- **Spring Data JPA Docs** · https://spring.io/projects/spring-data-jpa · JPA.

## 46.1 — Realidade de mercado

- **Martin Fowler — Strangler Fig Application** · https://martinfowler.com/bliki/StranglerFigApplication.html · strangler pattern e modernização.
- **Martin Fowler — Technical debt** · https://martinfowler.com/bliki/TechnicalDebt.html · débito técnico.

## 46.2 — Projeto incremental da fase

- **RabbitMQ Docs (reuso)** · https://www.rabbitmq.com/docs/tutorials · produtor/consumidor, retry e DLQ.
- **RabbitMQ — Reliability Guide** · https://www.rabbitmq.com/docs/reliability · confirmação e falhas de publicação/consumo.
- **Microservices.io — Transactional Outbox** · https://microservices.io/patterns/data/transactional-outbox.html · publicação confiável a partir de transação local.
- **OpenTelemetry Docs (reuso)** · https://opentelemetry.io/docs/ · logs, métricas e correlação.
- **[[Guia_Projetos_e_Rotacao_de_Tipos|Guia de Projetos]]** · regras do projeto acumulado.

## 46.3 — Projeto de fase (Trilho B)

- **[[Guia_Projetos_e_Rotacao_de_Tipos|Guia de Projetos]]** · regras de rotação de tipos e escopo do projeto.
- **Microservices.io — Saga pattern (reuso)** · https://microservices.io/patterns/data/saga.html · processamento assíncrono da entrega.


