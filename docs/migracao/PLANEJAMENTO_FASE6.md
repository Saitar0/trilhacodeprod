# Planejamento da migração estrutural — Fase 6

**Estado:** rascunho [PROPOSTA], sem geração da árvore. **Base:** `a229795d9296b71ab7d1adca1d71a9a3baaaf36a`. **Unidades:** 20 (18 convencionais, 2 projetos). **Assuntos propostos:** 57. **Arquivos estimados:** 449.

## Fontes e confiabilidade

- Foram conferidos a página da fase, referências e os 20 arquivos ativos. Não foi localizado mapa anterior de assuntos da Fase 6 no checkout. Assim, as divisões e a cobertura abaixo são [PROPOSTA], não decisões históricas aprovadas.
- Metadados vêm em listas Markdown sob o H1; o manifesto conserva os valores e prevê conversão literal ao YAML do README.
- A página da fase estima 39–71 h, com referência de 55 h; a soma dos 20 metadados é 3.300 minutos (55 h), em concordância com a referência.
- Contagem observada nas fontes: 74 microtópicos de teoria, 80 questões em quiz com resposta em linha, seis flashcards, 52 atividades práticas convencionais e oito marcos de projeto. Os projetos também têm dois escopos, duas rubricas comuns 0–4 e dois checklists finais.
- A contagem antiga de 90 questões não confere com os arquivos: foram localizadas 80 questões de quiz. Não foram acrescentadas questões para forçar a contagem anterior.
- As fontes listam 52 atividades convencionais e oito marcos de projeto. Os marcos ficam registrados como entregas de projeto, não como exercícios convencionais.

## Inventário por unidade

| Unidade | Módulo | Título | tipo / caráter / profundidade | minutos | tags | teoria | quiz | práticas | outros |
|---|---|---|---|---:|---|---:|---:|---:|---|
| 25.1 | Fundamentos de React | 25.1 — Fundamentos | solo / obrigatorio / alta | 180 | #web, #react | 5 | 5 | 3 | 3 soluções; 3 rubricas descritivas |
| 25.2 | Fundamentos de React | 25.2 — Estado e interação | solo / obrigatorio / alta | 180 | #web, #react, #interacao | 5 | 5 | 3 | 3 soluções; 3 rubricas descritivas |
| 26.1 | Hooks e organização de componentes | 26.1 — Hooks | solo / obrigatorio / alta | 180 | #web, #react, #hooks | 5 | 5 | 3 | 3 soluções; 3 rubricas descritivas |
| 26.2 | Hooks e organização de componentes | 26.2 — Organização | integrado / obrigatorio / media | 90 | #web, #arquitetura, #react | 4 | 5 | 3 | 3 soluções; 3 rubricas descritivas |
| 27.1 | Integração com o backend | 27.1 — Comunicação com backend | integrado / obrigatorio / alta | 180 | #web, #api, #seguranca | 5 | 5 | 3 | 3 soluções; 3 rubricas descritivas |
| 27.2 | Integração com o backend | 27.2 — Estados de interface | pratica / obrigatorio / alta | 210 | #web, #qualidade | 5 | 5 | 3 | sem solução ou rubrica identificada |
| 27.3 | Integração com o backend | 27.3 — Contrato de dados | integrado / obrigatorio / media | 90 | #web, #dados | 4 | 5 | 3 | rubrica comum 0–4 para as três práticas |
| 27.4 | Integração com o backend | 27.4 — Segurança no navegador | integrado / obrigatorio / media | 90 | #web, #seguranca | 4 | 5 | 3 | rubrica comum 0–4 para as três práticas |
| 28.1 | Gerência de estado e dados remotos | 28.1 — Ferramentas | solo / obrigatorio / media | 90 | #ferramentas, #web | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 28.2 | Gerência de estado e dados remotos | 28.2 — Gerência de dados | integrado / obrigatorio / media | 90 | #web, #dados | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 28.3 | Gerência de estado e dados remotos | 28.3 — Organização | integrado / obrigatorio / media | 90 | #web, #arquitetura | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 29.1 | Testes de frontend | 29.1 — Base de testes | solo / obrigatorio / media | 90 | #qualidade, #web | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 29.2 | Testes de frontend | 29.2 — Integração e borda | pratica / obrigatorio / media | 120 | #qualidade, #web | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 30.1 | Performance de frontend | 30.1 — Otimização | solo / obrigatorio / media | 90 | #web | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 30.2 | Performance de frontend | 30.2 — Maturidade | integrado / obrigatorio / media | 90 | #web, #qualidade | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 31.1 | Ecossistema: Next.js, React Native, Vue e Angular | 31.1 — Next.js | solo / obrigatorio / media | 90 | #web | 4 | 5 | 3 | sem solução ou rubrica identificada |
| 31.2 | Ecossistema: Next.js, React Native, Vue e Angular | 31.2 — React Native | solo / repertorio / repertorio | 45 | #web | 3 | 0 | 2 | 3 flashcards |
| 31.3 | Ecossistema: Next.js, React Native, Vue e Angular | 31.3 — Vue.js e Angular | solo / repertorio / repertorio | 45 | #web | 2 | 0 | 2 | 3 flashcards |
| 31.4 | Ecossistema: Next.js, React Native, Vue e Angular | 31.4 — Projeto incremental da fase | projeto / obrigatorio / alta | 600 | #web, #qualidade | 0 | 0 | 0 | 4 marcos; rubrica 0–4; checklist final |
| 31.5 | Ecossistema: Next.js, React Native, Vue e Angular | 31.5 — Projeto de fase (Trilho B) | projeto / obrigatorio / alta | 660 | #projeto | 0 | 0 | 0 | 4 marcos; rubrica 0–4; checklist final |

## Divisão de assuntos e cobertura detalhada

Todos os agrupamentos estão marcados como [PROPOSTA]. Q/P indicam atividade avaliativa e ficam fisicamente em um assunto quando exclusivos ou em `90_integracao/` quando compartilhados. A classificação compartilhada representa conteúdo que exige mais de um dos assuntos, não mera citação.

### 25.1 — Fundamentos

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_componentes_modelo_declarativo_props` | Microtópico 1 — React descreve a interface a partir dos dados; Microtópico 2 — Componentes são funções que compõem a UI; Microtópico 4 — Props são entradas de leitura do componente; Microtópico 5 — Renderização precisa ser previsível | Q02, Q03, Q04, Q05 | — | P01, P03 | P02 | — |
| `02_jsx_transformacao` | Microtópico 3 — JSX é sintaxe para descrever elementos | Q01 | — | — | P02 | — |

**Classificação individual de questões:**
- Q01 — **Conceito:** JSX é uma linguagem que o navegador interpreta diretamente como HTML? → `02_jsx_transformacao` (exclusiva).
- Q02 — **Leitura de componente:** em um TaskCard que recebe title e completed, quem decide os valores de cada cartão quando a lista é renderizada? → `01_componentes_modelo_declarativo_props` (exclusiva).
- Q03 — **Análise de código:** por que alterar task.completed dentro de TaskCard é um problema? → `01_componentes_modelo_declarativo_props` (exclusiva).
- Q04 — **Classificação:** uma função altera diretamente o texto de um nó do DOM dentro do corpo do componente. Isso segue o modelo declarativo de React? → `01_componentes_modelo_declarativo_props` (exclusiva).
- Q05 — **Transferência:** uma tela contém quatro cartões com o mesmo formato e dados distintos. Que parte é apropriado reutilizar e que dados devem variar? → `01_componentes_modelo_declarativo_props` (exclusiva).

**Classificação individual de práticas:**
- P01 — Converta marcação repetida em componente → `01_componentes_modelo_declarativo_props` (exclusiva; solução existente, rubrica existente na atividade).
- P02 — Corrija JSX e explique o resultado → `01_componentes_modelo_declarativo_props`, `02_jsx_transformacao` (compartilhada; solução existente, rubrica existente na atividade).
- P03 — Detecte renderização impura → `01_componentes_modelo_declarativo_props` (exclusiva; solução existente, rubrica existente na atividade).

**Conexões/pré-requisitos registrados:** Pré-requisitos: 6.3, 7.1 e 7.2. Retoma interação com DOM de 7.1; prepara props, estado e interação em 25.2.

### 25.2 — Estado e interação

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_estado_snapshot_formulario_controlado` | Microtópico 1 — Estado é a memória que muda a interface; Microtópico 5 — Formulário controlado mantém uma fonte clara | Q01 | — | — | P01, P02, P03 | — |
| `02_eventos_atualizadores` | Microtópico 2 — Eventos pedem mudanças; renderização descreve o resultado | Q02 | — | — | P03 | — |
| `03_colecoes_imutaveis_identidade` | Microtópico 3 — Atualize arrays e objetos sem mutar o estado | Q03, Q04 | — | — | P01, P03 | — |
| `04_valores_derivados_condicoes_filtros` | Microtópico 4 — Derive condições e filtros do estado essencial | Q05 | — | — | P02 | — |

**Classificação individual de questões:**
- Q01 — **Snapshot:** depois de chamar setCount(count + 1), o que console.log(count) no mesmo handler deve mostrar? → `01_estado_snapshot_formulario_controlado` (exclusiva).
- Q02 — **Escolha de atualização:** três ações no mesmo handler devem acrescentar uma unidade ao valor atual. Qual forma evita que todas usem o mesmo snapshot? → `02_eventos_atualizadores` (exclusiva).
- Q03 — **Diagnóstico:** um item foi removido com tasks.splice(index, 1) e setTasks(tasks). Por que isso pode não atualizar a UI de modo correto? → `03_colecoes_imutaveis_identidade` (exclusiva).
- Q04 — **Identidade:** ao reordenar e remover cartões, por que key baseada no índice pode associar estado local ao cartão errado? → `03_colecoes_imutaveis_identidade` (exclusiva).
- Q05 — **Modelo da tela:** deve-se guardar tasks, visibleTasks e completedCount em três estados independentes? → `04_valores_derivados_condicoes_filtros` (exclusiva).

**Classificação individual de práticas:**
- P01 — Construa uma lista interativa → `01_estado_snapshot_formulario_controlado`, `03_colecoes_imutaveis_identidade` (compartilhada; solução existente, rubrica existente na atividade).
- P02 — Adicione filtros e estados de interface → `01_estado_snapshot_formulario_controlado`, `04_valores_derivados_condicoes_filtros` (compartilhada; solução existente, rubrica existente na atividade).
- P03 — Corrija uma lista com estado defeituoso → `01_estado_snapshot_formulario_controlado`, `02_eventos_atualizadores`, `03_colecoes_imutaveis_identidade` (compartilhada; solução existente, rubrica existente na atividade).

**Conexões/pré-requisitos registrados:** Pré-requisito: 25.1. Revisa lógica e eventos de 6.2 e 7.1; prepara hooks em 26.1, formulários em 27.1 e aplicação em 29.1.

### 26.1 — Hooks

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_regras_de_chamada` | Microtópico 1 — Hooks obedecem a regras de chamada | Q01 | — | — | P01 | — |
| `02_effects_sincronizacao_limpeza` | Microtópico 2 — useEffect sincroniza um sistema externo | Q03 | — | P02 | P01 | — |
| `03_refs_valores_imperativos` | Microtópico 3 — useRef mantém um valor que não desenha a tela | Q02 | — | — | P01 | — |
| `04_memoizacao_decisao_por_evidencia` | Microtópico 4 — useMemo e useCallback otimizam valores diferentes; Microtópico 5 — Escolha pelo problema e confira o ciclo | Q04, Q05 | — | P03 | P01 | — |

**Classificação individual de questões:**
- Q01 — **Diagnóstico:** um componente chama useEffect somente quando isOpen é true. Qual é o problema e como reorganizar? → `01_regras_de_chamada` (exclusiva).
- Q02 — **Escolha de ferramenta:** é preciso focar um input após clicar num botão, sem que a própria referência determine conteúdo visível. Qual Hook é apropriado? → `03_refs_valores_imperativos` (exclusiva).
- Q03 — **Limpeza:** um efeito registra um listener de resize e depende de uma configuração atual. O que precisa acontecer quando a configuração muda e quando o componente sai da tela? → `02_effects_sincronizacao_limpeza` (exclusiva).
- Q04 — **Distinção:** qual a diferença entre useMemo e useCallback? → `04_memoizacao_decisao_por_evidencia` (exclusiva).
- Q05 — **Avaliação:** useMemo é necessário para que o filtro de uma lista seja correto? → `04_memoizacao_decisao_por_evidencia` (exclusiva).

**Classificação individual de práticas:**
- P01 — Audite e reorganize a chamada de Hooks → `01_regras_de_chamada`, `02_effects_sincronizacao_limpeza`, `03_refs_valores_imperativos`, `04_memoizacao_decisao_por_evidencia` (compartilhada; solução existente, rubrica existente na atividade).
- P02 — Sincronize uma assinatura com limpeza → `02_effects_sincronizacao_limpeza` (exclusiva; solução existente, rubrica existente na atividade).
- P03 — Justifique ou retire memoização → `04_memoizacao_decisao_por_evidencia` (exclusiva; solução existente, rubrica existente na atividade).

**Conexões/pré-requisitos registrados:** Pré-requisito: 25.2. Complementa organização em 26.2, comunicação com backend em 27.1 e análise de desempenho em 30.1.

### 26.2 — Organização

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_responsabilidades_ownership_composicao` | Microtópico 1 — Organize pelo fluxo e pela responsabilidade; Microtópico 2 — Composição e ownership deixam dados explícitos | Q01, Q03 | — | P01 | — | — |
| `02_custom_hooks` | Microtópico 3 — Custom Hooks compartilham lógica | Q02 | — | P02 | — | — |
| `03_context_compartilhamento` | Microtópico 4 — Context alcança descendentes quando props viram ruído | Q04, Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — **Escolha de fluxo:** uma prop passa por dois componentes que não a usam até chegar ao único consumidor. Qual alternativa pode manter o fluxo explícito com menos encaminhamento? → `01_responsabilidades_ownership_composicao` (exclusiva).
- Q02 — **Estado compartilhado:** duas chamadas ao mesmo custom Hook useField controlam dois campos. Elas compartilham o valor por terem o mesmo nome de Hook? → `02_custom_hooks` (exclusiva).
- Q03 — **Organização:** dois painéis precisam garantir que só um esteja aberto por vez. Onde deve ficar o estado isOpen? → `01_responsabilidades_ownership_composicao` (exclusiva).
- Q04 — **Context:** tema é usado por componentes em níveis profundos e muitos elementos não o encaminham nem consomem. Que vantagem Context oferece? → `03_context_compartilhamento` (exclusiva).
- Q05 — **Custo de atualização:** o provider passa um objeto com autenticação, formulário e dados de busca para todos os consumidores. Qual risco de organização investigar? → `03_context_compartilhamento` (exclusiva).

**Classificação individual de práticas:**
- P01 — Defina árvore e dono de cada dado → `01_responsabilidades_ownership_composicao` (exclusiva; solução existente, rubrica existente na atividade).
- P02 — Extraia lógica em custom Hook sem compartilhar estado por engano → `02_custom_hooks` (exclusiva; solução existente, rubrica existente na atividade).
- P03 — Decida entre props, composição e Context → `03_context_compartilhamento` (exclusiva; solução existente, rubrica existente na atividade).

**Conexões/pré-requisitos registrados:** Pré-requisito: 26.1. Relaciona-se à composição de 25.1, ao levantamento de estado de 25.2 e prepara comunicação com backend em 27.1.

