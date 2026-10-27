---
arquivo_id: "f5-18-2-03-idempotencia-em-retries-p03-pratica"
parent_key: "18.2"
tipo_arquivo: "practice"
assunto: "03_idempotencia_em_retries"
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Simular retries e concorrência
Desenhe uma operação de criação de pedido que recebe uma chave de idempotência. Especifique escopo da chave, comparação de payload, estados enquanto a primeira chamada está em andamento, retorno para repetição concluída, conflito de chave e retenção. Simule: resposta perdida após sucesso; duas chamadas simultâneas iguais; mesma chave com payload diferente; e falha durante chamada a um provedor externo.

**Dica:** escreva a sequência de persistência e efeito em ordem. Pergunte o que ocorre se o processo cair entre cada par de passos. Uma chave sem restrição única ou coordenação concorrente não protege contra duas execuções simultâneas.

