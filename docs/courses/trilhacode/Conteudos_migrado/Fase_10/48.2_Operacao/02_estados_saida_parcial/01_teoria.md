---
arquivo_id: "f10-48-2-t02"
parent_key: "48.2"
tipo_arquivo: "theory"
assunto: "02_estados_saida_parcial"
ordem: 2
itens_origem: ["### 2. Estados da interface e saída parcial"]
---


### 2. Estados da interface e saída parcial
Modele o ciclo de vida como estados explícitos: aguardando, recebendo, concluído, erro e cancelado. A interface deve distinguir uma resposta terminada de um texto parcial. Se a conexão cair após alguns fragmentos, informe que a resposta foi interrompida e não a apresente como resultado concluído. Não misture fragmentos de solicitações diferentes; ao trocar de tela ou iniciar outra solicitação, encerre ou invalide o fluxo anterior.

SSE é unidirecional: o navegador recebe eventos do servidor. Uma requisição separada pode iniciar a geração; o cancelamento pode ser enviado por outro endpoint ou pelo encerramento do fluxo, conforme a arquitetura. Verifique comportamento de autenticação, reconexão, cabeçalhos, limites de conexão e buffering em proxy/CDN. Uma API pode transmitir corretamente localmente e ser agrupada/bufferizada no caminho de produção.

