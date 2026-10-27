---
arquivo_id: "f5-17-2-03-logs-contexto-seguro-01-teoria"
parent_key: "17.2"
tipo_arquivo: "theory"
assunto: "03_logs_contexto_seguro"
ordem: 3
itens_origem: ["4. Logs úteis e seguros"]
---

### 4. Logs úteis e seguros
Um log de diagnóstico deve responder o que aconteceu e em qual operação. Registre evento, horário, nível, identificador de requisição, rota ou operação, resultado e código/classe do erro quando disponíveis. Inclua apenas dados necessários para investigar. Não registre senha, token, cabeçalho de autorização, dados pessoais completos ou conteúdo de request sem motivo e proteção adequados. Prefira um identificador de correlação não secreto a copiar dados sensíveis para o log.

console.log e console.error são úteis para experimentos locais; o objeto console envia dados a stdout/stderr, mas não define por si só formato estruturado, níveis, retenção, alertas ou política de privacidade de logs. No servidor, use a estratégia de logging do projeto e evite engolir erros. [Node.js — Console](https://nodejs.org/api/console.html).

