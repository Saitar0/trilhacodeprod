# Planejamento da migração estrutural — Fase 7

**Estado:** rascunho para revisão; nenhum conteúdo migrado foi gerado. **Base observada:** `53956919fc145e897f5ac7763513812b03f04dba` na branch `migracao-estrutura`. **Consulta:** 27/10/2026.

## Diagnóstico e fontes

- A página oficial da [Fase 7](../courses/trilhacode/Fase_7_Infra_Deploy_e_Cloud.md) descreve os Módulos 32–36 e lista sete subunidades ativas: 32.1, 32.2, 33.1, 34.1, 35.1, 36.1 e 36.2.
- Não foi localizado mapa aprovado da Fase 7 no repositório; todos os agrupamentos e classificações abaixo são **[PROPOSTA]**, não decisões históricas. As convenções estruturais gerais seguem as Fases 1–6 homologadas.
- As sete fontes ativas trazem metadados em lista Markdown sob o H1, sem YAML. Na futura migração, os valores serão copiados ao frontmatter do README, sem preencher campos ausentes.
- Inventário das fontes: 28 microtópicos, 35 questões com resposta esperada inline e 21 práticas. Não há flashcards, soluções de prática independentes, rubricas independentes ou checklists independentes nas sete fontes. Cada prática contém Evidências, Verificação e Aceite dentro do próprio bloco.
- A página estima 13–26 horas (referência de planejamento 20 h). A soma de `estimativa_minutos` é 1.170 min = 19,5 h, compatível com a referência de 20 h.
- A pasta `Conteudos/Fase_7` tem nove arquivos: as sete fontes listadas pela página e duas cópias 37.x. Não há decisão localizada que as marque formalmente como aposentadas; a Fase 8 as identifica como repertório e contém versões correspondentes. As cópias 37.x não serão tratadas como unidades F7 nem removidas.

## Inventário das unidades ativas

| Unidade | Módulo | Título | Metadados fonte: tipo / caráter / profundidade / min / tags / status | linhas / palavras | teoria / Q+respostas / P | refs (itens/links) |
|---|---|---|---|---:|---:|---:|
| 32.1 | 32 — CI/CD e entrega | 32.1 — Automação | solo / obrigatorio / media / 180 / #infra, #qualidade / rascunho | 176 / 2170 | 4 / 5 / 3 | 7 / 8 |
| 32.2 | 32 — CI/CD e entrega | 32.2 — Entrega | integrado / obrigatorio / media / 180 / #infra / rascunho | 187 / 2256 | 4 / 5 / 3 | 6 / 7 |
| 33.1 | 33 — Mensageria: conceitos | 33.1 — Conceitos | solo / obrigatorio / media / 90 / #infra, #arquitetura / rascunho | 143 / 2102 | 4 / 5 / 3 | 6 / 7 |
| 34.1 | 34 — Fundamentos de cloud (AWS) | 34.1 — Base de cloud | solo / obrigatorio / media / 180 / #infra, #seguranca / rascunho | 146 / 2378 | 4 / 5 / 3 | 9 / 12 |
| 35.1 | 35 — AWS: serviços sob demanda e eventos | 35.1 — Serviços e eventos | solo / obrigatorio / media / 180 / #infra / rascunho | 145 / 2326 | 4 / 5 / 3 | 6 / 9 |
| 36.1 | 36 — Infraestrutura como código | 36.1 — Infra como código | solo / obrigatorio / media / 180 / #infra / rascunho | 141 / 2021 | 4 / 5 / 3 | 6 / 9 |
| 36.2 | 36 — Infraestrutura como código | 36.2 — Ambientes | solo / obrigatorio / media / 180 / #infra / rascunho | 157 / 2378 | 4 / 5 / 3 | 6 / 7 |

## Divisão de assuntos e cobertura

A atribuição considera habilidade exigida pelo enunciado/aceite. Item exclusivo tem um assunto; item compartilhado tem mais de um assunto e um só destino físico em `90_integracao/`. Os Q/K são separados na futura árvore apenas porque a resposta já existe inline na fonte.

### 32.1 — Automação

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/32.1_Automacao.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/32.1_Automacao/` · **Arquivos previstos:** 21

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_workflow_reprodutibilidade_quality_gates` — Workflow, reprodutibilidade e quality gates | T1 — Workflow, evento, job e step (L16–23; ~179 palavras); T2 — Reprodutibilidade e quality gates (L24–31; ~203 palavras) | Q01, Q02, Q03 | — | P02 | P01 |
| `02_seguranca_actions_falhas` — Segurança, dependências de Actions e leitura de falhas | T3 — Permissões, secrets e dependências de Actions (L32–39; ~187 palavras); T4 — Leitura de falhas e limites da análise estática (L40–80; ~320 palavras) | Q04, Q05 | — | P03 | P01 |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L91–96) | 1. **Múltipla escolha:** qual configuração torna um check um requisito de merge em uma branch protegida? A. Adicionar uma badge ao README. B. Configurar a proteção da branch para exigir o status check correspondente. C. Rodar o workflow apenas em `push`. | `01_workflow_reprodutibilidade_quality_gates` | exclusiva | `01_workflow_reprodutibilidade_quality_gates/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L97–99) | 2. **Diagnóstico:** o workflow está verde, mas um PR ainda pode ser integrado mesmo quando o check falha. Qual hipótese deve ser verificada primeiro? | `01_workflow_reprodutibilidade_quality_gates` | exclusiva | `01_workflow_reprodutibilidade_quality_gates/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L100–102) | 3. **Leitura de configuração:** o projeto usa `package-lock.json`, mas o workflow executa `npm install`. Que mudança favorece instalação consistente em CI, e qual condição ela pressupõe? | `01_workflow_reprodutibilidade_quality_gates` | exclusiva | `01_workflow_reprodutibilidade_quality_gates/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L103–105) | 4. **Segurança:** um workflow acionado por `pull_request_target` faz checkout do código do PR e executa `npm install` com secrets disponíveis. Qual é o risco principal? | `02_seguranca_actions_falhas` | exclusiva | `02_seguranca_actions_falhas/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L106–108) | 5. **Decisão técnica:** a equipe quer fixar Actions por SHA completo. Cite uma vantagem, um custo operacional e uma prática para tornar a referência revisável. | `02_seguranca_actions_falhas` | exclusiva | `02_seguranca_actions_falhas/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L111–127) | Monte o workflow mínimo reproduzível — crie um workflow de CI para um repositório Node.js que valide cada pull request. | `01_workflow_reprodutibilidade_quality_gates`, `02_seguranca_actions_falhas` | compartilhada | `90_integracao/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L128–144) | Prove o bloqueio do quality gate — demonstre a diferença entre executar CI e exigir seu resultado para integrar uma mudança. | `01_workflow_reprodutibilidade_quality_gates` | exclusiva | `01_workflow_reprodutibilidade_quality_gates/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L145–162) | Faça uma revisão de segurança e manutenção — revise o workflow como uma dependência executável e documente riscos e ações. | `02_seguranca_actions_falhas` | exclusiva | `02_seguranca_actions_falhas/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Retoma o uso do GitHub em 3.3, a base de automação/CI da Fase 5 e os testes de 24.1 e 29.2. Reutiliza a imagem/container discutido em 10.1 quando o projeto empacota a aplicação, mas CI de código não exige publicar uma imagem.
- Pré-requisitos de unidade explicitamente declarados: nenhum identificado; valem também os pré-requisitos gerais da fase (Fases 1, 4 e 5).
- Referências individuais: 7 itens bibliográficos (8 links externos), consultados em 14/10/2026; preservar integralmente a seção da fonte.

