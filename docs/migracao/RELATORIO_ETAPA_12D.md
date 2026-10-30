# Relatório da Etapa 12D — contrato intermediário persistido

## Resultado

Conversão integral concluída. Duas execuções independentes, uma na ordem curricular e outra com ordem de leitura invertida, produziram 13 artefatos byte a byte idênticos. Saída: `docs/migracao/contrato_intermediario/`.

**Schema:** `trilhacode.intermediate/1.2`. **Base:** `147dc68b81169f66b0ba3802fa2f26e5130923a3`. **Branch:** `migracao-estrutura`.  
É contrato intermediário; não é o JSON definitivo do importador.

## Arquivos e contagens

Dez contratos (`fase_01.contract.json` a `fase_10.contract.json`), `source_mappings.json`, `diagnostics.json` e `integrity_manifest.json`: **13 arquivos**. Nenhum arquivo foi gravado em `Conteudos_migrado/`.

| Elemento | Total |
|---|---:|
| Arquivos migrados verificados | 2890 |
| Unidades ativas | 131 |
| Nós | 572 |
| Blocos | 3431 |
| Projetos | 15 |
| Colocações compartilhadas | 1001 |
| Relações | 55 |
| Pendências editoriais | 214 |
| IDs de entidades únicos | 5344 |
| SourceMappings | 2889 |
| Registros nos mapas de migração | 4311 |
| Destinos físicos únicos | 2879 |
| Arquivos estruturais fora dos destinos | 11 |
| Erros bloqueantes | 0 |

### Por fase

| Fase | Unidades | Arquivos | Nós | Blocos | Projetos | Colocações | Relações | Pendências |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fase_1 | 10 | 221 | 43 | 263 | 1 | 95 | 21 | 32 |
| Fase_2 | 7 | 144 | 27 | 189 | 0 | 95 | 9 | 15 |
| Fase_3 | 14 | 313 | 60 | 378 | 2 | 202 | 25 | 48 |
| Fase_4 | 17 | 395 | 77 | 508 | 2 | 205 | 0 | 19 |
| Fase_5 | 20 | 483 | 88 | 617 | 2 | 113 | 0 | 22 |
| Fase_6 | 20 | 449 | 85 | 503 | 2 | 100 | 0 | 23 |
| Fase_7 | 7 | 156 | 36 | 181 | 0 | 25 | 0 | 8 |
| Fase_8 | 8 | 124 | 25 | 143 | 2 | 15 | 0 | 11 |
| Fase_9 | 16 | 301 | 71 | 331 | 2 | 123 | 0 | 19 |
| Fase_10 | 12 | 304 | 60 | 318 | 2 | 28 | 0 | 17 |


### Blocos por tipo

| Tipo | Total |
|---|---:|
| `acceptance_criteria` | 17 |
| `answer_key` | 501 |
| `checklist` | 89 |
| `completion_criteria` | 130 |
| `feedback` | 181 |
| `flashcard` | 45 |
| `instructor_note` | 1 |
| `objective` | 131 |
| `practice` | 327 |
| `project_decision` | 1 |
| `project_review` | 1 |
| `project_scenario` | 1 |
| `quiz` | 506 |
| `reference` | 608 |
| `rubric` | 178 |
| `solution` | 212 |
| `summary` | 123 |
| `theory` | 379 |

## Reconciliação e integridade

Dos 4.311 registros de migração, 2.879 destinos físicos únicos existem; 11 arquivos estruturais autorizados ficam fora desses destinos. Há dois marcadores de remoção sem destino físico. O contrato representa 2.889 arquivos; a única exceção entre os 2.890 arquivos migrados é o índice `Conteudos_migrado/Fase_2/Projeto_incremental.md`, conforme decisão aprovada.

Os SHA-256 dos 2.890 arquivos migrados coincidem com `COBERTURA_CONVERSAO_12C1.csv`. Os 133 arquivos Markdown de `Conteudos/` não têm alterações rastreadas. O JSON legado `docs/courses/trilhacode/trilha-code-bulk-import.json` conserva SHA-256 `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`.

## Reprodutibilidade e manifesto

Os 13 caminhos e conteúdos foram comparados byte a byte entre as duas execuções. O manifesto contém os hashes dos demais artefatos:

- `diagnostics.json`: SHA-256 `10d9240a635fbdd7e1990706feef48a3b08d2b5e0f6e8d9e13faf17924756c8a`.
- `fase_01.contract.json`: SHA-256 `38d12a958c0bd31ec41f5b819068c15bcbcc6ad72fcf49943ddfc1f708256fa8`.
- `fase_02.contract.json`: SHA-256 `d91e01cd719bc7e2535ece8c3747fd3fcee410bb615d7052b34edd82f2799055`.
- `fase_03.contract.json`: SHA-256 `04864470f60e58e8c6f1a6767124860f93972fdeb1b972b605076481486ecd15`.
- `fase_04.contract.json`: SHA-256 `d3b537bb193e1526bcd76c8557453f59a67030827949b9e757ba2be072a0c8b5`.
- `fase_05.contract.json`: SHA-256 `5af9d81ee4ab283ed26fa90b45c1a8ddb46e70c4fa9deb5101148e763eb4e0dd`.
- `fase_06.contract.json`: SHA-256 `d77aef39a55f85dc2418e89b508e579e15b7bd1fa207d92a4f8e36d799eea15b`.
- `fase_07.contract.json`: SHA-256 `e7a7a5b04eea81d9d1ef43d0ab650bc431bd258875b7c5f7104d086a795b1a2e`.
- `fase_08.contract.json`: SHA-256 `7a715fed692684048f9c6928d2e7d2a56ae27459debc59f14a03d4bbbe6517ee`.
- `fase_09.contract.json`: SHA-256 `41a890c3d25c96b2d1b965c5cbfaf0807a71d2f65717032537ad8ad8008857ff`.
- `fase_10.contract.json`: SHA-256 `c3901af3f8884d31230e025e21ea41b8cb5cf8bdaf9714317d783027039e83f1`.
- `source_mappings.json`: SHA-256 `97dd5eb0f6f33cdc15d84bfaf9aca627dd25f6ce651d99a7bc3661d98b10f635`.

O manifesto exclui o próprio hash para evitar autorreferência; ele pode ser calculado externamente.

## Testes e limitações

A suíte 12A–12C.1 reportou 97 testes aprovados. Ruff, formatação, mypy, compilação Python e `git diff --check` aprovados no ambiente registrado em 12C.1 (Python 3.13.15, Pydantic 2.13.5, PyYAML 6.0.3, pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0). O conflito de dependências segue: `google-api-core==2.33.0` requer `grpcio-status>=1.75.1,<2`, mas `backend/requirements.txt` fixa `grpcio-status==1.71.2`; nenhuma dependência foi alterada.

Permanecem 214 pendências editoriais (wikilinks, referências sem destino, relações curriculares em prosa, guias e menções a 37.1/37.2 e 47.2/47.3). Nenhum destino foi inventado. Não houve geração do JSON definitivo, importador, acesso ao MongoDB ou alteração de plataforma.

## Git

HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`, branch `migracao-estrutura`; índice vazio e nenhum arquivo rastreado alterado. Novos artefatos: pasta do contrato, esta homologação técnica e este relatório. Sem commit.
