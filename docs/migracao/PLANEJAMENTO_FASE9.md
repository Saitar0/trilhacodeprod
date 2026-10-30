# Planejamento estrutural — Fase 9

Estado: rascunho para aprovação; sem geração da árvore.
Base: 2b906584f7e8b3d0b5e1cc84a21287d9e4ff57a6; branch migracao-estrutura.

## Decisões e escopo

- Aprovadas previamente: stacks implementáveis 42.1 Django/DRF, 43.1 Laravel, 44.1 ASP.NET Core, 45.1 Spring; 42.2, 42.3, 43.2 e 44.2 fora da escolha. 44.2 é legado; as duas unidades de noções são reconhecimento/repertório.
- 46.2: uma stack alternativa escolhida pelo estudante; 46.3 usa stack principal. A escolha concreta fica sem valor até o estudante decidir.
- Campo contextual nivel_dominio não substitui os metadados originais. Nenhum mapa histórico de assuntos foi encontrado no checkout; divisões e cobertura semântica abaixo são [PROPOSTA].
- Migração futura somente estrutural; expansões ficam em espera.

## Inventário de unidades

Foram comparados página oficial e pasta de fontes: 16/16 arquivos ativos em sete módulos. Metadados estão em listas sob H1, não em frontmatter YAML.

| Unidade | Módulo | Título original | tipo/caráter/profundidade | minutos; tags; status | linhas/palavras | teoria | Q | FC | P |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 40.1 | Mensageria na prática: RabbitMQ e Kafka | 40.1 — RabbitMQ | solo/obrigatorio/media | 90; #arquitetura, #infra, #mensageria; rascunho | 112/1917 | 4 | 5 | 0 | 3 |
| 40.2 | Mensageria na prática: RabbitMQ e Kafka | 40.2 — Kafka | solo/repertorio/repertorio | 45; #arquitetura, #infra, #mensageria; rascunho | 84/1288 | 3 | 0 | 3 | 2 |
| 40.3 | Mensageria na prática: RabbitMQ e Kafka | 40.3 — Comparação | integrado/obrigatorio/media | 90; #arquitetura; rascunho | 125/2113 | 4 | 5 | 0 | 3 |
| 41.1 | Arquitetura distribuída | 41.1 — Arquitetura distribuída | integrado/obrigatorio/media | 90; #arquitetura; rascunho | 129/2072 | 4 | 5 | 0 | 3 |
| 41.2 | Arquitetura distribuída | 41.2 — Regra dura | integrado/obrigatorio/media | 90; #arquitetura; rascunho | 126/1778 | 4 | 5 | 0 | 3 |
| 42.1 | Python e ecossistema web | 42.1 — Base: Python, Django e DRF | solo/repertorio/repertorio | 45; #mercado; rascunho | 107/1411 | 3 | 0 | 3 | 2 |
| 42.2 | Python e ecossistema web | 42.2 — Ecossistema Python | solo/repertorio/repertorio | 45; #mercado; rascunho | 96/1373 | 3 | 0 | 3 | 2 |
| 42.3 | Python e ecossistema web | 42.3 — Noções: FastAPI e Flask | solo/repertorio/repertorio | 45; #mercado; rascunho | 98/1466 | 3 | 0 | 3 | 2 |
| 43.1 | PHP e Laravel | 43.1 — Stack: PHP e Laravel | solo/repertorio/repertorio | 45; #mercado; rascunho | 96/1397 | 3 | 0 | 3 | 2 |
| 43.2 | PHP e Laravel | 43.2 — Noções: Slim e Phalcon | solo/repertorio/repertorio | 45; #mercado; rascunho | 99/1323 | 3 | 0 | 3 | 2 |
| 44.1 | C# e .NET | 44.1 — Stack: C# e .NET | solo/repertorio/repertorio | 45; #mercado; rascunho | 93/1374 | 3 | 0 | 3 | 2 |
| 44.2 | C# e .NET | 44.2 — Legado .NET: WebForms | solo/repertorio/repertorio | 45; #mercado; rascunho | 95/1561 | 3 | 0 | 3 | 2 |
| 45.1 | Java e Spring | 45.1 — Stack: Java e Spring | solo/repertorio/repertorio | 45; #mercado; rascunho | 75/1375 | 3 | 0 | 3 | 2 |
| 46.1 | Realidade de mercado e projeto da fase | 46.1 — Realidade de mercado | integrado/obrigatorio/media | 90; #mercado; rascunho | 84/1537 | 4 | 5 | 0 | 3 |
| 46.2 | Realidade de mercado e projeto da fase | 46.2 — Projeto incremental da fase | projeto/obrigatorio/alta | 900; #projeto; rascunho | 92/1465 | 0 | 0 | 0 | 0 |
| 46.3 | Realidade de mercado e projeto da fase | 46.3 — Projeto de fase (Trilho B) | projeto/obrigatorio/alta | 780; #projeto, #arquitetura; rascunho | 104/1633 | 0 | 0 | 0 | 0 |

