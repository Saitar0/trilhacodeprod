---
arquivo_id: "f9-40-3-04-operacao-custo-decisao-01-teoria"
parent_key: "40.3"
tipo_arquivo: "theory"
assunto: "04_operacao_custo_decisao"
ordem: 4
itens_origem: ["### 4. Operação, custo e decisão defensável"]
---


### 4. Operação, custo e decisão defensável
Compare pelo menos estes fatores com carga e região representativas:

| Dimensão | Pergunta para a decisão |
|---|---|
| Semântica | Fila, log retido ou publicação/assinatura? Precisa reter e reler? |
| Entrega | Quais confirmações, duplicatas, retries, DLQ e idempotência são necessários? |
| Ordem e escala | Qual escopo de ordem? Quantas partições, grupos, filas ou chaves? Onde está o gargalo? |
| Operação | Quem cuida de cluster, atualização, capacidade, segurança, backup, alertas e incidentes? |
| Integração | Clientes, protocolos, IAM, rede, limites, ferramentas e portabilidade atendem ao ambiente? |
| Custo total | Considere chamadas/unidades, volume, retenção/armazenamento, transferência, capacidade provisionada e horas de operação. |
| Recuperação | Como inspecionar DLQ, corrigir a causa, redrive sem duplicar efeitos e medir backlog? |

Preço publicado é fotografia de uma configuração e região. Compare cotações atuais e inclua custos indiretos: engenharia operacional, plantão, observabilidade, tráfego entre zonas/regiões e capacidade ociosa. Um serviço gerenciado reduz trabalho de infraestrutura, mas não elimina desenho de falhas, permissões, monitoramento e testes.

Uma recomendação boa registra: requisitos eliminatórios; opção escolhida; alternativa rejeitada e motivo; pelo menos dois trade-offs; teste de carga/falha que poderia invalidar a escolha; e fonte/documento com data de consulta.

