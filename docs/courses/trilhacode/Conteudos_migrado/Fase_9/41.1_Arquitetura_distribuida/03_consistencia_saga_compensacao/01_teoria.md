---
arquivo_id: "f9-41-1-03-consistencia-saga-compensacao-01-teoria"
parent_key: "41.1"
tipo_arquivo: "theory"
assunto: "03_consistencia_saga_compensacao"
ordem: 3
itens_origem: ["### 3. Consistência eventual, saga e compensação"]
---


### 3. Consistência eventual, saga e compensação
Quando serviços mantêm bancos separados, não existe uma transação ACID única que desfaça automaticamente todas as etapas. Uma **saga** organiza transações locais e define o que fazer em sucesso ou falha: tentar recuperação para frente ou executar compensações de negócio.

Exemplo de compra: criar pedido `PENDENTE` → reservar estoque → autorizar pagamento → confirmar pedido. Se o pagamento falhar, liberar a reserva e marcar o pedido como `CANCELAMENTO_PENDENTE` ou `CANCELADO` conforme a liberação seja confirmada. A compensação é uma nova operação; ela pode falhar, demorar ou precisar de intervenção. Por isso, estados intermediários e reconciliação fazem parte do desenho.

- **Orquestração:** um coordenador registra e conduz o próximo passo. Torna o fluxo explícito, mas exige persistir estado e tratar disponibilidade do coordenador.
- **Coreografia:** participantes reagem a eventos. Reduz coordenação central, mas o fluxo pode ficar difícil de enxergar conforme crescem participantes e relações.
- **Idempotência:** cada comando/evento usa identificador estável; o serviço registra processamentos concluídos de forma durável. Uma repetição retorna o resultado anterior ou não aplica o mesmo efeito novamente.

Não chame compensação de rollback: uma captura de pagamento pode exigir estorno, que é observável e pode ter prazo ou taxa. Especifique quem vê cada estado, quanto tempo pode permanecer nele e como uma rotina de reconciliação detecta processos incompletos.

**Checagem:** se a reserva de estoque falha depois de o pedido existir, qual estado de pedido representa a situação enquanto a compensação/reconciliação acontece?