Todos os 16 arquivos contêm os sete metadados. A transferência ao README mantém valores, sem preencher ou inferir campos.

## Assuntos e microtópicos

Cada assunto acompanha um cabeçalho de teoria. Os parágrafos introdutórios de 40.3 e 41.2 permanecem como contexto do assunto 01 correspondente; não são microtópicos adicionais. Divisões são propostas, não decisões históricas.

| Unidade | slug | título | origem literal |
|---|---|---|---|
| 40.1 | 01_exchange_binding_filas_consumers | Exchange, binding, filas e consumers | ### Microtópico 1 — Modelar exchange, binding, fila e consumer |
| 40.1 | 02_confirmacoes_ack_idempotencia | Confirmações, ack e idempotência | ### Microtópico 2 — Separar confirmação da publicação e confirmação do consumo |
| 40.1 | 03_prefetch_trabalho_em_voo | Prefetch e trabalho em voo | ### Microtópico 3 — Controlar trabalho em voo com ack manual e prefetch |
| 40.1 | 04_dead_letter_recuperacao | Dead-letter e recuperação de mensagens | ### Microtópico 4 — Projetar dead-letter e recuperação de mensagens |
| 40.2 | 01_log_particionado_ordem | Tópicos como log particionado e ordenação | ### Microtópico 1 — Ler um tópico como log particionado |
| 40.2 | 02_grupos_particoes_consumidores | Grupos e distribuição de consumidores | ### Microtópico 2 — Distribuir consumidores por grupos |
| 40.2 | 03_offsets_retencao_replay | Offsets, retenção e replay | ### Microtópico 3 — Usar offsets, retenção e replay corretamente |
| 40.3 | 01_modelar_problema_antes_escolha | Modelar o problema antes da escolha | ### 1. Modele o problema antes de escolher |
| 40.3 | 02_entrega_falhas_duplicatas | Entrega, falhas e duplicatas | ### 2. Entrega, falhas e duplicatas |
| 40.3 | 03_ordem_escala_replay | Ordem, escala e replay | ### 3. Ordem, escala e replay |
| 40.3 | 04_operacao_custo_decisao | Operação, custo e decisão defensável | ### 4. Operação, custo e decisão defensável |
| 41.1 | 01_fronteiras_orcamento_latencia | Fronteiras de serviço e orçamento de latência | ### 1. Fronteiras de serviço e orçamento de latência |
| 41.1 | 02_timeout_retry_circuit_breaker | Timeout, retry e circuit breaker | ### 2. Timeout, retry e circuit breaker |
| 41.1 | 03_consistencia_saga_compensacao | Consistência eventual, saga e compensação | ### 3. Consistência eventual, saga e compensação |
| 41.1 | 04_outbox_entrega_operacao | Outbox, entrega e operação observável | ### 4. Outbox, entrega e operação observável |
| 41.2 | 01_beneficio_fronteira | Benefício que justifica a fronteira | ### 1. Benefício que justifica a fronteira; parágrafo introdutório preservado como contexto no assunto 01 |
| 41.2 | 02_custo_prontidao_operacional | Custo total e prontidão operacional | ### 2. Custo total e prontidão operacional |
| 41.2 | 03_descoberta_teste_fronteira | Descoberta e teste da fronteira | ### 3. Descubra e teste a fronteira |
| 41.2 | 04_extracao_incremental_reversao | Extração incremental, reversão e decisão | ### 4. Extração incremental, reversão e decisão |
| 42.1 | 01_python_projeto_app_django | Python, projeto e app Django | ### 1. Python, projeto e app Django |
| 42.1 | 02_ciclo_url_modelo | Do URL ao modelo: ciclo Django | ### 2. Do URL ao modelo: ciclo Django |
| 42.1 | 03_drf_serializacao_views_acesso | DRF: serialização, views e controle de acesso | ### 3. DRF: serialização, views e controle de acesso |
| 42.2 | 01_celery_tarefas_fora_requisicao | Celery: tarefas fora da requisição | ### 1. Celery: tarefas fora da requisição |
| 42.2 | 02_pytest_fixtures_integracao | pytest: testes, fixtures e níveis de integração | ### 2. pytest: testes, fixtures e níveis de integração |
| 42.2 | 03_poetry_dependencias_distribuicao | Poetry: dependências e distribuição | ### 3. Poetry: dependências e distribuição |
| 42.3 | 01_api_validacao_documentacao | API, validação e documentação | ### 1. API, validação e documentação |
| 42.3 | 02_convencoes_composicao_custo | Convenções, composição e custo de equipe | ### 2. Convenções, composição e custo de equipe |
| 42.3 | 03_sync_async_operacao | Síncrono, async e operação | ### 3. Síncrono, async e operação |
| 43.1 | 01_php_composer_versoes | PHP, Composer e versões | ### 1. PHP, Composer e versões |
| 43.1 | 02_ciclo_requisicao_laravel | Ciclo de requisição no Laravel | ### 2. Ciclo de requisição no Laravel |
| 43.1 | 03_filas_decisao_stack | Filas e decisão de stack | ### 3. Filas e decisão de stack |
| 43.2 | 01_slim_http_composicao | Slim: HTTP e composição de componentes | ### 1. Slim: HTTP e composição de componentes |
| 43.2 | 02_phalcon_versao_distribuicao | Phalcon: versão e forma de distribuição | ### 2. Phalcon: versão e forma de distribuição |
| 43.2 | 03_comparacao_trabalho_completo | Comparação com Laravel pelo trabalho completo | ### 3. Compare com Laravel pelo trabalho completo |
| 44.1 | 01_csharp_sdk_pipeline_api | C#, SDK e pipeline de API | ### 1. C#, SDK e pipeline de API |
| 44.1 | 02_injecao_dependencia_persistencia | Injeção de dependência e persistência | ### 2. Injeção de dependência e persistência |
| 44.1 | 03_testes_suporte_producao | Testes, suporte e produção | ### 3. Testes, suporte e produção |
| 44.2 | 01_pagina_postback_ciclo_vida | Página server-side, postback e ciclo de vida | ### 1. Página server-side, postback e ciclo de vida |
| 44.2 | 02_controles_viewstate_codebehind | Controles server-side, ViewState e code-behind | ### 2. Controles server-side, ViewState e code-behind |
| 44.2 | 03_manutencao_suporte_modernizacao | Manutenção, suporte e modernização | ### 3. Manutenção, suporte e modernização |
| 45.1 | 01_java_spring_caminho_requisicao | Java, Spring e o caminho de uma requisição | ### 1. Java, Spring e o caminho de uma requisição |
| 45.1 | 02_persistencia_jpa_consultas | Persistência: especificação, implementação e consultas | ### 2. Persistência: especificação, implementação e consultas |
| 45.1 | 03_testes_integracao_kafka | Testes e integração com Kafka | ### 3. Testes e integração com Kafka |
| 46.1 | 01_vaga_fonte_de_sinais | Ler uma vaga como fonte de sinais | ### 1. Ler uma vaga como fonte de sinais, não como currículo universal |
| 46.1 | 02_requisitos_evidencias_honestas | Transformar requisitos em evidências honestas | ### 2. Transformar requisitos em evidências honestas |
| 46.1 | 03_projeto_portfolio_escopo | Projeto de portfólio com escopo defensável | ### 3. Escolher um projeto de portfólio com escopo defensável |
| 46.1 | 04_modernizar_ou_otimizar | Decidir quando modernizar e quando otimizar | ### 4. Decidir quando modernizar e quando otimizar |

