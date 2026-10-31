# Fase 2.1A.12C.3 — Validação persistente isolada

## Escopo e conclusão

Executamos o adaptador MongoDB da Fase 12C.2 contra um MongoDB 7 real, exclusivamente descartável. Duas execuções finais da suíte de integração passaram: cada invocação reportou **27/27**, incluindo os 24 casos MongoDB e três verificações de segurança da URI, sem skips no processo principal. O teste T24 também reexecutou a suíte em subprocesso e concluiu com sucesso.

O resultado sustenta o comportamento observado nessa topologia local. Não valida escritores da aplicação, failover, alta disponibilidade, runtime implantado nem uso em produção. G2 recebe evidência técnica nova, mas continua `NOT_VERIFIED`; G1 continua `PARTIAL`, G9 e G10 continuam `BLOCKED`.

## Ambiente e isolamento

Observações em 2026-10-29 UTC:

| Item | Evidência |
|---|---|
| Host | Windows 11 Enterprise LTSC Evaluation, build 26100 |
| Docker | CLI e daemon 29.8.2; contexto `desktop-linux`; Compose 5.6.0 |
| MongoDB | Imagem oficial preexistente `mongo:7.0.43`; RepoDigest e Image ID `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b` |
| Versão e topologia | MongoDB 7.0.43, replica set de nó único `rs12c3`, primário disponível, WiredTiger e sessões lógicas habilitadas |
| Read/write concern | O servidor reportou padrão `local` para leitura e `majority` para escrita. O adaptador usou leitura `majority`; nas transações, leitura `snapshot`, escrita `majority` com journal e preferência `primary` |
| Runner | Imagem oficial local `python:3.11-slim`, digest `sha256:e88e9763f943ec1834f992a4b51e0f24500486803e8bc534e5767af9ea65f6ce`; Python 3.11.17, PyMongo 4.18.2, dnspython 2.9.0 |
| Rede e portas | Rede Docker interna rotulada para a fase, sem gateway externo; nenhuma porta publicada no host. Runner compartilhou a namespace de rede do MongoDB |
| Dados | Volume dedicado e descartável; cada teste usou um banco aleatório `editorial_revision_test_*` e marcador de posse. A URI foi passada explicitamente, sem credenciais e com loopback e replica set |

Identificadores da execução: container MongoDB `306cc5d272e8f863da8b991d2f0c945f001b0cbe36ce1799560af68ff2eae6be`; rede `ca9c6027ce5342be4baa6015356b763f191c3e54513c80965c5b9df8237bae9c`. Os nomes e labels dos recursos incluíram a fase e um sufixo exclusivo. O container não tinha binding de porta. A porta local 27017 já estava ocupada por processo alheio e não foi consultada ou alterada.

O daemon Docker/Desktop foi iniciado pelo caminho normal porque estava instalado e parado. Não houve alteração de configuração do Windows, WSL2, Docker, rede ou serviço global. O container MongoDB foi criado na rede interna; nenhum banco ou serviço da aplicação foi acessado.

## Contrato exercitado

O adaptador permanece restrito a banco descartável e exige verificação explícita da topologia antes das operações. A revisão é derivada pelo servidor. A confirmação combina, em transação, validação do writer e do fence, CAS no documento da trilha, acréscimo ao histórico e recibo durável. O commit da transação é o ponto de linearização proposto e exercitado. A preparação persiste sem confirmar revisão. A operação lógica é idempotente por trilha, writer, identidade da operação, revisão-base e hash do payload canônico.

O fence e o CAS são serializados pelo mesmo documento de estado da trilha e pela sequência de controle. O avanço de fence concorre com o commit; o teste verifica uma ordem observável e rejeita writer antigo. Isso é evidência no replica set local de nó único, não prova formal nem evidência de comportamento em cluster com failover.

## Resultados

| Propriedade | Cenários | Resultado observado | Limite |
|---|---|---|---|
| Revisão monotônica e histórico denso | T1, T2, T23 | Aprovado; histórico e estado final coerentes | Topologia local de nó único |
| CAS persistente | T3, T4, T23 | Um vencedor para a mesma base; T4 e T23 usam processos independentes | Não prova disponibilidade sob falha de cluster |
| Fencing após takeover | T6, T20 | Writer/processo e handle antigos rejeitados | Authority é capability sintética de teste |
| Fencing sem nova revisão | T7 | Fence antigo rejeitado com revisão ainda inalterada | Sem failover de servidor |
| Corrida fence/commit | T22 | Uma ordem observável; commit anterior ao avanço ou rejeição pelo fence | Uma execução local não é prova formal de linearizabilidade |
| Idempotência e colisão | T8, T10, T11 | Recibo original recuperado; payload/intent incompatível conflita; repetição concorrente não duplica revisão | Falha de rede ambígua não foi injetada |
| Recuperação de recibo | T9, T15, T16 | Novo processo/adaptador recupera commit confirmado | Não houve reinício do servidor MongoDB |
| Atomicidade transacional | T17 | Falha injetada após atualização do estado não deixou revisão, histórico ou recibo parcial | Falha injetada no cliente dentro da callback; não é crash do servidor |
| Preparação abandonada e conflito | T5, T13, T14, T18, T21 | Draft não confirmado é preservado; erros permanecem distinguíveis | Contratos sintéticos, sem writer real |
| Isolamento de trilhas e limites | T12, T19 | Estado isolado; limites rejeitados antes da confirmação | Não avalia tamanho de conteúdo curricular real |
| Segurança da URI | Três testes | URI remota, com credenciais, SRV ou banco fora do padrão é recusada | Guardas de cliente não substituem isolamento de rede |

