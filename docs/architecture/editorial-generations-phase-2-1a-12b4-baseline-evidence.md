# Fase 2.1A.12B.4 — evidências de baseline e rastreabilidade de implantação

**Data da consulta:** 2026-10-28 14:13 UTC.
**Natureza:** investigação somente leitura.
**Conclusão principal:** **BASELINE IMPLANTADO NÃO COMPROVADO**.

## Escopo e método

Foram consultados os objetos Git locais e as referências públicas do GitHub para Saitar0/trilhacodeprod, além dos workflows e da documentação versionada de implantação. Não foram consultados Coolify, hosts, Docker da infraestrutura, endpoints privados, bancos ou secrets. Os SHAs e runs abaixo representam observações de leitura feitas nesta data; não demonstram o estado posterior a ela.

Referências examinadas:

| Elemento | Identidade observada | Nível |
|---|---|---|
| Branch padrão pública | main, SHA 22dca64556338a8fa9aaa89ce627a4f4af72317d | 4 — referência Git |
| Branch pública staging | SHA fff85218fd71b164dc7465ca72d22b4a53232f49 | 4 — referência Git |
| Snapshot técnico auditado | e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636; objeto local, pai 8a087fd5baa9e2eaa98bc1d2ed52b4a60f8c7036 | 4 — referência Git local |
| Commit documental B3 | 45fa5c5ff81982f7b784753e31a1dda0ce56cf5f; pai 4805e3caab18f183c37375d23af1b2e12a425d1b | 4 — documentação |
| Executor independente | main em 701b314230af3a87765a08671e1b69fd7b9864ac; transport.enabled=false | 4 — estado do executor, não da aplicação |

O commit B3 preserva a árvore técnica do snapshot e5bf3147… nas áreas comparadas (backend, frontend, .github, ops e Compose); sua finalidade foi documental. Isso não torna o snapshot uma versão implantada.

## Hierarquia de evidências aplicada

| Nível | Evidência necessária | Resultado nesta investigação |
|---|---|---|
| 1 — implantação comprovada | Digest imutável da imagem efetivamente em execução por ambiente, ligado a proveniência verificável do build e registro de implantação/saúde | Não disponível; nenhum container ou painel foi consultado |
| 2 — build comprovado | Run concluído ligado a um SHA; quando aplicável, digest do artefato de saída | Há builds ligados a SHAs; digest da imagem não foi recuperado das respostas públicas examinadas |
| 3 — configuração de implantação | Configuração versionada ou declarada de branch, build e destino | DEPLOY.md descreve API e frontend separados, produção acompanhando main, staging acompanhando staging, e deploy por webhook manual; descreve intenção/procedimento, não configuração efetiva atual |
| 4 — referência Git | HEAD remoto ou commit existente | main, staging e snapshot técnico foram identificados |
| 5 — hipótese | Inferência sem cadeia verificável | Qualquer afirmação de que um dos SHAs acima está hoje servindo usuários |

## Rastreamento de ambiente e artefatos

| Ambiente / artefato | Fonte e data | Commit | Build | Imagem | Digest | Deploy | Confiança |
|---|---|---|---|---|---|---|---|
| Produção | DEPLOY.md:3, 20-22, 44-55, 126-139; documentação versionada | NÃO COMPROVADO | NÃO COMPROVADO para a imagem atualmente implantada | NÃO COMPROVADO | NÃO COMPROVADO | NÃO COMPROVADO | Nível 3 para o procedimento; implantação real sem evidência de nível 1 |
| Staging | Mesma documentação; mapeamento pretendido de branch | NÃO COMPROVADO | NÃO COMPROVADO para a imagem atualmente implantada | NÃO COMPROVADO | NÃO COMPROVADO | NÃO COMPROVADO | Nível 3 para o procedimento; implantação real sem evidência de nível 1 |
| CI de main | Run 40488544210, push de 2026-10-27 10:26:57 UTC, SHA 22dca645… | 22dca645… | Backend, frontend e E2E concluíram; imagens foram construídas no runner | Tags locais de CI, não artefato implantado | NÃO COMPROVADO | Jobs deploy-staging e deploy-production foram skipped | Nível 2 para checks/build local; não é deploy |
| CI de staging | Run 40394870286, push de 2026-10-26 20:21:16 UTC, SHA fff85218… | fff85218… | Backend, frontend e E2E concluíram | Imagens de CI não comprovam imagem ativa | NÃO COMPROVADO | Jobs de deploy foram skipped | Nível 2 para checks/build local; não é deploy |
| Publicação de imagem backend | Run 39179762892, workflow manual G2, 2026-10-19, SHA 41dc470c567bae50b7ebcf0662d45d43863980c9 | 41dc470… | Job e passo de build/push para GHCR concluíram; passo de registro de digest concluiu | ghcr.io/saitar0/trilhacodeprod-backend:g2-41dc470… conforme workflow versionado | NÃO COMPROVADO nesta consulta | O workflow declara que não realiza deploy; não prova pull nem execução | Nível 2 — build/push de backend |
| Build local de backend | Run 38979959967, 2026-10-16, SHA 17b3bf1b26f69b0a5f4fed6f98c80b189b3b05e4 | 17b3bf1… | Build local e inspeção de imagem no runner concluíram | Imagem local efêmera do runner | NÃO COMPROVADO | Workflow informa explicitamente que imagem não foi publicada nem implantada | Nível 2 limitado ao build no runner |
| Protocolo experimental | Run 40686021030, MongoDB descartável 7.0.45 | Código de pacote 8a087fd…; SHA de executor documentado em B3 | 15/15 testes integrados da PoC e demais verificações informadas | Harness de homologação independente | Não é imagem da aplicação | Não é deploy | Homologa a PoC; nenhuma evidência de runtime da aplicação |

