# Registro de prontidão — autenticação e lançamento

## Missão atual

Implementar cadastro público com confirmação obrigatória, controles antiabuso e recuperação de senha em branch separada baseada em `origin/main` (`55d08dd734e862d46be91575226181b6bc9596b2`). Worktree: `C:\Users\Joao\Documents\CURSO\trilhacodeprod-auth-20261018`, branch `codex/public-email-verification-auth`. Checkout original e worktree da PR #24 preservados. PR #24 não foi integrada aqui.

## Evidências de CI

- PR #24 aberta em `b7c7ee0f91a3b6558092515777d736d7857d6ca9`; CI run `39102138622` concluída com `success` nesse head (consultado diretamente via GitHub).
- CI pós-merge da PR #23: run `39099796575`, conclusão `success` no commit `55d08dd734e862d46be91575226181b6bc9596b2` (consultado diretamente via GitHub; também informado anteriormente pelo supervisor).

## Missões realizadas nesta branch

- Inspecionados `routes_auth.py`, `services/auth.py`, `security.py`, `permissions.py`, settings, schemas, índices, seeds, frontend auth e fixtures de teste.
- Confirmado que `current_user` é a dependência central de sessões e permissões; rotas existentes autenticadas reutilizam esse mecanismo.
- Implementada política explícita: senha nova >=12 caracteres e <=72 bytes; contas legadas com flag ausente mantêm acesso; novos cadastros recebem `email_verified=false` e não recebem sessão antes da confirmação.
- Adicionados tokens aleatórios guardados somente por SHA-256, expiração (24h confirmação, 1h recuperação), consumo atômico e remoção após uso; versão JWT invalida sessões após reset/troca.
- Corrigido vazamento de hash/expiração de tokens de verificação e recuperação em respostas serializadas de usuário; regressão cobre `/auth/me` e a listagem administrativa.
- Criados limites Mongo TTL por IP/ação e e-mail hasheados sobre o índice TTL existente, mensagens genéricas e transporte local descartável/SMTP TLS; produção sem SMTP passa a falhar na validação de configuração.
- Chaves de limite agora usam HMAC com o segredo de aplicação para impedir adivinhação de e-mails/IPs a partir de dump dos contadores.
- Adicionadas telas de confirmação, recuperação e redefinição de senha, testes de integração/regressão e documentação operacional.
- A confirmação só consome o token após clique explícito, evitando consumo por scanners/preview e efeitos duplicados no modo de desenvolvimento. Troca de senha detecta atualização concorrente.

## Validação concluída

- `python -m compileall -q backend`, `ruff check .` (backend) e `git diff --check`: passaram.
- Backend após revisão final, contra Mongo 7 novo em tmpfs, sem volume, ligado só a loopback e removido depois: 155 testes passaram; 35 testes G2 foram pulados pelos requisitos do runner operacional.
- Frontend após revisão final: Vitest 11 passaram; typecheck, lint e build passaram; `npm ci` relatou zero vulnerabilidades auditadas.
- Playwright em banco limpo e descartável: 5 cenários passaram, cobrindo import/admin, navegação/admin, versões/admin, progresso/aluno, confirmação de e-mail e submissão/aluno.
- Revisão acrescentou confirmação no E2E pelo botão da interface; a lista Playwright ainda descobre os 5 cenários e os 11 testes Vitest seguem passando. A tentativa local de execução Playwright após essa alteração foi rejeitada pelo executor ao iniciar Vite; nenhuma alternativa para contornar a política foi tentada. A CI remota no head mais recente ainda precisa executar este cenário atualizado.
- `docker compose --env-file .env.example -f compose.yaml config --quiet`: passou.
- Testes de SMTP validam TLS obrigatório e credenciais emparelhadas; fluxo de integração usa transporte local `.eml` temporário, removido após a execução.

## Revisão crítica e limites

- Cadastro público retorna resposta genérica e não define cookies. A sessão só é criada após login posterior à confirmação.
- Tokens são guardados por hash, têm expiração, rotação e consumo atômico; senha redefinida ou trocada invalida JWTs existentes.
- `current_user` bloqueia qualquer conta marcada explicitamente como não verificada; falta do campo mantém compatibilidade com usuários legados.
- Limitação reutiliza o índice TTL `login_attempts.last`, sem alterar o manifesto do protocolo G2.
- SMTP de produção ainda precisa ser fornecido e validado pelo operador em Coolify/ambiente equivalente. Não há credencial ou provedor configurado nesta sessão.
- Nenhuma mutação de banco, deploy, restart, G2, VPS ou produção foi executada. Consultas Coolify foram somente leitura; sucesso local não homologa esses ambientes.

## Auditoria independente de operação

- Consulta somente leitura no Coolify em 2026-10-18: o app de API do Trilha Code em staging está `exited:unhealthy`, sem container presente; o último registro online é de 2026-10-03 e não há histórico de deploy retornado. Isso impede validação de staging nesta sessão.
- O MongoDB de staging aparece `running:healthy`, privado e sem porta pública. A listagem de backups retornou zero agendamentos. Não foi iniciada restauração nem alteração no banco.
- Inspecionei somente nomes de chaves do app, sem ler valores: `EMAIL_TRANSPORT`, `SMTP_HOST`, `SMTP_FROM_EMAIL` e demais chaves SMTP não estão configurados no recurso. Assim, não há evidência de entrega real de e-mail em staging.
- CI run #39104884203 passou no head `6bcfcb7f5c9a2b7d74c3d0645ba900a5329450cf`; não contém a atualização Playwright seguinte. Run #39105050233 passou no head `f742a5c6cb0513339d9754da257ff7341b710229`, incluindo o fluxo de confirmação pelo botão no navegador; deploys foram corretamente pulados por ser PR. O run #39105232718 foi criado para o head atual `914bcaa08b35a0e9c987a179c17ccf19b2a8613f` e estava `queued` no último snapshot.
- O runbook G2 ainda exige imagem privada GHCR identificada por digest, identidade SSH validada, runner/manifest instalados, topologia interna dedicada, usuário Mongo somente leitura e evidência de backup/restauração. Nenhum gate foi acionado ou alterado.
- O inventário de saúde mostrou aplicações fora do projeto Trilha Code em estado unhealthy; não investiguei nem alterei recursos de outros projetos.

## Próxima ação

Atualizar a CI da PR #25 quando ela concluir e continuar a auditoria independente de deploy/recuperação sem tocar nos gates operacionais bloqueados.
