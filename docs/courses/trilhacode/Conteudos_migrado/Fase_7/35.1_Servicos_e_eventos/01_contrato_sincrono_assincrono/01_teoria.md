---
arquivo_id: "f7-35-1-01-contrato-sincrono-assincrono-01-teoria-md"
parent_key: "35.1"
tipo_arquivo: "theory"
assunto: "01_contrato_sincrono_assincrono"
ordem: 1
itens_origem: ["### Microtópico 1 — Requisição síncrona ou processamento assíncrono"]
---

### Microtópico 1 — Requisição síncrona ou processamento assíncrono

**API Gateway** recebe chamadas HTTP/WebSocket e encaminha uma rota a uma integração. Uma integração com Lambda normalmente invoca a função de modo síncrono: a API aguarda a resposta para devolver status e corpo ao cliente. API Gateway também pode integrar com outros serviços conforme o tipo de API e sua configuração. Escolha HTTP API ou REST API pelos recursos necessários, autenticação/autorização, transformação, monitoramento e custo; não assuma que um tipo substitui o outro em todas as dimensões.

**Lambda** executa código sem que a equipe administre diretamente as máquinas do servidor. A equipe continua responsável por código, dependências, permissões da role, concorrência, limites/configuração, logs, observabilidade, timeout e custo por uso. Cold start e escala podem afetar latência; não é correto prometer latência zero ou custo sempre menor. Confira cotas e comportamento atual por runtime, região e tipo de invocação.

Use uma resposta síncrona quando a pessoa precisa do resultado para concluir a requisição e o trabalho cabe nos limites do caminho HTTP. Para tarefas demoradas ou que precisam absorver picos, a API pode validar e enfileirar um comando, responder `202 Accepted` com um identificador/status, e deixar um consumidor processar em segundo plano. A aplicação precisa então definir como consultar/notificar a conclusão, expirar tarefas e comunicar falha. Colocar uma fila no fluxo muda o contrato do cliente: sucesso ao enfileirar não significa que o trabalho final terminou.

