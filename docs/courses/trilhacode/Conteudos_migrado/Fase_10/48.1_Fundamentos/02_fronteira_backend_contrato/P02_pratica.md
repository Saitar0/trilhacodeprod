---
arquivo_id: "f10-48-1-p02"
parent_key: "48.1"
tipo_arquivo: "practice"
assunto: "02_fronteira_backend_contrato"
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Implementar uma integração mínima no backend
Implemente uma rota de backend para o caso definido. Injete cliente/configuração, mantenha a credencial em variável/configuração local fora do repositório, valide entrada e imponha tamanho/timeout adequados. Trate erro de autenticação, rate limit e falha do provedor sem expor conteúdo ou segredo. Crie teste com cliente falso para verificar o contrato e o tratamento de falha; se tiver acesso e autorização, faça uma chamada real apenas com dados sintéticos e dentro de um limite de uso definido.

**Entregável:** diff da rota/adaptador, teste do cliente falso, configuração de exemplo sem valor secreto e registro sanitizado de uma execução (real ou simulada).

