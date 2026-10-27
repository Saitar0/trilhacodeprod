---
arquivo_id: "f10-51-1-t02"
parent_key: "51.1"
tipo_arquivo: "theory"
assunto: "02_entradas_recuperacao_saidas_nao_confiaveis"
ordem: 2
itens_origem: ["### 2. Tratar entrada, recuperação e saída como não confiáveis"]
---


### 2. Tratar entrada, recuperação e saída como não confiáveis
Instruções maliciosas podem estar misturadas a conteúdo recuperado, e não há marcação textual que garanta que o modelo as ignore. Delimitar ou rotular fontes externas ajuda a explicar a fronteira, mas o controle decisivo precisa existir no código: acesso a dados autorizado no servidor, validação de saída e ferramentas de escopo mínimo. Não use prompts como única barreira para dados confidenciais ou ações privilegiadas.

Aplique autorização por requisição e por objeto; filtre o corpus antes de fornecer contexto e confirme que uma citação/resultado pode ser visto pelo usuário. Não envie credenciais no prompt. Trate saída do modelo como entrada não confiável para SQL, shell, HTML, URL ou API; use parâmetros, encoding e validações específicas. Se a saída puder direcionar uma URL, ferramenta ou arquivo, limite destinos e formatos e impeça acesso a recursos internos não previstos. Guarde logs mínimos, sem segredos nem conteúdo pessoal desnecessário.

