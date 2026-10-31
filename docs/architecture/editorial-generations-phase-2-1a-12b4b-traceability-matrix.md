# Fase 2.1A.12B.4B — matriz de rastreabilidade

**Janela observada:** Coolify em 2026-10-28 ~15:35 UTC; Git/GitHub e tentativa de consulta ao GHCR em ~15:36 UTC.
`NÃO COMPROVADO` significa que nenhuma fonte autorizada forneceu evidência suficiente; não é uma inferência negativa.

| Ambiente/recurso | Serviço / ID | Deployment / commit | Runtime / imagem | Digest ativo | Build | Rota | Tráfego | Confiança |
|---|---|---|---|---|---|---|---|---|
| Staging | API `skmrkg3jb1ifhx0qwwneeirx`; status Coolify `running:healthy`; container presence reportada | `yhhbs4g2qzypxbofndtu8toz`; deployment finished; commit `fff85218fd71b164dc7465ca72d22b4a53232f49` | ID do container: NÃO COMPROVADO; imagem configurada/ativa: NÃO COMPROVADO | NÃO COMPROVADO | Build que originou a imagem corrente: NÃO COMPROVADO | FQDN configurado; rota ativa NÃO COMPROVADA | NÃO COMPROVADO | Configuração observada; deployment histórico confirmado; runtime/digest/rota/tráfego não comprovados |
| Staging | Frontend `dcdudgprerqp8wbmgcxvfwmt`; status Coolify `running:healthy`; container presence reportada | `xl0tceppzoqobc20xigzlnoh`; deployment finished; mesmo commit `fff85218fd71b164dc7465ca72d22b4a53232f49` | ID do container: NÃO COMPROVADO; imagem configurada/ativa: NÃO COMPROVADO | NÃO COMPROVADO | Build que originou a imagem corrente: NÃO COMPROVADO | FQDN configurado; rota ativa NÃO COMPROVADA | NÃO COMPROVADO | Configuração observada; deployment histórico confirmado; runtime/digest/rota/tráfego não comprovados |
| Ambiente não classificado (`general`) | `trilhacode` `xm3mpex5rerhlbbuydpwf5wa`; `starting:unknown` | `ywtadtdspygsff5zmk18wfxp`; failed; commit `22dca64556338a8fa9aaa89ce627a4f4af72317d` | Presença reportada, mas identidade/estado do container e imagem: NÃO COMPROVADO | NÃO COMPROVADO | Build ativo: NÃO COMPROVADO | FQDN não observado | NÃO COMPROVADO | Recurso/configuração observados; ambiente de produção não comprovado |
| Build G2 (não é ambiente) | `ghcr.io/saitar0/trilhacodeprod-backend:g2-41dc470c567bae50b7ebcf0662d45d43863980c9` | Run `39179762892`, job `117829823005`; commit `41dc470c567bae50b7ebcf0662d45d43863980c9` | Nenhuma associação a runtime | Digest OCI: NÃO COMPROVADO | Build/push concluídos; artifact `.dockerbuild` tem digest de artifact GitHub `sha256:333eca7dd8391af88863811e09b777a056a58f47b2af5ab25512859110653c4f` (não é digest da imagem) | Não aplicável | Não aplicável | CONFIRMADO_BUILD; não é prova de implantação |

## Campos comuns de correlação

| Campo | Resultado desta fase |
|---|---|
| `environment_id` | Projeto Trilha Code em staging identificado; UUID de environment não necessário/exposto nesta coleta; produção não identificada |
| `service_id` | IDs de application acima; nenhum `service` Coolify separado retornado no projeto Trilha Code |
| `deployment_id` | IDs históricos acima; nenhum deployment queued/in-progress observado |
| `runtime_container_id` | NÃO COMPROVADO |
| `running_image_reference` | NÃO COMPROVADO |
| `running_image_digest` | NÃO COMPROVADO |
| `registry_artifact_digest` | NÃO COMPROVADO para imagem G2; GHCR anônimo respondeu 401 |
| `build_run_id` | `39179762892` somente para build G2 |
| `source_commit_sha` | Confirmado para cada execução/build acima, mas não correlacionado a runtime atual |
| `route_id` | NÃO COMPROVADO |
| `observed_at` | 2026-10-28 ~15:35–15:36 UTC |

## Fontes, limitações e contradições

Fontes: Coolify MCP somente leitura (`list_applications`, `list_services`, `list_deployments`, `get_application`, `get_deployment` sem logs e `list_rollback_images`); GitHub Actions metadata (`github_fetch_workflow_job_steps`, `github_fetch_workflow_run_artifacts`); GET anônimo de manifesto GHCR; `git ls-remote` para branches. Nenhuma resposta bruta completa foi arquivada.

O selector `HEAD` e a branch configurada descrevem origem selecionada, não o SHA ativo. `running:healthy` conflita semanticamente com healthcheck desabilitado apenas se interpretado como readiness; este relatório não faz essa interpretação. A tag do inventário de rollback foi marcada `is_current=false`. O deployment `trilhacode` falhou e não estabelece identidade de produção. O build G2 não tem ligação demonstrada com as apps de staging.
