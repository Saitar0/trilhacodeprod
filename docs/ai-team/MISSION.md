# Missão atual — documentação de equipe

**Data:** 17/10/2026 (America/Sao_Paulo)
**Base:** `main` em `27a98964d55b96003fac70154178c5892da8d453`
**Branch:** `codex/ai-team-mission-2026-10-17`

## Reconhecimento

- Produto full stack com frontend React 19/TypeScript/Vite, API FastAPI/Python e MongoDB; backend organizado em rotas, serviços e schemas.
- A CI `.github/workflows/ci-deploy.yml` cobre Ruff, pytest com Mongo de serviço, compilação Python, validação negativa de configuração de produção, imagem backend, auditoria de dependências, typecheck/lint/test/build frontend. Deploy é manual e condicionado a workflow dispatch.
- O histórico remoto recente inclui a PR #7, integrada à `main` antes desta missão. As PRs #2–#7 estão integradas; a PR #1 continua aberta contra a branch legada `master`. O repositório informa `main` como branch padrão, portanto esta missão usa `main`.
- Há três arquivos de teste da interface e não foi encontrada automação browser E2E. A CI não valida a resolução dos arquivos Compose. São lacunas de cobertura, não defeitos funcionais confirmados.
- A análise não confirmou bug de runtime que justifique alteração de produto nesta missão.

## Escopo selecionado

1. Criar `docs/ai-team/TEAM.md`, `ROADMAP.md`, `MISSION.md`, `DECISIONS.md` e `REPORT.md` com fatos, prioridades e estado inicial rastreáveis.
2. Criar `AGENTS.md` com instruções permanentes compatíveis com os limites do projeto e as salvaguardas já solicitadas.

## Critérios de conclusão

- Os seis arquivos existem e apontam para caminhos coerentes no repositório.
- O roadmap diferencia evidência de oportunidade/hipótese e mantém no máximo três itens priorizados.
- O relatório registra branch/base, diff, revisão, validação, riscos e limitações reais.
- Nenhuma alteração ou arquivo preexistente do usuário é incluído no commit.
- A branch é enviada e uma Pull Request contra `main` é criada para avaliação, sem merge ou deploy.
