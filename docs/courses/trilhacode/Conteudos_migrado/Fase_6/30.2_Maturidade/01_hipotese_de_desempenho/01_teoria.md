---
arquivo_id: "f6-30-2-01-hipotese-de-desempenho-01-teoria-md"
parent_key: "30.2"
tipo_arquivo: "theory"
assunto: "01_hipotese_de_desempenho"
ordem: 1
itens_origem: ["## Microtópico 1 — Transforme uma queixa em hipótese testável"]
---

## Microtópico 1 — Transforme uma queixa em hipótese testável
“A página parece lenta” não diz onde atuar. Descreva a tarefa, quem sente a demora e em que condições ela aparece. Separe carregamento inicial, resposta a uma interação, atualização da interface e espera de rede. Em seguida, formule uma hipótese que conecte causa e efeito: “ao filtrar esta coleção, recalculamos todos os grupos; cachear a transformação deve reduzir o tempo da interação sem alterar os resultados”.

Escolha uma medida que possa confirmar ou refutar essa hipótese. Um perfil de renderização pode mostrar duração de commits e componentes envolvidos; uma gravação do navegador pode revelar tarefas longas ou recursos que bloqueiam a interação; uma análise de bundle pode indicar código carregado antes de ser necessário. Se a medida não corresponde ao problema, um número melhor pode não significar uma experiência melhor.

Antes de alterar o código, registre o cenário, dados e métrica. Mude uma coisa de cada vez. Se aplicar simultaneamente memoização, paginação e divisão de código, não saberá qual mudança afetou o resultado nem qual introduziu uma regressão.

