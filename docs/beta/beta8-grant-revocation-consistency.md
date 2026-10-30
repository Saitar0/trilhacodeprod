# Beta 8 — Consistência de grants e revogação

## Fatos de autorização na fatia sintética

C12 mantém principal, sessão e grant por trilha com epochs. A autorização emite capability assinada e vinculada ao ator, sessão, operação, trilha, papel e epochs. Ao confirmar uma mutação, seu participante atualiza condicionalmente os três registros C12 usando a mesma sessão MongoDB da transação C8/C10. Uma revogação também altera o documento do grant. Assim, uma decisão não é aceita apenas por uma leitura de permissão anterior.

## Ponto de ordenação testado

No harness persistente, uma barreira pausa a correção **depois da última autorização de requisição e antes do início da transação C10**. A revogação do grant confirma enquanto a operação está parada; em seguida, a confirmação é liberada. O participante transacional não encontra grant ativo/epoch esperado, lança negação, aborta a transação e deixa a revisão e o bloco inalterados. Este cenário reproduz precisamente a janela que a revalidação imediatamente anterior ao CAS não fecharia.

O ponto de linearização do experimento é o commit da transação que escreve a revisão, o participante de conteúdo, os fatos de autorização usados, o histórico/recibo e a auditoria. Se a transação de revogação confirmou primeiro, a operação não confirma. A prova também exercitou uma corrida de dois writers contra a mesma revisão, com um vencedor e um `RevisionConflict`.

## O que não foi demonstrado

* Não houve corrida arbitrada pelo scheduler onde transação de revogação e transação de mutação estivessem simultaneamente abertas; foram testadas ordenação por barreira e disputa persistente de CAS.
* A revogação de JWT/IAM ativo não participa desta transação. O mecanismo C12 é sintético.
* A autoridade Python detém uma credencial MongoDB com update nas coleções que coordena. Um processo que obtenha essa credencial pode emitir update direto e contornar o protocolo.
* Epoch de política persistente compartilhado entre todas as instâncias e drenagem de writers antigos continuam dependências C15/ADR-008.

Portanto, a evidência fecha a corrida request-auth/CAS para a fatia C12/C10 testada; não prova linearizabilidade do IAM operacional nem contenção de todo writer.
