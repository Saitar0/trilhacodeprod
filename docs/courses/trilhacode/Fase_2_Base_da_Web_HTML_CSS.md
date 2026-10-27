---
title: "Fase 2 — Base da web: HTML e CSS"
aliases:
  - Fase 2
tags:
  - trilhas
  - fase
tipo: fase
ordem: 2
trilha: "[[00_Trilha_Full_Stack_Estruturada]]"
status: nao-iniciada
---

# Fase 2 — Base da web: HTML e CSS

Parte da trilha [[00_Trilha_Full_Stack_Estruturada|Desenvolvimento de Software — Full Stack e Engenharia]].

## Objetivo
Construir páginas semânticas, acessíveis e responsivas com HTML e CSS, sem framework.

## Por que esta fase vem agora?
A semântica define como o conteúdo é entendido por navegadores e leitores de tela, e o layout responsivo é requisito de qualquer interface. Dominar HTML e CSS antes de JavaScript e React torna as fases seguintes compreensíveis.

## Pré-requisitos
Familiaridade com o ambiente de desenvolvimento e noções básicas de terminal (Fase 1).

## Competências
- Estruturar documentos HTML semânticos e acessíveis
- Estilizar interfaces responsivas com flexbox e grid
- Validar navegação por teclado e leitor de tela

## Critério de conclusão
Publicar uma página semântica, acessível por teclado e responsiva em três larguras, sem depender de um framework.

## Estimativa de carga horária

**Total estimado da fase:** 12,5–24,5 h (referência de planejamento: 18 h), somando estudo das unidades e projeto(s) desta fase. As faixas incluem estudo, prática, correção e revisão; consulte [[Estimativa_de_Carga_Horaria|metodologia e estimativas detalhadas]].

## Módulos
- [[#Módulo 4 — HTML e acessibilidade inicial|Módulo 4 — HTML e acessibilidade inicial]]
- [[#Módulo 5 — CSS e layout responsivo|Módulo 5 — CSS e layout responsivo]]

---

## Módulo 4 — HTML e acessibilidade inicial

**Objetivo:** Escrever um documento HTML completo e válido com metadados, títulos, texto, listas, links, imagens, tabelas e formulários, escolhendo elementos adequados ao conteúdo.

**Submódulos:** [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1 Estrutura de documento]] · [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2 HTML semântico]] · [[Fase_2_Base_da_Web_HTML_CSS#4.3 — Acessibilidade inicial|4.3 Acessibilidade inicial]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 4.1 — Estrutura de documento

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Escrever um documento HTML completo e válido com metadados, títulos, texto, listas, links, imagens, tabelas e formulários, escolhendo elementos adequados ao conteúdo.

**Pré-requisitos:** - Pré-requisitos: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1]] e [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]]

**Tópicos:**
- [ ] estrutura básica HTML
- [ ] head e body
- [ ] títulos
- [ ] parágrafos
- [ ] listas
- [ ] links
- [ ] imagens
- [ ] tabelas
- [ ] formulários

**Atividade prática:** Crie do zero uma página HTML de currículo com título e metadados corretos, nome e apresentação, listas de competências e experiências, link para um perfil, imagem com alternativa apropriada e tabela pequena com dados realmente tabulares. Inclua um formulário de contato demonstrativo com labels; como a página não terá backend, não envie nem colete dados reais. Não use framework. Valide o documento completo com um validador HTML, corrija erros de marcação e revise os avisos que se aplicarem.

**Critério de conclusão:** Escrever um documento HTML válido sem copiar um modelo pronto e justificar por que escolheu cada elemento principal.

**Relações:** Relacionado: [[Fase_1_Base_Tecnica#1.1 — Computação e software|1.1]], [[Fase_1_Base_Tecnica#1.2 — Ambiente de desenvolvimento|1.2]], [[Fase_3_Base_da_Web_JS_TS_Node#7.1 — Navegador e interação|7.1]]

### 4.2 — HTML semântico

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Organizar uma página usando elementos semânticos do HTML e justificar a escolha de cada um conforme o significado e a função do conteúdo.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1 — Estrutura de documento]]

**Tópicos:**
- [ ] header
- [ ] nav
- [ ] main
- [ ] section
- [ ] article
- [ ] aside
- [ ] footer
- [ ] semântica para organização de conteúdo

**Atividade prática:** Receba ou crie uma página composta quase só por `div`. Identifique cabeçalho, navegação, conteúdo principal, grupos temáticos, conteúdo independente, informação complementar e encerramento. Substitua contêineres apenas quando houver correspondência semântica e escreva uma justificativa curta para cada mudança.

**Critério de conclusão:** Justificar a escolha de cada elemento estrutural usado na página e explicar quando é melhor manter um contêiner genérico.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1]] · Complementar: [[Fase_2_Base_da_Web_HTML_CSS#4.3 — Acessibilidade inicial|4.3]]

### 4.3 — Acessibilidade inicial

**Classificação:** `integrado` · `obrigatorio` · `media` · #web #qualidade

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Aplicar estrutura semântica, labels, texto alternativo e navegação básica por teclado para que mais pessoas consigam compreender e operar uma página.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2 — HTML semântico]]