### 32.2 — Entrega

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/32.2_Entrega.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/32.2_Entrega/` · **Arquivos previstos:** 23

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_identidade_do_artefato` — Identidade e promoção do artefato | T1 — Construa uma vez e identifique o artefato (L16–23; ~188 palavras) | Q01 | — | — | P01 |
| `02_ambientes_autorizacao_promocao` — Ambientes, autorização e promoção | T2 — Ambientes, autorização e promoção (L24–33; ~248 palavras) | Q03 | — | — | P01 |
| `03_saude_pos_deploy` — Verificação de saúde após deploy | T3 — Verifique a saúde depois de publicar (L34–41; ~181 palavras) | Q02 | — | — | P02 |
| `04_rollback_schema_dados` — Rollback, compatibilidade de schema e dados | T4 — Faça rollback sem confundir aplicação e dados (L42–91; ~411 palavras) | Q04, Q05 | — | P03 | P02 |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L102–107) | 1. **Múltipla escolha:** qual caminho preserva melhor a identidade da versão validada? A. Fazer um build para staging e outro independente para produção. B. Promover o mesmo artefato testado e registrar commit/digest e ambiente. C. Recompilar no servidor de produção sem guardar metadados. | `01_identidade_do_artefato` | exclusiva | `01_identidade_do_artefato/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L108–110) | 2. **Diagnóstico:** o deploy terminou com sucesso, mas o smoke check recebe erro de conexão. O pipeline deve promover a versão mesmo assim? Explique. | `03_saude_pos_deploy` | exclusiva | `03_saude_pos_deploy/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L111–113) | 3. **Aplicação de conceito:** por que staging não deve compartilhar credenciais e dados de produção, mesmo que replique a configuração da aplicação? | `02_ambientes_autorizacao_promocao` | exclusiva | `02_ambientes_autorizacao_promocao/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L114–116) | 4. **Análise de cenário:** após uma migração que remove uma coluna, a versão nova falha. Por que simplesmente voltar ao container anterior pode não recuperar o serviço? | `04_rollback_schema_dados` | exclusiva | `04_rollback_schema_dados/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L117–119) | 5. **Decisão técnica:** qual evidência demonstra que um backup pode apoiar um plano de recuperação? | `04_rollback_schema_dados` | exclusiva | `04_rollback_schema_dados/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L122–138) | Produza e promova um artefato — monte um fluxo que constrói uma aplicação uma vez e disponibiliza a mesma saída em staging. | `01_identidade_do_artefato`, `02_ambientes_autorizacao_promocao` | compartilhada | `90_integracao/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L139–156) | Detecte falha e recupere a aplicação — prove que um smoke check impede promoção e pratique a volta a uma versão conhecida. | `03_saude_pos_deploy`, `04_rollback_schema_dados` | compartilhada | `90_integracao/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L157–174) | Planeje compatibilidade e restauração — mostre como uma mudança de schema e dados convive com deploy e rollback. | `04_rollback_schema_dados` | exclusiva | `04_rollback_schema_dados/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Depende de CI e checks de 32.1. Retoma integridade e transações em 12.2 e operação em 18.2; prepara deploy, infraestrutura e ambiente de 36.1–36.2.
- Pré-requisitos de unidade explicitamente declarados: 32.1.
- Referências individuais: 6 itens bibliográficos (7 links externos), consultados em 14/10/2026; preservar integralmente a seção da fonte.

