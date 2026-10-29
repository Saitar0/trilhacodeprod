# Beta 2 — prova persistente isolada

## Ambiente e isolamento

- MongoDB `7.0.43`, replica set de nó único `rsBeta2`, WiredTiger.
- Container: `trilhacode-beta2-curriculum-mongo` (`9ba91c835f252e856d7d88282918aabca7c3f8cd58e47f5eb6687c26d14b1e9f`).
- Rede dedicada: `trilhacode-beta2-curriculum-net` (`4a2954e431b4ce49c5098041ea9a2a88785a0b4d2e74734858c0e38d574f0a99`), sem masquerade de saída.
- Única porta publicada: `127.0.0.1:27149`; sem conflito com 27017 ou portas de outras fases.
- `/data/db` e `/data/configdb` em tmpfs; nenhum volume/bind mount; sem autenticação ou credenciais operacionais.
- URI aceita pelo harness somente no host/porta local definidos, sem usuário/senha e com replica set exato.
- Banco com nome aleatório `beta2_curriculum_import_<token>` e marcador de propriedade da fase.

## Caminho exercitado

O teste invoca o `backend/services/imports.py::run_import` versionado, não chama a rota e não faz inserts manuais de trilha/blocos. Apenas os documentos mínimos de `block_types` e das três taxonomias reais referenciadas foram preparados como cópias sintéticas do seed. O ator é um admin sintético; nenhum token/JWT real é criado.

Resultados observados no mesmo teste:

1. `dry_run` do serviço real aprovou o payload com avisos sobre campos do quiz versionado que o metadata do editor genérico não declara.
2. A execução gravou 1 trilha privada em `draft`, 1 nó `submodule` em `draft`, 12 blocos em `draft` e 1 evento de auditoria de importação.
3. A leitura via `nodes.get_track_tree` e `nodes.get_node` retornou a estrutura, IDs e ordem persistidos.
4. Repetir exatamente o payload retornou replay idempotente; continuaram existindo 1 trilha, 1 nó, 12 blocos e 1 auditoria.
5. Leitura de estudante foi negada pelo serviço real, pois a trilha continua privada e em rascunho.
6. Os gabaritos de quiz permanecem no documento staff em draft; funções reais `normalize_quiz`, `public_activity` e `_student_block` foram testadas offline para conferir projeção sem resposta. Não houve publicação.
7. Gabaritos privados de exercício, critério de conclusão e descrição de referências não foram enviados/persistidos pelo conversor.

O serviço de importação tem job/lease e retomada, mas grava em múltiplas fases sem transação global. A prova não demonstra falhas parciais/recuperação operacional, autorização real, rota, E2E, frontend nem publicação. O `run_import` legado não substitui o protocolo editorial C8–C16 e não pode ser habilitado em produção por este resultado.

## Resultado de testes e limpeza

- Conversor offline: 9 aprovados.
- Prova MongoDB/importador/leitores: 1 aprovado.
- Regressões offline selecionadas: 148 aprovadas e 2 subtests aprovados.
- Testes persistentes históricos C7–C16 não foram reexecutados nem tiveram recursos reutilizados.
- A execução padrão sem isolamento de `conftest` falhou na coleta porque o ambiente C14 não tem `httpx`. Para esta prova, testes selecionados foram executados com `--confcutdir`, evitando fixtures que poderiam escolher banco fora do harness. Nenhuma instalação foi feita no Python global ou em venv de outra fase.
- Uma invocação final sem a variável local da URI foi recusada pelo harness antes de abrir conexão; a repetição com a URI loopback aprovada passou. O caso não alcançou qualquer banco.
- Após as verificações finais, o container `9ba91c835f252e856d7d88282918aabca7c3f8cd58e47f5eb6687c26d14b1e9f` e a rede `4a2954e431b4ce49c5098041ea9a2a88785a0b4d2e74734858c0e38d574f0a99` foram removidos após confirmação de propriedade Beta 2. Nenhum banco persistente da fase foi mantido.
