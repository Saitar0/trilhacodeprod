---
title: "Fase 6 — Frontend moderno"
aliases:
  - Fase 6
tags:
  - trilhas
  - fase
tipo: fase
ordem: 6
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 6 — Frontend moderno

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Construir interfaces modernas com React, conectadas à API construída na Fase 5, com estados explícitos, testes e performance medida.

## Por que esta fase vem agora?
Com os fundamentos web, de dados e de backend prontos, a pessoa passa a construir interfaces declarativas consumindo a API real.

## Pré-requisitos
Fase 3 (JavaScript, DOM, fetch e TypeScript), noções de dados da Fase 4 e a API da Fase 5.

## Competências
- Construir componentes com estado e efeitos
- Integrar a interface a APIs REST com estados de loading, erro, vazio, sucesso e retry
- Separar estado de interface de estado remoto
- Testar comportamento de componentes e fluxos
- Medir e otimizar performance quando houver gargalo
- Situar Next.js, React Native, Vue e Angular

## Projeto incremental
Frontend React tipado, conectado à API real da Fase 5, com estados de interface, testes de comportamento e medição de performance.

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_6_Frontend_Moderno#31.5 — Projeto de fase (Trilho B)|31.5 Projeto de fase (Trilho B)]].

## Critério de conclusão
Frontend React tipado, conectado à API da Fase 5, com os estados de interface cobertos por testes de comportamento e uma medição de performance.

## Estimativa de carga horária

