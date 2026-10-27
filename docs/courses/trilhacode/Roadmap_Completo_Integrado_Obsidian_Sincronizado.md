---
aliases:
- Roadmap Completo
status: em-construcao
tags:
- estudos/roadmap
- conexoes
- desenvolvimento
tipo: roadmap-principal
title: Roadmap Completo de Desenvolvimento — Trilha Integrada
versao: 1
---

# Roadmap Completo de Desenvolvimento --- Trilha Integrada

> [!abstract] Propósito Esta nota reúne o cronograma de estudos da
> trilha e serve como fonte de conteúdo para cadastrar, relacionar e
> apresentar os tópicos no site. O mapa de conexões vive em nota própria
> e complementa a sequência com pré-requisitos, relações conceituais,
> revisitas, projetos integradores e perguntas para aprofundamento.

## Como usar esta nota

-   Marque cada checkbox conforme conseguir **explicar e aplicar** o
    conteúdo, não apenas após assistir a uma aula.
-   Use as fases como sequência sugerida, mas revisite assuntos
    anteriores quando um tema novo depender deles.
-   Cada projeto incremental deve aproveitar, quando fizer sentido, o
    trabalho feito nas fases anteriores.
-   Não adicione tecnologia ao projeto apenas para marcar um item:
    prefira uma necessidade real ou um experimento isolado.
-   Use os links internos do Obsidian para transformar os grandes temas
    em notas próprias quando o conteúdo ficar extenso.
-   As conexões do [[Mapa_de_Conexoes_Roadmap_Obsidian_Sincronizado|mapa de conexões]] representam
    relações úteis de aprendizagem e engenharia; não significam que todos
    os tópicos precisem estar ligados entre si.

## Carga horária estimada

A estimativa inicial para concluir as 131 unidades e os projetos previstos é de
**313–560 horas**, com **436 horas** como referência de planejamento. As faixas
por fase, unidade e projeto, junto da metodologia e das premissas, estão em
[[Estimativa_de_Carga_Horaria|Estimativa de carga horária]]. O intervalo
representa estudo ativo e não inclui pausas, recuperação adicional de projetos
ou tempo de produção das aulas.

## Modelo pedagógico para cadastrar esta trilha no site

Esta seção traduz o vocabulário editorial apresentado nas telas do site
em uma convenção inicial para classificar conteúdos. As chaves são
identificadores estáveis; os rótulos e as cores podem ser alterados na
interface sem que seja necessário mudar o código, desde que o sistema
trate as chaves como identificadores e não como textos de exibição.

### Tipos pedagógicos

  -----------------------------------------------------------------------
  Chave             Rótulo            Cor               Uso
  ----------------- ----------------- ----------------- -----------------
  `solo`            Tema solo         `sky`             Estudo isolado e
                                                        focado em um
                                                        assunto

  `integrado`       Tema integrado    `violet`          Conecta vários
                                                        assuntos em um
                                                        contexto

  `revisita`        Revisita          `amber`           Retorno a um tema
                                                        já visto com nova
                                                        profundidade

  `pratica`         Prática guiada    `emerald`         Aplicação prática
                                                        conduzida

  `projeto`         Projeto           `rose`            Entrega
                                                        integradora
  -----------------------------------------------------------------------

### Caráter do conteúdo

  -----------------------------------------------------------------------
  Chave             Rótulo            Cor               Uso
  ----------------- ----------------- ----------------- -----------------
  `obrigatorio`     Obrigatório       `emerald`         Parte essencial
                                                        da trilha

  `repertorio`      Repertório        `cyan`            Amplia visão e
                                                        vocabulário
                                                        técnico

  `opcional`        Opcional          `slate`           Aprofundamento
                                                        livre
  -----------------------------------------------------------------------

### Profundidade esperada

  Chave          Rótulo               Cor       Uso
  -------------- -------------------- --------- -------------------------------
  `alta`         Profundidade alta    `rose`    Domínio detalhado esperado
  `media`        Profundidade média   `amber`   Entendimento funcional
  `repertorio`   Repertório           `sky`     Noção geral, saber que existe

> \[!note\] Profundidade não é o mesmo que caráter **Caráter** indica a
> importância do conteúdo para a trilha; **profundidade** indica o nível
> de domínio esperado. Um tópico pode ser obrigatório com profundidade
> média, ou ser repertório com profundidade alta em uma área específica,
> se a trilha assim decidir.

### Tipos de relação entre tópicos

  Chave            Rótulo          Cor        Uso
  ---------------- --------------- ---------- -------------------------------
  `prerequisite`   Pré-requisito   `amber`    Deve ser estudado antes
  `complement`     Complementar    `cyan`     Enriquece o estudo deste item
  `revisit`        Revisita de     `violet`   Retoma um tema anterior
  `related`        Relacionado     `slate`    Conexão temática

Use **Pré-requisito** para dependências reais de aprendizagem;
**Complementar** para assuntos que ganham valor quando estudados em
conjunto; **Revisita de** para indicar retomadas explícitas; e
**Relacionado** para conexões úteis que não implicam ordem obrigatória.

### Tags iniciais

