---
arquivo_id: "f2-5-2-90-integracao-04-gabarito-pratica-guiada"
parent_key: "5.2"
tipo_arquivo: "answer_key_pratica"
ordem: 1
itens_origem: ["P1"]
---

**Solução comentada:** use `display: flex; align-items: center; justify-content: space-between; gap: 1rem` na barra. Na grade, teste `repeat(2, minmax(0, 1fr))` e `min-width: 0` no cartão se o item continuar forçando a faixa; escolha uma regra de quebra de texto apropriada ao projeto, como `overflow-wrap: anywhere`, se quebrar identificadores for aceitável. Confirme no navegador com largura reduzida. A causa deve ser observada: não aplique as três declarações sem verificar qual resolve o problema.

**Erros comuns:** esperar que `justify-content` funcione sem um modo de layout que distribua itens; acreditar que `1fr` sempre ignora o tamanho mínimo do conteúdo; ocultar overflow sem avaliar se isso corta informação.

