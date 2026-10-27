---
arquivo_id: "f8-38-1-01-escolha-dos-sinais-01-teoria-md"
parent_key: "38.1"
tipo_arquivo: "theory"
assunto: "01_escolha_dos_sinais"
ordem: 1
itens_origem: ["### Microtópico 1 — Escolher o sinal pela pergunta"]
---

### Microtópico 1 — Escolher o sinal pela pergunta

Observabilidade começa com uma pergunta: **o que mudou, onde ocorreu e qual operação foi afetada?** Logs, métricas e traces mostram ângulos diferentes da execução e ganham valor quando podem ser correlacionados.

- **Log** registra um evento com instante e contexto: por exemplo, uma tentativa de acesso negada ou uma falha ao consultar o banco. Logs são úteis para detalhes de um evento específico.
- **Métrica** registra medições agregáveis ao longo do tempo, como quantidade de requisições, taxa de erros, duração ou uso de recursos. Serve para acompanhar tendências, comparar períodos e detectar mudanças em uma população de operações.
- **Trace** representa o caminho de uma operação distribuída. Um trace contém spans, que registram unidades de trabalho e relações temporais entre chamadas, como API → serviço de pagamento → banco.

Exemplo: um painel mostra que a latência p95 da API aumentou (métrica); um trace lento aponta que a consulta ao banco ocupa a maior parte do tempo (trace); logs associados revelam que houve timeout numa chamada externa (log). Um alerta pode indicar que algo merece atenção, mas nenhum desses sinais sozinho prova a causa raiz.

