# Validação da migração estrutural — Fase 10

**Base:** `2f3d8977e7d6c7a74e5f11abc4dec7e66660bc4d` · **branch:** `migracao-estrutura` · **resultado técnico:** APROVADA COM RESSALVAS.

## Contagens conferidas

| Unidade | Assuntos | Arquivos | Tipos |
|---|---:|---:|---|
| 47.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 48.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 48.2 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 49.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 50.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 51.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 52.1 | projeto | 17 | `{"checklist": 5, "conexoes": 1, "criterio": 1, "objetivo": 1, "project_milestone": 4, "project_scope": 1, "referencias": 1, "resumo": 1, "rubric": 1, "topic_index": 1}` |
| 52.2 | projeto | 17 | `{"checklist": 5, "conexoes": 1, "criterio": 1, "objetivo": 1, "project_milestone": 4, "project_scope": 1, "referencias": 1, "resumo": 1, "rubric": 1, "topic_index": 1}` |
| 53.1 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 53.2 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 53.3 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |
| 53.4 | 4 | 27 | `{"answer_key": 5, "answer_key_pratica": 3, "conexoes": 1, "criterio": 1, "objetivo": 1, "practice": 3, "quiz": 5, "referencias": 1, "resumo": 1, "rubric": 1, "theory": 4, "topic_index": 1}` |

| Tipo | Quantidade |
|---|---:|
| `answer_key` | 50 |
| `answer_key_pratica` | 30 |
| `checklist` | 10 |
| `conexoes` | 12 |
| `criterio` | 12 |
| `objetivo` | 12 |
| `practice` | 30 |
| `project_milestone` | 8 |
| `project_scope` | 2 |
| `quiz` | 50 |
| `referencias` | 12 |
| `resumo` | 12 |
| `rubric` | 12 |
| `theory` | 40 |
| `topic_index` | 12 |

- 12 fontes oficiais: dez unidades convencionais e projetos 52.1/52.2; 40 assuntos convencionais.
- 50 quizzes com gabaritos separados; 30 práticas com feedback; nenhum flashcard.
- Dez rubricas de prática em escala 0–4; duas rubricas de projeto em escala 0–2; oito entregas/aceites.
- E/S/N: **36/4/0**. Assuntos S-only: 51.1/`01_ativos_fronteiras_confianca`, 53.1/`04_selecao_apresentacao_evidencias`, 53.3/`01_requisitos_e_delimitacao`, 53.4/`01_entender_problema_antes_codificar`.
    - 406 registros de origem/destino: 84 conversões de metadados e 322 registros de conteúdo. Texto de cada segmento conferido contra offsets da fonte.
- Cobertura auditada: 127,483 de 127,906 caracteres fonte; cabeçalhos de seção restantes são contêineres estruturais mapeados por seus descendentes.

## Projetos

- 52.1: quatro entregas/aceites, checklist de 10 itens, rubrica original de oito dimensões/0–2 e limiar **13/16** preservados.
- 52.2: quatro entregas/aceites, três variações T6, checklist de 8 itens, rubrica original de seis dimensões/0–2 e limiar **10/12** preservados; nenhuma stack selecionada.

## Links e referências

- Links Markdown relativos resolvidos: **294**; avisos: **0**; wikilinks preservados: **0**.
- Normalizações estruturais autorizadas:
- `52.1`: `../../Guia_Projetos_e_Rotacao_de_Tipos.md` → `../../../Guia_Projetos_e_Rotacao_de_Tipos.md`; alvo `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md` rastreado; rótulo visível preservado.
- `52.2`: `../../Guia_Projetos_e_Rotacao_de_Tipos.md` → `../../../Guia_Projetos_e_Rotacao_de_Tipos.md`; alvo `docs/courses/trilhacode/Guia_Projetos_e_Rotacao_de_Tipos.md` rastreado; rótulo visível preservado.
- 47.1 menciona 47.2/47.3 em texto simples; não foram encontradas fontes/destinos correspondentes nem links Markdown. A menção foi preservada sem criar unidades fictícias.
- `consultado_em` foi mantido por referência somente quando presente na fonte; nenhuma data foi inferida.

## Integridade protegida

- Fases 1–9: 2586 arquivos com hashes SHA-256 idênticos ao pré-voo.
- `Conteudos/`: 133 arquivos verificados; JSON, página e referências gerais da Fase 10 e documentos locais preexistentes preservados.
- Diretórios de backup reconhecidos sob `Conteudos/`:
- Nenhum diretório de backup/legado com nome reconhecido encontrado sob `Conteudos/`.
- Arquivos efetivamente encontrados nesses diretórios:
- Nenhum arquivo separado foi encontrado dentro desses diretórios.

## Reprodução isolada

- Reconstrução em diretório temporário: **idêntica**; 304 arquivos, caminhos relativos idênticos, conteúdo SHA-256 idêntico.
- O manifesto declara 304 caminhos; não foram criados arquivos artificiais.
