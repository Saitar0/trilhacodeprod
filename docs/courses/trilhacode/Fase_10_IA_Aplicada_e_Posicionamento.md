---
title: "Fase 10 — IA aplicada, fechamento técnico e posicionamento"
aliases:
  - Fase 10
tags:
  - trilhas
  - fase
tipo: fase
ordem: 10
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 10 — IA aplicada, fechamento técnico e posicionamento

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Integrar IA a uma aplicação de forma segura, mensurável e proporcional, fechar o projeto final e preparar o posicionamento profissional.

## Por que esta fase vem agora?
IA aplicada reutiliza contratos, segurança, filas, observabilidade e custo estudados antes; por isso vem por último, como extensão do projeto acumulado e não como assunto isolado.

## Pré-requisitos
Fases 5 a 9, em especial autenticação e autorização (20.x), observabilidade (38.x) e filas ([[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]] e 40.x).

## Competências
- Usar assistentes e agentes de código com revisão crítica
- Integrar provedores de modelos com streaming, custo e latência
- Implementar RAG quando houver necessidade real
- Expor ações a modelos com contratos tipados e autorização
- Identificar riscos de prompt injection e vazamento de dados
- Apresentar projetos e decisões em currículo e entrevistas

## Projeto incremental
Expandir o projeto incremental acumulado (e não começar do zero) até uma aplicação full stack com IA. Detalhado em [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1 Estrutura do projeto final]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_10_IA_Aplicada_e_Posicionamento#52.2 — Projeto de fase (Trilho B)|52.2 Projeto de fase (Trilho B)]].

## Critério de conclusão
Aplicação full stack com funcionalidade de IA, testes, CI/CD, deploy na AWS, observabilidade, README e diagrama de arquitetura, evoluída a partir do projeto acumulado.

## Estimativa de carga horária