Total: 47 assuntos convencionais; 46.2 e 46.3 são contêineres de projeto, sem assuntos fictícios.

**E/S/N global recalculado:** 38 / 9 / 0 — 38 assuntos com item exclusivo, nove apenas compartilhados e zero sem verificação. A soma deriva das 47 linhas por unidade; o 38/10/0 informado anteriormente foi erro no total apresentado, não divergência do manifesto.

## Cobertura item a item

E = exclusivo; S = compartilhado entre os slugs indicados e com um único destino em 90_integracao; S-only = só tem itens compartilhados; N = sem item. Q, prática e flashcard são tratados como tipos distintos. Classificação [PROPOSTA] segundo enunciado; item integrador não substitui cobertura exclusiva.

### 40.1

- Q01 exclusiva → 01_exchange_binding_filas_consumers; origem ## Quiz, item 1; resposta inline.
- Q02 exclusiva → 02_confirmacoes_ack_idempotencia; origem ## Quiz, item 2; resposta inline.
- Q03 exclusiva → 02_confirmacoes_ack_idempotencia; origem ## Quiz, item 3; pergunta sobre falha antes do ack, redelivery e idempotência. Não exige dead-letter, portanto não cobre o assunto 04.
- Q04 exclusiva → 03_prefetch_trabalho_em_voo; origem ## Quiz, item 4; resposta inline.
- Q05 exclusiva → 04_dead_letter_recuperacao; origem ## Quiz, item 5; resposta inline.
- P01 Atividade 1 — Desenhar e provar o roteamento: exclusiva → 01_exchange_binding_filas_consumers; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Exercitar publicação, consumo, ack e idempotência: compartilhada → 01_exchange_binding_filas_consumers, 02_confirmacoes_ack_idempotencia, 03_prefetch_trabalho_em_voo; feedback existente=True; rubrica prática existente=False.
- P03 Atividade 3 — Definir retry, DLQ e triagem: compartilhada → 02_confirmacoes_ack_idempotencia, 04_dead_letter_recuperacao; feedback existente=True; rubrica prática existente=False.
E/S/N=4/0/0.

