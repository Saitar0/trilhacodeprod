# Relatório — Etapa 14A: adaptador versionado de importação curricular

**Resultado: CONCLUÍDA PARCIALMENTE — validação offline aprovada; importação bloqueada por incompatibilidades explícitas.**

## Escopo e segurança

Implementado um leitor, validador estrutural e planejador determinístico para `trilhacode.import_bundle/1.0`. A execução permaneceu offline: não abriu conexão MongoDB, não executou migração, não chamou `/api/import/track`, não publicou conteúdo e não modificou progresso. O plano não propõe exclusões. Nenhuma resposta ou explicação protegida de gabarito é serializada no relatório.

O adaptador é código de validação e planejamento; não é um importador e não tem função que aplique operações ao banco. Uma comparação com estado existente só pode ser feita a partir de um snapshot fornecido pelo chamador; não há leitura automática do banco.

## Pré-voo e integridade da entrada

- Raiz/worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD-base: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice Git: vazio antes da execução. Já existiam alterações rastreadas e não rastreadas; foram preservadas.
- Pacote: `docs/courses/trilhacode/trilha-code-bulk-import.json`.
- Versão: `trilhacode.import_bundle/1.0`.
- SHA-256 do pacote: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- Hash do manifesto de integridade: `c3f5aa792641408eb66fc80cf801206de4e1deef2130a5a5c436c8d9ade58055`.
- Sidecars verificados: 12 de 12.
- JSON: o hash antes e depois da execução permaneceu `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`; o arquivo já estava modificado no working tree antes desta etapa e não foi editado por ela.

O pacote declara `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7` como hash da entrada JSON legada **anterior à conversão**. Esse valor é metadado histórico, não o hash do pacote completo atual; o hash atual corresponde ao valor esperado acima.

## Cobertura reconciliada

| Inventário | Resultado validado |
|---|---:|
| Fases | 10 |
| Arquivos migrados | 2.890 |
| Unidades/submódulos | 131 |
| Nós curriculares totais | 572 |
| Blocos tipados | 3.431 |
| Projetos | 15 |
| Entregas de projeto | 20 |
| Marcos formais | 36 |
| Colocações compartilhadas | 1.001 |
| Relações curriculares | 55 |
| IDs de entidades únicos | 5.344 |
| Pendências editoriais | 214 |
| Registros de origem no pacote | 2.889 |
| Hashes de arquivos de origem conferidos | 2.889 de 2.889 |
| Linhas dos relatórios de mapeamento das fases | 4.311 |
| Destinos físicos de migração únicos | 2.879 |
| Linhas sentinela de remoção previamente autorizada | 2 |
| Arquivos estruturais não representados como conteúdo | 11 |
| Fontes Markdown encontradas | 133 |
| Fontes distintas listadas nos relatórios | 131 |

Os 11 caminhos estruturais são os dez `README.md` da Fase 1 e `Conteudos_migrado/Fase_2/Projeto_incremental.md`. O pacote ainda carrega o índice estrutural aprovado da Fase 2 como artefato de integridade. Os dois arquivos adicionais encontrados em `Conteudos/Fase_7/` — `37.1_Servicos_gerenciados.md` e `37.2_Kubernetes_basico.md` — são cópias editoriais preservadas, não removidas nem importadas como unidades da Fase 7; as versões oficiais da Fase 8 são as fontes migradas.

Os 4.311 registros referem-se à soma das linhas nos dez relatórios de mapeamento. Os 2.889 registros no pacote são os registros consolidados de origem usados pelo bundle. As 2.879 referências de destino físico únicas e as duas sentinelas explicam a relação entre as contagens sem inferir um destino para duplicações autorizadas.

## Resultado do plano offline

As 5.344 entidades foram classificadas sem acesso a um snapshot do banco:

| Estado | Quantidade | Interpretação |
|---|---:|---|
| `pending_database_snapshot` | 2.063 | O esquema alvo aparenta suportar o conteúdo, mas criar/atualizar/inalterado/conflito depende de comparação autorizada com estado existente. |
| `blocked` | 3.016 | O modelo/fluxo atual não oferece representação ou caminho seguro sem extensão. |
| `pending_decision` | 265 | A semântica ou o destino requer decisão explícita. |
| `create` / `update` / `unchanged` / `conflict` | 0 | Nenhum desses estados foi afirmado sem snapshot. |

O estado do track, fora das 5.344 entidades, também permanece `pending_database_snapshot`. Os estados não autorizam execução. O relatório detalhado é [DRY_RUN_IMPORTACAO_14A.json](DRY_RUN_IMPORTACAO_14A.json), SHA-256 `42fd4ceb1691d3367961b68189019ebe5e3b1de764c3d21f72832b80b672cc87`.

### Bloqueios e decisões principais

