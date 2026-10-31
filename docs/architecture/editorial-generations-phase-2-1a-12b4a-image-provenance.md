# Fase 2.1A.12B.4A — imagem e proveniência

**Data da consulta:** 2026-10-28.
**Escopo:** metadados de imagem/build retornados por Coolify e GitHub; nenhum log bruto, artifact baixado, registry autenticado ou container foi acessado.

## Cadeia por serviço

| Serviço | Configuração de origem | Registro de build/deploy | Referência de imagem | Digest ativo | Commit ligado ao registro | Conclusão |
|---|---|---|---|---|---|---|
| Staging API | Coolify informa repositório `Saitar0/trilhacodeprod`, branch `staging`, build pack `dockerfile` | Deployment Coolify `yhhbs4g2qzypxbofndtu8toz`, `finished` | Aplicação e deployment não retornaram `docker_registry_image_name`/`docker_registry_image_tag` preenchidos; inventário de rollback contém uma tag local `fff852...`, marcada `is_current=false` | **NÃO COMPROVADO** | SHA registrado no deployment: `fff85218fd71b164dc7465ca72d22b4a53232f49` | Deploy concluído reportado; não vincula digest ao runtime ativo. |
| Staging frontend | Mesma origem/branch, build pack `dockerfile` | Deployment Coolify `xl0tceppzoqobc20xigzlnoh`, `finished` | Sem referência ativa retornada; inventário de rollback lista tag local `fff852...`, `is_current=false` | **NÃO COMPROVADO** | SHA registrado no deployment: `fff85218fd71b164dc7465ca72d22b4a53232f49` | Deploy concluído reportado; não vincula digest ao runtime ativo. |
| Aplicação `trilhacode` (ambiente não identificado) | Repositório `Saitar0/trilhacodeprod`, branch `main`, build pack `dockercompose` | Deployment `ywtadtdspygsff5zmk18wfxp`, `failed` | Nome/tag não retornados; lista de rollback vazia | **NÃO COMPROVADO** | SHA registrado no deployment falho: `22dca64556338a8fa9aaa89ce627a4f4af72317d` | Não é evidência de versão de produção em execução. |

A lista de rollback informa imagens locais disponíveis para rollback, não identifica a imagem de um container ativo. O valor `is_current=false` impede tratar a tag `fff852...` como atual com base nessa fonte. Uma tag baseada em SHA também não substitui digest OCI.

## GitHub Actions e imagens produzidas

### CI de `main`

O run [40488544210](https://github.com/Saitar0/trilhacodeprod/actions/runs/40488544210) está ligado ao SHA `22dca64556338a8fa9aaa89ce627a4f4af72317d`. Os jobs de backend, frontend e E2E concluíram com sucesso; os jobs `deploy-staging` e `deploy-production` foram `skipped`. As imagens construídas pelo CI não constituem evidência de publicação ou implantação.

### CI de `staging`

O run [40394870286](https://github.com/Saitar0/trilhacodeprod/actions/runs/40394870286) está ligado ao SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`. Backend, frontend e E2E concluíram; os dois jobs de deploy foram `skipped`.

### Publicação manual G2 no GHCR

O run [39179762892](https://github.com/Saitar0/trilhacodeprod/actions/runs/39179762892), de 2026-10-19, está ligado ao commit `41dc470c567bae50b7ebcf0662d45d43863980c9`. Seu job `publish` (`117829823005`) e as etapas “Build and push backend image (not a deployment)” e “Record immutable image digest” concluíram com sucesso. O workflow versionado [`g2-publish-backend-ghcr.yml`](../../.github/workflows/g2-publish-backend-ghcr.yml):21–22 define a tag `ghcr.io/saitar0/trilhacodeprod-backend:g2-41dc470c567bae50b7ebcf0662d45d43863980c9`; :48–57 declara publicação no GHCR e provenance; :59–74 registra o digest pretendido no resumo do run e declara que não faz deploy.

O endpoint de jobs confirmou somente os estados das etapas, não o valor do digest. O catálogo de artifacts mostrou `Saitar0~trilhacodeprod~14ZTL7.dockerbuild`, com 45.941 bytes; o artifact não foi baixado nem inspecionado. Portanto:

- **CONFIRMADO — BUILD:** houve um job bem-sucedido de build/push de backend associado ao SHA completo `41dc470c567bae50b7ebcf0662d45d43863980c9` e à tag configurada no workflow.
- **NÃO COMPROVADO:** digest específico publicado, associação do digest a Coolify, deployment desse digest, permanência em execução ou atendimento de tráfego.

O deployment Coolify de API para o commit `41dc470c...` encontrado na listagem histórica terminou `failed` em 2026-10-19. Isso não estabelece relação com o build G2 bem-sucedido, nem prova que o artefato GHCR foi selecionado.

## Identificadores que não devem ser confundidos

1. **Branch configurada:** `main`/`staging` com seletor `HEAD`; muda conforme a branch avança.
2. **SHA de commit no registro de deployment:** identifica a origem que Coolify associou àquela tentativa; não identifica uma imagem ativa.
3. **Tag de imagem:** nome mutável ou tag local de rollback; não é digest.
4. **Digest de manifesto OCI:** identidade do conteúdo publicado no registry; pode representar um manifesto ou índice multi-arquitetura.
5. **Digest específico de plataforma / image ID local:** pode ser diferente do índice e requer mapeamento verificável.
6. **Container ativo e rota:** precisam de associação explícita ao digest e ao deployment; não estão expostos nos metadados consultados.

O [`Dockerfile.prod`](../../backend/Dockerfile.prod) e o workflow de publicação descrevem como construir uma imagem; não provam qual imagem existe no registry hoje nem qual está em execução.

## Cadeia resultante

Para staging há uma cadeia parcial `serviço Coolify → deployment concluído → SHA Git registrado`. Faltam `digest OCI → instância ativa → rota que recebe tráfego`. Para produção, nem o serviço de produção nem a cadeia de imagem foram identificados. Assim, não há cadeia completa `runtime → imagem/digest → build → commit` em nenhum ambiente.