### 40.2

- P01 Atividade 1 — Distribuir partições e prever ordenação: compartilhada → 01_log_particionado_ordem, 02_grupos_particoes_consumidores; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Analisar commit, replay e retenção: exclusiva → 03_offsets_retencao_replay; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_log_particionado_ordem; frente: Kafka garante ordem global de um topic com várias partições?.
- FC02 exclusivo → 02_grupos_particoes_consumidores; frente: Quatro consumers num grupo lendo um tópico de três partições aumentam o paralelismo ativo para quatro?.
- FC03 exclusivo → 03_offsets_retencao_replay; frente: Commit de offset apaga a mensagem ou evita duplicar efeito no banco?.
E/S/N=3/0/0.

### 40.3

- Q01 exclusiva → 03_ordem_escala_replay; origem ## Verificação, item 1; resposta inline.
- Q02 compartilhada → 01_modelar_problema_antes_escolha, 04_operacao_custo_decisao; origem ## Verificação, item 2; resposta inline.
- Q03 exclusiva → 02_entrega_falhas_duplicatas; origem ## Verificação, item 3; resposta inline.
- Q04 exclusiva → 03_ordem_escala_replay; origem ## Verificação, item 4; resposta inline.
- Q05 exclusiva → 04_operacao_custo_decisao; origem ## Verificação, item 5; resposta inline.
- P01 Atividade 1 — Matriz de decisão para três cenários: compartilhada → 01_modelar_problema_antes_escolha, 02_entrega_falhas_duplicatas, 03_ordem_escala_replay, 04_operacao_custo_decisao; feedback existente=False; rubrica prática existente=True.
- P02 Atividade 2 — Rastreie a falha e proponha recuperação: compartilhada → 02_entrega_falhas_duplicatas, 03_ordem_escala_replay, 04_operacao_custo_decisao; feedback existente=False; rubrica prática existente=True.
- P03 Atividade 3 — Recomendação operacional e econômica: compartilhada → 01_modelar_problema_antes_escolha, 02_entrega_falhas_duplicatas, 03_ordem_escala_replay, 04_operacao_custo_decisao; feedback existente=False; rubrica prática existente=True.
E/S/N=3/1/0.

### 41.1

- Q01 exclusiva → 02_timeout_retry_circuit_breaker; origem ## Quiz, item 1; resposta inline.
- Q02 exclusiva → 02_timeout_retry_circuit_breaker; origem ## Quiz, item 2; resposta inline.
- Q03 exclusiva → 02_timeout_retry_circuit_breaker; origem ## Quiz, item 3; resposta inline.
- Q04 exclusiva → 03_consistencia_saga_compensacao; origem ## Quiz, item 4; resposta inline.
- Q05 exclusiva → 04_outbox_entrega_operacao; origem ## Quiz, item 5; resposta inline.
- P01 Atividade 1 — Escolha síncrono ou assíncrono: compartilhada → 01_fronteiras_orcamento_latencia, 02_timeout_retry_circuit_breaker; feedback existente=False; rubrica prática existente=True.
- P02 Atividade 2 — Desenhe a política de resiliência: compartilhada → 01_fronteiras_orcamento_latencia, 02_timeout_retry_circuit_breaker; feedback existente=False; rubrica prática existente=True.
- P03 Atividade 3 — Saga e outbox sob falha: compartilhada → 03_consistencia_saga_compensacao, 04_outbox_entrega_operacao; feedback existente=False; rubrica prática existente=True.
E/S/N=3/1/0.

### 41.2

