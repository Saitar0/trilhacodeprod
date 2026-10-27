---
arquivo_id: "f9-40-1-01-exchange-binding-filas-consumers-p01-pratica"
parent_key: "40.1"
tipo_arquivo: "practice"
assunto: "01_exchange_binding_filas_consumers"
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Desenhar e provar o roteamento
Modele eventos sintéticos de pedido com routing keys `orders.created`, `orders.cancelled` e `orders.eu.created`. Crie uma topologia de exemplo com exchange topic e filas independentes de faturamento, auditoria e notificação. Escolha bindings, preveja os destinos de cada evento e depois teste a previsão num broker local ou com uma tabela de roteamento simulada.

**Entrega:** diagrama de exchange/bindings/filas, tabela chave → filas de destino e uma publicação não roteável com explicação de como o publisher a detecta.

**Critérios de aceite:** distingue exchange de fila; aplica `*` a exatamente um segmento e `#` a zero ou mais; explica competição de consumers na mesma fila versus cópias em filas distintas; trata mensagem sem binding.

