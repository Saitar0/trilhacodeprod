# Fase 2.1A.12B.4B — proveniência OCI

**Consulta:** metadados de workflow/artifact do GitHub e uma tentativa GET anônima ao endpoint de manifesto do GHCR; aproximadamente 2026-10-28 15:36 UTC. Nenhuma credencial foi usada.

## Build G2

| Campo | Evidência |
|---|---|
| Repositório | `Saitar0/trilhacodeprod` |
| Run | [39179762892](https://github.com/Saitar0/trilhacodeprod/actions/runs/39179762892) |
| Job | `publish`, ID `117829823005`, concluído com sucesso |
| Commit de origem do run | `41dc470c567bae50b7ebcf0662d45d43863980c9` |
| Tag configurada pelo workflow | `ghcr.io/saitar0/trilhacodeprod-backend:g2-41dc470c567bae50b7ebcf0662d45d43863980c9` |
| Plataforma do build | `linux/amd64` |
| Build/push e passo de registro do digest | ambos concluídos com sucesso segundo o sumário de steps |
| Digest OCI da imagem recuperado | **NÃO COMPROVADO** |
| Associação do artefato a deployment atual | **NÃO COMPROVADA** |

O workflow versionado em `.github/workflows/g2-publish-backend-ghcr.yml` constrói e publica a imagem, define `provenance: true` e escreve uma referência imutável no `GITHUB_STEP_SUMMARY` (linhas 48–74 no snapshot desta fase). O próprio workflow declara que não realiza deployment e orienta manter o pacote privado. O sumário do step confirma que o passo de registro foi executado, mas a API consultada de steps não devolve seu output nem o conteúdo do sumário. Não foram baixados logs.

## Artefato de Actions não é digest da imagem

A API do run listou o artifact `Saitar0~trilhacodeprod~14ZTL7.dockerbuild`, ID `12155638300`, 45.941 bytes, associado ao run e ao commit acima. O campo `digest` informado pelo GitHub para esse objeto é `sha256:333eca7dd8391af88863811e09b777a056a58f47b2af5ab25512859110653c4f`. É um digest do artifact do Actions, não do manifesto OCI publicado no GHCR. O artifact não foi baixado nem inspecionado.

## Consulta ao registry

Foi feita uma única consulta GET anônima ao endpoint de manifesto para a tag G2. O GHCR respondeu HTTP 401, com challenge de autenticação e sem `Docker-Content-Digest`. Nenhum token, login ou escopo adicional foi procurado ou utilizado; nenhuma camada da imagem foi baixada.

Resultado: o digest de registry não pôde ser consultado com o acesso disponível nesta fase. A tag mostrada pelo workflow é uma referência de build, não prova digest, runtime nem rota. A existência de `provenance: true` não substitui a verificação de uma attestation/proveniência consumível.

## Relação com os recursos de staging

As aplicações de staging têm branch configurada `staging`, deployments históricos no SHA `fff85218fd71b164dc7465ca72d22b4a53232f49` e não expõem referência ou digest da imagem. Portanto, não há evidência de que consumam a imagem G2 originada de `41dc470c567bae50b7ebcf0662d45d43863980c9`. Não correlacionar o build G2 com os containers presentes.

## Classificação

* **CONFIRMADO_BUILD:** build/push G2 concluído, com commit e tag declarados pelo run/workflow.
* **CONFIRMADO_PROVENIENCIA:** não atingido; a evidência declarada de origem do build existe, mas digest OCI e atestação verificável não foram recuperados.
* **NÃO COMPROVADO:** digest do manifesto OCI, digest de índice, digest por plataforma, associação a deployment, imagem em execução e atendimento por rota.

Próxima evidência apropriada: metadados sanitizados do pacote no GHCR ou saída do build summary contendo digest e proveniência, fornecidos por administrador autorizado, mais evidência separada de associação do digest ao container ativo.
