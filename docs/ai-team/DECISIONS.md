# Decisões técnicas

## 17/10/2026 — Basear PRs na branch padrão atual

- **Decisão:** usar `main` como base de desenvolvimento.
- **Evidência:** GitHub informa `main` como branch padrão, SHA inicial `27a98964`; a referência local `origin/HEAD` estava desatualizada.
- **Consequência:** PRs desta missão apontam para `main`; PR #1 contra a branch legada permanece fora do escopo.

## 17/10/2026 — Testes de integração somente com dados descartáveis

- **Decisão:** PR #9 recusa URLs Mongo remotas, SRV, multihost e topologias ambíguas nos testes e usa DB gerado e conexão direta loopback.
- **Motivo:** evitar que cleanup/fixtures de integração atinjam staging ou produção por URI mal configurada.
- **Verificação:** CI #18 aprovada para backend, frontend e Compose; serviços reais não foram acessados.

## 17/10/2026 — E2E em Mongo efêmero separado

- **Decisão:** executar Playwright em job dedicado com serviço Mongo efêmero, banco `trilhacode_e2e`, seed do job e credenciais fictícias.
- **Motivo:** testar persistência aluno sem montar volumes QA nem apontar a staging.
- **Verificação:** fluxo aluno passou na CI #23; a ponta atual inclui admin read-only e medições responsivas, aguardando CI #29.

## 17/10/2026 — Resolver ícones sob demanda

- **Decisão:** substituir o import global de `lucide-react` por resolução dinâmica por nome em PR #10.
- **Evidência:** chunk IconCatalog: 799.578 B bruto/147,81 KiB gzip antes; 213.071 B/50,78 KiB gzip depois.
- **Tradeoff:** build cria aproximadamente 1.593 chunks de ícone menores; manter monitoramento de quantidade de requisições e uso em páginas densas.

## 17/10/2026 — Bloquear forma inválida de import antes do planejamento

- **Decisão:** validar containers, tipos de valores que serão usados em execução e limite de profundidade antes de acessar Mongo ou planejar writes; retornar 422 com paths.
- **Motivo:** o código anterior podia acessar propriedades/usar `int()` e `hierarchy.index()` com tipos inválidos; uma falha após criar a trilha poderia deixar import parcial.
- **Verificação:** testes unitários puros locais; ponta corrigida PR #13 aguarda CI #31 e revisão independente final.

## 17/10/2026 — Não executar gates de staging sem aprovação específica

- **Decisão:** não alterar Coolify/VPS/SSH/firewall/secrets, não acessar Mongo real, não executar G3–G6, webhook, backup/restore ou deploy.
- **Motivo:** os runbooks identificam operações de dados/infraestrutura compartilhada como gates separados; autonomia de desenvolvimento não as autoriza.
- **Consequência:** preparação fica documentada; status de release depende de aprovação e evidências atuais do operador.