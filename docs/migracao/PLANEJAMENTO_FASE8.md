# Planejamento estrutural — Fase 8

**Estado:** rascunho para revisão; nenhuma árvore da Fase 8 foi gerada.  
**Base de planejamento:** commit `b74e053879bd7c8ec8093479e5c645bba9cc6be8`, branch `migracao-estrutura`.  
**Manifesto correspondente:** `docs/migracao/mapa_de_migracao_fase8.yml`.

## 1. Escopo e fontes

A página oficial `docs/courses/trilhacode/Fase_8_Infra_Operacao.md` enumera três módulos e oito unidades ativas: 37.1–37.3, 38.1–38.2 e 39.1–39.3. Não há outras unidades Fase 8 ativas na pasta de origem. As sete unidades ativas da Fase 7 (32.1, 32.2, 33.1, 34.1, 35.1, 36.1 e 36.2) não interferem nesse inventário; as cópias 37.1/37.2 na pasta `Conteudos/Fase_7/` são tratadas separadamente abaixo.

Não foi localizado manifesto histórico da Fase 8. Portanto, as divisões de assuntos e a cobertura abaixo são **[PROPOSTA]**, reconstruídas dos microtópicos, itens avaliativos e relações da fonte. Os IDs, títulos, módulos e metadados são transcritos das fontes existentes.

| Unidade | Módulo | Tipo / caráter / profundidade | Minutos | Tópicos teóricos | Quiz + resposta inline | Atividades convencionais | Flashcards | Observação de fonte |
|---|---|---|---:|---:|---:|---:|---:|---|
| 37.1 Serviços gerenciados | 37 | solo / repertorio / repertorio | 45 | teoria sintética sem subtítulos | 0 | 0 | 3 | versão ativa curta da Fase 8 |
| 37.2 Kubernetes básico | 37 | solo / repertorio / repertorio | 45 | teoria sintética sem subtítulos | 0 | 0 | 3 | versão ativa curta da Fase 8 |
| 37.3 GCP: noções | 37 | solo / repertorio / repertorio | 45 | 3 microtópicos | 0 | 2 | 3 | 98 linhas, 1.337 palavras |
| 38.1 Sinais operacionais | 38 | solo / obrigatorio / media | 90 | 4 microtópicos | 5 | 3 | 0 | respostas embutidas nos itens do quiz |
| 38.2 Ferramentas | 38 | pratica / obrigatorio / media | 120 | 4 microtópicos | 5 | 3 | 0 | respostas embutidas nos itens do quiz |
| 39.1 Operação madura | 39 | integrado / obrigatorio / media | 90 | 4 microtópicos | 5 | 3 | 0 | respostas embutidas nos itens do quiz |
| 39.2 Projeto incremental da fase | 39 | projeto / obrigatorio / alta | 780 | 4 microtópicos de apoio ao projeto | 0 | projeto, não prática convencional | 0 | checklist, rubrica e cenários de aceite próprios |
| 39.3 Projeto de fase (Trilho B) | 39 | projeto / obrigatorio / alta | 660 | quatro entregas formais | 0 | projeto, não prática convencional | 0 | 4 entregas, 4 aceites, checklist e rubrica |

**Totais da fonte Fase 8:** 8 unidades ativas; 6 convencionais e 2 contêineres de projeto; 13 assuntos convencionais propostos; 19 microtópicos teóricos com título; 2 seções de teoria sintética sem microtópicos titulados; 15 questões com 15 respostas inline; 11 atividades convencionais; 9 flashcards; 4 marcos/entregas formais em 39.3; 4 aceites de marco; 2 checklists finais; 2 rubricas de projeto. Não contei como quiz as listas numeradas que aparecem dentro das atividades.

### Metadados de origem

As oito fontes usam metadados em lista Markdown sob o H1, não frontmatter. Os valores devem ser copiados para o frontmatter do `README.md` sem completar campos nem reinterpretar os valores.

