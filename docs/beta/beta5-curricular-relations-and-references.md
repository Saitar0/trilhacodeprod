# Beta 5 — relações curriculares e referências completas

## Relações

`beta_curricular_metadata.py` distingue relação interna ao lote, alvo externo ainda não carregado e referência de origem não resolvida. Preserva categoria textual, caminho, âncora, rótulo e IDs. Alvos externos ou não resolvidos não podem ser marcados como enforcement. Relações extraídas não se convertem automaticamente em pré-requisitos.

O lote da Fase 1 contém 30 relações no inventário Beta 4. O staging as registra tipadamente; a validação de escopo não afirma que todos os destinos externos foram carregados. Unidade externa é pendência, não erro de origem.

## Referências

Referências tipadas mantêm título, descrição, URL, ordem, origem, unidade/tópico e hash de proveniência. A Beta 4 contou 39 referências. Não houve requisição a URLs nem cópia de conteúdo externo. O backend atual permanece sem destino tipado demonstrado para descrições completas; a transformação operacional necessita adaptador e teste do leitor.
