# Relatório de validação — migração estrutural da Fase 3

- Resultado: **APROVADA COM RESSALVAS** (ressalva conhecida: wikilinks Obsidian dependem da raiz do vault).
- Commit-base: `fba3a029f8956d349c430c797331b459733281f3`
- Branch: `migracao-estrutura`
- Unidades ativas: 14
- Assuntos: 42
- Questões: 59
- Práticas convencionais: 36
- Marcos de projeto: 8 (quatro em cada projeto)
- Arquivos no destino da Fase 3: 313
- Registros de mapeamento: 581

## Contagem por tipo

- `answer_key`: 39
- `answer_key_pratica`: 22
- `checklist`: 26
- `conexoes`: 14
- `criterio`: 14
- `milestone`: 8
- `objetivo`: 14
- `practice`: 36
- `project_scope`: 2
- `quiz`: 39
- `referencias`: 14
- `resumo`: 12
- `rubric`: 19
- `theory`: 40
- `topic_index`: 14

## Resultado por unidade

| Unidade | Assuntos | Arquivos | Mapeamentos | Integridade |
|---|---:|---:|---:|---|
| 6.1 | 4 | 26 | 47 | OK |
| 6.2 | 4 | 25 | 45 | OK |
| 6.3 | 4 | 25 | 45 | OK |
| 6.4 | 4 | 25 | 43 | OK |
| 7.1 | 4 | 25 | 44 | OK |
| 7.2 | 3 | 23 | 47 | OK |
| 7.3 | 2 | 18 | 47 | OK |
| 7.4 | 3 | 20 | 36 | OK |
| 7.5 | 2 | 20 | 47 | OK |
| 8.1 | 3 | 24 | 48 | OK |
| 8.2 | 3 | 24 | 49 | OK |
| 8.3 | 4 | 26 | 47 | OK |
| 8.5 | 1 | 16 | 18 | OK |
| 8.6 | 1 | 16 | 18 | OK |

## Validações

- O manifesto passou pelo parser YAML reutilizado do gerador homologado; chaves duplicadas e referências inconsistentes foram recusadas.
- Todos os segmentos de cada fonte foram reconstruídos, em ordem, por intervalos de caracteres sem lacunas nem sobreposições.
- Os blocos de código cercados são idênticos após normalização de CRLF/CR para LF; o BOM UTF-8 de leitura foi ignorado.
- Os 59 enunciados e 59 gabaritos de quiz, as 36 práticas e seus gabaritos, critérios e rubricas foram mapeados a partir de conteúdo existente.
- Os oito títulos literais de marcos, oito aceites, dois checklists finais e duas rubricas 0–4 foram conferidos diretamente nas fontes.
- A escala das rubricas de prática foi copiada dos metadados do manifesto; nenhum valor foi alterado.
- A resposta esperada de 6.1/P2 e o bloco `<details>` de 7.4/P2 foram separados por limites literais; a concatenação por intervalos reconstitui integralmente as atividades originais.
- Os READMEs mantêm os metadados originais e indexam apenas caminhos existentes; não há README por assunto.
- IDs `f3-*` únicos e sem colisão com os 365 IDs homologados das Fases 1 e 2.
- Não há pasta, arquivo ou nó 8.4; JSON de importação e importador não foram tocados.
- Fontes da Fase 3, documentos gerais e JSON foram comparados ao commit-base após normalização exclusiva de BOM e finais de linha.
- Hashes dos 365 arquivos homologados das Fases 1 e 2 permaneceram iguais: 53d56d8c758083f577fee9405643f3d56b41b2bf4db09d5363039ff9e6b6262f.

## Links relativos

- Todos os links Markdown relativos gerados resolvem para arquivos existentes.

## Limitações

- Wikilinks Obsidian foram preservados; a árvore migrada continua fora da raiz de vault confirmada, então alguns links externos podem não resolver nesta localização.
- O arquivo local preexistente `Guia_de_Producao_de_Conteudo.md` permaneceu fora do conteúdo gerado e inalterado.
- Nenhum commit foi criado; Fases 1 e 2, conteúdos originais e JSON permanecem inalterados.
