# Fase 2.1A.12B.4B — relatório final

## A. Resumo executivo

As consultas de leitura confirmaram metadados de duas applications de staging e um build G2, mas não fecharam a cadeia solicitada. Coolify reporta API e frontend de staging como `running:healthy`; healthchecks estavam desabilitados, nenhum ID de container ou digest ativo foi exposto, e não houve prova de rota ativa ou tráfego. O GHCR não permitiu consulta anônima do manifesto (401). O build G2 está ligado ao SHA `41dc470c567bae50b7ebcf0662d45d43863980c9`, mas não a runtime. O recurso `trilhacode` no projeto `general` não pode ser declarado produção.

**Veredito:** BASELINE PARCIALMENTE COMPROVADO — há configuração, deployments históricos e build; baseline de produção, digest/runtime atual, rota ativa e tráfego permanecem não comprovados. ADR-008 continua Proposed/PENDING_APPROVAL.

## B. Git e isolamento

* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b4b-runtime-provenance-routing\trilhacodeprod`.
* Branch: `codex/fase2-1a-12b4b-runtime-provenance-routing`.
* Base: `22f1b0df56d4bf5c0a35611db98523b54e5eca76`.
* `main` remoto observado: `22dca64556338a8fa9aaa89ce627a4f4af72317d`.
* `staging` remoto observado: `fff85218fd71b164dc7465ca72d22b4a53232f49`.
* A comparação remota foi somente `git ls-remote`; não houve fetch/push ou alteração de referência.

## C–H. Fontes, serviços e artefatos

Fontes Coolify: listagens de applications, services e deployments; detalhes de três apps, três deployments e inventário de rollback, sem logs. Duas apps de staging foram identificadas. Um recurso `trilhacode` do projeto `general` foi mantido como candidato não classificado. Não houve serviço separado listado no projeto Trilha Code.

Build G2: run `39179762892`, job `117829823005`, commit `41dc470c567bae50b7ebcf0662d45d43863980c9`, tag `g2-41dc470c567bae50b7ebcf0662d45d43863980c9`; build/push e step de registro de digest concluíram. Digest OCI da imagem não recuperado. O campo `digest` `sha256:333eca7dd8391af88863811e09b777a056a58f47b2af5ab25512859110653c4f` pertence ao artifact `.dockerbuild` de 45.941 bytes do Actions, não à imagem OCI. A consulta GET anônima do manifesto GHCR respondeu 401; nenhuma autenticação foi tentada.

## I–M. Cadeia e roteamento

Para staging, a cadeia chega a deployment histórico e commit, não ao container/imagem atual. O Coolify mostra FQDN configurado nas duas apps, porém não expôs regra ativa de proxy nem evidência de encaminhamento. Atendimento de tráfego não foi testado nem observado. Para produção, nem a identidade do recurso está confirmada. A matriz campo a campo está em [traceability-matrix](./editorial-generations-phase-2-1a-12b4b-traceability-matrix.md); evidências de runtime e rota estão em [runtime](./editorial-generations-phase-2-1a-12b4b-runtime-evidence.md) e [routing](./editorial-generations-phase-2-1a-12b4b-routing-evidence.md).

Status `running:healthy` coexistia com `health_check_enabled=false`; isso é status administrativo e não prova readiness. A API reportou `container_present=true` e `server_status=true`, mas sem ID/imagem/digest do container.

## N–Q. Confiança, produção, staging e Git

* Staging: `CONFIGURACAO_OBSERVADA` para apps, branch e FQDN; `CONFIRMADO_BUILD` para deployments históricos; `NÃO COMPROVADO` para runtime de imagem/digest, proveniência até runtime, rota ativa e tráfego.
* Produção: `NÃO COMPROVADO`. O candidato `trilhacode` usa branch configurada `main`, último deployment falhou, estado `starting:unknown`, sem FQDN observado; isso não autoriza classificá-lo como produção.
* GitHub Actions main run `40488544210` e staging run `40394870286` foram reportados na fase anterior com jobs de deploy ignorados; são builds/CI históricos, não prova de implantação atual.
* `git ls-remote` confirma que os SHAs informados de main e staging continuam atuais no momento da consulta. A linha auditada `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636` e a documentação `22f1b0df56d4bf5c0a35611db98523b54e5eca76` não foram identificadas como implantadas.

## R–S. ADR-008 e evidências faltantes

ADR-008 permanece **Proposed** e a decisão permanece **PENDING_APPROVAL**. São necessários: identidade explícita do serviço de produção; container e imagem/digest atualmente ativos em cada ambiente; associação container-deployment; proveniência OCI ligada ao SHA completo; regra de rota ativa; readiness e evidência agregada de tráfego; e seleção humana do ambiente/baseline para implementação.

O pedido sanitizado está em [admin-evidence-request](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md); gates e recomendação condicional estão em [adr008-gates](./editorial-generations-phase-2-1a-12b4b-adr008-gates.md).

## T–V. Segurança e operações

Consultas Coolify foram limitadas a metadados dos recursos relacionados. GitHub forneceu metadados de run, steps e artifact. O GHCR recebeu somente GET anônimo ao manifesto. Nenhum secret, variável, log bruto, dado pessoal, container shell, host, banco, endpoint da aplicação ou route probe foi consultado. Não houve operação de escrita remota, execução de workflow, mudança de serviço, deploy ou operação Docker/MongoDB.

Os diretórios `docs/courses/trilhacode/` e `docs/migracao/` permaneceram fora do sparse-checkout. Nenhum código executável foi alterado.

## W–X. Documentos e próxima ação

Foram preparados seis documentos de evidência e este relatório; após as validações documentais, eles serão registrados em commit local. A menor próxima ação é o administrador autorizado retornar a solicitação sanitizada, especialmente a associação digest OCI ↔ container ativo ↔ deployment e a regra ativa de roteamento. Até então, não selecionar baseline de implementação nem iniciar mudanças funcionais.

## Y. Veredito

**BASELINE PARCIALMENTE COMPROVADO.** A evidência suporta configuração e deployments históricos de staging e um build G2, mas não identifica a imagem ativa nem comprova produção, rota ativa ou tráfego. Nenhum ADR foi aprovado.
