---
arquivo_id: "f5-18-1-90-integracao-p03-pratica-compartilhada"
parent_key: "18.1"
tipo_arquivo: "practice"
assuntos: ["02_fluxo_de_requisicao_e_camadas", "04_status_e_erros_http"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Montar matriz de testes do contrato
Escreva uma matriz de verificações HTTP para: criação válida, body inválido, ID inexistente, usuário sem autenticação, usuário sem permissão, conflito de domínio, erro inesperado e repetição de DELETE. Para cada caso, declare entrada, status esperado e formato mínimo da resposta. Inclua uma verificação de que uma falha não vaza detalhes internos e que cada requisição termina com apenas uma resposta.

**Dica:** use uma identidade e dados de teste controlados; não use tokens reais em exemplos ou logs. O comportamento de autenticação pode retornar 404 em alguns produtos para ocultar a existência de um recurso, desde que a política seja deliberada e consistente.