**Total estimado da fase:** 39–71 h (referência de planejamento: 55 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 25 — Fundamentos de React|Módulo 25 — Fundamentos de React]]
- [[#Módulo 26 — Hooks e organização de componentes|Módulo 26 — Hooks e organização de componentes]]
- [[#Módulo 27 — Integração com o backend|Módulo 27 — Integração com o backend]]
- [[#Módulo 28 — Gerência de estado e dados remotos|Módulo 28 — Gerência de estado e dados remotos]]
- [[#Módulo 29 — Testes de frontend|Módulo 29 — Testes de frontend]]
- [[#Módulo 30 — Performance de frontend|Módulo 30 — Performance de frontend]]
- [[#Módulo 31 — Ecossistema: Next.js, React Native, Vue e Angular|Módulo 31 — Ecossistema: Next.js, React Native, Vue e Angular]]

---

## Módulo 25 — Fundamentos de React

**Objetivo:** Explicar o papel do React e converter uma interface repetitiva em componentes declarativos com JSX e props.

**Submódulos:** [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1 Fundamentos]] · [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2 Estado e interação]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 25.1 — Fundamentos

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Explicar o papel do React e converter uma interface repetitiva em componentes declarativos com JSX e props.

**Pré-requisitos:** Pré-requisitos: 6.3, 7.1 e 7.2. Revisita a interação com DOM em 7.1; prepara 25.2.

**Tópicos:**
- [ ] por que React existe
- [ ] componentes
- [ ] JSX
- [ ] props
- [ ] renderização

**Atividade prática:** Refatore duas linhas de HTML repetidas para um componente `TaskCard` com props `title`, `owner` e `completed`. Renderize três dados diferentes, incluindo um título com caracteres especiais. Explique qual dado é entrada e qual markup se repete.

**Critério de conclusão:** O componente aceita dados por props, representa itens distintos sem duplicar markup e a pessoa explica a diferença entre descrever a UI e manipular o DOM diretamente.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3]], [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]], [[Fase_3_Base_da_Web_JS_TS_Node#7.2 — Organização do código|7.2]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]]

### 25.2 — Estado e interação

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Construir uma interface interativa com estado, eventos, listas, condições e formulário controlado.

**Pré-requisitos:** Pré-requisito: 25.1. Revisa 6.2 e 7.1; prepara 26.1, 27.1 e 29.1.

**Tópicos:**
- [ ] state
- [ ] eventos
- [ ] listas
- [ ] renderização condicional
- [ ] formulários

**Atividade prática:** Reimplemente a lista de tarefas da Fase 3: adicionar, marcar concluída, remover e filtrar. Use ID estável, estado imutável, formulário com rótulo e mensagem para a lista vazia. Faça o total visível ser derivado da lista.

**Critério de conclusão:** A lista suporta as ações sem manipulação manual do DOM; a pessoa explica quando o estado atualiza, o que provoca nova renderização e como a key mantém identidade.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1]], [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]], [[Fase_6_Frontend_Moderno#26.1 — Hooks|26.1]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]], [[Fase_6_Frontend_Moderno#29.1 — Base de testes|29.1]]

---

## Módulo 26 — Hooks e organização de componentes

**Objetivo:** Usar `useEffect`, `useRef`, `useMemo` e `useCallback` com base na responsabilidade de cada hook.

**Submódulos:** [[Fase_6_Frontend_Moderno#26.1 — Hooks|26.1 Hooks]] · [[Fase_6_Frontend_Moderno#26.2 — Organização|26.2 Organização]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 26.1 — Hooks

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Usar `useEffect`, `useRef`, `useMemo` e `useCallback` com base na responsabilidade de cada hook.

**Pré-requisitos:** Pré-requisito: 25.2. Complementa 30.1 e revisita funções/estruturas em 6.2.

**Tópicos:**
- [ ] useEffect
- [ ] useRef
- [ ] useMemo
- [ ] useCallback

**Atividade prática:** Corrija um componente com busca duplicada disparada por Effect e dependência omitida. Faça a ação de busca partir da intenção do usuário ou da biblioteca de query; mantenha uma referência ao input para foco; só use memoização após registrar um gargalo reproduzível. Liste setup e cleanup de qualquer sincronização externa.

**Critério de conclusão:** Para cada hook, a pessoa identifica o problema resolvido, quando não usá-lo e como dependências/limpeza afetam o resultado.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]], [[Fase_6_Frontend_Moderno#30.1 — Otimização|30.1]], [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]]

### 26.2 — Organização

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Organizar componentes por responsabilidade e compartilhar dados com composição, hooks customizados e Context quando apropriado.

**Pré-requisitos:** Pré-requisito: 26.1. Relaciona-se com organização visual em 5.4 e responsabilidades em 21.1.

**Tópicos:**
- [ ] context
- [ ] hooks customizados
- [ ] composição de componentes
- [ ] separação de responsabilidades

**Atividade prática:** Extraia o estado e validação repetidos de dois formulários para um hook customizado. Use composição para um campo com label e mensagem. Desenhe uma árvore mostrando quais dados ficam locais e quais justificam Context; evite incluir o estado remoto da API.

**Critério de conclusão:** A pessoa justifica as fronteiras de componentes e hooks e demonstra compartilhamento sem criar Context para dados de um único consumidor.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#26.1 — Hooks|26.1]], [[Fase_2_Base_da_Web_HTML_CSS#5.4 — Organização visual|5.4]], [[Fase_5_Backend_e_Arquitetura#21.1 — Base conceitual|21.1]]

---

## Módulo 27 — Integração com o backend

**Objetivo:** Consumir a API REST real da Fase 5 com autenticação, headers e paginação sem expor credenciais nem deixar respostas antigas sobrescreverem novas.

**Submódulos:** [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1 Comunicação com backend]] · [[Fase_6_Frontend_Moderno#27.2 — Estados de interface|27.2 Estados de interface]] · [[Fase_6_Frontend_Moderno#27.3 — Contrato de dados|27.3 Contrato de dados]] · [[Fase_6_Frontend_Moderno#27.4 — Segurança no navegador|27.4 Segurança no navegador]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 27.1 — Comunicação com backend

**Classificação:** `integrado` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Consumir a API REST real da Fase 5 com autenticação, headers e paginação sem expor credenciais nem deixar respostas antigas sobrescreverem novas.

**Tópicos:**
- [ ] requisições REST
- [ ] autenticação por token
- [ ] headers
- [ ] paginação

**Atividade prática:** Integre a listagem paginada da API da Fase 5: montar header de autenticação conforme projeto, converter erros para estados tipados, avançar/voltar páginas e tratar 401. Inspecione a aba de rede e confirme que não há token em URL. Teste expiração e uma navegação rápida entre filtros.

**Critério de conclusão:** Token e headers seguem o contrato; falhas HTTP são diferenciadas de falhas de rede; paginação e expiração mantêm UI consistente e a pessoa justifica a decisão de armazenamento.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]]

### 27.2 — Estados de interface

**Classificação:** `pratica` · `obrigatorio` · `alta` · #web #qualidade

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Representar loading, retry, erro, vazio e sucesso em uma tela de listagem conectada a API.

**Pré-requisitos:** Pré-requisito 27.1. Relaciona-se a 7.3 e à estrutura de dados em 8.2.

**Tópicos:**
- [ ] loading
- [ ] retry
- [ ] erro
- [ ] vazio
- [ ] sucesso

**Atividade prática:** Implemente os cinco estados em uma lista. Produza cada cenário com servidor lento, lista vazia, 500, retry bem-sucedido e dados reais. Preserve filtros/página quando fizer sentido; verifique teclado, leitor de tela e mensagens de erro.

**Critério de conclusão:** Todos os cinco estados têm evidência reproduzível, diferenciam vazio de falha, e o retry não duplica ação insegura.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]], [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]]

### 27.3 — Contrato de dados

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Tipar dados JSON com base no contrato da API e tratar respostas incompatíveis em runtime.

**Tópicos:**
- [ ] integração com JSON
- [ ] contrato definido no backend ([[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]])
- [ ] tipagem de resposta
- [ ] tipos compartilhados entre frontend e backend (conferidos no 18.1)
- [ ] tratamento defensivo

**Atividade prática:** Consuma duas rotas reais, tipando paginação e itens. Valide ao menos campos essenciais na fronteira com schema/guard, produza cenário com campo ausente e trate sem crash. Explique onde mora o contrato compartilhado e como um cliente antigo reage a campo novo.

**Critério de conclusão:** Resposta válida chega à UI tipada; payload inválido gera falha controlada; a pessoa distingue tipos estáticos de validação em runtime.

**Relações:** Revisita: [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]]

### 27.4 — Segurança no navegador

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #seguranca

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Reconhecer XSS, CSRF, risco de credenciais e exposição de segredos; aplicar medidas compatíveis com a arquitetura.

**Tópicos:**
- [ ] XSS refletido e armazenado
- [ ] por que o React escapa o conteúdo e onde deixa de proteger (dangerouslySetInnerHTML e URLs)
- [ ] sanitização de HTML
- [ ] CSRF e cookies (SameSite e HttpOnly)
- [ ] onde guardar o token: memória, cookie HttpOnly e localStorage, com os riscos de cada um
- [ ] Content Security Policy (noção)
- [ ] segredos e variáveis públicas no bundle
- [ ] dependências: npm audit e cadeia de suprimentos (noção)

**Atividade prática:** Em aplicação local descartável, reproduza XSS armazenado em campo renderizado como texto, corrija-o e demonstre que HTML não executa. Revise uso de HTML bruto, URLs, CSP, cookies/token, variáveis públicas e `npm audit`; registre ameaça, mitigação e limite. Não use credenciais ou dados reais.

**Critério de conclusão:** A pessoa explica a cadeia XSS, localiza uma saída perigosa, corrige com abordagem de contexto e justifica o armazenamento de credenciais frente a XSS e CSRF.

**Relações:** Complementar: [[Fase_5_Backend_e_Arquitetura#20.1 — Autenticação|20.1]], [[Fase_5_Backend_e_Arquitetura#20.2 — Segurança básica|20.2]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]]

---

## Módulo 28 — Gerência de estado e dados remotos

**Objetivo:** Distinguir Vite, Zustand e TanStack Query pelas responsabilidades que resolvem e usá-los sem sobreposição desnecessária.

**Submódulos:** [[Fase_6_Frontend_Moderno#28.1 — Ferramentas|28.1 Ferramentas]] · [[Fase_6_Frontend_Moderno#28.2 — Gerência de dados|28.2 Gerência de dados]] · [[Fase_6_Frontend_Moderno#28.3 — Organização|28.3 Organização]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 28.1 — Ferramentas

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Distinguir Vite, Zustand e TanStack Query pelas responsabilidades que resolvem e usá-los sem sobreposição desnecessária.

**Pré-requisitos:** Pré-requisito 27.2. Complementa 28.2.

**Tópicos:**
- [ ] Vite
- [ ] Zustand
- [ ] TanStack Query

**Atividade prática:** Em app React, execute o projeto com Vite; substitua uma consulta manual por TanStack Query com chave que inclui filtro/página; crie um estado de UI simples em Zustand. Marque no diagrama o que vem do servidor e o que é escolha local.

**Critério de conclusão:** A pessoa explica uma responsabilidade e um limite de cada ferramenta e não armazena resposta remota simultaneamente em duas fontes sem política de sincronização.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#27.2 — Estados de interface|27.2]], [[Fase_6_Frontend_Moderno#28.2 — Gerência de dados|28.2]]

### 28.2 — Gerência de dados

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #dados

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Classificar estado local, global e remoto e manter cache correto após leitura e mutação.

**Pré-requisitos:** Pré-requisitos 26.1 e 27.1. Relaciona-se a cache Redis em 15.1 sem confundir camadas.

**Tópicos:**
- [ ] estado local
- [ ] estado global
- [ ] estado remoto
- [ ] cache
- [ ] invalidação

**Atividade prática:** Classifique 8 estados da aplicação (sessão, modal, lista de API, página, preferências, formulário, erro, contador do servidor). Implemente uma mutação de edição; invalide as queries pertinentes e demonstre antes/depois. Explique uma política de atualização otimista ou justifique não usá-la.

**Critério de conclusão:** Cada estado tem fonte de verdade justificada; mutação atualiza/refaz as queries corretas e falha não deixa cache enganoso.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#26.1 — Hooks|26.1]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]], [[Fase_4_Dados_e_Bancos#15.1 — Redis|15.1]]

### 28.3 — Organização

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Justificar a localização de um estado e evitar ferramentas globais para dados que têm escopo local.

**Tópicos:**

**Atividade prática:** Escolha estado de um formulário, drawer ou resultado de API no projeto. Desenhe consumidores, fonte de verdade e ciclo de vida. Proponha a menor localização adequada (local, elevado, Context/store ou cache de consulta) e descreva uma mudança de requisito que faria você rever a decisão. Não marque os princípios como checklist de conceitos.

**Critério de conclusão:** Em um estado concreto, a pessoa explica fonte de verdade, consumidores, ciclo de vida e por que solução local, Context, store ou query é proporcional.

**Relações:** Complementar: [[Fase_6_Frontend_Moderno#28.2 — Gerência de dados|28.2]], [[Fase_6_Frontend_Moderno#26.2 — Organização|26.2]]

---

## Módulo 29 — Testes de frontend

**Objetivo:** Testar componentes pelo comportamento observável com Jest ou Vitest e Testing Library.

**Submódulos:** [[Fase_6_Frontend_Moderno#29.1 — Base de testes|29.1 Base de testes]] · [[Fase_6_Frontend_Moderno#29.2 — Integração e borda|29.2 Integração e borda]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 29.1 — Base de testes

**Classificação:** `solo` · `obrigatorio` · `media` · #qualidade #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Testar componentes pelo comportamento observável com Jest ou Vitest e Testing Library.

**Tópicos:**
- [ ] Jest ou Vitest
- [ ] Testing Library
- [ ] testes de componente
- [ ] testes de comportamento

**Atividade prática:** Escreva testes para um formulário: label visível, submissão inválida com mensagem, submissão válida e confirmação. Use `user-event` ou API equivalente da versão instalada; selecione por papel e nome. Faça um teste falhar ao remover a validação.

**Critério de conclusão:** Testes cobrem comportamento visível, interação realista e erro; uma refatoração interna sem mudar comportamento não exige reescrever assertions.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]], [[Fase_5_Backend_e_Arquitetura#24.1 — Tipos de teste|24.1]]

### 29.2 — Integração e borda

**Classificação:** `pratica` · `obrigatorio` · `media` · #qualidade #web

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Testar a fronteira HTTP com MSW e cobrir um fluxo de navegador com Playwright.

**Tópicos:**
- [ ] mocks de API
- [ ] testes e2e com Playwright

**Atividade prática:** Com MSW, testar listagem, vazio e erro; com Playwright, percorrer login e abrir listagem usando ambiente de teste. Registre quais partes cada ambiente substitui e quais serviços são reais. Faça o cenário reproduzível sem conta de produção.

**Critério de conclusão:** Um cenário mockado e um fluxo E2E passam conceitualmente por fronteiras diferentes; a pessoa enumera o que não foi validado pelo mock.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]], [[Fase_6_Frontend_Moderno#29.1 — Base de testes|29.1]], [[Fase_5_Backend_e_Arquitetura#24.2 — Aplicação|24.2]], [[Fase_7_Infra_Deploy_e_Cloud#32.1 — Automação|32.1]]

---

## Módulo 30 — Performance de frontend

**Objetivo:** Medir uma tela e aplicar memoização, carregamento sob demanda, divisão de código e virtualização de forma verificável.

**Submódulos:** [[Fase_6_Frontend_Moderno#30.1 — Otimização|30.1 Otimização]] · [[Fase_6_Frontend_Moderno#30.2 — Maturidade|30.2 Maturidade]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 30.1 — Otimização

**Classificação:** `solo` · `obrigatorio` · `media` · #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Medir uma tela e aplicar memoização, carregamento sob demanda, divisão de código e virtualização de forma verificável.

**Pré-requisitos:** Pré-requisito 26.1. Relaciona-se a desempenho em 7.4 e 12.1.

**Tópicos:**
- [ ] memoization
- [ ] lazy loading
- [ ] code splitting
- [ ] virtualização

**Atividade prática:** Escolha uma tela pesada, defina métrica e método de coleta. Aplique carregamento sob demanda a uma rota e virtualização a uma lista grande. Compare métricas antes/depois e verifique foco por teclado, loading e tamanho do bundle.

**Critério de conclusão:** Cada otimização tem baseline, justificativa e medição repetível; a pessoa registra custo/regressão e não infere ganho por percepção isolada.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#26.1 — Hooks|26.1]], [[Fase_3_Base_da_Web_JS_TS_Node#7.4 — Revisita de lógica|7.4]], [[Fase_4_Dados_e_Bancos#12.1 — Performance e leitura|12.1]]

### 30.2 — Maturidade

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #qualidade

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Demonstrar que uma otimização só entra quando a medição prova um gargalo relevante.

**Tópicos:**

**Atividade prática:** Use profiler ou ferramenta de medição em uma interação representativa. Registre hipótese e baseline, tente uma otimização simples e compare. Se não houver ganho reproduzível ou aparecer regressão, reverta e escreva por que a não adoção é a decisão mais madura. Não transforme princípios em uma lista de termos para decorar.

**Critério de conclusão:** Apresentar uma otimização tentada que não mostrou ganho relevante, explicar a medição e justificar sua remoção ou não adoção.

**Relações:** Complementar: [[Fase_6_Frontend_Moderno#30.1 — Otimização|30.1]]

---

## Módulo 31 — Ecossistema: Next.js, React Native, Vue e Angular

**Objetivo:** Explicar roteamento, renderização no servidor e cliente, geração/prerenderização e endpoints no modelo atual do Next.js.

**Submódulos:** [[Fase_6_Frontend_Moderno#31.1 — Next.js|31.1 Next.js]] · [[Fase_6_Frontend_Moderno#31.2 — React Native|31.2 React Native]] · [[Fase_6_Frontend_Moderno#31.3 — Vue.js e Angular|31.3 Vue.js e Angular]] · [[Fase_6_Frontend_Moderno#31.4 — Projeto incremental da fase|31.4 Projeto incremental da fase]] · [[Fase_6_Frontend_Moderno#31.5 — Projeto de fase (Trilho B)|31.5 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 31.1 — Next.js

**Classificação:** `solo` · `obrigatorio` · `media` · #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Explicar roteamento, renderização no servidor e cliente, geração/prerenderização e endpoints no modelo atual do Next.js.

**Pré-requisitos:** Relaciona-se a 25.1 e organização em 26.2; a comunicação com API em 27.1 é pré-requisito conceitual.

**Tópicos:**
- [ ] rotas
- [ ] SSR
- [ ] SSG
- [ ] API routes
- [ ] deploy
- [ ] visão arquitetural

**Atividade prática:** Crie um mini app App Router com página de catálogo prerenderizável, detalhe que busca no servidor e botão cliente interativo. Faça um Route Handler de leitura e compare uma rota estática com outra dependente de requisição. Registre estratégia, cache, segredos e limitações do destino de deploy. Se o framework exigir config adicional, anote versão e fonte consultada.

**Critério de conclusão:** A pessoa compara renderização cliente, SSR e prerenderização no contexto dos dados; identifica Server/Client boundary e diferencia Route Handler de API Route do Pages Router.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1]], [[Fase_6_Frontend_Moderno#26.2 — Organização|26.2]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]]

### 31.2 — React Native

**Classificação:** `solo` · `repertorio` · `repertorio` · #web

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Reconhecer o que React Native reutiliza do React e o que muda ao construir interface para plataformas nativas.

**Tópicos:**
- [ ] visão geral
- [ ] posicionamento no ecossistema

**Critério de conclusão:** Explicar pelo menos duas partes reutilizáveis e duas que precisam de implementação/plataforma específicas.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]]

### 31.3 — Vue.js e Angular

**Classificação:** `solo` · `repertorio` · `repertorio` · #web

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Comparar modelos de componentes, reatividade e organização em Vue 3 e Angular e reconhecer Vue 2 como legado.

**Tópicos:**
- [ ] Vue 3
- [ ] Vue 2 legado — *opcional*
- [ ] Angular 2+
- [ ] módulos
- [ ] serviços
- [ ] leitura comparativa de mercado

**Critério de conclusão:** Comparar componentização, reatividade, organização e serviços em Vue/Angular com React, identificando Vue 2 como legado e anotando fontes/versionamento.

**Relações:** Relacionado: [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]]

### 31.4 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #web #qualidade

**Carga horária estimada:** 8 h–12 h (referência: 10 h).

**Objetivo:** Evoluir o projeto principal (Trilho A) com frontend React tipado ligado à API real, cobertura dos cinco estados, testes de comportamento e medição de performance.

**Tópicos:**
- [ ] frontend React tipado do projeto principal
- [ ] conexão com a API real, com os cinco estados de interface
- [ ] testes de comportamento do fluxo principal
- [ ] uma medição de performance antes e depois de uma otimização

**Atividade prática:** Implemente uma rota principal, uma consulta real e a ação mais representativa da ideia escolhida. Use mocks para forçar os estados; execute fluxo principal contra ambiente de teste. Capture a métrica selecionada em condições equivalentes. **Rubrica:** integração coerente; cinco estados reproduzíveis; teste falha diante de regressão visível; medição comparável; decisões e limites documentados.

**Critério de conclusão:** Frontend tipado usa API real, cobre cinco estados por cenários, possui testes de comportamento e registra medição antes/depois de otimização justificada.

**Relações:** Complementar: [[Fase_6_Frontend_Moderno#27.2 — Estados de interface|27.2]], [[Fase_6_Frontend_Moderno#29.2 — Integração e borda|29.2]]

### 31.5 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 8 h–14 h (referência: 11 h).

**Objetivo:** Escolher uma ideia elegível de Trilho B e entregar uma fatia React tipada sobre API real da Fase 5 que demonstre a regra técnica central do tipo escolhido.

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Implemente a jornada mínima da ideia selecionada e provoque um cenário que poderia quebrar sua regra central. **Rubrica:** escolha válida conforme guia; interface consome API; estado de erro/retentativa coerente; teste cobre comportamento do usuário; evidência demonstra requisito central; escopo, limitações e decisões ficam registrados. Repetição opcional não pode ser marcada como novo tipo concluído.

**Critério de conclusão:** A interface da ideia selecionada cumpre a versão de Fase 6, os cinco estados são reproduzíveis, testes de comportamento passam conceitualmente e o critério central do tipo está demonstrado e registrado no guia de cobertura.

**Relações:** Complementar: [[Fase_6_Frontend_Moderno#31.4 — Projeto incremental da fase|31.4]]
