---
title: "Fase 4 — Dados e bancos"
aliases:
  - Fase 4
tags:
  - trilhas
  - fase
tipo: fase
ordem: 4
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 4 — Dados e bancos

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Modelar, persistir, consultar e otimizar dados, escolhendo o tipo de armazenamento conforme o problema e não por preferência de tecnologia.

## Por que esta fase vem agora?
Quase toda aplicação real depende de dados persistentes; modelar e consultar bem antes de construir o backend define o contrato que as camadas acima vão consumir.

## Pré-requisitos
Fase 1, noções de JSON e objetos da Fase 3 e Node/npm (6.4).

## Competências
- Modelar um domínio em entidades e relacionamentos
- Escrever consultas SQL com junções e agregações
- Garantir integridade com constraints, transações e migrations
- Analisar desempenho com índices e EXPLAIN
- Controlar concorrência com isolamento e locks e buscar texto no PostgreSQL
- Escolher entre PostgreSQL, Redis e MongoDB conforme o padrão de acesso
- Subir os bancos de forma reproduzível com Docker Compose

## Projeto incremental
Persistir o projeto incremental em PostgreSQL com modelagem própria, aplicar cache Redis em uma consulta lenta e usar uma coleção MongoDB quando houver caso de uso. Detalhado em [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2 Projeto incremental da fase]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_4_Dados_e_Bancos#16.3 — Projeto de fase (Trilho B)|16.3 Projeto de fase (Trilho B)]].

## Critério de conclusão
Aplicação persistida em PostgreSQL, com uma consulta medida e otimizada, cache funcional em Redis e um caso de uso documental justificado.

## Ordem de estudo sugerida
1. Módulo 9 (fundamentos e modelagem)
2. Módulo 10 (Docker, para subir os bancos de forma reproduzível)
3. 11.3, depois 11.1 e 11.2
4. Módulos 12, 13, 14 e 15
5. Módulo 16 (projetos)

## Estimativa de carga horária

