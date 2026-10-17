# Decisões técnicas

## 17/10/2026 — Usar branch padrão atual

- Decisão: criar PRs da missão contra main.
- Evidência: GitHub indicou main e SHA 27a98964; referência local origin/HEAD estava antiga.

## 17/10/2026 — Isolar testes que limpam Mongo

- Decisão: rejeitar URI Mongo remota/SRV/multihost ou ambígua nas fixtures; gerar DB descartável e exigir conexão local/direct-only.
- Motivo: impedir cleanup de atingir staging/produção por URI mal definida.
- Evidência: PR #9 e CI #18 passaram backend, frontend e validação Compose sem subir serviços localmente.

## 17/10/2026 — E2E em serviço temporário

- Decisão: usar Mongo service por job, DB trilhacode_e2e, seed e credenciais fictícias.
- Motivo: confirmar login, progresso persistido e fluxo administrativo sem tocar em dados persistentes.
- Evidência: CI #45 passou fluxo estudante, navegação admin e overflow 360/390 px; CI #50 passou edição de descrição e reload; CI #51 passou dependência E2E dos deploy jobs, mantendo-os pulados.

## 17/10/2026 — E2E de submissão em entidade temporária

- Decisão: criar bloco exercise_open publicado por API no seed descartável, registrar um estudante exclusivo para o caso, enviar pela UI, recarregar e verificar status/resposta; apagar o bloco no teardown.
- Motivo: manter o teste representativo da interface e evitar interferência do progresso do estudante usado em outro E2E.
- Limite: Mongo é efêmero por job. A execução atual PR #12/CI #60 aguarda validação; não usar base de staging ou produção.

## 17/10/2026 — Import deve validar BSON antes de qualquer escrita

- Decisão: validar forma JSON, valores BSON e tamanho conservador dos documentos gerados de track, node, tag, bloco (incluindo node_ref/block_ref) e relation antes de planejar a importação.
- Motivo: evitar falhas tardias por input inválido ou limite de documento após criar trilha/nó.
- Evidência: PR #13; 33 testes locais, Ruff, CI #48 e revisão independente aprovados. A validação não transforma erros gerais de banco/runtime em transação.

## 17/10/2026 — Confirmar mudança de papel em sessão existente

- Decisão: manter teste de integração que promove e rebaixa usuário com cookie já ativo, confirmando permissões atuais no request seguinte.
- Motivo: detectar role stale em token/sessão após revogação.
- Evidência: PR #14 e CI #46 passaram no DB descartável.

## 17/10/2026 — Não acionar gates operacionais por autonomia de código

- Decisão: não alterar Mongo real, secrets, SSH/firewall, Coolify/VPS, Dev Forge; não rodar G3–G6 ou deploy.
- Motivo: esses gates têm impacto em dados/infra compartilhados e aprovadores definidos no plano.
- Consequência: permanece pendente a investigação segura da configuração de host key e aprovação operacional individual.


## 17/10/2026 — Cobrir importação e edição de nó no navegador

- Decisão: no E2E administrativo, validar preview sem criar a trilha, aplicar a importação hierárquica, conferir os três nós, editar o tópico, recarregar e validar persistência; remover a trilha temporária.
- Motivo: cobrir homologação funcional de import e editor por UI em base isolada.
- Evidência: PR #12, CI #70 passou; revisor independente não encontrou achados acionáveis. A base Mongo é descartável e a mutação roda somente quando CI está habilitado.
