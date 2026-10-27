# Decisões técnicas

## 18/10/2026 — Endurecimento G2 isolado em PR

- Decisão: implementar protocolo/validação/runner e documentação em `codex/g2-fix`, sem executar G2 nem publicar imagem.
- Razão: o backend novo não existe na imagem pinada atualmente pelo runner; ativação antes de reconstrução verificada falharia. Infraestrutura, imagem e runner no host precisam de etapa e autorização próprias.
- Segurança: URI exige `directConnection=true` além de host/porta/db aprovados; nenhuma resposta contém URI, documentos ou IDs de negócio; runner descarta logs brutos e serializa invocações com lock root. O manifesto esperado é independente do resultado. Status ausente é informativo; conflito e duplicatas reprovam.
- Execução: workflow G2 continua manual, restrito à ref `main`, com `StrictHostKeyChecking=yes` e comando SSH fixo. CI de PR não aciona G2.

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

## 17/10/2026 — QA de resposta acessível em mobile

- Decisão: deixar o rodapé de progresso não fixo abaixo do breakpoint `sm`, associar labels visíveis para leitores de tela aos campos de resposta/código, e nomear controles icon-only de reordenação/ações admin.
- Motivo: Chromium local com API simulada reproduziu sobreposição do rodapé ao textarea em 360 e 390 px, textarea sem label e três botões admin sem nome acessível.
- Evidência: após mudança, não há interseção do footer/textarea nem overflow a 360/390; labels e nomes dos três botões são detectados. E2E de regressão foi adicionado ao workflow Mongo descartável.

## 17/10/2026 — Não modificar known_hosts sem confirmação criptográfica

- Decisão: preservar `StrictHostKeyChecking=yes` e não alterar o workflow ou secrets enquanto hostname e fingerprint não forem confirmados pelo administrador da VPS.
- Motivo: o log de G2 diz que nenhuma chave ED25519 é conhecida para o host mascarado; não afirma que houve troca. `G2_STAGING_SSH_HOST` e `G2_STAGING_SSH_KNOWN_HOSTS` são secrets inacessíveis no log, e não existe fonte confiável do host no ambiente de trabalho.
- Evidência/ação: comparar `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` no próprio servidor com a chave do `known_hosts` para o hostname efetivo; só então corrigir secret com aprovação do dono da infraestrutura.

## 17/10/2026 — Cobrir acessibilidade do campo de código no E2E

- Decisão: incluir no E2E de submissão um bloco `practical_challenge` temporário no Mongo efêmero e verificar seu nome acessível; selecionar o textarea pelo ID do bloco criado ao medir sobreposição.
- Motivo: a revisão independente apontou que o teste anterior podia medir outro exercício e não cobria o label do campo de código.
- Evidência: payload conferido com `BlockIn`/serviço de blocos, cleanup dos IDs temporários no teardown e revisão independente sem achados acionáveis. CI #39030010321 passou backend, frontend, Compose e Playwright E2E.


## 17/10/2026 — E2E do histórico pela interface

- Decisão: cobrir a publicação com nota pela tela administrativa, edição posterior da descrição e comparação do snapshot com o estado atual. Usar o track seed apenas no job E2E descartável; não restaurar nem acionar operações operacionais.
- Motivo: os testes existentes cobrem edição e persistência de settings, enquanto o fluxo de versão publicado e compare ainda não tem cobertura UI.
- Evidência: PR #18; CI #39035017901 passou backend, frontend, Compose e E2E; deploys de staging/produção foram pulados. Revisão independente aprovou o isolamento e os asserts do fluxo.

## 17/10/2026 — Não alterar configuração G2 sem chave verificada

- Decisão: manter `StrictHostKeyChecking=yes` e não alterar host/secret nem despachar o workflow.
- Evidência: YAML usa SSH na porta padrão 22. A sessão autenticada Hostinger confirma a VPS e status em atividade, mas Web Console está desabilitado; Coolify MCP confirma apenas a disponibilidade do painel e estado dos recursos. O hostname alvo é secret, e não foi possível ler a chave ED25519 do servidor para fingerprint.
- Próximo passo: administrador obter a chave pública pela fonte confiável do servidor, calcular SHA256 e comparar com a entrada e identidade host de `G2_STAGING_SSH_KNOWN_HOSTS` em canal privado. A correção de secret e a execução de G2 permanecem gates separados.


## 17/10/2026 — Homologação de importação acessível e reenvio do aluno

- Decisão: ampliar E2E com axe-core WCAG 2.1 A/AA e navegação por teclado no formulário de importação admin; verificar reenvio de uma resposta já enviada. Os testes só mutam o Mongo efêmero do CI.
- Motivo: cobertura comprovada ainda não verificava nome acessível do JSON, ativação por teclado, nem a transição de atualização de resposta já enviada.
- Evidência: PR #19 e PR #20 abertos; revisões técnicas independentes aprovadas. CI #39037180408 e #39037237806 passaram frontend, backend, Compose e E2E; deploys foram pulados.

## 17/10/2026 — Hostinger Web Console novamente disponível; manter G2 bloqueado

- Decisão: usar somente `hostname -f` e `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256` no console administrativo autenticado; não expor a fingerprint em arquivos/PR/logs; não alterar secrets nem despachar G2.
- Evidência: o console identificou o hostname canônico esperado para a VPS; a fingerprint foi calculada localmente no terminal. O valor do hostname/known_hosts no GitHub é secret e não foi lido, impedindo comparar a identidade e escolher a correção.
- Próximo passo: responsável compara host, porta 22 e fingerprint em canal privado; aprova especificamente qualquer alteração de secret. A execução G2 é uma autorização separada.

## 17/10/2026 — Registrar baseline de bundle antes de otimizar

- Decisão: não otimizar os ícones sem uma medição de requests por rota e confirmação de compatibilidade do catálogo.
- Evidência: CI #39036366799 reportou 1.611 chunks JavaScript, soma gzip de 874,12 kB para todos os arquivos, `index` 493,75/159,36 kB e `IconCatalog` 213,07/50,83 kB (bruto/gzip). A soma de todos os chunks não representa tráfego de uma visita, pois há lazy loading.

## 26/10/2026 — Notas versionadas e progresso reconciliável

- Decisão: atualizar notas com `expected_version` e comparação atômica, preservando o texto local em conflito; representar exclusão como tombstone versionado.
- Decisão: usar revisão CAS por registro de progresso e um evento pendente no mesmo documento; projetar evento/estado de trilha com IDs estáveis e reconciliar pendências em retry/leitura do histórico, sem presumir transações Mongo multidocumento.
- Decisão: separar `operation_id` (replay técnico) de `attempt_id` (submissão explícita de quiz). Conclusão de leitura é auto-relatada e não prova domínio.
- Evidência: Fase 1.2 em worktree isolada sobre `d2824aa6b910f747a29cbbbf8a2f123a5ad51d5c`; pytest 112/112, Vitest 21/21, Ruff, typecheck, ESLint e build passaram. Nenhuma migração/índice foi necessária.