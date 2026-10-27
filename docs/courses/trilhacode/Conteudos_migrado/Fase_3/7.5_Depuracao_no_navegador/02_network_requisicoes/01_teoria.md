---
arquivo_id: "f3-7-5-02-network-requisicoes-01-teoria"
parent_key: "7.5"
tipo_arquivo: "theory"
assunto: "02_network_requisicoes"
ordem: 2
itens_origem: ["4. Network: investigar requisições"]
---

### 4. Network: investigar requisições
**Network** registra requisições enquanto o painel está aberto. Reproduza a ação e filtre por Fetch/XHR; selecione a requisição para conferir URL, método, status, headers, payload, resposta e timing. A coluna Initiator e a pilha do iniciador ajudam a localizar o código que disparou a solicitação.

Um status HTTP como 404 ou 500 indica que uma resposta chegou com status malsucedido. Uma requisição marcada como falha/bloqueada pode não apresentar status HTTP legível; investigue Console e detalhes de rede, especialmente se suspeitar de CORS. Não conclua que todo erro sem status é CORS. Ao compartilhar evidências, oculte tokens, cookies, dados pessoais e conteúdo sensível.

**Erro comum:** interpretar “há uma linha vermelha na Network” como diagnóstico completo. Registre o detalhe observável, URL e comportamento esperado; só então formule a causa provável.

