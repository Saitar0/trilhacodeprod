---
arquivo_id: "f5-18-2-90-integracao-p02-pratica-compartilhada"
parent_key: "18.2"
tipo_arquivo: "practice"
assuntos: ["02_compatibilidade_versionamento_openapi", "03_idempotencia_em_retries"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Revisar mudança de versão e OpenAPI
Parta de uma API v1 com campo nome obrigatório e resposta de erro com código e mensagem. Proponha duas mudanças: uma aditiva e uma que quebra clientes. Marque a decisão para cada uma: manter versão, adicionar nova versão ou deprecar com prazo. Atualize uma descrição OpenAPI para incluir a operação, parâmetros, schema, sucesso, erros e exemplo de paginação. Compare cada resposta documentada com o comportamento que o servidor deve implementar.

**Dica:** mudanças no significado e nas garantias também podem quebrar mesmo quando os nomes dos campos permanecem iguais. OpenAPI documenta o comportamento, não o implementa automaticamente.

