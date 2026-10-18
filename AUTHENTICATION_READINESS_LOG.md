# Registro de prontidão — autenticação e lançamento

## Missão atual

Implementar cadastro público com confirmação obrigatória, controles antiabuso e recuperação de senha em branch separada baseada em `origin/main` (`55d08dd734e862d46be91575226181b6bc9596b2`). Worktree: `C:\Users\Joao\Documents\CURSO\trilhacodeprod-auth-20261018`, branch `codex/public-email-verification-auth`. Checkout original e worktree da PR #24 preservados. PR #24 não foi integrada aqui.

## Evidências recebidas do supervisor

- PR #24 aberta em `b7c7ee0f91a3b6558092515777d736d7857d6ca9`.
- CI pós-merge da PR #23: run `39099796575`, conclusão `success` no commit `55d08dd734e862d46be91575226181b6bc9596b2` (informação externa do supervisor, não consultada diretamente nesta sessão).
- CI da PR #24: run `39102138622`, sucesso informado pelo supervisor; não revalidado diretamente nesta branch.

## Missões realizadas nesta branch

- Inspecionados `routes_auth.py`, `services/auth.py`, `security.py`, `permissions.py`, settings, schemas, índices, seeds, frontend auth e fixtures de teste.
- Confirmado que `current_user` é a dependência central de sessões e permissões; rotas existentes autenticadas reutilizam esse mecanismo.
- Implementada política explícita: senha nova >=12 caracteres e <=72 bytes; contas legadas com flag ausente mantêm acesso; novos cadastros recebem `email_verified=false` e não recebem sessão antes da confirmação.
- Adicionados tokens aleatórios guardados somente por SHA-256, expiração (24h confirmação, 1h recuperação), consumo atômico e remoção após uso; versão JWT invalida sessões após reset/troca.
- Criados limites Mongo TTL por IP/ação e e-mail hasheados sobre o índice TTL existente, mensagens genéricas e transporte local descartável/SMTP TLS; produção sem SMTP passa a falhar na validação de configuração.
- Adicionadas telas de confirmação, recuperação e redefinição de senha, testes de integração/regressão e documentação operacional.
- A confirmação só consome o token após clique explícito, evitando consumo por scanners/preview e efeitos duplicados no modo de desenvolvimento. Troca de senha detecta atualização concorrente.

## Validação concluída

- `python -m compileall -q backend`, `ruff check .` (backend) e `git diff --check`: passaram.
- Backend após revisão final, contra Mongo 7 novo em tmpfs, sem volume, ligado só a loopback e removido depois: 153 testes passaram; 35 testes G2 foram pulados pelos requisitos do runner operacional.
- Frontend após revisão final: Vitest 11 passaram; typecheck, lint e build passaram; `npm ci` relatou zero vulnerabilidades auditadas.
- Playwright em banco limpo e descartável: 5 cenários passaram, cobrindo import/admin, navegação/admin, versões/admin, progresso/aluno, confirmação de e-mail e submissão/aluno.
- `docker compose --env-file .env.example -f compose.yaml config --quiet`: passou.
- Testes de SMTP validam TLS obrigatório e credenciais emparelhadas; fluxo de integração usa transporte local `.eml` temporário, removido após a execução.

## Revisão crítica e limites

- Cadastro público retorna resposta genérica e não define cookies. A sessão só é criada após login posterior à confirmação.
- Tokens são guardados por hash, têm expiração, rotação e consumo atômico; senha redefinida ou trocada invalida JWTs existentes.
- `current_user` bloqueia qualquer conta marcada explicitamente como não verificada; falta do campo mantém compatibilidade com usuários legados.
- Limitação reutiliza o índice TTL `login_attempts.last`, sem alterar o manifesto do protocolo G2.
- SMTP de produção ainda precisa ser fornecido e validado pelo operador em Coolify/ambiente equivalente. Não há credencial ou provedor configurado nesta sessão.
- Nenhuma operação de banco, staging, G2, VPS, Coolify ou produção foi executada; sucesso local não homologa esses ambientes.

## Próxima ação

Criar commit e PR separada para este branch (sem merge), registrar as evidências CI da PR e continuar a auditoria independente de deploy/recuperação sem tocar nos gates operacionais bloqueados.
