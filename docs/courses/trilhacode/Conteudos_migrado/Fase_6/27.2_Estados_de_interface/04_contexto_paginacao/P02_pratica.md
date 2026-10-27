---
arquivo_id: "f6-27-2-04-contexto-paginacao-p02-pratica-md"
parent_key: "27.2"
tipo_arquivo: "practice"
assunto: "04_contexto_paginacao"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Implemente paginação com dados provisórios
**Objetivo:** evitar saltos visuais e decisões baseadas em metadados desatualizados.

**Passos:**
1. Use uma API paginada ou um mock com pelo menos três páginas, total de páginas e indicação de próxima página.
2. Inclua página, filtro e ordenação na identidade da consulta, para que cada combinação represente resultados diferentes.
3. Ao mudar de página, mantenha temporariamente os itens anteriores se a biblioteca permitir e sinalize visualmente a atualização.
4. Enquanto a resposta nova for provisória, impeça que `hasMore`, contagem ou cursores da página antiga autorizem outra navegação.
5. Teste a chegada da resposta, uma falha de rede e uma troca rápida de filtros; confirme que os itens e controles correspondem ao contexto selecionado.

**Dica:** verifique a documentação da biblioteca para distinguir dados definitivos de `placeholderData` ou equivalente.

**Entrega:** paginação funcional com estado provisório explícito e evidência dos três cenários.

**Critérios de conclusão:** parâmetros da consulta estão completos; os controles não usam metadados provisórios; uma falha mantém uma saída compreensível e permite recuperação segura.