**Total estimado da fase:** 60,5–105,5 h (referência de planejamento: 83 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 47 — Desenvolvimento assistido por IA|Módulo 47 — Desenvolvimento assistido por IA]]
- [[#Módulo 48 — Modelos de linguagem em aplicações|Módulo 48 — Modelos de linguagem em aplicações]]
- [[#Módulo 49 — Embeddings e RAG|Módulo 49 — Embeddings e RAG]]
- [[#Módulo 50 — Orquestração e agentes|Módulo 50 — Orquestração e agentes]]
- [[#Módulo 51 — Segurança e governança em IA|Módulo 51 — Segurança e governança em IA]]
- [[#Módulo 52 — Projeto final|Módulo 52 — Projeto final]]
- [[#Módulo 53 — Posicionamento profissional|Módulo 53 — Posicionamento profissional]]

---

## Módulo 47 — Desenvolvimento assistido por IA

**Objetivo:** Usar assistentes e agentes de código para acelerar uma tarefa delimitada, mantendo responsabilidade por requisitos, revisão, segurança e validação do resultado.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#47.1 — Uso assistido|47.1 Uso assistido]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 47.1 — Uso assistido

**Classificação:** `pratica` · `obrigatorio` · `media` · #ia #ferramentas

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Usar assistentes e agentes de código para acelerar uma tarefa delimitada, mantendo responsabilidade por requisitos, revisão, segurança e validação do resultado.

**Tópicos:**
- [ ] Copilot
- [ ] assistentes de código
- [ ] agentes de código
- [ ] boas práticas de prompt
- [ ] revisão crítica do código gerado

**Atividade prática:** Escolha uma melhoria pequena e segura em um repositório de estudo. Escreva requisito e critérios antes de usar o assistente; peça plano e alteração limitada; examine o diff; valide contra os critérios; registre uma sugestão aceita, uma rejeitada e por quê. Não inclua segredos ou dados reais.

**Critério de conclusão:** Entregar mudança que atende aos critérios, explicar cada parte aceita e documentar ao menos uma correção ou rejeição de sugestão da ferramenta.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]], [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]]

---

## Módulo 48 — Modelos de linguagem em aplicações

**Objetivo:** Integrar um provedor de modelo ao backend com credencial protegida, limites explícitos e tratamento de falha, justificando a escolha para um caso de uso.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#48.1 — Fundamentos|48.1 Fundamentos]] · [[Fase_10_IA_Aplicada_e_Posicionamento#48.2 — Operação|48.2 Operação]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 48.1 — Fundamentos

**Classificação:** `solo` · `obrigatorio` · `media` · #ia

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Integrar um provedor de modelo ao backend com credencial protegida, limites explícitos e tratamento de falha, justificando a escolha para um caso de uso.

**Tópicos:**
- [ ] OpenAI
- [ ] Claude
- [ ] Azure OpenAI — *repertorio*
- [ ] Vertex AI — *repertorio*

**Atividade prática:** Implemente uma rota de backend que chama um único provedor para uma entrada sintética. Injete cliente/configuração, defina timeout e limite de entrada, trate rate limit e falha e mantenha a credencial fora do código. Registre latência e custo estimado sem gravar o conteúdo. Explique como substituiria o provedor.

**Critério de conclusão:** Chamada executável no backend sem chave exposta, com limites e erros tratados; estudante explica autenticação, unidade de custo, latência e a razão da escolha.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

### 48.2 — Operação

**Classificação:** `integrado` · `obrigatorio` · `media` · #ia #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Entregar respostas de modelo progressivamente pela interface e operar a chamada com cancelamento, limites, custo e latência observáveis.

**Tópicos:**
- [ ] engenharia de prompt
- [ ] streaming
- [ ] SSE e streaming no navegador
- [ ] custo
- [ ] latência

**Atividade prática:** Adicione ao app uma resposta em streaming com SSE. Implemente os estados da interface, cancelamento, timeout, falha e limite máximo. Meça tempo até primeiro fragmento, duração total e custo aproximado com dados sintéticos; mostre como os dados são protegidos de logs.

**Critério de conclusão:** Interface trata conclusão, erro e cancelamento sem ficar presa; há medição de latência e custo e limites de uso documentados.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#27.2 — Estados de interface|27.2]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]]

---

## Módulo 49 — Embeddings e RAG

**Objetivo:** Construir e avaliar um fluxo RAG pequeno que ingere documentos, recupera trechos pertinentes e gera resposta com citações verificáveis.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#49.1 — Base|49.1 Base]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 49.1 — Base

**Classificação:** `integrado` · `obrigatorio` · `media` · #ia #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Construir e avaliar um fluxo RAG pequeno que ingere documentos, recupera trechos pertinentes e gera resposta com citações verificáveis.

**Tópicos:**
- [ ] embeddings
- [ ] upload e ingestão de documentos
- [ ] bancos vetoriais
- [ ] chunking
- [ ] busca semântica
- [ ] avaliação de respostas

**Atividade prática:** Use documentos públicos ou sintéticos. Implemente ingestão com chunking, armazenamento de vetor e metadados, busca top-k e resposta com citações para IDs/trechos recuperados. Prepare pelo menos dez perguntas: respostas cobertas, sem resposta e documentos com instrução hostil. Registre resultados de recuperação e revise manualmente fundamentação e citações.

**Critério de conclusão:** Pipeline recupera trechos com origem, apresenta citação que abre o material correspondente e demonstra avaliação com casos cobertos e não cobertos, incluindo falha de recuperação ou resposta sem suporte.

**Relações:** Relacionado: [[Fase_4_Dados_e_Bancos#9.1 — Conceitos|9.1]], [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]], [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1]]

---

## Módulo 50 — Orquestração e agentes

**Objetivo:** Expor ao modelo uma operação de domínio por contrato tipado, validar parâmetros e autorização no backend e decidir com evidência se um framework de orquestração é necessário.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#50.1 — Orquestração|50.1 Orquestração]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 50.1 — Orquestração

**Classificação:** `solo` · `obrigatorio` · `media` · #ia #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Expor ao modelo uma operação de domínio por contrato tipado, validar parâmetros e autorização no backend e decidir com evidência se um framework de orquestração é necessário.

**Tópicos:**
- [ ] function calling
- [ ] LangChain
- [ ] LangGraph
- [ ] Semantic Kernel — *repertorio*
- [ ] CrewAI — *repertorio*

**Atividade prática:** Implemente ferramenta `consultar_pedido` ou `listar_tarefas` apenas de leitura com contrato tipado. Faça validação no servidor, derive usuário autenticado da sessão, limite resultado e teste argumento inválido e tentativa de acessar registro de outro usuário. Esboce como mudaria para uma ação de escrita que exige confirmação.

**Critério de conclusão:** Uma chamada tipada executa somente após validação e autorização; tentativa inválida ou não autorizada falha sem revelar dados, e a decisão de framework é explicada.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]], [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_10_IA_Aplicada_e_Posicionamento#49.1 — Base|49.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1]]

---

## Módulo 51 — Segurança e governança em IA

**Objetivo:** Modelar ameaças de uma funcionalidade com IA, localizar fronteiras de confiança e aplicar controles no sistema para limitar prompt injection, exposição de dados e ações não autorizadas.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1 Segurança e governança]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 51.1 — Segurança e governança

**Classificação:** `integrado` · `obrigatorio` · `media` · #ia #seguranca

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Modelar ameaças de uma funcionalidade com IA, localizar fronteiras de confiança e aplicar controles no sistema para limitar prompt injection, exposição de dados e ações não autorizadas.

**Tópicos:**
- [ ] Model Context Protocol
- [ ] prompt injection
- [ ] vazamento de credenciais
- [ ] guardrails
- [ ] governança de dados
- [ ] privacidade e LGPD aplicadas a IA: dados pessoais em prompts, retenção e exclusão

**Atividade prática:** Escolha assistente RAG ou tool-calling e produza diagrama de fluxo e tabela com ativo, ameaça, caminho, impacto, controle preventivo, detecção e resposta. Inclua documento malicioso, usuário tentando acessar outro tenant, vazamento em log e ação indevida. Demonstre pelo menos um controle com teste ou cenário reproduzível. Liste dados pessoais, finalidade, minimização e retenção sem inserir dados reais.

**Critério de conclusão:** Modelo de ameaças identifica ao menos três caminhos relevantes e relaciona cada um a controle verificável; inclui autorização fora do LLM e análise de dados/retenção.

**Relações:** Relacionado: [[Fase_5_Backend_e_Arquitetura#20.3 — Segurança aplicada|20.3]], [[Fase_10_IA_Aplicada_e_Posicionamento#49.1 — Base|49.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#50.1 — Orquestração|50.1]]

---

## Módulo 52 — Projeto final

**Objetivo:** Expandir o projeto principal acumulado desde a Fase 1 até uma aplicação full stack com IA, demonstrando necessidade do produto, segurança, qualidade, operação e decisões técnicas.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1 Estrutura do projeto final]] · [[Fase_10_IA_Aplicada_e_Posicionamento#52.2 — Projeto de fase (Trilho B)|52.2 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 52.1 — Estrutura do projeto final

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 30 h–50 h (referência: 40 h).

**Objetivo:** Expandir o projeto principal acumulado desde a Fase 1 até uma aplicação full stack com IA, demonstrando necessidade do produto, segurança, qualidade, operação e decisões técnicas.

**Tópicos:**
- [ ] app fullstack com IA
- [ ] frontend React
- [ ] backend estruturado
- [ ] banco relacional
- [ ] cache
- [ ] fila
- [ ] Docker
- [ ] testes
- [ ] CI/CD
- [ ] deploy em AWS
- [ ] Terraform
- [ ] observabilidade
- [ ] README
- [ ] diagrama de arquitetura
- [ ] cada capacidade justificada por necessidade do produto ou por experimento isolado documentado
- [ ] expandir o projeto incremental acumulado, não começar do zero

**Atividade prática:** Atualize o README com problema e público, desenhe arquitetura atual e alvo, registre ADR para uma decisão de IA e escreva critérios verificáveis. Implemente uma fatia pequena no projeto principal, acrescente testes de fluxo e falha, custos/latência e barreiras de autorização. Prepare um experimento separado para qualquer capacidade sem necessidade de produto.

**Critério de conclusão:** Projeto acumulado atende aos critérios de aceite justificados, tem funcionalidade de IA avaliada, testes, CI/CD, deploy AWS, Terraform, observabilidade, README e diagrama; limitações e decisões estão registradas.

**Relações:** Complementar: [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2]], [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2]], [[Fase_10_IA_Aplicada_e_Posicionamento#49.1 — Base|49.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#48.2 — Operação|48.2]], [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1]]

### 52.2 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto #ia

**Carga horária estimada:** 20 h–35 h (referência: 27,5 h).

**Objetivo:** Entregar uma variante T6 autocontida com assistente RAG ou ferramenta autorizada, avaliação em conjunto de casos, custo e latência medidos e modelo de ameaças curto.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Construa o menor protótipo útil para uma das três variações com conteúdo sintético. Execute o conjunto de avaliação antes e depois de uma mudança; registre resultado, custo e latência. Simule acesso a conteúdo de outro usuário e uma instrução maliciosa no documento. Faça uma ADR curta e explique o que não foi validado.

**Critério de conclusão:** Protótipo T6 executável demonstra recuperação citada ou tool calling autorizado, conjunto de avaliação reproduzível, medição de custo e latência e modelo de ameaças curto com controles verificáveis. Cobertura T1–T5 é registrada separadamente.

**Relações:** Complementar: [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#49.1 — Base|49.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#50.1 — Orquestração|50.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#51.1 — Segurança e governança|51.1]]

---

## Módulo 53 — Posicionamento profissional

**Objetivo:** Apresentar projetos e competências com evidências verificáveis em currículo, LinkedIn e GitHub, sem exagerar experiência, impacto ou autoria.

**Submódulos:** [[Fase_10_IA_Aplicada_e_Posicionamento#53.1 — Portfólio e presença|53.1 Portfólio e presença]] · [[Fase_10_IA_Aplicada_e_Posicionamento#53.2 — Inglês técnico e entrevistas|53.2 Inglês técnico e entrevistas]] · [[Fase_10_IA_Aplicada_e_Posicionamento#53.3 — System design|53.3 System design]] · [[Fase_10_IA_Aplicada_e_Posicionamento#53.4 — Algoritmos para entrevistas técnicas|53.4 Algoritmos para entrevistas técnicas]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 53.1 — Portfólio e presença

**Classificação:** `solo` · `obrigatorio` · `media` · #mercado

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Apresentar projetos e competências com evidências verificáveis em currículo, LinkedIn e GitHub, sem exagerar experiência, impacto ou autoria.

**Tópicos:**
- [ ] currículo
- [ ] LinkedIn
- [ ] GitHub organizado (repositórios fixados, READMEs e histórico)
- [ ] apresentar cada projeto: problema, decisões, trade-offs e métricas

**Atividade prática:** Escolha dois projetos do curso. Para cada um, escreva um README conciso com problema, escopo, arquitetura, decisões, execução, testes, evidência e limitações. Prepare três bullets de currículo com ação, contexto e resultado verificável. Revise repositório para remover segredos e deixe claro que são projetos educacionais.

**Critério de conclusão:** Portfólio contém ao menos dois projetos demonstráveis com README executável, contribuição delimitada, decisão técnica e resultado/limitação verificáveis; currículo e perfil não fazem afirmações sem suporte.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3]], [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#53.2 — Inglês técnico e entrevistas|53.2]]

### 53.2 — Inglês técnico e entrevistas

**Classificação:** `solo` · `obrigatorio` · `media` · #mercado

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Explicar projetos e decisões técnicas em inglês com estrutura, vocabulário claro e capacidade de responder a perguntas de acompanhamento.

**Tópicos:**
- [ ] inglês de entrevista: apresentação pessoal e explicação de decisões
- [ ] respostas comportamentais estruturadas (situação, ação e resultado)
- [ ] escrita técnica em inglês (PRs, ADRs e README)
- [ ] entrevistas simuladas, com gravação e revisão

**Atividade prática:** Grave uma apresentação de dois minutos de um projeto em inglês e uma resposta comportamental com STAR. Depois grave uma explicação de decisão técnica com alternativa e trade-off. Faça autoavaliação: clareza, estrutura, precisão, evidência e resposta ao que foi perguntado. Regrave após escolher dois pontos para melhorar.

**Critério de conclusão:** Entrevista simulada gravada e revisada: apresenta projeto, responde uma pergunta comportamental e uma técnica em inglês, sustentando afirmações com exemplos e reconhecendo limites.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#3.4 — Revisita contínua|3.4]], [[Fase_10_IA_Aplicada_e_Posicionamento#53.1 — Portfólio e presença|53.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#53.3 — System design|53.3]]

### 53.3 — System design

**Classificação:** `solo` · `obrigatorio` · `media` · #mercado #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Estruturar uma proposta de sistema a partir de requisitos, estimar ordens de grandeza, desenhar componentes e justificar trade-offs em entrevista.

**Tópicos:**
- [ ] requisitos funcionais e não funcionais
- [ ] estimativa de capacidade (ordens de grandeza)
- [ ] desenho de API, dados, cache e fila
- [ ] trade-offs: consistência, disponibilidade, latência e custo
- [ ] exercícios clássicos (encurtador de URL, feed e fila de notificações)

**Atividade prática:** Escolha um caso clássico: encurtador de URL, feed ou fila de notificações. Especifique requisitos, faça conta simples de volume diário, pico e armazenamento, proponha API/dados/cache/fila conforme necessário e defina garantias de duplicata, ordem e retry. Identifique três falhas e métricas. Grave a explicação e marque onde hipótese ou trade-off ficou implícito.

**Critério de conclusão:** Apresentação cobre requisitos, estimativas, fluxo de dados, falhas e trade-offs; outra pessoa consegue questionar uma hipótese e acompanhar como o desenho muda.

**Relações:** Relacionado: [[Fase_9_Escala_Mensageria_e_Mercado#41.1 — Arquitetura distribuída|41.1]], [[Fase_9_Escala_Mensageria_e_Mercado#41.2 — Regra dura|41.2]], [[Fase_8_Infra_Operacao#38.1 — Sinais operacionais|38.1]], [[Fase_10_IA_Aplicada_e_Posicionamento#53.2 — Inglês técnico e entrevistas|53.2]]

### 53.4 — Algoritmos para entrevistas técnicas

**Classificação:** `solo` · `obrigatorio` · `media` · #fundamentos #mercado

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Resolver problemas comuns de estruturas de dados e algoritmos enquanto explica abordagem, casos limite e complexidade de tempo e espaço.

**Tópicos:**
- [ ] arrays, strings e mapas hash
- [ ] dois ponteiros e janela deslizante
- [ ] pilha, fila e recursão
- [ ] árvores e grafos (noção)
- [ ] busca, ordenação e análise de complexidade
- [ ] prática regular com exercícios cronometrados

**Atividade prática:** Resolva três problemas cronometrados: frequência com mapa hash, janela deslizante ou dois ponteiros, e busca/ordenação em uma coleção. Para cada um, grave a explicação do enunciado, solução inicial, otimização, complexidade e teste de casos limite. Em uma revisão adicional, escolha um exercício de pilha/fila ou travessia de árvore/grafo. Compare sua gravação com uma rubrica e reescreva uma solução sem consultar resposta.

**Critério de conclusão:** Resolver problemas representativos de arrays/strings/mapas, janela deslizante ou dois ponteiros e busca/ordenação, explicando complexidade e demonstrando correção com casos limite; praticar regularmente pilha, fila e travessia de árvore/grafo.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#7.4 — Revisita de lógica|7.4]], [[Fase_5_Backend_e_Arquitetura#23.2 — Base de raciocínio|23.2]], [[Fase_10_IA_Aplicada_e_Posicionamento#53.2 — Inglês técnico e entrevistas|53.2]]