### 27.1 — Comunicação com backend

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_contrato_requisicao_resposta` | Microtópico 1 — Requisição e resposta seguem o contrato da API | Q01 | — | — | P01 | — |
| `02_autenticacao_credenciais` | Microtópico 2 — Autenticação e credenciais exigem decisão explícita | Q02, Q03 | — | — | P03 | — |
| `03_requisicao_vigente_paginacao` | Microtópico 3 — Integração React acompanha a requisição vigente; Microtópico 4 — Paginação, filtros e ordem dos resultados | Q04 | — | P02 | P03 | — |
| `04_cors_erros_integracao` | Microtópico 5 — CORS e erros são parte da integração | Q05 | — | — | P01, P03 | — |

**Classificação individual de questões:**
- Q01 — **Interpretação de fetch:** fetch recebe status 500 e resolve Response. Isso significa que a operação foi bem-sucedida? → `01_contrato_requisicao_resposta` (exclusiva).
- Q02 — **Segurança:** por que um bearer token não deve ser colocado como parâmetro da URL? → `02_autenticacao_credenciais` (exclusiva).
- Q03 — **Autorização:** qual diferença prática entre 401 e 403? → `02_autenticacao_credenciais` (exclusiva).
- Q04 — **Concorrência:** filtro “abertas” inicia primeira requisição; em seguida a pessoa escolhe “concluídas”, cuja resposta chega antes. O que fazer com a primeira resposta? → `03_requisicao_vigente_paginacao` (exclusiva).
- Q05 — **Diagnóstico:** a página funciona em desenvolvimento com proxy e falha no navegador ao chamar uma API em outra origem em produção. Desativar CORS no fetch resolve? → `04_cors_erros_integracao` (exclusiva).

**Classificação individual de práticas:**
- P01 — Construa um cliente de lista que modele erros → `01_contrato_requisicao_resposta`, `04_cors_erros_integracao` (compartilhada; solução existente, rubrica existente na atividade).
- P02 — Impeça que resposta antiga substitua a atual → `03_requisicao_vigente_paginacao` (exclusiva; solução existente, rubrica existente na atividade).
- P03 — Escolha autenticação, paginação e CORS para um fluxo → `02_autenticacao_credenciais`, `03_requisicao_vigente_paginacao`, `04_cors_erros_integracao` (compartilhada; solução existente, rubrica existente na atividade).

**Conexões/pré-requisitos registrados:** Revisita requisições e HTTP de 7.3, relaciona-se à autenticação de 18.1 e 20.1, exige o estado de 25.2 e prepara estados de interface em 27.2.

### 27.2 — Estados de interface

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_estado_operacao_comunicacao_acessivel` | Microtópico 1 — Modele o estado dos dados e da operação; Microtópico 5 — Torne mudanças perceptíveis e verificáveis | Q02 | — | — | P01, P03 | — |
| `02_vazio_resultados_falhas` | Microtópico 2 — Diferencie vazio, ausência de resultados e falha | Q01, Q03 | — | — | P01 | — |
| `03_retry_seguro` | Microtópico 3 — Faça novas tentativas com segurança | Q04 | — | — | P03 | — |
| `04_contexto_paginacao` | Microtópico 4 — Preserve contexto durante atualização e paginação | Q05 | — | P02 | — | — |

**Classificação individual de questões:**
- Q01 — Uma consulta terminou com HTTP 200 e `items: []`. A tela deve exibir erro? → `02_vazio_resultados_falhas` (exclusiva).
- Q02 — Por que separar estado dos dados e atividade de rede? → `01_estado_operacao_comunicacao_acessivel` (exclusiva).
- Q03 — Uma busca não encontrou resultados. Isso é igual ao primeiro acesso sem itens? → `02_vazio_resultados_falhas` (exclusiva).
- Q04 — É seguro repetir automaticamente uma requisição `POST` de pagamento após timeout? → `03_retry_seguro` (exclusiva).
- Q05 — Durante a mudança de página, a interface mantém temporariamente a lista anterior. O que deve fazer com metadados como `hasMore`? → `04_contexto_paginacao` (exclusiva).