| Unidade | key | tipo | carater | profundidade | estimativa_minutos | tags | status |
|---|---|---|---|---|---:|---|---|
| 37.1 | 37.1 | solo | repertorio | repertorio | 45 | `#infra` | rascunho |
| 37.2 | 37.2 | solo | repertorio | repertorio | 45 | `#infra` | rascunho |
| 37.3 | 37.3 | solo | repertorio | repertorio | 45 | `#infra`, `#cloud`, `#mensageria` | rascunho |
| 38.1 | 38.1 | solo | obrigatorio | media | 90 | `#infra`, `#qualidade`, `#observabilidade` | rascunho |
| 38.2 | 38.2 | pratica | obrigatorio | media | 120 | `#ferramentas`, `#infra`, `#observabilidade` | rascunho |
| 39.1 | 39.1 | integrado | obrigatorio | media | 90 | `#infra`, `#qualidade`, `#confiabilidade` | rascunho |
| 39.2 | 39.2 | projeto | obrigatorio | alta | 780 | `#infra`, `#observabilidade`, `#projeto` | rascunho |
| 39.3 | 39.3 | projeto | obrigatorio | alta | 660 | `#projeto`, `#infra`, `#observabilidade` | rascunho |

## 2. Investigação das cópias 37.1 e 37.2

| ID | Cópia em Conteudos/Fase_7 | SHA-256 / tamanho | Cópia em Conteudos/Fase_8 | SHA-256 / tamanho | Diferenças verificadas |
|---|---|---|---|---|---|
| 37.1 | `docs/courses/trilhacode/Conteudos/Fase_7/37.1_Servicos_gerenciados.md` | `2B8823F965D41F8733F5D55CFBFBFB4D1EC019E97804C64B96E9932176634027`; 95 linhas, 1.264 palavras, 9.395 bytes | `docs/courses/trilhacode/Conteudos/Fase_8/37.1_Servicos_gerenciados.md` | `BB4443823E00A5078929C25F1144D4D6E39F47CA31492E745EF299243197BA43`; 40 linhas, 375 palavras, 2.863 bytes | Hashes e texto diferem. F7: `obrigatorio/media`, 3 microtópicos titulados e 2 atividades curtas. F8: `repertorio/repertorio`, teoria sintética sem títulos de microtópico, 3 flashcards e nenhuma atividade/quiz. A F7 detalha modos de capacidade e operação, comparação de custo e seleção por workload/equipe; a F8 mantém a comparação resumida. |
| 37.2 | `docs/courses/trilhacode/Conteudos/Fase_7/37.2_Kubernetes_basico.md` | `34959A8FBFC4156E6A3C7A0A46A4D88974A18561148276C9F7C9CAD09BF6103C`; 101 linhas, 1.319 palavras, 9.928 bytes | `docs/courses/trilhacode/Conteudos/Fase_8/37.2_Kubernetes_basico.md` | `F864C16CBE297BB08B3CE5745B89F43D33FCA8F0933C49A8FF830706C456E3FE`; 44 linhas, 437 palavras, 3.558 bytes | Hashes e texto diferem. F7: `obrigatorio/media`, tag adicional `#containers`, 3 microtópicos titulados e 2 atividades curtas. F8: `repertorio/repertorio`, sem tag `#containers`, teoria sintética, 3 flashcards e nenhuma atividade/quiz. F7 desenvolve configuração e fronteira de segurança num microtópico próprio; a F8 resume esse conteúdo dentro da teoria geral. |

**Evidência editorial e recomendação:** a página oficial da Fase 7 lista apenas os Módulos 32–36 e não lista 37.1/37.2. A página oficial da Fase 8 lista ambas em Módulo 37, com classificação repertório e 45 minutos; as fontes da Fase 8, `Referencias_Fase_8.md`, o roadmap e o JSON também as tratam como Fase 8. A recomendação é usar as fontes de `Conteudos/Fase_8/` como base do manifesto F8. Não foi localizado `CHANGELOG_Correcoes.md` nem um registro que formalize a transferência ou explique a redução. Assim, não declaro aposentadoria formal das cópias F7.

Há referências de conteúdo para 37.1/37.2 na página oficial, na página de referências da Fase 8, no roadmap, no JSON, em 37.3 e nos links recíprocos das cópias. Não encontrei referência que exija migrar as cópias físicas da pasta F7. O conteúdo extra das cópias F7 — quatro atividades e teoria mais detalhada — não será incorporado nem duplicado na migração estrutural da Fase 8; sua eventual restauração/consolidação continua uma decisão editorial separada.

## 3. Assuntos propostos e cobertura

`[PROPOSTA]` As unidades curtas 37.1 e 37.2 ficam cada uma com um assunto, pois a fonte F8 apresenta uma síntese contínua e repertorial sem divisões naturais. Os três flashcards de cada unidade permanecem agrupados nesse assunto. Não importo práticas das cópias F7.