### 33.1 — Conceitos

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/33.1_Conceitos.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/33.1_Conceitos/` · **Arquivos previstos:** 22

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_modelos_mensageria_entrega` — Modelos de mensageria, confirmação e entrega | T1 — Produtor, broker, fila e tópico (L16–23; ~220 palavras); T2 — Entrega, confirmação e redelivery (L24–31; ~208 palavras) | Q01, Q02 | — | — | P01 |
| `02_retry_backoff_dlq` — Retry, backoff, poison messages e DLQ | T3 — Retry, backoff, poison message e DLQ (L32–39; ~202 palavras) | Q04 | — | — | P01, P03 |
| `03_idempotencia_outbox_consistencia` — Idempotência, outbox e consistência | T4 — Idempotência, outbox e consistência (L40–49; ~291 palavras) | Q03, Q05 | — | P02 | P01, P03 |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L60–62) | 1. **Classificação:** em uma fila de trabalho compartilhada por vários workers, o que normalmente acontece com uma mensagem concluída e confirmada? | `01_modelos_mensageria_entrega` | exclusiva | `01_modelos_mensageria_entrega/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L63–68) | 2. **Múltipla escolha:** o broker confirma que aceitou a publicação. O que isso prova? A. O consumidor terminou a regra de negócio. B. O broker aceitou a publicação segundo a confirmação configurada. C. O pagamento externo foi efetivado uma única vez. | `01_modelos_mensageria_entrega` | exclusiva | `01_modelos_mensageria_entrega/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L69–71) | 3. **Diagnóstico de falha:** o worker atualiza o pedido no banco e cai antes do ack. O pedido pode ser atualizado novamente após redelivery? Como prevenir efeito duplicado? | `03_idempotencia_outbox_consistencia` | exclusiva | `03_idempotencia_outbox_consistencia/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L72–74) | 4. **Decisão de retry:** uma mensagem recebe erro de formato inválido em todas as tentativas. O que fazer e por quê? | `02_retry_backoff_dlq` | exclusiva | `02_retry_backoff_dlq/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L75–77) | 5. **Análise de arquitetura:** serviço grava pedido no banco e publica evento em seguida. Que janela de inconsistência permanece e como a outbox ajuda? | `03_idempotencia_outbox_consistencia` | exclusiva | `03_idempotencia_outbox_consistencia/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L80–96) | Desenhe o ciclo da mensagem e as falhas — modele um pedido que dispara processamento assíncrono e descreva o que acontece nos pontos de falha. | `01_modelos_mensageria_entrega`, `02_retry_backoff_dlq`, `03_idempotencia_outbox_consistencia` | compartilhada | `90_integracao/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L97–113) | Torne o consumidor idempotente — implemente ou modele um worker que receba duas vezes o mesmo evento sem duplicar o efeito de negócio. | `03_idempotencia_outbox_consistencia` | exclusiva | `03_idempotencia_outbox_consistencia/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L114–130) | Defina política de retry e DLQ — estabeleça uma política operacional para falha transitória e poison message. | `02_retry_backoff_dlq`, `03_idempotencia_outbox_consistencia` | compartilhada | `90_integracao/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Retoma Redis/filas em 15.1 e decisões arquiteturais em 18.1–18.2. Prepara mensageria gerenciada em 35.1, implementação com RabbitMQ em 40.1 e a etapa de retry/DLQ do projeto 46.3.
- Pré-requisitos de unidade explicitamente declarados: nenhum identificado; valem também os pré-requisitos gerais da fase (Fases 1, 4 e 5).
- Referências individuais: 6 itens bibliográficos (7 links externos), consultados em 14/10/2026; preservar integralmente a seção da fonte.

### 34.1 — Base de cloud

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/34.1_Base_de_cloud.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/34.1_Base_de_cloud/` · **Arquivos previstos:** 23

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_conta_iam_responsabilidade` — Conta, IAM e responsabilidade compartilhada | T1 — Conta, regiões e responsabilidade compartilhada (L16–23; ~245 palavras) | Q02, Q05 | — | — | P02 |
| `02_vpc_subnets_rotas_security_groups` — VPC, subnets, rotas e security groups | T2 — VPC, subnets, rotas e security groups (L24–31; ~246 palavras) | Q01 | — | — | P01, P02 |
| `03_dns_tls_caminho_requisicao` — DNS, TLS e caminho da requisição | T3 — Identidade e caminho da requisição (L32–39; ~224 palavras) | Q03 | — | — | P01 |
| `04_custos_orcamento_laboratorio` — Custos, orçamento e encerramento do laboratório | T4 — Custo, orçamento e encerramento do laboratório (L40–49; ~288 palavras) | Q04 | — | P03 | — |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L60–65) | 1. **Múltipla escolha:** uma route table da subnet tem rota para Internet Gateway. O que se pode concluir? A. Todos os recursos da subnet estão automaticamente acessíveis publicamente. B. A subnet é pública, mas cada recurso ainda depende de endereçamento, configuração e regras de tráfego para ser alcançável. C. A aplicação deixa de precisar de autenticação. | `02_vpc_subnets_rotas_security_groups` | exclusiva | `02_vpc_subnets_rotas_security_groups/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L66–68) | 2. **Diagnóstico de IAM:** uma aplicação em EC2 precisa ler objetos de um bucket e recebeu uma access key estática no arquivo de configuração. Qual melhoria reduz o risco? | `01_conta_iam_responsabilidade` | exclusiva | `01_conta_iam_responsabilidade/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L69–71) | 3. **Traçado de requisição:** o DNS do domínio resolve corretamente, mas o navegador acusa certificado inválido. Que partes do caminho precisam ser verificadas? | `03_dns_tls_caminho_requisicao` | exclusiva | `03_dns_tls_caminho_requisicao/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L72–74) | 4. **Análise de custo:** um budget envia alerta ao ultrapassar um valor. Isso garante que recursos parem antes de surgir cobrança adicional? Explique. | `04_custos_orcamento_laboratorio` | exclusiva | `04_custos_orcamento_laboratorio/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L75–77) | 5. **Responsabilidade compartilhada:** ao escolher RDS em vez de instalar o banco numa VM EC2, quais tarefas operacionais diminuem e quais decisões continuam com quem usa a conta? | `01_conta_iam_responsabilidade` | exclusiva | `01_conta_iam_responsabilidade/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L80–96) | Desenhe a rede e rastreie uma requisição — proponha uma arquitetura mínima para uma aplicação web em AWS e explique o caminho de uma requisição. | `02_vpc_subnets_rotas_security_groups`, `03_dns_tls_caminho_requisicao` | compartilhada | `90_integracao/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L97–113) | Defina acesso e responsabilidades — dê à aplicação acesso mínimo ao storage e ao banco e identifique as responsabilidades de operação. | `01_conta_iam_responsabilidade`, `02_vpc_subnets_rotas_security_groups` | compartilhada | `90_integracao/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L114–130) | Estime, monitore e encerre um laboratório — planeje um laboratório seguro e documente custo provável e remoção completa. | `04_custos_orcamento_laboratorio` | exclusiva | `04_custos_orcamento_laboratorio/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Revisita SSH em 2.3, containers em 10.1 e segurança em 20.2–20.3. Prepara serviços gerenciados/mensageria em 35.1 e infraestrutura como código em 36.1.
- Pré-requisitos de unidade explicitamente declarados: nenhum identificado; valem também os pré-requisitos gerais da fase (Fases 1, 4 e 5).
- Referências individuais: 9 itens bibliográficos (12 links externos), consultados em 15/10/2026; preservar integralmente a seção da fonte.