### Contagem e repetibilidade

- Integração, primeira execução final: 27 executados, 27 aprovados, zero falhas, zero skips; 24 são casos MongoDB e três validam URI.
- Integração, segunda execução final em bancos novos: mesmos 27/27, sem falha ou skip no processo principal.
- T24 executa uma suíte filha de 27 casos. Em cada filha, T24 é intencionalmente ignorado para impedir recursão; os outros 26 passam. Esse skip é apenas a guarda de recursão da execução filha e não ocorre nas duas invocações principais.
- Regressão 12C.1, contratos offline 12C.2 e testes unitários da PoC: **52/52 aprovados**, sem skips.
- Ruff nos três arquivos Python da fase e mypy no adaptador: aprovados sem alertas.
- Duração reportada pela suíte integrada principal: 32,164 s e 42,027 s. As suítes filhas de T24 estão incluídas no tempo de cada invocação.

Comandos de teste executados no runner Python isolado:

```text
python -m unittest -v integration_tests.test_mongodb_editorial_revision_integration
python -m unittest -v unit_tests.test_editorial_revision_protocol unit_tests.test_mongodb_editorial_revision_adapter unit_tests.test_editorial_generations_poc
```

Na integração, `EDITORIAL_REVISION_TEST_URI` foi definido explicitamente para o MongoDB local da fase; não foi herdado de configuração da aplicação.

## Defeitos da fixture encontrados e corrigidos

As primeiras tentativas completas identificaram dois defeitos em T24, não no adaptador:

1. O subprocesso tentava carregar o módulo pelo pacote `unit_tests`, mas o arquivo está em `integration_tests`.
2. O ambiente mínimo do subprocesso descartava `PYTHONPATH`, necessário para o runner isolado.

O teste agora usa o pacote correto e propaga `PYTHONPATH` somente quando definido. Após as correções, duas invocações completas passaram, incluindo a reexecução. Nenhuma assertion de protocolo foi relaxada.

## Matriz resumida de evidências

| Propriedade | MongoDB real | Multiprocesso | Resultado |
|---|---|---|---|
| Revisão monotônica | Sim | T23 | Aprovado |
| CAS | Sim | T4, T23 | Aprovado |
| Fencing | Sim | T6, T22 | Aprovado |
| Fencing sem revisão nova | Sim | Não necessário no cenário T7 | Aprovado |
| Idempotência e recibo | Sim | T9, T11 | Aprovado |
| Histórico persistente | Sim | T16 recria adaptador | Aprovado |
| Atomicidade transacional | Sim | Não é requisito do T17 | Aprovado para a falha injetada |
| Resposta perdida | Sim, exceção simulada após commit confirmado | T15 em novo adaptador | Aprovado para esse cenário |
| Isolamento entre trilhas | Sim | Não | Aprovado |
| Recuperação após reinício | Recriação do processo/adaptador, não do servidor | T9 | Aprovado somente para cliente/adaptador |

## Limitações e gates

O replica set tem um único membro: `w: majority` representa a confirmação no único membro e não fornece tolerância a perda de nó ou failover. Não foram testados reinício do servidor, failover, partição de rede, perda de resposta no protocolo de commit do driver com `UnknownTransactionCommitResult`, nem grants/roles de produção. O cenário T15 perde a resposta no chamador depois que o adaptador retornou commit confirmado.

O adaptador usa capabilities sintéticas; isso não comprova IAM MongoDB, isolamento de roles ou controle de escritores reais. Não houve integração FastAPI, migração, publicação ou alteração de dados reais.

G2 permanece `NOT_VERIFIED` porque ainda faltam persistência em topologia operacional pertinente, cobertura de writers reais, compatibilidade e revisão de integração. G1 permanece `PARTIAL`; G9 e G10 permanecem `BLOCKED`. A matriz histórica não foi alterada.

## Limpeza

Após as duas suítes, o comando de listagem do servidor não encontrou bancos `editorial_revision_test_*`. Foram parados e removidos somente o container rotulado da fase, seu volume anônimo `/data/configdb`, a rede interna e os volumes nomeados de dados e dependências rotulados da fase. A conferência posterior não encontrou containers, redes ou volumes com a label `org.trilhacode.phase=2.1A.12C.3`. As imagens oficiais preexistentes foram mantidas. O Docker Desktop global ficou em execução para não interromper serviços fora do escopo.

## Arquivos relacionados

- [Adaptador persistente](../../backend/curriculum_contract/mongodb_editorial_revision_adapter.py)
- [Suíte de integração](../../backend/integration_tests/test_mongodb_editorial_revision_integration.py)
- [Testes offline](../../backend/unit_tests/test_mongodb_editorial_revision_adapter.py)
- [Protocolo em memória](../../backend/curriculum_contract/editorial_revision_protocol.py)
- [Relatório final](./editorial-generations-phase-2-1a-12c3-final-report.md)
