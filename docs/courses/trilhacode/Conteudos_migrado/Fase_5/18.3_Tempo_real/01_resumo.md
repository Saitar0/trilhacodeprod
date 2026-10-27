---
arquivo_id: "f5-18-3-01-resumo"
parent_key: "18.3"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Polling pergunta periodicamente; SSE transmite servidor→cliente; WebSocket permite troca bidirecional.
- Reconexão e replay dependem de IDs, retenção e lógica do aplicativo.
- IDs/sequências permitem tratar duplicatas, mensagens antigas e lacunas; não garantem entrega exatamente uma vez.
- Autorização precisa proteger a conexão, a assinatura em cada recurso e cada comando.
- Um canal não substitui o estado autoritativo; conflito e limites de escala devem ser declarados.