| Unidade / assunto (slug) | Microtópicos originais destinados ao assunto | Quiz exclusivo | Quiz compartilhado | Prática exclusiva | Prática compartilhada | Flashcards |
|---|---|---|---|---|---|---|
| 37.1 `01_ecs_eks_modelos_responsabilidades` | Seção inteira `## Teoria`, sem subtítulos na fonte: ECS, EKS, responsabilidades, abstração, controle, operação e custo | — | — | — | — | FC01–FC03 exclusivos |
| 37.2 `01_pods_deployments_services_probes` | Seção inteira `## Teoria`, sem subtítulos na fonte: Pod, Deployment/ReplicaSet, Service, probes e manifestos | — | — | — | — | FC01–FC03 exclusivos |
| 37.3 `01_modelos_de_execucao_cloud_run` | Microtópico 1 — Cloud Run: Service, Job, worker pool e instance | — | — | — | P01 com 02 e 03; P02 com 02 | FC01 exclusivo |
| 37.3 `02_pubsub_entrega_idempotencia` | Microtópico 2 — Pub/Sub, confirmação, reentrega e efeito de negócio | — | — | — | P01 com 01 e 03; P02 com 01 | FC02 exclusivo |
| 37.3 `03_gke_autopilot_standard_provedores` | Microtópico 3 — GKE Autopilot/Standard e limites de comparação entre provedores | — | — | — | P01 com 01 e 02 | FC03 exclusivo |
| 38.1 `01_escolha_dos_sinais` | Microtópico 1 — escolher log, métrica ou trace pela pergunta | Q1 | — | — | P2 com 03; P3 com 02 | — |
| 38.1 `02_logs_metricas_dimensoes_privacidade` | Microtópico 2 — esquema e campos analisáveis, cardinalidade, dados pessoais | Q3, Q4 | — | P1 | P3 com 01 | — |
| 38.1 `03_tracing_contexto_otel` | Microtópicos 3–4 — traces/spans, propagação de contexto e instrumentação OpenTelemetry | Q2, Q5 | — | — | P2 com 01 | — |
| 38.2 `01_fluxo_otel_prometheus_promql` | Microtópicos 1–2 — papéis no pipeline, coleta Prometheus, PromQL, histogramas | Q1, Q3, Q4, Q5 | — | — | P1, P2 e P3 com 02 | — |
| 38.2 `02_grafana_dashboards_operacao` | Microtópicos 3–4 — perguntas de dashboard, integração, volume e operação | Q2 | — | — | P1, P2 e P3 com 01 | — |
| 39.1 `01_sli_slo_sla_error_budget` | Microtópico 1 — SLI, SLO, SLA e error budget | Q1–Q3 | — | P1 | — | — |
| 39.1 `02_resposta_incidente_runbooks` | Microtópico 2 — restaurar serviço, coordenar resposta e usar runbook | Q4 | — | P2 | — | — |
| 39.1 `03_postmortem_adrs` | Microtópicos 3–4 — postmortem sem culpa, ADR e ações verificáveis | Q5 | — | P3 | — | — |

### Atribuição individual dos itens

| Unidade | Item | Conteúdo avaliado na fonte | Classificação proposta |
|---|---|---|---|
| 38.1 | Q1 | tendência de latência p95 e sinal métrica | exclusivo 01 |
| 38.1 | Q2 | localizar chamada downstream lenta por trace/spans | exclusivo 03 |
| 38.1 | Q3 | JSON não garante esquema de log estável | exclusivo 02 |
| 38.1 | Q4 | cardinalidade e exposição por `user_id` em métrica | exclusivo 02 |
| 38.1 | Q5 | propagação ausente e quebra de correlação de trace | exclusivo 03 |
| 38.1 | P1 | normalizar três logs e retirar dados sensíveis | exclusivo 02 |
| 38.1 | P2 | diagrama de spans, propagação e seleção de sinal para três sintomas | compartilhado 01 + 03 |
| 38.1 | P3 | classificar dimensões e propor métrica/consulta com privacidade | compartilhado 01 + 02 |
| 38.2 | Q1 | alvo Prometheus indisponível apesar de app local responder | exclusivo 01 |
| 38.2 | Q2 | onde residem as séries consultadas por Grafana | exclusivo 02 |
| 38.2 | Q3 | função de `rate(...[5m])` | exclusivo 01 |
| 38.2 | Q4 | preservar label `le` ao agregar histograma clássico | exclusivo 01 |
| 38.2 | Q5 | limite interpretativo do p95 calculado por buckets | exclusivo 01 |
| 38.2 | P1 | pipeline OTel/Prometheus/Grafana e falhas entre componentes | compartilhado 01 + 02 |
| 38.2 | P2 | consultas de taxa/erro/p95 e dashboard | compartilhado 01 + 02 |
| 38.2 | P3 | incidente, dashboard, trace/log, alerta e comparação de backend | compartilhado 01 + 02 |
| 39.1 | Q1 | diferença entre SLI e SLO | exclusivo 01 |
| 39.1 | Q2 | objetivo interno não é automaticamente SLA | exclusivo 01 |
| 39.1 | Q3 | margem de eventos ruins para SLO de 99% | exclusivo 01 |
| 39.1 | Q4 | coordenar, avaliar impacto e restaurar antes de concluir causa | exclusivo 02 |
| 39.1 | Q5 | insuficiência de postmortem que culpa uma pessoa | exclusivo 03 |
| 39.1 | P1 | definir SLI/SLO, população, janela e orçamento | exclusivo 01 |
| 39.1 | P2 | runbook com decisão, rollback, validação e escalonamento | exclusivo 02 |
| 39.1 | P3 | postmortem e ADR a partir do cenário | exclusivo 03 |

