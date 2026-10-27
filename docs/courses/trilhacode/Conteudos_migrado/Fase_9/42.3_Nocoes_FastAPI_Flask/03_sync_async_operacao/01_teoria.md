---
arquivo_id: "f9-42-3-03-sync-async-operacao-01-teoria"
parent_key: "42.3"
tipo_arquivo: "theory"
assunto: "03_sync_async_operacao"
ordem: 3
itens_origem: ["### 3. Síncrono, async e operação"]
---


### 3. Síncrono, async e operação
FastAPI permite handlers `async def` e foi projetado para trabalhar com funções assíncronas quando as bibliotecas chamadas também oferecem operações awaitable. Se uma biblioteca de banco ou HTTP for bloqueante, marcá-la como `async` não a torna não bloqueante. Use async para concorrência de I/O que o stack suporta; não espere acelerar trabalho intensivo de CPU só por mudar a assinatura da função.

Flask é WSGI e aceita views assíncronas com a dependência extra correspondente, mas sua documentação explica que cada requisição ainda ocupa um worker durante o ciclo; async permite, entre outros usos, aguardar I/O concorrente dentro da requisição, mas não muda automaticamente a capacidade de requisições simultâneas de cada worker. Tarefas lançadas sem espera numa view podem ser canceladas quando o ciclo de eventos termina; trabalho durável de fundo deve usar uma fila/worker apropriado, como o padrão discutido em 42.2.

Django também tem suporte assíncrono em partes do stack, mas compatibilidade de middleware, ORM e bibliotecas depende de versão e uso. Não faça afirmações gerais a partir de um benchmark isolado. Compare o servidor/protocolo, bibliotecas, chamadas bloqueantes, concorrência, carga, latência, observabilidade e requisitos de WebSocket/long-lived connections na versão que pretende usar.

Todos precisam de configuração de produção adequada. Servidores de desenvolvimento e modo debug são para desenvolvimento; deployment envolve servidor compatível, variáveis/secrets, segurança, limites e telemetria.

**Checagem:** mudar um endpoint Flask para `async def` garante que uma requisição atendida deixa o worker livre para outra? Não; no modelo WSGI descrito pelo Flask, cada ciclo ainda ocupa um worker.

