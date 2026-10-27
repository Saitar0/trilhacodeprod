---
arquivo_id: "f4-15-1-01-cache-aside-chaves-p01-pratica"
parent_key: "15.1"
tipo_arquivo: "practice"
assunto: "01_cache_aside_chaves"
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Implementar o fluxo cache-aside
Escolha uma consulta de catálogo ou perfil que possa ser reconstruída a partir de uma fonte de verdade. Defina uma chave com os parâmetros relevantes, serialize uma resposta, use TTL e registre o caminho de hit e miss. Faça duas leituras idênticas e demonstre que a segunda pode usar o cache. Inclua fallback controlado caso Redis esteja indisponível.

**Dica:** se estiver usando um serviço já existente, comece com uma função pequena que receba a chave e uma função de leitura da origem; registre explicitamente hit, miss e erro. Não coloque dados pessoais ou segredos no exemplo.