### 35.1 — Serviços e eventos

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/35.1_Servicos_e_eventos.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/35.1_Servicos_e_eventos/` · **Arquivos previstos:** 23

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_contrato_sincrono_assincrono` — Contrato síncrono e processamento assíncrono | T1 — Requisição síncrona ou processamento assíncrono (L16–23; ~237 palavras) | Q02 | — | — | P01 |
| `02_filas_pubsub_event_routing` — Filas, pub/sub e roteamento de eventos | T2 — Escolha fila, pub/sub ou roteamento de evento (L24–33; ~312 palavras) | Q01, Q04 | — | — | P01, P02 |
| `03_confiabilidade_integracao_falhas` — Confiabilidade da integração e fronteiras de falha | T3 — Confiabilidade da integração e fronteiras de falha (L34–41; ~234 palavras) | Q03 | — | — | P02 |
| `04_cache_isolamento_custos` — Cache, isolamento de tenant e custos | T4 — Cache gerenciado, limites e custo (L42–49; ~236 palavras) | Q05 | — | P03 | — |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L60–65) | 1. **Múltipla escolha:** vários serviços precisam receber a mesma notificação, mas cada um deve processar no seu ritmo. Qual composição costuma atender melhor? A. Uma única chamada síncrona da API a todos os serviços em sequência. B. SNS distribuindo para uma fila SQS por consumidor. C. ElastiCache como fila persistente de eventos. | `02_filas_pubsub_event_routing` | exclusiva | `02_filas_pubsub_event_routing/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L66–68) | 2. **Contrato de API:** uma requisição coloca um relatório na fila e recebe `202 Accepted`. O que esse status deve significar ao cliente? | `01_contrato_sincrono_assincrono` | exclusiva | `01_contrato_sincrono_assincrono/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L69–71) | 3. **Diagnóstico de lote:** uma Lambda consome cinco mensagens de SQS; três foram processadas, uma falhou e a invocação lança erro. O que pode acontecer sem resposta parcial configurada? | `03_confiabilidade_integracao_falhas` | exclusiva | `03_confiabilidade_integracao_falhas/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L72–74) | 4. **Escolha de roteamento:** produtores emitem eventos de tipos diversos e consumidores querem assinar apenas os que correspondem a padrões de conteúdo, sem conhecer diretamente uns aos outros. Qual serviço considerar e qual condição de falha documentar? | `02_filas_pubsub_event_routing` | exclusiva | `02_filas_pubsub_event_routing/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L75–77) | 5. **Análise de cache:** a mesma chave `perfil:42` pode retornar dados de duas empresas diferentes. Qual risco existe e como corrigir? | `04_cache_isolamento_custos` | exclusiva | `04_cache_isolamento_custos/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L80–98) | Compare serviços por requisito — selecione serviços gerenciados para três fluxos e justifique a escolha com requisitos explícitos. | `01_contrato_sincrono_assincrono`, `02_filas_pubsub_event_routing` | compartilhada | `90_integracao/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L99–115) | Projete o fluxo com falhas e redrive — desenhe API Gateway → Lambda produtora → SQS → Lambda consumidora e acrescente um assinante de evento por SNS ou EventBridge. | `02_filas_pubsub_event_routing`, `03_confiabilidade_integracao_falhas` | compartilhada | `90_integracao/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L116–132) | Decida se precisa de cache — modele uma leitura frequente de catálogo ou perfil com e sem ElastiCache. | `04_cache_isolamento_custos` | exclusiva | `04_cache_isolamento_custos/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Reutiliza os fundamentos de mensageria, duplicação e DLQ de 33.1, além da rede e IAM de 34.1. Retoma cache em 15.1; prepara arquitetura como código em 36.1 e filas/RabbitMQ em 40.1.
- Pré-requisitos de unidade explicitamente declarados: nenhum identificado; valem também os pré-requisitos gerais da fase (Fases 1, 4 e 5).
- Referências individuais: 6 itens bibliográficos (9 links externos), consultados em 15/10/2026; preservar integralmente a seção da fonte.