**Total estimado da fase:** 39–72 h (referência de planejamento: 56 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 9 — Fundamentos de bancos de dados e modelagem relacional|Módulo 9 — Fundamentos de bancos de dados e modelagem relacional]]
- [[#Módulo 10 — Containers com Docker (antecipado da Fase 7)|Módulo 10 — Containers com Docker (antecipado da Fase 7)]]
- [[#Módulo 11 — SQL e PostgreSQL|Módulo 11 — SQL e PostgreSQL]]
- [[#Módulo 12 — Performance, integridade e modelagem aplicada|Módulo 12 — Performance, integridade e modelagem aplicada]]
- [[#Módulo 13 — Outros bancos relacionais|Módulo 13 — Outros bancos relacionais]]
- [[#Módulo 14 — MongoDB e modelagem orientada a documentos|Módulo 14 — MongoDB e modelagem orientada a documentos]]
- [[#Módulo 15 — Redis, cache e filas simples|Módulo 15 — Redis, cache e filas simples]]
- [[#Módulo 16 — Noções complementares e projeto de dados|Módulo 16 — Noções complementares e projeto de dados]]

---

## Módulo 9 — Fundamentos de bancos de dados e modelagem relacional

**Objetivo:** Explicar como bancos relacionais organizam dados e distinguir tabela, linha, coluna, chave primária e chave estrangeira.

**Submódulos:** [[Fase_4_Dados_e_Bancos#9.1 — Conceitos|9.1 Conceitos]] · [[Fase_4_Dados_e_Bancos#9.2 — Modelagem|9.2 Modelagem]] · [[Fase_4_Dados_e_Bancos#9.3 — Integridade|9.3 Integridade]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 9.1 — Conceitos

**Classificação:** `solo` · `obrigatorio` · `alta` · #dados #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Explicar como bancos relacionais organizam dados e distinguir tabela, linha, coluna, chave primária e chave estrangeira.

**Tópicos:**
- [ ] o que é banco de dados
- [ ] tabelas
- [ ] linhas
- [ ] colunas
- [ ] chaves
- [ ] relacionamentos

**Atividade prática:** Transforme uma lista de contatos com vários telefones por pessoa em tabelas. Desenhe as chaves e explique a cardinalidade. **Critérios:** cada telefone pertence a uma pessoa; chaves identificam linhas; a relação não duplica dados da pessoa.

**Critério de conclusão:** Explique tabela, chave e relacionamento usando um domínio próprio e identifique PK/FK em um diagrama simples.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#9.2 — Modelagem|9.2]], [[Fase_4_Dados_e_Bancos#11.1 — Consulta de dados|11.1]]

### 9.2 — Modelagem

**Classificação:** `integrado` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Converter um domínio em entidades, atributos e relações, justificando cardinalidades e normalização básica.

**Tópicos:**
- [ ] entidades
- [ ] atributos
- [ ] cardinalidade
- [ ] normalização
- [ ] modelagem relacional

**Atividade prática:** Desenhe biblioteca ou loja com ao menos quatro entidades. Marque cardinalidade, opcionalidade, PK/FK e atributos da relação. Aponte uma anomalia evitada pela separação.

**Critério de conclusão:** Justifique chaves, cardinalidades e formas normais aplicadas em um diagrama legível.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_4_Dados_e_Bancos#9.3 — Integridade|9.3]], [[Fase_4_Dados_e_Bancos#12.3 — Modelagem aplicada|12.3]]

### 9.3 — Integridade

**Classificação:** `solo` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Codificar regras de validade do domínio com chaves e constraints relacionais.

**Tópicos:**
- [ ] chave primária
- [ ] chave estrangeira
- [ ] constraints
- [ ] consistência de dados

**Atividade prática:** Adicione constraints ao modelo de loja: preço não negativo, SKU único, item referenciando pedido/produto e quantidade positiva. Demonstre uma inserção válida e três inválidas, identificando a regra violada.

**Critério de conclusão:** O banco rejeita dados inválidos e você explica a constraint responsável.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2]]

---

## Módulo 10 — Containers com Docker (antecipado da Fase 7)

**Objetivo:** Construir uma imagem e executar containers compreendendo armazenamento, rede e ciclo de vida.

**Submódulos:** [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1 Containerização]] · [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2 Orquestração local]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 10.1 — Containerização

**Classificação:** `solo` · `obrigatorio` · `alta` · #infra #ferramentas

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Construir uma imagem e executar containers compreendendo armazenamento, rede e ciclo de vida.

**Tópicos:**
- [ ] Dockerfile
- [ ] imagens
- [ ] containers
- [ ] volumes
- [ ] redes

**Atividade prática:** Execute PostgreSQL com volume nomeado, crie uma tabela, remova e recrie o container mantendo o mesmo volume. Containerize um script Node que consulta o banco. **Aceite:** explicar rede, volume, imagem e como destruir explicitamente os dados.

**Critério de conclusão:** Construa imagem reproduzível e explique imagem, container, volume e rede.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#2.2 — Sistema e operação|2.2]], [[Fase_7_Infra_Deploy_e_Cloud#32.1 — Automação|32.1]]

### 10.2 — Orquestração local

**Classificação:** `pratica` · `obrigatorio` · `alta` · #infra #ferramentas

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Descrever e iniciar uma aplicação local composta por serviços com Docker Compose.

**Tópicos:**
- [ ] docker compose
- [ ] serviços integrados
- [ ] containerizar projetos

**Atividade prática:** Escreva `compose.yaml` com PostgreSQL e Redis; acrescente MongoDB para o projeto da fase. Configure volume para dados persistentes, rede e portas necessárias ao host. **Aceite:** subir com um comando, testar conexão, parar e demonstrar persistência sem apagar o volume.

**Critério de conclusão:** Outra pessoa inicia os serviços com um comando e entende como preservar ou apagar os dados locais.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1]], [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2]]

---

## Módulo 11 — SQL e PostgreSQL

**Objetivo:** Criar um banco PostgreSQL, definir tabelas e executar operações básicas de escrita.

**Submódulos:** [[Fase_4_Dados_e_Bancos#11.3 — Ambiente PostgreSQL|11.3 Ambiente PostgreSQL]] · [[Fase_4_Dados_e_Bancos#11.1 — Consulta de dados|11.1 Consulta de dados]] · [[Fase_4_Dados_e_Bancos#11.2 — Relações|11.2 Relações]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 11.3 — Ambiente PostgreSQL

**Classificação:** `pratica` · `obrigatorio` · `media` · #dados #ferramentas

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Criar um banco PostgreSQL, definir tabelas e executar operações básicas de escrita.

**Tópicos:**
- [ ] instalação (nativa ou em container)
- [ ] criação de banco
- [ ] criação de tabelas
- [ ] inserção e atualização
- [ ] remoção de dados

**Atividade prática:** Crie banco de estudo e tabelas para clientes e pedidos, insira e altere dados de exemplo e salve o DDL num script. **Aceite:** ambiente recriado a partir dos arquivos e operações apontando as linhas pretendidas.

**Critério de conclusão:** Ambiente PostgreSQL funcional, recriável por script.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#11.1 — Consulta de dados|11.1]], [[Fase_4_Dados_e_Bancos#11.2 — Relações|11.2]], [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]]

### 11.1 — Consulta de dados

**Classificação:** `pratica` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Consultar dados com SELECT, WHERE, ORDER BY, LIMIT e aliases, prevendo o conjunto de resultados.

**Tópicos:**
- [ ] SELECT
- [ ] WHERE
- [ ] ORDER BY
- [ ] LIMIT
- [ ] aliases

**Atividade prática:** Responda perguntas sobre pedidos: pagos acima de um valor, mais recentes, e top 10 maiores valores. Inclua desempate determinístico. **Rubrica:** filtro correto, seleção adequada, ordenação explícita, limite aplicado depois da ordenação.

**Critério de conclusão:** Escreva consultas de filtro e ordenação para cenários novos e explique o resultado esperado.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#11.2 — Relações|11.2]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]]

### 11.2 — Relações

**Classificação:** `pratica` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Combinar tabelas e produzir agregações com JOIN, GROUP BY, HAVING e subqueries.

**Tópicos:**
- [ ] JOIN
- [ ] GROUP BY
- [ ] HAVING
- [ ] subqueries

**Atividade prática:** Gere relatório de vendas por cliente e mês usando pedidos e itens. Compare uma subquery com JOIN para selecionar clientes com compras. **Rubrica:** junção correta, totais não duplicados, agrupamento/filtros no estágio adequado, decisão explicada.

**Critério de conclusão:** Explique cada JOIN e compare uma subquery com equivalente em JOIN.

**Relações:** Revisita: [[Fase_4_Dados_e_Bancos#9.2 — Modelagem|9.2]]

---

## Módulo 12 — Performance, integridade e modelagem aplicada

**Objetivo:** Usar EXPLAIN e índices para avaliar consultas e comparar busca textual integrada com busca aproximada.

**Submódulos:** [[Fase_4_Dados_e_Bancos#12.1 — Performance e leitura|12.1 Performance e leitura]] · [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2 Integridade e operação]] · [[Fase_4_Dados_e_Bancos#12.3 — Modelagem aplicada|12.3 Modelagem aplicada]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 12.1 — Performance e leitura

**Classificação:** `solo` · `obrigatorio` · `media` · #dados #qualidade

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Usar EXPLAIN e índices para avaliar consultas e comparar busca textual integrada com busca aproximada.

**Tópicos:**
- [ ] índices
- [ ] EXPLAIN
- [ ] análise de consultas
- [ ] busca textual: tsvector, índice GIN e ranking
- [ ] busca aproximada com pg_trgm

**Atividade prática:** Meça busca de catálogo antes/depois de índice; registre plano, linhas, ambiente e limitações. Implemente busca textual com ranking e compare com busca aproximada/LIKE. **Rubrica:** hipótese, evidência reproduzível, índice justificado, trade-offs de produto discutidos.

**Critério de conclusão:** Justifique índice com plano e explique quando busca do PostgreSQL basta ou um motor dedicado merece avaliação.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]], [[Fase_6_Frontend_Moderno#30.1 — Otimização|30.1]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

### 12.2 — Integridade e operação

**Classificação:** `solo` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Preservar consistência em operações concorrentes e evoluir schema com transações, constraints e migrations.

**Tópicos:**
- [ ] transações
- [ ] níveis de isolamento e anomalias (leitura suja, não repetível e fantasma)
- [ ] locks de linha e SELECT ... FOR UPDATE
- [ ] locking otimista (coluna de versão)
- [ ] deadlock: o que é e como evitar (noção)
- [ ] constraints (incluindo UNIQUE composta e restrição de exclusão para conflito de intervalo)
- [ ] migrations
- [ ] backup e restore

**Atividade prática:** Demonstre concorrência numa reserva de estoque limitada e aplique migration aditiva. Explique isolamento, lock escolhido, conflito e recuperação. **Rubrica:** nunca saldo negativo; cenário concorrente reproduzível; migration rastreável; trade-off documentado.

**Critério de conclusão:** Explique isolamento, locks e locking otimista; evolua schema por migration e descreva teste de restore.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#9.3 — Integridade|9.3]], [[Fase_7_Infra_Deploy_e_Cloud#32.2 — Entrega|32.2]]

### 12.3 — Modelagem aplicada

**Classificação:** `integrado` · `obrigatorio` · `alta` · #dados

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Desenhar e justificar um modelo relacional completo para pedidos, itens, pagamentos e estoque.

**Tópicos:**
- [ ] modelar e-commerce
- [ ] relacionamentos reais
- [ ] consistência em cenários comuns

**Atividade prática:** Modele e-commerce com pedidos, itens, pagamentos e estoque. Entregue ERD e DDL; execute consultas de relatório e descreva a transação para venda de estoque. **Rubrica:** cardinalidades justificadas, histórico preservado, integridade expressa, relatórios sem duplicidade.

**Critério de conclusão:** Justifique chaves, cardinalidades e constraints do modelo completo e explique uma regra concorrente.

**Relações:** Revisita: [[Fase_4_Dados_e_Bancos#9.2 — Modelagem|9.2]], [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2]], [[Fase_4_Dados_e_Bancos#16.3 — Projeto de fase (Trilho B)|16.3]]

---

## Módulo 13 — Outros bancos relacionais

**Objetivo:** Reconhecer MySQL/MariaDB, Oracle Database e SQL Server e comparar dialetos sem presumir equivalência total.

**Submódulos:** [[Fase_4_Dados_e_Bancos#13.1 — Outros bancos relacionais|13.1 Outros bancos relacionais]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 13.1 — Outros bancos relacionais

**Classificação:** `solo` · `repertorio` · `repertorio` · #dados

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer MySQL/MariaDB, Oracle Database e SQL Server e comparar dialetos sem presumir equivalência total.

**Tópicos:**
- [ ] MySQL/MariaDB
- [ ] Oracle noções
- [ ] SQL Server noções

**Atividade prática:** Compare uma tabela e uma consulta simples em PostgreSQL e MySQL usando a documentação oficial. Registre uma diferença concreta confirmada e um ponto conceitualmente semelhante.

**Critério de conclusão:** Apontar diferenças de dialeto/recursos sem extrapolar compatibilidade.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#11.1 — Consulta de dados|11.1]]

---

## Módulo 14 — MongoDB e modelagem orientada a documentos

**Objetivo:** Modelar e consultar documentos e justificar quando o modelo documental atende melhor ao padrão de acesso.

**Submódulos:** [[Fase_4_Dados_e_Bancos#14.1 — MongoDB|14.1 MongoDB]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 14.1 — MongoDB

**Classificação:** `solo` · `obrigatorio` · `media` · #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Modelar e consultar documentos e justificar quando o modelo documental atende melhor ao padrão de acesso.

**Tópicos:**
- [ ] documentos
- [ ] coleções
- [ ] modelagem orientada a documento
- [ ] consultas básicas
- [ ] diferenças para modelo relacional

**Atividade prática:** Modele catálogo com atributos variáveis e consulte por categoria/estado. Compare embedding de especificações com referência a uma entidade compartilhada. **Rubrica:** consultas esperadas explícitas, crescimento limitado avaliado, trade-off fundamentado.

**Critério de conclusão:** Explique quando o modelo documental compensa e quando o relacional é mais adequado.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#9.2 — Modelagem|9.2]], [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]]

---

## Módulo 15 — Redis, cache e filas simples

**Objetivo:** Usar Redis como cache com TTL e invalidação explícita e reconhecer estruturas básicas e filas simples.

**Submódulos:** [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1 Redis]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 15.1 — Redis

**Classificação:** `solo` · `obrigatorio` · `media` · #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Usar Redis como cache com TTL e invalidação explícita e reconhecer estruturas básicas e filas simples.

**Tópicos:**
- [ ] cache
- [ ] TTL
- [ ] estruturas básicas
- [ ] uso como suporte de performance
- [ ] filas simples

**Atividade prática:** Cacheie consulta lenta com TTL; atualize origem e invalide a chave. Compare latência com dataset controlado e registre taxa de acerto, comportamento em miss e janela de desatualização. **Rubrica:** fonte de verdade clara, invalidation funcional, evidência, limite reconhecido.

**Critério de conclusão:** Explique cache como suporte, não fonte de verdade, e demonstre invalidação após escrita.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#28.2 — Gerência de dados|28.2]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]]

---

## Módulo 16 — Noções complementares e projeto de dados

**Objetivo:** Situar DynamoDB, Firestore e Elasticsearch por modelo e padrão de uso.

**Submódulos:** [[Fase_4_Dados_e_Bancos#16.1 — Noções complementares|16.1 Noções complementares]] · [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2 Projeto incremental da fase]] · [[Fase_4_Dados_e_Bancos#16.3 — Projeto de fase (Trilho B)|16.3 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 16.1 — Noções complementares

**Classificação:** `solo` · `repertorio` · `repertorio` · #dados

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Situar DynamoDB, Firestore e Elasticsearch por modelo e padrão de uso.

**Tópicos:**
- [ ] DynamoDB
- [ ] Firestore
- [ ] Elasticsearch

**Atividade prática:** Para cada sistema, associe um cenário e um requisito que poderia torná-lo inadequado; consulte a documentação do serviço escolhido.

**Critério de conclusão:** Explique quando cada opção complementar se justifica, citando uma limitação relevante.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#12.1 — Performance e leitura|12.1]]

### 16.2 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #dados

**Carga horária estimada:** 6 h–10 h (referência: 8 h).

**Objetivo:** Persistir o projeto principal escolhido na Fase 1 e integrar PostgreSQL, uma melhoria medida com Redis e um caso documental justificado.

**Tópicos:**
- [ ] persistir o projeto incremental em PostgreSQL com modelagem própria
- [ ] cache Redis em uma consulta lenta e uma coleção MongoDB
- [ ] PostgreSQL, Redis e MongoDB subindo com Docker Compose

**Atividade prática:** Implemente uma fatia vertical do projeto escolhido: persistência, endpoint/script de consulta, cache e coleção documental. Compare a mesma consulta quente/fria em condições anotadas. Não alegue ganho universal a partir de uma execução isolada.

**Critério de conclusão:** Projeto persistido, consulta medida, cache funcional e justificativa documental; ambientes sobem por Compose.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#10.2 — Orquestração local|10.2]], [[Fase_4_Dados_e_Bancos#12.3 — Modelagem aplicada|12.3]], [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1]]

### 16.3 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #dados

**Carga horária estimada:** 8 h–14 h (referência: 11 h).

**Objetivo:** Entregar uma fatia de modelagem relacional PostgreSQL da Fase 4, escolhendo uma ideia elegível do Trilho B.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Construa o menor conjunto de tabelas e dados que demonstre o tipo escolhido; execute migrações do zero; gere relatório e capture plano da consulta. Para T1, simule reservas concorrentes; para T2, tente leitura cruzada e horários conflitantes; para T5, processe CSV com registros válidos/inválidos e repetição controlada.

**Critério de conclusão:** Modelo relacional com migrations, relatórios e consulta medida com EXPLAIN, além de evidência reproduzível do problema difícil do tipo.

**Relações:** Complementar: [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2]], [[Fase_4_Dados_e_Bancos#12.2 — Integridade e operação|12.2]], [[Fase_4_Dados_e_Bancos#12.3 — Modelagem aplicada|12.3]]
