# Auditoria final — migração da Fase 1

## Resultado

**APROVADA COM RESSALVAS**

Não foram encontradas perdas, divergências textuais, duplicações de mapeamento ou arquivos fora do manifesto na árvore migrada. As ressalvas são operacionais: os wikilinks Obsidian não resolvem para uma árvore fora do vault configurado; e o checkout original já tinha alterações locais, inclusive no JSON, portanto seu diff não é um indicador de limpeza. A migração permaneceu no worktree isolado.

## Escopo e método

- Base isolada: `9b79751278496e51134a6ab8d495706bb2c700a7` (`origin/main`, branch `migracao-estrutura`).
- Destino auditado: `docs/courses/trilhacode/Conteudos_migrado/Fase_1/`.
- Fontes de controle: os dez Markdown originais, `docs/migracao/mapa_de_migracao.yml` e `docs/migracao/relatorio_mapeamento_fase1.csv`.
- Reextraí os blocos em memória, segundo o manifesto, e comparei o texto produzido com cada arquivo persistido. A comparação foi exata depois de normalizar somente finais de linha `CRLF`/`CR` para `LF`; nenhum arquivo migrado foi escrito ou corrigido durante esta auditoria.
- Conferi cada linha do CSV contra o bloco extraído da fonte, o destino físico, a contagem registrada e o SHA-256 do bloco. Também confirmei que o fragmento integral está no destino declarado.
- Comparei os blocos cercados de código como texto completo, incluindo delimitadores, linguagem e conteúdo.

## Resultado por unidade

| Unidade | Arquivos | Mapeamentos | Blocos de código | Resultado |
|---|---:|---:|---:|---|
| 1.1 | 28 | 33 | 4 | OK |
| 1.2 | 26 | 29 | 1 | OK |
| 2.1 | 23 | 28 | 3 | OK |
| 2.2 | 24 | 27 | 3 | OK |
| 2.3 | 22 | 27 | 1 | OK |
| 3.1 | 19 | 29 | 2 | OK |
| 3.2 | 21 | 27 | 3 | OK |
| 3.3 | 27 | 28 | 1 | OK |
| 3.4 | 13 | 23 | 0 | OK |
| 3.5 | 18 | 21 | 1 | OK |

Totais: **10 unidades**, **221 arquivos**, **272 mapeamentos únicos** e **19 blocos cercados de código**. Todos os blocos de código comparados coincidem integralmente.

## Cobertura textual e mapeamentos

- Os **272/272** registros têm origem e destino existentes e correspondem à extração textual e ao hash do bloco. Há **zero** chaves duplicadas `(unidade, bloco, tipo)` no CSV.
- Os arquivos persistidos correspondem exatamente aos **221** arquivos reconstruídos em memória a partir das fontes e do manifesto. Não há arquivo extra, vazio ou divergência de texto.
- Todas as seções Markdown de nível 2 das dez fontes foram contabilizadas: oito por unidade, exceto 3.5, que tem sete por ser projeto. Não há seção de conteúdo sem destino.
- Enunciados, alternativas, respostas, explicações, práticas, critérios, rubricas, escalas, checklists, marcos e referências mantêm o texto original. Os itens compartilhados aparecem uma vez em `90_integracao/`; suas associações ficam no manifesto/cobertura.
- As 221 frontmatters foram interpretadas pelo parser do subconjunto YAML usado nesses arquivos. Há **221 `arquivo_id` únicos**; os valores originais da unidade permanecem no README e os filhos não repetem `key`, `estimativa_minutos`, `tags` ou `status`.
- Os links Markdown relativos dos dez README resolvem para arquivos existentes. Os wikilinks de `03_conexoes.md` foram preservados.
- Não foi encontrado conteúdo didático inventado: os corpos persistidos coincidem com a reconstrução dos blocos das fontes. O texto adicional nos README limita-se ao índice estrutural e aos links previstos.

## Normalizações estruturais observadas

1. Para a comparação, normalizei apenas finais de linha `CRLF`/`CR` para `LF`; isso não altera caracteres ou palavras.
2. O frontmatter original fica no README com os campos estruturais de índice aprovados. Filhos recebem frontmatter estrutural próprio. Os README acrescentam títulos de índice e links, sem substituir os arquivos comuns separados.
3. Respostas, gabaritos de prática, rubricas e checklists existentes foram movidos para seus arquivos separados. Nos quizzes com resposta inline, o texto da resposta foi separado do enunciado; somente o espaço separador imediatamente anterior ao marcador `**Resposta:**` não é repetido entre os dois arquivos. Enunciado, alternativas, resposta e explicação foram preservados.
4. Foram removidas somente as três relações duplicadas previamente autorizadas: `3.1` relacionado a `2.1`; `3.4` relacionado a `3.3`; e `3.5` complementar a `3.3`. Os pré-requisitos permanecem. As linhas removidas estão transcritas em `docs/migracao/relatorio_validacao_fase1.md`.
5. Nenhum outro cabeçalho, bloco de código, frase, exercício, resposta, critério ou escala foi normalizado ou removido.

