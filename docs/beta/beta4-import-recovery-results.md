# Beta 4 — falha parcial e recuperação

## Sequência verificada no writer

`run_import` verifica permissão global e formato, planeja o payload e, fora do dry-run, adquire lock de importação. Replaneja sob o lock, inicializa o job com resumo e destino, prepara/atualiza a trilha e seus nós/blocos/relações em etapas, atualiza o estado de importação, registra histórico e encerra job/lock. Em exceção, o handler marca job/trilha como interrompidos e conserva o mesmo identificador para recuperação. A sequência não está envolvida em uma transação global MongoDB.

## Falha controlada

O harness substituiu temporariamente `_block_values` no módulo real para lançar exceção na 61.ª chamada, após 60 blocos terem sido persistidos. A inspeção encontrou trilha marcada `interrupted`, job também `interrupted` e exatamente 60 blocos. A retomada usou o mesmo payload/identidade; o writer concluiu 44 nós, 161 blocos, 21 relações e uma única entrada de `edit_history`. Não houve remoção manual nem duplicação observada.

Esta é uma falha sintética dentro de um estágio, não uma falha real de processo ou rede. Não exercitou especificamente uma falha após resposta de banco perdida, entre duas unidades, durante escrita de auditoria ou sob duas importações concorrentes. Esses cenários permanecem pendentes.

## Comparação de recuperação futura

| Estratégia | Avaliação para Beta |
|---|---|
| Transação global | Coerente para um lote pequeno somente se todas as coleções, auditoria e autoridade editorial couberem na transação/topologia. Não é o comportamento atual; lotes maiores aumentam duração e custo. |
| Staging + promoção | Recomendação preferida para fase curricular: converter e validar tudo em staging isolado; promoção controlada de versão/generation após integridade. Promoção ainda precisa do protocolo C8–C16 e de proteção contra escritores diretos. |
| Job recuperável | Útil para preparar staging com checkpoints e identidade estável. A experiência observada recupera uma importação, mas depende de cooperação do writer e não equivale a atomicidade. |
| Híbrida | Melhor alvo: job idempotente para staging e promoção breve/atômica sob revisão, fencing e auditoria compartilhados. Depende de desenho e implementação operacional futura. |

Nenhuma recuperação futura poderá apagar auditoria/revisões confirmadas ou tocar tentativas/progresso dos alunos. Corrigir conteúdo publicado deve gerar nova revisão; rollback do lote deve impedir nova entrada, preservar evidência e reconciliar estado parcial, não apagar histórico.
