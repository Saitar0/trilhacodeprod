---
arquivo_id: "f9-42-2-01-celery-tarefas-fora-requisicao-01-teoria"
parent_key: "42.2"
tipo_arquivo: "theory"
assunto: "01_celery_tarefas_fora_requisicao"
ordem: 1
itens_origem: ["### 1. Celery: tarefas fora da requisição"]
---


### 1. Celery: tarefas fora da requisição
Celery executa funções como tarefas em processos worker. A aplicação pode enviar uma tarefa por um broker e continuar sem esperar todo o trabalho terminar. O broker transporta tarefas; um result backend, quando configurado, guarda estados/resultados consultáveis. São responsabilidades diferentes, e nem todo fluxo precisa armazenar o resultado da tarefa.

Exemplos adequados incluem processar relatórios, enviar lotes de notificações ou executar uma etapa demorada que pode terminar depois da resposta HTTP. Se o usuário precisa de confirmação imediata, mantenha a operação síncrona ou devolva estado explícito como `PENDENTE` e ofereça consulta posterior. Celery não substitui o desenho do fluxo nem garante que toda tarefa será executada sem configuração e operação apropriadas.

Falhas e redeliveries podem repetir trabalho. Uma tarefa que cobra cartão, envia e-mail ou altera dados externos precisa de chave idempotente ou proteção equivalente. Retry deve ser limitado e reservado a erros elegíveis; falha permanente, esgotamento de tentativas e tarefa presa precisam ser observáveis. Considere broker, workers, concorrência, filas, monitoramento e caminho de recuperação como parte do custo.

Comparação aproximada: Celery pode cumprir o papel de sistema de tarefas/workers que em Node é atendido por bibliotecas como BullMQ, mas recursos, garantias, brokers e configuração diferem.

**Checagem:** broker e result backend são sinônimos? Não; um transporta tarefas e o outro, se usado, persiste estados/resultados consultáveis.