### 36.1 — Infra como código

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/36.1_Infra_como_codigo.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/36.1_Infra_como_codigo/` · **Arquivos previstos:** 22

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_configuracao_providers_modulos` — Configuração, providers e módulos | T1 — Configuração declarativa e ciclo de trabalho (L16–23; ~197 palavras); T2 — Providers, módulos e entradas/saídas (L24–31; ~187 palavras) | Q05 | Q01 | P01 | — |
| `02_state_drift_colaboracao` — State, drift e colaboração | T3 — State, drift e colaboração (L32–39; ~216 palavras) | Q03, Q04 | Q01 | P03 | — |
| `03_plano_segredos_aprovacao` — Plano, segredos e aprovação de mudanças | T4 — Plano, segredo e aprovação de mudança (L40–47; ~209 palavras) | Q02 | — | P02 | — |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L58–60) | 1. **Classificação:** qual arquivo fixa a seleção/checksum de providers e qual arquivo mantém o vínculo com recursos da infraestrutura? | `01_configuracao_providers_modulos`, `02_state_drift_colaboracao` | compartilhada | `90_integracao/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L61–66) | 2. **Múltipla escolha:** `terraform plan` mostra `-/+` (substituição) num recurso de banco. Qual é a próxima ação mais segura? A. Aplicar imediatamente porque o plano não é destrutivo. B. Investigar por que a substituição é necessária, dados afetados, backup/recuperação e escopo da conta antes de aprovar. C. Editar state manualmente para remover a linha. | `03_plano_segredos_aprovacao` | exclusiva | `03_plano_segredos_aprovacao/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L67–69) | 3. **Diagnóstico de segredo:** variável marcada como `sensitive = true` apareceu no state compartilhado. Isso indica vazamento ou bug? | `02_state_drift_colaboracao` | exclusiva | `02_state_drift_colaboracao/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L70–72) | 4. **Análise de drift:** alguém mudou uma regra de rede diretamente no console e o plano propõe desfazer a mudança. O que fazer antes de aplicar? | `02_state_drift_colaboracao` | exclusiva | `02_state_drift_colaboracao/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L73–75) | 5. **Aplicação de fluxo:** um provider está dentro da restrição configurada, mas a equipe precisa reproduzir a versão instalada nos demais ambientes. Que recurso do Terraform ajuda e o que deve ser revisado ao atualizar? | `01_configuracao_providers_modulos` | exclusiva | `01_configuracao_providers_modulos/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L78–94) | Crie uma configuração pequena e rastreável — declare um recurso AWS de laboratório com entradas explícitas e uma interface simples de módulo. | `01_configuracao_providers_modulos` | exclusiva | `01_configuracao_providers_modulos/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L95–111) | Leia e aprove um plano de mudança — produza uma mudança controlada e decida se um plano está pronto para aplicação. | `03_plano_segredos_aprovacao` | exclusiva | `03_plano_segredos_aprovacao/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L112–128) | Proteja state e prepare colaboração/limpeza — escolha armazenamento e fluxo de colaboração apropriados ao estágio do laboratório. | `02_state_drift_colaboracao` | exclusiva | `02_state_drift_colaboracao/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Revisita versionamento em 3.1; depende de terminal em 2.1 e dos fundamentos de AWS/IAM/rede em 34.1. Prepara gestão de ambientes em 36.2 e configuração de cloud para deploys posteriores.
- Pré-requisitos de unidade explicitamente declarados: 2.1, 34.1.
- Referências individuais: 6 itens bibliográficos (9 links externos), consultados em 15/10/2026; preservar integralmente a seção da fonte.

### 36.2 — Ambientes

**Origem:** `docs/courses/trilhacode/Conteudos/Fase_7/36.2_Ambientes.md` · **Destino proposto:** `docs/courses/trilhacode/Conteudos_migrado/Fase_7/36.2_Ambientes/` · **Arquivos previstos:** 22

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivas | Q compartilhadas | P exclusivas | P compartilhadas |
|---|---|---|---|---|---|
| `01_ambientes_state_isolamento` — Ambientes, state e isolamento | T1 — Defina o que muda e o que fica isolado (L16–23; ~200 palavras); T2 — Separe configuração, state e permissões Terraform (L24–43; ~283 palavras) | Q01, Q02 | — | P01 | P02 |
| `02_pipeline_identidade_gates` — Pipeline, identidade e gates | T3 — Promova mudanças com identidade e gates (L44–53; ~308 palavras) | Q03, Q04 | — | — | P02, P03 |
| `03_custo_recuperacao_encerramento` — Custo, recuperação e encerramento | T4 — Custo, recuperação e encerramento do ciclo (L54–61; ~203 palavras) | Q05 | — | — | P03 |

**Questões individuais:**

| Item | Habilidade avaliada no enunciado original | Assunto(s) | Classe | Arquivo Q | Gabarito existente |
|---|---|---|---|---|---|
| Q01 (L72–74) | 1. **Classificação:** dev e staging usam `dev.tfvars` e `staging.tfvars`, mas a mesma role com permissão de administrar todos os recursos e o mesmo state. Estão isolados? | `01_ambientes_state_isolamento` | exclusiva | `01_ambientes_state_isolamento/Q01_quiz.md` | sim, inline na fonte |
| Q02 (L75–80) | 2. **Múltipla escolha:** quando workspace da Terraform CLI é uma opção razoável? A. Para criar cópias temporárias e semelhantes que compartilham configuração/backend, após conferir o workspace selecionado. B. Para garantir fronteira de credenciais entre produção e desenvolvimento. C. Para dispensar backend protegido em equipe. | `01_ambientes_state_isolamento` | exclusiva | `01_ambientes_state_isolamento/Q02_quiz.md` | sim, inline na fonte |
| Q03 (L81–83) | 3. **Rastreabilidade:** o pipeline gera um plano de staging, alguém altera configuração/state e depois executa o plano antigo. O que fazer? | `02_pipeline_identidade_gates` | exclusiva | `02_pipeline_identidade_gates/Q03_quiz.md` | sim, inline na fonte |
| Q04 (L84–86) | 4. **Segurança de credencial:** cite os dois lados necessários para usar OIDC com AWS e uma restrição que reduz o risco de outra execução obter a role. | `02_pipeline_identidade_gates` | exclusiva | `02_pipeline_identidade_gates/Q04_quiz.md` | sim, inline na fonte |
| Q05 (L87–89) | 5. **Análise de encerramento:** após `terraform destroy`, a aplicação parou, mas custos continuam aparecendo. Que recursos e processo verificar? | `03_custo_recuperacao_encerramento` | exclusiva | `03_custo_recuperacao_encerramento/Q05_quiz.md` | sim, inline na fonte |

**Práticas individuais:**

| Item | Atividade/desafio original | Assunto(s) | Classe | Arquivo P | Solução/rubrica/aceite |
|---|---|---|---|---|---|
| P01 (L92–108) | Modele ambientes e limites de state — prepare uma estrutura para `dev`, `staging` e `prod`, mantendo dev/staging executáveis apenas em sandbox e deixando produção documentada sem aplicar. | `01_ambientes_state_isolamento` | exclusiva | `01_ambientes_state_isolamento/P01_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P02 (L109–126) | Construa pipeline Terraform + deploy para staging — integre a infraestrutura e aplicação da Fase 7 numa promoção auditável para staging. | `01_ambientes_state_isolamento`, `02_pipeline_identidade_gates` | compartilhada | `90_integracao/P02_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |
| P03 (L127–144) | Faça rollback controlado e encerre o laboratório — provar que a equipe consegue interromper uma versão problemática e remover o ambiente temporário sem apagar evidência necessária. | `02_pipeline_identidade_gates`, `03_custo_recuperacao_encerramento` | compartilhada | `90_integracao/P03_pratica.md` | solução/rubrica separadas: não; aceite/evidências/verificação: embutidos |

