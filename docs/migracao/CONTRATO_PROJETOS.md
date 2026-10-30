# Contrato proposto — projetos e componentes avaliativos

**Status: proposta; não implementada.** Preservar a estrutura do contrato intermediário e as fontes; não criar marcos ou requisitos.

## Entidades

### Projeto versionado

`ProjectVersion` deve manter `project_ref`, `unit_ref`, título, escopo integral, metadados, proveniência, hash, versão, estado de publicação, `has_formal_deliveries`, `has_formal_milestones`, lista de opções de stack, stack selecionada (incluindo `null`) e refs dos componentes. A versão é imutável depois de publicada; uma alteração cria nova versão e não apaga histórico.

### Entrega ou marco

`ProjectComponent` representa uma entrega ou marco **somente se existir na fonte**, com ID estável, tipo (`delivery`/`milestone`), título, corpo Markdown integral, ordem, refs de aceite, checklist, rubrica e conteúdo associado, mais proveniência/hash. Não converter uma entrega em marco nem criar marcos para os projetos sem marcos formais.

### Critérios e avaliação

- `AcceptanceCriteria`: itens e texto original, ID por item, ordem, rótulos de fonte e alvo exato (entrega/marco/prática). Cardinalidade e alvo devem validar.
- `ProjectChecklist`: itens e ordem; estado de aluno é separado do conteúdo curricular e associado a usuário, projeto/versão, componente e item.
- `Rubric`: alvo ou lista ordenada de alvos, dimensões, pesos, descritores, escala mínima/máxima e limiar se a fonte o trouxer. Não normalizar escalas diferentes nem inferir threshold.
- `ProjectDecision`, `ProjectScenario`, `ProjectReview`: tipos distintos com texto/contexto/ordem/referências originais. Perguntas de revisão não viram quiz automaticamente.
- `ProjectVariant`: opções de stack/variação e entregas associadas; `stack_selected=null` continua sem seleção.

Rubricas e critérios são entidades privadas/admin até que exista UI/API com autorização. A publicação do escopo do projeto não publica automaticamente respostas, notas de instrutor ou dados de correção.

## Estado encontrado

- 15 projetos; 20 entregas; 36 marcos formais.
- Nove projetos têm marcos formais; cinco têm entregas formais; um não tem entrega/marco formal.
- Os projetos não estão representados por entidade operacional correspondente no importador legado.
- Há 17 blocos de `acceptance_criteria`, 178 rubricas, 89 checklists, 130 critérios de conclusão, uma decisão, um cenário e uma revisão em blocos tipados, além das ligações nas 20 entregas/36 marcos.

## Publicação e interação propostas

1. Administração valida projeto/versão, componentes e referências antes de publicar.
2. API de aluno serve escopo e componentes liberados por allowlist, ordenados e sem campos privados.
3. Progresso de projeto é armazenado separado do conteúdo de autoria, com associação explícita à versão e ao contexto.
4. Aceites/checklists são apresentados como requisitos existentes; não se marcam automaticamente a partir de quiz/read progress.
5. Rubrica só produz avaliação quando houver avaliador/fluxo explícito; importar a rubrica não gera nota.
6. Uma versão atualizada preserva estado anterior e resultados; reconciliação de itens removidos é relatório pendente, não exclusão automática.

## Riscos e dependências

- Embutir tudo num documento Mongo pode ultrapassar limite/tornar atualizações concorrentes frágeis; usar coleção/componente separado ou snapshots com limite validado.
- Um serializer genérico pode expor rubrica/solução/nota instrutor.
- Perder `target_refs` multi-alvo altera o critério.
- Reordenação pode alterar relação entre entrega e tabela/aceite.
- Tratar `has_formal_milestones=false` como ausência de projeto é incorreto.
- Múltiplos stacks são alternativas disponíveis, não seleção para o aluno.

## Critérios de aceite futuros

Round-trip de texto/Markdown, ordem, todos os refs e alvos, escalas/limiares, opções nulas, projetos sem marcos, controle de acesso, serialização pública, progresso versionado e reimportação sem reset. Nenhum modelo de produção foi criado nesta etapa.
