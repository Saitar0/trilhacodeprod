---
arquivo_id: "f6-26-1-02-effects-sincronizacao-limpeza-kp02-solucao-md"
parent_key: "26.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_effects_sincronizacao_limpeza"
ordem: 2
itens_origem: ["P02"]
---

**Solução de referência:** setup cria handle/subscription para o roomId atual e registra o listener; cleanup remove essa assinatura específica. Dependência [roomId] faz React limpar e configurar novamente ao trocar sala. Na desmontagem remove a última assinatura; repetir o primeiro ciclo em desenvolvimento não deixa duplicatas.