### Limites dos metadados públicos

O endpoint público de workflows listou 197 runs do workflow “CI and Coolify deploy”; foram examinadas as duas páginas que compunham essa contagem. Os runs de main e staging descritos acima foram pushes e tiveram os dois jobs de deploy ignorados. Nenhum workflow_dispatch desse workflow apareceu na listagem consultada. Isso não prova o estado do Coolify nem exclui deployments acionados fora desse workflow.

O run G2 39179762892 confirma que houve um build e push de imagem de backend associado a 41dc470…. A resposta pública de check-runs não continha o digest; nenhum log privado, package registry privado ou painel foi consultado para tentar recuperá-lo. Mesmo com o digest de build, ainda seria necessário demonstrar que aquele digest foi implantado e permanece em execução.

## Decisão sobre o baseline implantado

Não há cadeia verificável entre:

1. commit de origem;
2. build e digest imutável de API e frontend;
3. seleção do digest no ambiente;
4. execução saudável desse digest no ambiente acessível aos usuários.

Portanto, não se deve declarar main, staging, e5bf3147…, 41dc470… ou qualquer outro SHA como baseline implantado.

### Evidência mínima necessária para fechar a lacuna

Com autorização separada e participação do responsável de infraestrutura, obter para cada ambiente:

1. registro de implantação com horário UTC e recurso/serviço identificado;
2. referência imutável da imagem em execução (digest, não apenas tag);
3. metadados de build que associem digest, repositório, SHA completo, Dockerfile e workflow/run;
4. evidência de saúde/readiness após a implantação;
5. identificação separada de API e frontend, pois são aplicações independentes;
6. confirmação se houve deploy manual fora do workflow ou mudança posterior.

Os artefatos devem ser sanitizados e não conter URI, token, variável secreta ou dado de aluno. Esta investigação não solicita nem autoriza acesso à infraestrutura privada.

## Fontes locais verificadas

- [Repositório principal](https://github.com/Saitar0/trilhacodeprod), branches [main](https://github.com/Saitar0/trilhacodeprod/tree/main) e [staging](https://github.com/Saitar0/trilhacodeprod/tree/staging).
- [Run CI de main 40488544210](https://github.com/Saitar0/trilhacodeprod/actions/runs/40488544210) e [run CI de staging 40394870286](https://github.com/Saitar0/trilhacodeprod/actions/runs/40394870286).
- [Publicação de imagem backend 39179762892](https://github.com/Saitar0/trilhacodeprod/actions/runs/39179762892) e [build local 38979959967](https://github.com/Saitar0/trilhacodeprod/actions/runs/38979959967).
- [Homologação isolada da PoC 40686021030](https://github.com/Saitar0/trilhacode-mongodb-homologation/actions/runs/40686021030).

- DEPLOY.md:3,20-22,44-55,126-139: arquitetura e procedimento versionado; configuração efetiva não observada.
- .github/workflows/ci-deploy.yml:1-18,102-105,228-258: triggers, checks e condições dos webhooks de staging/produção.
- .github/workflows/g2-publish-backend-ghcr.yml:1-74: build/push manual de backend separado de deploy e gravação pretendida de digest no resumo.
- .github/workflows/g2-manual-backend-build.yml:1-61: build somente no runner, sem publicação/deploy.
- backend/Dockerfile.prod:1-13: imagem Python 3.11; não contém label de SHA/digest de runtime visível neste arquivo.
- compose.yaml:1-76: Compose de desenvolvimento, com volume Mongo nomeado e aplicação; documentação proíbe seu uso como configuração de produção.
- Auditoria B2: editorial-generations-phase-2-1a-12b2-audit.md:203-209.

**Estado:** baseline implantado pendente de evidência autorizada de nível 1. Não acessar infraestrutura privada é um limite desta autorização, não uma falha a contornar.
