# Planejamento da migração estrutural — Fase 5

**Estado:** rascunho para aprovação. **Base:** `36247635f007de44deb064573101a09a6ac10a7c`. **Árvore migrada:** não gerada.

## Diagnóstico

- Fontes: página da Fase 5, referências gerais e 20 arquivos ativos de conteúdo. Não há manifesto decisório da Fase 5 no checkout; por isso todas as divisões de assunto abaixo são [PROPOSTA], não decisões históricas aprovadas.
- Ordem dos IDs preservada: 17.1–24.4. A página sugere 24.1 antecipada entre 18.2 e 19.1; não alterar a página original.
- Pré-requisitos originais: Fase 3 (JavaScript/TypeScript/Node/npm) e Fase 4 (dados/Docker).
- A página prevê 45–79 h, referência 62 h; soma dos metadados = 3.720 minutos = 62 h. Preservar ambas as informações.
- 18 unidades convencionais: 81 microtópicos, 90 questões com respostas/feedbacks e 54 práticas com soluções e rubricas. Não há flashcards.
- Na reconstrução de cobertura, 88 questões e 36 práticas são exclusivas; 2 questões e 18 práticas são compartilhadas e terão um destino físico por item. As 21 associações adicionais das práticas de integração são referências de cobertura, não cópias.
- Exceção de formato: em 19.1, Q1–Q5 colocam enunciado e resposta na mesma linha sem rótulo de resposta. O manifesto delimita cada pergunta pelo trecho em negrito e mantém o texto restante no gabarito; a futura geração deve seguir esses limites literais.
- As 54 rubricas práticas preservam 24 escalas 0–2 e 30 rubricas descritivas; projetos 24.3 e 24.4 têm rubricas originais 0–4.
- Metadados das 20 fontes estão em listas Markdown, não em frontmatter. Copiá-los sem alteração ao README de cada unidade. Referências individuais permanecem; documentos gerais da fase ficam intactos.

## Divisão, cobertura e destino por unidade

Os microtópicos e atividades abaixo são identificados pelos títulos e limites existentes. Cada Q/P terá um destino físico; itens compartilhados ficam em `90_integracao/`, e os gabaritos, soluções e rubricas existentes são separados.

### 17.1 — Fundamentos