**Conexões, pré-requisitos e referências:**

- Relações declaradas: Complementa Terraform e state de 36.1; entrega em staging aplica conceitos de pipeline de 32.1–32.2 e de IAM/rede/custos de 34.1. Terragrunt permanece repertório quando o número de stacks justifica coordenação adicional.
- Pré-requisitos de unidade explicitamente declarados: nenhum identificado; valem também os pré-requisitos gerais da fase (Fases 1, 4 e 5).
- Referências individuais: 6 itens bibliográficos (7 links externos), consultados em 15/10/2026; preservar integralmente a seção da fonte.

## Resumo de cobertura E/S/N

E = assunto com ao menos um item exclusivo; S = assunto sem item exclusivo, coberto apenas por item compartilhado; N = sem Q/P. As categorias são mutuamente exclusivas por assunto.

| Unidade | Assuntos | E | S-only | N |
|---|---:|---:|---:|---:|
| 32.1 | 2 | 2 | 0 | 0 |
| 32.2 | 4 | 4 | 0 | 0 |
| 33.1 | 3 | 3 | 0 | 0 |
| 34.1 | 4 | 4 | 0 | 0 |
| 35.1 | 4 | 4 | 0 | 0 |
| 36.1 | 3 | 3 | 0 | 0 |
| 36.2 | 3 | 3 | 0 | 0 |

**Resultado:** 23/23 assuntos têm ao menos uma verificação exclusiva; nenhum assunto depende exclusivamente de item compartilhado e nenhum fica sem Q/P. Itens compartilhados continuam complementares.

## Arquivos auxiliares 37.1 e 37.2

| Cópia sob `Conteudos/Fase_7` | Evidência de status na página F7/F8 | Comparação da fonte | Ação deste plano |
|---|---|---|---|
| `37.1_Servicos_gerenciados.md` | A página F7 não lista Módulo 37; a página F8 lista 37.1 no Módulo 37 e a versão F8 tem `carater: repertorio`, `profundidade: repertorio`, 45 min. | Cópia F7: `obrigatorio`, `media`, 45 min, 3 microtópicos e 2 atividades curtas; cópia F8: repertório, síntese comparativa e 3 flashcards. | Excluir do conjunto ativo planejado de F7; original intacto. Não chamar de aposentado formalmente; destino editorial pendente. |
| `37.2_Kubernetes_basico.md` | A página F7 não lista 37.2; a página F8 lista 37.2 no Módulo 37 e a versão F8 tem `carater: repertorio`, `profundidade: repertorio`, 45 min. | Cópia F7: `obrigatorio`, `media`, 45 min, 3 microtópicos e 2 atividades curtas; cópia F8: repertório, síntese e 3 flashcards. | Mesmo tratamento: fora da árvore F7, sem remover ou mover original. A aposentadoria das cópias não está formalizada nas fontes encontradas. |

A página `CHANGELOG_Correcoes.md` não existe nesse diretório do curso. A evidência de escopo vem da lista explícita de módulos da página F7 e da listagem/metadata das versões F8; não há prova suficiente para classificar as cópias F7 como oficialmente aposentadas.

## Projeto incremental da fase

- A seção “Projeto incremental” da página da fase traz literalmente: “Deploy automatizado do projeto na AWS com Terraform e pipeline.” e remete a 36.2.
- A prática existente que detalha esse objetivo é **36.2/P02 — “Construa pipeline Terraform + deploy para staging”**; o desafio, evidências, verificação e aceite já estão no enunciado.
- Não existem unidade de projeto separada, marcos formais, checklist final nem rubrica geral em F7. A representação no manifesto é só uma referência de fase para P02, sem novo arquivo/nó/critério.
- Dependências explícitas e relações de 36.2 permanecem registradas a partir da fonte; a continuidade de um único projeto desde unidades anteriores não é adicionada.
- **[PROPOSTA]** Marcos progressivos ou rubrica transversal exigiriam aprovação pedagógica futura; não são parte da migração estrutural.

## Árvore proposta

Cada unidade terá `README.md` com os metadados originais no frontmatter e links relativos para os arquivos. Cinco arquivos comuns ficam separados (`00_objetivo.md`, `01_resumo.md`, `02_criterio_de_conclusao.md`, `03_conexoes.md`, `04_referencias.md`). Pastas de assunto planas, sem README individual. Os assuntos compartilhados usam `90_integracao/` com um arquivo físico por item.

### `32.1_Automacao/` — 21 arquivos

```text
32.1_Automacao/
  00_objetivo.md
  01_resumo.md
  01_workflow_reprodutibilidade_quality_gates/01_teoria.md
  01_workflow_reprodutibilidade_quality_gates/K01_gabarito_quiz.md
  01_workflow_reprodutibilidade_quality_gates/K02_gabarito_quiz.md
  01_workflow_reprodutibilidade_quality_gates/K03_gabarito_quiz.md
  01_workflow_reprodutibilidade_quality_gates/P02_pratica.md
  01_workflow_reprodutibilidade_quality_gates/Q01_quiz.md
  01_workflow_reprodutibilidade_quality_gates/Q02_quiz.md
  01_workflow_reprodutibilidade_quality_gates/Q03_quiz.md
  02_criterio_de_conclusao.md
  02_seguranca_actions_falhas/01_teoria.md
  02_seguranca_actions_falhas/K04_gabarito_quiz.md
  02_seguranca_actions_falhas/K05_gabarito_quiz.md
  02_seguranca_actions_falhas/P03_pratica.md
  02_seguranca_actions_falhas/Q04_quiz.md
  02_seguranca_actions_falhas/Q05_quiz.md
  03_conexoes.md
  04_referencias.md
  90_integracao/P01_pratica.md
  README.md
```