- **Quizzes e gabaritos:** o bundle contém 506 quizzes; todos declaram `format: other` e zero alternativas. 501 requerem gabarito, mas os gabaritos armazenam resposta esperada em texto livre. O avaliador seguro atual exige múltipla escolha estruturada. Esses 501 pares estão bloqueados; cinco questões de revisão sem gabarito exigem decisão de produto. Os 501 gabaritos permanecem privados e o relatório contém apenas referências, nunca resposta, explicação ou hash do conteúdo privado.
- **Compartilhamento:** os 406 blocos canônicos ligados a 1.001 colocações não possuem modelo nativo de colocação curricular/contextual no importador atual. As colocações ficam bloqueadas; não são duplicadas.
- **Projetos:** os 15 projetos, 20 entregas e 36 marcos são estruturas tipadas no contrato, mas o importador e os modelos operacionais não oferecem entidade de projeto/componente compatível. Permanecem bloqueados, sem rebaixar critérios a texto genérico.
- **Outros blocos:** rubricas, critérios de conclusão, checklists, soluções/feedback, cenários, decisões, revisões e notas do instrutor exigem suporte semântico/visibilidade específico. Tipos desconhecidos falham fechados.
- **Relações:** 35 pré-requisitos marcados como enforced não declaram se exigem leitura concluída ou quiz aprovado. Permanecem `pending_decision`; não são convertidos para `quiz_passed`. As 16 relações complementares e quatro relacionadas são preservadas como relações, mas ainda dependem da comparação com o banco.
- **Referências:** 597 referências externas com URL/rótulo/texto coincidente têm transformação candidata para `external_link`, pendente de snapshot. 11 referências sem destino/renderização inequívocos permanecem pendentes. Wikilinks e guias sem destino não recebem resolução inventada.
- **Artefato estrutural:** o índice aprovado da Fase 2 está íntegro, mas o destino operacional para esse tipo de arquivo ainda requer decisão; não será publicado como conteúdo de aluno.
- **Identidade:** `meta.import_ref` já é utilizado por nós e blocos no importador legado, mas não há índice único comprovado para as chaves externas. Os IDs curriculares não são tratados como `ObjectId`; a resolução e a garantia de unicidade exigem extensão planejada antes de qualquer escrita.

## Implementação e evidências da plataforma

- Adaptador: `backend/curriculum_contract/import_adapter.py`.
- Testes novos: `backend/unit_tests/test_curriculum_import_adapter.py`.
- Plano estruturado: `docs/migracao/DRY_RUN_IMPORTACAO_14A.json`.
- O bundle validado é definido em `backend/curriculum_contract/bulk_import.py`; a validação de semântica curricular usa `backend/curriculum_contract/validation.py`.
- `backend/import_payload.py::validate_import_shape` rejeita qualquer payload com `schema_version`, com mensagem para usar adaptador explícito. A rota legada está em `backend/routes_import.py`; seu serviço `backend/services/imports.py` consulta o banco para planejar, faz upsert de nós/blocos e não entende o bundle versionado. Nenhuma dessas rotas foi chamada.
- Os nós e blocos de produção usam documentos genéricos (`backend/schemas/content.py`, `backend/services/nodes.py`, `backend/services/blocks.py`). A lista de tipos seed está em `backend/seed.py`; isso não equivale a suporte a todos os tipos do contrato.
- A API segura de quizzes está em `backend/routes_quizzes.py` e `backend/services/quizzes.py`. O parser atual rejeita formato diferente de `multiple_choice`, ausência de opções e gabarito não avaliável. A leitura comum de blocos filtra campos de resposta em `backend/services/nodes.py`, por isso não é um destino aceitável para gabaritos importados.
- Relações tipadas no produto têm `prerequisite_kind` opcional em `backend/schemas/content.py` e validação em `backend/services/relations.py`/`backend/learning.py`. O pacote não dá evidência suficiente para preencher esse campo para as 35 relações enforced.

## Verificações executadas

Ambiente local Windows, Python 3.13, Pydantic 2.13.5, PyMongo 4.17.0. Nenhum serviço ou banco foi iniciado.

- `python -m pytest unit_tests/test_curriculum_import_adapter.py unit_tests/test_curriculum_bulk_import.py unit_tests/test_curriculum_contract.py -q` — **67 passaram**.
- `ruff check curriculum_contract/import_adapter.py unit_tests/test_curriculum_import_adapter.py` — passou.
- `ruff format --check curriculum_contract/import_adapter.py unit_tests/test_curriculum_import_adapter.py` — passou.
- `mypy --explicit-package-bases --namespace-packages curriculum_contract/import_adapter.py unit_tests/test_curriculum_import_adapter.py` — passou, sem erros.
- `python -m py_compile curriculum_contract/import_adapter.py unit_tests/test_curriculum_import_adapter.py` — passou.
- Execução real do módulo para ler/validar o bundle e criar o relatório — passou.
- Hash reportado, integridade de sidecars, mapeamentos, destino estrutural e hash de origem — passaram.
- Nenhum teste Mongo/API/E2E foi executado: esta etapa não contém escrita e o modo offline não requer banco.
- `git diff --check` será registrado no fechamento final, após os documentos desta etapa.

## Arquivos desta etapa

- Criado: `backend/curriculum_contract/import_adapter.py`.
- Criado: `backend/unit_tests/test_curriculum_import_adapter.py`.
- Criado: `docs/migracao/DRY_RUN_IMPORTACAO_14A.json`.
- Criados: `docs/migracao/RELATORIO_ETAPA_14A.md`, `docs/migracao/PLANO_DRY_RUN_IMPORTACAO.md` e `docs/migracao/MATRIZ_COMPATIBILIDADE_IMPORTADOR.md`.
- Não foram alterados os schemas de produção, importador, contrato intermediário persistido, árvores curriculares ou conteúdo JSON por esta etapa.

## Parecer e próxima etapa

**Validação estrutural: aprovada. Plano de importação: não pronto para execução.** A plataforma atual não pode representar/importar sem perda quizzes de resposta textual, gabaritos privados, colocações compartilhadas e componentes de projeto. Além disso, a semântica de relações enforced permanece pendente. A próxima etapa recomendada é especificar e homologar as extensões de modelo/API e os contratos de privacidade/identidade; depois, comparar contra snapshot sanitizado autorizado e repetir o dry-run. Importação real requer autorização separada.
