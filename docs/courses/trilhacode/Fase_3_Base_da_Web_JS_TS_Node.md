---
title: "Fase 3 — Base da web: JavaScript, TypeScript e Node.js"
aliases:
  - Fase 3
tags:
  - trilhas
  - fase
tipo: fase
ordem: 3
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 3 — Base da web: JavaScript, TypeScript e Node.js

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Compreender a lógica de interação no navegador, programar com JavaScript, tipar e organizar o código com TypeScript e usar Node.js e npm no dia a dia.

## Por que esta fase vem agora?
JavaScript sustenta o navegador, o frontend moderno e o backend; JSON e contratos de dados nascem aqui. TypeScript prepara a organização que o frontend e o backend vão reutilizar.

## Pré-requisitos
HTML e CSS (Fase 2) e noções de terminal (Fase 1).

## Competências
- Programar interações e consumir dados com JavaScript
- Tipar e organizar o código com TypeScript
- Depurar no navegador com DevTools
- Usar Node.js e npm para dependências, scripts, lint e formatação

## Projeto incremental
Interface estática da ideia escolhida no 3.5 (Trilho A), sem framework, em HTML, CSS, JavaScript e TypeScript, com dados em JSON local e publicada com deploy estático. Detalhado em [[Fase_3_Base_da_Web_JS_TS_Node#8.5 — Projeto incremental da fase|8.5 Projeto incremental da fase]].

## Projeto de fase (Trilho B)
Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_3_Base_da_Web_JS_TS_Node#8.6 — Projeto de fase (Trilho B)|8.6 Projeto de fase (Trilho B)]].

## Critério de conclusão
Publicar uma página funcional, acessível, responsiva e organizada, sem depender de um framework frontend.

## Estimativa de carga horária

**Total estimado da fase:** 33–59,5 h (referência de planejamento: 46 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 6 — Fundamentos de JavaScript|Módulo 6 — Fundamentos de JavaScript]]
- [[#Módulo 7 — JavaScript no navegador|Módulo 7 — JavaScript no navegador]]
- [[#Módulo 8 — TypeScript|Módulo 8 — TypeScript]]

---

## Módulo 6 — Fundamentos de JavaScript

**Objetivo:** Usar variáveis, tipos, operadores, condicionais e laços para transformar entradas em resultados previsíveis.

**Submódulos:** [[Fase_3_Base_da_Web_JS_TS_Node#6.1 — Fundamentos de JavaScript|6.1 Fundamentos de JavaScript]] · [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2 Estruturas básicas]] · [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3 Base moderna de JavaScript]] · [[Fase_3_Base_da_Web_JS_TS_Node#6.4 — Node.js e npm no dia a dia|6.4 Node.js e npm no dia a dia]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 6.1 — Fundamentos de JavaScript

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Usar variáveis, tipos, operadores, condicionais e laços para transformar entradas em resultados previsíveis.

**Pré-requisitos:** - Pré-requisito: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2 — Ambiente de desenvolvimento]]

**Tópicos:**
- [ ] variáveis
- [ ] tipos
- [ ] operadores
- [ ] condicionais
- [ ] laços

**Atividade prática:** Escreva um programa que recebe uma lista de notas numéricas, calcula total e média, informa aprovação segundo uma regra definida e trata lista vazia. Crie também um contador que percorra a lista e conte quantas notas alcançam a média da turma. Explique cada variável, condição e laço.

**Critério de conclusão:** Resolver um problema simples sem copiar código, explicar como os valores percorrem o programa e justificar as condições e repetições usadas.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]]

### 6.2 — Estruturas básicas

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Organizar lógica em funções e representar informações com arrays e objetos, controlando parâmetros, retorno e escopo.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#6.1 — Fundamentos|6.1 — Fundamentos]]

**Tópicos:**
- [ ] funções
- [ ] arrays
- [ ] objetos
- [ ] escopo
- [ ] retorno
- [ ] parâmetros

**Atividade prática:** Crie uma lista de objetos `{ id, titulo, ativa, prioridade }`. Escreva funções separadas para filtrar tarefas ativas, ordenar por prioridade e calcular quantas estão ativas. Cada função deve receber os dados por parâmetro e retornar o resultado, sem alterar a lista original. Teste lista vazia e prioridades iguais.

**Critério de conclusão:** Explicar parâmetros, retorno, escopo e escolha entre array/objeto; produzir transformações que funcionam nos casos normais e de borda.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.1 — Fundamentos de JavaScript|6.1]], [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_3_Base_da_Web_JS_TS_Node#7.4 — Revisita de lógica|7.4]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3]]

### 6.3 — Base moderna de JavaScript

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Ler e escrever JavaScript moderno com `let`/`const`, arrow functions, template strings, destructuring e operadores spread/rest.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2 — Estruturas básicas]]

