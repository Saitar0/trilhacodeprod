# Auditoria final — Fase 10

**Veredito técnico: APROVADA COM RESSALVAS**

## Integridade textual e cobertura

- As 12 fontes ativas foram validadas por SHA-256 e metadados antes da construção.
- 406 registros têm origem e destino real; o conteúdo foi comparado por segmento e faixa de origem, não apenas por contagens de palavras.
- 40 microtópicos, 50 pares quiz/gabarito, 30 práticas/feedbacks, dez rubricas práticas, duas rubricas de projeto, oito entregas e oito aceites preservados.
- Q/K recompõe a linha original nos itens rotulados como `Resposta` e nos itens 53.2–53.4 cuja resposta começa após o sinal de pergunta; os enunciados, alternativas e respostas permanecem literais.
- Itens compartilhados ocupam um destino físico único em `90_integracao/`; E/S/N permanece 36/4/0.
- Blocos de código e exemplos foram transportados dentro dos segmentos literais, sem reescrita.

## Projetos e links

- 52.1: 4 entregas, 4 aceites, checklist 10, rubrica original 0–2, limiar 13/16.
- 52.2: 4 entregas, 4 aceites, 3 variações T6, checklist 8, rubrica original 0–2, limiar 10/12.
- Links Markdown relativos: 294 resolvidos; 0 avisos; 0 wikilinks mantidos.
- 2 hrefs para `Guia_Projetos_e_Rotacao_de_Tipos.md` foram normalizados conforme o manifesto. Texto visível preservado.
- A menção textual a 47.2/47.3 em 47.1 foi preservada; os destinos permanecem sem confirmação editorial.

## Reprodução independente e preservação

- Árvore persistida vs reconstrução isolada: **idêntica** por caminho relativo e SHA-256.
- Fases 1–9: 2586 hashes preservados. Fontes, páginas/referências da fase e JSON: hashes preservados.
- Backups: somente os diretórios/arquivos listados no relatório de validação foram efetivamente verificados; ausência não é tratada como integridade.
- Ressalva: a raiz do vault Obsidian não foi confirmada; wikilinks de origem não foram reescritos.
- Nenhum commit, push, importador, modificação de originais ou alteração do JSON foi executado.
