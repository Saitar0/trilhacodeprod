# Fase 2.1A.12B.4B — evidências de runtime

**Observação:** 2026-10-28, aproximadamente 15:35 UTC (Coolify); referências Git verificadas às 15:36 UTC.
**Escopo:** consultas de metadados somente leitura. Nenhum comando foi executado em container/host e nenhuma configuração foi alterada.

## Critério de leitura

Este documento separa o estado reportado pela plataforma da identidade de uma imagem efetivamente em execução. `running:healthy`, `container_present` e `server_status` são campos reportados pelo Coolify; não identificam por si sós um container, digest OCI, readiness ou tráfego. Os valores de domínio foram deliberadamente omitidos; somente a presença de configuração foi registrada.

## Recursos encontrados

| Recurso | Identidade e configuração observadas | Último deployment visível | Estado observado | Conclusão |
|---|---|---|---|---|
| `trilhacode-staging-api` | Projeto Trilha Code; app `skmrkg3jb1ifhx0qwwneeirx`; repositório `Saitar0/trilhacodeprod`; branch configurada `staging`; seletor de commit `HEAD`; build pack Dockerfile; porta interna 8000; FQDN configurado (valor omitido) | `yhhbs4g2qzypxbofndtu8toz`; `fff85218fd71b164dc7465ca72d22b4a53232f49`; finished em 2026-10-26 20:30:04–20:31:06 UTC | `running:healthy`; `container_present=true`; `server_status=true`; `last_online_at=2026-10-28 15:34:08 UTC`; healthcheck desabilitado | App de staging e presença reportada pelo Coolify confirmadas. Container/imagem/digest ativos e atendimento de tráfego não comprovados. |
| `trilhacode-staging-frontend` | Projeto Trilha Code; app `dcdudgprerqp8wbmgcxvfwmt`; mesmo repositório e branch `staging`; seletor `HEAD`; build pack Dockerfile; porta interna 8080; FQDN configurado (valor omitido) | `xl0tceppzoqobc20xigzlnoh`; `fff85218fd71b164dc7465ca72d22b4a53232f49`; finished em 2026-10-26 20:21:16–20:23:23 UTC | `running:healthy`; `container_present=true`; `server_status=true`; `last_online_at=2026-10-28 15:34:08 UTC`; healthcheck desabilitado | App de frontend de staging e presença reportada confirmadas. Container/imagem/digest ativos e atendimento de tráfego não comprovados. |
| `trilhacode` (candidato) | App `xm3mpex5rerhlbbuydpwf5wa`, projeto `general`; repositório principal; branch `main`; seletor `HEAD`; build pack Docker Compose; porta interna 3000; sem FQDN observado | `ywtadtdspygsff5zmk18wfxp`; `22dca64556338a8fa9aaa89ce627a4f4af72317d`; failed em 2026-10-27 10:26:56–10:31:42 UTC | `starting:unknown`; `container_present=true`; `server_status=true`; healthcheck desabilitado | Associação à produção não demonstrada. Não classificar como produção pela branch `main` ou pelo nome. Estado de container não correlacionado ao deployment falho. |

A consulta do projeto Trilha Code retornou duas applications e zero services. A lista de deployments não mostrou execução queued/in-progress no instante observado. Isso não demonstra que não existam workers ou serviços da aplicação em outros projetos/escopos.

## O que o Coolify não expôs nas consultas

Nos detalhes de applications e deployments consultados, os campos de referência de imagem do registry estavam vazios ou ausentes (`docker_registry_image_name/tag` nulos); não foi retornado identificador de container, image ID, digest de manifesto, digest de índice OCI, nem vínculo do container atual a um deployment específico. O campo de commit configurado era `HEAD`, isto é, um seletor móvel da branch, e não um SHA de runtime.

O inventário de rollback das duas apps de staging listou a tag local `fff85218fd71b164dc7465ca72d22b4a53232f49` com `is_current=false`, sem digest. Esse dado é apenas inventário de rollback; não identifica a imagem ativa.

Os detalhes de deployment foram consultados sem resumo de logs. Não houve consulta a logs brutos, variáveis, secrets, shell de container, host ou daemon Docker.

## Classificação da evidência

* **CONFIGURACAO_OBSERVADA:** aplicações de staging, repositório, branch, seletor `HEAD`, portas e presença de FQDN configurado.
* **Sinal administrativo do Coolify:** `running:healthy`, container presente e `server_status=true` para as duas apps de staging. Como o healthcheck estava desabilitado, isso não comprova liveness/readiness da aplicação.
* **CONFIRMADO_BUILD:** deployment histórico de staging terminou com o SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`; não prova que esse SHA ainda atende tráfego.
* **NÃO COMPROVADO:** identidade de runtime → imagem OCI → digest → build → commit para as apps atualmente presentes.
* **NÃO COMPROVADO:** serviço de produção, rota ativa e tráfego atendido.

## Fontes e limites

Fontes: Coolify MCP, consultas `list_applications`, `list_services`, `list_deployments`, `get_application`, `get_deployment` sem logs e `list_rollback_images`, limitadas aos recursos Trilha Code já identificados. A leitura atual é um retrato de metadados e pode mudar após a observação. Não foram consultados servidores, proxy, DNS, páginas de environment variables ou endpoints privados da aplicação.

Ver também [matriz de rastreabilidade](./editorial-generations-phase-2-1a-12b4b-traceability-matrix.md), [roteamento](./editorial-generations-phase-2-1a-12b4b-routing-evidence.md) e [pedido sanitizado ao administrador](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md).
