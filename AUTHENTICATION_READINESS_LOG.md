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
- Simulei a integração textual da head PR #24 com a head de autenticação em worktree descartável; não houve conflito de arquivos. A primeira execução backend combinada achou duas pendências em fixtures de produção: a fixture SMTP nova desta PR usava domínio reservado (corrigida aqui) e a fixture `test_settings_production.py` da PR #24 não define SMTP. Com ambas as fixtures coerentes no scratch, a suíte combinada passou com 170 testes e 35 skips G2; Ruff passou. A PR #24 e seu worktree ficaram intocados; após o merge futuro da PR #24, a fixture de configuração de produção precisará incluir SMTP de teste para a CI combinada passar.
- CI run #39105232718 passou no head `914bcaa08b35a0e9c987a179c17ccf19b2a8613f`, incluindo E2E; deploys foram pulados por ser PR.
- CI run #39105423611 passou no head `8d98c932395fa2d4c256f9163ea630d2d6037709`: Compose, backend, frontend e E2E passaram; deploys de staging/produção foram pulados. Esse head inclui a fixture SMTP compatível com a validação de produção.
- CI run #39105643216 passou no head `03c7e4e7c987161694e02a0f14615bac3b55cec8`: Compose, backend, frontend e E2E passaram; deploys de staging/produção foram pulados. PR #25 permanece aberta, sem merge.
- CI run #39105915130 no head `4e465d769ccfbcd287d9caa0d3b7d2fa09e27b29`: Compose, frontend e E2E passaram, mas o backend falhou em `test_registration_and_mail_requests_are_rate_limited_per_recipient`. A inspeção dos logs mostrou que o teste atravessou 07:00 UTC: as primeiras chamadas ficaram no bucket horário anterior e a última no bucket seguinte. Corrigi a fragilidade congelando o relógio usado pelo rate limiter nesse teste; nenhuma lógica de produção foi alterada.
- Validação local do ajuste de bucket: backend de integração passou com 82 testes em MongoDB 7 novo, temporário, somente em loopback e sem volume; suíte unitária passou com 73 testes e 35 skips referentes ao runner G2; Ruff passou. Container descartável foi encerrado e removido.
- CI run #39106565192 passou em backend, frontend, Compose e E2E no head `2f48e39ca9c3afeee297ebdd4ae325149870fed5`. O Playwright concluiu com quatro testes diretos e uma repetição bem-sucedida, mas registrou o fluxo de cadastro como flaky: o diretório local de e-mail ainda não existia no primeiro `readdir`. O E2E foi ajustado para criar o diretório descartável antes de aguardar a mensagem; typecheck, lint, Vitest (11 testes) e descoberta dos cinco cenários Playwright passaram localmente.
- CI run #39106923821 passou integralmente no head `b1938093df538d51133aca7ebc0c4cfd3c12178b`: backend, frontend, Compose e todos os cinco cenários E2E passaram sem retry. Deploys staging/produção foram pulados por ser PR.

## Próxima ação

PR #24 já está integrada e sua CI pós-merge passou. Concluir o commit local da integração, avançar a branch remota da PR #25 sem force push e aguardar CI da nova head. Manter staging e G2 bloqueados até backup/restore, imagem, rede, proxy, SMTP e identidade operacional serem comprovados.

## Revisão final independente e segurança (2026-10-18)