### `32.2_Entrega/` — 23 arquivos

```text
32.2_Entrega/
  00_objetivo.md
  01_identidade_do_artefato/01_teoria.md
  01_identidade_do_artefato/K01_gabarito_quiz.md
  01_identidade_do_artefato/Q01_quiz.md
  01_resumo.md
  02_ambientes_autorizacao_promocao/01_teoria.md
  02_ambientes_autorizacao_promocao/K03_gabarito_quiz.md
  02_ambientes_autorizacao_promocao/Q03_quiz.md
  02_criterio_de_conclusao.md
  03_conexoes.md
  03_saude_pos_deploy/01_teoria.md
  03_saude_pos_deploy/K02_gabarito_quiz.md
  03_saude_pos_deploy/Q02_quiz.md
  04_referencias.md
  04_rollback_schema_dados/01_teoria.md
  04_rollback_schema_dados/K04_gabarito_quiz.md
  04_rollback_schema_dados/K05_gabarito_quiz.md
  04_rollback_schema_dados/P03_pratica.md
  04_rollback_schema_dados/Q04_quiz.md
  04_rollback_schema_dados/Q05_quiz.md
  90_integracao/P01_pratica.md
  90_integracao/P02_pratica.md
  README.md
```

### `33.1_Conceitos/` — 22 arquivos

```text
33.1_Conceitos/
  00_objetivo.md
  01_modelos_mensageria_entrega/01_teoria.md
  01_modelos_mensageria_entrega/K01_gabarito_quiz.md
  01_modelos_mensageria_entrega/K02_gabarito_quiz.md
  01_modelos_mensageria_entrega/Q01_quiz.md
  01_modelos_mensageria_entrega/Q02_quiz.md
  01_resumo.md
  02_criterio_de_conclusao.md
  02_retry_backoff_dlq/01_teoria.md
  02_retry_backoff_dlq/K04_gabarito_quiz.md
  02_retry_backoff_dlq/Q04_quiz.md
  03_conexoes.md
  03_idempotencia_outbox_consistencia/01_teoria.md
  03_idempotencia_outbox_consistencia/K03_gabarito_quiz.md
  03_idempotencia_outbox_consistencia/K05_gabarito_quiz.md
  03_idempotencia_outbox_consistencia/P02_pratica.md
  03_idempotencia_outbox_consistencia/Q03_quiz.md
  03_idempotencia_outbox_consistencia/Q05_quiz.md
  04_referencias.md
  90_integracao/P01_pratica.md
  90_integracao/P03_pratica.md
  README.md
```

### `34.1_Base_de_cloud/` — 23 arquivos

```text
34.1_Base_de_cloud/
  00_objetivo.md
  01_conta_iam_responsabilidade/01_teoria.md
  01_conta_iam_responsabilidade/K02_gabarito_quiz.md
  01_conta_iam_responsabilidade/K05_gabarito_quiz.md
  01_conta_iam_responsabilidade/Q02_quiz.md
  01_conta_iam_responsabilidade/Q05_quiz.md
  01_resumo.md
  02_criterio_de_conclusao.md
  02_vpc_subnets_rotas_security_groups/01_teoria.md
  02_vpc_subnets_rotas_security_groups/K01_gabarito_quiz.md
  02_vpc_subnets_rotas_security_groups/Q01_quiz.md
  03_conexoes.md
  03_dns_tls_caminho_requisicao/01_teoria.md
  03_dns_tls_caminho_requisicao/K03_gabarito_quiz.md
  03_dns_tls_caminho_requisicao/Q03_quiz.md
  04_custos_orcamento_laboratorio/01_teoria.md
  04_custos_orcamento_laboratorio/K04_gabarito_quiz.md
  04_custos_orcamento_laboratorio/P03_pratica.md
  04_custos_orcamento_laboratorio/Q04_quiz.md
  04_referencias.md
  90_integracao/P01_pratica.md
  90_integracao/P02_pratica.md
  README.md
```

### `35.1_Servicos_e_eventos/` — 23 arquivos

```text
35.1_Servicos_e_eventos/
  00_objetivo.md
  01_contrato_sincrono_assincrono/01_teoria.md
  01_contrato_sincrono_assincrono/K02_gabarito_quiz.md
  01_contrato_sincrono_assincrono/Q02_quiz.md
  01_resumo.md
  02_criterio_de_conclusao.md
  02_filas_pubsub_event_routing/01_teoria.md
  02_filas_pubsub_event_routing/K01_gabarito_quiz.md
  02_filas_pubsub_event_routing/K04_gabarito_quiz.md
  02_filas_pubsub_event_routing/Q01_quiz.md
  02_filas_pubsub_event_routing/Q04_quiz.md
  03_conexoes.md
  03_confiabilidade_integracao_falhas/01_teoria.md
  03_confiabilidade_integracao_falhas/K03_gabarito_quiz.md
  03_confiabilidade_integracao_falhas/Q03_quiz.md
  04_cache_isolamento_custos/01_teoria.md
  04_cache_isolamento_custos/K05_gabarito_quiz.md
  04_cache_isolamento_custos/P03_pratica.md
  04_cache_isolamento_custos/Q05_quiz.md
  04_referencias.md
  90_integracao/P01_pratica.md
  90_integracao/P02_pratica.md
  README.md
```

### `36.1_Infra_como_codigo/` — 22 arquivos

```text
36.1_Infra_como_codigo/
  00_objetivo.md
  01_configuracao_providers_modulos/01_teoria.md
  01_configuracao_providers_modulos/K05_gabarito_quiz.md
  01_configuracao_providers_modulos/P01_pratica.md
  01_configuracao_providers_modulos/Q05_quiz.md
  01_resumo.md
  02_criterio_de_conclusao.md
  02_state_drift_colaboracao/01_teoria.md
  02_state_drift_colaboracao/K03_gabarito_quiz.md
  02_state_drift_colaboracao/K04_gabarito_quiz.md
  02_state_drift_colaboracao/P03_pratica.md
  02_state_drift_colaboracao/Q03_quiz.md
  02_state_drift_colaboracao/Q04_quiz.md
  03_conexoes.md
  03_plano_segredos_aprovacao/01_teoria.md
  03_plano_segredos_aprovacao/K02_gabarito_quiz.md
  03_plano_segredos_aprovacao/P02_pratica.md
  03_plano_segredos_aprovacao/Q02_quiz.md
  04_referencias.md
  90_integracao/K01_gabarito_quiz.md
  90_integracao/Q01_quiz.md
  README.md
```