**Tópicos:**
- [ ] let e const
- [ ] arrow functions
- [ ] template strings
- [ ] destructuring
- [ ] spread e rest

**Atividade prática:** Receba um código com `var`, concatenação de strings e funções tradicionais simples. Refatore para `const`/`let`, arrow functions onde apropriado, template strings, destructuring e spread/rest. Não mude o comportamento; escreva uma nota por recurso explicando como melhora a leitura e identifique qualquer cópia rasa.

**Critério de conclusão:** Reescrever um trecho com sintaxe moderna e explicar cada mudança, incluindo onde spread cria cópia rasa e quando arrow function não é substituição direta.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_6_Frontend_Moderno#25.1 — Fundamentos|25.1]]

### 6.4 — Node.js e npm no dia a dia

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas #fundamentos

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Usar Node.js para executar JavaScript fora do navegador e npm para configurar projetos, dependências, scripts e ferramentas básicas de qualidade.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]], [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]] e [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna|6.3]]

**Tópicos:**
- [ ] instalar o Node.js com um gerenciador de versões
- [ ] executar um arquivo com node
- [ ] npm init e package.json
- [ ] dependencies e devDependencies
- [ ] scripts do npm
- [ ] package-lock e node_modules (e por que não vão para o Git)
- [ ] módulos ESM e CommonJS (noção)
- [ ] ESLint e Prettier básicos
- [ ] ler o relatório do npm audit (noção)

**Atividade prática:** Crie um projeto com `npm init`, arquivo `dados.json` fictício e script Node que lê o JSON local e imprime um pequeno resumo. Instale uma dependência apropriada ao projeto, configure um script de lint e outro de formatação com ESLint e Prettier, e execute `npm audit` para aprender a ler o relatório. Configure `.gitignore` para `node_modules`; versione manifesto e lockfile.

**Critério de conclusão:** Em outra cópia do repositório, instalar dependências e executar o script sem passos manuais não documentados; explicar o papel do `package-lock.json`, `node_modules` e scripts.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]], [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1]], [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3]], [[Fase_4_Dados_e_Bancos#10.1 — Containerização|10.1]], [[Fase_5_Backend_e_Arquitetura#17.1 — Fundamentos|17.1]], [[Fase_6_Frontend_Moderno#28.1 — Ferramentas|28.1]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso de TypeScript|8.3]]

---

## Módulo 7 — JavaScript no navegador

**Objetivo:** Manipular o DOM com JavaScript, responder a eventos e validar um formulário preservando os comportamentos nativos e acessíveis do navegador.

**Submódulos:** [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1 Navegador e interação]] · [[Fase_3_Base_da_Web_JS_TS_Node#7.2 — Organização do código|7.2 Organização do código]] · [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3 Dados e comunicação]] · [[Fase_3_Base_da_Web_JS_TS_Node#7.4 — Revisita de lógica|7.4 Revisita de lógica]] · [[Fase_3_Base_da_Web_JS_TS_Node#7.5 — Depuração no navegador|7.5 Depuração no navegador]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 7.1 — Navegador e interação

**Classificação:** `integrado` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Manipular o DOM com JavaScript, responder a eventos e validar um formulário preservando os comportamentos nativos e acessíveis do navegador.

**Pré-requisitos:** - Pré-requisitos: [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2]] e [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]]

**Tópicos:**
- [ ] DOM
- [ ] seleção de elementos
- [ ] manipulação de conteúdo
- [ ] eventos
- [ ] formulários
- [ ] validação básica

**Atividade prática:** Construa um formulário de contato sem framework com nome, e-mail e mensagem. Use labels e validação nativa; adicione uma regra simples com evento `submit`, apresente erros em texto e mostre confirmação sem recarregar a página. Teste campos vazios, e-mail malformado e envio válido com teclado.

**Critério de conclusão:** Explicar a relação entre HTML e DOM e demonstrar uma validação que impede envio inválido sem remover a semântica ou acessibilidade do formulário.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2]], [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_6_Frontend_Moderno#25.2 — Estado e interação|25.2]] · Revisita: [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1]]

### 7.2 — Organização do código

**Classificação:** `solo` · `obrigatorio` · `media` · #fundamentos #web

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Organizar JavaScript em módulos e arquivos com responsabilidades claras, exportando e reutilizando funções sem concentrar toda a lógica em um único script.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2 — Estruturas básicas]]

