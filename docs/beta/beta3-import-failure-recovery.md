# Beta 3 — falhas e recuperação de importação

## Sequência observada no serviço versionado

Leitura estática de `backend/services/imports.py::run_import` e `_execute` confirmou: validação de permissão `content.write` e formato; cálculo determinístico de `operation_id` a partir do payload e `job_id` a partir de slug/operação; plano/dry-run; aquisição de lock/job com lease; replano sob o lock; criação/atualização da trilha com marcador `_import_state`; gravação de nós e blocos por ref; relações; snapshot se já publicado; upsert de `edit_history` por `import_operation_id`; finalização do marcador da trilha; conclusão do job e resposta persistida.

Os writes são feitos em várias operações e **não** participam de uma transação global. A recuperação real é por repetição do mesmo payload e identidade estável: o serviço retoma jobs `interrupted`, compara refs já persistidas, completa o que falta e faz upsert da auditoria. Lease de 15 minutos e heartbeat ajudam a reservar trabalho; não são fencing suficiente contra escritores externos nem substituem o protocolo editorial C8–C16.

## Falhas controladas em MongoDB descartável

| Injeção | Estado confirmado antes da exceção | Retomada com o mesmo payload | Resultado |
|---|---|---|---|
| Exceção na quinta chamada de `_block_values` | Trilha, nó e quatro blocos de teoria gravados; job/trilha marcados interrompidos | Sim | 19 blocos, 1 nó e 1 evento de auditoria, sem duplicar os quatro existentes |
| Wrapper grava auditoria e perde confirmação antes de finalizar | Todos os blocos e um `edit_history` persistidos; marcador ainda presente | Sim | operação finalizada; continua havendo somente uma auditoria |
| Falha antes de qualquer gravação | Não foi isolada neste harness; lock/job já são gravações precoces | Não exercitada | Exige cenário próprio para distinguir reserva persistida de ausência de efeito |
| Falha natural de rede/driver | Não induzida | Não aplicável | Não alegar equivalência com os wrappers sintéticos |

As falhas são injetadas por patch temporário de helpers do serviço real de importação. A resposta perdida após auditoria é uma simulação de confirmação perdida, não erro real do driver. A leitura após os cenários confirmou drafts, refs estáveis e ausência de duplicação.

## Estratégias avaliadas

| Estratégia | Benefício | Limites | Uso indicado |
|---|---|---|---|
| Transação global | Tudo confirma ou aborta junto | Limite de duração/tamanho, custo de transação e importações grandes; não é o comportamento do importador atual | Importações pequenas, somente após topologia/IAM/protocolo e testes confirmarem viabilidade |
| Staging e promoção | Dados incompletos permanecem privados e inelegíveis; promoção pode ser pequena e condicionada à validação | Requer destino/versionamento, controle de referências e promoção coordenada; não resolve bypass legado por si só | Preferível para primeira fase, em combinação com reconciliação e protocolo editorial aprovado |
| Job recuperável por etapas | Reinício, checkpoints, refs estáveis e reconciliação sem reiniciar do zero | Estado parcial existe; exige idempotência de cada etapa, autoridade/fencing e política de limpeza | Necessário para importações maiores; combinar com staging e auditoria por etapa |

Recomendação para uma fase futura: preparar versão de importação privada em staging, validar manifesto/refs/contagens, depois promover por uma operação pequena da autoridade editorial comum; manter job recuperável por etapas e identidade de operação estável. A operação de promoção precisa CAS/fence, grant e sessão ordenados, auditoria, recibo idempotente e ausência de escritores capazes de bypass. Ainda não foi implementada.

Não apagar documentos parciais ou auditoria automaticamente, não reverter revisões confirmadas por delete, e não tocar em progresso/tentativas de alunos durante recuperação.
