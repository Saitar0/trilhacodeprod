# Fase 2.1A.12B.4A — inventário de runtime autorizado

**Observação Coolify:** 2026-10-28, aproximadamente 15:15 UTC. Os campos `updated_at` e `last_online_at` das aplicações consultadas eram 15:11:24 UTC.
**Método:** consultas de leitura pelo conector Coolify da equipe; nenhum log, variável de ambiente, segredo, terminal, host, container ou banco foi acessado.

## Escopo e fontes

Foram consultados `search_resources` para o nome do repositório, `list_applications` no projeto Coolify **Trilha Code**, `list_services` no mesmo projeto, `get_application`, `list_deployments`, `get_deployment` sem resumo de logs e `list_rollback_images`. A listagem de deployments em andamento/na fila retornou zero itens na observação.

O projeto **Trilha Code**, ambiente **staging**, retornou duas aplicações e nenhum serviço adicional. A busca por aplicações/serviços encontrou ainda uma aplicação chamada `trilhacode` no projeto genérico `general`; ela não foi identificada como produção. A consulta é limitada ao escopo acessível pelo conector e não prova que não existam recursos com outros nomes ou projetos.

## Recursos encontrados

| Ambiente observado | Aplicação | Identificador Coolify | Origem/branch configurada | Deployment mais recente registrado | Estado reportado | Limite da evidência |
|---|---|---|---|---|---|---|
| Staging | `trilhacode-staging-api` | `skmrkg3jb1ifhx0qwwneeirx` | `Saitar0/trilhacodeprod`, `staging`; seletor `HEAD` | `yhhbs4g2qzypxbofndtu8toz`, `finished`, SHA `fff85218fd71b164dc7465ca72d22b4a53232f49` | `running:healthy`; `container_present=true`; `last_online_at=2026-10-28 15:11:24 UTC` | Não há imagem/digest ativo nem associação explícita entre o deployment e o container reportado. O health check está desabilitado. |
| Staging | `trilhacode-staging-frontend` | `dcdudgprerqp8wbmgcxvfwmt` | `Saitar0/trilhacodeprod`, `staging`; seletor `HEAD` | `xl0tceppzoqobc20xigzlnoh`, `finished`, SHA `fff85218fd71b164dc7465ca72d22b4a53232f49` | `running:healthy`; `container_present=true`; `last_online_at=2026-10-28 15:11:24 UTC` | Mesmas limitações; domínio omitido. |
| Ambiente não identificado (projeto `general`) | `trilhacode` | `xm3mpex5rerhlbbuydpwf5wa` | `Saitar0/trilhacodeprod`, `main`; seletor `HEAD` | `ywtadtdspygsff5zmk18wfxp`, `failed`, SHA `22dca64556338a8fa9aaa89ce627a4f4af72317d` | `starting:unknown`; `container_present=true`; sem FQDN informado | Não classificar como produção: ambiente/rota não identificados e último deployment falhou. |

Os deployments de staging foram concluídos em 2026-10-26: API entre 20:30:04 e 20:31:06 UTC; frontend entre 20:21:16 e 20:23:23 UTC. A aplicação candidata `trilhacode` teve o último registro de deployment em 2026-10-27, entre 10:26:56 e 10:31:42 UTC, com resultado `failed`. O endpoint Coolify reportou zero deployments atualmente em andamento ou enfileirados às 15:15 UTC de 2026-10-28.

## Saúde e prontidão

Para API e frontend de staging, Coolify reportou `running:healthy`, servidor acessível e container presente. Porém, `health_check_enabled=false` em ambos, apesar de o campo de caminho conter `/health` para API e `/` para frontend. Assim, o rótulo da plataforma é evidência de estado reportado, não comprovação de uma probe ativa, readiness HTTP, associação ao tráfego ou versão servida. Nenhum endpoint da aplicação foi chamado.

Na aplicação `trilhacode`, Coolify reportou `starting:unknown`, health check desabilitado, caminho `/`, container presente e ausência de FQDN. Esses metadados não identificam sua função operacional.

## Escopo de privacidade

Valores de FQDN, configuração de ambiente, logs, nomes de secrets, URIs e payloads foram omitidos. Nenhuma página de variáveis ou secrets foi aberta. Identificadores de recurso e deployment acima são os metadados mínimos necessários para rastreabilidade.

## Referências versionadas

- [`DEPLOY.md`](../../DEPLOY.md):3 descreve API e frontend separados; :20–22 descreve a topologia pretendida de `staging` e `production`.
- [`ci-deploy.yml`](../../.github/workflows/ci-deploy.yml):228–258 condiciona os webhooks a um `workflow_dispatch` explícito na branch correspondente.
- [Relatório de baseline da Fase 2.1A.12B.4](editorial-generations-phase-2-1a-12b4-baseline-evidence.md) contém as observações Git e CI anteriores; esta fase acrescenta metadados Coolify de leitura.

**Conclusão do inventário:** há evidência de duas aplicações de staging reportadas como saudáveis e de uma aplicação candidata em `main` com último deployment falho. O inventário não comprova serviço de produção, worker, rota pública ativa nem versão efetivamente atendendo tráfego.
