---
arquivo_id: "f4-15-1-01-cache-aside-chaves-kp01-gabarito-pratica"
parent_key: "15.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_cache_aside_chaves"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:** primeiro tentar ler a chave; em hit, validar e retornar o valor; em miss, buscar a origem, serializar e gravar com TTL; se o Redis falhar, usar a origem com timeout e registrar a falha. A política deve impedir que erro de desserialização seja confundido com um resultado válido.

