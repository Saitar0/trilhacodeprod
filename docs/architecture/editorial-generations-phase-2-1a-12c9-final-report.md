# Fase 2.1A.12C.9 — Relatório final

## A. Resultado executivo

O contrato C8 foi composto experimentalmente com o writer real `update_block`, a forma versionada de `content_blocks` e o formato legado de `edit_history`, sem alterar o writer ou conectar a aplicação ativa. Em MongoDB 7 descartável, a atualização do bloco, auditoria, revisão, histórico e recibo confirmaram juntos; falha de auditoria reverteu o conjunto. Uma disputa entre dois clientes PyMongo independentes confirmou apenas uma revisão e retornou conflito ao outro.

O resultado é **parcial**, não compatibilidade operacional completa. A adaptação é síncrona (PyMongo em thread), usa identidades e autorização sintéticas, tem retorno diferente do endpoint e cobre apenas documentos/índices versionados e fixtures controladas. Validadores, grants, dados legados, runtime e todos os demais escritores não foram verificados.

## B. Git e isolamento

- Base exata: `63c190fb1cbaba423115bb307db0f95b9c111079`.
- Branch: `codex/fase2-1a-12c9-editorial-compatibility`.
- Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c9-editorial-compatibility\trilhacodeprod`.
- Checkout original e demais worktrees não foram alterados.
- Nenhum arquivo em `docs/courses/trilhacode/` ou `docs/migracao/` foi materializado.
- Nenhuma operação Git remota foi realizada.

## C. Código real e diferenças

`backend/services/blocks.py:update_block` lê o bloco, aplica `$set`, chama auditoria sem sessão e retorna o bloco. `backend/audit.py:audit` insere o formato legado de `edit_history`. A auditoria não recebe sessão; o writer não aplica revisão/CAS/fencing/idempotência. A rota aplica `content.write`, converte `BlockUpdate` em campos presentes e serializa o documento.

A adaptação [experimental](../../backend/curriculum_contract/experimental_editorial_compatibility.py) mantém o writer ativo intocado, converte estritamente ID hex para `ObjectId`, restringe campos a `title`/`data`/`status`, exige `track_id` direto, chama a autoridade C8 existente e insere os campos legados e de correlação C8 na mesma sessão. O índice parcial de operação foi criado apenas no banco descartável. Não foi criada uma segunda autoridade editorial.

## D. Assíncrono, autorização e contrato de resposta

O backend usa `AsyncMongoClient`; a adaptação C8 disponível usa PyMongo síncrono. C9 executa a operação em `asyncio.to_thread` com cliente e sessão próprios, sem bloquear o event loop no cenário testado e sem compartilhar sessões entre drivers. Cancelar a coroutine não interrompe a thread; um commit pode ocorrer depois do cancelamento. O teste reconciliou esse caso por replay com a mesma identidade e não há retry automático.

A autenticação/autorização real não foi executada. A rota exige `content.write`; a capability do protocolo e o ator do teste são sintéticos e não substituem IAM. O endpoint retorna um documento de bloco; C9 retorna recibo e bloco e usa exceções de domínio próprias. A conversão para erros/response HTTP, bem como a semântica de replay se o bloco for posteriormente removido/alterado, permanece pendente.

## E. Ambiente C9

- MongoDB `7.0.43`, imagem local `mongo:7.0.43`; image ID `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b` (identificador local, não digest OCI de manifesto).
- Replica set de um nó `rs12c9`, primário único, WiredTiger, sessões lógicas; PyMongo `4.18.2`, Python `3.11.9`, Pydantic `2.13.5`.
- Dados sintéticos em bancos novos `editorial_revision_test_c9_*`, com marcador de propriedade antes das fixtures. MongoDB usou tmpfs sem mounts persistentes. Cliente AsyncMongoClient do writer e clientes PyMongo do contrato eram distintos.
- Container e bridge exclusivos C9; publicação apenas `127.0.0.1:29127`, sem masquerade de saída e sem comunicação entre containers. Não havia credenciais operacionais.
- A topologia valida transações no replica set local de um membro. Não prova failover multinó, perda do host, grants/validadores implantados ou durabilidade equivalente à produção.

## F. Testes e resultados

Suíte persistente C9: **12 testes aprovados e 5 subtests aprovados**. Cobriu writer real e forma do schema, auditoria legada, falha parcial do writer atual, rollback transacional, recibo/replay, fingerprint conflitante, ID e validação, `track_id` divergente, event loop, cancelamento/reconciliação e CAS concorrente com dois clientes independentes. Resultado da última execução: `12 passed, 5 subtests passed` (16,85 s).

Regressões offline: **118 testes e 38 subtests aprovados** (1,05 s) para protocolo em memória, adaptador offline, observabilidade, harness C6 e PoC offline de gerações. Comandos, executados a partir de `backend/`: `python -m pytest -q integration_tests/test_editorial_compatibility.py -ra` com a URI e os IDs C9 explícitos, e `python -m pytest -q unit_tests/test_editorial_revision_protocol.py unit_tests/test_mongodb_editorial_revision_adapter.py unit_tests/test_editorial_observability.py integration_tests/test_editorial_observability_harness.py unit_tests/test_editorial_generations_poc.py -ra`. O contrato C8 persistente não foi executado em seus próprios recursos/porta: seriam recursos de outra fase; a composição foi testada em servidor C9 próprio. As suítes persistentes C7/C8 não foram reexecutadas. Ruff passou nos três arquivos Python novos; Mypy passou nos três com `MYPYPATH=backend` e `--explicit-package-bases`; compilação sintática também passou. Verificações finais de escopo e documentação foram executadas nesta worktree.

Uma primeira versão do novo teste concorrente falhou no preflight porque cada instância nova do adaptador precisava chamar explicitamente `verify_transaction_topology()`. Após incluir essa verificação, a assertion foi ajustada para contar somente auditorias da disputa, excluindo as duas linhas históricas sintéticas da fixture. A execução final passou; não houve mudança no contrato funcional para mascarar falha.

## G. Evidência por dimensão

| Propriedade | Evidência C9 | Limitação |
|---|---|---|
| Schema de bloco e IDs | Writer exato carregado por harness; `ObjectId`, `node_id`, `track_id`, `schema_version` e campos de update persistidos/consultados. | Fixtures sintéticas; validators implantados desconhecidos. |
| Auditoria | Formato real de `audit.py` e extensão aditiva coexistem; falha do insert reverte o bloco na transação C9. | Grants/índices/validators implantados desconhecidos. |
| CAS/revisão | Dois clientes MongoClient independentes disputaram revisão 0; um confirmou revisão 1 e um conflitou. | Um replica set de um nó; demais writers não cobertos. |
| Fencing | A ponte passa a credencial/fence do protocolo C8 para a mesma transação. | Não é IAM de produção; a autoridade operacional não foi conectada. |
| Idempotência | Replay recupera recibo sem segunda auditoria/revisão; payload divergente conflita. | Integração HTTP e registro de chave no cliente não implementados. |
| Async/cancelamento | Async writer real; ponte em worker não bloqueia o loop; cancelamento e reconciliação foram exercitados. | Thread pode confirmar após cancelamento; não há teste de shutdown do runtime ou queda real de rede. |
| Atomicidade | Falha no insert de auditoria reverte bloco, histórico e revisão no C9. | Não extrapolar a produção ou failover multinó. |

## H. Segurança e escopo

Antes de qualquer escrita, o harness verificou identidade de container/rede C9, label da fase, imagem, versão do servidor, replica set primário, WiredTiger, URI loopback sem credenciais, ausência de mounts, tmpfs, porta e topologia. O módulo experimental não cria cliente no import e não tem imports de rota/serviço. O writer real foi carregado com dependências controladas pelo harness e dados sintéticos. Não houve acesso a banco operacional, conteúdo curricular real, Docker de outra fase, Coolify, GHCR, staging ou produção.

## I. Arquivos

Novos arquivos locais:

- `backend/curriculum_contract/experimental_editorial_compatibility.py`
- `backend/integration_tests/editorial_compatibility_harness.py`
- `backend/integration_tests/test_editorial_compatibility.py`
- `docs/architecture/editorial-generations-phase-2-1a-12c9-compatibility-matrix.md`
- `docs/architecture/editorial-generations-phase-2-1a-12c9-final-report.md`

Nenhum arquivo operacional, ADR, matriz histórica ou documento anterior foi alterado.

## J. Gates e limites

Gates históricos preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. A prova de um writer e uma composição experimental não satisfaz cobertura global nem autoriza integração. ADR-008 permanece bloqueado.

Limites centrais: sem grants/validators/documentos implantados; sem IAM real; sem integração async nativa; sem mapeamento HTTP; sem equivalência de resposta/replay; sem cobertura de todos os writers; sem baseline operacional; sem failover multinó. Os campos aditivos de auditoria e o histórico de payload do protocolo também precisam de validação de schema, acesso e retenção segundo ADR-005/ADR-004.

## K. Próximo incremento recomendado

Com nova autorização, definir e testar isoladamente o contrato de fronteira HTTP/IAM para revisão esperada, chave idempotente, erros de conflito e replay, junto de uma escolha explícita entre adaptador async nativo e thread worker. Não integrar enquanto writers legados puderem contornar a revisão/fencing e enquanto o baseline ADR-008 estiver bloqueado.

## L. Veredito

**COMPATIBILIDADE EDITORIAL PARCIAL — ADAPTAÇÕES E DECISÕES PENDENTES**. A composição estrutural e transacional do subconjunto testado foi demonstrada apenas no ambiente isolado C9. Integração ao runtime, mudança de API, IAM e aplicação operacional não foram autorizadas nem realizadas.
