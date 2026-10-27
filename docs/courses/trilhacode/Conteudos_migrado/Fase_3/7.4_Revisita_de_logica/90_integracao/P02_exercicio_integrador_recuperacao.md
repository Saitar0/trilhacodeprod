---
arquivo_id: "f3-7-4-90-integracao-p02-exercicio-integrador-recuperacao"
parent_key: "7.4"
tipo_arquivo: "practice"
assuntos: ["01_transformacoes_e_colecoes", "02_complexidade", "03_pilhas_e_filas"]
ordem: 2
itens_origem: ["P2"]
---

## Exercício integrador — recuperação sem consulta
**Antes de começar:** feche as anotações e reserve 20 minutos. Resolva de memória; se não souber algo, registre sua hipótese e siga. Só consulte o gabarito depois de entregar suas respostas. O objetivo é recuperar e conectar ideias, não acertar tudo de primeira.

Considere estes pedidos:

```js
const pedidos = [
  { id: 1, cliente: "Lia", total: 30, status: "concluido" },
  { id: 2, cliente: "Caio", total: 12, status: "pendente" },
  { id: 3, cliente: "Lia", total: 8, status: "concluido" },
  { id: 4, cliente: "Bia", total: 20, status: "cancelado" },
];
```

Sem executar o código, resolva e explique:
1. Use `filter()` para selecionar pedidos concluídos e `map()` para criar linhas com `id`, `cliente` e `total`. Escreva o resultado.
2. Use `reduce()` para calcular o total concluído por cliente. Diga o valor de Lia e explique como tratou um cliente que ainda não estivesse no acumulador.
3. Compare uma solução que percorre a lista separadamente para filtrar, transformar e agrupar com uma solução que realiza tudo em uma passagem. Qual é a ordem de crescimento de cada uma? Qual outra diferença prática deve ser considerada?
4. Para registrar duas ações de desfazer, escolha a estrutura adequada e diga qual ação sai primeiro. Para processar pedidos recebidos na ordem de chegada, escolha a estrutura e diga qual pedido sai primeiro.
5. Diga se sua solução altera o array original e como você verificaria o caso de uma lista vazia.

**Dica de recuperação:** associe cada operação à pergunta que responde: “quais passam na condição?”, “como cada item vira outra coisa?” e “como combinar tudo num resultado?”. Depois desenhe o estado do acumulador a cada pedido concluído.



**Autoavaliação:** marque cada item como “recuperei”, “recuperei com hesitação” ou “preciso revisar”. Compare sua resposta com os resultados e justificativas, corrija em outra cor e escreva uma frase para cada erro explicando a confusão. Domínio esperado: pelo menos 4 dos 5 itens sem consulta; erros em `filter/map/reduce` ou LIFO/FIFO devem ser revistos antes de avançar.

