# Auditoria da migração estrutural — Fase 1

- Base Git: `9b79751278496e51134a6ab8d495706bb2c700a7`
- Branch isolada: `migracao-estrutura`
- Destino: `docs/courses/trilhacode/Conteudos_migrado/Fase_1/`
- Unidades: 10
- Arquivos criados: 221
- Blocos mapeados: 272
- JSON: não modificado nem importado.

## Tipos de arquivo

- `answer_key`: 30
- `answer_key_pratica`: 16
- `checklist`: 14
- `conexoes`: 10
- `criterio`: 10
- `milestone`: 4
- `objetivo`: 10
- `practice`: 26
- `project_brief`: 1
- `quiz`: 30
- `referencias`: 10
- `resumo`: 10
- `rubric`: 10
- `theory`: 30
- `topic_index`: 10

## Integridade por unidade

| Unidade | Palavras origem | Palavras migradas | Remoção aprovada | Arquivos | Blocos mapeados | Resultado |
|---|---:|---:|---:|---:|---:|---|
| 1.1 | 2711 | 2711 | 0 | 28 | 33 | OK |
| 1.2 | 1773 | 1773 | 0 | 26 | 29 | OK |
| 2.1 | 1568 | 1568 | 0 | 23 | 28 | OK |
| 2.2 | 1672 | 1672 | 0 | 24 | 27 | OK |
| 2.3 | 1654 | 1654 | 0 | 22 | 27 | OK |
| 3.1 | 1724 | 1712 | 12 | 19 | 29 | OK |
| 3.2 | 1627 | 1627 | 0 | 21 | 27 | OK |
| 3.3 | 1715 | 1715 | 0 | 27 | 28 | OK |
| 3.4 | 1042 | 1034 | 8 | 13 | 23 | OK |
| 3.5 | 1393 | 1385 | 8 | 18 | 21 | OK |

## Validações

- Todos os caminhos declarados e os arquivos comuns esperados estão presentes; nenhum destino extra foi gerado.
- Cada fragmento registrado no CSV foi encontrado no arquivo físico mapeado.
- Itens compartilhados têm um destino físico em `90_integracao/`; cobertura e slugs conferem com o manifesto.
- Frontmatter é YAML parseável; `arquivo_id` é único; valores originais permanecem no README e metadados de unidade não se repetem nos filhos.
- Todos os links Markdown relativos de README resolvem dentro da unidade.
- Contagem de palavras por unidade coincide; a diferença registrada corresponde apenas às relações duplicadas aprovadas.
- SHA-256 de cada unidade original, da nota de fase e do JSON permaneceu inalterado.
- O importador não foi executado; nenhuma escala de rubrica foi alterada.

## Links Obsidian

O vault configurado é externo ao repositório e contém uma cópia antiga independente da Fase 1. Os wikilinks de origem foram preservados em `03_conexoes.md`; eles não resolvem para esta árvore enquanto ela ficar fora do vault. Os links do README são relativos ao repositório e foram validados.

## Remoções estruturais aprovadas

- 3.1: removida somente a relação duplicada com 2.1; manteve-se o pré-requisito. Linha removida: `- Relacionado: [[Fase_1_Base_Tecnica#2.1 — Terminal e navegação|2.1 — Terminal e navegação]]`
- 3.4: removida somente a relação duplicada com 3.3; manteve-se o pré-requisito. Linha removida: `- Relacionado: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3 — GitHub]]`
- 3.5: removida somente a relação complementar duplicada com 3.3; manteve-se o pré-requisito. Linha removida: `- Complementar: [[Fase_1_Base_Tecnica#3.3 — GitHub|3.3 — GitHub]]`

## Hashes de controle

- `docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md`: `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/1.2_Ambiente_de_desenvolvimento.md`: `d9cdab3f9c9f74478e0f37b121039d8d9d2edc9750353278df0efddc204939c4` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/2.1_Terminal_e_navegacao.md`: `5c7110c2347f775afc8ab0e3a4fce883a5b7dbc00ba791b5426cc52c1ec6327a` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/2.2_Sistema_e_operacao.md`: `6c8a57b957a2f70fac63b2b9793c3a1a434de195e8e652ff8d347dc85b3ee41c` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/2.3_Acesso_remoto.md`: `9ca6dd0af3dab0233d8cfa3c49152fdb74414df715c883ac6973b8fc76b1b381` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/3.1_Git_local.md`: `465ca7b27c44b8bba649ce353c17a0547ba10cbeaaa3de46e024889d16541bcd` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/3.2_Trabalho_com_historico.md`: `13c21ed397d995d7532a7712edbeb94d78773f546db6de380a608fa9b78b7d59` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/3.3_GitHub.md`: `1a72998bce31317b6695c25b9c73b69c7ac75b0d3a4d91eb48e1e947459d8b66` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/3.4_Revisita_continua.md`: `ad3654fb1000aca42028e94e66e4d9180c525c920d72c770ad5fe531da5d9a3e` (inalterado)
- `docs/courses/trilhacode/Conteudos/Fase_1/3.5_Projeto_incremental.md`: `3bbd7f6d251ff137c8c84fb96ddb81f30f29d9f0f44fafada7beac7ad3032d51` (inalterado)
- `docs/courses/trilhacode/Fase_1_Base_Tecnica.md`: `1a8864461e5c97f7352048fddd308f8a4de2e7367589d6e3ea9342c035fa99ee` (inalterado)
- `docs/courses/trilhacode/trilha-code-bulk-import.json`: `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7` (inalterado)

O mapeamento por bloco está em `docs/migracao/relatorio_mapeamento_fase1.csv`.