- Q01 exclusiva → 01_beneficio_fronteira; origem ## Verificação, item 1; resposta inline.
- Q02 exclusiva → 03_descoberta_teste_fronteira; origem ## Verificação, item 2; resposta inline.
- Q03 exclusiva → 01_beneficio_fronteira; origem ## Verificação, item 3; resposta inline.
- Q04 exclusiva → 02_custo_prontidao_operacional; origem ## Verificação, item 4; resposta inline.
- Q05 exclusiva → 04_extracao_incremental_reversao; origem ## Verificação, item 5; resposta inline.
- P01 Atividade 1 — ADR: manter, preparar ou extrair: compartilhada → 01_beneficio_fronteira, 02_custo_prontidao_operacional, 03_descoberta_teste_fronteira, 04_extracao_incremental_reversao; feedback existente=False; rubrica prática existente=True.
- P02 Atividade 2 — Mapa de dependências e prontidão: compartilhada → 02_custo_prontidao_operacional, 03_descoberta_teste_fronteira; feedback existente=False; rubrica prática existente=True.
- P03 Atividade 3 — Plano de extração gradual e reversão: compartilhada → 02_custo_prontidao_operacional, 04_extracao_incremental_reversao; feedback existente=False; rubrica prática existente=True.
E/S/N=4/0/0.

### 42.1

- P01 Atividade 1 — Siga uma requisição até a resposta: compartilhada → 02_ciclo_url_modelo, 03_drf_serializacao_views_acesso; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Revise o isolamento entre usuários: exclusiva → 03_drf_serializacao_views_acesso; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_python_projeto_app_django; frente: O que distingue project de app no Django?.
- FC02 exclusivo → 03_drf_serializacao_views_acesso; frente: Serializer do DRF controla autorização?.
- FC03 exclusivo → 01_python_projeto_app_django; frente: `runserver` pode ser usado como servidor de produção?.
E/S/N=2/1/0.

### 42.2

- P01 Atividade 1 — Escolha a ferramenta proporcional: compartilhada → 01_celery_tarefas_fora_requisicao, 02_pytest_fixtures_integracao, 03_poetry_dependencias_distribuicao; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Revise retry, teste e dependências: compartilhada → 01_celery_tarefas_fora_requisicao, 02_pytest_fixtures_integracao, 03_poetry_dependencias_distribuicao; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_celery_tarefas_fora_requisicao; frente: O que o broker e o result backend fazem no Celery?.
- FC02 exclusivo → 02_pytest_fixtures_integracao; frente: Uma fixture pytest é o quê?.
- FC03 exclusivo → 03_poetry_dependencias_distribuicao; frente: Poetry substitui Python ou fixa a instalação de quem consome uma biblioteca?.
E/S/N=3/0/0.

### 42.3

- P01 Atividade 1 — Matriz de escolha de framework: compartilhada → 01_api_validacao_documentacao, 02_convencoes_composicao_custo, 03_sync_async_operacao; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Revise uma afirmação sobre async: compartilhada → 02_convencoes_composicao_custo, 03_sync_async_operacao; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_api_validacao_documentacao; frente: Qual papel de FastAPI em APIs?.
- FC02 exclusivo → 02_convencoes_composicao_custo; frente: Flask inclui ORM obrigatório?.
- FC03 exclusivo → 03_sync_async_operacao; frente: `async def` no Flask aumenta automaticamente o número de requisições simultâneas por worker?.
E/S/N=3/0/0.

### 43.1

- P01 Atividade 1 — Trace uma requisição Laravel: compartilhada → 01_php_composer_versoes, 02_ciclo_requisicao_laravel; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Revisão de risco em Eloquent e fila: compartilhada → 02_ciclo_requisicao_laravel, 03_filas_decisao_stack; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_php_composer_versoes; frente: Composer substitui o runtime PHP?.
- FC02 exclusivo → 02_ciclo_requisicao_laravel; frente: O que Eloquent oferece e o que continua exigindo atenção?.
- FC03 compartilhado → 02_ciclo_requisicao_laravel, 03_filas_decisao_stack; frente: Login ou queue garante autorização e ausência de duplicatas?.
E/S/N=2/1/0.

### 43.2

- P01 Atividade 1 — Compare a composição de uma API: compartilhada → 01_slim_http_composicao, 03_comparacao_trabalho_completo; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Identifique versão e risco de implantação Phalcon: exclusiva → 02_phalcon_versao_distribuicao; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_slim_http_composicao; frente: Slim inclui ORM obrigatório?.
- FC02 exclusivo → 01_slim_http_composicao; frente: O que PSR-7 representa em Slim?.
- FC03 exclusivo → 02_phalcon_versao_distribuicao; frente: Phalcon 5 e 6 são instalados da mesma forma?.
E/S/N=2/1/0.

### 44.1

- P01 Atividade 1 — Trace endpoint e ciclo de vida: compartilhada → 01_csharp_sdk_pipeline_api, 02_injecao_dependencia_persistencia; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Escolha persistência e revise migração: compartilhada → 02_injecao_dependencia_persistencia, 03_testes_suporte_producao; feedback existente=True; rubrica prática existente=False.
- FC01 compartilhado → 02_injecao_dependencia_persistencia, 03_testes_suporte_producao; frente: Uma migration EF Core deve ser aplicada em produção sem revisão?.
- FC02 exclusivo → 02_injecao_dependencia_persistencia; frente: Dapper elimina SQL?.
- FC03 exclusivo → 02_injecao_dependencia_persistencia; frente: Um singleton pode depender diretamente de serviço scoped, como DbContext?.
E/S/N=1/2/0.