**Tópicos:**
- [ ] módulos
- [ ] separação de arquivos
- [ ] reutilização de funções

**Atividade prática:** Comece com uma página que mistura seleção DOM, validação e transformação de dados. Separe em módulos: um para funções puras de transformação, outro para interação/formulário e um ponto de entrada que conecta os dois. Exporte apenas o que será reutilizado e explique cada dependência.

**Critério de conclusão:** Explicar o que cada módulo exporta e por que, e mostrar como a separação torna uma mudança ou revisão mais localizada.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso de TypeScript|8.3]]

### 7.3 — Dados e comunicação

**Classificação:** `integrado` · `obrigatorio` · `alta` · #web #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Consumir dados HTTP com `fetch`, interpretar JSON, usar promises e `async/await`, e diferenciar falhas de rede, respostas HTTP não bem-sucedidas e bloqueios de CORS.

**Pré-requisitos:** - Pré-requisitos: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna|6.3]] e [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]]

**Tópicos:**
- [ ] JSON
- [ ] métodos HTTP (GET, POST, PUT, PATCH e DELETE)
- [ ] códigos de status e headers principais
- [ ] fetch
- [ ] promises
- [ ] async/await
- [ ] tratamento de erros
- [ ] noção de CORS: por que o navegador bloqueia uma chamada

**Atividade prática:** Consuma uma API pública apropriada ou uma API de demonstração, leia resposta JSON e apresente os itens. Inclua estados de carregamento, sucesso, erro HTTP, erro de rede e conteúdo inválido; permita filtro ou busca local. Registre método, URL, status e headers relevantes. Não envie dados pessoais.

**Critério de conclusão:** Explicar o ciclo de uma Promise, distinguir erro de rede de erro HTTP e erro de parsing, e justificar a mensagem/ação escolhida para cada falha.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3]], [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]], [[Fase_6_Frontend_Moderno#27.1 — Comunicação com backend|27.1]] · Revisita: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1]]

### 7.4 — Revisita de lógica

**Classificação:** `revisita` · `obrigatorio` · `media` · #fundamentos

**Carga horária estimada:** 30 min–1 h (referência: 45 min).

**Objetivo:** Transformar dados com métodos de array, compor funções, escolher entre arrays e objetos e estimar a complexidade linear em cenários comuns, reconhecendo pilhas e filas.

**Pré-requisitos:** - Pré-requisito/revisita: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2 — Estruturas básicas]]

**Tópicos:**
- [ ] manipulação de arrays
- [ ] transformação de dados
- [ ] composição de funções
- [ ] arrays vs. objetos como estruturas base
- [ ] noção de complexidade: O(n) na prática
- [ ] pilha e fila em cenários reais

**Atividade prática:** Receba um JSON de pedidos fictícios com identificador, cliente, itens, total e status. Implemente funções para filtrar pedidos concluídos, transformar cada um em uma linha de relatório e calcular total por cliente. Compare uma implementação com uma passagem e outra com várias passagens. Descreva uma pilha de ações de desfazer e uma fila de pedidos de processamento para o mesmo domínio.