## Decisões específicas conferidas

- **3.1:** mantém `01_registrar_e_ignorar_mudancas` e `02_inspecionar_e_recuperar_com_seguranca`; o desafio P3 está uma vez em `90_integracao/`. Q2 sobre `git restore --staged` e seu gabarito estão no assunto de recuperação.
- **3.2:** P3 continua exclusivo de `01_integracao_e_mensagens_commit`. As ocorrências de `## Entregas` dentro de exemplos cercados de código permanecem no bloco e foram incluídas na comparação integral de fences.
- **3.5:** os quatro blocos de teoria permanecem juntos em `teoria_contexto.md`. Os quatro `titulo_marco` correspondem literalmente aos títulos da fonte; os aceites estão em checklists e a rubrica comum mantém a escala `0–4`.
- **Compartilhados:** Q5/P2 de 1.2, Q5 de 2.2 e os demais itens associados a vários assuntos estão uma vez no destino integrador previsto; não há classificação simultânea como exclusivo e compartilhado.

## Git e arquivos preservados

- No worktree isolado, `git diff` contra `HEAD` para `Conteudos/Fase_1/`, `Fase_1_Base_Tecnica.md` e `trilha-code-bulk-import.json` está vazio. Os dez arquivos de unidade, a nota de fase e o JSON mantêm os mesmos hashes registrados na validação anterior:

- `docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md` — `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`
- `docs/courses/trilhacode/Conteudos/Fase_1/1.2_Ambiente_de_desenvolvimento.md` — `d9cdab3f9c9f74478e0f37b121039d8d9d2edc9750353278df0efddc204939c4`
- `docs/courses/trilhacode/Conteudos/Fase_1/2.1_Terminal_e_navegacao.md` — `5c7110c2347f775afc8ab0e3a4fce883a5b7dbc00ba791b5426cc52c1ec6327a`
- `docs/courses/trilhacode/Conteudos/Fase_1/2.2_Sistema_e_operacao.md` — `6c8a57b957a2f70fac63b2b9793c3a1a434de195e8e652ff8d347dc85b3ee41c`
- `docs/courses/trilhacode/Conteudos/Fase_1/2.3_Acesso_remoto.md` — `9ca6dd0af3dab0233d8cfa3c49152fdb74414df715c883ac6973b8fc76b1b381`
- `docs/courses/trilhacode/Conteudos/Fase_1/3.1_Git_local.md` — `465ca7b27c44b8bba649ce353c17a0547ba10cbeaaa3de46e024889d16541bcd`
- `docs/courses/trilhacode/Conteudos/Fase_1/3.2_Trabalho_com_historico.md` — `13c21ed397d995d7532a7712edbeb94d78773f546db6de380a608fa9b78b7d59`
- `docs/courses/trilhacode/Conteudos/Fase_1/3.3_GitHub.md` — `1a72998bce31317b6695c25b9c73b69c7ac75b0d3a4d91eb48e1e947459d8b66`
- `docs/courses/trilhacode/Conteudos/Fase_1/3.4_Revisita_continua.md` — `ad3654fb1000aca42028e94e66e4d9180c525c920d72c770ad5fe531da5d9a3e`
- `docs/courses/trilhacode/Conteudos/Fase_1/3.5_Projeto_incremental.md` — `3bbd7f6d251ff137c8c84fb96ddb81f30f29d9f0f44fafada7beac7ad3032d51`
- `docs/courses/trilhacode/Fase_1_Base_Tecnica.md` — `1a8864461e5c97f7352048fddd308f8a4de2e7367589d6e3ea9342c035fa99ee`
- `docs/courses/trilhacode/trilha-code-bulk-import.json` — `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`

- O checkout original continua em `27a98964d55b96003fac70154178c5892da8d453`, na branch `codex/compose-ci-validation`; o destino `Conteudos_migrado/Fase_1/` não existe nele. Esse checkout já apresentava alterações locais antes da migração, incluindo uma modificação local no JSON; por isso, seu diff não é limpo e não o atribuo a esta migração. Não executei operações de escrita nele.
- Nenhum commit, troca de branch, alteração de referência, atualização do JSON ou execução do importador ocorreu nesta auditoria.

## Avisos e limitações

- **Obsidian:** o vault configurado está fora do repositório e contém uma cópia independente/antiga. Wikilinks foram preservados, mas não resolvem para a árvore migrada enquanto ela permanecer fora do vault. Os links Markdown relativos dos índices funcionam.
- **Checkout original:** as alterações locais anteriores, inclusive a edição do JSON, impedem afirmar que esse checkout coincide com `HEAD`; a confirmação de ausência de alterações da migração é baseada no isolamento de worktree, no destino ausente no checkout original e nos diffs vazios dos arquivos de origem/JSON no worktree isolado.
- Não há divergência crítica de conteúdo ou estrutura na árvore migrada.

