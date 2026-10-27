---
arquivo_id: "f6-27-2-04-contexto-paginacao-01-teoria-md"
parent_key: "27.2"
tipo_arquivo: "theory"
assunto: "04_contexto_paginacao"
ordem: 4
itens_origem: ["## Microtópico 4 — Preserve contexto durante atualização e paginação"]
---

## Microtópico 4 — Preserve contexto durante atualização e paginação
Atualizar não exige apagar a tela. Quando há dados anteriores úteis, mantenha-os visíveis e indique que estão sendo atualizados. Se a atualização falhar, diferencie “não há dados para exibir” de “a última atualização falhou”. Isso reduz saltos visuais e impede que um erro secundário transforme uma tela utilizável em uma tela vazia.

Em paginação, a página selecionada faz parte da identidade da consulta: a chave deve incluir parâmetros que mudam o resultado, como página, filtro e ordenação. Algumas bibliotecas preservam temporariamente a página anterior enquanto buscam a próxima. Nesse intervalo, identifique que o conteúdo é provisório e não use metadados antigos como se fossem da página atual. Por exemplo, não permita avançar outra página com base em um `hasMore` ainda pertencente à resposta anterior. Mantenha também filtros e posição de navegação quando isso fizer sentido para a tarefa.