**Regras da classificação:** cada quiz tem um assunto de destino; uma prática só é compartilhada quando o enunciado exige as habilidades dos assuntos listados. Cada compartilhada terá um arquivo físico em `90_integracao/`; os assuntos a referenciarão na cobertura. Respostas existentes estão inline nos 15 quizzes, sem criar gabarito para unidades sem questão. Na futura separação Q/K, o limite literal verificado é `? **`: o enunciado conserva o espaço após a interrogação e o gabarito começa no primeiro asterisco; em cada item, a concatenação dos dois segmentos deve reconstruir a fonte sem alteração. As 11 práticas incluem entregas, critérios de aceite e feedback dentro do próprio enunciado; não há rubricas/soluções independentes para elas.

## 4. Projetos existentes

| Unidade | Organização proposta | Critérios, checklists e rubrica existentes | Dependências explicitamente descritas |
|---|---|---|---|
| 39.2 — Projeto incremental da fase | Um contêiner de projeto, sem pastas de assuntos ou marcos inventados. Preservar quatro microtópicos teóricos em arquivos separados; objetivo; escopo/regras; checklist; rubrica; cinco verificações por cenário; critério; conexões; referências. | Checklist final com 11 itens. Rubrica final: seis dimensões, 0–2 cada, total 12; aceite mínimo 10/12 e dimensões bloqueadoras sem zero. Cinco cenários de verificação. | Continuação do projeto principal do Trilho A iniciado em 3.5 e implantado em 32.2/36.1; usa 38.1–38.2 e 39.1. A página chama o projeto de tracing/métricas/dashboard/postmortem. |
| 39.3 — Projeto de fase (Trilho B) | Um contêiner de projeto. Quatro arquivos planos de entrega, com `titulo_marco` literal; quatro checklists de aceite separados; checklist final e rubrica separados. A tabela T1–T5 fica no marco 2 (Entrega 2), onde está na fonte. | Quatro blocos Teste/aceite; checklist final com 12 itens; rubrica com seis dimensões, escala 0–2, total 12, aceite mínimo 10/12 e bloqueadores descritos na fonte. Sem rubrica nova. | Reutiliza API, banco e testes de fases anteriores; Docker/pipeline/infra de 32.2 e 36.1; observabilidade 38.1–38.2; operação 39.1; guia de rotação. É declarado independente do projeto principal 39.2. |

**Títulos literais de 39.3:** “Entrega 1 — Escolher tipo, ideia e contrato de aceite”; “Entrega 2 — Construir a fatia vertical e testar o risco central”; “Entrega 3 — Empacotar, automatizar e observar”; “Entrega 4 — Demonstrar, reverter, documentar e encerrar”. Os IDs de entrega são referências do manifesto. A tabela T1–T5 está na Entrega 2. A Entrega 3 contém cinco itens de instrumentação por tipo, também rotulados T1–T5; são blocos distintos.

## 5. Relações curriculares e pré-requisitos

