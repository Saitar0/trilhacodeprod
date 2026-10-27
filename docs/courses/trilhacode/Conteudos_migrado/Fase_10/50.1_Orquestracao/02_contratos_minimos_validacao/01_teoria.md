---
arquivo_id: "f10-50-1-t02"
parent_key: "50.1"
tipo_arquivo: "theory"
assunto: "02_contratos_minimos_validacao"
ordem: 2
itens_origem: ["### 2. Projetar contratos mínimos e previsíveis"]
---


### 2. Projetar contratos mínimos e previsíveis
Cada ferramenta deve ter nome e descrição específicos, um propósito claro, parâmetros tipados e saída pequena. Use enums e limites para reduzir estados inválidos. Não peça ao modelo valores que a aplicação já conhece: por exemplo, derive usuário e tenant da sessão autenticada, em vez de aceitar um `user_id` arbitrário como autoridade. O esquema controla formato; o backend ainda valida tamanho, faixa, estado atual, relações e invariantes de negócio.

Evite superfícies abertas como “executar SQL”, “rodar qualquer comando” ou “buscar qualquer URL”. Transforme-as em operações estreitas de domínio, com allowlists e limites. Retorne somente os dados necessários para a próxima etapa e não inclua segredos, dados de outros usuários ou mensagens internas de erro. A saída da ferramenta pode conter conteúdo hostil ou incorreto e não deve alterar permissões nem instruções do sistema.