**Critério de conclusão:** Explicar o custo aproximado da transformação e escolher array, objeto, pilha ou fila conforme a operação e a ordem esperada.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.2 — Estruturas básicas|6.2]], [[Fase_5_Backend_e_Arquitetura#23.2 — Base de raciocínio|23.2]]

### 7.5 — Depuração no navegador

**Classificação:** `pratica` · `obrigatorio` · `media` · #ferramentas #qualidade

**Carga horária estimada:** 1,5 h–2,5 h (referência: 2 h).

**Objetivo:** Usar Console, Elements, Network, breakpoints e stack traces do DevTools para localizar a causa de um erro de interação e de uma requisição com falha.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1 — Navegador e interação]]

**Tópicos:**
- [ ] DevTools: console, elements e network
- [ ] breakpoints e execução passo a passo
- [ ] leitura de stack trace sem pânico
- [ ] depurar requisições na aba network

**Atividade prática:** Use uma página interativa com dois defeitos controlados: um handler que lê o valor errado e uma requisição para uma rota inválida. Reproduza os problemas, capture evidência no Console, pause no breakpoint e registre os detalhes da requisição na Network. Corrija um defeito por vez e repita o cenário.

**Critério de conclusão:** Localizar e explicar a causa de um erro de interação com breakpoint e de uma requisição com a aba Network, distinguindo evidência de hipótese.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]], [[Fase_5_Backend_e_Arquitetura#17.2 — Depuração no servidor|17.2]]

---

## Módulo 8 — TypeScript

**Objetivo:** Descrever valores JavaScript com tipos primitivos, usar inferência e unions e nomear estruturas com aliases e interfaces.

**Submódulos:** [[Fase_3_Base_da_Web_JS_TS_Node#8.1 — Fundamentos de tipagem|8.1 Fundamentos de tipagem]] · [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2 Estrutura e modelagem]] · [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso de TypeScript|8.3 Configuração e uso de TypeScript]] · [[Fase_3_Base_da_Web_JS_TS_Node#8.5 — Projeto incremental da fase|8.5 Projeto incremental da fase]] · [[Fase_3_Base_da_Web_JS_TS_Node#8.6 — Projeto de fase (Trilho B)|8.6 Projeto de fase (Trilho B)]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 8.1 — Fundamentos de tipagem

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Descrever valores JavaScript com tipos primitivos, usar inferência e unions e nomear estruturas com aliases e interfaces.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna|6.3 — Base moderna]]

**Tópicos:**
- [ ] tipos primitivos
- [ ] inferência
- [ ] unions
- [ ] aliases
- [ ] interfaces

**Atividade prática:** Modele `Tarefa` com interface e `StatusTarefa` com alias union literal. Escreva funções para formatar uma tarefa e para mudar seu status. Use inferência quando ela for clara e anote contratos públicos. Inclua um campo opcional e trate sua ausência sem asserções de tipo indiscriminadas.

**Critério de conclusão:** Explicar a diferença prática entre `type` e `interface`, quando usar union e como uma checagem pode estreitar as formas possíveis de um valor.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.3 — Base moderna de JavaScript|6.3]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]]

### 8.2 — Estrutura e modelagem

**Classificação:** `solo` · `obrigatorio` · `alta` · #fundamentos

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Modelar dados e funções com tipos compostos, generics e narrowing, reconhecendo que anotações TypeScript não validam dados externos em tempo de execução.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#8.1 — Fundamentos de tipagem|8.1 — Fundamentos de tipagem]]

**Tópicos:**
- [ ] generics
- [ ] tipos compostos
- [ ] tipagem de funções
- [ ] tipagem de objetos
- [ ] narrowing

**Atividade prática:** Modele com TypeScript a resposta de um catálogo como `Resultado<Produto[]>`, incluindo sucesso e erro. Crie uma função genérica que recebe uma coleção e retorna o primeiro elemento ou `undefined`. Em separado, escreva uma validação runtime mínima de um objeto desconhecido recebido de JSON, conferindo campos essenciais antes de tratá-lo como `Produto`.

**Critério de conclusão:** Modelar uma resposta com tipos compostos e generic e explicar com exemplo por que o tipo estático não garante a forma dos dados recebidos em runtime.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#8.1 — Fundamentos de tipagem|8.1]], [[Fase_6_Frontend_Moderno#27.3 — Contrato de dados|27.3]], [[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]]