O vocabulário controlado completo está no [[Guia_de_Producao_de_Conteudo#3. Taxonomia de tags (vocabulário controlado)|Guia de Produção de Conteúdo]]. As onze tags permitidas são `#fundamentos`, `#web`, `#dados`, `#seguranca`, `#arquitetura`, `#infra`, `#ferramentas`, `#qualidade`, `#ia`, `#mercado` e `#projeto`. Cada submódulo usa no máximo duas. Tags são etiquetas transversais e não substituem fases, tipos pedagógicos ou relações.

### Tipos de bloco de conteúdo

Os blocos abaixo são os tipos mostrados na interface do site. Os nomes
internos devem ser tratados como identificadores técnicos estáveis.

  ----------------------------------------------------------------------------------------
  Bloco             Chave                   Campos indicados pela        Uso sugerido
                                            interface                    
  ----------------- ----------------------- ---------------------------- -----------------
  Texto teórico     `theory_text`           `body:markdown`              Explicação
                                                                         conceitual
                                                                         estruturada

  Resumo curto      `summary`               `body:textarea`              Síntese para
                                                                         revisão rápida

  Checklist         `checklist`             `items:list`                 Lista de
                                                                         objetivos ou
                                                                         tarefas
                                                                         verificáveis

  Exercício         `exercise_objective`    `format:select`,             Questão com
  objetivo                                  `prompt:markdown`,           opções, resposta
                                            `options:list`,              e correção
                                            `answer:text`,               
                                            `explanation:markdown`,      
                                            `grading:select`,            
                                            `criteria:list`,             
                                            `allow_resubmit:boolean`,    
                                            `max_score:number`           

  Exercício aberto  `exercise_open`         `prompt:markdown`,           Resposta
                                            `rubric:markdown`,           construída pelo
                                            `grading:select`,            estudante
                                            `criteria:list`,             
                                            `allow_resubmit:boolean`,    
                                            `max_score:number`           

  Desafio prático   `practical_challenge`   `prompt:markdown`,           Implementação
                                            `language:text`,             prática com
                                            `starter_code:code`,         critérios de
                                            `acceptance:list`,           aceitação
                                            `grading:select`,            
                                            `criteria:list`,             
                                            `allow_resubmit:boolean`,    
                                            `max_score:number`           

  Quiz              `quiz`                  `question:text`,             Verificação
                                            `options:list`,              rápida de
                                            `correct_index:number`,      compreensão
                                            `explanation:markdown`       

  Flashcard         `flashcard`             `front:textarea`,            Recuperação ativa
                                            `back:textarea`              de conceitos

  Snippet de código `code_snippet`          `language:text`,             Exemplo técnico
                                            `code:code`, `caption:text`  executável ou
                                                                         comentado

  Vídeo             `video_embed`           `url:url`, `caption:text`    Recurso
                                                                         audiovisual

  Link externo      `external_link`         `url:url`, `label:text`,     Documentação ou
                                            `description:textarea`       material externo

  Observação do     `instructor_note`       `body:markdown`              Orientação,
  instrutor                                                              alerta ou
                                                                         contexto
                                                                         adicional

  Revisão           `review`                `body:markdown`,             Retomada espaçada
                                            `review_after_days:number`   de conteúdo

  Material          `supplementary`         `body:markdown`, `url:url`   Leitura ou
  complementar                                                           recurso extra

  Referência        `reference`             `citation:text`, `url:url`   Fonte
                                                                         bibliográfica ou
                                                                         técnica
  ----------------------------------------------------------------------------------------

A interface também permite ativar ou desativar tipos de bloco. Desativar
um tipo deve impedir seu uso em novos conteúdos, sem apagar
silenciosamente conteúdos antigos que já o utilizem.

### Convenção editorial sugerida para cada tópico

Quando o conteúdo for cadastrado no site, procure preencher os seguintes
elementos, conforme fizer sentido:

1.  **Objetivo de aprendizagem:** o que a pessoa deverá conseguir
    explicar ou fazer.
2.  **Pré-requisitos:** o que precisa saber antes.
3.  **Conteúdo principal:** teoria e exemplos.
4.  **Prática:** exercício, checklist ou desafio que demonstre
    compreensão.
5.  **Critérios de conclusão:** evidências observáveis de que o objetivo
    foi atingido.
6.  **Conexões:** temas relacionados, revisitas e aplicações futuras.
7.  **Referências:** documentação e materiais usados.

Nem todo tópico precisa de todos os blocos. Use apenas os que melhor
atendem ao objetivo pedagógico.

### Exemplo de classificação de uma unidade

  -----------------------------------------------------------------------
  Campo                               Exemplo
  ----------------------------------- -----------------------------------
  Tópico                              Requisições HTTP e APIs

  Tipo pedagógico                     `integrado` --- Tema integrado

  Caráter                             `obrigatorio` --- Obrigatório

  Profundidade                        `media` --- Profundidade média

  Tags                                `#fundamentos`, `#web`

  Pré-requisitos                      Cliente-servidor; navegador; noção
                                      de rede

  Relações                            JSON; TypeScript; autenticação;
                                      DevTools/Network

  Blocos possíveis                    Texto teórico, resumo curto,
                                      snippet, checklist, quiz e desafio
                                      prático
  -----------------------------------------------------------------------

> \[!important\] Regra de modelagem Separe identificadores (`key`) de
> rótulos (`label`), descrições e cores. As relações entre conteúdos
> devem apontar para identificadores estáveis. Isso permite renomear,
> recolorir e expandir o vocabulário editorial sem alterar a identidade
> dos registros ou exigir mudanças no código.

------------------------------------------------------------------------

# Parte I — Cronograma de estudos

Esta parte é a lista de execução do curso e foi sincronizada com os dez arquivos de fase (revisão com as correções de dependências, projetos e lacunas de conteúdo). Os checkboxes refletem tópicos de estudo; princípios, regras de maturidade e critérios de aceitação do projeto aparecem separados para não distorcer o progresso.

> [!important] Fonte de verdade
> Os arquivos `Fase_1` a `Fase_10` são a fonte canônica dos tópicos, classificações,
> objetivos e pré-requisitos. Esta Parte I é derivada delas. Altere primeiro a fase
> e depois regenere esta lista. Detalhes operacionais (identificadores, tags, status,
> volume de blocos, rubricas e avaliação) estão no [[Guia_de_Producao_de_Conteudo|guia de produção de conteúdo]].

---

# Fase 1 — Base técnica e alfabetização de desenvolvimento

> **Objetivo:** Construir a base técnica para estudar com autonomia: entender como software e web funcionam, operar o terminal e versionar o trabalho com Git e GitHub.
> **Pré-requisitos:** Nenhum além de um computador com acesso à internet.
> **Projeto incremental:** Dotfiles e setup do ambiente versionados e repositório de estudos com README e histórico limpo; esse repositório é a base dos projetos das fases seguintes. Detalhado em [[Fase_1_Base_Tecnica#3.5 — Projeto incremental da fase|3.5 Projeto incremental da fase]].
> **Critério de conclusão:** Um repositório de estudos com README e histórico limpo e um ambiente de desenvolvimento documentado e reproduzível.

## 1.1 — Computação e software

- [ ] o que é software
- [ ] o que é programa
- [ ] como um programa é executado
- [ ] diferença entre frontend, backend e banco de dados
- [ ] diferença entre aplicação local e aplicação na web
- [ ] cliente e servidor
- [ ] navegador e servidor
- [ ] requisição e resposta
- [ ] noção de HTTP
- [ ] noção de DNS
- [ ] noção de APIs

## 1.2 — Ambiente de desenvolvimento

- [ ] sistema de arquivos
- [ ] pastas e arquivos
- [ ] extensões de arquivo
- [ ] editor de código
- [ ] terminal
- [ ] variáveis de ambiente
- [ ] instalação de ferramentas
- [ ] leitura de documentação técnica básica
- [ ] WSL (para quem usa Windows)

## 2.1 — Terminal e navegação

- [ ] navegação por diretórios
- [ ] criar, mover, copiar e apagar arquivos
- [ ] caminhos absolutos e relativos
- [ ] visualização de conteúdo
- [ ] redirecionamento básico
- [ ] pipes
- [ ] find

## 2.2 — Sistema e operação

- [ ] permissões
- [ ] usuários
- [ ] processos
- [ ] serviços
- [ ] logs
- [ ] grep
- [ ] tail
- [ ] chmod e chown

## 2.3 — Acesso remoto

- [ ] o que é SSH
- [ ] conexão SSH
- [ ] chaves SSH
- [ ] uso com GitHub
- [ ] noção de servidor remoto

## 3.1 — Git local

- [ ] init
- [ ] status
- [ ] add
- [ ] commit
- [ ] log
- [ ] diff
- [ ] restore
- [ ] reset
- [ ] branch
- [ ] .gitignore

## 3.2 — Trabalho com histórico

- [ ] merge
- [ ] rebase
- [ ] cherry-pick
- [ ] resolução de conflitos
- [ ] boas mensagens de commit

## 3.3 — GitHub

- [ ] repositórios remotos
- [ ] push
- [ ] pull
- [ ] fetch
- [ ] clone
- [ ] pull requests
- [ ] code review
- [ ] GitFlow
- [ ] organização de repositórios
- [ ] segredos e credenciais fora do repositório

## 3.4 — Revisita contínua

- [ ] versionar todo estudo daqui para frente
- [ ] revisão de histórico
- [ ] limpeza de branches
- [ ] organização de README
- [ ] commits, README e issues escritos em inglês

## 3.5 — Projeto incremental da fase

- [ ] dotfiles e setup do ambiente versionados
- [ ] repositório de estudos com README e histórico limpo
- [ ] escolher a ideia do Trilho A entre 3 candidatos (gestor de tarefas, loja virtual ou base de conhecimento)


# Fase 2 — Base da web: HTML e CSS

> **Objetivo:** Construir páginas semânticas, acessíveis e responsivas com HTML e CSS, sem framework.
> **Pré-requisitos:** Familiaridade com o ambiente de desenvolvimento e noções básicas de terminal (Fase 1).
> **Critério de conclusão:** Publicar uma página semântica, acessível por teclado e responsiva em três larguras, sem depender de um framework.

## 4.1 — Estrutura de documento

- [ ] estrutura básica HTML
- [ ] head e body
- [ ] títulos
- [ ] parágrafos
- [ ] listas
- [ ] links
- [ ] imagens
- [ ] tabelas
- [ ] formulários

## 4.2 — HTML semântico

- [ ] header
- [ ] nav
- [ ] main
- [ ] section
- [ ] article
- [ ] aside
- [ ] footer
- [ ] semântica para organização de conteúdo

## 4.3 — Acessibilidade inicial

- [ ] hierarquia semântica
- [ ] labels
- [ ] alt
- [ ] navegação básica
- [ ] estrutura acessível

## 5.1 — Base visual

- [ ] seletores
- [ ] cascata
- [ ] especificidade
- [ ] box model
- [ ] display
- [ ] position
- [ ] cores
- [ ] tipografia
- [ ] espaçamento

## 5.2 — Layout moderno

- [ ] flexbox
- [ ] grid
- [ ] alinhamento
- [ ] distribuição
- [ ] composição de layouts

## 5.3 — Responsividade

- [ ] medidas relativas
- [ ] media queries
- [ ] layout adaptável
- [ ] mobile first
- [ ] desktop first

## 5.4 — Organização visual

- [ ] estruturação de estilos
- [ ] separação de responsabilidades
- [ ] manutenção de CSS
- [ ] Tailwind CSS (utility-first) — *repertorio*


# Fase 3 — Base da web: JavaScript, TypeScript e Node.js

> **Objetivo:** Compreender a lógica de interação no navegador, programar com JavaScript, tipar e organizar o código com TypeScript e usar Node.js e npm no dia a dia.
> **Pré-requisitos:** HTML e CSS (Fase 2) e noções de terminal (Fase 1).
> **Projeto incremental:** Interface estática da ideia escolhida no 3.5 (Trilho A), sem framework, em HTML, CSS, JavaScript e TypeScript, com dados em JSON local e publicada com deploy estático. Detalhado em [[Fase_3_Base_da_Web_JS_TS_Node#8.5 — Projeto incremental da fase|8.5 Projeto incremental da fase]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_3_Base_da_Web_JS_TS_Node#8.6 — Projeto de fase (Trilho B)|8.6 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Publicar uma página funcional, acessível, responsiva e organizada, sem depender de um framework frontend.

## 6.1 — Fundamentos

- [ ] variáveis
- [ ] tipos
- [ ] operadores
- [ ] condicionais
- [ ] laços

## 6.2 — Estruturas básicas

- [ ] funções
- [ ] arrays
- [ ] objetos
- [ ] escopo
- [ ] retorno
- [ ] parâmetros

## 6.3 — Base moderna

- [ ] let e const
- [ ] arrow functions
- [ ] template strings
- [ ] destructuring
- [ ] spread e rest

## 6.4 — Node.js e npm no dia a dia

- [ ] instalar o Node.js com um gerenciador de versões
- [ ] executar um arquivo com node
- [ ] npm init e package.json
- [ ] dependencies e devDependencies
- [ ] scripts do npm
- [ ] package-lock e node_modules (e por que não vão para o Git)
- [ ] módulos ESM e CommonJS (noção)
- [ ] ESLint e Prettier básicos
- [ ] ler o relatório do npm audit (noção)

## 7.1 — Navegador e interação

- [ ] DOM
- [ ] seleção de elementos
- [ ] manipulação de conteúdo
- [ ] eventos
- [ ] formulários
- [ ] validação básica

## 7.2 — Organização do código

- [ ] módulos
- [ ] separação de arquivos
- [ ] reutilização de funções

## 7.3 — Dados e comunicação

- [ ] JSON
- [ ] métodos HTTP (GET, POST, PUT, PATCH e DELETE)
- [ ] códigos de status e headers principais
- [ ] fetch
- [ ] promises
- [ ] async/await
- [ ] tratamento de erros
- [ ] noção de CORS: por que o navegador bloqueia uma chamada

## 7.4 — Revisita de lógica

- [ ] manipulação de arrays
- [ ] transformação de dados
- [ ] composição de funções
- [ ] arrays vs. objetos como estruturas base
- [ ] noção de complexidade: O(n) na prática
- [ ] pilha e fila em cenários reais

## 7.5 — Depuração no navegador

- [ ] DevTools: console, elements e network
- [ ] breakpoints e execução passo a passo
- [ ] leitura de stack trace sem pânico
- [ ] depurar requisições na aba network

## 8.1 — Fundamentos de tipagem

- [ ] tipos primitivos
- [ ] inferência
- [ ] unions
- [ ] aliases
- [ ] interfaces

## 8.2 — Estrutura e modelagem

- [ ] generics
- [ ] tipos compostos
- [ ] tipagem de funções
- [ ] tipagem de objetos
- [ ] narrowing

## 8.3 — Configuração e uso

- [ ] tsconfig
- [ ] compilação
- [ ] integração com projetos JavaScript
- [ ] migração JS para TS

## 8.5 — Projeto incremental da fase

- [ ] interface principal da ideia do Trilho A (listagem e formulário) sem framework
- [ ] dados em JSON local e módulos TypeScript organizados
- [ ] hospedagem estática: build e publicação em GitHub Pages, Netlify ou Vercel

## 8.6 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 4 — Dados e bancos

> **Objetivo:** Modelar, persistir, consultar e otimizar dados, escolhendo o tipo de armazenamento conforme o problema e não por preferência de tecnologia.
> **Pré-requisitos:** Fase 1, noções de JSON e objetos da Fase 3 e Node/npm (6.4).
> **Projeto incremental:** Persistir o projeto incremental em PostgreSQL com modelagem própria, aplicar cache Redis em uma consulta lenta e usar uma coleção MongoDB quando houver caso de uso. Detalhado em [[Fase_4_Dados_e_Bancos#16.2 — Projeto incremental da fase|16.2 Projeto incremental da fase]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_4_Dados_e_Bancos#16.3 — Projeto de fase (Trilho B)|16.3 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Aplicação persistida em PostgreSQL, com uma consulta medida e otimizada, cache funcional em Redis e um caso de uso documental justificado.

## 9.1 — Conceitos

- [ ] o que é banco de dados
- [ ] tabelas
- [ ] linhas
- [ ] colunas
- [ ] chaves
- [ ] relacionamentos

## 9.2 — Modelagem

- [ ] entidades
- [ ] atributos
- [ ] cardinalidade
- [ ] normalização
- [ ] modelagem relacional

## 9.3 — Integridade

- [ ] chave primária
- [ ] chave estrangeira
- [ ] constraints
- [ ] consistência de dados

## 10.1 — Containerização

- [ ] Dockerfile
- [ ] imagens
- [ ] containers
- [ ] volumes
- [ ] redes

## 10.2 — Orquestração local

- [ ] docker compose
- [ ] serviços integrados
- [ ] containerizar projetos

## 11.3 — Ambiente PostgreSQL

- [ ] instalação (nativa ou em container)
- [ ] criação de banco
- [ ] criação de tabelas
- [ ] inserção e atualização
- [ ] remoção de dados

## 11.1 — Consulta de dados

- [ ] SELECT
- [ ] WHERE
- [ ] ORDER BY
- [ ] LIMIT
- [ ] aliases

## 11.2 — Relações

- [ ] JOIN
- [ ] GROUP BY
- [ ] HAVING
- [ ] subqueries

## 12.1 — Performance e leitura

- [ ] índices
- [ ] EXPLAIN
- [ ] análise de consultas
- [ ] busca textual: tsvector, índice GIN e ranking
- [ ] busca aproximada com pg_trgm

## 12.2 — Integridade e operação

- [ ] transações
- [ ] níveis de isolamento e anomalias (leitura suja, não repetível e fantasma)
- [ ] locks de linha e SELECT ... FOR UPDATE
- [ ] locking otimista (coluna de versão)
- [ ] deadlock: o que é e como evitar (noção)
- [ ] constraints (incluindo UNIQUE composta e restrição de exclusão para conflito de intervalo)
- [ ] migrations
- [ ] backup e restore

## 12.3 — Modelagem aplicada

- [ ] modelar e-commerce
- [ ] relacionamentos reais
- [ ] consistência em cenários comuns

## 13.1 — Outros bancos relacionais

- [ ] MySQL/MariaDB
- [ ] Oracle noções
- [ ] SQL Server noções

## 14.1 — MongoDB

- [ ] documentos
- [ ] coleções
- [ ] modelagem orientada a documento
- [ ] consultas básicas
- [ ] diferenças para modelo relacional

## 15.1 — Redis

- [ ] cache
- [ ] TTL
- [ ] estruturas básicas
- [ ] uso como suporte de performance
- [ ] filas simples

## 16.1 — Noções complementares

- [ ] DynamoDB
- [ ] Firestore
- [ ] Elasticsearch

## 16.2 — Projeto incremental da fase

- [ ] persistir o projeto incremental em PostgreSQL com modelagem própria
- [ ] cache Redis em uma consulta lenta e uma coleção MongoDB
- [ ] PostgreSQL, Redis e MongoDB subindo com Docker Compose

## 16.3 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 5 — Backend e arquitetura

> **Objetivo:** Construir APIs seguras, testáveis e bem organizadas em Node.js, aplicando princípios de arquitetura de forma proporcional ao problema.
> **Pré-requisitos:** Fase 3 (JavaScript, TypeScript e Node/npm) e Fase 4 (dados e Docker).
> **Projeto incremental:** API com autenticação persistindo no PostgreSQL, com cache e suíte de testes cobrindo rotas e serviços, executável com Docker Compose (Módulo 10, estudado na Fase 4). Detalhado em [[Fase_5_Backend_e_Arquitetura#24.3 — Projeto incremental da fase|24.3 Projeto incremental da fase]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_5_Backend_e_Arquitetura#24.4 — Projeto de fase (Trilho B)|24.4 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** API autenticada, persistida em PostgreSQL, com suíte de testes cobrindo rotas e serviços e executável por um comando.

## 17.1 — Fundamentos

- [ ] runtime JavaScript no servidor
- [ ] event loop
- [ ] módulos
- [ ] npm
- [ ] scripts
- [ ] jobs
- [ ] streams
- [ ] processamento assíncrono

## 17.2 — Depuração no servidor

- [ ] inspector e breakpoints no Node
- [ ] leitura de erros e stack traces do servidor
- [ ] logs úteis durante o desenvolvimento

## 18.1 — Estrutura

- [ ] métodos HTTP e códigos de status
- [ ] semântica REST: recursos e verbos
- [ ] Express como base do NestJS (noção)
- [ ] rotas
- [ ] controllers
- [ ] middlewares
- [ ] validação
- [ ] tratamento de erros
- [ ] tipos e DTOs do contrato conferidos com o frontend (revisita do 27.3)

## 18.2 — Boas práticas

- [ ] versionamento
- [ ] paginação
- [ ] padronização de resposta
- [ ] documentação com OpenAPI/Swagger
- [ ] organização de camadas
- [ ] idempotência em endpoints de escrita (Idempotency-Key)

## 18.3 — Tempo real

- [ ] polling, SSE e WebSocket: diferenças e quando usar cada um
- [ ] autenticação na conexão
- [ ] salas ou canais e difusão (broadcast)
- [ ] reconexão com backoff e retomada a partir do último evento
- [ ] mensagens duplicadas e fora de ordem
- [ ] estado compartilhado: last-write-wins e resolução de conflitos (OT e CRDT, noção)
- [ ] limites da escala horizontal (noção; retomado na Fase 9)

## 19.1 — ORM e acesso a dados

- [ ] o que é ORM
- [ ] vantagem e limite de ORM
- [ ] mapeamento objeto-relacional
- [ ] Prisma ou TypeORM

## 19.2 — Regra de maturidade

> **Princípios — nota do instrutor, sem checkbox:**
- entender SQL antes de abstrair com ORM
- reconhecer quando ORM ajuda
- reconhecer quando ORM atrapalha

## 20.1 — Autenticação

- [ ] JWT
- [ ] refresh token
- [ ] OAuth2
- [ ] sessão vs token
- [ ] cookies e armazenamento de tokens

## 20.2 — Segurança básica

- [ ] hash de senha
- [ ] CORS
- [ ] SQL injection e prepared statements
- [ ] CSRF no backend (tokens e SameSite)
- [ ] segredos
- [ ] variáveis de ambiente
- [ ] OWASP básico

## 20.3 — Segurança aplicada

- [ ] riscos comuns em APIs
- [ ] autorização
- [ ] exposição de dados
- [ ] proteção de credenciais
- [ ] rate limiting
- [ ] dados pessoais e LGPD (noções): minimização, base legal e retenção

## 21.1 — Base conceitual

- [ ] acoplamento
- [ ] coesão
- [ ] separação de responsabilidades

## 22.1 — Estrutura de framework

- [ ] módulos
- [ ] controllers
- [ ] providers
- [ ] injeção de dependência

## 22.2 — Organização forte

- [ ] DTOs
- [ ] pipes
- [ ] guards
- [ ] arquitetura mais estruturada

## 23.1 — Modelos

- [ ] Clean Architecture
- [ ] Hexagonal
- [ ] SOLID
- [ ] design patterns

## 23.2 — Base de raciocínio

- [ ] estruturas de dados
- [ ] algoritmos básicos
- [ ] escolha de estrutura
- [ ] custo conceitual

## 23.3 — Regra dura

> **Princípios — nota do instrutor, sem checkbox:**
- arquitetura só depois de sistema simples entendido
- padrão não substitui clareza

## 24.1 — Tipos de teste

- [ ] unitários
- [ ] integração
- [ ] mocks
- [ ] cobertura

## 24.2 — Aplicação

- [ ] testes em serviços
- [ ] testes em rotas
- [ ] testes com banco
- [ ] isolamento de dependências

## 24.3 — Projeto incremental da fase

- [ ] API com autenticação persistindo no PostgreSQL
- [ ] Docker Compose subindo app + banco + cache
- [ ] suíte de testes cobrindo rotas e serviços

## 24.4 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 6 — Frontend moderno

> **Objetivo:** Construir interfaces modernas com React, conectadas à API construída na Fase 5, com estados explícitos, testes e performance medida.
> **Pré-requisitos:** Fase 3 (JavaScript, DOM, fetch e TypeScript), noções de dados da Fase 4 e a API da Fase 5.
> **Projeto incremental:** Frontend React tipado, conectado à API real da Fase 5, com estados de interface, testes de comportamento e medição de performance.
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_6_Frontend_Moderno#31.5 — Projeto de fase (Trilho B)|31.5 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Frontend React tipado, conectado à API da Fase 5, com os estados de interface cobertos por testes de comportamento e uma medição de performance.

## 25.1 — Fundamentos

- [ ] por que React existe
- [ ] componentes
- [ ] JSX
- [ ] props
- [ ] renderização

## 25.2 — Estado e interação

- [ ] state
- [ ] eventos
- [ ] listas
- [ ] renderização condicional
- [ ] formulários

## 26.1 — Hooks

- [ ] useEffect
- [ ] useRef
- [ ] useMemo
- [ ] useCallback

## 26.2 — Organização

- [ ] context
- [ ] hooks customizados
- [ ] composição de componentes
- [ ] separação de responsabilidades

## 27.1 — Comunicação com backend

- [ ] requisições REST
- [ ] autenticação por token
- [ ] headers
- [ ] paginação

## 27.2 — Estados de interface

- [ ] loading
- [ ] retry
- [ ] erro
- [ ] vazio
- [ ] sucesso

## 27.3 — Contrato de dados

- [ ] integração com JSON
- [ ] contrato definido no backend ([[Fase_5_Backend_e_Arquitetura#18.1 — Estrutura|18.1]])
- [ ] tipagem de resposta
- [ ] tipos compartilhados entre frontend e backend (conferidos no 18.1)
- [ ] tratamento defensivo

## 27.4 — Segurança no navegador

- [ ] XSS refletido e armazenado
- [ ] por que o React escapa o conteúdo e onde deixa de proteger (dangerouslySetInnerHTML e URLs)
- [ ] sanitização de HTML
- [ ] CSRF e cookies (SameSite e HttpOnly)
- [ ] onde guardar o token: memória, cookie HttpOnly e localStorage, com os riscos de cada um
- [ ] Content Security Policy (noção)
- [ ] segredos e variáveis públicas no bundle
- [ ] dependências: npm audit e cadeia de suprimentos (noção)

## 28.1 — Ferramentas

- [ ] Vite
- [ ] Zustand
- [ ] TanStack Query

## 28.2 — Gerência de dados

- [ ] estado local
- [ ] estado global
- [ ] estado remoto
- [ ] cache
- [ ] invalidação

## 28.3 — Organização

> **Princípios — nota do instrutor, sem checkbox:**
- distinguir UI state de server state
- evitar complexidade desnecessária

## 29.1 — Base de testes

- [ ] Jest ou Vitest
- [ ] Testing Library
- [ ] testes de componente
- [ ] testes de comportamento

## 29.2 — Integração e borda

- [ ] mocks de API
- [ ] testes e2e com Playwright

## 30.1 — Otimização

- [ ] memoization
- [ ] lazy loading
- [ ] code splitting
- [ ] virtualização

## 30.2 — Maturidade

> **Princípios — nota do instrutor, sem checkbox:**
- reduzir re-render
- só otimizar o que realmente é gargalo
- reconhecer quando performance é problema real

## 31.1 — Next.js

- [ ] rotas
- [ ] SSR
- [ ] SSG
- [ ] API routes
- [ ] deploy
- [ ] visão arquitetural

## 31.2 — React Native

- [ ] visão geral
- [ ] posicionamento no ecossistema

## 31.3 — Vue.js e Angular

- [ ] Vue 3
- [ ] Vue 2 legado — *opcional*
- [ ] Angular 2+
- [ ] módulos
- [ ] serviços
- [ ] leitura comparativa de mercado

## 31.4 — Projeto incremental da fase

- [ ] frontend React tipado do projeto principal
- [ ] conexão com a API real, com os cinco estados de interface
- [ ] testes de comportamento do fluxo principal
- [ ] uma medição de performance antes e depois de uma otimização

## 31.5 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 7 — Infraestrutura, deploy e cloud

> **Objetivo:** Automatizar a entrega da aplicação e provisionar infraestrutura em nuvem com CI/CD, cloud e infraestrutura como código.
> **Pré-requisitos:** Fase 1 (terminal, SSH e Git), Fase 4 (dados e containers) e Fase 5 (API e testes).
> **Projeto incremental:** Deploy automatizado do projeto na AWS com Terraform e pipeline. Detalhado em [[Fase_7_Infra_Deploy_e_Cloud#36.2 — Ambientes|36.2 Ambientes]].

> [!note] Trilho B na Fase 8
> O projeto de fase (Trilho B) desta trilha de infraestrutura fica na [[Fase_8_Infra_Operacao#39.3 — Projeto de fase (Trilho B)|Fase 8]], junto com o postmortem e a observabilidade.
> **Critério de conclusão:** Deploy automatizado do projeto na AWS com Terraform e pipeline, com recursos destruídos ao fim do laboratório.

## 32.1 — Automação

- [ ] GitHub Actions
- [ ] build
- [ ] teste
- [ ] lint
- [ ] quality gates
- [ ] Sonar — *repertorio*

## 32.2 — Entrega

- [ ] deploy automatizado
- [ ] staging
- [ ] rollback

## 33.1 — Conceitos

- [ ] filas
- [ ] tópicos
- [ ] DLQ
- [ ] idempotência
- [ ] retries

## 34.1 — Base de cloud

- [ ] IAM
- [ ] EC2
- [ ] S3
- [ ] RDS
- [ ] VPC básica
- [ ] domínio e DNS na prática
- [ ] TLS/HTTPS
- [ ] reverse proxy e load balancer
- [ ] custos
- [ ] free tier
- [ ] alertas de orçamento
- [ ] destruir recursos ao fim do estudo
- [ ] CDN — *repertorio*

## 35.1 — Serviços e eventos

- [ ] Lambda
- [ ] API Gateway
- [ ] SQS
- [ ] SNS
- [ ] EventBridge
- [ ] ElastiCache

## 36.1 — Infra como código

- [ ] providers
- [ ] state
- [ ] módulos
- [ ] variáveis

## 36.2 — Ambientes

- [ ] múltiplos ambientes com tfvars e workspaces
- [ ] provisionamento de stack
- [ ] Terragrunt — *repertorio*


# Fase 8 — Orquestração, observabilidade e operação

> **Objetivo:** Operar a aplicação publicada: orquestração gerenciada, observabilidade e resposta madura a incidentes.
> **Pré-requisitos:** Fase 7 (pipeline, cloud e Terraform).
> **Projeto incremental:** Tracing e métricas em dashboard e postmortem simulado de um incidente, sobre o deploy da Fase 7. Detalhado em [[Fase_8_Infra_Operacao#39.2 — Projeto incremental da fase|39.2 Projeto incremental da fase]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_8_Infra_Operacao#39.3 — Projeto de fase (Trilho B)|39.3 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Deploy observado com dashboard de métricas e traces e um postmortem simulado de incidente.

## 37.1 — Serviços gerenciados

- [ ] ECS
- [ ] EKS

## 37.2 — Kubernetes básico

- [ ] pods
- [ ] deployments
- [ ] services

## 37.3 — GCP noções

- [ ] Cloud Run
- [ ] Pub/Sub
- [ ] GKE

## 38.1 — Sinais operacionais

- [ ] logs estruturados
- [ ] métricas
- [ ] tracing

## 38.2 — Ferramentas

- [ ] OpenTelemetry
- [ ] Prometheus
- [ ] Grafana
- [ ] New Relic — *opcional*

## 39.1 — Operação madura

- [ ] análise de causa raiz
- [ ] postmortem
- [ ] SLA
- [ ] SLO
- [ ] runbooks
- [ ] ADRs

## 39.2 — Projeto incremental da fase

- [ ] deploy automatizado do projeto na AWS com Terraform e pipeline
- [ ] tracing e métricas em dashboard + postmortem simulado de um incidente

## 39.3 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 9 — Escala, mensageria e pluralidade de mercado

> **Objetivo:** Entender processamento assíncrono e sistemas distribuídos e ler outras stacks de mercado por comparação, sem reescrever o projeto desnecessariamente.
> **Pré-requisitos:** Fases 5 e 8, em especial [[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]] (mensageria: conceitos) e a operação com observabilidade.
> **Projeto incremental:** Fila no projeto com produtor e consumidor, retry e DLQ; serviço extra via mensageria e comparação escrita com a stack escolhida. Detalhado em [[Fase_9_Escala_Mensageria_e_Mercado#46.2 — Projeto incremental da fase|46.2 Projeto incremental da fase]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_9_Escala_Mensageria_e_Mercado#46.3 — Projeto de fase (Trilho B)|46.3 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Fila no projeto com produtor e consumidor, retry e DLQ funcionando, com decisões documentadas e comparação escrita com uma segunda stack.

## 40.1 — RabbitMQ

- [ ] filas e exchanges
- [ ] bindings e roteamento
- [ ] ack e nack
- [ ] prefetch e consumo concorrente
- [ ] DLQ no RabbitMQ

## 40.2 — Kafka

- [ ] producers
- [ ] consumers
- [ ] partições
- [ ] grupos
- [ ] offsets
- [ ] retenção de mensagens

## 40.3 — Comparação

## 41.1 — Arquitetura distribuída

- [ ] comunicação síncrona
- [ ] comunicação assíncrona
- [ ] saga
- [ ] outbox
- [ ] resiliência
- [ ] circuit breaker
- [ ] tolerância a falhas

## 41.2 — Regra dura

> **Princípios — nota do instrutor, sem checkbox:**
- microsserviço não é evolução automática
- complexidade distribuída cobra caro

## 42.1 — Base

- [ ] fundamentos de Python: sintaxe, tipos e pacotes (só se for a stack construída)
- [ ] Django
- [ ] DRF
- [ ] ORM
- [ ] migrations

## 42.2 — Ecossistema

- [ ] Celery
- [ ] pytest
- [ ] Poetry

## 42.3 — Noções

- [ ] FastAPI
- [ ] Flask

## 43.1 — Stack

- [ ] fundamentos de PHP 7.4+ e Composer (só se for a stack construída)
- [ ] Laravel
- [ ] Eloquent
- [ ] filas
- [ ] APIs
- [ ] autenticação

## 43.2 — Noções

- [ ] Slim
- [ ] Phalcon

## 44.1 — Stack

- [ ] fundamentos de C# e NuGet (só se for a stack construída)
- [ ] ASP.NET Core
- [ ] EF Core
- [ ] Dapper
- [ ] xUnit
- [ ] SQL Server

## 44.2 — Legado

- [ ] WebForms

## 45.1 — Stack

- [ ] fundamentos de Java e Maven ou Gradle (só se for a stack construída)
- [ ] Spring
- [ ] injeção de dependência
- [ ] JPA
- [ ] testes
- [ ] integração com Kafka

## 46.1 — Realidade de mercado

- [ ] estratégias de modernização
- [ ] strangler pattern
- [ ] débito técnico
- [ ] alta volumetria

## 46.2 — Projeto incremental da fase

- [ ] fila no projeto: produtor e consumidor com retry e DLQ
- [ ] serviço extra via mensageria + comparação escrita com a stack escolhida

## 46.3 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura


# Fase 10 — IA aplicada, fechamento técnico e posicionamento

> **Objetivo:** Integrar IA a uma aplicação de forma segura, mensurável e proporcional, fechar o projeto final e preparar o posicionamento profissional.
> **Pré-requisitos:** Fases 5 a 9, em especial autenticação e autorização (20.x), observabilidade (38.x) e filas ([[Fase_7_Infra_Deploy_e_Cloud#33.1 — Conceitos|33.1]] e 40.x).
> **Projeto incremental:** Expandir o projeto incremental acumulado (e não começar do zero) até uma aplicação full stack com IA. Detalhado em [[Fase_10_IA_Aplicada_e_Posicionamento#52.1 — Estrutura do projeto final|52.1 Estrutura do projeto final]].
> **Projeto de fase (Trilho B):** Uma ideia entre 3, com rotação de tipos, conforme o [[Guia_Projetos_e_Rotacao_de_Tipos|guia de projetos]]. Detalhado em [[Fase_10_IA_Aplicada_e_Posicionamento#52.2 — Projeto de fase (Trilho B)|52.2 Projeto de fase (Trilho B)]].
> **Critério de conclusão:** Aplicação full stack com funcionalidade de IA, testes, CI/CD, deploy na AWS, observabilidade, README e diagrama de arquitetura, evoluída a partir do projeto acumulado.

## 47.1 — Uso assistido

- [ ] Copilot
- [ ] assistentes de código
- [ ] agentes de código
- [ ] boas práticas de prompt
- [ ] revisão crítica do código gerado

## 48.1 — Fundamentos

- [ ] OpenAI
- [ ] Claude
- [ ] Azure OpenAI — *repertorio*
- [ ] Vertex AI — *repertorio*

## 48.2 — Operação

- [ ] engenharia de prompt
- [ ] streaming
- [ ] SSE e streaming no navegador
- [ ] custo
- [ ] latência

## 49.1 — Base

- [ ] embeddings
- [ ] upload e ingestão de documentos
- [ ] bancos vetoriais
- [ ] chunking
- [ ] busca semântica
- [ ] avaliação de respostas

## 50.1 — Orquestração

- [ ] function calling
- [ ] LangChain
- [ ] LangGraph
- [ ] Semantic Kernel — *repertorio*
- [ ] CrewAI — *repertorio*

## 51.1 — Segurança e governança

- [ ] Model Context Protocol
- [ ] prompt injection
- [ ] vazamento de credenciais
- [ ] guardrails
- [ ] governança de dados
- [ ] privacidade e LGPD aplicadas a IA: dados pessoais em prompts, retenção e exclusão

## 52.1 — Estrutura do projeto final

> Os itens abaixo são critérios de aceitação do projeto, e não tópicos de estudo.
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

## 52.2 — Projeto de fase (Trilho B)

- [ ] escolher 1 das 3 ideias oferecidas (tipo ainda não concluído)
- [ ] entregar a versão da fase da ideia escolhida
- [ ] registrar o tipo concluído na tabela de cobertura

## 53.1 — Portfólio e presença

- [ ] currículo
- [ ] LinkedIn
- [ ] GitHub organizado (repositórios fixados, READMEs e histórico)
- [ ] apresentar cada projeto: problema, decisões, trade-offs e métricas

## 53.2 — Inglês técnico e entrevistas

- [ ] inglês de entrevista: apresentação pessoal e explicação de decisões
- [ ] respostas comportamentais estruturadas (situação, ação e resultado)
- [ ] escrita técnica em inglês (PRs, ADRs e README)
- [ ] entrevistas simuladas, com gravação e revisão

## 53.3 — System design

- [ ] requisitos funcionais e não funcionais
- [ ] estimativa de capacidade (ordens de grandeza)
- [ ] desenho de API, dados, cache e fila
- [ ] trade-offs: consistência, disponibilidade, latência e custo
- [ ] exercícios clássicos (encurtador de URL, feed e fila de notificações)

## 53.4 — Algoritmos para entrevistas técnicas

- [ ] arrays, strings e mapas hash
- [ ] dois ponteiros e janela deslizante
- [ ] pilha, fila e recursão
- [ ] árvores e grafos (noção)
- [ ] busca, ordenação e análise de complexidade
- [ ] prática regular com exercícios cronometrados


---

## Mapa de conexões

O mapa de conexões vive em nota própria: [[Mapa_de_Conexoes_Roadmap_Obsidian_Sincronizado|Mapa de Conexões do Roadmap de Desenvolvimento]].
