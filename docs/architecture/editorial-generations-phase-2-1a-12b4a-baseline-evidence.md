# Fase 2.1A.12B.4A — matriz de evidências do baseline

**Observação Coolify:** 2026-10-28 15:15 UTC.
**Observação GitHub/refs:** 2026-10-28 15:11:56 UTC.
**Conclusão:** baseline de runtime ainda não comprovado integralmente; evidência parcial de deploy para staging.

## Matriz de rastreabilidade

| Ambiente/serviço | Estado | Digest ativo | Build/deployment | Commit | Evidência e confiança |
|---|---|---|---|---|---|
| Staging / API | Coolify `running:healthy`; `container_present=true`; health check desabilitado | **NÃO COMPROVADO** | Deployment `yhhbs4g2qzypxbofndtu8toz` finalizado em 2026-10-26 20:31:06 UTC | `fff85218fd71b164dc7465ca72d22b4a53232f49` no registro do deployment; commit ativo **NÃO COMPROVADO** | **CONFIGURAÇÃO OBSERVADA** e **deploy concluído reportado**. Estado e commit do último deploy não provam imagem ativa ou tráfego. |
| Staging / frontend | Coolify `running:healthy`; `container_present=true`; health check desabilitado | **NÃO COMPROVADO** | Deployment `xl0tceppzoqobc20xigzlnoh` finalizado em 2026-10-26 20:23:23 UTC | `fff85218fd71b164dc7465ca72d22b4a53232f49` no registro; commit ativo **NÃO COMPROVADO** | **CONFIGURAÇÃO OBSERVADA** e **deploy concluído reportado**. A imagem servida não está identificada. |
| Produção / serviço | **NÃO COMPROVADO** | **NÃO COMPROVADO** | **NÃO COMPROVADO** | **COMMIT DE ORIGEM NÃO COMPROVADO** | A documentação versionada descreve produção em `main`, mas o único candidato Coolify encontrado no projeto `general` está `starting:unknown`, sem FQDN, e seu último deployment `ywtadtdspygsff5zmk18wfxp` falhou. Não foi classificado como produção. |
| Build GHCR G2 / backend | Não é serviço implantado | Digest publicado **NÃO COMPROVADO nesta consulta** | Run `39179762892`, job `117829823005`, etapa de build/push bem-sucedida | `41dc470c567bae50b7ebcf0662d45d43863980c9` | **CONFIRMADO — BUILD** (associação do run e workflow); deployment não comprovado. |

Os registros Coolify retornaram `docker_registry_image_name=null` e `docker_registry_image_tag=null` para as aplicações. Os registros de deployment não continham digest nem referência de imagem. A lista de rollback de cada app de staging mostrava apenas uma tag local `fff85218...` com `is_current=false`; esse dado não identifica o runtime atual.

## Estado por nível de confiança

| Nível | Resultado |
|---|---|
| **CONFIRMADO — RUNTIME** | Nenhum ambiente: não foi possível ligar uma instância efetivamente ativa a digest imutável e rota de tráfego. |
| **CONFIRMADO — PROVENIÊNCIA** | Nenhuma imagem ativa com proveniência verificável até o commit foi demonstrada. |
| **CONFIRMADO — BUILD** | Run G2 de publicação de imagem associado a `41dc470c567bae50b7ebcf0662d45d43863980c9`; o digest não foi exposto na resposta de metadados consultada. Os runs CI de `main` e `staging` construíram imagens nos runners, mas seus jobs de deploy foram ignorados. |
| **CONFIGURAÇÃO OBSERVADA** | Branches Git configuradas no Coolify: `main` para o recurso candidato `trilhacode` e `staging` para as aplicações API/frontend de staging; seletor reportado `HEAD`. |
| **INFERIDO** | Os serviços de staging podem corresponder ao SHA fff registrado em seus deploys concluídos, mas o catálogo de rollback marca a tag correspondente `is_current=false` e a plataforma não expõe o vínculo com o container/rota. Não usar como baseline aprovado. |
| **NÃO COMPROVADO** | Digest da imagem ativa em staging/produção; digest G2 consultado; identidade da aplicação de produção; associação container → deployment → tráfego; versão efetivamente acessível a usuários. |

## Evidências ausentes

Para fechar o baseline por serviço e ambiente, ainda são necessários, em forma sanitizada e mediante autorização apropriada:

1. Identificação explícita dos recursos Coolify que correspondem a produção e staging, incluindo API, frontend e eventuais workers.
2. Referência imutável (digest OCI completo, com distinção de índice/plataforma) associada a cada serviço/instância que esteja ativa.
3. Associação verificável entre o digest ativo, o registro de deployment e o SHA completo utilizado no build; preferencialmente provenance/attestation verificável.
4. Evidência de que a instância identificada está associada à rota ativa de tráfego, e não apenas presente/saudável ou disponível para rollback.
5. Estado de readiness ligado ao serviço e à revisão observada. Não é necessário fornecer payloads, logs ou variáveis secretas.
6. Para a imagem G2: valor do digest registrado no resumo/provenance do run, sem fornecer logs brutos.

Não é necessário nem solicitado acesso a MongoDB, conteúdo de alunos, secrets, shell, Docker CLI ou logs não sanitizados.

## Baseline atual e candidatos

- **Baseline implantado de produção:** `NÃO COMPROVADO`.
- **Baseline de runtime de staging:** `NÃO COMPROVADO`; existe evidência parcial de deployments Coolify concluídos para API e frontend no SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`, seguida por estado `running:healthy` reportado, sem digest/rota e com check ativo desabilitado.
- **Candidato de validação técnica:** o SHA de deployment `fff852...` é a referência mais próxima de uma revisão observada em serviço de staging, mas só pode ser selecionado após o responsável confirmar o serviço, digest e objetivo da validação.
- **Snapshot e5bf3147...:** continua sendo uma linha técnica de auditoria local; não aparece nos registros Coolify consultados e não é baseline implantado.

## Histórico documental

A evidência anterior em [B4 — baseline](editorial-generations-phase-2-1a-12b4-baseline-evidence.md) não consultava Coolify por restrição de acesso. Esta fase usou somente o conector autorizado de leitura e atualiza a conclusão para **baseline parcialmente evidenciado**, sem promover a hipótese de staging a `CONFIRMADO — RUNTIME`.
