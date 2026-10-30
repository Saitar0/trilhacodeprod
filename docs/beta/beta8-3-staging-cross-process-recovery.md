# Beta 8.3 — Staging através da autoridade separada

## Fluxo exercitado

O harness usa `CurriculumStagingService` Beta 5 para preparar um lote sintético no banco `beta5_<UUID>`, usando o usuário Mongo `beta8-3-stager`. A API não recebe essa URI nem a chave HMAC do stager. A autoridade recebe somente `beta8-3-stage-reader`, relê o owner marker, batch, registros, manifestos e checkpoints, compara os campos persistidos com o pacote e só então monta uma intenção `SYNTHETIC_FIXTURE_APPROVED` para o namespace experimental.

O bridge e `Beta8ExperimentalPromoter` existentes continuam responsáveis por grants, CAS/fencing, transação e auditoria. Um guard de sessão/usuário participa da mesma transação da decisão C8. Não há chamada a rotas de publicação, `track_publications` ou banco operacional.

## Cenários persistentes

No MongoDB 7/replica set descartável foram exercitados:

* preparação real Beta 5 e transição pelo processo separado;
* retry após commit com o mesmo operation ID, sem nova geração;
* duas chamadas concorrentes da mesma transição: uma confirmação e um replay;
* adulteração de campo persistido após preparação: rejeição HTTP 409 antes de uma geração adicional;
* negativa MongoDB para o escritor de staging fora das coleções de staging, e para o leitor ao tentar atualizar batch;
* preservação da geração experimental anterior e de sentinelas de tentativas, submissões e progresso.

O conjunto demonstra os cenários exercitados, não recuperação universal para perda natural de processo/rede. A resposta perdida é simulada por retry após confirmação persistida; não é uma interrupção real de rede entre o commit e o cliente. Reinício da autoridade durante uma transição não foi exercitado.

## Bloqueios pedagógicos

O lote desta prova é explicitamente sintético. A rubrica real do projeto 3.5 permanece `PROPOSED`; a prova não aprova rubrica, não conclui fase real e não altera draft/private da primeira fase.
