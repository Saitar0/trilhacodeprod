# Pendências globais após auditoria das Fases 1–10

**Estado:** preparação documental concluída; importação não autorizada nesta etapa.  
**Base auditada:** `147dc68b81169f66b0ba3802fa2f26e5130923a3` na branch `migracao-estrutura`.

## Antes de gerar o JSON ou executar o importador

| Prioridade | Pendência | Evidência / risco | Próxima ação recomendada |
|---|---|---|---|
| Bloqueante | Definir o mapeamento da árvore Markdown para a hierarquia de nós da plataforma | A organização migrada é `fase/unidade/assunto/arquivos`; a hierarquia padrão atual declara `phase/module/submodule/topic` em `backend/constants.py`. Não se deve presumir que pastas de assunto sejam equivalentes a nós da plataforma. | Especificar, no gerador futuro, a correspondência de fase, módulo, unidade e assunto, incluindo títulos, ordenação e IDs estáveis. Validar o resultado em preview antes de qualquer importação. |
| Bloqueante | Especificar tipos e campos dos blocos que representam gabaritos e feedbacks | `backend/seed.py` lista os tipos suportados e não inclui `answer_key`. A decisão aprovada mantém gabaritos em `theory_text` no JSON até uma tarefa separada de extensão do importador e renderer. O renderer usa `GenericBlock` para tipos não mapeados explicitamente em `frontend/src/components/blocks/BlockRenderer.tsx`. | Manter a limitação aprovada ou planejar, em tarefa separada, a extensão coordenada de validação, importador, renderer e testes. Não emitir um tipo novo no JSON sem suporte de ponta a ponta. |
| Bloqueante | Definir como feedback, rubrica, critérios de aceite e checklist são serializados | Há arquivos separados na migração, mas nem todo tipo documental corresponde a um tipo de bloco nativo. Parte dos aceites permanece associada a marcos/checklists. | Aprovar mapeamentos determinísticos para campos de exercício e blocos `checklist`; preservar escalas, descritores, limiares e associação ao marco de origem. |
| Bloqueante | Preservar itens compartilhados sem duplicar o conteúdo importado | Os mapas apontam itens compartilhados a um único arquivo físico e a vários assuntos. Uma importação ingênua por pasta pode duplicar blocos ou perder as relações entre assuntos. | Gerar um registro/bloco canônico por item compartilhado e relações explícitas com todos os assuntos relacionados; validar unicidade e referências no JSON gerado. |
| Bloqueante | Mapear `arquivo_id`, relações e ordenação para os identificadores da plataforma | Os 2.890 `arquivo_id` são únicos e prefixados por fase no Markdown; ainda não há prova de que esses identificadores estejam convertidos para os campos e restrições de ID do formato de importação. Conexões curriculares são arquivos separados e não há links Markdown relativos entre fases. | Definir IDs estáveis de nós/blocos, serialização de `pre_requisito`/relações e ordenação a partir dos manifestos. Verificar referências órfãs antes do preview. |
| Bloqueante | Reconciliar a estrutura do JSON atual antes de substituí-lo | O JSON existente tem SHA-256 `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`, 194 nós e 1.691 blocos de três tipos. Ele não foi regenerado a partir das 2.890 páginas da árvore migrada. | Tratar o JSON migrado futuro como artefato gerado, comparar contagens e hashes, revisar o diff e validar preview/importação descartável somente sob autorização específica. |

## Pendências editoriais e de navegação

| Prioridade | Pendência | Situação observada | Ação recomendada |
|---|---|---|---|
| Alta | Raiz do vault Obsidian | 94 wikilinks foram preservados. A raiz do vault não foi confirmada, portanto sua resolução real não foi testada. | Confirmar a raiz do vault e executar uma validação de resolução sem reescrever os links automaticamente. |
| Alta | Referências textuais 47.2 e 47.3 em 47.1 | As menções existem como texto, sem link Markdown e sem unidades ativas correspondentes identificadas na Fase 10. | Decidir editorialmente se as referências continuam como texto, são corrigidas ou recebem destinos válidos; não criar unidades por inferência. |
| Média | Cópias 37.1 e 37.2 na pasta original da Fase 7 | As cópias diferem por hash das fontes oficiais da Fase 8. Foram mantidas intactas e não migradas como unidades ativas da Fase 7. | Registrar formalmente o status editorial das cópias antes de qualquer limpeza, consolidação ou renomeação futura. |
| Média | Links externos | 556 destinos externos foram identificados sintaticamente; não foi verificada disponibilidade, redirecionamento, autenticação nem atualidade das páginas. | Fazer revisão de links por risco e conteúdo volátil antes da publicação, em tarefa separada. |
| Baixa | Divergência de carga horária da Fase 2 | A página da fase registra 18 h e a soma dos metadados das unidades registra 18,5 h; a divergência aprovada foi preservada. | Decisão editorial futura; não alterar durante a migração estrutural. |
| Baixa | Backups | Não foram encontrados diretórios separados de backup sob `Conteudos/`. | Não declarar backups verificados; se existirem em outra localização, identificá-los antes de uma auditoria que os inclua. |

## Riscos técnicos comprovados e potenciais

### Comprovados

- O JSON atual não representa a árvore Markdown migrada e não foi atualizado nesta execução.
- O importador utiliza uma hierarquia de nós específica; a tradução da pasta de assunto para essa hierarquia precisa ser definida.
- `answer_key` não está entre os tipos listados em `backend/seed.py`; até a extensão futura aprovada, a serialização legada em `theory_text` permanece uma limitação conhecida.
- A raiz do vault Obsidian continua desconhecida e 94 wikilinks não foram resolvidos.
- As referências a 47.2/47.3 não têm destino confirmado.
- As fontes originais incluem duas cópias de unidades 37.x da Fase 7 com conteúdo diferente das fontes oficiais da Fase 8; nenhuma foi fundida ou descartada.

### Potenciais, a validar no gerador futuro

- Colisão ou instabilidade de IDs caso a rotina de importação não derive os IDs a partir de uma regra determinística.
- Perda de associações quando o mesmo conteúdo atende a mais de um assunto.
- Dessincronização entre ordem do manifesto e ordem dos nós importados.
- Perda da associação entre entrega, aceite, checklist, rubrica e limiar de projeto.
- Renderização genérica ou inadequada de tipos ainda não suportados explicitamente.
- Links Markdown para arquivos e conexões curriculares que não sejam convertidos em relações da plataforma.

## Sequência segura recomendada

1. Aprovar o mapeamento de hierarquia, relações e tipos de bloco sem tocar no JSON atual.
2. Implementar o gerador como tarefa separada; manter o comportamento atual dos manifestos e registrar os gabaritos no formato aprovado até que o suporte dedicado exista.
3. Gerar JSON candidato em arquivo temporário e validar esquema, IDs, relações, ordem, conteúdo compartilhado, projetos e contagens.
4. Revisar o diff do JSON candidato contra o JSON atual e validar em preview/ambiente descartável quando houver autorização específica.
5. Só então solicitar autorização para substituir o JSON ou executar o importador. Nenhuma dessas ações foi feita nesta auditoria.

## Encerramento

Os três relatórios globais permanecem sem commit. Não houve alteração curricular, regeneração do JSON, execução do importador ou modificação das árvores homologadas. A recomendação atual é **não importar ainda**: a documentação migrada está íntegra dentro das verificações descritas, mas o contrato de conversão para o formato executável e a resolução dos wikilinks ainda precisam ser tratados.
