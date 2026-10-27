---
arquivo_id: "f10-50-1-t01"
parent_key: "50.1"
tipo_arquivo: "theory"
assunto: "01_ciclo_tool_calling"
ordem: 1
itens_origem: ["### 1. Tool calling é um ciclo controlado pela aplicação"]
---


### 1. Tool calling é um ciclo controlado pela aplicação
No tool/function calling, a aplicação informa ao modelo quais ferramentas estão disponíveis e seus contratos. O modelo pode devolver uma proposta de chamada com nome e argumentos. A aplicação interpreta essa proposta, valida, autoriza e executa ou recusa; depois pode enviar o resultado ao modelo para continuar a conversa. O nome exato dos eventos e o formato de integração variam por provedor.

O modelo não recebe por isso acesso automático ao banco ou à rede: os poderes vêm das funções e serviços que a aplicação decide expor. Uma chamada proposta não é prova de intenção autorizada do usuário. Mantenha o executor e a decisão de acesso no servidor e trate qualquer saída do modelo como entrada não confiável.