**Tópicos:**
- [ ] hierarquia semântica
- [ ] labels
- [ ] alt
- [ ] navegação básica
- [ ] estrutura acessível

**Atividade prática:** Use a página criada em 4.1/4.2. Percorra-a sem mouse com Tab e Shift+Tab; use Enter/Espaço quando apropriado. Observe ordem, foco visível, links e campos. Revise a hierarquia de títulos, labels e `alt`. Corrija pelo menos três problemas ou registre por que a página já atende a cada item.

**Critério de conclusão:** Navegar a página usando apenas o teclado e explicar as correções feitas em labels, alt, hierarquia e estrutura.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2]], [[Fase_6_Frontend_Moderno#29.1 — Base de testes|29.1]] · Complementar: [[Fase_2_Base_da_Web_HTML_CSS#4.2 — HTML semântico|4.2]]

---

## Módulo 5 — CSS e layout responsivo

**Objetivo:** Estilizar uma página com seletores, cascata, especificidade, box model, display, position, cores, tipografia e espaçamento, prevendo o efeito das regras aplicadas.

**Submódulos:** [[Fase_2_Base_da_Web_HTML_CSS#5.1 — Base visual|5.1 Base visual]] · [[Fase_2_Base_da_Web_HTML_CSS#5.2 — Layout moderno|5.2 Layout moderno]] · [[Fase_2_Base_da_Web_HTML_CSS#5.3 — Responsividade|5.3 Responsividade]] · [[Fase_2_Base_da_Web_HTML_CSS#5.4 — Organização visual|5.4 Organização visual]]

**Critério de conclusão:** Concluir os submódulos e demonstrar as competências descritas em suas unidades.

### 5.1 — Base visual

**Classificação:** `solo` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Estilizar uma página com seletores, cascata, especificidade, box model, display, position, cores, tipografia e espaçamento, prevendo o efeito das regras aplicadas.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1 — Estrutura de documento]]

**Tópicos:**
- [ ] seletores
- [ ] cascata
- [ ] especificidade
- [ ] box model
- [ ] display
- [ ] position
- [ ] cores
- [ ] tipografia
- [ ] espaçamento

**Atividade prática:** Estilize a página de currículo usando CSS externo. Defina tipografia, paleta com contraste legível, espaçamento consistente, largura de leitura, estados de link e estilo de formulário. Inclua duas regras concorrentes e explique qual declaração prevalece. Use DevTools para inspecionar a caixa de um elemento e registrar dimensões de conteúdo, padding, borda e margem.

**Critério de conclusão:** Prever o resultado de conflitos simples de especificidade, explicar a cascata em contexto e descrever o box model de um elemento inspecionado.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#4.1 — Estrutura de documento|4.1]] · Complementar: [[Fase_2_Base_da_Web_HTML_CSS#5.2 — Layout moderno|5.2]]

### 5.2 — Layout moderno

**Classificação:** `pratica` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2,5 h–4,5 h (referência: 3,5 h).

**Objetivo:** Compor layouts com Flexbox e CSS Grid, controlar alinhamento e distribuição e escolher a ferramenta conforme a estrutura do problema.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#5.1 — Base visual|5.1 — Base visual]]

**Tópicos:**
- [ ] flexbox
- [ ] grid
- [ ] alinhamento
- [ ] distribuição
- [ ] composição de layouts

**Atividade prática:** Escolha uma página de referência simples com cabeçalho, navegação, área principal e cartões. Construa a estrutura com HTML existente e reproduza a composição usando Grid para áreas bidimensionais e Flexbox para grupos unidimensionais. Registre por que cada contêiner usa aquele modo e como os itens se comportam quando falta espaço.

**Critério de conclusão:** Escolher entre Flexbox e Grid para cada parte do layout e justificar a escolha com base nos eixos, linhas/colunas e comportamento do conteúdo.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#5.1 — Base visual|5.1]] · Complementar: [[Fase_2_Base_da_Web_HTML_CSS#5.3 — Responsividade|5.3]]

### 5.3 — Responsividade

**Classificação:** `integrado` · `obrigatorio` · `alta` · #web

**Carga horária estimada:** 2 h–4 h (referência: 3 h).

**Objetivo:** Adaptar uma interface a diferentes larguras com medidas flexíveis e media queries, usando abordagem mobile first ou desktop first de forma justificada.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#5.2 — Layout moderno|5.2 — Layout moderno]]

**Tópicos:**
- [ ] medidas relativas
- [ ] media queries
- [ ] layout adaptável
- [ ] mobile first
- [ ] desktop first

**Atividade prática:** Adapte a página de referência em três larguras representativas: estreita, intermediária e ampla. Primeiro redimensione a viewport e registre onde texto, navegação, imagens ou cartões deixam de funcionar. Depois ajuste medidas e composição. Inclua pelo menos uma media query e indique se a estratégia é mobile first ou desktop first.

**Critério de conclusão:** Layout funciona nas três larguras testadas, sem quebra relevante, e a pessoa explica as medidas relativas, a media query e a abordagem escolhida.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#5.2 — Layout moderno|5.2]] · Complementar: [[Fase_2_Base_da_Web_HTML_CSS#5.2 — Layout moderno|5.2]]

### 5.4 — Organização visual

**Classificação:** `solo` · `obrigatorio` · `media` · #web #arquitetura

**Carga horária estimada:** 1 h–2 h (referência: 1,5 h).

**Objetivo:** Organizar estilos com separação de responsabilidades e uma convenção explícita, tornando alterações localizadas, compreensíveis e de baixo risco; reconhecer Tailwind CSS como abordagem utility-first de repertório.

**Pré-requisitos:** - Pré-requisito: [[Fase_2_Base_da_Web_HTML_CSS#5.1 — Base visual|5.1 — Base visual]]

**Tópicos:**
- [ ] estruturação de estilos
- [ ] separação de responsabilidades
- [ ] manutenção de CSS
- [ ] Tailwind CSS (utility-first) — *repertorio*

**Atividade prática:** Receba ou crie um CSS com regras duplicadas, seletores amplos e nomes inconsistentes. Defina uma convenção simples, separe regras globais das específicas, reduza duplicação e documente decisões que não forem óbvias. Compare a página antes e depois e faça uma alteração pequena de baixo risco.

**Critério de conclusão:** Explicar a convenção adotada, localizar estilos de um componente e realizar uma alteração de baixo risco sem quebrar outros elementos da página.

**Relações:** Relacionado: [[Fase_2_Base_da_Web_HTML_CSS#5.1 — Base visual|5.1]], [[Fase_6_Frontend_Moderno#26.2 — Organização|26.2]]