**Classificação individual de práticas:**
- P01 — Construa a matriz de estados da listagem → `01_estado_operacao_comunicacao_acessivel`, `02_vazio_resultados_falhas` (compartilhada; sem solução/rubrica separada identificada).
- P02 — Implemente paginação com dados provisórios → `04_contexto_paginacao` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Defina retry e acessibilidade para estados de falha → `01_estado_operacao_comunicacao_acessivel`, `03_retry_seguro` (compartilhada; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Pré-requisito 27.1. Relaciona-se à experiência de formulários e validação em 7.3 e à estrutura de dados em 8.2.

### 27.3 — Contrato de dados

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_fronteira_contrato_validacao_runtime` | 1. Descrever a fronteira entre cliente e API; 2. Separar tipo estático de validação em runtime | Q01, Q04 | — | — | P01, P02 | — |
| `02_presenca_nulidade_variacoes` | 3. Modelar presença, nulidade e variações de resposta | Q02 | — | — | P01, P02 | — |
| `03_evolucao_compatibilidade` | 4. Evoluir contratos sem surpreender consumidores | Q03, Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — `const task = await response.json() as Task` comprova que `title` existe e é string? → `01_fronteira_contrato_validacao_runtime` (exclusiva).
- Q02 — Qual diferença entre `dueDate?: string` e `dueDate: string | null`? → `02_presenca_nulidade_variacoes` (exclusiva).
- Q03 — Uma API adiciona `archived: boolean` à resposta. Isso sempre quebra clientes antigos? → `03_evolucao_compatibilidade` (exclusiva).
- Q04 — Por que a UI precisa checar o status HTTP além de validar JSON? → `01_fronteira_contrato_validacao_runtime` (exclusiva).
- Q05 — O que um teste de contrato compartilhado ajuda a detectar? → `03_evolucao_compatibilidade` (exclusiva).

**Classificação individual de práticas:**
- P01 — Especificar contrato de uma listagem paginada → `01_fronteira_contrato_validacao_runtime`, `02_presenca_nulidade_variacoes` (compartilhada; sem solução/rubrica separada identificada).
- P02 — Validar JSON externo e adaptar para a UI → `01_fronteira_contrato_validacao_runtime`, `02_presenca_nulidade_variacoes` (compartilhada; sem solução/rubrica separada identificada).
- P03 — Revisar evolução e compatibilidade de contrato → `03_evolucao_compatibilidade` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Revisita tipos e modelagem de dados (8.2), integra com contratos de API (18.1) e comunicação de estado da interface (27.1); aplica-se aos clientes da Fase 6 e às rotas do projeto.

### 27.4 — Segurança no navegador

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_entrada_nao_confiavel_defesas_xss` | 1. Rastrear entrada não confiável até a renderização (XSS); 2. Escolher defesa conforme o contexto | Q02 | — | P01 | — | — |
| `02_csrf_cors_cookies` | 3. Distinguir XSS, CSRF, CORS e atributos de cookie | Q01, Q03, Q04 | — | P02 | — | — |
| `03_segredos_csp_dependencias` | 4. Manter segredos e dependências fora do bundle | Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — `HttpOnly` impede CSRF? → `02_csrf_cors_cookies` (exclusiva).
- Q02 — React escapa texto interpolado. Isso torna seguro qualquer conteúdo enviado à propriedade `dangerouslySetInnerHTML`? → `01_entrada_nao_confiavel_defesas_xss` (exclusiva).
- Q03 — Qual a diferença entre `HttpOnly` e `SameSite`? → `02_csrf_cors_cookies` (exclusiva).
- Q04 — CORS autentica o usuário e bloqueia toda requisição de outro site? → `02_csrf_cors_cookies` (exclusiva).
- Q05 — `npm audit` não encontrou vulnerabilidades. Pode-se concluir que todas as dependências são seguras? → `03_segredos_csp_dependencias` (exclusiva).

**Classificação individual de práticas:**
- P01 — Revisar renderização de comentários (XSS) → `01_entrada_nao_confiavel_defesas_xss` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Modelo de ameaça CSRF para uma sessão → `02_csrf_cors_cookies` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Revisar bundle, CSP e dependências → `03_segredos_csp_dependencias` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Complementa autenticação/autorização e segurança das Fases 4–5 (20.1 e 20.2); depende do modelo de estado e requisições do navegador (27.1) e se beneficia da validação de contratos (27.3).

### 28.1 — Ferramentas

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_criterio_de_escolha_vite_build` | Microtópico 1 — Identifique o problema antes da ferramenta; Microtópico 2 — Use Vite para desenvolvimento e build | Q01, Q04 | — | — | P02, P03 | — |
| `02_estado_local_vs_remoto` | Microtópico 3 — Separe estado de interface e estado remoto | Q02 | — | P01 | P02 | — |
| `03_fronteiras_store_cache` | Microtópico 4 — Combine com fronteiras claras | Q03, Q05 | — | — | P02, P03 | — |

**Classificação individual de questões:**
- Q01 — Vite invalida o cache de uma consulta à API quando um componente é atualizado? → `01_criterio_de_escolha_vite_build` (exclusiva).
- Q02 — Uma store global deve conter todo estado de formulário? → `02_estado_local_vs_remoto` (exclusiva).
- Q03 — Qual informação deve participar da chave de uma consulta paginada por filtro? → `03_fronteiras_store_cache` (exclusiva).
- Q04 — É seguro colocar `VITE_API_SECRET` no `.env`? → `01_criterio_de_escolha_vite_build` (exclusiva).
- Q05 — Qual risco aparece ao copiar uma resposta remota para Zustand e também mantê-la no cache do TanStack Query? → `03_fronteiras_store_cache` (exclusiva).

**Classificação individual de práticas:**
- P01 — Faça um mapa de responsabilidades → `02_estado_local_vs_remoto` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Integre uma lista remota e estado de interface → `01_criterio_de_escolha_vite_build`, `02_estado_local_vs_remoto`, `03_fronteiras_store_cache` (compartilhada; sem solução/rubrica separada identificada).
- P03 — Audite build e variáveis expostas → `01_criterio_de_escolha_vite_build`, `03_fronteiras_store_cache` (compartilhada; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Pré-requisito 27.2. Complementa 28.2, sobre gerência de dados, e 28.3, sobre organização do projeto.

### 28.2 — Gerência de dados

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_fonte_de_verdade` | Microtópico 1 — Classifique a origem e a fonte de verdade | Q01 | — | P01 | — | — |
| `02_identidade_de_consultas` | Microtópico 2 — Dê identidade estável às consultas | Q02 | — | — | P02 | — |
| `03_frescor_ciclo_de_cache` | Microtópico 3 — Entenda frescor e ciclo de vida do cache | Q03 | — | — | P02 | — |
| `04_mutacoes_conflitos_reconciliacao` | Microtópico 4 — Reconcilie mutações, falhas e identidade do usuário | Q04, Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — “Modal aberto” costuma ser dado remoto? → `01_fonte_de_verdade` (exclusiva).
- Q02 — A função de uma consulta usa `page` e `status` para buscar pedidos. O que deve aparecer na query key? → `02_identidade_de_consultas` (exclusiva).
- Q03 — `staleTime` determina por quanto tempo uma consulta inativa fica armazenada antes da coleta? → `03_frescor_ciclo_de_cache` (exclusiva).
- Q04 — A API devolve o registro atualizado completo após uma edição. Cite duas estratégias válidas para atualizar a interface. **Atualizar a entrada de cache com a resposta ou invalidar a consulta relacionada para buscar novamente.** → `04_mutacoes_conflitos_reconciliacao` (exclusiva).
- Q05 — Uma alteração otimista falhou enquanto outra atualização simultânea ocorreu. Por que restaurar cegamente um snapshot antigo pode ser perigoso? → `04_mutacoes_conflitos_reconciliacao` (exclusiva).

**Classificação individual de práticas:**
- P01 — Mapeie a fonte de verdade e os ciclos de vida → `01_fonte_de_verdade` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Construa chaves e política de frescor → `02_identidade_de_consultas`, `03_frescor_ciclo_de_cache` (compartilhada; sem solução/rubrica separada identificada).
- P03 — Implemente uma mutação com reconciliação → `04_mutacoes_conflitos_reconciliacao` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Pré-requisitos 26.1 e 27.1. Relaciona-se à experiência de interface em 27.2, às ferramentas de 28.1 e ao cache Redis em 15.1, sem confundir cache do cliente com cache de infraestrutura.

### 28.3 — Organização

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_consumidores_dono_elevacao` | Microtópico 1 — Decida a partir dos consumidores e do ciclo de vida; Microtópico 2 — Eleve estado só até o proprietário necessário | Q01, Q03, Q04 | — | P01 | P02 | — |
| `02_estado_derivado_sem_redundancia` | Microtópico 3 — Remova redundância e valores que podem ser derivados | Q02 | — | — | P02 | — |
| `03_persistencia_reset_identidade` | Microtópico 4 — Defina quando preservar, redefinir e revisar | Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — **Múltipla escolha.** Dois painéis irmãos devem garantir que apenas um fique aberto. Onde começar a manter `activePanel`? → `01_consumidores_dono_elevacao` (exclusiva).
- Q02 — **Cenário.** Uma aplicação guarda os itens do carrinho e também um total que é sempre calculável a partir deles. Qual é o problema e a correção? → `02_estado_derivado_sem_redundancia` (exclusiva).
- Q03 — **Verdadeiro ou falso, justifique.** “Se um valor é usado por componentes distantes, ele deve sempre ficar em uma store global.” **Falso.** Context, URL, composição de componentes ou store podem ser adequados; decida conforme origem, ciclo de vida e necessidade de compartilhamento. → `01_consumidores_dono_elevacao` (exclusiva).
- Q04 — **Escolha a estrutura.** Uma lista está no cache remoto e a pessoa seleciona um item por identificador. Deve-se guardar no estado local o objeto completo selecionado ou seu ID? → `01_consumidores_dono_elevacao` (exclusiva).
- Q05 — **Resposta curta.** Quando `key` em um componente de formulário ajuda e qual cuidado exige? → `03_persistencia_reset_identidade` (exclusiva).

**Classificação individual de práticas:**
- P01 — Faça uma auditoria de localização de estado → `01_consumidores_dono_elevacao` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Refatore estado duplicado e coordene componentes → `01_consumidores_dono_elevacao`, `02_estado_derivado_sem_redundancia` (compartilhada; sem solução/rubrica separada identificada).
- P03 — Defina limites de persistência e redefinição → `03_persistencia_reset_identidade` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Complementa 28.2, sobre gerência de dados, e organiza as escolhas de 26.2. Relaciona-se às transições de interface em 27.2.

### 29.1 — Base de testes

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_consultas_semanticas` | Microtópico 1 — Teste o contrato que a pessoa usa | Q01 | — | — | P01 | — |
| `02_runner_ambiente` | Microtópico 2 — Configure runner e ambiente coerentes | Q05 | — | — | P03 | — |
| `03_interacao_assincrona` | Microtópico 3 — Consulte, interaja e aguarde corretamente | Q02, Q04 | — | P02 | P01 | — |
| `04_isolamento_assertions` | Microtópico 4 — Isole dependências sem esconder defeitos | Q03 | — | — | P01, P03 | — |

**Classificação individual de questões:**
- Q01 — **Múltipla escolha.** Qual busca é mais apropriada para encontrar o botão de envio? → `01_consultas_semanticas` (exclusiva).
- Q02 — **Associe a necessidade à consulta.** Verificar que um aviso está ausente; localizar um campo que já deve estar renderizado; esperar o resultado de uma busca assíncrona. **Resposta:** `queryBy...`; `getBy...`; `findBy...`, respectivamente. → `03_interacao_assincrona` (exclusiva).
- Q03 — **Verdadeiro ou falso, justifique.** “Se o teste passa e a cobertura é 100%, o comportamento está correto.” **Falso.** Código executado não garante assertions capazes de detectar resultados incorretos. → `04_isolamento_assertions` (exclusiva).
- Q04 — **Cenário.** Um teste coloca `await user.click(...)` dentro de uma callback de `waitFor`. Qual é o risco e como melhorar? → `03_interacao_assincrona` (exclusiva).
- Q05 — **Resposta curta.** Por que usar `jsdom` não comprova que o layout funciona em navegadores reais? → `02_runner_ambiente` (exclusiva).

**Classificação individual de práticas:**
- P01 — Teste o contrato de um formulário → `01_consultas_semanticas`, `03_interacao_assincrona`, `04_isolamento_assertions` (compartilhada; sem solução/rubrica separada identificada).
- P02 — Cubra estados assíncronos de uma lista → `03_interacao_assincrona` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Revise isolamento, mocks e valor das assertions → `02_runner_ambiente`, `04_isolamento_assertions` (compartilhada; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Baseia-se em 25.2 e conecta-se aos tipos de teste em 24.1. Relaciona-se aos estados de interface em 27.2 e às ferramentas de frontend em 28.1.

### 29.2 — Integração e borda

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_fronteiras_e_mocks_de_rede` | Microtópico 1 — Escolha qual fronteira cada teste precisa atravessar; Microtópico 2 — Simule a rede na fronteira com MSW | Q01, Q05 | Q04 | P01 | — | — |
| `02_fluxos_e2e_playwright` | Microtópico 3 — Percorra um caminho crítico no navegador com Playwright | Q02 | Q04 | P02 | — | — |
| `03_flakiness_e_evidencia` | Microtópico 4 — Reduza flakiness e registre o limite da evidência | Q03 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — **Múltipla escolha.** Um teste renderiza a lista, faz o cliente executar seu `fetch` e MSW responde ao endpoint. Qual afirmação é correta? → `01_fronteiras_e_mocks_de_rede` (exclusiva).
- Q02 — **Classifique a evidência.** Um cenário Playwright intercepta `/api/orders` e mostra a mensagem de sucesso. Ele valida a interface no navegador, a resposta simulada, o endpoint real, ou todos? → `02_fluxos_e2e_playwright` (exclusiva).
- Q03 — **Verdadeiro ou falso, justifique.** “Esperar dois segundos em todo teste elimina flakiness.” **Falso.** Pausa fixa torna o teste lento e ainda pode não ser suficiente; aguarde a condição observável com as ferramentas de retry/assertion do runner. → `03_flakiness_e_evidencia` (exclusiva).
- Q04 — **Resposta curta.** Que cuidados são necessários se o teste Playwright usa um backend de teste real para criar pedidos? → `01_fronteiras_e_mocks_de_rede`, `02_fluxos_e2e_playwright` (compartilhada).
- Q05 — **Diagnóstico.** Um handler MSW simula `200` com um objeto incompatível com o contrato, e a tela aceita esse valor. Qual lacuna existe? → `01_fronteiras_e_mocks_de_rede` (exclusiva).

**Classificação individual de práticas:**
- P01 — Teste o contrato HTTP do cliente com MSW → `01_fronteiras_e_mocks_de_rede` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Automatize um fluxo crítico com Playwright → `02_fluxos_e2e_playwright` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Investigue e estabilize um teste intermitente → `03_flakiness_e_evidencia` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Requer 27.1 e 29.1; relaciona-se à integração de 24.2, aos estados de interface em 27.2 e à automação em 32.1.

### 30.1 — Otimização

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_medicao_baseline_memoizacao` | Microtópico 1 — Meça antes de escolher a técnica; Microtópico 2 — Use memoização só para trabalho repetido que importa | Q01, Q02, Q05 | Q03 | P01, P02 | — | — |
| `02_carregamento_e_virtualizacao` | Microtópico 3 — Divida código e carregue partes quando forem necessárias; Microtópico 4 — Virtualize coleções realmente grandes com cuidado | Q04 | Q03 | P03 | — | — |

**Classificação individual de questões:**
- Q01 — **Escolha a intervenção.** Uma interação refaz um filtro custoso em milhares de registros mesmo quando os dados e o filtro não mudaram. Que técnica pode ajudar, após confirmar o custo? → `01_medicao_baseline_memoizacao` (exclusiva).
- Q02 — **Verdadeiro ou falso, justifique.** “`useMemo` é necessário para manter o resultado correto entre renders.” **Falso.** É uma otimização; o cálculo precisa continuar correto mesmo se for refeito. → `01_medicao_baseline_memoizacao` (exclusiva).
- Q03 — **Associe a técnica ao efeito direto.** `lazy`/`Suspense`; virtualização; `useMemo`. **Resposta:** adiar carregamento de código; limitar elementos montados perto da janela visível; reutilizar um valor calculado enquanto as dependências não mudam. → `01_medicao_baseline_memoizacao`, `02_carregamento_e_virtualizacao` (compartilhada).
- Q04 — **Cenário.** Uma tela tem 80 mil registros vindos da API, mas o perfil mostra que o endpoint demora a responder. Virtualização resolve o gargalo principal? → `02_carregamento_e_virtualizacao` (exclusiva).
- Q05 — **Resposta curta.** Por que medir uma mudança em uma única execução de desenvolvimento pode levar a uma conclusão errada? → `01_medicao_baseline_memoizacao` (exclusiva).

**Classificação individual de práticas:**
- P01 — Faça um diagnóstico com baseline → `01_medicao_baseline_memoizacao` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Otimize uma renderização ou um cálculo → `01_medicao_baseline_memoizacao` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Escolha entre divisão de código e virtualização → `02_carregamento_e_virtualizacao` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Pré-requisito 26.1. Relaciona-se a desempenho em 7.4 e 12.1, aos estados de interface em 27.2 e à base de testes em 29.1.

### 30.2 — Maturidade

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_hipotese_de_desempenho` | Microtópico 1 — Transforme uma queixa em hipótese testável | Q01 | — | — | P01 | — |
| `02_variacao_medicoes` | Microtópico 2 — Interprete medições com contexto e variação | Q02 | — | — | P01 | — |
| `03_tradeoffs_regressoes` | Microtópico 3 — Avalie benefícios junto aos custos e às regressões | Q03, Q04 | — | P02 | — | — |
| `04_registro_decisao` | Microtópico 4 — Registre a decisão e torne-a revisável | Q05 | — | P03 | — | — |

**Classificação individual de questões:**
- Q01 — **Múltipla escolha.** Um perfil não mostra renderizações custosas e a interação está responsiva no cenário observado. Qual decisão tem melhor suporte? → `01_hipotese_de_desempenho` (exclusiva).
- Q02 — **Interpretação de dados.** Uma otimização reduziu o tempo de uma execução em 4 ms, mas execuções repetidas variam entre 15 e 25 ms. O que se pode concluir? → `02_variacao_medicoes` (exclusiva).
- Q03 — **Verdadeiro ou falso, justifique.** “Uma melhoria em laboratório prova que todos os usuários sentirão a mesma diferença.” **Falso.** Dados de laboratório controlam condições; experiência real varia por dispositivo, rede, dados e tarefa. → `03_tradeoffs_regressoes` (exclusiva).
- Q04 — **Cenário.** Code splitting reduz o JavaScript da primeira página, mas o recurso principal agora demora para abrir e o fallback não anuncia a espera. A otimização está concluída? → `03_tradeoffs_regressoes` (exclusiva).
- Q05 — **Resposta curta.** O que precisa constar em um registro para que outra pessoa consiga rever uma decisão de não otimizar? → `04_registro_decisao` (exclusiva).

**Classificação individual de práticas:**
- P01 — Separe evidência de percepção → `01_hipotese_de_desempenho`, `02_variacao_medicoes` (compartilhada; sem solução/rubrica separada identificada).
- P02 — Experimente uma otimização e decida se fica → `03_tradeoffs_regressoes` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Escreva um registro de decisão revisável → `04_registro_decisao` (exclusiva; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Complementa 30.1 e os critérios de performance da Fase 4. Relaciona-se à qualidade e aos testes em 29.1 e 29.2.

### 31.1 — Next.js

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_estrutura_rotas_app_router` | Microtópico 1 — Leia a estrutura de rotas do App Router | — | — | P01 | — | — |
| `02_fronteira_e_renderizacao` | Microtópico 2 — Desenhe fronteiras pequenas entre servidor e cliente; Microtópico 3 — Escolha quando e onde o conteúdo é produzido | Q02, Q03, Q04 | Q05 | P02 | P03 | — |
| `03_route_handlers_endpoints` | Microtópico 4 — Trate Route Handlers como endpoints públicos | Q01 | Q05 | — | P03 | — |

**Classificação individual de questões:**
- Q01 — **Múltipla escolha.** Onde fica um endpoint no App Router? → `03_route_handlers_endpoints` (exclusiva).
- Q02 — **Verdadeiro ou falso, justifique.** “Um Server Component é privado porque não roda no navegador.” **Falso.** A resposta renderizada ou os dados que ele retorna ainda podem ser públicos; autorização precisa ser feita no servidor para cada recurso. → `02_fronteira_e_renderizacao` (exclusiva).
- Q03 — **Cenário.** Um botão requer clique e estado local, enquanto o restante da página lê dados com credencial privada. Como organizar? → `02_fronteira_e_renderizacao` (exclusiva).
- Q04 — **Associe o contexto à decisão.** Página de marketing com conteúdo estável; painel personalizado por sessão; abrir menu lateral. **Resposta:** avaliar prerenderização; usar contexto de requisição no servidor e proteger os dados; interação cliente local. → `02_fronteira_e_renderizacao` (exclusiva).
- Q05 — **Diagnóstico.** Uma rota `GET` funciona em desenvolvimento, mas em produção entrega dados personalizados de uma conta a outra. Que áreas precisam ser revisadas? → `02_fronteira_e_renderizacao`, `03_route_handlers_endpoints` (compartilhada).

**Classificação individual de práticas:**
- P01 — Modele rotas, páginas e layouts → `01_estrutura_rotas_app_router` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Separe servidor e interação cliente → `02_fronteira_e_renderizacao` (exclusiva; sem solução/rubrica separada identificada).
- P03 — Compare Route Handler e estratégia de renderização → `02_fronteira_e_renderizacao`, `03_route_handlers_endpoints` (compartilhada; sem solução/rubrica separada identificada).

**Conexões/pré-requisitos registrados:** Relaciona-se a 25.1 e à organização em 26.2; a comunicação com API em 27.1 é pré-requisito conceitual. Complementa as ferramentas de 28.1 e os estados de interface em 27.2.

### 31.2 — React Native

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_modelo_react_renderizador_nativo` | Microtópico 1 — Reutilize o modelo React, não o renderizador HTML | — | — | — | P01 | F01 |
| `02_reuso_adaptacao_plataforma_distribuicao` | Microtópico 2 — Compartilhe lógica e adapte o que depende da plataforma; Microtópico 3 — Entenda o papel do framework e da distribuição | — | — | P02 | P01 | F02, F03 |

**Classificação individual de questões:**

**Classificação individual de práticas:**
- P01 — Traduza um componente web para a linguagem nativa → `01_modelo_react_renderizador_nativo`, `02_reuso_adaptacao_plataforma_distribuicao` (compartilhada; sem solução/rubrica separada identificada).
- P02 — Faça um mapa de compartilhamento e diferenças → `02_reuso_adaptacao_plataforma_distribuicao` (exclusiva; sem solução/rubrica separada identificada).

**Flashcards:**
- F01 — - **React Native usa `<div>`?** Não. Usa componentes como `View`, `Text` e `Pressable`, que são mapeados para elementos nativos. → `01_modelo_react_renderizador_nativo`.
- F02 — - **Hooks e validação de domínio podem ser reaproveitados?** Sim, se a lógica não depender de DOM ou de APIs exclusivas do navegador. → `02_reuso_adaptacao_plataforma_distribuicao`.
- F03 — - **Uma tela React web funciona automaticamente em iOS e Android?** Não. Componentes, estilos, acessibilidade e APIs precisam ser adaptados e verificados nas plataformas alvo. → `02_reuso_adaptacao_plataforma_distribuicao`.

**Conexões/pré-requisitos registrados:** Relaciona-se aos fundamentos de React em 25.1, ao estado em 25.2 e à separação entre estado local e remoto em 28.2.

### 31.3 — Vue.js e Angular

| Assunto [PROPOSTA] | Microtópicos originais | Q exclusivos | Q compartilhados | P exclusivas | P compartilhadas | Flashcards |
|---|---|---|---|---|---|---|
| `01_modelos_componentes_reatividade` | Microtópico 1 — Compare como os frameworks descrevem a interface | — | — | P01 | — | F01, F02 |
| `02_versoes_padroes_legado` | Microtópico 2 — Reconheça versões, padrões atuais e legado | — | — | P02 | — | F03 |

**Classificação individual de questões:**

**Classificação individual de práticas:**
- P01 — Compare um pequeno componente → `01_modelos_componentes_reatividade` (exclusiva; sem solução/rubrica separada identificada).
- P02 — Reconheça padrões em código e versões → `02_versoes_padroes_legado` (exclusiva; sem solução/rubrica separada identificada).

**Flashcards:**
- F01 — - **Vue template é JSX do React?** Não. Vue usa sua própria sintaxe de template, embora ambos descrevam uma interface declarativa. → `01_modelos_componentes_reatividade`.
- F02 — - **Como Angular compartilha serviços entre partes da aplicação?** Por injeção de dependências, que fornece serviços ou valores aos componentes e outras classes. → `01_modelos_componentes_reatividade`.
- F03 — - **Vue 2 é o padrão indicado para iniciar um projeto novo?** Não. Vue 2 chegou ao fim de vida; use Vue 3 para código novo e reconheça Vue 2 ao manter legado. → `02_versoes_padroes_legado`.

**Conexões/pré-requisitos registrados:** Comparação parte dos fundamentos de React em 25.1 e 25.2. Relaciona-se à organização de componentes em 28.3.

### 31.4 — Projeto incremental da fase

- **Projeto:** preserva os blocos de contexto/escopo, quatro marcos, quatro aceites, rubrica original 0–4, checklist final, critério, conexões e referências. Não há quiz convencional.
- **Marcos:** Marco 1 — Delimite uma fatia vertical e conecte a API; Marco 2 — Complete estados e acessibilidade do fluxo; Marco 3 — Cubra comportamento e fronteiras com testes; Marco 4 — Meça, revise e entregue a fatia
- **Dependências explícitas:** ver seção Conexões da unidade; 31.4 continua 3.5 e consome API da Fase 5; 31.5 é especializado Trilho B e distinto de 31.4.

### 31.5 — Projeto de fase (Trilho B)

- **Projeto:** preserva os blocos de contexto/escopo, quatro marcos, quatro aceites, rubrica original 0–4, checklist final, critério, conexões e referências. Não há quiz convencional.
- **Marcos:** Marco 1 — Escolha o tipo e feche o contrato da fatia; Marco 2 — Implemente a fatia vertical e a regra do tipo; Marco 3 — Teste a jornada e tente quebrar a regra; Marco 4 — Revise, registre a cobertura e entregue
- **Dependências explícitas:** ver seção Conexões da unidade; 31.4 continua 3.5 e consome API da Fase 5; 31.5 é especializado Trilho B e distinto de 31.4.

## Gabaritos, soluções, rubricas e checklists

- As 80 respostas dos quizzes estão inline nos itens originais e serão separadas em 80 arquivos answer_key; cada uma aponta para um Q correspondente.
- Existem 15 soluções de referência e 15 rubricas descritivas junto às práticas de 25.1–27.1. A escala não é numérica nessas rubricas.
- 27.3 e 27.4 têm, cada uma, uma rubrica comum 0–4 por atividade, com quatro dimensões de 0–1, aplicável às três práticas da unidade.
- As demais práticas convencionais não têm solução/rubrica separada identificada nas fontes. Critérios inline das práticas permanecem no bloco da própria atividade.
- 31.4 tem quatro aceites, rubrica comum original 0–4 e checklist final de oito itens; 31.5 tem quatro aceites, rubrica comum original 0–4 e checklist final de nove itens.
- Nenhum gabarito ou critério ausente será criado.

## Projetos da unidade 31

- **31.4 — Projeto incremental da fase:** quatro marcos literais; critérios de aceite por marco; rubrica comum original 0–4; checklist final de oito itens. Conexão explícita: continua o projeto iniciado em 3.5 e reutiliza a API da Fase 5; os marcos correspondem a fatia/API, estados/acessibilidade, testes/fronteiras e medição/entrega.
- **31.5 — Projeto de fase (Trilho B):** quatro marcos literais; critérios de aceite por marco; rubrica comum original 0–4; checklist final de nove itens. Regra explícita: selecionar T1/T2/T4/T5 conforme guia e cobertura; não há quiz genérico. O projeto é especializado e não deve ser mesclado com a base comum 31.4.
- Os oito marcos são avaliados por evidências do próprio enunciado. A escala 0–4 fica intacta; nenhum novo critério ou rubrica é criado.

## Relações entre fases e fronteiras canônicas

- **25.x ↔ Fase 3 (6.x/7.x):** Fase 3 permanece fonte de JavaScript/DOM; Fase 6 aplica React e estado declarativo.
- **27.1 ↔ 18.1/20.1/20.x:** API e autenticação no servidor permanecem canônicas na Fase 5; Fase 6 trata consumo cliente, erros, sessão visível e CORS do navegador.
- **27.3 ↔ 18.1/8.2:** contrato é definido/documentado no backend; validação em runtime e adaptação de JSON ficam na fronteira cliente.
- **27.4 ↔ 20.x:** segurança do servidor é canônica na Fase 5; ameaças de navegador, XSS/CSRF/CORS e exposição no bundle ficam aqui.
- **28.2 ↔ 15.1:** Redis/cache de servidor pertence à Fase 4; query cache e ciclo de vida remoto do frontend pertencem à 28.2.
- **29.x ↔ 24.x/32.1:** 24.x é canônica para testes de serviço/backend; 29.x para componentes e browser; 32.1 para CI/automação.
- **30.x ↔ 7.4/12.1:** algoritmos e banco/performance de backend ficam em suas fases canônicas; 30.x cobre medição, renderização, bundle e interface.
- **31.4/31.5 ↔ 3.5/24.x/29.x/30.x:** projetos usam conteúdos anteriores como ferramentas e critérios locais; não duplicar suas explicações conceituais nos projetos.

## Propostas pedagógicas pendentes

- [PROPOSTA] Os agrupamentos de 25.1, 29.2, 30.1 e 31.1 reúnem microtópicos coesos avaliados em conjunto pelos enunciados/práticas. Confirmar essa granularidade antes de qualquer geração.
- [PROPOSTA] 31.2 e 31.3 permanecem repertório curto: flashcards e práticas comparativas existentes são a avaliação; não adicionar quiz.
- [PROPOSTA] Não uniformizar decisões de implementação para React Native, Vue ou Angular; fontes/referências têm atualização temporal e a unidade 31.3 já identifica Vue 2 como legado.

## Estrutura de arquivos proposta

A árvore segue `Fase_6/<ID>_<slug_original>/`; README como índice com metadados; cinco arquivos comuns separados; pastas de assunto planas; itens compartilhados em `90_integracao/`; arquivos planos de marcos. Não há README por assunto. A execução futura mantém originais e JSON intactos.

### 25.1 — 25.1_Fundamentos
- `25.1_Fundamentos/README.md` — topic_index (IDX; `f6-25-1-readme-md`).
- `25.1_Fundamentos/00_objetivo.md` — objetivo (OBJ; `f6-25-1-00-objetivo-md`).
- `25.1_Fundamentos/01_resumo.md` — resumo (RES; `f6-25-1-01-resumo-md`).
- `25.1_Fundamentos/02_criterio_de_conclusao.md` — criterio (CRI; `f6-25-1-02-criterio-de-conclusao-md`).
- `25.1_Fundamentos/03_conexoes.md` — conexoes (CON; `f6-25-1-03-conexoes-md`).
- `25.1_Fundamentos/04_referencias.md` — referencias (REF; `f6-25-1-04-referencias-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/01_teoria.md` — theory (T01; `f6-25-1-01-componentes-modelo-declarativo-props-01-teoria-md`).
- `25.1_Fundamentos/02_jsx_transformacao/01_teoria.md` — theory (T02; `f6-25-1-02-jsx-transformacao-01-teoria-md`).
- `25.1_Fundamentos/02_jsx_transformacao/Q01_quiz.md` — quiz (Q01; `f6-25-1-02-jsx-transformacao-q01-quiz-md`).
- `25.1_Fundamentos/02_jsx_transformacao/K01_gabarito_quiz.md` — answer_key (K01; `f6-25-1-02-jsx-transformacao-k01-gabarito-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/Q02_quiz.md` — quiz (Q02; `f6-25-1-01-componentes-modelo-declarativo-props-q02-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/K02_gabarito_quiz.md` — answer_key (K02; `f6-25-1-01-componentes-modelo-declarativo-props-k02-gabarito-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/Q03_quiz.md` — quiz (Q03; `f6-25-1-01-componentes-modelo-declarativo-props-q03-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/K03_gabarito_quiz.md` — answer_key (K03; `f6-25-1-01-componentes-modelo-declarativo-props-k03-gabarito-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/Q04_quiz.md` — quiz (Q04; `f6-25-1-01-componentes-modelo-declarativo-props-q04-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/K04_gabarito_quiz.md` — answer_key (K04; `f6-25-1-01-componentes-modelo-declarativo-props-k04-gabarito-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/Q05_quiz.md` — quiz (Q05; `f6-25-1-01-componentes-modelo-declarativo-props-q05-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/K05_gabarito_quiz.md` — answer_key (K05; `f6-25-1-01-componentes-modelo-declarativo-props-k05-gabarito-quiz-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/P01_pratica.md` — practice (P01; `f6-25-1-01-componentes-modelo-declarativo-props-p01-pratica-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/KP01_solucao.md` — answer_key_pratica (KP01; `f6-25-1-01-componentes-modelo-declarativo-props-kp01-solucao-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/R01_rubrica.md` — rubric (R01; `f6-25-1-01-componentes-modelo-declarativo-props-r01-rubrica-md`).
- `25.1_Fundamentos/90_integracao/P02_pratica.md` — practice (P02; `f6-25-1-90-integracao-p02-pratica-md`).
- `25.1_Fundamentos/90_integracao/KP02_solucao.md` — answer_key_pratica (KP02; `f6-25-1-90-integracao-kp02-solucao-md`).
- `25.1_Fundamentos/90_integracao/R02_rubrica.md` — rubric (R02; `f6-25-1-90-integracao-r02-rubrica-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/P03_pratica.md` — practice (P03; `f6-25-1-01-componentes-modelo-declarativo-props-p03-pratica-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/KP03_solucao.md` — answer_key_pratica (KP03; `f6-25-1-01-componentes-modelo-declarativo-props-kp03-solucao-md`).
- `25.1_Fundamentos/01_componentes_modelo_declarativo_props/R03_rubrica.md` — rubric (R03; `f6-25-1-01-componentes-modelo-declarativo-props-r03-rubrica-md`).

### 25.2 — 25.2_Estado_e_interacao
- `25.2_Estado_e_interacao/README.md` — topic_index (IDX; `f6-25-2-readme-md`).
- `25.2_Estado_e_interacao/00_objetivo.md` — objetivo (OBJ; `f6-25-2-00-objetivo-md`).
- `25.2_Estado_e_interacao/01_resumo.md` — resumo (RES; `f6-25-2-01-resumo-md`).
- `25.2_Estado_e_interacao/02_criterio_de_conclusao.md` — criterio (CRI; `f6-25-2-02-criterio-de-conclusao-md`).
- `25.2_Estado_e_interacao/03_conexoes.md` — conexoes (CON; `f6-25-2-03-conexoes-md`).
- `25.2_Estado_e_interacao/04_referencias.md` — referencias (REF; `f6-25-2-04-referencias-md`).
- `25.2_Estado_e_interacao/01_estado_snapshot_formulario_controlado/01_teoria.md` — theory (T01; `f6-25-2-01-estado-snapshot-formulario-controlado-01-teoria-md`).
- `25.2_Estado_e_interacao/02_eventos_atualizadores/01_teoria.md` — theory (T02; `f6-25-2-02-eventos-atualizadores-01-teoria-md`).
- `25.2_Estado_e_interacao/03_colecoes_imutaveis_identidade/01_teoria.md` — theory (T03; `f6-25-2-03-colecoes-imutaveis-identidade-01-teoria-md`).
- `25.2_Estado_e_interacao/04_valores_derivados_condicoes_filtros/01_teoria.md` — theory (T04; `f6-25-2-04-valores-derivados-condicoes-filtros-01-teoria-md`).
- `25.2_Estado_e_interacao/01_estado_snapshot_formulario_controlado/Q01_quiz.md` — quiz (Q01; `f6-25-2-01-estado-snapshot-formulario-controlado-q01-quiz-md`).
- `25.2_Estado_e_interacao/01_estado_snapshot_formulario_controlado/K01_gabarito_quiz.md` — answer_key (K01; `f6-25-2-01-estado-snapshot-formulario-controlado-k01-gabarito-quiz-md`).
- `25.2_Estado_e_interacao/02_eventos_atualizadores/Q02_quiz.md` — quiz (Q02; `f6-25-2-02-eventos-atualizadores-q02-quiz-md`).
- `25.2_Estado_e_interacao/02_eventos_atualizadores/K02_gabarito_quiz.md` — answer_key (K02; `f6-25-2-02-eventos-atualizadores-k02-gabarito-quiz-md`).
- `25.2_Estado_e_interacao/03_colecoes_imutaveis_identidade/Q03_quiz.md` — quiz (Q03; `f6-25-2-03-colecoes-imutaveis-identidade-q03-quiz-md`).
- `25.2_Estado_e_interacao/03_colecoes_imutaveis_identidade/K03_gabarito_quiz.md` — answer_key (K03; `f6-25-2-03-colecoes-imutaveis-identidade-k03-gabarito-quiz-md`).
- `25.2_Estado_e_interacao/03_colecoes_imutaveis_identidade/Q04_quiz.md` — quiz (Q04; `f6-25-2-03-colecoes-imutaveis-identidade-q04-quiz-md`).
- `25.2_Estado_e_interacao/03_colecoes_imutaveis_identidade/K04_gabarito_quiz.md` — answer_key (K04; `f6-25-2-03-colecoes-imutaveis-identidade-k04-gabarito-quiz-md`).
- `25.2_Estado_e_interacao/04_valores_derivados_condicoes_filtros/Q05_quiz.md` — quiz (Q05; `f6-25-2-04-valores-derivados-condicoes-filtros-q05-quiz-md`).
- `25.2_Estado_e_interacao/04_valores_derivados_condicoes_filtros/K05_gabarito_quiz.md` — answer_key (K05; `f6-25-2-04-valores-derivados-condicoes-filtros-k05-gabarito-quiz-md`).
- `25.2_Estado_e_interacao/90_integracao/P01_pratica.md` — practice (P01; `f6-25-2-90-integracao-p01-pratica-md`).
- `25.2_Estado_e_interacao/90_integracao/KP01_solucao.md` — answer_key_pratica (KP01; `f6-25-2-90-integracao-kp01-solucao-md`).
- `25.2_Estado_e_interacao/90_integracao/R01_rubrica.md` — rubric (R01; `f6-25-2-90-integracao-r01-rubrica-md`).
- `25.2_Estado_e_interacao/90_integracao/P02_pratica.md` — practice (P02; `f6-25-2-90-integracao-p02-pratica-md`).
- `25.2_Estado_e_interacao/90_integracao/KP02_solucao.md` — answer_key_pratica (KP02; `f6-25-2-90-integracao-kp02-solucao-md`).
- `25.2_Estado_e_interacao/90_integracao/R02_rubrica.md` — rubric (R02; `f6-25-2-90-integracao-r02-rubrica-md`).
- `25.2_Estado_e_interacao/90_integracao/P03_pratica.md` — practice (P03; `f6-25-2-90-integracao-p03-pratica-md`).
- `25.2_Estado_e_interacao/90_integracao/KP03_solucao.md` — answer_key_pratica (KP03; `f6-25-2-90-integracao-kp03-solucao-md`).
- `25.2_Estado_e_interacao/90_integracao/R03_rubrica.md` — rubric (R03; `f6-25-2-90-integracao-r03-rubrica-md`).

### 26.1 — 26.1_Hooks
- `26.1_Hooks/README.md` — topic_index (IDX; `f6-26-1-readme-md`).
- `26.1_Hooks/00_objetivo.md` — objetivo (OBJ; `f6-26-1-00-objetivo-md`).
- `26.1_Hooks/01_resumo.md` — resumo (RES; `f6-26-1-01-resumo-md`).
- `26.1_Hooks/02_criterio_de_conclusao.md` — criterio (CRI; `f6-26-1-02-criterio-de-conclusao-md`).
- `26.1_Hooks/03_conexoes.md` — conexoes (CON; `f6-26-1-03-conexoes-md`).
- `26.1_Hooks/04_referencias.md` — referencias (REF; `f6-26-1-04-referencias-md`).
- `26.1_Hooks/01_regras_de_chamada/01_teoria.md` — theory (T01; `f6-26-1-01-regras-de-chamada-01-teoria-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/01_teoria.md` — theory (T02; `f6-26-1-02-effects-sincronizacao-limpeza-01-teoria-md`).
- `26.1_Hooks/03_refs_valores_imperativos/01_teoria.md` — theory (T03; `f6-26-1-03-refs-valores-imperativos-01-teoria-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/01_teoria.md` — theory (T04; `f6-26-1-04-memoizacao-decisao-por-evidencia-01-teoria-md`).
- `26.1_Hooks/01_regras_de_chamada/Q01_quiz.md` — quiz (Q01; `f6-26-1-01-regras-de-chamada-q01-quiz-md`).
- `26.1_Hooks/01_regras_de_chamada/K01_gabarito_quiz.md` — answer_key (K01; `f6-26-1-01-regras-de-chamada-k01-gabarito-quiz-md`).
- `26.1_Hooks/03_refs_valores_imperativos/Q02_quiz.md` — quiz (Q02; `f6-26-1-03-refs-valores-imperativos-q02-quiz-md`).
- `26.1_Hooks/03_refs_valores_imperativos/K02_gabarito_quiz.md` — answer_key (K02; `f6-26-1-03-refs-valores-imperativos-k02-gabarito-quiz-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/Q03_quiz.md` — quiz (Q03; `f6-26-1-02-effects-sincronizacao-limpeza-q03-quiz-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/K03_gabarito_quiz.md` — answer_key (K03; `f6-26-1-02-effects-sincronizacao-limpeza-k03-gabarito-quiz-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/Q04_quiz.md` — quiz (Q04; `f6-26-1-04-memoizacao-decisao-por-evidencia-q04-quiz-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/K04_gabarito_quiz.md` — answer_key (K04; `f6-26-1-04-memoizacao-decisao-por-evidencia-k04-gabarito-quiz-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/Q05_quiz.md` — quiz (Q05; `f6-26-1-04-memoizacao-decisao-por-evidencia-q05-quiz-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/K05_gabarito_quiz.md` — answer_key (K05; `f6-26-1-04-memoizacao-decisao-por-evidencia-k05-gabarito-quiz-md`).
- `26.1_Hooks/90_integracao/P01_pratica.md` — practice (P01; `f6-26-1-90-integracao-p01-pratica-md`).
- `26.1_Hooks/90_integracao/KP01_solucao.md` — answer_key_pratica (KP01; `f6-26-1-90-integracao-kp01-solucao-md`).
- `26.1_Hooks/90_integracao/R01_rubrica.md` — rubric (R01; `f6-26-1-90-integracao-r01-rubrica-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/P02_pratica.md` — practice (P02; `f6-26-1-02-effects-sincronizacao-limpeza-p02-pratica-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/KP02_solucao.md` — answer_key_pratica (KP02; `f6-26-1-02-effects-sincronizacao-limpeza-kp02-solucao-md`).
- `26.1_Hooks/02_effects_sincronizacao_limpeza/R02_rubrica.md` — rubric (R02; `f6-26-1-02-effects-sincronizacao-limpeza-r02-rubrica-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/P03_pratica.md` — practice (P03; `f6-26-1-04-memoizacao-decisao-por-evidencia-p03-pratica-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/KP03_solucao.md` — answer_key_pratica (KP03; `f6-26-1-04-memoizacao-decisao-por-evidencia-kp03-solucao-md`).
- `26.1_Hooks/04_memoizacao_decisao_por_evidencia/R03_rubrica.md` — rubric (R03; `f6-26-1-04-memoizacao-decisao-por-evidencia-r03-rubrica-md`).

### 26.2 — 26.2_Organizacao
- `26.2_Organizacao/README.md` — topic_index (IDX; `f6-26-2-readme-md`).
- `26.2_Organizacao/00_objetivo.md` — objetivo (OBJ; `f6-26-2-00-objetivo-md`).
- `26.2_Organizacao/01_resumo.md` — resumo (RES; `f6-26-2-01-resumo-md`).
- `26.2_Organizacao/02_criterio_de_conclusao.md` — criterio (CRI; `f6-26-2-02-criterio-de-conclusao-md`).
- `26.2_Organizacao/03_conexoes.md` — conexoes (CON; `f6-26-2-03-conexoes-md`).
- `26.2_Organizacao/04_referencias.md` — referencias (REF; `f6-26-2-04-referencias-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/01_teoria.md` — theory (T01; `f6-26-2-01-responsabilidades-ownership-composicao-01-teoria-md`).
- `26.2_Organizacao/02_custom_hooks/01_teoria.md` — theory (T02; `f6-26-2-02-custom-hooks-01-teoria-md`).
- `26.2_Organizacao/03_context_compartilhamento/01_teoria.md` — theory (T03; `f6-26-2-03-context-compartilhamento-01-teoria-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/Q01_quiz.md` — quiz (Q01; `f6-26-2-01-responsabilidades-ownership-composicao-q01-quiz-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/K01_gabarito_quiz.md` — answer_key (K01; `f6-26-2-01-responsabilidades-ownership-composicao-k01-gabarito-quiz-md`).
- `26.2_Organizacao/02_custom_hooks/Q02_quiz.md` — quiz (Q02; `f6-26-2-02-custom-hooks-q02-quiz-md`).
- `26.2_Organizacao/02_custom_hooks/K02_gabarito_quiz.md` — answer_key (K02; `f6-26-2-02-custom-hooks-k02-gabarito-quiz-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/Q03_quiz.md` — quiz (Q03; `f6-26-2-01-responsabilidades-ownership-composicao-q03-quiz-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/K03_gabarito_quiz.md` — answer_key (K03; `f6-26-2-01-responsabilidades-ownership-composicao-k03-gabarito-quiz-md`).
- `26.2_Organizacao/03_context_compartilhamento/Q04_quiz.md` — quiz (Q04; `f6-26-2-03-context-compartilhamento-q04-quiz-md`).
- `26.2_Organizacao/03_context_compartilhamento/K04_gabarito_quiz.md` — answer_key (K04; `f6-26-2-03-context-compartilhamento-k04-gabarito-quiz-md`).
- `26.2_Organizacao/03_context_compartilhamento/Q05_quiz.md` — quiz (Q05; `f6-26-2-03-context-compartilhamento-q05-quiz-md`).
- `26.2_Organizacao/03_context_compartilhamento/K05_gabarito_quiz.md` — answer_key (K05; `f6-26-2-03-context-compartilhamento-k05-gabarito-quiz-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/P01_pratica.md` — practice (P01; `f6-26-2-01-responsabilidades-ownership-composicao-p01-pratica-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/KP01_solucao.md` — answer_key_pratica (KP01; `f6-26-2-01-responsabilidades-ownership-composicao-kp01-solucao-md`).
- `26.2_Organizacao/01_responsabilidades_ownership_composicao/R01_rubrica.md` — rubric (R01; `f6-26-2-01-responsabilidades-ownership-composicao-r01-rubrica-md`).
- `26.2_Organizacao/02_custom_hooks/P02_pratica.md` — practice (P02; `f6-26-2-02-custom-hooks-p02-pratica-md`).
- `26.2_Organizacao/02_custom_hooks/KP02_solucao.md` — answer_key_pratica (KP02; `f6-26-2-02-custom-hooks-kp02-solucao-md`).
- `26.2_Organizacao/02_custom_hooks/R02_rubrica.md` — rubric (R02; `f6-26-2-02-custom-hooks-r02-rubrica-md`).
- `26.2_Organizacao/03_context_compartilhamento/P03_pratica.md` — practice (P03; `f6-26-2-03-context-compartilhamento-p03-pratica-md`).
- `26.2_Organizacao/03_context_compartilhamento/KP03_solucao.md` — answer_key_pratica (KP03; `f6-26-2-03-context-compartilhamento-kp03-solucao-md`).
- `26.2_Organizacao/03_context_compartilhamento/R03_rubrica.md` — rubric (R03; `f6-26-2-03-context-compartilhamento-r03-rubrica-md`).

### 27.1 — 27.1_Comunicacao_com_backend
- `27.1_Comunicacao_com_backend/README.md` — topic_index (IDX; `f6-27-1-readme-md`).
- `27.1_Comunicacao_com_backend/00_objetivo.md` — objetivo (OBJ; `f6-27-1-00-objetivo-md`).
- `27.1_Comunicacao_com_backend/01_resumo.md` — resumo (RES; `f6-27-1-01-resumo-md`).
- `27.1_Comunicacao_com_backend/02_criterio_de_conclusao.md` — criterio (CRI; `f6-27-1-02-criterio-de-conclusao-md`).
- `27.1_Comunicacao_com_backend/03_conexoes.md` — conexoes (CON; `f6-27-1-03-conexoes-md`).
- `27.1_Comunicacao_com_backend/04_referencias.md` — referencias (REF; `f6-27-1-04-referencias-md`).
- `27.1_Comunicacao_com_backend/01_contrato_requisicao_resposta/01_teoria.md` — theory (T01; `f6-27-1-01-contrato-requisicao-resposta-01-teoria-md`).
- `27.1_Comunicacao_com_backend/02_autenticacao_credenciais/01_teoria.md` — theory (T02; `f6-27-1-02-autenticacao-credenciais-01-teoria-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/01_teoria.md` — theory (T03; `f6-27-1-03-requisicao-vigente-paginacao-01-teoria-md`).
- `27.1_Comunicacao_com_backend/04_cors_erros_integracao/01_teoria.md` — theory (T04; `f6-27-1-04-cors-erros-integracao-01-teoria-md`).
- `27.1_Comunicacao_com_backend/01_contrato_requisicao_resposta/Q01_quiz.md` — quiz (Q01; `f6-27-1-01-contrato-requisicao-resposta-q01-quiz-md`).
- `27.1_Comunicacao_com_backend/01_contrato_requisicao_resposta/K01_gabarito_quiz.md` — answer_key (K01; `f6-27-1-01-contrato-requisicao-resposta-k01-gabarito-quiz-md`).
- `27.1_Comunicacao_com_backend/02_autenticacao_credenciais/Q02_quiz.md` — quiz (Q02; `f6-27-1-02-autenticacao-credenciais-q02-quiz-md`).
- `27.1_Comunicacao_com_backend/02_autenticacao_credenciais/K02_gabarito_quiz.md` — answer_key (K02; `f6-27-1-02-autenticacao-credenciais-k02-gabarito-quiz-md`).
- `27.1_Comunicacao_com_backend/02_autenticacao_credenciais/Q03_quiz.md` — quiz (Q03; `f6-27-1-02-autenticacao-credenciais-q03-quiz-md`).
- `27.1_Comunicacao_com_backend/02_autenticacao_credenciais/K03_gabarito_quiz.md` — answer_key (K03; `f6-27-1-02-autenticacao-credenciais-k03-gabarito-quiz-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/Q04_quiz.md` — quiz (Q04; `f6-27-1-03-requisicao-vigente-paginacao-q04-quiz-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/K04_gabarito_quiz.md` — answer_key (K04; `f6-27-1-03-requisicao-vigente-paginacao-k04-gabarito-quiz-md`).
- `27.1_Comunicacao_com_backend/04_cors_erros_integracao/Q05_quiz.md` — quiz (Q05; `f6-27-1-04-cors-erros-integracao-q05-quiz-md`).
- `27.1_Comunicacao_com_backend/04_cors_erros_integracao/K05_gabarito_quiz.md` — answer_key (K05; `f6-27-1-04-cors-erros-integracao-k05-gabarito-quiz-md`).
- `27.1_Comunicacao_com_backend/90_integracao/P01_pratica.md` — practice (P01; `f6-27-1-90-integracao-p01-pratica-md`).
- `27.1_Comunicacao_com_backend/90_integracao/KP01_solucao.md` — answer_key_pratica (KP01; `f6-27-1-90-integracao-kp01-solucao-md`).
- `27.1_Comunicacao_com_backend/90_integracao/R01_rubrica.md` — rubric (R01; `f6-27-1-90-integracao-r01-rubrica-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/P02_pratica.md` — practice (P02; `f6-27-1-03-requisicao-vigente-paginacao-p02-pratica-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/KP02_solucao.md` — answer_key_pratica (KP02; `f6-27-1-03-requisicao-vigente-paginacao-kp02-solucao-md`).
- `27.1_Comunicacao_com_backend/03_requisicao_vigente_paginacao/R02_rubrica.md` — rubric (R02; `f6-27-1-03-requisicao-vigente-paginacao-r02-rubrica-md`).
- `27.1_Comunicacao_com_backend/90_integracao/P03_pratica.md` — practice (P03; `f6-27-1-90-integracao-p03-pratica-md`).
- `27.1_Comunicacao_com_backend/90_integracao/KP03_solucao.md` — answer_key_pratica (KP03; `f6-27-1-90-integracao-kp03-solucao-md`).
- `27.1_Comunicacao_com_backend/90_integracao/R03_rubrica.md` — rubric (R03; `f6-27-1-90-integracao-r03-rubrica-md`).

### 27.2 — 27.2_Estados_de_interface
- `27.2_Estados_de_interface/README.md` — topic_index (IDX; `f6-27-2-readme-md`).
- `27.2_Estados_de_interface/00_objetivo.md` — objetivo (OBJ; `f6-27-2-00-objetivo-md`).
- `27.2_Estados_de_interface/01_resumo.md` — resumo (RES; `f6-27-2-01-resumo-md`).
- `27.2_Estados_de_interface/02_criterio_de_conclusao.md` — criterio (CRI; `f6-27-2-02-criterio-de-conclusao-md`).
- `27.2_Estados_de_interface/03_conexoes.md` — conexoes (CON; `f6-27-2-03-conexoes-md`).
- `27.2_Estados_de_interface/04_referencias.md` — referencias (REF; `f6-27-2-04-referencias-md`).
- `27.2_Estados_de_interface/01_estado_operacao_comunicacao_acessivel/01_teoria.md` — theory (T01; `f6-27-2-01-estado-operacao-comunicacao-acessivel-01-teoria-md`).
- `27.2_Estados_de_interface/02_vazio_resultados_falhas/01_teoria.md` — theory (T02; `f6-27-2-02-vazio-resultados-falhas-01-teoria-md`).
- `27.2_Estados_de_interface/03_retry_seguro/01_teoria.md` — theory (T03; `f6-27-2-03-retry-seguro-01-teoria-md`).
- `27.2_Estados_de_interface/04_contexto_paginacao/01_teoria.md` — theory (T04; `f6-27-2-04-contexto-paginacao-01-teoria-md`).
- `27.2_Estados_de_interface/02_vazio_resultados_falhas/Q01_quiz.md` — quiz (Q01; `f6-27-2-02-vazio-resultados-falhas-q01-quiz-md`).
- `27.2_Estados_de_interface/02_vazio_resultados_falhas/K01_gabarito_quiz.md` — answer_key (K01; `f6-27-2-02-vazio-resultados-falhas-k01-gabarito-quiz-md`).
- `27.2_Estados_de_interface/01_estado_operacao_comunicacao_acessivel/Q02_quiz.md` — quiz (Q02; `f6-27-2-01-estado-operacao-comunicacao-acessivel-q02-quiz-md`).
- `27.2_Estados_de_interface/01_estado_operacao_comunicacao_acessivel/K02_gabarito_quiz.md` — answer_key (K02; `f6-27-2-01-estado-operacao-comunicacao-acessivel-k02-gabarito-quiz-md`).
- `27.2_Estados_de_interface/02_vazio_resultados_falhas/Q03_quiz.md` — quiz (Q03; `f6-27-2-02-vazio-resultados-falhas-q03-quiz-md`).
- `27.2_Estados_de_interface/02_vazio_resultados_falhas/K03_gabarito_quiz.md` — answer_key (K03; `f6-27-2-02-vazio-resultados-falhas-k03-gabarito-quiz-md`).
- `27.2_Estados_de_interface/03_retry_seguro/Q04_quiz.md` — quiz (Q04; `f6-27-2-03-retry-seguro-q04-quiz-md`).
- `27.2_Estados_de_interface/03_retry_seguro/K04_gabarito_quiz.md` — answer_key (K04; `f6-27-2-03-retry-seguro-k04-gabarito-quiz-md`).
- `27.2_Estados_de_interface/04_contexto_paginacao/Q05_quiz.md` — quiz (Q05; `f6-27-2-04-contexto-paginacao-q05-quiz-md`).
- `27.2_Estados_de_interface/04_contexto_paginacao/K05_gabarito_quiz.md` — answer_key (K05; `f6-27-2-04-contexto-paginacao-k05-gabarito-quiz-md`).
- `27.2_Estados_de_interface/90_integracao/P01_pratica.md` — practice (P01; `f6-27-2-90-integracao-p01-pratica-md`).
- `27.2_Estados_de_interface/04_contexto_paginacao/P02_pratica.md` — practice (P02; `f6-27-2-04-contexto-paginacao-p02-pratica-md`).
- `27.2_Estados_de_interface/90_integracao/P03_pratica.md` — practice (P03; `f6-27-2-90-integracao-p03-pratica-md`).

### 27.3 — 27.3_Contrato_de_dados
- `27.3_Contrato_de_dados/README.md` — topic_index (IDX; `f6-27-3-readme-md`).
- `27.3_Contrato_de_dados/00_objetivo.md` — objetivo (OBJ; `f6-27-3-00-objetivo-md`).
- `27.3_Contrato_de_dados/01_resumo.md` — resumo (RES; `f6-27-3-01-resumo-md`).
- `27.3_Contrato_de_dados/02_criterio_de_conclusao.md` — criterio (CRI; `f6-27-3-02-criterio-de-conclusao-md`).
- `27.3_Contrato_de_dados/03_conexoes.md` — conexoes (CON; `f6-27-3-03-conexoes-md`).
- `27.3_Contrato_de_dados/04_referencias.md` — referencias (REF; `f6-27-3-04-referencias-md`).
- `27.3_Contrato_de_dados/01_fronteira_contrato_validacao_runtime/01_teoria.md` — theory (T01; `f6-27-3-01-fronteira-contrato-validacao-runtime-01-teoria-md`).
- `27.3_Contrato_de_dados/02_presenca_nulidade_variacoes/01_teoria.md` — theory (T02; `f6-27-3-02-presenca-nulidade-variacoes-01-teoria-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/01_teoria.md` — theory (T03; `f6-27-3-03-evolucao-compatibilidade-01-teoria-md`).
- `27.3_Contrato_de_dados/01_fronteira_contrato_validacao_runtime/Q01_quiz.md` — quiz (Q01; `f6-27-3-01-fronteira-contrato-validacao-runtime-q01-quiz-md`).
- `27.3_Contrato_de_dados/01_fronteira_contrato_validacao_runtime/K01_gabarito_quiz.md` — answer_key (K01; `f6-27-3-01-fronteira-contrato-validacao-runtime-k01-gabarito-quiz-md`).
- `27.3_Contrato_de_dados/02_presenca_nulidade_variacoes/Q02_quiz.md` — quiz (Q02; `f6-27-3-02-presenca-nulidade-variacoes-q02-quiz-md`).
- `27.3_Contrato_de_dados/02_presenca_nulidade_variacoes/K02_gabarito_quiz.md` — answer_key (K02; `f6-27-3-02-presenca-nulidade-variacoes-k02-gabarito-quiz-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/Q03_quiz.md` — quiz (Q03; `f6-27-3-03-evolucao-compatibilidade-q03-quiz-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/K03_gabarito_quiz.md` — answer_key (K03; `f6-27-3-03-evolucao-compatibilidade-k03-gabarito-quiz-md`).
- `27.3_Contrato_de_dados/01_fronteira_contrato_validacao_runtime/Q04_quiz.md` — quiz (Q04; `f6-27-3-01-fronteira-contrato-validacao-runtime-q04-quiz-md`).
- `27.3_Contrato_de_dados/01_fronteira_contrato_validacao_runtime/K04_gabarito_quiz.md` — answer_key (K04; `f6-27-3-01-fronteira-contrato-validacao-runtime-k04-gabarito-quiz-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/Q05_quiz.md` — quiz (Q05; `f6-27-3-03-evolucao-compatibilidade-q05-quiz-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/K05_gabarito_quiz.md` — answer_key (K05; `f6-27-3-03-evolucao-compatibilidade-k05-gabarito-quiz-md`).
- `27.3_Contrato_de_dados/90_integracao/P01_pratica.md` — practice (P01; `f6-27-3-90-integracao-p01-pratica-md`).
- `27.3_Contrato_de_dados/90_integracao/P02_pratica.md` — practice (P02; `f6-27-3-90-integracao-p02-pratica-md`).
- `27.3_Contrato_de_dados/03_evolucao_compatibilidade/P03_pratica.md` — practice (P03; `f6-27-3-03-evolucao-compatibilidade-p03-pratica-md`).
- `27.3_Contrato_de_dados/90_integracao/RUB_rubrica_praticas.md` — rubric (RUB; `f6-27-3-90-integracao-rub-rubrica-praticas-md`).

### 27.4 — 27.4_Seguranca_no_navegador
- `27.4_Seguranca_no_navegador/README.md` — topic_index (IDX; `f6-27-4-readme-md`).
- `27.4_Seguranca_no_navegador/00_objetivo.md` — objetivo (OBJ; `f6-27-4-00-objetivo-md`).
- `27.4_Seguranca_no_navegador/01_resumo.md` — resumo (RES; `f6-27-4-01-resumo-md`).
- `27.4_Seguranca_no_navegador/02_criterio_de_conclusao.md` — criterio (CRI; `f6-27-4-02-criterio-de-conclusao-md`).
- `27.4_Seguranca_no_navegador/03_conexoes.md` — conexoes (CON; `f6-27-4-03-conexoes-md`).
- `27.4_Seguranca_no_navegador/04_referencias.md` — referencias (REF; `f6-27-4-04-referencias-md`).
- `27.4_Seguranca_no_navegador/01_entrada_nao_confiavel_defesas_xss/01_teoria.md` — theory (T01; `f6-27-4-01-entrada-nao-confiavel-defesas-xss-01-teoria-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/01_teoria.md` — theory (T02; `f6-27-4-02-csrf-cors-cookies-01-teoria-md`).
- `27.4_Seguranca_no_navegador/03_segredos_csp_dependencias/01_teoria.md` — theory (T03; `f6-27-4-03-segredos-csp-dependencias-01-teoria-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/Q01_quiz.md` — quiz (Q01; `f6-27-4-02-csrf-cors-cookies-q01-quiz-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/K01_gabarito_quiz.md` — answer_key (K01; `f6-27-4-02-csrf-cors-cookies-k01-gabarito-quiz-md`).
- `27.4_Seguranca_no_navegador/01_entrada_nao_confiavel_defesas_xss/Q02_quiz.md` — quiz (Q02; `f6-27-4-01-entrada-nao-confiavel-defesas-xss-q02-quiz-md`).
- `27.4_Seguranca_no_navegador/01_entrada_nao_confiavel_defesas_xss/K02_gabarito_quiz.md` — answer_key (K02; `f6-27-4-01-entrada-nao-confiavel-defesas-xss-k02-gabarito-quiz-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/Q03_quiz.md` — quiz (Q03; `f6-27-4-02-csrf-cors-cookies-q03-quiz-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/K03_gabarito_quiz.md` — answer_key (K03; `f6-27-4-02-csrf-cors-cookies-k03-gabarito-quiz-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/Q04_quiz.md` — quiz (Q04; `f6-27-4-02-csrf-cors-cookies-q04-quiz-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/K04_gabarito_quiz.md` — answer_key (K04; `f6-27-4-02-csrf-cors-cookies-k04-gabarito-quiz-md`).
- `27.4_Seguranca_no_navegador/03_segredos_csp_dependencias/Q05_quiz.md` — quiz (Q05; `f6-27-4-03-segredos-csp-dependencias-q05-quiz-md`).
- `27.4_Seguranca_no_navegador/03_segredos_csp_dependencias/K05_gabarito_quiz.md` — answer_key (K05; `f6-27-4-03-segredos-csp-dependencias-k05-gabarito-quiz-md`).
- `27.4_Seguranca_no_navegador/01_entrada_nao_confiavel_defesas_xss/P01_pratica.md` — practice (P01; `f6-27-4-01-entrada-nao-confiavel-defesas-xss-p01-pratica-md`).
- `27.4_Seguranca_no_navegador/02_csrf_cors_cookies/P02_pratica.md` — practice (P02; `f6-27-4-02-csrf-cors-cookies-p02-pratica-md`).
- `27.4_Seguranca_no_navegador/03_segredos_csp_dependencias/P03_pratica.md` — practice (P03; `f6-27-4-03-segredos-csp-dependencias-p03-pratica-md`).
- `27.4_Seguranca_no_navegador/90_integracao/RUB_rubrica_praticas.md` — rubric (RUB; `f6-27-4-90-integracao-rub-rubrica-praticas-md`).

### 28.1 — 28.1_Ferramentas
- `28.1_Ferramentas/README.md` — topic_index (IDX; `f6-28-1-readme-md`).
- `28.1_Ferramentas/00_objetivo.md` — objetivo (OBJ; `f6-28-1-00-objetivo-md`).
- `28.1_Ferramentas/01_resumo.md` — resumo (RES; `f6-28-1-01-resumo-md`).
- `28.1_Ferramentas/02_criterio_de_conclusao.md` — criterio (CRI; `f6-28-1-02-criterio-de-conclusao-md`).
- `28.1_Ferramentas/03_conexoes.md` — conexoes (CON; `f6-28-1-03-conexoes-md`).
- `28.1_Ferramentas/04_referencias.md` — referencias (REF; `f6-28-1-04-referencias-md`).
- `28.1_Ferramentas/01_criterio_de_escolha_vite_build/01_teoria.md` — theory (T01; `f6-28-1-01-criterio-de-escolha-vite-build-01-teoria-md`).
- `28.1_Ferramentas/02_estado_local_vs_remoto/01_teoria.md` — theory (T02; `f6-28-1-02-estado-local-vs-remoto-01-teoria-md`).
- `28.1_Ferramentas/03_fronteiras_store_cache/01_teoria.md` — theory (T03; `f6-28-1-03-fronteiras-store-cache-01-teoria-md`).
- `28.1_Ferramentas/01_criterio_de_escolha_vite_build/Q01_quiz.md` — quiz (Q01; `f6-28-1-01-criterio-de-escolha-vite-build-q01-quiz-md`).
- `28.1_Ferramentas/01_criterio_de_escolha_vite_build/K01_gabarito_quiz.md` — answer_key (K01; `f6-28-1-01-criterio-de-escolha-vite-build-k01-gabarito-quiz-md`).
- `28.1_Ferramentas/02_estado_local_vs_remoto/Q02_quiz.md` — quiz (Q02; `f6-28-1-02-estado-local-vs-remoto-q02-quiz-md`).
- `28.1_Ferramentas/02_estado_local_vs_remoto/K02_gabarito_quiz.md` — answer_key (K02; `f6-28-1-02-estado-local-vs-remoto-k02-gabarito-quiz-md`).
- `28.1_Ferramentas/03_fronteiras_store_cache/Q03_quiz.md` — quiz (Q03; `f6-28-1-03-fronteiras-store-cache-q03-quiz-md`).
- `28.1_Ferramentas/03_fronteiras_store_cache/K03_gabarito_quiz.md` — answer_key (K03; `f6-28-1-03-fronteiras-store-cache-k03-gabarito-quiz-md`).
- `28.1_Ferramentas/01_criterio_de_escolha_vite_build/Q04_quiz.md` — quiz (Q04; `f6-28-1-01-criterio-de-escolha-vite-build-q04-quiz-md`).
- `28.1_Ferramentas/01_criterio_de_escolha_vite_build/K04_gabarito_quiz.md` — answer_key (K04; `f6-28-1-01-criterio-de-escolha-vite-build-k04-gabarito-quiz-md`).
- `28.1_Ferramentas/03_fronteiras_store_cache/Q05_quiz.md` — quiz (Q05; `f6-28-1-03-fronteiras-store-cache-q05-quiz-md`).
- `28.1_Ferramentas/03_fronteiras_store_cache/K05_gabarito_quiz.md` — answer_key (K05; `f6-28-1-03-fronteiras-store-cache-k05-gabarito-quiz-md`).
- `28.1_Ferramentas/02_estado_local_vs_remoto/P01_pratica.md` — practice (P01; `f6-28-1-02-estado-local-vs-remoto-p01-pratica-md`).
- `28.1_Ferramentas/90_integracao/P02_pratica.md` — practice (P02; `f6-28-1-90-integracao-p02-pratica-md`).
- `28.1_Ferramentas/90_integracao/P03_pratica.md` — practice (P03; `f6-28-1-90-integracao-p03-pratica-md`).

### 28.2 — 28.2_Gerencia_de_dados
- `28.2_Gerencia_de_dados/README.md` — topic_index (IDX; `f6-28-2-readme-md`).
- `28.2_Gerencia_de_dados/00_objetivo.md` — objetivo (OBJ; `f6-28-2-00-objetivo-md`).
- `28.2_Gerencia_de_dados/01_resumo.md` — resumo (RES; `f6-28-2-01-resumo-md`).
- `28.2_Gerencia_de_dados/02_criterio_de_conclusao.md` — criterio (CRI; `f6-28-2-02-criterio-de-conclusao-md`).
- `28.2_Gerencia_de_dados/03_conexoes.md` — conexoes (CON; `f6-28-2-03-conexoes-md`).
- `28.2_Gerencia_de_dados/04_referencias.md` — referencias (REF; `f6-28-2-04-referencias-md`).
- `28.2_Gerencia_de_dados/01_fonte_de_verdade/01_teoria.md` — theory (T01; `f6-28-2-01-fonte-de-verdade-01-teoria-md`).
- `28.2_Gerencia_de_dados/02_identidade_de_consultas/01_teoria.md` — theory (T02; `f6-28-2-02-identidade-de-consultas-01-teoria-md`).
- `28.2_Gerencia_de_dados/03_frescor_ciclo_de_cache/01_teoria.md` — theory (T03; `f6-28-2-03-frescor-ciclo-de-cache-01-teoria-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/01_teoria.md` — theory (T04; `f6-28-2-04-mutacoes-conflitos-reconciliacao-01-teoria-md`).
- `28.2_Gerencia_de_dados/01_fonte_de_verdade/Q01_quiz.md` — quiz (Q01; `f6-28-2-01-fonte-de-verdade-q01-quiz-md`).
- `28.2_Gerencia_de_dados/01_fonte_de_verdade/K01_gabarito_quiz.md` — answer_key (K01; `f6-28-2-01-fonte-de-verdade-k01-gabarito-quiz-md`).
- `28.2_Gerencia_de_dados/02_identidade_de_consultas/Q02_quiz.md` — quiz (Q02; `f6-28-2-02-identidade-de-consultas-q02-quiz-md`).
- `28.2_Gerencia_de_dados/02_identidade_de_consultas/K02_gabarito_quiz.md` — answer_key (K02; `f6-28-2-02-identidade-de-consultas-k02-gabarito-quiz-md`).
- `28.2_Gerencia_de_dados/03_frescor_ciclo_de_cache/Q03_quiz.md` — quiz (Q03; `f6-28-2-03-frescor-ciclo-de-cache-q03-quiz-md`).
- `28.2_Gerencia_de_dados/03_frescor_ciclo_de_cache/K03_gabarito_quiz.md` — answer_key (K03; `f6-28-2-03-frescor-ciclo-de-cache-k03-gabarito-quiz-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/Q04_quiz.md` — quiz (Q04; `f6-28-2-04-mutacoes-conflitos-reconciliacao-q04-quiz-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/K04_gabarito_quiz.md` — answer_key (K04; `f6-28-2-04-mutacoes-conflitos-reconciliacao-k04-gabarito-quiz-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/Q05_quiz.md` — quiz (Q05; `f6-28-2-04-mutacoes-conflitos-reconciliacao-q05-quiz-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/K05_gabarito_quiz.md` — answer_key (K05; `f6-28-2-04-mutacoes-conflitos-reconciliacao-k05-gabarito-quiz-md`).
- `28.2_Gerencia_de_dados/01_fonte_de_verdade/P01_pratica.md` — practice (P01; `f6-28-2-01-fonte-de-verdade-p01-pratica-md`).
- `28.2_Gerencia_de_dados/90_integracao/P02_pratica.md` — practice (P02; `f6-28-2-90-integracao-p02-pratica-md`).
- `28.2_Gerencia_de_dados/04_mutacoes_conflitos_reconciliacao/P03_pratica.md` — practice (P03; `f6-28-2-04-mutacoes-conflitos-reconciliacao-p03-pratica-md`).

### 28.3 — 28.3_Organizacao
- `28.3_Organizacao/README.md` — topic_index (IDX; `f6-28-3-readme-md`).
- `28.3_Organizacao/00_objetivo.md` — objetivo (OBJ; `f6-28-3-00-objetivo-md`).
- `28.3_Organizacao/01_resumo.md` — resumo (RES; `f6-28-3-01-resumo-md`).
- `28.3_Organizacao/02_criterio_de_conclusao.md` — criterio (CRI; `f6-28-3-02-criterio-de-conclusao-md`).
- `28.3_Organizacao/03_conexoes.md` — conexoes (CON; `f6-28-3-03-conexoes-md`).
- `28.3_Organizacao/04_referencias.md` — referencias (REF; `f6-28-3-04-referencias-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/01_teoria.md` — theory (T01; `f6-28-3-01-consumidores-dono-elevacao-01-teoria-md`).
- `28.3_Organizacao/02_estado_derivado_sem_redundancia/01_teoria.md` — theory (T02; `f6-28-3-02-estado-derivado-sem-redundancia-01-teoria-md`).
- `28.3_Organizacao/03_persistencia_reset_identidade/01_teoria.md` — theory (T03; `f6-28-3-03-persistencia-reset-identidade-01-teoria-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/Q01_quiz.md` — quiz (Q01; `f6-28-3-01-consumidores-dono-elevacao-q01-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/K01_gabarito_quiz.md` — answer_key (K01; `f6-28-3-01-consumidores-dono-elevacao-k01-gabarito-quiz-md`).
- `28.3_Organizacao/02_estado_derivado_sem_redundancia/Q02_quiz.md` — quiz (Q02; `f6-28-3-02-estado-derivado-sem-redundancia-q02-quiz-md`).
- `28.3_Organizacao/02_estado_derivado_sem_redundancia/K02_gabarito_quiz.md` — answer_key (K02; `f6-28-3-02-estado-derivado-sem-redundancia-k02-gabarito-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/Q03_quiz.md` — quiz (Q03; `f6-28-3-01-consumidores-dono-elevacao-q03-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/K03_gabarito_quiz.md` — answer_key (K03; `f6-28-3-01-consumidores-dono-elevacao-k03-gabarito-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/Q04_quiz.md` — quiz (Q04; `f6-28-3-01-consumidores-dono-elevacao-q04-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/K04_gabarito_quiz.md` — answer_key (K04; `f6-28-3-01-consumidores-dono-elevacao-k04-gabarito-quiz-md`).
- `28.3_Organizacao/03_persistencia_reset_identidade/Q05_quiz.md` — quiz (Q05; `f6-28-3-03-persistencia-reset-identidade-q05-quiz-md`).
- `28.3_Organizacao/03_persistencia_reset_identidade/K05_gabarito_quiz.md` — answer_key (K05; `f6-28-3-03-persistencia-reset-identidade-k05-gabarito-quiz-md`).
- `28.3_Organizacao/01_consumidores_dono_elevacao/P01_pratica.md` — practice (P01; `f6-28-3-01-consumidores-dono-elevacao-p01-pratica-md`).
- `28.3_Organizacao/90_integracao/P02_pratica.md` — practice (P02; `f6-28-3-90-integracao-p02-pratica-md`).
- `28.3_Organizacao/03_persistencia_reset_identidade/P03_pratica.md` — practice (P03; `f6-28-3-03-persistencia-reset-identidade-p03-pratica-md`).

### 29.1 — 29.1_Base_de_testes
- `29.1_Base_de_testes/README.md` — topic_index (IDX; `f6-29-1-readme-md`).
- `29.1_Base_de_testes/00_objetivo.md` — objetivo (OBJ; `f6-29-1-00-objetivo-md`).
- `29.1_Base_de_testes/01_resumo.md` — resumo (RES; `f6-29-1-01-resumo-md`).
- `29.1_Base_de_testes/02_criterio_de_conclusao.md` — criterio (CRI; `f6-29-1-02-criterio-de-conclusao-md`).
- `29.1_Base_de_testes/03_conexoes.md` — conexoes (CON; `f6-29-1-03-conexoes-md`).
- `29.1_Base_de_testes/04_referencias.md` — referencias (REF; `f6-29-1-04-referencias-md`).
- `29.1_Base_de_testes/01_consultas_semanticas/01_teoria.md` — theory (T01; `f6-29-1-01-consultas-semanticas-01-teoria-md`).
- `29.1_Base_de_testes/02_runner_ambiente/01_teoria.md` — theory (T02; `f6-29-1-02-runner-ambiente-01-teoria-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/01_teoria.md` — theory (T03; `f6-29-1-03-interacao-assincrona-01-teoria-md`).
- `29.1_Base_de_testes/04_isolamento_assertions/01_teoria.md` — theory (T04; `f6-29-1-04-isolamento-assertions-01-teoria-md`).
- `29.1_Base_de_testes/01_consultas_semanticas/Q01_quiz.md` — quiz (Q01; `f6-29-1-01-consultas-semanticas-q01-quiz-md`).
- `29.1_Base_de_testes/01_consultas_semanticas/K01_gabarito_quiz.md` — answer_key (K01; `f6-29-1-01-consultas-semanticas-k01-gabarito-quiz-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/Q02_quiz.md` — quiz (Q02; `f6-29-1-03-interacao-assincrona-q02-quiz-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/K02_gabarito_quiz.md` — answer_key (K02; `f6-29-1-03-interacao-assincrona-k02-gabarito-quiz-md`).
- `29.1_Base_de_testes/04_isolamento_assertions/Q03_quiz.md` — quiz (Q03; `f6-29-1-04-isolamento-assertions-q03-quiz-md`).
- `29.1_Base_de_testes/04_isolamento_assertions/K03_gabarito_quiz.md` — answer_key (K03; `f6-29-1-04-isolamento-assertions-k03-gabarito-quiz-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/Q04_quiz.md` — quiz (Q04; `f6-29-1-03-interacao-assincrona-q04-quiz-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/K04_gabarito_quiz.md` — answer_key (K04; `f6-29-1-03-interacao-assincrona-k04-gabarito-quiz-md`).
- `29.1_Base_de_testes/02_runner_ambiente/Q05_quiz.md` — quiz (Q05; `f6-29-1-02-runner-ambiente-q05-quiz-md`).
- `29.1_Base_de_testes/02_runner_ambiente/K05_gabarito_quiz.md` — answer_key (K05; `f6-29-1-02-runner-ambiente-k05-gabarito-quiz-md`).
- `29.1_Base_de_testes/90_integracao/P01_pratica.md` — practice (P01; `f6-29-1-90-integracao-p01-pratica-md`).
- `29.1_Base_de_testes/03_interacao_assincrona/P02_pratica.md` — practice (P02; `f6-29-1-03-interacao-assincrona-p02-pratica-md`).
- `29.1_Base_de_testes/90_integracao/P03_pratica.md` — practice (P03; `f6-29-1-90-integracao-p03-pratica-md`).

### 29.2 — 29.2_Integracao_e_borda
- `29.2_Integracao_e_borda/README.md` — topic_index (IDX; `f6-29-2-readme-md`).
- `29.2_Integracao_e_borda/00_objetivo.md` — objetivo (OBJ; `f6-29-2-00-objetivo-md`).
- `29.2_Integracao_e_borda/01_resumo.md` — resumo (RES; `f6-29-2-01-resumo-md`).
- `29.2_Integracao_e_borda/02_criterio_de_conclusao.md` — criterio (CRI; `f6-29-2-02-criterio-de-conclusao-md`).
- `29.2_Integracao_e_borda/03_conexoes.md` — conexoes (CON; `f6-29-2-03-conexoes-md`).
- `29.2_Integracao_e_borda/04_referencias.md` — referencias (REF; `f6-29-2-04-referencias-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/01_teoria.md` — theory (T01; `f6-29-2-01-fronteiras-e-mocks-de-rede-01-teoria-md`).
- `29.2_Integracao_e_borda/02_fluxos_e2e_playwright/01_teoria.md` — theory (T02; `f6-29-2-02-fluxos-e2e-playwright-01-teoria-md`).
- `29.2_Integracao_e_borda/03_flakiness_e_evidencia/01_teoria.md` — theory (T03; `f6-29-2-03-flakiness-e-evidencia-01-teoria-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/Q01_quiz.md` — quiz (Q01; `f6-29-2-01-fronteiras-e-mocks-de-rede-q01-quiz-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/K01_gabarito_quiz.md` — answer_key (K01; `f6-29-2-01-fronteiras-e-mocks-de-rede-k01-gabarito-quiz-md`).
- `29.2_Integracao_e_borda/02_fluxos_e2e_playwright/Q02_quiz.md` — quiz (Q02; `f6-29-2-02-fluxos-e2e-playwright-q02-quiz-md`).
- `29.2_Integracao_e_borda/02_fluxos_e2e_playwright/K02_gabarito_quiz.md` — answer_key (K02; `f6-29-2-02-fluxos-e2e-playwright-k02-gabarito-quiz-md`).
- `29.2_Integracao_e_borda/03_flakiness_e_evidencia/Q03_quiz.md` — quiz (Q03; `f6-29-2-03-flakiness-e-evidencia-q03-quiz-md`).
- `29.2_Integracao_e_borda/03_flakiness_e_evidencia/K03_gabarito_quiz.md` — answer_key (K03; `f6-29-2-03-flakiness-e-evidencia-k03-gabarito-quiz-md`).
- `29.2_Integracao_e_borda/90_integracao/Q04_quiz.md` — quiz (Q04; `f6-29-2-90-integracao-q04-quiz-md`).
- `29.2_Integracao_e_borda/90_integracao/K04_gabarito_quiz.md` — answer_key (K04; `f6-29-2-90-integracao-k04-gabarito-quiz-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/Q05_quiz.md` — quiz (Q05; `f6-29-2-01-fronteiras-e-mocks-de-rede-q05-quiz-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/K05_gabarito_quiz.md` — answer_key (K05; `f6-29-2-01-fronteiras-e-mocks-de-rede-k05-gabarito-quiz-md`).
- `29.2_Integracao_e_borda/01_fronteiras_e_mocks_de_rede/P01_pratica.md` — practice (P01; `f6-29-2-01-fronteiras-e-mocks-de-rede-p01-pratica-md`).
- `29.2_Integracao_e_borda/02_fluxos_e2e_playwright/P02_pratica.md` — practice (P02; `f6-29-2-02-fluxos-e2e-playwright-p02-pratica-md`).
- `29.2_Integracao_e_borda/03_flakiness_e_evidencia/P03_pratica.md` — practice (P03; `f6-29-2-03-flakiness-e-evidencia-p03-pratica-md`).

### 30.1 — 30.1_Otimizacao
- `30.1_Otimizacao/README.md` — topic_index (IDX; `f6-30-1-readme-md`).
- `30.1_Otimizacao/00_objetivo.md` — objetivo (OBJ; `f6-30-1-00-objetivo-md`).
- `30.1_Otimizacao/01_resumo.md` — resumo (RES; `f6-30-1-01-resumo-md`).
- `30.1_Otimizacao/02_criterio_de_conclusao.md` — criterio (CRI; `f6-30-1-02-criterio-de-conclusao-md`).
- `30.1_Otimizacao/03_conexoes.md` — conexoes (CON; `f6-30-1-03-conexoes-md`).
- `30.1_Otimizacao/04_referencias.md` — referencias (REF; `f6-30-1-04-referencias-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/01_teoria.md` — theory (T01; `f6-30-1-01-medicao-baseline-memoizacao-01-teoria-md`).
- `30.1_Otimizacao/02_carregamento_e_virtualizacao/01_teoria.md` — theory (T02; `f6-30-1-02-carregamento-e-virtualizacao-01-teoria-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/Q01_quiz.md` — quiz (Q01; `f6-30-1-01-medicao-baseline-memoizacao-q01-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/K01_gabarito_quiz.md` — answer_key (K01; `f6-30-1-01-medicao-baseline-memoizacao-k01-gabarito-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/Q02_quiz.md` — quiz (Q02; `f6-30-1-01-medicao-baseline-memoizacao-q02-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/K02_gabarito_quiz.md` — answer_key (K02; `f6-30-1-01-medicao-baseline-memoizacao-k02-gabarito-quiz-md`).
- `30.1_Otimizacao/90_integracao/Q03_quiz.md` — quiz (Q03; `f6-30-1-90-integracao-q03-quiz-md`).
- `30.1_Otimizacao/90_integracao/K03_gabarito_quiz.md` — answer_key (K03; `f6-30-1-90-integracao-k03-gabarito-quiz-md`).
- `30.1_Otimizacao/02_carregamento_e_virtualizacao/Q04_quiz.md` — quiz (Q04; `f6-30-1-02-carregamento-e-virtualizacao-q04-quiz-md`).
- `30.1_Otimizacao/02_carregamento_e_virtualizacao/K04_gabarito_quiz.md` — answer_key (K04; `f6-30-1-02-carregamento-e-virtualizacao-k04-gabarito-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/Q05_quiz.md` — quiz (Q05; `f6-30-1-01-medicao-baseline-memoizacao-q05-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/K05_gabarito_quiz.md` — answer_key (K05; `f6-30-1-01-medicao-baseline-memoizacao-k05-gabarito-quiz-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/P01_pratica.md` — practice (P01; `f6-30-1-01-medicao-baseline-memoizacao-p01-pratica-md`).
- `30.1_Otimizacao/01_medicao_baseline_memoizacao/P02_pratica.md` — practice (P02; `f6-30-1-01-medicao-baseline-memoizacao-p02-pratica-md`).
- `30.1_Otimizacao/02_carregamento_e_virtualizacao/P03_pratica.md` — practice (P03; `f6-30-1-02-carregamento-e-virtualizacao-p03-pratica-md`).

### 30.2 — 30.2_Maturidade
- `30.2_Maturidade/README.md` — topic_index (IDX; `f6-30-2-readme-md`).
- `30.2_Maturidade/00_objetivo.md` — objetivo (OBJ; `f6-30-2-00-objetivo-md`).
- `30.2_Maturidade/01_resumo.md` — resumo (RES; `f6-30-2-01-resumo-md`).
- `30.2_Maturidade/02_criterio_de_conclusao.md` — criterio (CRI; `f6-30-2-02-criterio-de-conclusao-md`).
- `30.2_Maturidade/03_conexoes.md` — conexoes (CON; `f6-30-2-03-conexoes-md`).
- `30.2_Maturidade/04_referencias.md` — referencias (REF; `f6-30-2-04-referencias-md`).
- `30.2_Maturidade/01_hipotese_de_desempenho/01_teoria.md` — theory (T01; `f6-30-2-01-hipotese-de-desempenho-01-teoria-md`).
- `30.2_Maturidade/02_variacao_medicoes/01_teoria.md` — theory (T02; `f6-30-2-02-variacao-medicoes-01-teoria-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/01_teoria.md` — theory (T03; `f6-30-2-03-tradeoffs-regressoes-01-teoria-md`).
- `30.2_Maturidade/04_registro_decisao/01_teoria.md` — theory (T04; `f6-30-2-04-registro-decisao-01-teoria-md`).
- `30.2_Maturidade/01_hipotese_de_desempenho/Q01_quiz.md` — quiz (Q01; `f6-30-2-01-hipotese-de-desempenho-q01-quiz-md`).
- `30.2_Maturidade/01_hipotese_de_desempenho/K01_gabarito_quiz.md` — answer_key (K01; `f6-30-2-01-hipotese-de-desempenho-k01-gabarito-quiz-md`).
- `30.2_Maturidade/02_variacao_medicoes/Q02_quiz.md` — quiz (Q02; `f6-30-2-02-variacao-medicoes-q02-quiz-md`).
- `30.2_Maturidade/02_variacao_medicoes/K02_gabarito_quiz.md` — answer_key (K02; `f6-30-2-02-variacao-medicoes-k02-gabarito-quiz-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/Q03_quiz.md` — quiz (Q03; `f6-30-2-03-tradeoffs-regressoes-q03-quiz-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/K03_gabarito_quiz.md` — answer_key (K03; `f6-30-2-03-tradeoffs-regressoes-k03-gabarito-quiz-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/Q04_quiz.md` — quiz (Q04; `f6-30-2-03-tradeoffs-regressoes-q04-quiz-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/K04_gabarito_quiz.md` — answer_key (K04; `f6-30-2-03-tradeoffs-regressoes-k04-gabarito-quiz-md`).
- `30.2_Maturidade/04_registro_decisao/Q05_quiz.md` — quiz (Q05; `f6-30-2-04-registro-decisao-q05-quiz-md`).
- `30.2_Maturidade/04_registro_decisao/K05_gabarito_quiz.md` — answer_key (K05; `f6-30-2-04-registro-decisao-k05-gabarito-quiz-md`).
- `30.2_Maturidade/90_integracao/P01_pratica.md` — practice (P01; `f6-30-2-90-integracao-p01-pratica-md`).
- `30.2_Maturidade/03_tradeoffs_regressoes/P02_pratica.md` — practice (P02; `f6-30-2-03-tradeoffs-regressoes-p02-pratica-md`).
- `30.2_Maturidade/04_registro_decisao/P03_pratica.md` — practice (P03; `f6-30-2-04-registro-decisao-p03-pratica-md`).

### 31.1 — 31.1_Next_js
- `31.1_Next_js/README.md` — topic_index (IDX; `f6-31-1-readme-md`).
- `31.1_Next_js/00_objetivo.md` — objetivo (OBJ; `f6-31-1-00-objetivo-md`).
- `31.1_Next_js/01_resumo.md` — resumo (RES; `f6-31-1-01-resumo-md`).
- `31.1_Next_js/02_criterio_de_conclusao.md` — criterio (CRI; `f6-31-1-02-criterio-de-conclusao-md`).
- `31.1_Next_js/03_conexoes.md` — conexoes (CON; `f6-31-1-03-conexoes-md`).
- `31.1_Next_js/04_referencias.md` — referencias (REF; `f6-31-1-04-referencias-md`).
- `31.1_Next_js/01_estrutura_rotas_app_router/01_teoria.md` — theory (T01; `f6-31-1-01-estrutura-rotas-app-router-01-teoria-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/01_teoria.md` — theory (T02; `f6-31-1-02-fronteira-e-renderizacao-01-teoria-md`).
- `31.1_Next_js/03_route_handlers_endpoints/01_teoria.md` — theory (T03; `f6-31-1-03-route-handlers-endpoints-01-teoria-md`).
- `31.1_Next_js/03_route_handlers_endpoints/Q01_quiz.md` — quiz (Q01; `f6-31-1-03-route-handlers-endpoints-q01-quiz-md`).
- `31.1_Next_js/03_route_handlers_endpoints/K01_gabarito_quiz.md` — answer_key (K01; `f6-31-1-03-route-handlers-endpoints-k01-gabarito-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/Q02_quiz.md` — quiz (Q02; `f6-31-1-02-fronteira-e-renderizacao-q02-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/K02_gabarito_quiz.md` — answer_key (K02; `f6-31-1-02-fronteira-e-renderizacao-k02-gabarito-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/Q03_quiz.md` — quiz (Q03; `f6-31-1-02-fronteira-e-renderizacao-q03-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/K03_gabarito_quiz.md` — answer_key (K03; `f6-31-1-02-fronteira-e-renderizacao-k03-gabarito-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/Q04_quiz.md` — quiz (Q04; `f6-31-1-02-fronteira-e-renderizacao-q04-quiz-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/K04_gabarito_quiz.md` — answer_key (K04; `f6-31-1-02-fronteira-e-renderizacao-k04-gabarito-quiz-md`).
- `31.1_Next_js/90_integracao/Q05_quiz.md` — quiz (Q05; `f6-31-1-90-integracao-q05-quiz-md`).
- `31.1_Next_js/90_integracao/K05_gabarito_quiz.md` — answer_key (K05; `f6-31-1-90-integracao-k05-gabarito-quiz-md`).
- `31.1_Next_js/01_estrutura_rotas_app_router/P01_pratica.md` — practice (P01; `f6-31-1-01-estrutura-rotas-app-router-p01-pratica-md`).
- `31.1_Next_js/02_fronteira_e_renderizacao/P02_pratica.md` — practice (P02; `f6-31-1-02-fronteira-e-renderizacao-p02-pratica-md`).
- `31.1_Next_js/90_integracao/P03_pratica.md` — practice (P03; `f6-31-1-90-integracao-p03-pratica-md`).

### 31.2 — 31.2_React_Native
- `31.2_React_Native/README.md` — topic_index (IDX; `f6-31-2-readme-md`).
- `31.2_React_Native/00_objetivo.md` — objetivo (OBJ; `f6-31-2-00-objetivo-md`).
- `31.2_React_Native/01_resumo.md` — resumo (RES; `f6-31-2-01-resumo-md`).
- `31.2_React_Native/02_criterio_de_conclusao.md` — criterio (CRI; `f6-31-2-02-criterio-de-conclusao-md`).
- `31.2_React_Native/03_conexoes.md` — conexoes (CON; `f6-31-2-03-conexoes-md`).
- `31.2_React_Native/04_referencias.md` — referencias (REF; `f6-31-2-04-referencias-md`).
- `31.2_React_Native/01_modelo_react_renderizador_nativo/01_teoria.md` — theory (T01; `f6-31-2-01-modelo-react-renderizador-nativo-01-teoria-md`).
- `31.2_React_Native/02_reuso_adaptacao_plataforma_distribuicao/01_teoria.md` — theory (T02; `f6-31-2-02-reuso-adaptacao-plataforma-distribuicao-01-teoria-md`).
- `31.2_React_Native/90_integracao/P01_pratica.md` — practice (P01; `f6-31-2-90-integracao-p01-pratica-md`).
- `31.2_React_Native/02_reuso_adaptacao_plataforma_distribuicao/P02_pratica.md` — practice (P02; `f6-31-2-02-reuso-adaptacao-plataforma-distribuicao-p02-pratica-md`).
- `31.2_React_Native/01_modelo_react_renderizador_nativo/F01_flashcard.md` — flashcard (F01; `f6-31-2-01-modelo-react-renderizador-nativo-f01-flashcard-md`).
- `31.2_React_Native/02_reuso_adaptacao_plataforma_distribuicao/F02_flashcard.md` — flashcard (F02; `f6-31-2-02-reuso-adaptacao-plataforma-distribuicao-f02-flashcard-md`).
- `31.2_React_Native/02_reuso_adaptacao_plataforma_distribuicao/F03_flashcard.md` — flashcard (F03; `f6-31-2-02-reuso-adaptacao-plataforma-distribuicao-f03-flashcard-md`).

### 31.3 — 31.3_Vue_e_Angular
- `31.3_Vue_e_Angular/README.md` — topic_index (IDX; `f6-31-3-readme-md`).
- `31.3_Vue_e_Angular/00_objetivo.md` — objetivo (OBJ; `f6-31-3-00-objetivo-md`).
- `31.3_Vue_e_Angular/01_resumo.md` — resumo (RES; `f6-31-3-01-resumo-md`).
- `31.3_Vue_e_Angular/02_criterio_de_conclusao.md` — criterio (CRI; `f6-31-3-02-criterio-de-conclusao-md`).
- `31.3_Vue_e_Angular/03_conexoes.md` — conexoes (CON; `f6-31-3-03-conexoes-md`).
- `31.3_Vue_e_Angular/04_referencias.md` — referencias (REF; `f6-31-3-04-referencias-md`).
- `31.3_Vue_e_Angular/01_modelos_componentes_reatividade/01_teoria.md` — theory (T01; `f6-31-3-01-modelos-componentes-reatividade-01-teoria-md`).
- `31.3_Vue_e_Angular/02_versoes_padroes_legado/01_teoria.md` — theory (T02; `f6-31-3-02-versoes-padroes-legado-01-teoria-md`).
- `31.3_Vue_e_Angular/01_modelos_componentes_reatividade/P01_pratica.md` — practice (P01; `f6-31-3-01-modelos-componentes-reatividade-p01-pratica-md`).
- `31.3_Vue_e_Angular/02_versoes_padroes_legado/P02_pratica.md` — practice (P02; `f6-31-3-02-versoes-padroes-legado-p02-pratica-md`).
- `31.3_Vue_e_Angular/01_modelos_componentes_reatividade/F01_flashcard.md` — flashcard (F01; `f6-31-3-01-modelos-componentes-reatividade-f01-flashcard-md`).
- `31.3_Vue_e_Angular/01_modelos_componentes_reatividade/F02_flashcard.md` — flashcard (F02; `f6-31-3-01-modelos-componentes-reatividade-f02-flashcard-md`).
- `31.3_Vue_e_Angular/02_versoes_padroes_legado/F03_flashcard.md` — flashcard (F03; `f6-31-3-02-versoes-padroes-legado-f03-flashcard-md`).

### 31.4 — 31.4_Projeto_incremental_da_fase
- `31.4_Projeto_incremental_da_fase/README.md` — topic_index (IDX; `f6-31-4-readme-md`).
- `31.4_Projeto_incremental_da_fase/00_objetivo.md` — objetivo (OBJ; `f6-31-4-00-objetivo-md`).
- `31.4_Projeto_incremental_da_fase/01_resumo.md` — resumo (RES; `f6-31-4-01-resumo-md`).
- `31.4_Projeto_incremental_da_fase/02_criterio_de_conclusao.md` — criterio (CRI; `f6-31-4-02-criterio-de-conclusao-md`).
- `31.4_Projeto_incremental_da_fase/03_conexoes.md` — conexoes (CON; `f6-31-4-03-conexoes-md`).
- `31.4_Projeto_incremental_da_fase/04_referencias.md` — referencias (REF; `f6-31-4-04-referencias-md`).
- `31.4_Projeto_incremental_da_fase/00_escopo_e_regras.md` — project_scope (SCP; `f6-31-4-00-escopo-e-regras-md`).
- `31.4_Projeto_incremental_da_fase/M01_fatia_vertical_api.md` — milestone (M01; `f6-31-4-m01-fatia-vertical-api-md`).
- `31.4_Projeto_incremental_da_fase/C01_aceite.md` — acceptance_criteria (C01; `f6-31-4-c01-aceite-md`).
- `31.4_Projeto_incremental_da_fase/M02_estados_acessibilidade.md` — milestone (M02; `f6-31-4-m02-estados-acessibilidade-md`).
- `31.4_Projeto_incremental_da_fase/C02_aceite.md` — acceptance_criteria (C02; `f6-31-4-c02-aceite-md`).
- `31.4_Projeto_incremental_da_fase/M03_testes_fronteiras.md` — milestone (M03; `f6-31-4-m03-testes-fronteiras-md`).
- `31.4_Projeto_incremental_da_fase/C03_aceite.md` — acceptance_criteria (C03; `f6-31-4-c03-aceite-md`).
- `31.4_Projeto_incremental_da_fase/M04_medicao_entrega.md` — milestone (M04; `f6-31-4-m04-medicao-entrega-md`).
- `31.4_Projeto_incremental_da_fase/C04_aceite.md` — acceptance_criteria (C04; `f6-31-4-c04-aceite-md`).
- `31.4_Projeto_incremental_da_fase/RUB_rubrica_marcos.md` — rubric (RUB; `f6-31-4-rub-rubrica-marcos-md`).
- `31.4_Projeto_incremental_da_fase/CHK_checklist_final.md` — checklist (CHK; `f6-31-4-chk-checklist-final-md`).

### 31.5 — 31.5_Projeto_de_fase_Trilho_B
- `31.5_Projeto_de_fase_Trilho_B/README.md` — topic_index (IDX; `f6-31-5-readme-md`).
- `31.5_Projeto_de_fase_Trilho_B/00_objetivo.md` — objetivo (OBJ; `f6-31-5-00-objetivo-md`).
- `31.5_Projeto_de_fase_Trilho_B/01_resumo.md` — resumo (RES; `f6-31-5-01-resumo-md`).
- `31.5_Projeto_de_fase_Trilho_B/02_criterio_de_conclusao.md` — criterio (CRI; `f6-31-5-02-criterio-de-conclusao-md`).
- `31.5_Projeto_de_fase_Trilho_B/03_conexoes.md` — conexoes (CON; `f6-31-5-03-conexoes-md`).
- `31.5_Projeto_de_fase_Trilho_B/04_referencias.md` — referencias (REF; `f6-31-5-04-referencias-md`).
- `31.5_Projeto_de_fase_Trilho_B/00_escopo_e_regras.md` — project_scope (SCP; `f6-31-5-00-escopo-e-regras-md`).
- `31.5_Projeto_de_fase_Trilho_B/M01_escolha_contrato.md` — milestone (M01; `f6-31-5-m01-escolha-contrato-md`).
- `31.5_Projeto_de_fase_Trilho_B/C01_aceite.md` — acceptance_criteria (C01; `f6-31-5-c01-aceite-md`).
- `31.5_Projeto_de_fase_Trilho_B/M02_fatia_regra_tipo.md` — milestone (M02; `f6-31-5-m02-fatia-regra-tipo-md`).
- `31.5_Projeto_de_fase_Trilho_B/C02_aceite.md` — acceptance_criteria (C02; `f6-31-5-c02-aceite-md`).
- `31.5_Projeto_de_fase_Trilho_B/M03_jornada_teste_regra.md` — milestone (M03; `f6-31-5-m03-jornada-teste-regra-md`).
- `31.5_Projeto_de_fase_Trilho_B/C03_aceite.md` — acceptance_criteria (C03; `f6-31-5-c03-aceite-md`).
- `31.5_Projeto_de_fase_Trilho_B/M04_revisao_cobertura_entrega.md` — milestone (M04; `f6-31-5-m04-revisao-cobertura-entrega-md`).
- `31.5_Projeto_de_fase_Trilho_B/C04_aceite.md` — acceptance_criteria (C04; `f6-31-5-c04-aceite-md`).
- `31.5_Projeto_de_fase_Trilho_B/RUB_rubrica_marcos.md` — rubric (RUB; `f6-31-5-rub-rubrica-marcos-md`).
- `31.5_Projeto_de_fase_Trilho_B/CHK_checklist_final.md` — checklist (CHK; `f6-31-5-chk-checklist-final-md`).

## Estimativa por tipo e unidade

| Tipo | Arquivos |
|---|---:|
| acceptance_criteria | 8 |
| answer_key | 80 |
| answer_key_pratica | 15 |
| checklist | 2 |
| conexoes | 20 |
| criterio | 20 |
| flashcard | 6 |
| milestone | 8 |
| objetivo | 20 |
| practice | 52 |
| project_scope | 2 |
| quiz | 80 |
| referencias | 20 |
| resumo | 20 |
| rubric | 19 |
| theory | 57 |
| topic_index | 20 |
| **Total** | **449** |

| Unidade | Arquivos previstos |
|---|---:|
| 25.1 | 27 |
| 25.2 | 29 |
| 26.1 | 29 |
| 26.2 | 28 |
| 27.1 | 29 |
| 27.2 | 23 |
| 27.3 | 23 |
| 27.4 | 23 |
| 28.1 | 22 |
| 28.2 | 23 |
| 28.3 | 22 |
| 29.1 | 23 |
| 29.2 | 22 |
| 30.1 | 21 |
| 30.2 | 23 |
| 31.1 | 22 |
| 31.2 | 13 |
| 31.3 | 13 |
| 31.4 | 17 |
| 31.5 | 17 |

## Validações do rascunho

- YAML parseado com PyYAML 6.0.3; 20 unidades na ordem aprovada; 449 paths e IDs únicos.
- Teoria: 74 blocos de microtópicos originais atribuídos exatamente uma vez a 57 arquivos de teoria.
- Quiz: 80 questões com resposta em linha; cada Q tem um único arquivo físico de enunciado e um arquivo de gabarito separado.
- Práticas: 52 atividades convencionais mapeadas; 15 soluções existentes e 17 arquivos de rubrica prática (15 por atividade e duas rubricas comuns 0–4).
- Repertório: seis flashcards em arquivos próprios, cada enunciado/resposta permanece junto.
- Projetos: oito marcos, oito arquivos de aceite, duas rubricas comuns 0–4 e dois checklists finais.
- Itens compartilhados são associados a múltiplos assuntos, mas têm um só caminho físico em `90_integracao/`; aliases/referências são internos e únicos.
- Nenhuma unidade 8.4 ou árvore migrada foi criada. 31.4/31.5 são contêineres de projeto, não pastas de assuntos.
- Arquivos comuns contabilizados somente quando a seção original existe; paths no manifesto são relativos ao destino da Fase 6.

## Divergências e decisões para aprovação

- A previsão antiga de 90 questões não é sustentada pelas fontes atuais: 16 unidades de conteúdo possuem cinco questões cada = 80. Se houver uma versão/arquivo de quiz adicional fora da pasta ativa, ela não foi incluída porque não consta entre as fontes ativas.
- A contagem de 54 práticas também não corresponde às 52 atividades convencionais identificadas; os oito marcos dos dois projetos foram contados separadamente como marcos.
- A estimativa resulta em 449 arquivos estruturais sem arquivos artificiais. Pode mudar se a revisão aprovar outra divisão dos assuntos ou exigir arquivos adicionais para conteúdo com origem identificada.
- As divisões de assuntos, os mapas de itens e fronteiras curriculares precisam de aprovação antes de qualquer geração.
