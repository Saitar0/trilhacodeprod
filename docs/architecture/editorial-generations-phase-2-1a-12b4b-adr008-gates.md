# Fase 2.1A.12B.4B — gates e revisão do ADR-008

**Status do ADR-008:** Proposed.
**Status da decisão humana:** PENDING_APPROVAL.
Esta análise não aprova baseline nem libera implementação.

## Recomendação condicionada

* **Baseline comprovadamente implantado:** não identificado para produção nem integralmente para staging. O Coolify reporta duas apps de staging presentes e `running:healthy`, com deployments históricos no SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`, mas não expõe digest/container ativo nem associação com rota carregada.
* **Linha técnica para investigação/desenvolvimento:** manter `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636` somente como snapshot de auditoria, não como baseline implantado ou destino escolhido. Nenhuma linha é recomendada para código até o responsável confirmar o alvo de release e reconciliar sua compatibilidade com a imagem realmente implantada.
* **Linha de validação:** definir após a escolha humana do baseline; deve validar os contratos de cada ambiente e não usar branches como substituto de artefato.
* **Estratégia de release:** associar release futuro a artefato imutável/digest, build verificável, SHA completo e deployment identificável. A decisão de cutover continua separada.

## Evidências que faltam

1. Identidade e digest do container/imagem atualmente associados a cada app de staging.
2. Digest OCI da imagem G2 (o GHCR anônimo retornou 401; o digest recuperado da API do artifact é do ZIP `.dockerbuild`, não da imagem).
3. Proveniência verificável ligando o digest OCI a build e commit.
4. Associação entre container ativo e deployment atual.
5. Regra de roteamento ativa ligada ao serviço e evidência sanitizada de tráfego atendido.
6. Identificação explícita do serviço de produção. O candidato no projeto `general` está `starting:unknown`, tem último deployment falho e não foi classificado como produção.
7. Commit da Fase 12B.4A, `22f1b0df56d4bf5c0a35611db98523b54e5eca76`, ligado a um deploy/build real (não foi encontrado vínculo nesta investigação).

## Gates

| Gate | Evidência necessária | Estado |
|---|---|---|
| G1 — serviço e ambiente | Owner confirma quais recursos são produção e staging | PENDENTE |
| G2 — runtime | Metadados sanitizados ligam serviço ativo, container e deployment | PENDENTE |
| G3 — identidade do artefato | Referência e digest OCI ativo, sem depender de tag móvel | PENDENTE |
| G4 — proveniência | Digest ligado a build e SHA completo por metadado/attestation verificável | PENDENTE |
| G5 — roteamento | Regra ativa do proxy/load balancer aponta para serviço identificado | PENDENTE |
| G6 — tráfego/readiness | Evidência agregada de atendimento e fonte de readiness, se disponível | PENDENTE |
| G7 — compatibilidade | Diff de contratos/schema entre imagem implantada, main, staging e snapshot auditado | PENDENTE |
| G8 — decisão humana | Aprovação explícita do baseline e linha de release | PENDING_APPROVAL |

## Condição para ADR-008

O build G2 `39179762892` em `41dc470c567bae50b7ebcf0662d45d43863980c9` é `CONFIRMADO_BUILD`, não runtime. As branches atuais consultadas permanecem `main=22dca64556338a8fa9aaa89ce627a4f4af72317d` e `staging=fff85218fd71b164dc7465ca72d22b4a53232f49`; isso não identifica o código implantado. Portanto, ADR-008 continua bloqueando a primeira implementação funcional e não pode ser aprovado com base apenas nesta evidência.

## Decisão humana solicitada

Após receber a evidência sanitizada do [administrador](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md), decidir: qual ambiente será primeiro alvo; qual baseline de release será fonte; como reconciliar diferenças entre imagem implantada e branches; e quem autoriza o cutover. Nenhuma dessas escolhas está presumida.
