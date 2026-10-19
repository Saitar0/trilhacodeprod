---
title: "Referências — Fase 4"
aliases:
  - Referências da Fase 4
tags:
  - trilhas
  - referencias
tipo: referencia
status: planejamento
---

# Referências — Fase 4

> [!abstract] Como usar
> Lista de referências selecionadas para a Fase 4. Cada item segue o padrão
> do [[Guia_de_Producao_de_Conteudo|guia de produção]]: **título + URL + o que cobre**.
> Antes de produzir cada unidade, confira a URL e a cobertura da referência e
> registre a data da conferência no conteúdo; complemente fontes gerais com
> materiais específicos do tópico.

## 9.1 — Conceitos

- **PostgreSQL Docs — Tutorial** · https://www.postgresql.org/docs/current/tutorial.html · conceitos de banco, tabelas, linhas, colunas e chaves.
- **MDN — Database basics (conceitos relacionais)** · https://developer.mozilla.org/docs/Learn_web_development/Extensions/Server-side · noções de banco e relacionamentos.

## 9.2 — Modelagem

- **PostgreSQL Docs — Data definition** · https://www.postgresql.org/docs/current/ddl.html · entidades, atributos e modelagem relacional.
- **Aalto OpenCS — Normalization: From Anomalies to Normal Forms** · https://opencs.aalto.fi/en/courses/databases/part-8/4-normalization · formas normais e anomalias de inserção, atualização e remoção.

## 9.3 — Integridade

- **PostgreSQL Docs — Constraints** · https://www.postgresql.org/docs/current/ddl-constraints.html · chaves primárias, estrangeiras e constraints.
- **PostgreSQL Docs — Data types** · https://www.postgresql.org/docs/current/datatype.html · tipos usados na garantia de consistência.

## 10.1 — Containerização

- **Docker Docs — Get started** · https://docs.docker.com/get-started/ · imagens, containers, volumes e redes.
- **Docker Docs — Dockerfile reference** · https://docs.docker.com/reference/dockerfile/ · escrita de Dockerfile.

## 10.2 — Orquestração local

- **Docker Docs — Compose overview** · https://docs.docker.com/compose/ · serviços integrados e orquestração local.
- **Docker Docs — Compose file reference** · https://docs.docker.com/reference/compose-file/ · referência do arquivo Compose.
- **Docker Official Image — PostgreSQL** · https://hub.docker.com/_/postgres · caminho de volume da imagem oficial PostgreSQL 18.

## 11.3 — Ambiente PostgreSQL

- **PostgreSQL Docs — Installation** · https://www.postgresql.org/docs/current/installation.html · instalação nativa.
- **PostgreSQL Docs — Data manipulation (DML)** · https://www.postgresql.org/docs/current/dml.html · inserção, atualização e remoção de dados.

## 11.1 — Consulta de dados

- **PostgreSQL Docs — Queries** · https://www.postgresql.org/docs/current/queries.html · SELECT, WHERE, ORDER BY e LIMIT.
- **PostgreSQL Docs — Query syntax (SELECT)** · https://www.postgresql.org/docs/current/sql-select.html · referência do SELECT e aliases.

## 11.2 — Relações

- **PostgreSQL Docs — Table expressions (JOIN)** · https://www.postgresql.org/docs/current/queries-table-expressions.html · JOIN e subqueries.
- **PostgreSQL Docs — Aggregates (GROUP BY/HAVING)** · https://www.postgresql.org/docs/current/tutorial-agg.html · GROUP BY e HAVING.

## 12.1 — Performance e leitura

- **PostgreSQL Docs — Indexes** · https://www.postgresql.org/docs/current/indexes.html · índices e EXPLAIN.
- **PostgreSQL Docs — Full text search** · https://www.postgresql.org/docs/current/textsearch.html · tsvector, índice GIN e ranking.
- **PostgreSQL Docs — pg_trgm** · https://www.postgresql.org/docs/current/pgtrgm.html · busca aproximada com trigramas.

## 12.2 — Integridade e operação

- **PostgreSQL Docs — Transactions** · https://www.postgresql.org/docs/current/tutorial-transactions.html · transações e isolamento.
- **PostgreSQL Docs — Concurrency control** · https://www.postgresql.org/docs/current/mvcc.html · isolamento, locks e SELECT FOR UPDATE.
- **PostgreSQL Docs — Backup and restore** · https://www.postgresql.org/docs/current/backup.html · pg_dump e restore.
- **Prisma Migrate (referência de migrations)** · https://www.prisma.io/docs/orm/prisma-migrate · conceito de migrations versionadas.

## 12.3 — Modelagem aplicada

- **PostgreSQL Docs — Data definition (reuso)** · https://www.postgresql.org/docs/current/ddl.html · modelagem de um domínio real.
- **PostgreSQL Docs — Performance tips** · https://www.postgresql.org/docs/current/performance-tips.html · consistência em cenários comuns.

## 13.1 — Outros bancos relacionais

- **MySQL Reference Manual** · https://dev.mysql.com/doc/refman/8.0/en/ · MySQL/MariaDB.
- **Oracle Database Docs** · https://docs.oracle.com/en/database/ · noções de Oracle.
- **Microsoft SQL Server Docs** · https://learn.microsoft.com/sql/ · noções de SQL Server.

## 14.1 — MongoDB

- **MongoDB Docs — Manual** · https://www.mongodb.com/docs/manual/ · documentos, coleções e consultas.
- **MongoDB Docs — Data modeling** · https://www.mongodb.com/docs/manual/data-modeling/ · modelagem orientada a documento.

## 15.1 — Redis

- **Redis Docs** · https://redis.io/docs/latest/ · cache, TTL e estruturas básicas.
- **Redis Docs — Data types** · https://redis.io/docs/latest/develop/data-types/ · estruturas e uso como suporte de performance.
- **Redis — SET** · https://redis.io/docs/latest/commands/set/ · armazenamento de valores e opção `EX` para expiração.
- **Redis — EXPIRE** · https://redis.io/docs/latest/commands/expire/ · configuração de expiração em segundos.

## 16.1 — Noções complementares

- **AWS — DynamoDB Docs** · https://docs.aws.amazon.com/dynamodb/ · DynamoDB.
- **Firebase — Firestore Docs** · https://firebase.google.com/docs/firestore · Firestore.
- **Elastic — Elasticsearch Docs** · https://www.elastic.co/docs · Elasticsearch.

## 16.2 — Projeto incremental da fase

- **PostgreSQL Docs — Tutorial (reuso)** · https://www.postgresql.org/docs/current/tutorial.html · persistência e consultas do projeto.
- **Redis Docs (reuso)** · https://redis.io/docs/latest/ · cache da consulta lenta.

## 16.3 — Projeto de fase (Trilho B)

- **[[Guia_Projetos_e_Rotacao_de_Tipos|Guia de Projetos]]** · regras de rotação de tipos e escopo do projeto.
- **PostgreSQL Docs — EXPLAIN** · https://www.postgresql.org/docs/current/using-explain.html · consulta medida com EXPLAIN.

