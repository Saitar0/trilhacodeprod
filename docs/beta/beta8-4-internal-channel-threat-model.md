# Beta 8.4 — canal interno e limites de confiança

## Protocolo exercitado

O RPC fechado foi endurecido para o protocolo `beta8-4-rpc-v2`. HMAC-SHA256 cobre versão, serviço emissor, audiência explícita `trilhacode-editorial-authority`, método, caminho, timestamp, nonce e SHA-256 dos bytes exatos do corpo; a comparação da assinatura é constante. O corpo tipado vincula operação, ator/sessão, recurso, revisão, identidade idempotente e dados validados. A autoridade determina o fence; o chamador não escolhe esse valor. A resposta é assinada com a audiência do serviço chamador, nonce da request, status e hash do corpo. A janela de timestamp é limitada, nonces são persistidos com unicidade/TTL, e indisponibilidade do registro de replay falha fechada.

`EditorialMutationCommand` rejeita campos extras, comandos fora do conjunto `block.update`, `block.create`, `node.update`, shapes inválidos, payload acima do limite e campos de consulta/coleção/autorização arbitrários. A autoridade revalida usuário, sessão e grant C12 por recurso; `authorized=true` do chamador não faz parte do contrato. Retry legítimo usa novo nonce de transporte e mantém a identidade/idempotência da operação; replay do mesmo nonce e payload divergente para a operação são rejeitados.

## Cenários de ameaça

| Cenário | Estado B8.4 | Evidência/limite |
| --- | --- | --- |
| Request sem assinatura, adulterada, expirada, com serviço ou audiência errados | VERIFIED | HTTP direto à autoridade rejeitado no harness real |
| Replay de nonce | VERIFIED | Ledger persistente Beta 8.3 e prova HTTP |
| Retry legítimo após resposta perdida | VERIFIED no caso exercitado | Mesmo comando reconciliado após commit/restart, sem duplicar histórico/geração |
| Comando ou coleção arbitrária | VERIFIED | Schema fechado rejeita campo extra via HTTP |
| Grant, sessão, ator e escopo | VERIFIED nos caminhos exercitados | Releitura da fonte IAM da autoridade e negativas HTTP |
| Chave interna ausente/autoridade indisponível | VERIFIED fail-closed no harness | Não há writer direto alternativo; mutações retornam falha segura |
| Transporte cifrado/mTLS | NOT_VERIFIED | Teste usa rede Docker interna; não prova TLS operacional |
| Rotação/distribuição operacional de segredos | NOT_VERIFIED | Nenhum ambiente operacional foi acessado |
| Comprometimento total da API | NOT_PROTECTED_BY_DESIGN | A chave HMAC de serviço é compartilhada pela API e autoridade. Uma API comprometida pode assinar mensagens como serviço; a autorização revalidada limita ações/escopo, mas não prova resistência ao gateway comprometido nem impede abuso de sessões alcançáveis pelo processo. |
| Comprometimento da autoridade ou credencial Mongo privilegiada | NOT_PROTECTED_BY_DESIGN | A autoridade precisa de escrita nas coleções testadas; processo/segredo comprometido pode contornar o protocolo dentro desses privilégios. |

## Veredito

**AUTENTICAÇÃO E INTEGRIDADE DO CANAL INTERNO VALIDADAS NO MODELO DE AMEAÇAS DEFINIDO**. A afirmação se limita à rede e às chaves sintéticas do harness; não substitui gestão de identidade/segredo operacional nem protege um participante que possua a chave compartilhada.