### 44.2

- P01 Atividade 1 — Leia o ciclo de uma página: compartilhada → 01_pagina_postback_ciclo_vida, 02_controles_viewstate_codebehind; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Avalie um legado e proponha próximo passo: compartilhada → 02_controles_viewstate_codebehind, 03_manutencao_suporte_modernizacao; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 01_pagina_postback_ciclo_vida; frente: O que `IsPostBack` indica?.
- FC02 exclusivo → 02_controles_viewstate_codebehind; frente: Onde fica normalmente o ViewState e qual custo observar?.
- FC03 exclusivo → 03_manutencao_suporte_modernizacao; frente: WebForms é apenas ASP.NET Core com outra sintaxe?.
E/S/N=3/0/0.

### 45.1

- P01 Atividade 1 — Rastrear um endpoint: compartilhada → 01_java_spring_caminho_requisicao, 02_persistencia_jpa_consultas; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Escolher testes e proteger o consumo: compartilhada → 02_persistencia_jpa_consultas, 03_testes_integracao_kafka; feedback existente=True; rubrica prática existente=False.
- FC01 exclusivo → 02_persistencia_jpa_consultas; frente: JPA é um ORM específico?.
- FC02 exclusivo → 02_persistencia_jpa_consultas; frente: Spring Data repository elimina a necessidade de entender SQL?.
- FC03 exclusivo → 03_testes_integracao_kafka; frente: Confirmar o offset do Kafka garante que banco e negócio ocorreram exatamente uma vez?.
E/S/N=2/1/0.

### 46.1

- Q01 exclusiva → 01_vaga_fonte_de_sinais; origem ## Quiz, item 1; resposta inline.
- Q02 exclusiva → 02_requisitos_evidencias_honestas; origem ## Quiz, item 2; resposta inline.
- Q03 exclusiva → 02_requisitos_evidencias_honestas; origem ## Quiz, item 3; resposta inline.
- Q04 exclusiva → 04_modernizar_ou_otimizar; origem ## Quiz, item 4; resposta inline.
- Q05 exclusiva → 04_modernizar_ou_otimizar; origem ## Quiz, item 5; resposta inline.
- P01 Atividade 1 — Desmontar uma vaga: compartilhada → 01_vaga_fonte_de_sinais, 02_requisitos_evidencias_honestas; feedback existente=True; rubrica prática existente=False.
- P02 Atividade 2 — Ligar lacunas a evidências de portfólio: compartilhada → 02_requisitos_evidencias_honestas, 03_projeto_portfolio_escopo; feedback existente=True; rubrica prática existente=False.
- P03 Atividade 3 — Defender uma decisão de modernização: exclusiva → 04_modernizar_ou_otimizar; feedback existente=True; rubrica prática existente=False.
E/S/N=3/1/0.

### Assuntos sem avaliação exclusiva

Lacunas ficam como proposta; nenhum exercício é criado.

| unidade | slug | hoje | proposta |
|---|---|---|---|
| 40.3 | 01_modelar_problema_antes_escolha | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 41.1 | 01_fronteiras_orcamento_latencia | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 42.1 | 02_ciclo_url_modelo | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 43.1 | 03_filas_decisao_stack | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 43.2 | 03_comparacao_trabalho_completo | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 44.1 | 01_csharp_sdk_pipeline_api | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 44.1 | 03_testes_suporte_producao | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 45.1 | 01_java_spring_caminho_requisicao | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |
| 46.1 | 03_projeto_portfolio_escopo | S-only | [PROPOSTA EM ESPERA] avaliar verificação própria; não criar na migração. |

Na leitura atual, 43.1/02 tem FC02 específico sobre Eloquent e é exclusivo; portanto, uma expansão antiga para 43.1/02 não se confirma. 43.1/03 permanece S-only: FC03 e P02 combinam fila/autorização/Eloquent. Não se escreve conteúdo.

## Projetos