### 8.3 — Configuração e uso de TypeScript

**Classificação:** `solo` · `obrigatorio` · `media` · #ferramentas

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Configurar o compilador com `tsconfig.json`, compilar TypeScript para JavaScript e migrar gradualmente um projeto JavaScript sem alterar seu comportamento.

**Pré-requisitos:** - Pré-requisitos: [[Fase_3_Base_da_Web_JS_TS_Node#6.4 — Node.js e npm no dia a dia|6.4]] e [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]]

**Tópicos:**
- [ ] tsconfig
- [ ] compilação
- [ ] integração com projetos JavaScript
- [ ] migração JS para TS

**Atividade prática:** Escolha um módulo JavaScript pequeno do projeto de Fase 3. Configure `tsconfig` compatível com o ambiente, inclua apenas os arquivos necessários, converta o módulo para TypeScript e adapte consumidores. Compare o comportamento antes/depois, resolva os erros de tipo e documente as opções principais.

**Critério de conclusão:** Compilar o projeto sem erros nos arquivos abrangidos e explicar opções essenciais do `tsconfig`, o que é emitido e quais garantias a compilação não fornece.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#6.4 — Node.js e npm no dia a dia|6.4]], [[Fase_3_Base_da_Web_JS_TS_Node#8.2 — Estrutura e modelagem|8.2]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#6.4 — Node.js e npm no dia a dia|6.4]]

### 8.5 — Projeto incremental da fase

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 6 h–10 h (referência: 8 h).

**Objetivo:** Entregar uma primeira interface estática da ideia escolhida no Trilho A, sem framework, usando HTML, CSS, JavaScript, módulos TypeScript e dados de exemplo em JSON local.

**Pré-requisitos:** - Pré-requisitos: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]] e [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso|8.3]]

**Tópicos:**
- [ ] interface principal da ideia do Trilho A (listagem e formulário) sem framework
- [ ] dados em JSON local e módulos TypeScript organizados
- [ ] hospedagem estática: build e publicação em GitHub Pages, Netlify ou Vercel

**Atividade prática:** Construa a interface principal da ideia escolhida, com listagem e formulário. Carregue conteúdo de um JSON local e organize a lógica em módulos TypeScript. Execute o processo de build definido no projeto e publique a saída em GitHub Pages, Netlify ou Vercel. No README, registre como instalar, desenvolver, compilar e publicar, e explique que os dados ainda não têm persistência real.

**Critério de conclusão:** Publicar uma página acessível, responsiva e organizada, sem framework frontend, com dados JSON locais e instruções suficientes para reproduzir o build.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#7.3 — Dados e comunicação|7.3]], [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso de TypeScript|8.3]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#8.6 — Projeto de fase (Trilho B)|8.6]]

### 8.6 — Projeto de fase (Trilho B)

**Classificação:** `projeto` · `obrigatorio` · `alta` · #projeto

**Carga horária estimada:** 8 h–12 h (referência: 10 h).

**Objetivo:** Escolher um tipo de problema ainda não concluído dentre as opções da Fase 3 e demonstrá-lo em um protótipo estático, acessível e responsivo, sem framework e sem infraestrutura de backend.

**Pré-requisitos:** - Pré-requisito: [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso|8.3 — Configuração e uso]]

**Tópicos:**
- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

**Atividade prática:** Implemente a fatia da Fase 3 para o tipo selecionado. Use JSON local e módulos TypeScript, sem framework. Demonstre a regra principal por cenário reproduzível ou teste manual documentado, publique os arquivos estáticos e atualize a tabela de cobertura.

**Critério de conclusão:** Protótipo acessível, responsivo e publicado; critério específico do tipo demonstrado; decisão e limites documentados; tipo registrado na tabela de cobertura.

**Relações:** Relacionado: [[Fase_3_Base_da_Web_JS_TS_Node#8.3 — Configuração e uso de TypeScript|8.3]] · Complementar: [[Fase_3_Base_da_Web_JS_TS_Node#8.5 — Projeto incremental da fase|8.5]]