- Revalidei no GitHub a PR #24 aberta/mergeable no head `b7c7ee0f91a3b6558092515777d736d7857d6ca9` e o run `39102138622`: jobs backend/frontend/Compose/E2E passaram; deploys foram pulados. A PR foi integrada por squash no commit `b9ff5f095d523dced82878cd39011b5cd3d3b079`; CI pós-merge `39107971585` passou em Compose, backend, frontend e E2E; jobs de deploy foram pulados. Nenhum deploy foi acionado.
- Revisão de autenticação encontrou rajada de até duas vezes o limite nas transições das janelas fixas e atualização de falhas de login via documento sem `_id` determinístico, vulnerável a duplicação de upsert concorrente. Substituí os limites por buckets de tokens atômicos no Mongo, com relógio do servidor e reposição gradual, e fiz o contador de falhas convergir em `_id` hash único; continua sem guardar IP/e-mail em claro e sem alterar o índice/manifesto TTL.
- Adicionei regressões para 40 requisições concorrentes (exatamente cinco aprovadas no limite configurado), reposição gradual sem rajada de borda e 40 falhas simultâneas em um único contador. `ruff check .` passou; suíte backend completa passou com 85 testes em Mongo 7 descartável ligado somente a loopback/tmpfs. Container dedicado foi parado/removido; nenhum container existente foi alterado.
- Revalidei rate limiting compartilhado por Mongo, índices/TTL existentes, hash/expiração e consumo atômico de tokens, invalidação de sessões por `token_version`, compatibilidade de contas sem `email_verified`, respostas anti-enumeração, transporte e falhas SMTP sanitizadas, link só consumido após clique explícito e confiança de proxy configurada por IP/CIDR. Os logs de request guardam `request.url.path`, sem query-string/token. Cookies e rotas protegidas continuam usando `current_user`.
- Limite operacional: janelas residuais de cinco falhas são por par IP/e-mail; o limite por IP é compartilhado entre instâncias. TRUSTED_PROXY_IPS precisa apontar aos IPs/CIDRs reais do proxy Coolify; o valor de exemplo `127.0.0.1` não deve ser copiado sem topologia comprovada.
- Coolify permanece somente em leitura: API staging `exited:unhealthy`, sem container e sem histórico de implantação/logs disponíveis para recurso parado; Mongo de staging saudável, privado e com armazenamento persistente, porém sem backup registrado. A causa raiz exata continua indeterminada por ausência do container/logs/histórico; não inferi que recriar o app resolveria. São evidências de ausência de SMTP no app e de configuração de Dockerfile/Compose a reconferir antes de recuperação, não autorização para deploy.
- A inspeção detalhada confirmou build pack Dockerfile, caminho `backend/Dockerfile.prod`, porta 8000, health check desativado com caminho cadastrado `/` (a rota da API é `/health`), referência também preenchida como `/docker-compose.yaml` embora o repositório use `compose.yaml`, sem imagem por digest. A API aponta para `main`/`HEAD`; nenhum container identifica o commit implantado. Não há recurso frontend visível no projeto consultado. As chaves `EMAIL_TRANSPORT`, `SMTP_*` e `TRUSTED_PROXY_IPS` estão ausentes. Registrei sequência mínima, gates, critérios de interrupção e rollback em [plano de recuperação do staging](docs/operations/staging-recovery.md); ele não executa mudanças.
- SMTP: confirmei documentação oficial atual. Resend e Postmark aceitam SMTP autenticado com STARTTLS em portas 587/2525 e remetente/domínio verificado; AWS SES exige TLS, endpoint/credenciais regionais e conta fora do sandbox para enviar a endereços não verificados. Nenhuma conta, credencial ou envio externo foi criado.
- A consulta direta ao GitHub encontrou o workflow G2 de publicação concluído com sucesso (run `39096460065`, source commit `cb4524d3176548fbc82915c60d3224e0a43c0d13`, ancestral da main atual). Steps de validação de source/Dockerfile, build/push e registro do digest passaram. A API de checks não expõe o valor do resumo/digest e o endpoint de pacote privado não é acessível por esta conexão; portanto não confirmei o digest publicado nem a imagem puxada no VPS. O runner versionado continua pinado em `sha256:a6bf47a3fb1c8019678c85ce5d6d6b055a61e547c62681865f8fd1be20fad71e`, e a correspondência desse pin com o artefato da run não foi comprovada. SSH/host key, topologia, runner/manifesto instalado, usuário Mongo read-only e backup/restore também seguem sem evidência. Nenhum SSH, G2, pull de imagem ou recurso real foi alterado.
- PR #25 permanece sem merge; depois do sync, a fixture `test_settings_production.py` adicionada por #24 e o teste de cookies de staging precisam incluir SMTP fictício de teste, pois as validações de staging/production exigem esse transporte.
- Após comparar docs e runtime, fechei outra falha operacional: o código aceitava `EMAIL_TRANSPORT=local` em staging apesar da documentação exigir SMTP, permitindo aparentar sucesso de confirmação sem entrega. Staging agora valida host/remetente/TLS/credenciais junto com production; a bateria local de config (`pytest unit_tests/test_email_settings.py`) passou 5/5 e Ruff passou. A validação combinada desta branch ainda requer configurar as fixtures de staging/production trazidas por #24 com SMTP fictício de teste.
- CI pós-merge da PR #24 (`39107971585`) concluiu success em `b9ff5f095d523dced82878cd39011b5cd3d3b079`: Compose, backend, frontend e E2E passaram; deploy-staging/production foram pulados.
- Integrei localmente `origin/main` (`b9ff5f0`) à branch da PR #25 sem reescrever commits. O conflito de `backend/settings.py` foi resolvido preservando as origens/cookies seguros de #24 e validação SMTP de staging/produção de #25. Atualizei fixtures da #24 com SMTP unitário fictício, sem conexão externa.
- Após a integração local: Ruff passou; `pytest unit_tests -q` passou com 89 testes e 35 skips G2; `pytest -q` passou 85 testes contra Mongo 7 efêmero em loopback/tmpfs. O container foi parado/removido; nenhuma instância/container preexistente foi alterada. Ainda falta CI da nova head da PR #25.

