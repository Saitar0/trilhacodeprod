---
arquivo_id: "f4-15-1-02-consistencia-atualizacao-invalidacao-p02-pratica"
parent_key: "15.1"
tipo_arquivo: "practice"
assunto: "02_consistencia_atualizacao_invalidacao"
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Planejar invalidação e janela de desatualização
Considere uma página de produtos por categoria, ordenação e página. Desenhe três chaves de exemplo e descreva o que acontece quando um produto muda de categoria ou preço. Escolha quais chaves apagar, ou proponha uma estratégia de versão/namespace. Declare qual atraso de atualização o caso tolera e explique o custo da alternativa.

**Dica:** liste as consultas afetadas por uma escrita antes de escolher TTL. Uma chave agregada pode representar várias páginas e filtros, não apenas o registro atualizado.

