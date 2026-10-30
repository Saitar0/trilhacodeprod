# Beta 8.4 — isolamento, limpeza e bloqueios restantes

## Ambiente e limpeza

O runner usa Docker local verificado, MongoDB 7.0.43 pinado em replica set descartável, rede bridge interna, sem portas publicadas, sem volumes de dados e com apenas um keyfile temporário do replica set montado como read-only. API, autoridade e verifier usam identidades sintéticas distintas; o root temporário fica restrito ao provisionador/verifier. O harness exige UUID/run labels, identidade de contêiner/rede, URI, credenciais, ausência de endpoints externos e composição experimental explícita antes de escrever.

O controlador revalida IDs/labels/papéis, rede e ausência de participantes externos antes do cleanup. Na execução concluída, contêineres, rede, imagem local e arquivos temporários próprios foram removidos e a consulta final por labels não encontrou recursos B8.4. Nenhum recurso de outras fases foi tocado. Não houve conexão a `localhost:27017`, produção ou staging operacional.

## Bloqueios não resolvidos

* Playwright da jornada das dez unidades: **NOT_RUN**.
* Suíte integral do backend e regressões históricas completas: **NOT_RUN**; o escopo seguro listado em [regressões](beta8-4-backend-regression-results.md) não substitui esse conjunto.
* Só W-07 PUT/POST e W-05 PUT foram exercitados através da autoridade; o inventário global de writers continua parcial.
* A chave HMAC compartilhada não isola a arquitetura de uma API totalmente comprometida. TLS, rotação e distribuição operacional de segredos não foram comprovados.
* A credencial da autoridade conserva escrita nas coleções necessárias; isolamento de processos no Docker não prova ACL/distribuição real de credenciais.
* Startup comum sem composição experimental continua sem essa capacidade editorial (fail-closed/503 no caminho selecionado); não foi habilitado fallback.
* Backup/restore, recuperação operacional, observabilidade, resposta a incidente, rollout/rollback e revisão independente de segurança permanecem pendentes.
* Rubrica real do projeto 3.5: **PROPOSED**; nenhuma decisão pedagógica alterada.
* ADR-008: **BLOCKED**. Nenhuma publicação ou promoção operacional ocorreu.

## Próximo incremento mínimo

Integrar uma composição Playwright isolada à prévia autorizada existente, com frontend real, API e autoridade separadas, sem publicar a trilha; em paralelo, preparar a etapa autorizada de confirmação operacional para distribuição/ACL de credenciais e reconciliar writers restantes por operação antes de reavaliar ADR-008.