| Unidade | Relações explícitas na fonte | Fronteira a preservar |
|---|---|---|
| Fase 8 | Pré-requisito declarado: Fase 7 (pipeline, cloud e Terraform). | A navegação da Fase 8 preservará o pré-requisito; o texto original da página não será alterado. |
| 37.1 | Complementa 37.2 e 10.2; depende de fundamentos de cloud 34.1. | Comparação ECS/EKS não torna Kubernetes requisito de implementação. |
| 37.2 | Complementa 37.1; baseia-se em containerização local 10.2. | Repertório de noções; não equivale à implementação de uma stack Kubernetes em projeto. |
| 37.3 | Relaciona-se a 35.1, 37.1, 37.2 e 40.1–40.2. | Comparação GCP não substitui os serviços canônicos de outras fases. |
| 38.1 | Revisa depuração em 17.2 e 7.5; relaciona-se a 38.2. | Depuração local/servidor versus observabilidade operacional. |
| 38.2 | Relaciona-se a 38.1 e 39.2. | Ferramentas e pipeline de telemetria; não reensina definição conceitual dos sinais. |
| 39.1 | Relaciona-se a entrega 32.2, sinais 38.1 e regra dura 23.3. | Operação, incidentes e aprendizado; não substitui segurança da aplicação. |
| 39.2 | Continuação do projeto principal; liga-se a 3.5, 32.2, 36.1, 38.1–38.2 e 39.1. | Projeto incremental do Trilho A, não um novo marco/nó JSON. |
| 39.3 | Reutiliza fases anteriores, 32.2, 36.1, 38.1–38.2, 39.1 e guia de rotação; complementar, mas não duplicado de 39.2. | Projeto de fase do Trilho B permanece escolha independente. |

## 6. Estimativa da árvore futura

O manifesto prevê 124 arquivos gerados a partir de blocos existentes. A estimativa não inclui este planejamento nem o manifesto. Não cria arquivos para quiz/atividade em 37.1/37.2 e não inventa marcos em 39.2.

| Unidade | README | Objetivo | Resumo | Critério | Conexões | Referências | Teoria | Quiz | Gabarito | Prática | Flashcards | Projeto / aceite / rubrica | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 37.1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 8 |
| 37.2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 8 |
| 37.3 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 0 | 0 | 2 | 3 | 0 | 14 |
| 38.1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 5 | 5 | 3 | 0 | 0 | 22 |
| 38.2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 5 | 5 | 3 | 0 | 0 | 21 |
| 39.1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 5 | 5 | 3 | 0 | 0 | 22 |
| 39.2 | 1 | 1 | 0 | 1 | 1 | 1 | 4 | 0 | 0 | 0 | 0 | 4 | 13 |
| 39.3 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 11 | 16 |
| **Total** | **8** | **8** | **6** | **8** | **8** | **8** | **17** | **15** | **15** | **11** | **5** | **15** | **124** |

| Tipo de arquivo | Quantidade |
|---|---:|
| topic_index / README | 8 |
| objetivo | 8 |
| resumo | 6 |
| criterio | 8 |
| conexoes | 8 |
| referencias | 8 |
| theory | 17 |
| quiz | 15 |
| answer_key | 15 |
| practice | 11 |
| flashcards agrupados por assunto | 5 |
| project_scope | 2 |
| project_milestone | 4 |
| checklist (quatro aceites e dois checklists finais) | 6 |
| rubrica | 2 |
| project_scenarios | 1 |
| **Total** | **124** |

## 7. Lacunas e decisões ainda abertas

- [PROPOSTA] 37.1/37.2: manter as versões F8 curtas como repertório; decidir em fluxo editorial separado se alguma teoria/atividade das cópias F7 deve voltar à trilha ativa. A migração estrutural não funde os textos.
- [PROPOSTA] 37.1/37.2/37.3: manter ausência de quiz convencional; não preencher a lacuna com exercício novo durante a migração.
- [PROPOSTA] 37.3: P1 e P2 integram vários assuntos; os três flashcards existentes oferecem verificações focais de reconhecimento, mas não há quiz nem prática exclusiva para cada assunto.
- [PROPOSTA] 38.2: Q2 foi alocada a Grafana/dashboard por avaliar localização e papel da fonte consultada; P1–P3 são compartilhadas entre o fluxo Prometheus e a camada Grafana/integração.
- [PROPOSTA] 39.2 não traz títulos de marcos. Os quatro microtópicos são teoria do projeto e não serão renomeados como marcos.
- A raiz do vault Obsidian continua por confirmar. O manifesto preserva referências existentes, mas resolução de wikilinks deve ser validada quando a árvore migrada for gerada.
- Nenhuma expansão, restauração de cópias, atividade, gabarito ou rubrica está autorizada por este planejamento.
