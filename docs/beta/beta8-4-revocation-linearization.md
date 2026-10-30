# Beta 8.4 — ordenação de revogação e commit

## Semântica

Uma autorização C12 é revalidada dentro da transação C8. O guard faz atualização condicional do principal, da sessão e do mesmo documento de grant (incremento de `use_sequence`), exigindo epochs, estado ativo, escopo e operação esperados. A mutação editorial, a revisão CAS/fencing, o histórico e a auditoria participam da mesma transação MongoDB. O ponto de confirmação é o commit dessa transação, não a recepção HTTP nem a consulta inicial do grant.

Uma revogação é efetiva quando o `update_one` no grant persiste `state=revoked` e incrementa `authorization_epoch`. Como a mutação participa do mesmo documento do grant, as duas operações têm de serializar no MongoDB. Uma mutação cujo commit vem primeiro permanece válida e auditada; quando a revogação persiste primeiro, o guard condicional da mutação falha e a transação não confirma.

Essa garantia cobre os fatos de IAM armazenados nessas coleções e este writer transacional. Não implica atomicidade entre MongoDB e resposta HTTP, nem cobre writers fora do protocolo ou uma credencial privilegiada que ignore a autoridade.

## Evidência persistente

O harness B8.4 instala barreiras persistentes somente no contêiner de autoridade descartável (`BETA8_4_TEST_BARRIERS=1`). A barreira `before_commit`, situada depois da autorização/capability inicial e antes da transação editorial, permite revogar grant (W-07 PUT e W-05 PUT) ou sessão (W-07 POST), confirmar a revogação no banco e então liberar a chamada. As três respostas foram negadas; revisão, bloco/unidade, histórico e auditoria permaneceram sem mutação. Retry com a mesma identidade de operação continuou negado.

Uma segunda prova pausa W-07 PUT dentro da transação, depois que o guard atualizou condicionalmente principal/sessão/grant e depois da mutação/auditoria transacionais. Um segundo cliente MongoDB inicia a revogação enquanto a transação permanece aberta. Na execução final, a operação editorial confirmou primeiro; a revogação foi confirmada em seguida. O harness conferiu revisão, conteúdo, um único item de histórico, um único evento de auditoria e grant finalmente revogado. Assim, a autorização usada pela operação precedeu sua confirmação, e a revogação não foi reportada como efetiva antes desse commit.

O segundo interleaving foi exercitado em W-07 PUT. As negativas após revogação pré-commit cobriram as três operações. Não se afirma que a revogação vence uma transação que já adquiriu a participação condicional do grant; ela é ordenada depois nesse caso.

## Veredito

**REVOGAÇÃO CONCORRENTE VALIDADA ENTRE PROCESSOS COM ORDEM DE COMMIT COMPROVADA**, para os caminhos exercitados no laboratório. API, autoridade e MongoDB estavam em processos/serviços separados. A verificação combina respostas HTTP com leituras persistentes posteriores; não depende somente de 403/409.