| unidade | objetivo existente (síntese) | entregas e aceites | rubrica | stack/dependências |
|---|---|---|---|---|
| 46.2 | Evoluir o Trilho A em quatro entregas revisáveis: definir um contrato e um limite de serviço; publicar eventos com confiabilidade; consumir com retry limitado, DLQ e idempotência; e concluir um serviço adicional via mensageria com observabilidade e comparação documentada de stack. | M01 ### Entrega 1 — Fluxo, contrato e ambiente local<br>M02 ### Entrega 2 — Publicação confiável e rastreável<br>M03 ### Entrega 3 — Consumidor resiliente, retry e DLQ<br>M04 ### Entrega 4 — Serviço adicional, observabilidade e comparação; quatro blocos de aceite | seis dimensões, 0–2 cada, total 12 | Trilho A e stack principal preservada; entrega 4 escolhe uma alternativa das quatro stacks aprovadas. |
| 46.3 | Escolher, segundo a rotação do curso, um tipo de projeto ainda pendente (ou aprofundamento livre quando T1–T5 já estiverem concluídos) e demonstrar sua regra técnica central em uma fatia local autocontida, com base mínima, fila, retry limitado, DLQ, idempotência e ADR. | M01 ### Entrega 1 — Escolha, hipótese e contrato<br>M02 ### Entrega 2 — Base executável e fluxo normal<br>M03 ### Entrega 3 — Falhas, retry, DLQ e idempotência<br>M04 ### Entrega 4 — Prova do tipo, revisão e cobertura; quatro blocos de aceite | seis dimensões, 0–2 cada, total 12 | Trilho B e escolha de tipo conforme Guia; stack_mode principal. |

Arquivos planos M01–M04 com titulo_marco literal; C01–C04 com os aceites existentes; R00 com rubrica existente. Sem checklist final adicional. T1–T5 segue dentro do bloco de opções de 46.3.

## Duplicações e fronteiras

| relação | fonte canônica | fronteira Fase 9 |
|---|---|---|
| 40.x ↔ F7 33.1/35.1 | 33.1 fundamentos mensageria; 35.1 serviços/events cloud | F9 especifica RabbitMQ, Kafka, cenários e comparação; não duplica fundamentos gerais. |
| 41.x ↔ F7 35.1 e F8 38.x/39.x | 35.1 integrações; 38.1/38.2 observabilidade; 39.1 operação madura | F9 41.1 padrões distribuídos; 41.2 limites/custo; referenciar telemetria sem recopiá-la. |
| 42.x–45.1 ↔ F5/F6 | F5 18.1–20.x e unidades canônicas de API/testes das Fases 5–6 | F9 apresenta equivalências específicas; REST, ORM, auth e testes base continuam nas fases anteriores. |
| 46.2/46.3 ↔ projetos anteriores | cada projeto tem seu brief/rubrica | 46.2 Trilho A; 46.3 Trilho B; sem copiar critérios anteriores. |

Relações literais e wikilinks de cada unidade estão registrados no manifesto.

## Referências que envelhecem

consultado_em é por referência, nunca global; as fontes atuais registram principalmente 15/10/2026. Links sem data ficam sem data.

- Revalidar preços/drivers SQS, Pub/Sub, MSK; variam por região, configuração e uso, sem tarifa numérica fixa a migrar.
- Revalidar versões/suporte nomeados: Kafka 4.2; RabbitMQ, DLX e quorum queues; PHP 7.4 legado, Laravel 13/PHP 8.3+; Phalcon 5.18/6.0/PHP 8.1+; .NET 8/9/10 e janelas; Django 6.1; Java 25/Spring.
- APIs/documentação oficial, limites, compatibilidade e suporte podem mudar. Não atualizar durante migração; revisão editorial futura registra data por fonte.
- Não há nomes de modelos de IA nem endpoints de IA nas fontes; o conteúdo volátil aqui é framework, serviços, versão e preços.

## Links

- Preservar wikilinks literalmente; vault Obsidian não confirmado.
- Normalização estrutural proposta para três links: alvo do guia conferido; preservar texto visível. O destino migrado fica registrado no manifesto.

| unidade | linha fonte | seção | arquivo destino | href relativo |
|---|---:|---|---|---|
| 46.2 | 92 | ## Referências | `docs/courses/trilhacode/Conteudos_migrado/Fase_9/46.2_Projeto_incremental_da_fase/05_referencias.md` | `../../../Guia_Projetos_e_Rotacao_de_Tipos.md` |
| 46.3 | 15 | ## Regras de escolha e escopo | `docs/courses/trilhacode/Conteudos_migrado/Fase_9/46.3_Projeto_de_fase_Trilho_B/01_escopo_regras.md` | `../../../Guia_Projetos_e_Rotacao_de_Tipos.md` |
| 46.3 | 100 | ## Referências | `docs/courses/trilhacode/Conteudos_migrado/Fase_9/46.3_Projeto_de_fase_Trilho_B/05_referencias.md` | `../../../Guia_Projetos_e_Rotacao_de_Tipos.md` |

