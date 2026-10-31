# Fase 2.1A.12B.4A — revisão de evidências do ADR-008

**Status do ADR-008:** Proposed.
**Status para aprovação humana:** PENDING_APPROVAL.
Esta revisão acrescenta evidência; não aprova baseline nem políticas.

## Evidências observadas

1. `git ls-remote` em 2026-10-28 15:11:56 UTC confirmou `main=22dca64556338a8fa9aaa89ce627a4f4af72317d` e `staging=fff85218fd71b164dc7465ca72d22b4a53232f49`.
2. Coolify reportou API e frontend de staging como `running:healthy`, com container presente; seus deployments mais recentes registrados finalizaram no SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`.
3. Para ambos os recursos, o health check aparece desabilitado; não foram retornados nome/tag de registry ou digest ativo. O inventário de rollback lista a tag SHA `fff852...` como imagem local `is_current=false`.
4. A aplicação `trilhacode` no projeto `general` tem origem configurada em main, mas o último deployment associado a `22dca645...` falhou e o recurso está `starting:unknown`, sem ambiente/FQDN identificado.
5. CI de push para main/staging construiu imagens, mas os jobs de deploy foram ignorados. O workflow G2 publicou uma imagem de backend associada a `41dc470c567bae50b7ebcf0662d45d43863980c9`; o valor do digest não foi obtido por metadados. Seu workflow declara que publicação não equivale a deployment.
6. O snapshot e5bf continua local à linha de auditoria e não aparece como SHA em nenhum deployment Coolify consultado.

Detalhes e limites: [inventário de runtime](editorial-generations-phase-2-1a-12b4a-runtime-inventory.md), [proveniência](editorial-generations-phase-2-1a-12b4a-image-provenance.md), [matriz de baseline](editorial-generations-phase-2-1a-12b4a-baseline-evidence.md) e [compatibilidade](editorial-generations-phase-2-1a-12b4a-compatibility.md).

## Ficha atualizada

**Problema:** branch configurada e deployment concluído não identificam necessariamente a imagem ativa que recebe tráfego. A evidência atual não fecha a cadeia de produção nem a de staging.

**Recommended Decision — recomendação técnica:** manter a política D do ADR original: escolher baseline por ambiente e objetivo de release, usando SHA de origem e digest imutável verificados. Para staging, tratar `fff85218fd71b164dc7465ca72d22b4a53232f49` apenas como SHA do deployment Coolify mais recente concluído e como candidato a validação, condicionado à confirmação de owner e à evidência do digest/rota. Para produção, não há candidato confirmado. Manter e5bf3147... apenas como snapshot de auditoria.

**Approved Decision:** nenhuma. O baseline permanece bloqueado.

| Alternativa | Vantagem | Risco/condição |
|---|---|---|
| main `22dca...` | Ref remota principal e linha de produção descrita em documentação | O recurso de mesmo repositório/branch encontrado não foi identificado como produção; seu último deployment falhou. |
| staging `fff852...` | Há deployments concluídos de API e frontend com esse SHA, e o estado atual é reportado como healthy | Não há digest ativo/roteamento; health check Coolify está desabilitado; tag local consta `is_current=false`. |
| snapshot e5bf... | Contém a auditoria técnica e PoC | Não consta nos deploys; difere amplamente das branches e carece de prova de implantação. |
| linha dedicada reconciliada | Permite escolher origem com revisão explícita e compatibilidade cruzada | Depende de evidência por ambiente, decisão de release owner e comparação de schema/API/frontend. |

## Evidência mínima para aprovação

- Owner identifica sem ambiguidade recurso, ambiente, frontend/API/worker e rota de tráfego.
- Metadado de runtime associa cada serviço ativo a referência de imagem imutável e digest completo (índice e/ou plataforma claramente tipados).
- Provenance verificável liga digest, workflow/build, repositório, SHA completo e Dockerfile.
- Registro de deployment/rota demonstra que essa imagem atende o ambiente-alvo; health/readiness deve se referir ao mesmo serviço e revisão.
- Owner seleciona o baseline de implementação/validação e a linha de release. A matriz main/staging/e5 e plano de reconciliação são atualizados para esses SHAs.

Não pedir logs brutos, secrets, dados de aluno, shell ou inspeção Docker remota. Preferir exportação sanitizada de metadados ou autorização explícita para uma tela de leitura específica do Coolify que exponha imagem/digest e vínculo com rota.

## Gate

**ADR-008 continua PENDING_APPROVAL.** Implementação de runtime permanece bloqueada porque nenhum ambiente atingiu `CONFIRMADO — RUNTIME` e não há cadeia verificável até digest ativo. A evidência parcial de staging pode orientar a solicitação seguinte, não liberar código.
