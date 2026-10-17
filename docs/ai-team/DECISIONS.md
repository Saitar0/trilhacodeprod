# Decisões técnicas

## 17/10/2026 — Basear novas PRs na branch padrão atual

- **Decisão:** usar `main` como base de desenvolvimento e Pull Request.
- **Evidência:** a API do GitHub informa `main` como `default_branch`, apontando para `27a98964`; `origin/HEAD` local ainda apontava para `master`, que está atrás.
- **Motivo:** evitar iniciar trabalho na referência legada e desatualizada.
- **Consequência:** a missão atual foi atualizada a partir da ponta remota de `main`; a PR #1 antiga permanece fora do escopo.

## 17/10/2026 — Missão documental, sem mudança de runtime

- **Decisão:** criar os registros permanentes pedidos e documentar lacunas técnicas no roadmap, sem alterar o comportamento da aplicação.
- **Evidência:** revisão de documentação, código-fonte, suíte declarada e workflow não reproduziu um defeito funcional atual.
- **Motivo:** priorizar evidência e evitar mudança de produto especulativa.
- **Consequência:** validações de Compose, E2E e tamanho de bundle ficam para uma missão separada.
