---
arquivo_id: "f9-46-2-m04-servico-adicional-observabilidade-e-comparacao"
parent_key: "46.2"
tipo_arquivo: "project_milestone"
ordem: 4
itens_origem: ["M04"]
titulo_marco: "Entrega 4 — Serviço adicional, observabilidade e comparação"
---


### Entrega 4 — Serviço adicional, observabilidade e comparação
Implemente um serviço pequeno na stack alternativa escolhida entre as stacks estudadas nas unidades 42–45. Ele deve consumir ou produzir uma mensagem no fluxo definido, expor apenas a interface necessária e deixar claro seu ownership. Não replique dados por conveniência sem indicar como serão atualizados. Se houver API, documente autenticação/autorização necessárias ao contexto e não exponha endpoint administrativo sem proteção.

Complete a visão operacional: métricas de taxa de entrada/saída, erros, redelivery, tamanho/idade da fila e DLQ; logs estruturados com correlation ID/event ID; health/readiness conforme o ambiente; instrução de investigação e resposta a mensagens presas. Compare stack principal e alternativa em modelo de execução, injeção de dependência, persistência/ORM, testes, configuração e deployment. Baseie a comparação no código e em observações deste projeto, não em generalizações de linguagem.


**Evidência:** demonstração do fluxo ponta a ponta com dados fictícios, relatório ou capturas de métricas/logs e README/ADR atualizado.

**Revisão:** confirme que há um caminho para detectar e tratar fila acumulada/DLQ e que a comparação aborda trade-offs observados. Registre o que não foi validado em produção.

