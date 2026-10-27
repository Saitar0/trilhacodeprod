---
arquivo_id: "f5-18-1-90-integracao-kp03-gabarito-pratica-compartilhado"
parent_key: "18.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_fluxo_de_requisicao_e_camadas", "04_status_e_erros_http"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** documentar 201 para criação; 400 para body inválido; 404 para ID inexistente; 401 para falta de autenticação; 403 para identidade sem permissão; 409 para conflito; 500 com mensagem genérica para erro inesperado; e comportamento de DELETE repetido conforme contrato idempotente. A matriz verifica forma comum de erro, ausência de stack trace e encerramento correto da resposta.

