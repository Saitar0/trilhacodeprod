# Homologação da migração estrutural — Fase 9

**Resultado: APROVADA COM RESSALVAS**  
**Commit-base:** `ccd2668cf3ba00ffc11c386fc5de26d917a854f0`  
**Branch:** `migracao-estrutura`

## Inventário e auditoria

- 16 unidades oficiais, 47 assuntos convencionais e dois contêineres de projeto.
- 301 arquivos migrados e 428 registros de mapeamento; 300 registros de conteúdo foram conferidos contra os trechos de origem e destino.
- 47 microtópicos, 25 quizzes e 25 gabaritos, 27 flashcards em 23 arquivos, 33 práticas e 24 arquivos de solução/feedback.
- Nove rubricas de prática e duas rubricas de projeto preservadas. Os projetos 46.2 e 46.3 mantêm quatro entregas e quatro blocos de aceite cada, com as rubricas originais de seis dimensões na escala 0–2.
- 46.2 preserva as opções de stack 42.1, 43.1, 44.1 e 45.1 e `stack_selecionada: null`; 46.3 preserva `stack_mode: principal`.
- Cobertura E/S/N: **38/9/0**. Os assuntos S-only permanecem associados a itens compartilhados existentes; nenhum exercício foi criado para preencher lacunas.

## Reprodução e preservação

- A reprodução isolada reconstruiu os mesmos 301 caminhos e conteúdos, verificados por SHA-256, sem sobrescrever a árvore existente.
- Foram validados 288 links Markdown relativos, sem avisos. Os três links ao guia de projetos apontam para o arquivo rastreado e preservam seus rótulos visíveis.
- As Fases 1–8, totalizando 2.285 arquivos, permaneceram intactas.
- Os 133 arquivos encontrados sob `Conteudos/` e o JSON permaneceram inalterados durante a geração e auditoria.
- Não foram encontrados diretórios separados de backup sob `Conteudos/` com nomes de arquivo, backup ou legado. Não se presume a existência de backups não localizados.
- A migração usou somente as fontes oficiais da Fase 9. As cópias 37.1 e 37.2 presentes na Fase 7 não foram usadas, alteradas ou declaradas aposentadas.

## Ressalva

A raiz do vault Obsidian continua sem confirmação. Nenhum wikilink da Fase 9 foi reescrito.

Nenhum commit da Fase 9, atualização do JSON, execução do importador ou início da Fase 10 foi realizado nesta homologação.
