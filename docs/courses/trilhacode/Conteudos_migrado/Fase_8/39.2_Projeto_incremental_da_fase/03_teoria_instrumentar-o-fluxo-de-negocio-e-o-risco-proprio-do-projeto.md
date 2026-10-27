---
arquivo_id: "f8-39-2-03-teoria-instrumentar-o-fluxo-de-negocio-e-o-risco-proprio-do-projeto-md"
parent_key: "39.2"
tipo_arquivo: "theory"
ordem: 2
itens_origem: ["MT02"]
---


### Microtópico 2 — Instrumentar o fluxo de negócio e o risco próprio do projeto

Adicione instrumentação OpenTelemetry ao caminho principal e às dependências que podem explicar falhas ou demora. Use nome de serviço, versão e ambiente como atributos de recurso estáveis; propague contexto entre chamadas; defina quais métricas, logs e traces são necessários. Para cada sinal, escreva a pergunta que ele responde. Evite tokens, payloads, dados pessoais e IDs únicos como labels de métricas. Registre amostragem, retenção e o que não é coletado.

O indicador mais importante da Fase 8 depende do tipo do projeto definido no [Guia de Projetos — Trilhos A e B](../../../Guia_Projetos_e_Rotacao_de_Tipos.md):

| Tipo do Trilho A | Evidência operacional específica nesta fase |
|---|---|
| **T1 — Transacional** | Métrica de pedidos/transações concluídos por período; verificação de que estoque/reserva não ultrapassa o limite e que repetição segura não duplica uma operação. Se o risco central de transação/idempotência ainda não foi implementado nas fases anteriores, entregue a base mínima necessária conforme o guia. |
| **T2 — SaaS multiempresa** | Configuração separada por ambiente e rollback demonstrado; teste de fumaça confirma que uma empresa não acessa dados de outra. Não use identificador de empresa/usuário como label de alta cardinalidade nem exponha dados do tenant. |
| **T3 — Tempo real e colaboração** | Deploy preserva conexão WebSocket/SSE através de proxy e HTTPS; métrica de conexões abertas e teste com clientes conectando, reconectando e recebendo atualização. |
| **T4 — Conteúdo, feed e busca** | Latência observável por rota normalizada, especialmente listagem/busca; painel permite localizar rota lenta e relacionar uma execução a trace. |
| **T5 — Dados e processamento assíncrono** | Job/container emite logs estruturados e métricas de duração e falhas; execução de teste deixa estado/resultado consultável sem duplicar efeitos indevidos. |

**Entrega 2 — Instrumentação com foco no tipo.** Implemente o sinal específico da linha correspondente e a cobertura comum do caminho de requisição/job. Inclua um teste automatizado ou procedimento repetível que gere o comportamento esperado e produza uma evidência observável.

**Critérios de aceite:** o sinal mede o comportamento descrito, não apenas disponibilidade do host; nomes/labels são estáveis e de baixa cardinalidade; um trace de teste pode ser correlacionado entre os componentes cobertos; dados sensíveis são removidos; limites de instrumentação ou de cobertura ficam documentados.