- **Módulo:** Node.js e execução no servidor. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/17.1_Fundamentos.md`. **Arquivos previstos:** 25.
- **Metadados originais:** `key=17.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=180`, `tags=['#fundamentos']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_runtime_event_loop_workers` | 1. Runtime Node.js e responsabilidades; 2. Event loop e concorrência de I/O; 4. CPU-bound, I/O e workers | Q1, Q2 | — | P1 | — |
| `02_promises_async_await` | 3. Promises e async/await | Q3 | — | — | — |
| `03_streams_backpressure_csv` | 5. Streams e backpressure | Q4, Q5 | — | P2 | — |
| `04_modulos_package_scripts` | 6. Módulos, package.json e scripts | — | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_runtime_event_loop_workers` — Uma rota aguarda uma consulta assíncrona ao banco. Enquanto aguarda, o que pode acontecer no processo? (origem linhas 52–55; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_runtime_event_loop_workers` — Uma função JavaScript síncrona leva vários segundos para processar um arquivo. O que pode ocorrer em um servidor Node? (origem linhas 56–59; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_promises_async_await` — await em uma Promise cria um novo thread? (origem linhas 60–63; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_streams_backpressure_csv` — Por que um pipeline de streams pode processar um arquivo grande usando menos memória que ler tudo e depois processar? (origem linhas 64–67; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_streams_backpressure_csv` — Um programa lê CSV por chunks e separa cada chunk por vírgula para montar registros. Qual é o risco? (origem linhas 68–71; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_runtime_event_loop_workers` — Classificar caminhos de execução (linhas 74–82; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `03_streams_backpressure_csv` — Processar arquivo grande com stream (linhas 83–91; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `04_modulos_package_scripts` — Declarar módulos e scripts do projeto (linhas 92–100; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Revisita 7.3 — JavaScript assíncrono. Jobs e streams reaparecem no T5 (24.4) e em operação (33.1).

### 17.2 — Depuração no servidor

- **Módulo:** Node.js e execução no servidor. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/17.2_Depuracao_no_servidor.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=17.2`, `tipo=pratica`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=120`, `tags=['#ferramentas', '#qualidade']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_reproducao_e_inspector` | 1. Reproduzir antes de alterar; 2. Inspector e breakpoints | Q1, Q2 | — | P1 | — |
| `02_stack_traces_e_erros_assincronos` | 3. Stack traces e falhas assíncronas | Q3, Q4 | — | — | P2 |
| `03_logs_contexto_seguro` | 4. Logs úteis e seguros | Q5 | — | P3 | P2 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_reproducao_e_inspector` — Para que usar node --inspect-brk ao depurar uma falha que ocorre durante a inicialização? (origem linhas 44–47; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_reproducao_e_inspector` — Qual risco existe ao expor publicamente a porta padrão do inspector? (origem linhas 48–51; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_stack_traces_e_erros_assincronos` — Como começar a ler uma stack trace extensa? (origem linhas 52–55; resposta/feedback acompanhados).
- Q4 [exclusivo] → `02_stack_traces_e_erros_assincronos` — Uma camada captura um erro de banco e cria outra mensagem contextual, mas descarta o objeto original. O que se perde? (origem linhas 56–59; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_logs_contexto_seguro` — Qual conjunto de informações ajuda a investigar uma falha sem registrar dados sensíveis? (origem linhas 60–63; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_reproducao_e_inspector` — Encontrar a causa de uma falha reproduzível (linhas 66–74; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `02_stack_traces_e_erros_assincronos, 03_logs_contexto_seguro` — Seguir uma falha assíncrona (linhas 75–83; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_logs_contexto_seguro` — Criar um registro de erro seguro (linhas 84–92; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Revisita 7.5 — diagnóstico de erros; logs operacionais aprofundam-se em 38.1.

### 18.1 — Estrutura

- **Módulo:** APIs REST. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/18.1_Estrutura.md`. **Arquivos previstos:** 27.
- **Metadados originais:** `key=18.1`, `tipo=integrado`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=180`, `tags=['#web', '#arquitetura']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_recursos_e_semantica_http` | 1. Recursos, URIs e operações; 2. Semântica, repetição e idempotência | Q1, Q2 | — | — | P1 |
| `02_fluxo_de_requisicao_e_camadas` | 3. Fluxo de uma requisição e responsabilidades | Q5 | — | — | P2, P3 |
| `03_validacao_em_runtime` | 4. Validação e limites de confiança | Q3 | — | — | P2 |
| `04_status_e_erros_http` | 5. Status e formato de resposta | Q4 | — | — | P1, P2, P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_recursos_e_semantica_http` — Uma rota GET /tarefas/42 envia uma notificação e altera o estado da tarefa. Qual é o problema? (origem linhas 50–53; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_recursos_e_semantica_http` — O que significa dizer que PUT é idempotente? (origem linhas 54–57; resposta/feedback acompanhados).
- Q3 [exclusivo] → `03_validacao_em_runtime` — A aplicação frontend envia um objeto que satisfaz uma interface TypeScript. O servidor ainda precisa validar o body? (origem linhas 58–61; resposta/feedback acompanhados).
- Q4 [exclusivo] → `04_status_e_erros_http` — Por que distinguir 401 de 403? (origem linhas 62–65; resposta/feedback acompanhados).
- Q5 [exclusivo] → `02_fluxo_de_requisicao_e_camadas` — Onde deve ficar a regra de negócio de criação de uma tarefa: no controller ou no serviço? (origem linhas 66–69; resposta/feedback acompanhados).
- P1 [compartilhada] → `01_recursos_e_semantica_http, 04_status_e_erros_http` — Desenhar o contrato de um recurso (linhas 72–80; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `02_fluxo_de_requisicao_e_camadas, 03_validacao_em_runtime, 04_status_e_erros_http` — Separar camadas e validar uma criação (linhas 81–89; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `02_fluxo_de_requisicao_e_camadas, 04_status_e_erros_http` — Montar matriz de testes do contrato (linhas 90–98; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Revisita HTTP e JavaScript assíncrono de 7.3, organização de módulos em 8.2; contrato é retomado em 27.3 e testado em 24.1.

### 18.2 — Boas práticas

- **Módulo:** APIs REST. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/18.2_Boas_praticas.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=18.2`, `tipo=integrado`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#web', '#arquitetura']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_paginacao_de_colecoes` | 1. Paginação para coleções | Q1, Q2, Q3 | — | P1 | — |
| `02_compatibilidade_versionamento_openapi` | 2. Compatibilidade e versionamento; 3. OpenAPI como contrato legível por máquinas | Q4 | — | — | P2 |
| `03_idempotencia_em_retries` | 4. Idempotência em escritas sujeitas a retry | Q5 | — | P3 | P2 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_paginacao_de_colecoes` — Por que uma listagem com muitos registros deve ter limite imposto pelo servidor? (origem linhas 47–50; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_paginacao_de_colecoes` — Uma listagem ordena apenas por data de criação, que pode se repetir. O que falta para paginação cursor estável? (origem linhas 51–54; resposta/feedback acompanhados).
- Q3 [exclusivo] → `01_paginacao_de_colecoes` — Base64 transforma um cursor transparente em cursor seguro e opaco? (origem linhas 55–58; resposta/feedback acompanhados).
- Q4 [exclusivo] → `02_compatibilidade_versionamento_openapi` — Adicionar um campo opcional a uma resposta sempre é compatível com todos os clientes? (origem linhas 59–62; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_idempotencia_em_retries` — O serviço salva uma chave de idempotência antes de chamar uma cobrança externa. Isso, sozinho, garante que a cobrança ocorre uma única vez? (origem linhas 63–66; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_paginacao_de_colecoes` — Projetar contrato de paginação (linhas 69–77; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `02_compatibilidade_versionamento_openapi, 03_idempotencia_em_retries` — Revisar mudança de versão e OpenAPI (linhas 78–86; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_idempotencia_em_retries` — Simular retries e concorrência (linhas 87–95; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Complementa a integração frontend (27.1); versionamento e entrega reaparecem em 32.2 e 33.1. Contratos e testes de rotas continuam em 24.1 e documentação em 27.3.

### 18.3 — Tempo real

- **Módulo:** APIs REST. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/18.3_Tempo_real.md`. **Arquivos previstos:** 29.
- **Metadados originais:** `key=18.3`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#web', '#arquitetura']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_transportes_de_tempo_real` | 1. Escolher o transporte pela interação | Q1 | — | P1 | — |
| `02_eventos_ordem_e_retomada` | 2. Formato do evento, ordem e retomada | Q2 | Q3 | — | P3 |
| `03_seguranca_de_canais` | 3. Autenticação, autorização e limites | Q4 | — | — | P2, P3 |
| `04_estado_compartilhado_e_concorrencia` | 4. Estado compartilhado e concorrência | Q5 | Q3 | — | P2, P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_transportes_de_tempo_real` — O servidor precisa enviar atualizações ao navegador, mas o navegador envia comandos por HTTP normal. Qual opção pode atender com menor complexidade? (origem linhas 45–48; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_eventos_ordem_e_retomada` — Qual diferença de reconexão importa entre EventSource e WebSocket? (origem linhas 49–52; resposta/feedback acompanhados).
- Q3 [compartilhado] → `02_eventos_ordem_e_retomada, 04_estado_compartilhado_e_concorrencia` — Uma mensagem recebida contém ID já processado. O que o consumidor pode fazer? (origem linhas 53–56; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_seguranca_de_canais` — O servidor adiciona um usuário à sala “projeto-42” após receber o nome da sala do cliente. Isso comprova autorização? (origem linhas 57–60; resposta/feedback acompanhados).
- Q5 [exclusivo] → `04_estado_compartilhado_e_concorrencia` — Dois clientes editam o mesmo recurso e o servidor aplica last-write-wins. Qual limitação precisa ser explicada? (origem linhas 61–64; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_transportes_de_tempo_real` — Escolher o transporte (linhas 67–75; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `03_seguranca_de_canais, 04_estado_compartilhado_e_concorrencia` — Implementar canal autenticado para um recurso (linhas 76–84; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `02_eventos_ordem_e_retomada, 03_seguranca_de_canais, 04_estado_compartilhado_e_concorrencia` — Testar queda, repetição e concorrência (linhas 85–93; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Complementa 18.2; broadcast entre instâncias e escala horizontal retomam em 41.1 e 48.2.

### 19.1 — ORM e acesso a dados

- **Módulo:** ORM e acesso a dados (movido da Fase 4). **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/19.1_ORM_e_acesso_a_dados.md`. **Arquivos previstos:** 27.
- **Metadados originais:** `key=19.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#dados']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_mapeamento_orm_responsabilidades` | 1. Mapeamento e responsabilidades | Q1 | — | — | P1 |
| `02_consultas_relacoes_custo` | 2. Consultas, relações e custo | Q2, Q3 | — | P2 | — |
| `03_transacoes_unidade_negocio` | 3. Transações e unidade de negócio | Q4 | — | — | P3 |
| `04_migrations_sql_explicito` | 4. Migrations e SQL explícito | Q5 | — | — | P1, P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_mapeamento_orm_responsabilidades` — **Uma API tipada elimina a necessidade de conhecer SQL?** Não. Ela reduz trabalho repetitivo, mas desempenho e comportamento dependem do SQL e do banco. (origem linhas 65–65; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_consultas_relacoes_custo` — **Qual evidência sugere N+1?** Uma consulta inicial seguida de consultas relacionadas que crescem proporcionalmente ao número de itens processados. (origem linhas 66–66; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_consultas_relacoes_custo` — **Por que carregar todas as relações antecipadamente pode ser ruim?** Pode aumentar linhas, colunas e memória ou criar joins caros, mesmo reduzindo o número de chamadas. (origem linhas 67–67; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_transacoes_unidade_negocio` — **Duas gravações de uma mesma regra de negócio precisam ser confirmadas juntas. Como proceder?** Colocá-las na mesma transação/conexão e manter constraints e controle de concorrência adequados. (origem linhas 68–68; resposta/feedback acompanhados).
- Q5 [exclusivo] → `04_migrations_sql_explicito` — **Como incluir um valor fornecido pelo usuário em SQL explícito?** Usar parâmetro vinculado. Não concatenar o valor no texto; identificadores dinâmicos devem vir de allowlist. (origem linhas 69–70; resposta/feedback acompanhados).
- P1 [compartilhada] → `01_mapeamento_orm_responsabilidades, 04_migrations_sql_explicito` — Modelagem e migration (linhas 73–88; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_consultas_relacoes_custo` — Diagnóstico de N+1 e projeção (linhas 89–104; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `03_transacoes_unidade_negocio, 04_migrations_sql_explicito` — Atomicidade e SQL parametrizado (linhas 105–120; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Depende de SQL e modelagem da Fase 4 e da estrutura trabalhada em 18.1. A unidade 19.2 aprofunda critérios de maturidade para escolher abstrações e práticas de persistência.

### 19.2 — Regra de maturidade

- **Módulo:** ORM e acesso a dados (movido da Fase 4). **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/19.2_Regra_de_maturidade.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=19.2`, `tipo=integrado`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#dados', '#arquitetura']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_requisito_e_escolha_de_abstracao` | 1. Comece pela regra e pela consulta; 2. Escolha a menor abstração que mantém clareza | Q1, Q4 | — | P1 | — |
| `02_evidencia_antes_de_otimizar` | 3. Exija evidência antes de otimizar | Q2, Q3 | — | P2 | — |
| `03_fronteira_seguranca_contrato` | 4. Mantenha fronteira, segurança e contrato | Q5 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_requisito_e_escolha_de_abstracao` — **Múltipla escolha —** um CRUD comum está claro na API do ORM e não há evidência de problema. Qual é o próximo passo mais maduro? (origem linhas 63–68; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_evidencia_antes_de_otimizar` — **Verdadeiro ou falso —** uma consulta em SQL explícito será mais rápida que a consulta equivalente do ORM. (origem linhas 69–71; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_evidencia_antes_de_otimizar` — **Cenário —** uma consulta ORM demora em ambiente com muitos registros. Cite duas evidências a coletar antes de reescrevê-la. (origem linhas 72–74; resposta/feedback acompanhados).
- Q4 [exclusivo] → `01_requisito_e_escolha_de_abstracao` — **Resposta curta —** quando um query builder pode ser uma escolha intermediária? (origem linhas 75–77; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_fronteira_seguranca_contrato` — **Identifique o risco —** a aplicação monta uma cláusula ORDER BY concatenando texto vindo da URL. Qual correção é necessária? (origem linhas 78–80; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_requisito_e_escolha_de_abstracao` — Registro de decisão por operação (linhas 83–98; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_evidencia_antes_de_otimizar` — Diagnóstico antes da otimização (linhas 99–114; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_fronteira_seguranca_contrato` — Exceção de persistência sustentável (linhas 115–130; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Complementa 19.1, que introduz mapeamento, consultas, transações e migrations; revisita índices, cardinalidade e plano de execução estudados na Fase 4.

### 20.1 — Autenticação

- **Módulo:** Autenticação e segurança de APIs. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/20.1_Autenticacao.md`. **Arquivos previstos:** 29.
- **Metadados originais:** `key=20.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=180`, `tags=['#seguranca']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_identidade_e_sessao` | 1. Identidade, autenticação e autorização; 2. Sessão no servidor | Q1 | — | — | P1, P3 |
| `02_jwt_e_validacao_de_tokens` | 3. Tokens, JWT e validação | Q2 | Q5 | — | P1 |
| `03_oauth_oidc_e_arquitetura_cliente` | 4. OAuth 2.0 e OpenID Connect; 6. Escolha uma arquitetura coerente com o cliente | Q3 | Q5 | P2 | — |
| `04_renovacao_expiracao_e_logout` | 5. Renovação, expiração e encerramento | Q4 | — | — | P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_identidade_e_sessao` — **Classificação —** um usuário autenticado solicita a leitura de um pedido. Qual controle ainda decide se ele pode ver aquele pedido? (origem linhas 99–101; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_jwt_e_validacao_de_tokens` — **Verdadeiro ou falso —** um JWT assinado contém um payload secreto e pode ser aceito após apenas decodificá-lo. (origem linhas 102–104; resposta/feedback acompanhados).
- Q3 [exclusivo] → `03_oauth_oidc_e_arquitetura_cliente` — **Escolha de fluxo —** uma SPA é cliente público e precisa obter token por OAuth. Qual grant deve orientar o fluxo atual? (origem linhas 105–107; resposta/feedback acompanhados).
- Q4 [exclusivo] → `04_renovacao_expiracao_e_logout` — **Cenário —** uma aplicação apaga o cookie no navegador, mas não invalida a sessão no servidor. O que ocorre se um atacante copiou o identificador antes? (origem linhas 108–110; resposta/feedback acompanhados).
- Q5 [compartilhado] → `02_jwt_e_validacao_de_tokens, 03_oauth_oidc_e_arquitetura_cliente` — **Relacionamento —** associe cada artefato ao seu propósito: ID Token OIDC, access token, refresh token. (origem linhas 111–113; resposta/feedback acompanhados).
- P1 [compartilhada] → `01_identidade_e_sessao, 02_jwt_e_validacao_de_tokens` — Compare sessão e token (linhas 116–131; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `03_oauth_oidc_e_arquitetura_cliente` — Revisão de um fluxo OIDC/OAuth (linhas 132–147; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `01_identidade_e_sessao, 04_renovacao_expiracao_e_logout` — Implementação demonstrativa do ciclo de sessão (linhas 148–163; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Prepara 20.2, que aprofunda hash de senhas, segredos, CSRF e proteções de entrada, e 20.3, que aplica autorização por recurso e ação. Retoma sessões e proteção do navegador em 27.4.

### 20.2 — Segurança básica

- **Módulo:** Autenticação e segurança de APIs. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/20.2_Seguranca_basica.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=20.2`, `tipo=solo`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=180`, `tags=['#seguranca']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_armazenamento_de_senhas` | 1. Armazenamento de senhas | Q1 | — | P1 | — |
| `02_sql_e_fronteira_cross_origin` | 2. SQL seguro e limites de ORM; 3. CORS e fronteira do navegador | Q2, Q3 | — | P2 | — |
| `03_csrf_e_segredos` | 4. CSRF em credenciais enviadas automaticamente; 5. Segredos e resposta a exposição | Q4, Q5 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_armazenamento_de_senhas` — **Múltipla escolha —** o banco de usuários foi exposto. Qual dado reduz a chance de recuperar uma senha por tentativa rápida? (origem linhas 81–86; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_sql_e_fronteira_cross_origin` — **Identifique o erro —** uma busca parametriza o e-mail, mas concatena o texto recebido em sortBy dentro do ORDER BY. O que falta? (origem linhas 87–89; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_sql_e_fronteira_cross_origin` — **Verdadeiro ou falso —** se CORS não permite uma origem, a API está protegida contra requisições de curl e contra CSRF. (origem linhas 90–92; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_csrf_e_segredos` — **Cenário —** um endpoint altera e-mail por GET e usa cookie de sessão. Que dois problemas devem ser corrigidos? (origem linhas 93–95; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_csrf_e_segredos` — **Resposta curta —** uma credencial de serviço foi enviada ao Git por engano. Qual ação vem primeiro e por que limpar o commit não basta? (origem linhas 96–98; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_armazenamento_de_senhas` — Armazenamento de senha em ambiente local (linhas 101–116; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_sql_e_fronteira_cross_origin` — Consulta e configuração cross-origin (linhas 117–132; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_csrf_e_segredos` — CSRF e incidente de segredo simulado (linhas 133–148; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Depende do fluxo de autenticação em 20.1 e complementa autorização por recurso em 20.3. Retoma ambiente e configuração segura de 1.2; CSRF e origem cross-site são retomados em 27.4; entrega de credenciais é aprofundada em 34.1.

### 20.3 — Segurança aplicada

- **Módulo:** Autenticação e segurança de APIs. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/20.3_Seguranca_aplicada.md`. **Arquivos previstos:** 27.
- **Metadados originais:** `key=20.3`, `tipo=integrado`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#seguranca']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_autorizacao_acao_objeto` | 1. Decida acesso para ação e recurso | Q1 | — | P1 | — |
| `02_propriedades_e_minimizacao` | 2. Proteja propriedades e minimize respostas | Q2 | — | — | P2 |
| `03_limites_de_abuso_e_recursos` | 3. Limite abuso e consumo de recursos | Q3, Q4 | — | P3 | — |
| `04_finalidade_retencao_e_logs` | 4. Registre finalidade e retenção com cautela | Q5 | — | — | P2 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_autorizacao_acao_objeto` — **Cenário —** um usuário autenticado altera o ID de um pedido na URL e recebe o pedido de outra conta. Qual controle falhou? (origem linhas 70–72; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_propriedades_e_minimizacao` — **Múltipla escolha —** o formulário não exibe o campo role, mas a API aceita role no corpo de atualização do perfil. Qual risco permanece? (origem linhas 73–78; resposta/feedback acompanhados).
- Q3 [exclusivo] → `03_limites_de_abuso_e_recursos` — **Resposta curta —** por que limitar chamadas somente pelo IP pode prejudicar usuários legítimos e ainda não conter abuso? (origem linhas 79–81; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_limites_de_abuso_e_recursos` — **Verdadeiro ou falso —** configurar limite de requisições torna desnecessário limitar tamanho do upload e quantidade de itens por chamada. (origem linhas 82–84; resposta/feedback acompanhados).
- Q5 [exclusivo] → `04_finalidade_retencao_e_logs` — **Identifique o princípio —** a equipe deixa de coletar um dado pessoal que não é necessário, remove valores dos logs e define quando descartar os registros restantes. (origem linhas 85–87; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_autorizacao_acao_objeto` — Matriz de autorização e teste negativo (linhas 90–105; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `02_propriedades_e_minimizacao, 04_finalidade_retencao_e_logs` — Minimização de propriedades e dados (linhas 106–121; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_limites_de_abuso_e_recursos` — Proteção contra abuso de uma rota (linhas 122–137; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Depende dos conceitos de identidade e proteções básicas em 20.1/20.2; autorização por recurso reaparece em 24.1. Gestão de dados de aplicação conecta-se a 34.1, e uso de dados em IA/segurança é aprofundado em 51.1.

### 21.1 — Base conceitual

- **Módulo:** Princípios de design de software. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/21.1_Base_conceitual.md`. **Arquivos previstos:** 27.
- **Metadados originais:** `key=21.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#arquitetura', '#fundamentos']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_coesao_responsabilidades` | 1. Coesão: responsabilidades que pertencem juntas | Q1 | — | — | P1 |
| `02_acoplamento_custo_mudanca` | 2. Acoplamento: dependências e custo de mudança | Q2 | — | — | P1, P3 |
| `03_di_ponto_de_composicao` | 3. Injeção de dependência e ponto de composição | Q3, Q4 | — | — | P2, P3 |
| `04_refatoracao_comportamento_evidencia` | 4. Refatore com comportamento e evidência | Q5 | — | — | P2, P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_coesao_responsabilidades` — **Classificação —** uma função pequena faz parsing HTTP, regra de negócio e envio de e-mail. Ela é necessariamente coesa por ser pequena? (origem linhas 70–72; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_acoplamento_custo_mudanca` — **Cenário —** três módulos chamam o mesmo adaptador de pagamento. Isso prova que o sistema tem acoplamento ruim? (origem linhas 73–75; resposta/feedback acompanhados).
- Q3 [exclusivo] → `03_di_ponto_de_composicao` — **Múltipla escolha —** quando uma interface é mais justificável? (origem linhas 76–81; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_di_ponto_de_composicao` — **Verdadeiro ou falso —** DI exige um container e uma interface formal para toda dependência. (origem linhas 82–84; resposta/feedback acompanhados).
- Q5 [exclusivo] → `04_refatoracao_comportamento_evidencia` — **Resposta curta —** que evidência pode mostrar que uma refatoração melhorou a testabilidade sem provar sozinha que toda a arquitetura é melhor? (origem linhas 85–87; resposta/feedback acompanhados).
- P1 [compartilhada] → `01_coesao_responsabilidades, 02_acoplamento_custo_mudanca` — Mapa de responsabilidades e mudanças (linhas 90–105; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `03_di_ponto_de_composicao, 04_refatoracao_comportamento_evidencia` — Extração de uma regra testável (linhas 106–121; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `02_acoplamento_custo_mudanca, 03_di_ponto_de_composicao, 04_refatoracao_comportamento_evidencia` — Revisão crítica da abstração (linhas 122–137; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Revisita organização de código em 7.2; prepara uso de módulos, providers e injeção no NestJS (22) e modelos de arquitetura em 23.1. A separação de infraestrutura também se conecta ao acesso a dados em 19.1.

### 22.1 — Estrutura de framework

- **Módulo:** NestJS e organização modular. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/22.1_Estrutura_de_framework.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=22.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#arquitetura']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_modulos_grafo_e_composicao` | 1. O módulo e o grafo da aplicação; 4. Fronteiras e composição sem atalhos globais | Q1, Q2, Q4 | — | P2 | P1 |
| `02_controller_provider_e_di_runtime` | 2. Controller adapta HTTP; provider executa colaboração; 3. Injeção e tokens em tempo de execução | Q3 | — | — | P1 |
| `03_testes_da_composicao_nest` | 5. Teste o módulo e substitua a dependência certa | Q5 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_modulos_grafo_e_composicao` — **Associação —** qual parte declara a API HTTP e qual parte pode fornecer uma colaboração injetável? (origem linhas 80–82; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_modulos_grafo_e_composicao` — **Cenário —** BillingModule precisa usar OrdersService. Qual é o caminho modular explícito? (origem linhas 83–85; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_controller_provider_e_di_runtime` — **Verdadeiro ou falso —** uma interface TypeScript pode ser o token de runtime para que Nest injete diretamente a implementação. (origem linhas 86–88; resposta/feedback acompanhados).
- Q4 [exclusivo] → `01_modulos_grafo_e_composicao` — **Diagnóstico —** dois providers precisam de forwardRef. Qual deve ser a primeira investigação? (origem linhas 89–91; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_testes_da_composicao_nest` — **Escolha de teste —** você quer validar que a regra de pedidos grava no repositório correto. Que combinação de evidência é adequada? (origem linhas 92–94; resposta/feedback acompanhados).
- P1 [compartilhada] → `01_modulos_grafo_e_composicao, 02_controller_provider_e_di_runtime` — Estruture uma rota em módulos Nest (linhas 97–112; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `01_modulos_grafo_e_composicao` — Importe e exponha uma dependência de feature (linhas 113–128; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_testes_da_composicao_nest` — Teste a fronteira com TestingModule (linhas 129–144; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Aplica os conceitos de responsabilidade e dependência de 21.1; prepara validação de entrada e guards em 22.2 e organização de domínio em 23.1. A unidade 19.1 mostra um exemplo de fronteira de persistência que pode ser fornecida como provider.

### 22.2 — Organização forte

- **Módulo:** NestJS e organização modular. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/22.2_Organizacao_forte.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=22.2`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#arquitetura', '#seguranca']`, `status=revisado`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_validacao_entrada_runtime` | 1. DTO e contrato de entrada em runtime; 2. Pipes validam e transformam argumentos | Q1, Q2 | — | P1 | — |
| `02_guards_ciclo_requisicao` | 3. Guards e posição no ciclo da requisição | Q3 | — | P2 | — |
| `03_autorizacao_contextual_respostas` | 4. Autorização contextual e formato de saída | Q4, Q5 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_validacao_entrada_runtime` — **Verdadeiro ou falso —** tipar o corpo como interface TypeScript é suficiente para rejeitar JSON malformado em runtime. (origem linhas 70–72; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_validacao_entrada_runtime` — **Configuração —** em ValidationPipe com class-validator, qual diferença existe entre whitelist e forbidNonWhitelisted? (origem linhas 73–75; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_guards_ciclo_requisicao` — **Ordenação —** na sequência usual Nest, o que ocorre primeiro: guard ou pipe? Por que isso importa? (origem linhas 76–78; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_autorizacao_contextual_respostas` — **Cenário —** uma pessoa tem papel de editor, mas tenta alterar um documento de outro tenant. Um RolesGuard basta? (origem linhas 79–81; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_autorizacao_contextual_respostas` — **Escolha de saída —** um handler retorna a entidade do banco, incluindo um campo interno. Como evitar expô-lo? (origem linhas 82–84; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_validacao_entrada_runtime` — DTO e pipe de entrada (linhas 87–102; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_guards_ciclo_requisicao` — Guard de autenticação e papel (linhas 103–118; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_autorizacao_contextual_respostas` — Recurso protegido e resposta permitida (linhas 119–134; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Aplica módulos e providers de 22.1; utiliza autenticação e proteção básica de 20.1/20.2 e autorização por objeto de 20.3. Modelos de domínio de 23.1 aprofundam as regras que continuam fora da validação estrutural do DTO.

### 23.1 — Modelos

- **Módulo:** Arquitetura de software e raciocínio de design. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/23.1_Modelos.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=23.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#arquitetura', '#design']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_fronteiras_e_ports_adapters` | 1. Arquitetura começa por uma decisão de mudança; 2. Ports and adapters protege uma conversa | Q1, Q4 | — | P1, P3 | — |
| `02_solid_criterios_design` | 3. SOLID como perguntas de design | Q3 | — | P2 | — |
| `03_padroes_modulos_proposito` | 4. Padrões e módulos: escolha pelo problema | Q2, Q5 | — | — | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_fronteiras_e_ports_adapters` — **Classificação:** em uma solução com regra de reserva, interface PostgreSQL e fake de teste, qual peça é o adapter? (origem linhas 70–72; resposta/feedback acompanhados).
- Q2 [exclusivo] → `03_padroes_modulos_proposito` — **Cenário:** o caso de uso importa o cliente SQL e executa a consulta diretamente. Criar um módulo Nest separado torna a regra independente do banco? (origem linhas 73–75; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_solid_criterios_design` — **Seleção de princípio:** há uma interface enorme usada por dois consumidores, cada um chamando operações diferentes. Qual princípio ajuda a investigar esse desenho? (origem linhas 76–78; resposta/feedback acompanhados).
- Q4 [exclusivo] → `01_fronteiras_e_ports_adapters` — **Análise de trade-off:** só existe um gateway de pagamento, mas a política de cobrança é central e precisa ser testada sem rede. Uma abstração pode fazer sentido? Explique. (origem linhas 79–81; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_padroes_modulos_proposito` — **Transferência:** um novo algoritmo de frete pode ser escolhido por região e muda com frequência. Que pergunta indica se Strategy é apropriada? (origem linhas 82–84; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_fronteiras_e_ports_adapters` — Desenhe a fronteira da reserva (linhas 87–103; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_solid_criterios_design` — Revise SOLID em um desenho (linhas 104–120; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `01_fronteiras_e_ports_adapters` — Injete uma porta e prove a troca (linhas 121–138; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Aplica composição e dependências de 21.1, antecede a modelagem de domínio em 23.2 e oferece uma alternativa organizacional ao recorte modular de 24.2.

### 23.2 — Base de raciocínio

- **Módulo:** Arquitetura de software e raciocínio de design. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/23.2_Base_de_raciocinio.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=23.2`, `tipo=solo`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#fundamentos', '#arquitetura', '#algoritmos']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_trabalho_e_crescimento_assintotico` | 1. Comece pelo trabalho que o programa faz; 2. O que Big O explica e o que não explica | Q1, Q3 | — | P2 | — |
| `02_estruturas_e_custo_total` | 3. Compare operações e custo total | Q2, Q4 | — | P1 | — |
| `03_medicao_e_decisao_de_desempenho` | 4. Decida, meça e preserve clareza | Q5 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_trabalho_e_crescimento_assintotico` — **Interpretação:** um algoritmo percorre no máximo uma vez cada item de uma lista de n elementos. Qual é o crescimento do trabalho em relação a n, se o trabalho por item é constante? (origem linhas 71–73; resposta/feedback acompanhados).
- Q2 [exclusivo] → `02_estruturas_e_custo_total` — **Escolha com trade-off:** um processo percorre a mesma lista muitas vezes procurando IDs. O que um Map construído uma vez pode melhorar e que custo acrescenta? (origem linhas 74–76; resposta/feedback acompanhados).
- Q3 [exclusivo] → `01_trabalho_e_crescimento_assintotico` — **Limite da notação:** uma solução é O(1) e outra O(n). É possível concluir que a primeira sempre termina antes? (origem linhas 77–79; resposta/feedback acompanhados).
- Q4 [exclusivo] → `02_estruturas_e_custo_total` — **Distinção de análise:** uma estrutura ocasionalmente copia n itens ao aumentar a capacidade, mas inserir no fim tem custo O(1) amortizado. Isso quer dizer que toda inserção individual custa O(1)? (origem linhas 80–82; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_medicao_e_decisao_de_desempenho` — **Transferência:** uma API filtra milhões de registros no banco. Por que transformar todos em Map no servidor pode não ser a melhoria adequada? (origem linhas 83–85; resposta/feedback acompanhados).
- P1 [exclusiva] → `02_estruturas_e_custo_total` — Faça a conta de buscas repetidas (linhas 88–104; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `01_trabalho_e_crescimento_assintotico` — Analise o crescimento de pequenos trechos (linhas 105–125; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_medicao_e_decisao_de_desempenho` — Faça uma decisão com dados e fronteira corretos (linhas 126–142; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Revisita lógica e estruturas de dados de 6.2 e 7.4; usa fronteiras de 23.1 para distinguir memória de persistência; análise de desempenho reaparece em 30.1.

### 23.3 — Regra dura

- **Módulo:** Arquitetura de software e raciocínio de design. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/23.3_Regra_dura.md`. **Arquivos previstos:** 21.
- **Metadados originais:** `key=23.3`, `tipo=integrado`, `carater=obrigatorio`, `profundidade=media`, `estimativa_minutos=90`, `tags=['#arquitetura', '#design-evolutivo']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_complexidade_essencial_e_acidental` | 1. Simples não significa improvisado; 2. Complexidade tem custo dos dois lados | Q1, Q2 | — | P1 | P3 |
| `02_evolucao_reversivel_com_evidencia` | 3. Evoluir requer feedback e uma rota de volta; 4. Decida com evidências e revise | Q3, Q4, Q5 | — | P2 | P3 |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_complexidade_essencial_e_acidental` — **Diagnóstico:** um serviço converte um único formato estável e ganhou uma fábrica de plugins, registro dinâmico, hierarquia de classes e configuração. Qual evidência você buscaria antes de manter a estrutura? (origem linhas 57–59; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_complexidade_essencial_e_acidental` — **Cenário:** um adapter tem apenas uma implementação, mas permite testar a regra de cobrança sem acessar um gateway externo. A existência de uma implementação prova que o adapter deve ser removido? (origem linhas 60–62; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_evolucao_reversivel_com_evidencia` — **Compreensão:** design evolutivo significa deixar decisões arquiteturais para depois sem testes nem revisão? (origem linhas 63–65; resposta/feedback acompanhados).
- Q4 [exclusivo] → `02_evolucao_reversivel_com_evidencia` — **Seleção:** qual decisão tende a ser mais reversível: publicar agora um contrato usado por vários clientes ou experimentar uma implementação interna atrás de um limite ainda privado? (origem linhas 66–68; resposta/feedback acompanhados).
- Q5 [exclusivo] → `02_evolucao_reversivel_com_evidencia` — **Transferência:** que condição justificaria revisar uma decisão inicialmente simples de persistir arquivos localmente? (origem linhas 69–71; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_complexidade_essencial_e_acidental` — Remova ou mantenha as camadas (linhas 74–90; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_evolucao_reversivel_com_evidencia` — Escreva uma decisão reversível (linhas 91–107; solução e rubrica existentes acompanhadas).
- P3 [compartilhada] → `01_complexidade_essencial_e_acidental, 02_evolucao_reversivel_com_evidencia` — Refatore em passos seguros (linhas 108–124; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Complementa as fronteiras de 23.1 e a escolha de estruturas de 23.2; conclui os critérios arquiteturais do módulo antes da aplicação de testes em 24.1.

### 24.1 — Tipos de teste

- **Módulo:** Testes de backend. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/24.1_Tipos_de_teste.md`. **Arquivos previstos:** 24.
- **Metadados originais:** `key=24.1`, `tipo=solo`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=180`, `tags=['#qualidade', '#testes']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_escopo_doubles_unitarios_integracao` | 1. Classifique pelo limite que o teste atravessa; 2. Escolha dublês de teste pela pergunta; 3. Testes unitários e integração respondem a riscos diferentes | Q1, Q2 | — | P1 | — |
| `02_e2e_isolamento_confiabilidade` | 4. E2E, dados isolados e confiabilidade | Q4, Q5 | — | P2 | — |
| `03_assertions_e_cobertura` | 5. Asserções e cobertura medem coisas diferentes | Q3 | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_escopo_doubles_unitarios_integracao` — **Classificação:** um teste instancia um serviço de aplicação e um repositório PostgreSQL real de teste, mas não inicia HTTP. Ele é unitário ou de integração? (origem linhas 72–74; resposta/feedback acompanhados).
- Q2 [exclusivo] → `01_escopo_doubles_unitarios_integracao` — **Seleção de dublê:** para testar se uma cobrança rejeitada não grava pedido, que substituição pode ajudar e qual comportamento precisa ser afirmado? (origem linhas 75–77; resposta/feedback acompanhados).
- Q3 [exclusivo] → `03_assertions_e_cobertura` — **Diagnóstico:** a cobertura de linhas chegou a 100%, mas nenhuma asserção verifica o caminho em que o usuário não tem permissão. O risco foi coberto? (origem linhas 78–80; resposta/feedback acompanhados).
- Q4 [exclusivo] → `02_e2e_isolamento_confiabilidade` — **Estabilidade:** uma suíte passa quando executada inteira, mas falha se um teste de criação roda sozinho. Qual propriedade está quebrada e que medidas investigar? (origem linhas 81–83; resposta/feedback acompanhados).
- Q5 [exclusivo] → `02_e2e_isolamento_confiabilidade` — **Transferência:** uma interface de compra tem dezenas de combinações de campos e regras. É melhor reproduzir todas em E2E? (origem linhas 84–86; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_escopo_doubles_unitarios_integracao` — Monte uma matriz de confiança para pedidos (linhas 89–105; solução e rubrica existentes acompanhadas).
- P2 [exclusiva] → `02_e2e_isolamento_confiabilidade` — Torne um teste repetível (linhas 106–122; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `03_assertions_e_cobertura` — Revise cobertura contra comportamento (linhas 123–139; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Retoma testes de autorização de 20.3; usa fronteiras e providers vistos em 22.1 e 23.1; prepara a aplicação da suíte no módulo 24.2.

### 24.2 — Aplicação

- **Módulo:** Testes de backend. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/24.2_Aplicacao.md`. **Arquivos previstos:** 25.
- **Metadados originais:** `key=24.2`, `tipo=pratica`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=210`, `tags=['#qualidade', '#testes', '#persistencia']`, `status=rascunho`

| Assunto [PROPOSTA] | Microtópicos de teoria (títulos originais) | Q exclusivo | Q compartilhado | P exclusiva | P compartilhada |
|---|---|---|---|---|---|
| `01_planejamento_teste_servico` | 1. Planeje a evidência antes de abrir o editor | Q1 | — | P1 | — |
| `02_integracao_rota_nest` | 2. Teste o serviço com um dublê controlado | Q3 | — | — | P2 |
| `03_persistencia_banco_isolado` | 3. Exercite a rota pela aplicação Nest de teste; 4. Prove a persistência com o banco real | Q2, Q4, Q5 | — | — | P2 |
| `04_isolamento_repetibilidade` | 5. Faça a suíte repetir sem depender da ordem | — | — | P3 | — |

**Questões e práticas, item por item:**
- Q1 [exclusivo] → `01_planejamento_teste_servico` — **Aplicação:** um teste do serviço passa com repositório falso, mas uma migration esqueceu a constraint de unicidade. O teste deveria detectar isso? (origem linhas 72–74; resposta/feedback acompanhados).
- Q2 [exclusivo] → `03_persistencia_banco_isolado` — **Configuração segura:** que ambiente usar para testar criação e duplicidade? (origem linhas 75–77; resposta/feedback acompanhados).
- Q3 [exclusivo] → `02_integracao_rota_nest` — **Leitura do escopo:** o teste sobe Nest, envia HTTP e substitui provider de persistência por mock. O que ele prova e o que não prova? (origem linhas 78–80; resposta/feedback acompanhados).
- Q4 [exclusivo] → `03_persistencia_banco_isolado` — **Falha de isolamento:** a limpeza usa rollback de uma transação aberta pelo teste, mas o endpoint grava em outra conexão do pool. Por que os dados podem continuar? (origem linhas 81–83; resposta/feedback acompanhados).
- Q5 [exclusivo] → `03_persistencia_banco_isolado` — **Diagnóstico:** um endpoint retorna 201 e o corpo correto, mas a consulta posterior não encontra o registro. Qual evidência falta? (origem linhas 84–86; resposta/feedback acompanhados).
- P1 [exclusiva] → `01_planejamento_teste_servico` — Cubra serviço e falhas controladas (linhas 89–105; solução e rubrica existentes acompanhadas).
- P2 [compartilhada] → `02_integracao_rota_nest, 03_persistencia_banco_isolado` — Teste rota e persistência sem mockar o que está avaliando (linhas 106–122; solução e rubrica existentes acompanhadas).
- P3 [exclusiva] → `04_isolamento_repetibilidade` — Audite a suíte entre execuções (linhas 123–139; solução e rubrica existentes acompanhadas).
- **Rubricas:** 0–2: 24 rubricas; descritiva: 30 rubricas. Critérios de aceite/checklists convencionais: nenhum bloco separado identificado.
- **Conexões e pré-requisitos declarados:** ## Conexões Aplica os escopos e dublês de 24.1 e complementa constraints e integridade de 12.2.

### 24.3 — Projeto incremental da fase

- **Módulo:** Testes de backend. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/24.3_Projeto_incremental.md`. **Arquivos previstos:** 17.
- **Metadados originais:** `key=24.3`, `tipo=projeto`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=600`, `tags=['#qualidade', '#infra']`, `status=rascunho`

| Marco | Título literal | Aceite | Arquivos planos propostos |
|---|---|---|---|
| M01 | Escopo vertical, contrato e ambiente reproduzível | C01 | `m01_escopo-vertical-contrato-e-ambiente-reproduzivel.md` + `m01_criterios_de_aceite.md` |
| M02 | API autenticada e persistência migrável | C02 | `m02_api-autenticada-e-persistencia-migravel.md` + `m02_criterios_de_aceite.md` |
| M03 | Testes de serviço/rota e coerência de cache | C03 | `m03_testes-de-servico-rota-e-coerencia-de-cache.md` + `m03_criterios_de_aceite.md` |
| M04 | Compose, documentação e revisão de ponta a ponta | C04 | `m04_compose-documentacao-e-revisao-de-ponta-a-ponta.md` + `m04_criterios_de_aceite.md` |
- **Rubrica:** 0–4 original, sem alteração. Checklist final de 8 itens e seção de decisões existentes serão separados.
- **Conexões e pré-requisitos declarados:** ## Conexões Continua a ideia do Trilho A (3.5), o modelo de dados (16.2) e aplicação/confiabilidade de testes (24.1–24.2). Reutiliza fundamentos de API, autenticação, migrations e Compose já apresentados nas fases anteriores.

### 24.4 — Projeto de fase (Trilho B)

- **Módulo:** Testes de backend. **Origem:** `docs/courses/trilhacode/Conteudos/Fase_5/24.4_Projeto_de_fase_Trilho_B.md`. **Arquivos previstos:** 16.
- **Metadados originais:** `key=24.4`, `tipo=projeto`, `carater=obrigatorio`, `profundidade=alta`, `estimativa_minutos=900`, `tags=['#projeto', '#qualidade']`, `status=rascunho`

| Marco | Título literal | Aceite | Arquivos planos propostos |
|---|---|---|---|
| M01 | Seleção elegível, contrato e modelo mínimo | C01 | `m01_selecao-elegivel-contrato-e-modelo-minimo.md` + `m01_criterios_de_aceite.md` |
| M02 | Base da Fase 5: API, autenticação e PostgreSQL | C02 | `m02_base-da-fase-5-api-autenticacao-e-postgresql.md` + `m02_criterios_de_aceite.md` |
| M03 | Implementação da propriedade difícil do tipo | C03 | `m03_implementacao-da-propriedade-dificil-do-tipo.md` + `m03_criterios_de_aceite.md` |
| M04 | Testes, documentação e decisão de cobertura | C04 | `m04_testes-documentacao-e-decisao-de-cobertura.md` + `m04_criterios_de_aceite.md` |
- **Rubrica:** 0–4 original, sem alteração. Sem checklist final; preservar os quatro pontos de revisão e o aceite por tipo T1–T5 do Marco 3.
- **Conexões e pré-requisitos declarados:** ## Conexões Complementa o projeto incremental do Trilho A (24.3); as versões por tipo são definidas no [Guia de Projetos e Rotação](../../Guia_Projetos_e_Rotacao_de_Tipos.md). Pré-requisitos conceituais incluem modelos relacionais/migrations, APIs, autenticação, testes e fluxos de aplicação já apresentados.

## Projetos

- **24.3 — Projeto incremental:** preservar quatro marcos e quatro aceites literais, o checklist final de oito itens, as quatro dimensões 0–4 por marco e a seção “Decisões que precisam ser demonstradas”. O texto da fonte relaciona o trabalho à ideia de 3.5 e ao modelo/banco de 16.2. Os arquivos novos serão apenas referências estruturais aos blocos atuais; não duplicar enunciados nem criar brief/rubrica geral.
- **24.4 — Projeto de fase (Trilho B):** preservar quatro marcos e quatro aceites; Marco 3 mantém a tabela de aceite por tipo T1–T5; preservar quatro pontos de revisão e rubrica 0–4. Não existe checklist final separado na fonte. O link para o guia exige retarget estrutural apenas se o destino continuar existente e inequívoco.
- Os identificadores M1–M4 são referências de blocos fonte, não novas atividades.

## Fronteiras com outras fases

| Sobreposição | Fonte canônica e fronteira |
|---|---|
| 19.x ↔ 12.x | Fase 4 (12.x) é canônica para SQL, constraints, transações, isolamento, locking, índices e planos. 19.1/19.2 cobrem ORM, SQL gerado, N+1, unidade de trabalho e escolha proporcional entre ORM/query builder/SQL. |
| 20.x ↔ 27.4 | 20.1–20.3: autenticação e segurança no backend/API; 27.4: aplicação das proteções na fronteira do navegador. |
| 18.x ↔ 27.x | 18.1/18.2: semântica e contrato HTTP no servidor; 27.x: consumo e integração no frontend. |
| 18.3 ↔ 41.x/48.x | 18.3: transporte, eventos, segurança e estado no canal em tempo real; 41.x/48.x: distribuição e estado entre instâncias. |
| 23.2 ↔ 6.2/7.4/30.1 | 23.2: raciocínio de custo no backend; Fase 3: fundamentos de lógica e estruturas; 30.1: otimização da interface. |
| 21.x/22.x/23.x | 21.1 fundamenta responsabilidades e dependências; 22.x aplica ao Nest; 23.x toma decisões de arquitetura. Preservar conexões, sem duplicar teoria. |
| 24.1/24.2 ↔ 12.2 | 24.1/24.2 cobrem estratégia e aplicação de testes; 12.2 permanece canônica para semântica de constraints e integridade do banco. |
| 24.3/24.4 ↔ projetos anteriores | 24.3 continua os projetos 3.5/16.2 como a fonte declara; 24.4 é uma escolha alternativa do Trilho B, orientada pelo guia. |

## Propostas pedagógicas e divergências

- [PROPOSTA] Aprovar os 61 assuntos e os limites de teoria antes da geração. A lista anterior de propostas de cobertura destaca 20.1 e 24.2, mas o mapa slug-a-slug não está no checkout. Esta reconstrução atribui Q/P conforme as habilidades diretamente exigidas e propõe item exclusivo para cada assunto; isso não resolve retroativamente a classificação anterior. Revisar esses dois casos na aprovação do mapa, sem criar novos exercícios agora.
- [PROPOSTA] Não há outra lacuna de verificação exclusiva no mapa reconstruído. A regra de cobertura exclusiva continua valendo; itens integradores complementam, não substituem.
- [PROPOSTA] Tratar links Obsidian como ressalva até confirmar a raiz do vault. Links Markdown relativos devem ser validados na geração.

## Estimativa de arquivos

| Unidade | Arquivos | Assuntos de conteúdo |
|---|---:|---:|
| 17.1 | 25 | 4 |
| 17.2 | 24 | 3 |
| 18.1 | 27 | 4 |
| 18.2 | 24 | 3 |
| 18.3 | 29 | 4 |
| 19.1 | 27 | 4 |
| 19.2 | 24 | 3 |
| 20.1 | 29 | 4 |
| 20.2 | 24 | 3 |
| 20.3 | 27 | 4 |
| 21.1 | 27 | 4 |
| 22.1 | 24 | 3 |
| 22.2 | 24 | 3 |
| 23.1 | 24 | 3 |
| 23.2 | 24 | 3 |
| 23.3 | 21 | 2 |
| 24.1 | 24 | 3 |
| 24.2 | 25 | 4 |
| 24.3 | 17 | 0 |
| 24.4 | 16 | 0 |
| **Total** | **486** | **61** |

| Tipo | Arquivos previstos |
|---|---:|
| `acceptance_criteria` | 8 |
| `answer_key_practice` | 54 |
| `answer_key_quiz` | 61 |
| `checklist` | 1 |
| `connections` | 20 |
| `criterion` | 20 |
| `milestone` | 8 |
| `objective` | 20 |
| `practice` | 54 |
| `project_decisions` | 1 |
| `project_review` | 1 |
| `project_scope` | 2 |
| `quiz` | 61 |
| `references` | 20 |
| `rubric` | 56 |
| `summary` | 18 |
| `theory` | 61 |
| `topic_index` | 20 |
| **Total** | **486** |

Contagem prevista, sem arquivos vazios ou artificiais. Mudanças na divisão ou em formatos aprovados alteram essa estimativa.

## Manifesto

O arquivo `mapa_de_migracao_fase5.yml` é um rascunho não aprovado, com caminhos relativos a `destino_raiz`, origem por seção/linhas, IDs `f5` únicos, cobertura por slug e campos preservados. Não executar até a aprovação.

