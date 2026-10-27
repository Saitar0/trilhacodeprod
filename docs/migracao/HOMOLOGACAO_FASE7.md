# Homologação da migração estrutural — Fase 7

**Veredito: APROVADA COM RESSALVAS**

## Base e escopo

- Commit-base: `53956919fc145e897f5ac7763513812b03f04dba`.
- Branch de trabalho: `migracao-estrutura`.
- Sete unidades ativas, listadas pela página oficial da Fase 7: 32.1, 32.2, 33.1, 34.1, 35.1, 36.1 e 36.2.
- 23 assuntos; 156 arquivos migrados.
- 210 registros de mapeamento: 161 associações de conteúdo (incluindo títulos de unidade) e 49 conversões de metadados.
- Fontes: 28 microtópicos, 35 questões com respostas existentes e 21 práticas.

## Integridade e reprodução

- A reconstrução dos pares questão/resposta recompõe integralmente os 35 blocos originais, usando o limite literal `Resposta esperada:`; não houve reescrita dos enunciados ou respostas.
- Itens compartilhados foram armazenados uma única vez em `90_integracao/`: 36.1/Q1 e 11 práticas compartilhadas.
- A reprodução isolada, em diretório temporário fora do repositório, gerou os mesmos 156 caminhos relativos e os mesmos hashes SHA-256 da árvore homologada. O manifesto e o gerador validaram 7 unidades, 23 assuntos e 210 mapeamentos; os 149 links Markdown relativos foram resolvidos e não há wikilinks nas sete unidades ativas.
- Os metadados originais em listas foram transportados ao frontmatter YAML sem alterar seus valores. As únicas normalizações foram estruturais: separação literal das respostas, serialização UTF-8/LF e criação de índices/links previstos no manifesto.
- Uma execução anterior concluiu a geração e a auditoria, mas falhou ao formatar a mensagem final. O erro ocorreu após a escrita e era apenas de apresentação; a reprodução atual terminou com sucesso e confirmou a árvore por hash.

## Ressalvas

- A raiz do vault Obsidian não foi confirmada. A integração futura de wikilinks permanece pendente; nenhum wikilink foi reescrito nesta migração.
- Cópias de 37.1 e 37.2 existem na pasta de origem da Fase 7, mas não aparecem na lista oficial da fase e são listadas na Fase 8. Permaneceram intactas e fora da árvore migrada. Não se presume aposentadoria formal; a pendência editorial continua aberta.

## Preservação

- As 2.005 arquivos migrados das Fases 1–6 foram verificados e permanecem idênticos por SHA-256.
- As fontes originais e backups verificados, o JSON de importação e os documentos protegidos permaneceram inalterados durante a reprodução.
- Nenhum importador foi executado. Nenhuma fase posterior foi gerada. Esta homologação não substitui a revisão do proprietário nem autoriza integração com a plataforma.
