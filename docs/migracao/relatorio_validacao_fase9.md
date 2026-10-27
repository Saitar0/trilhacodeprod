# Validação da migração estrutural — Fase 9

**Base:** `ccd2668cf3ba00ffc11c386fc5de26d917a854f0` · **branch:** `migracao-estrutura` · **resultado:** APROVADA COM RESSALVAS.

## Contagens reais

| Unidade | Arquivos |
|---|---:|
| 40.1 | 26 |
| 40.2 | 16 |
| 40.3 | 26 |
| 41.1 | 26 |
| 41.2 | 26 |
| 42.1 | 15 |
| 42.2 | 16 |
| 42.3 | 16 |
| 43.1 | 16 |
| 43.2 | 15 |
| 44.1 | 15 |
| 44.2 | 16 |
| 45.1 | 15 |
| 46.1 | 26 |
| 46.2 | 15 |
| 46.3 | 16 |
| **Total** | **301** |

| Tipo de arquivo | Quantidade |
|---|---:|
| `answer_key` | 25 |
| `answer_key_pratica` | 24 |
| `checklist` | 8 |
| `conexoes` | 16 |
| `criterio` | 15 |
| `flashcards` | 23 |
| `objetivo` | 16 |
| `practice` | 33 |
| `project_milestone` | 8 |
| `project_scope` | 2 |
| `quiz` | 25 |
| `referencias` | 16 |
| `resumo` | 16 |
| `rubric` | 11 |
| `theory` | 47 |
| `topic_index` | 16 |

## Cobertura e integridade

- 16 fontes oficiais ativas; 47 assuntos convencionais e dois contêineres de projeto.
- 47 blocos de teoria, 25 quizzes, 25 gabaritos, 27 flashcards em 23 arquivos, 33 práticas, 24 feedbacks/soluções, nove rubricas de prática, duas rubricas de projeto, oito entregas e oito aceites.
- Cobertura E/S/N: **38/9/0**; os nove assuntos S-only seguem vinculados apenas a avaliações compartilhadas existentes.
- `428` registros de origem→destino; cada faixa foi comparada com o texto real no offset correspondente. Nenhuma sobreposição nem trecho não estrutural omitido.
- 301 arquivos, 301 IDs únicos e sem colisão com os 2285 IDs das Fases 1–8.
- Projetos 46.2 e 46.3: quatro entregas, quatro aceites e rubrica original de seis dimensões/escala 0–2 em cada projeto. 46.2 mantém as quatro opções de stack e `stack_selecionada: null`; 46.3 mantém `stack_mode: principal`.
- 41.2: parágrafo introdutório preservado como contexto do assunto 01, sem contá-lo como microtópico adicional.
- 44 cabeçalhos estruturais sem arquivo próprio foram preservados no contexto de suas seções; não são blocos de conteúdo independentes.
- Metadados originais conferidos por unidade e transportados ao README; `nivel_dominio` e metadados de escolha de stack aparecem no README quando declarados no manifesto.

## Links e referências

- Links Markdown relativos resolvidos: **288**; wikilinks preservados sem reescrita: **0**.
- Três links para o guia rastreado foram normalizados no `href` relativo; os rótulos visíveis e o conteúdo de origem foram preservados.
- `consultado_em` não foi inferido: as referências foram copiadas literalmente das fontes; datas permanecem somente onde a fonte já as traz.
- O arquivo local não rastreado `Guia_de_Producao_de_Conteudo.md` não foi usado como destino nem incluído na árvore.

## Backups verificados

- Diretórios com nomes `Arquivo(s)`, `Backup(s)` ou `Legado(s)` encontrados: 0.
  - Nenhum.
- Arquivos sob esses diretórios incluídos no snapshot SHA-256: 0.
  - Nenhum arquivo separado de backup foi encontrado nesses diretórios.
- Todo o conteúdo sob `Conteudos/` foi verificado antes/depois; a lista acima identifica os subconjuntos reconhecidos pelo nome do diretório.

## Árvores protegidas

- Fases 1–8: 2285 arquivos, hashes iguais ao pré-voo.
- Fontes em `Conteudos/`, JSON, guia rastreado e oito documentos não rastreados preexistentes: hashes iguais ao pré-voo.
- Nenhum commit da Fase 9, importador ou Fase 10 foi executado.
