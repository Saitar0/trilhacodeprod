# Relatório — Etapa 14B: contratos de compatibilidade para importação

## Resultado

**Especificação concluída para revisão; sem implementação de produção e sem importação.** O pacote `trilhacode.import_bundle/1.0` foi reconciliado com o dry-run da Etapa 14A. Os contratos aqui são propostas: decisões marcadas como `[PROPOSTA]` não foram aplicadas ao pacote, ao banco ou às relações curriculares.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch/HEAD: `migracao-estrutura` / `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice Git: vazio. O working tree já continha alterações rastreadas e não rastreadas; elas foram mantidas.
- Pacote: `docs/courses/trilhacode/trilha-code-bulk-import.json`.
- SHA-256 verificado: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- Dry-run consultado: `docs/migracao/DRY_RUN_IMPORTACAO_14A.json`, SHA-256 `42fd4ceb1691d3367961b68189019ebe5e3b1de764c3d21f72832b80b672cc87`.
- Reconciliação: 5.344 operações/entidades no detalhe do dry-run — 3.016 `blocked`, 2.063 `pending_database_snapshot` e 265 `pending_decision`; nenhuma operação de criação/atualização foi afirmada sem snapshot.
- Nenhuma consulta ao MongoDB; nenhum arquivo curricular, contrato intermediário ou JSON foi modificado.

## Reconciliação dos bloqueios e pendências

| Estado do dry-run | Quantidade | Composição |
|---|---:|---|
| `blocked` | 3.016 | 1.002 entidades de quiz/gabarito; 1.001 colocações; 71 entidades de projeto; 942 outros blocos tipados. |
| `pending_decision` | 265 | 214 pendências editoriais (148 referências sem destino e 66 dependentes da raiz Obsidian); 35 relações; 11 referências em bloco; cinco perguntas de revisão sem gabarito. |
| `pending_database_snapshot` | 2.063 | 572 nós; 1.471 blocos compatíveis candidatos (379 theory, 123 summary, 327 practice, 45 flashcard e 597 referências externas); 20 relações informativas/de associação (16 complementares e quatro relacionadas); nenhum classificado por estado do banco. |
| `create/update/unchanged/conflict` | 0 | Nenhum snapshot foi consultado nem fornecido. |

Os 3.016 bloqueios por causa são detalhados na [matriz de compatibilidade da 14A](MATRIZ_COMPATIBILIDADE_IMPORTADOR.md) e, por entidade, em `DRY_RUN_IMPORTACAO_14A.json`. A seção “Inventário dos bloqueios” desta entrega discrimina tipos, contagem, risco, dependências e critério de resolução sem ocultar o ID individual que permanece no relatório estruturado.

### Composição dos 3.016 bloqueios

Cada linha agrupa somente entidades com o mesmo tipo/código de causa; IDs, arquivos e códigos individuais continuam rastreáveis em `DRY_RUN_IMPORTACAO_14A.json` (`operations_detail`). A extensão proposta é necessária, mas não autorizada nesta etapa.

| Tipo/causa | Entidades | Modelo ausente ou incompatibilidade | Extensão necessária | Risco de perda | Dependência | Critério para resolver |
|---|---:|---|---|---|---|---|
| `quiz` textual `other` sem opções | 501 | O avaliador operacional aceita múltipla escolha, não o formato textual do pacote. | Tipo de questão e política de correção/revisão compatíveis com o texto-fonte. | Correção por regra inventada ou publicação de quiz não avaliável. | Decisão de produto sobre resposta textual; parser que preserve Markdown e refs. | Round-trip dos enunciados; regra explícita por formato; qualquer ambiguidade bloqueia publicação. |
| `answer_key` privado sem caminho de importação | 501 | Não há destino curricular privado versionado associado à importação. | Armazenamento privado, vínculo 1:1, serializer allowlist e versão imutável. | Vazamento de resposta/explicação ou perda de vínculo. | Modelo privado, autorização e endpoints seguros. | Cada chave aponta para questão/versão exatas; chave ausente de payloads e logs antes da autorização. |
| `shared_placement` | 1.001 | Não existe modelo nativo de colocação contextual para bloco canônico. | Entidade canônica + colocação, ordenação contextual e refs. | Duplicação ou perda de associação/progresso. | Decisão humana de progresso; índice único e plano de reconciliação. | 406 refs canônicas e 1.001 placements resolvidas; cada placement tem assunto/ordem; sem clones indevidos. |
| `project` | 15 | Não existe entidade/serviço operacional de projeto curricular tipado no importador. | Projeto versionado, escopo, opções/variações e publicação autorizada. | Perda de escopo, opções ou identidade. | Contrato de projeto e UI/API apropriada. | Round-trip de refs, texto, estado e opções; nenhum projeto publicado parcialmente. |
| `project_delivery` | 20 | Entregas não são entidades de primeira classe no modelo atual. | Componente com ordem, Markdown integral e refs de aceite. | Perda de texto, ordem ou vínculo com aceite. | Serviço/modelo de projeto e validação de refs. | 20 entregas preservadas e ligadas aos alvos originais. |
| `project_milestone` | 36 | Marcos formais não têm representação operacional e não podem ser inferidos para todos os projetos. | Componente `milestone` somente quando presente na fonte. | Criar etapas inexistentes ou perder associação. | Modelo de componente e validação de proveniência. | 36 marcos com origem/ordem comprovadas; projetos sem marcos continuam sem marcos. |
| `rubric` | 178 | Não há schema/importação tipada suficiente para dimensões, alvos e descritores. | Rubrica com alvos ordenados, dimensões, escalas e limiar apenas se explícito. | Perda de escala, descritor, alvo múltiplo ou limiar. | Schema/API e apresentação administrativa autorizada. | Alvos resolvidos; escalas e limiares idênticos à fonte; nenhuma nota criada pelo importador. |
| `completion_criteria` | 130 | Critérios não têm tipo operacional; conclusão não pode ser inferida livremente do texto. | Tipo com ordem, texto integral, alvo e condições documentadas. | Aprovação automática não autorizada ou critério apagado. | Decisão semântica e modelo de progresso aprovado. | Texto/alvo preservados; nenhuma regra de aprovação inferida; leitura e avaliação testadas separadamente. |
| `checklist` | 89 | Item e estado de checklist não têm representação curricular contextual comprovada. | Itens estáveis e ordenados separados do estado do aluno. | Perder identidade/ordem ou misturar conteúdo com progresso. | Modelo tipado e política contextual aprovada. | Round-trip dos itens; estado do usuário separado; importação não os marca concluídos. |
| `acceptance_criteria` | 17 | Critérios não têm associação tipada e garantida ao alvo correto. | Critério ordenado ligado a entrega, marco ou prática. | Critério se soltar do alvo correto. | Modelos de projeto/prática e cardinalidade validada. | Todo alvo existe e corresponde à proveniência; associação ambígua bloqueia. |
| `objective` | 131 | Não há destino semântico nativo comprovado para objetivos. | Tipo de objetivo ou regra editorial aprovada por uso. | Objetivo virar texto genérico ou perder ordem. | Mapeamento tipado ou decisão editorial. | Cada objetivo tem destino aprovado e preserva texto/proveniência. |
| `solution` | 212 | Solução não tem relação/visibilidade privada de prática no importador. | Solução versionada vinculada à prática, com autorização separada. | Expor solução ou perder relação. | Modelo privado, controle de acesso e política de revelação. | 212 soluções resolvem prática/versão e não aparecem em payload público indevido. |
| `feedback` | 181 | Feedback não tem alvo, audiência e revelação suficientemente modelados. | Tipo com alvo, contexto, audiência e ordem conforme a fonte. | Exposição indevida ou associação à atividade errada. | Contrato de feedback e serializers autorizados. | Alvo/audiência resolvidos; acesso público somente sob regra explícita. |
| `instructor_note` | 1 | Leitura genérica de bloco não garante audiência exclusiva do instrutor. | Tipo administrativo fail-closed, fora do payload de aluno. | Vazamento de nota interna. | Controle de audiência e teste de serialização. | Ausência comprovada em endpoints, erros, logs e OpenAPI públicos. |
| `project_decision` | 1 | Decisão não é distinta de conteúdo comum no modelo operacional. | Tipo próprio que preserve opções sem impor escolha. | Alternativa apresentada como obrigatória. | Modelo/UI de decisão e decisão de produto. | Texto/opções em round-trip; nenhuma escolha selecionada automaticamente. |
| `project_scenario` | 1 | Cenário não tem estrutura tipada de contexto/condições. | Tipo próprio com descrição, condições e relações. | Omitir condições ou confundi-las com decisão. | Modelo de cenário e renderer. | Conteúdo integral preservado e distinto de uma decisão. |
| `project_review` | 1 | Revisão pode ser interpretada incorretamente como avaliação. | Tipo de revisão não avaliativa separado de quiz/gabarito. | Criar correção ou requisitos inexistentes. | Decisão de produto e suporte sem pontuação. | Perguntas preservadas sem score/gabarito artificial e sem satisfazer `quiz_passed`. |

### Composição das 265 pendências

| Pendência | Quantidade | Tratamento proposto |
|---|---:|---|
| Pendências editoriais `unresolved_reference` | 148 | Manter sem destino inventado; decisão editorial por referência. |
| Pendências `obsidian_vault_root_unknown` | 66 | Preservar wikilinks, não resolver até confirmar raiz do vault. |
| Pré-requisitos `enforced` sem subtipo explícito | 35 | Aprovar semântica individualmente; nenhuma conversão automática. |
| Referências em blocos sem destino/renderização inequívoca | 11 | Resolver o destino ou manter como texto pendente. |
| Perguntas sem gabarito (R1–R5 de 16.3) | 5 | Preservar como perguntas de revisão, sem resposta ou nota inventada. |

As 35 relações, com origem, destino, título, trecho literal, hash de proveniência e classificação proposta individual, estão na seção de relações da [Matriz de decisões curriculares](MATRIZ_DECISOES_CURRICULARES.md). As cinco perguntas sem gabarito estão listadas em [Contrato de quizzes](CONTRATO_QUIZZES_IMPORTACAO.md).

## Propostas e decisões pendentes

- `[PROPOSTA]` Para os 34 vínculos cuja fonte diz literalmente `Pré-requisito` e cujo pacote marca `kind=prerequisite` e `enforced=true`, considerar `content_completed` como candidato compatível com a semântica legada, sujeito a aprovação humana. A fonte não fala em aprovação de quiz; portanto não propor `quiz_passed` para esses vínculos.
- A relação de 7.4 que combina “pré-requisito/revisita” permanece ambígua; não classificar até decisão editorial.
- `[PROPOSTA]` Progresso de conteúdo compartilhado independente por colocação (`per_context`). As 1.001 colocações estão `undecided`; nenhuma recebe essa política até aprovação.
- Os 501 quizzes com gabarito textual não devem entrar no avaliador atual nem receber alternativas ou critérios gerados. Definir um fluxo de resposta textual/manual ou conservar como material não avaliativo depende de decisão de produto.
- O destino e o acesso das notas do instrutor, soluções e rubricas permanecem dependentes de privacidade/funcionalidade explícita.
- Não consultar MongoDB nem inferir estados de sincronização. Não excluir automaticamente registro ausente no pacote.

## Arquivos desta etapa

- `docs/migracao/RELATORIO_ETAPA_14B.md`
- `docs/migracao/CONTRATO_QUIZZES_IMPORTACAO.md`
- `docs/migracao/CONTRATO_CONTEUDO_COMPARTILHADO.md`
- `docs/migracao/CONTRATO_PROJETOS.md`
- `docs/migracao/MATRIZ_DECISOES_CURRICULARES.md`
- `docs/migracao/PLANO_EXTENSOES_IMPORTADOR.md`

## Verificações e parecer

O pacote e o relatório da 14A foram lidos localmente; a contagem e a composição acima foram recalculadas das entidades/estados do dry-run. Não foram criados testes ou código porque esta entrega especifica contratos, sem mudar implementação. Não se executaram ferramentas de lint/teste nem conexão de banco.

**Parecer:** documentação concluída para homologação. A implementação do importador continua bloqueada até aprovação das decisões de produto/editoriais e implementação testada dos suportes ausentes. Nenhuma escrita ou commit foi realizado.