Os três links acima já existem nas fontes originais e apontam para `Guia_Projetos_e_Rotacao_de_Tipos.md`, arquivo rastreado presente em `HEAD` e disponível em checkout limpo. Não apontam para `Guia_de_Producao_de_Conteudo.md`, que está local e não rastreado; a árvore proposta não depende desse arquivo. As referências ao guia local em 46.2 e 46.3 não têm `consultado_em` na fonte; o campo permanece ausente, sem inferir uma data.

## Estimativa de arquivos por unidade

| unidade | assuntos/projeto | Q | K | arquivos FC (cards) | P | KP | rubricas | marcos | aceites | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 40.1 | 4 | 5 | 5 | 0 (0) | 3 | 3 | 0 | 0 | 0 | 26 |
| 40.2 | 3 | 0 | 0 | 3 (3) | 2 | 2 | 0 | 0 | 0 | 16 |
| 40.3 | 4 | 5 | 5 | 0 (0) | 3 | 0 | 3 | 0 | 0 | 26 |
| 41.1 | 4 | 5 | 5 | 0 (0) | 3 | 0 | 3 | 0 | 0 | 26 |
| 41.2 | 4 | 5 | 5 | 0 (0) | 3 | 0 | 3 | 0 | 0 | 26 |
| 42.1 | 3 | 0 | 0 | 2 (3) | 2 | 2 | 0 | 0 | 0 | 15 |
| 42.2 | 3 | 0 | 0 | 3 (3) | 2 | 2 | 0 | 0 | 0 | 16 |
| 42.3 | 3 | 0 | 0 | 3 (3) | 2 | 2 | 0 | 0 | 0 | 16 |
| 43.1 | 3 | 0 | 0 | 3 (3) | 2 | 2 | 0 | 0 | 0 | 16 |
| 43.2 | 3 | 0 | 0 | 2 (3) | 2 | 2 | 0 | 0 | 0 | 15 |
| 44.1 | 3 | 0 | 0 | 2 (3) | 2 | 2 | 0 | 0 | 0 | 15 |
| 44.2 | 3 | 0 | 0 | 3 (3) | 2 | 2 | 0 | 0 | 0 | 16 |
| 45.1 | 3 | 0 | 0 | 2 (3) | 2 | 2 | 0 | 0 | 0 | 15 |
| 46.1 | 4 | 5 | 5 | 0 (0) | 3 | 3 | 0 | 0 | 0 | 26 |
| 46.2 | projeto | 0 | 0 | 0 (0) | 0 | 0 | 1 | 4 | 4 | 15 |
| 46.3 | projeto | 0 | 0 | 0 (0) | 0 | 0 | 1 | 4 | 4 | 16 |

### Total por tipo

| tipo | arquivos |
|---|---:|
| topic_index | 16 |
| objetivo | 16 |
| resumo | 16 |
| criterio | 15 |
| conexoes | 16 |
| referencias | 16 |
| theory | 47 |
| quiz | 25 |
| answer_key | 25 |
| practice | 33 |
| answer_key_pratica | 24 |
| flashcards | 23 |
| rubric | 11 |
| project_scope | 2 |
| project_milestone | 8 |
| checklist | 8 |
| **Total** | **301** |

Estimativa: 301 arquivos, sem arquivos artificiais: 47 theory, 25 quiz + 25 answer_key, 27 cartões agrupados em 23 arquivos, 33 practice, 24 KP de feedback/solução já existente, 9 rubricas de prática e 2 de projeto, 8 milestones, 8 checklists, 16 índices e arquivos comuns/scope. Arquivos comuns e integração sem assuntos fictícios.

## Validação do rascunho

- 16 fontes, 47 assuntos, 25 Q/respostas, 27 flashcards, 33 práticas, 11 rubricas totais, 8 entregas e 8 aceites.
- Parser YAML passou; 301 caminhos e 301 IDs f9 únicos; sem colisões com os 2.285 IDs únicos lidos dos frontmatters efetivamente gerados nas árvores F1–F8. Origens, aliases e slugs validados.
- Itens compartilhados têm associação explícita e destino único; respostas permanecem ligadas à Q; rubricas/checklists têm origem.
- Arquivos 46.2/46.3 mantêm quatro entregas e aceites, escalas originais; sem 8.4/8.x extra.
- Nenhuma árvore, JSON, fonte, fase homologada, importador ou commit foi alterado.

## Decisões para a revisão

1. Aprovar slugs e agrupamentos [PROPOSTA], incluindo itens S-only.
2. Confirmar split de feedback existente em KP, sem alterar texto.
3. Deixar escolha concreta de stack de 46.2/46.3 para o estudante.
4. Revalidar referências e versões antes da publicação, com data individual por fonte.
