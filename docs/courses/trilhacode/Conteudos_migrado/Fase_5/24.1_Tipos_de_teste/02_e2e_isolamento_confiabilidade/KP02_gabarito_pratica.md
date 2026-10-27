---
arquivo_id: "f5-24-1-02-e2e-isolamento-confiabilidade-kp02-gabarito-pratica"
parent_key: "24.1"
tipo_arquivo: "answer_key_pratica"
assunto: "02_e2e_isolamento_confiabilidade"
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:** preparar a base e fixture por teste, usar identificador único controlado e consultar o registro criado pelo próprio teste; limpar ao final ou usar transação/esquema isolado; aguardar a conclusão da operação e a condição resultante em vez de pausa fixa; fechar conexões e aplicação no teardown. O resultado deve ser repetível sem depender de outro teste.

