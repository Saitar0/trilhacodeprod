---
arquivo_id: "f5-17-2-03-logs-contexto-seguro-kp03-gabarito-pratica"
parent_key: "17.2"
tipo_arquivo: "answer_key_pratica"
assunto: "03_logs_contexto_seguro"
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** registrar, por exemplo, evento request_failed, request ID não secreto, rota-modelo, status, duração e error code; omitir senha, token e corpo completo. Falha de autenticação deve registrar categoria e resultado, sem valor de credencial. Falha de banco pode registrar a classe/código técnico em destino restrito, enquanto a resposta ao usuário permanece segura.

