---
arquivo_id: "f6-27-1-90-integracao-kp01-solucao-md"
parent_key: "27.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_contrato_requisicao_resposta", "04_cors_erros_integracao"]
ordem: 1
itens_origem: ["P01"]
---

**Solução de referência:** função recebe page/filter/signal e credencial disponível; monta query conforme contrato; faz fetch; checa status; trata JSON de erro somente quando o corpo é parseável; converte 401 e 403 separadamente e retorna dados e metadados de sucesso. Falha de rede e abort são estados diferentes. Token só no header bearer se esse for o contrato.

