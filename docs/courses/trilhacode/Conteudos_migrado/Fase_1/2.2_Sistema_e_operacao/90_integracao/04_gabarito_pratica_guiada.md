---
arquivo_id: "f1-2-2-90-integracao-04-gabarito-pratica-guiada"
parent_key: "2.2"
tipo_arquivo: "answer_key_pratica"
ordem: 1
itens_origem: ["P1"]
---

**Gabarito comentado:** fatos: há um erro `EACCES` em uma operação de escrita às 14:32:01, associado ao processo `webapp` e ao pedido `r-221`; um health check posterior aparece como bem-sucedido. Hipótese: o processo pode não ter permissão de escrita no caminho indicado — o log sozinho não mostra proprietário, grupo nem permissões. Verificações seguras: identificar a conta efetiva do serviço e inspecionar as permissões do caminho completo, sem alterá-las. `grep -n -C 1` mostra a linha correspondente, seu número e uma linha ao redor; `tail -n 3` mostra as três últimas linhas. O health check bem-sucedido não prova que o upload voltou a funcionar.

