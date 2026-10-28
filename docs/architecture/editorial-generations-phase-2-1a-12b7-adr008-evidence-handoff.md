# Fase 2.1A.12B.7 — Handoff de evidências para ADR-008

**Estado:** `BLOCKED_BY_EVIDENCE`. Nenhuma consulta a Coolify, GHCR, staging ou produção foi feita nesta fase. O baseline permanece parcialmente comprovado.

## 1. Pedido existente

Não duplicar a auditoria nem substituir o pedido de 12B.4B: [`editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md`](./editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md).

## 2. Síntese mínima a retornar pelo administrador autorizado

Para cada ambiente/serviço, retornados como metadados sanitizados e observados no mesmo intervalo UTC:

1. **Produção:** identidade inequívoca do serviço backend e, se pertinente, frontend/worker; não deduzir pelo nome do projeto ou branch.
2. **Runtime:** identificador sanitizado do deployment e da instância/container ativo, com evidência de associação ao serviço.
3. **Artefato:** referência OCI atribuída ao runtime e digest imutável; distinguir digest do índice multi-arquitetura e digest do manifesto/plataforma quando aplicável.
4. **Proveniência:** build/run e job que produziram aquele digest; repositório e SHA Git completo. Indicar se a revisão é label declarada ou proveniência/attestation verificável.
5. **Rota:** regra carregada que aponta ao serviço e evidência agregada/sanitizada de tráfego no período. Não enviar logs de requisições.
6. **Disponibilidade:** status da plataforma/processo, healthcheck, readiness separada (ou declaração de que não existe) e horário UTC.
7. **Linha alvo:** confirmação do owner sobre ambiente e branch/linha de release pretendidos para uma futura integração.

Solicitar apenas os resultados mínimos e sanitizados. Não solicitar/receber credenciais, `.env`, tokens, dados pessoais, dumps, logs brutos, acesso SSH ou exportação integral da plataforma.

## 3. Critério de fechamento

Uma branch/commit remotos ou um build histórico não fecham o gate. ADR-008 só pode ser reconsiderado quando há associação verificável entre serviço/ambiente ativo, digest da imagem, build/proveniência e SHA completo, além da linha alvo aprovada. Se um elo faltar, registrar `NÃO COMPROVADO`; não inferir nem escolher substituto.

**Gate atual:** G10 `BLOCKED`.
**Próximo passo autorizado nesta fase:** nenhum acesso; aguardar resposta do administrador autorizado.
**Após a resposta:** analisar documentalmente e pedir decisão humana explícita. Isso não autoriza implementação ou deployment.