### `36.2_Ambientes/` — 22 arquivos

```text
36.2_Ambientes/
  00_objetivo.md
  01_ambientes_state_isolamento/01_teoria.md
  01_ambientes_state_isolamento/K01_gabarito_quiz.md
  01_ambientes_state_isolamento/K02_gabarito_quiz.md
  01_ambientes_state_isolamento/P01_pratica.md
  01_ambientes_state_isolamento/Q01_quiz.md
  01_ambientes_state_isolamento/Q02_quiz.md
  01_resumo.md
  02_criterio_de_conclusao.md
  02_pipeline_identidade_gates/01_teoria.md
  02_pipeline_identidade_gates/K03_gabarito_quiz.md
  02_pipeline_identidade_gates/K04_gabarito_quiz.md
  02_pipeline_identidade_gates/Q03_quiz.md
  02_pipeline_identidade_gates/Q04_quiz.md
  03_conexoes.md
  03_custo_recuperacao_encerramento/01_teoria.md
  03_custo_recuperacao_encerramento/K05_gabarito_quiz.md
  03_custo_recuperacao_encerramento/Q05_quiz.md
  04_referencias.md
  90_integracao/P02_pratica.md
  90_integracao/P03_pratica.md
  README.md
```

## Propostas pedagógicas futuras

- **[PROPOSTA] Cópias 37.1/37.2:** decidir separadamente se as cópias obrigatórias da pasta F7 serão arquivadas ou removidas. Não incluí-las na árvore F7 se mantida a lista atual da página oficial; nenhuma fonte as marca formalmente aposentadas.
- **[PROPOSTA] Atualização de referências voláteis:** revalidar AWS Free Tier/planos, preços e disponibilidade regional (34.1/35.1), releases/versões de GitHub Actions (32.1/32.2) e versões/integrações Terraform (36.x). Manter `consultado_em` por referência; datas existentes são 14–15/10/2026.
- Nenhum assunto proposto fica sem avaliação exclusiva após os agrupamentos; não há lacuna que exija criar exercício para justificar a estrutura. Compartilhamentos integradores permanecem complementares. Não foram criados novos quizzes, práticas ou respostas.

## Estimativa de arquivos

| Unidade | README | Comuns | Teoria | Quiz | Gabarito | Prática | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| 32.1 | 1 | 5 | 2 | 5 | 5 | 3 | 21 |
| 32.2 | 1 | 5 | 4 | 5 | 5 | 3 | 23 |
| 33.1 | 1 | 5 | 3 | 5 | 5 | 3 | 22 |
| 34.1 | 1 | 5 | 4 | 5 | 5 | 3 | 23 |
| 35.1 | 1 | 5 | 4 | 5 | 5 | 3 | 23 |
| 36.1 | 1 | 5 | 3 | 5 | 5 | 3 | 22 |
| 36.2 | 1 | 5 | 3 | 5 | 5 | 3 | 22 |

| Tipo | Quantidade |
|---|---:|
| README/índice | 7 |
| Arquivos comuns | 35 |
| Teoria (23 assuntos; 28 microtópicos preservados) | 23 |
| Quiz | 35 |
| Gabarito de quiz extraído da resposta inline | 35 |
| Prática com aceite/evidências/verificação existentes | 21 |
| Solução separada / rubrica separada / checklist independente / flashcard | 0 |
| **Total** | **156** |

Há 13 arquivos físicos em `90_integracao/`: Q/K da questão compartilhada 36.1/Q1 (2 arquivos) e onze práticas compartilhadas (11 arquivos). As fontes contêm 126 blocos de origem distintos (42 seções comuns, 28 microtópicos, 35 questões, 21 práticas). Os gabaritos são um segundo destino para as 35 respostas inline: 161 associações bloco-destino no total.

## Validação interna do rascunho

- Sete fontes/unidades ativas; 23 assuntos propostos; 28 microtópicos; 35 questões e respectivas 35 respostas; 21 práticas.
- Cada bloco teórico recebe destino; todas as questões e práticas aparecem uma vez na tabela de cobertura. Itens compartilhados têm um só caminho em `90_integracao/` e são associados a todos os assuntos envolvidos.
- `arquivo_id` global único com prefixo `f7`, caminhos planejados únicos, aliases Q/K/P válidos, gabarito associado à questão de origem e limites de linha dentro das fontes.
- Nenhum arquivo 37.1/37.2 entra nas unidades ou na árvore prevista.
- Nenhum conteúdo migrado foi gerado. Links do índice são relativos aos arquivos planejados e seus destinos foram conferidos no manifesto; não existem wikilinks nas sete unidades-fonte. A página da fase e seus wikilinks permanecem fora do escopo; a raiz do vault não está confirmada.
- Estado observado depois do commit F6: branch `migracao-estrutura`, HEAD `53956919fc145e897f5ac7763513812b03f04dba`, índice vazio, nenhum diff rastreado. Permanecem três arquivos não rastreados preexistentes fora do escopo: `Guia_de_Producao_de_Conteudo.md`, `PLANEJAMENTO_FASE5.md` e `PLANEJAMENTO_FASE6.md`. Os dois documentos F7 serão novos e não commitados.

## Pendências para aprovação

1. Aprovar ou ajustar os 23 agrupamentos [PROPOSTA] e a classificação Q/P antes de futura geração.
2. Decidir posteriormente o tratamento editorial das cópias 37.1/37.2 que não aparecem na lista da Fase 7.
3. Revalidar as referências com datas de outubro de 2026 antes de publicação futura.
4. Integrar wikilinks ao vault somente quando sua raiz for conhecida.
