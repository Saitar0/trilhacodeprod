# Fase 2.1A.12C.16 — Relatório final

## A. Resultado executivo

A prova persistente demonstrou que nove pares de writers **sintéticos e cooperativos** podem compartilhar a autoridade de revisão C8/C10: cada corrida confirmou somente um participante, uma revisão, uma auditoria e um item de histórico. Falhas determinísticas dentro de participantes compostos abortaram as mutações em múltiplas coleções e permitiram retry/replay sem duplicação.

A prova também demonstrou que uma conta MongoDB com escrita direta em `content_blocks` consegue contornar revisão, fence e auditoria. Portanto, a C16 valida contenção cooperativa e explicita um bypass operacional ainda não eliminado. Nenhum writer ativo foi exercitado nesta fase; não há contenção global comprovada.

**Veredito:** CONTENÇÃO EDITORIAL PARCIALMENTE VALIDADA — COBERTURA E ENFORCEMENT PENDENTES.

## B. Git e isolamento

* Base: `32b56147f5e993095b11cf56be04ba8ffbc6cc01` (contém C15).
* Branch: `codex/fase2-1a-12c16-editorial-writer-containment`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c16-editorial-writer-containment\trilhacodeprod`.
* Checkout original e demais worktrees permaneceram sem alterações.
* Sem push, PR, merge, rebase ou deploy.
* `docs/courses/trilhacode/` e `docs/migracao/` não foram materializados.
* Commit local criado após as validações com a mensagem `test(curriculum): validate isolated editorial writer containment`.
* A worktree foi deixada limpa; o hash final consta no relatório entregue ao responsável.

## C. Writers investigados

A matriz C13 versionada possui 17 caminhos/símbolos, revalidados por testes estáticos C14: W-01 a W-17, com 6 A, 8 B, 1 C e 2 D; todos marcados `runtime=NOT_VERIFIED`. C16 relacionou os modelos de edição, publicação, importação, restauração, exclusão, duplicação, reordenação e seed aos IDs C13. As famílias reais foram inspecionadas via inventário e símbolos, mas os modelos C16 não chamam esses writers. W-08/09/14/15/16/17 permanecem sem participantes persistentes equivalentes.

## D. Contrato e evidência persistente

O módulo C16 reutiliza `AsyncEditorialRevisionAdapter` C10 e o protocolo C8. Um participante familiar é executado na sessão transacional comum a CAS/fence, atualização C8, evento funcional sintético, histórico e recibo. Não cria autoridade paralela.

MongoDB 7.0.43, replica set exclusivo `rsC16` de nó único, WiredTiger, sessões habilitadas, PyMongo 4.18.2 e runner Python 3.11. Cada cenário usou banco de nome aleatório `editorial_revision_test_c10_c16_*`, exigido pelo validador do adaptador C10 e marcado como propriedade C16. O contêiner tinha `/data/db` e `/data/configdb` em tmpfs, rede bridge interna dedicada sem saída/porta publicada; o runner se conectou somente pelo alias privado `mongo-c16`. Usuários e dados foram sintéticos. Não houve banco real, volume ou recurso de outra fase.

## E. Concorrência, falhas e bypass

Nove cenários usaram clientes independentes e barreira explícita: edição×edição, edição×publicação, edição×importação, edição×restauração, publicação×restauração, importação×publicação, exclusão×edição, duplicação×reordenação e seed×edição. Em todos: uma revisão confirmada, um conflito, um evento de auditoria, uma entrada de histórico, um marcador de efeito e os estados de operação `COMMITTED`/`CONFLICTED`.

Cinco falhas determinísticas foram injetadas após a primeira mutação composta (importação/restauração/exclusão), após criar snapshot sintético e antes da auditoria. Em cada caso a revisão continuou zero, nenhuma mutação/versão/publicação/auditoria/histórico/recibo de sucesso permaneceu. Retry da mesma preparação confirmou uma vez; replay não repetiu participante.

O bypass usou uma segunda identidade sintética `readWrite`: gravou o bloco antes e depois do commit protocolar, sem alterar revisão/histórico/auditoria em cada escrita direta. Role de teste limitada à coleção de conteúdo também conseguiu alterar o bloco enquanto não podia alterar a coleção C8 de revisão; somente leitura foi rejeitada. A prova confirma que privilégios por coleção podem limitar acesso ao protocolo, mas não transformam escrita de conteúdo direta em edição conforme. A prevenção requer retirar essa capacidade, restringir entradas antigas ou centralizar credenciais, após validação operacional própria.

## F. Snapshots, publicação, importação, restauração e alunos

Snapshot/publicação sintéticos validaram que um snapshot de revisão fonte desatualizada é rejeitado e falha após criação do snapshot não ativa/publica efeito parcial. Isso não exercita W-04/W-12/W-15 reais nem readers/head de geração.

Importação/restauração sintéticas demonstraram rollback atômico de pequenos grupos de documentos, não dos jobs, batches, leases, retomadas ou limites de volume reais. A exclusão sintética apagou junto um bloco, progresso e tentativa. Esse resultado mostra precisamente que atomicidade não define se apagar dados dos alunos é permitido. Contratos de preservação de sessões por geração, progresso, tentativas e correções continuam requisitos sem prova C16.

## G. IAM, grants, CAS, fencing, auditoria e idempotência

CAS/fence e escritor protocolar foram exercitados em MongoDB pelo C10 sob credenciais C16 de writer sintéticas. IAM C11/C12 não foi repetido: não se prova autorização real ou grant por trilha. A identidade MongoDB `readWrite` usada no teste é a ameaça de bypass, não a capability IAM C11.

Auditoria e histórico sintéticos participaram da transação C10. Isso não altera `backend/audit.py` nem prova seus callers. O recibo C8/C10 não duplicou operação em replay do participante; falha de auditoria abortou a operação. Falha natural de rede/UnknownTransactionCommitResult não foi induzida.

## H. Testes e regressões

* C16 persistente: **19 aprovados**, sem falhas ou skips, em MongoDB descartável (9 concorrências parametrizadas, 5 injeções de falha, snapshot obsoleto, fence obsoleto, bypass direto, role restrita e exclusão/learner-state).
* Execução combinada C16 + inventário C13: **27 aprovados**, incluindo 19 casos persistentes, 3 contratos unitários C16 e 5 verificações do inventário.
* Regressões offline selecionadas: **295 aprovados, 36 skips, 6 deselected e 38 subtests aprovados**. Incluíram unit tests C1/C2/C5/C8/C10/C11/C12/C14/C15, snapshot safety, C13 inventory/governance e harness C6/C5.
* A tentativa inicial da suíte offline sem seleção terminou com os mesmos 295 aprovados, 36 skips e 38 subtests, mas 6 erros `FileNotFoundError` porque o sparse-checkout não materializou workflows `.github` e artefatos `ops/g2`. Esses seis testes de contrato/deploy foram explicitamente deselected na repetição; não materializei esses caminhos nem investiguei G2/ADR-008, conforme o escopo.
* Suítes persistentes históricas C2/C3/C7–C12: não executadas; exigiriam recursos exclusivos de fases anteriores, que não foram reutilizados. C16 exercitou em MongoDB descartável o adaptador async C10 e a revisão C8 nos cenários deste harness.

## I. Qualidade, segurança e limpeza

O fixture verifica propriedade do contêiner/rede por label, ID da imagem, isolamento, armazenamento temporário, ausência de volumes e ausência de portas publicadas. O test runner foi um contêiner transitório ligado apenas à rede interna e código/venv montados read-only. Cada DB temporário só é removido após validar seu marcador C16. Na limpeza final confirmei que não restavam bancos com o prefixo C16, volumes ou rede/contêiner da fase; removi somente o contêiner e a rede marcados C16. Não se usou dados reais, nem staging/produção.

O primeiro arranjo de teste tentou publicar porta na rede Docker `--internal`; o Docker não a publicou. Os testes então falharam por conectar a uma topologia diferente e foram cancelados como evidência. Recursos próprios da tentativa foram verificados por labels, imagem, tmpfs, binding apenas loopback e membro único antes de remoção. A instância final foi recriada sem portas e os testes passaram no runner da rede interna. O episódio está registrado para não confundir falha de fixture com resultado funcional.

Qualidade C16: Ruff passou nos quatro arquivos Python novos; Mypy passou nos dois módulos de harness/participante; compilação sintática dos quatro arquivos passou. `git diff --check`, escopo, links, segredos e imports operacionais foram verificados antes do commit.

## J. Gates e ADR-008

Preservados exatamente: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 continua bloqueado. Sem promoção de gates.

## K. Arquivos

Arquivos novos incluídos no commit local:

* `backend/curriculum_contract/experimental_editorial_writer_containment.py`
* `backend/integration_tests/editorial_writer_containment_harness.py`
* `backend/integration_tests/test_editorial_writer_containment.py`
* `backend/unit_tests/test_editorial_writer_containment_contract.py`
* `docs/architecture/editorial-generations-phase-2-1a-12c16-writer-containment-contract.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c16-bypass-evidence.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c16-integration-dependencies.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c16-final-report.md`

## L. Limitações e próximo incremento

Não demonstrados: execução dos writers reais por família sob sessão C10, IAM e grants implantados, privileges/identidades reais de serviço, inventário dinâmico completo, falha natural de rede, commit desconhecido, topologia multinó, política de retenção/progresso, consistência de readers de publicação e integração operacional.

**Próximo incremento recomendado:** obter evidência autorizada e não invasiva da matriz de identidades de serviço/roles e das entradas que podem escrever nas coleções protegidas; sem essa prova não há como desenhar ou validar a contenção contra bypass para uma primeira onda.

**Veredito:** CONTENÇÃO EDITORIAL PARCIALMENTE VALIDADA — COBERTURA E ENFORCEMENT PENDENTES. Integração operacional não autorizada.
