---
arquivo_id: "f10-48-2-p02"
parent_key: "48.2"
tipo_arquivo: "practice"
assuntos: ["01_streaming_contrato_eventos", "02_estados_saida_parcial", "03_cancelamento_timeout_falhas"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Implementar e provocar falhas
Adicione streaming por SSE ao app, com autenticação conforme o projeto, estados da interface e um mecanismo de cancelamento. Use um provedor simulado ou mock para produzir: resposta normal, erro antes do primeiro fragmento, erro após alguns fragmentos, atraso acima do timeout e cancelamento. Depois, se autorizado e com dados sintéticos, teste uma chamada real sob limite de uso. Verifique também se o ambiente local entrega fragmentos sem buffering inesperado.

**Entregável:** diff da rota/cliente/interface, testes ou roteiro reproduzível dos cenários, evidência dos estados observados e descrição do que o cancelamento realmente interrompe.