## Continuação de revisão, integração e regressões (2026-10-18)

- CI da PR #25 no head `452dde0ddf5ecc7e1e4b0668050f911812f110a6`, run `39108381068`: Compose, backend, frontend e E2E concluídos com sucesso; deploys de staging e produção foram pulados. A integração da main da PR #24 está na base dessa head.
- Acrescentei regressões concorrentes para duas requisições consumirem simultaneamente o mesmo token de confirmação e o mesmo token de recuperação: em ambos os fluxos, exatamente uma resposta deve concluir com HTTP 200 e a outra deve rejeitar o token já consumido.
- Acrescentei testes de transporte SMTP sem rede para exigir a ordem EHLO/STARTTLS/autenticação/envio, verificar TLS implícito com SMTP_SSL e assegurar que falhas não registrem token, endereço nem erro SMTP sensível.
- Ajustei os fixtures HTTP para atribuir um IP loopback por caso de teste e reutilizá-lo entre os clientes daquele caso. Isso mantém o teste de seis tentativas de login no mesmo bucket e impede que limites por IP vazem de um caso para outro.
- Validação local no Mongo 7 descartável `trilhacode-auth-followup-mongo-20261018`: integração backend 87 passed; unitários 92 passed e 35 skips G2; `ruff check backend` passou. O Mongo usou tmpfs, porta publicada apenas em `127.0.0.1:27029`, sem volumes, sem dados preexistentes; os testes concluíram sem acessar Mongo compartilhado.
- SMTP transacional permanece sem conta/credenciais: documentação oficial consultada para [Resend](https://resend.com/docs/send-with-smtp), [Postmark](https://www.postmarkapp.com/developer/user-guide/send-email-with-smtp) e [AWS SES](https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html). Resend e Postmark oferecem SMTP autenticado; SES requer credenciais SMTP regionais e saída do sandbox para entrega ampla. Recomendação operacional: escolher um provedor, verificar domínio/remetente e fornecer secret via ambiente seguro; executar depois teste real de confirmação e reset em staging. Nenhuma mensagem real foi enviada.
- G2 continua bloqueado pelos gates registrados acima. A ausência de acesso ao manifesto privado GHCR não foi contornada; imagem/digest e correspondência com o pin do runner continuam sem comprovação. Staging segue sem container da API, sem histórico/logs disponíveis e sem backup agendado demonstrado.
- Alterações de teste e este registro estão locais na branch `codex/public-email-verification-auth`, ainda não incluídos no head da PR; próxima ação: revisão do diff, commit e push sem force, depois aguardar CI na head nova antes de decidir merge.
