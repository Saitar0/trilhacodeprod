---
arquivo_id: "f5-24-4-02-pontos-de-revisao"
parent_key: "24.4"
tipo_arquivo: "project_review"
ordem: 0
itens_origem: ["Pontos de revisão do projeto"]
---

## Pontos de revisão do projeto
- A repetição de uma solicitação ou job não duplica efeito perigoso; descreva idempotência observável sem alegar execução exatamente uma vez.
- Cada identificador de objeto enviado pelo cliente passa por autorização no servidor; teste com usuários e objetos distintos.
- Um teste com mock não demonstra integração real com PostgreSQL; inclua ao menos um teste de rota/integração no ambiente descartável.
- Arquivo, conexão em tempo real, catálogo e cenário transacional têm limites explícitos; mensagens/logs não vazam dados sensíveis.

