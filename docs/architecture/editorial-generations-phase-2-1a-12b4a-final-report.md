# Fase 2.1A.12B.4A — relatório final

## A. Resumo executivo

As consultas autorizadas confirmaram metadados parciais de staging: API e frontend são reportados por Coolify como `running:healthy`, e seus deployments concluídos mais recentes estão associados ao SHA `fff85218fd71b164dc7465ca72d22b4a53232f49`. Porém, nenhum digest imutável ativo foi retornado, não há associação explícita entre deployment, instância e rota, e o health check aparece desabilitado. Não há baseline de produção comprovado.

O workflow G2 confirmou um build/push de backend associado a `41dc470c567bae50b7ebcf0662d45d43863980c9`, mas não se recuperou o valor do digest nem evidência de que essa imagem esteja implantada. Os CI atuais de main/staging tiveram os jobs de deploy ignorados.

## B. Git e isolamento

- Worktree dedicada: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b4a-runtime-baseline-evidence\trilhacodeprod`.
- Branch local: `codex/fase2-1a-12b4a-runtime-baseline-evidence`.
- Base: `7c72a837ea0e89a31e67b457130b019658561bb1`.
- A worktree foi criada com `git worktree add --no-checkout`; o sparse-checkout foi configurado antes da materialização final. A primeira configuração cone materializou diretórios técnicos mais amplos do que o necessário; ela foi imediatamente reduzida a padrões exatos. `docs/courses/trilhacode/` e `docs/migracao/` não estão materializados; nenhum arquivo protegido foi lido ou alterado.
- A origem B4 estava limpa em `7c72a837...` antes da criação da nova worktree.

## C–J. Fontes, ambientes, serviços, imagens e saúde

As interfaces e o inventário por serviço estão em [runtime-inventory](editorial-generations-phase-2-1a-12b4a-runtime-inventory.md). Foram consultados metadados de aplicações, deployments e imagens de rollback do Coolify, sem logs, variáveis ou secrets. A listagem scoped retornou duas aplicações de staging e zero serviços adicionais; uma aplicação `trilhacode` no projeto `general` é apenas candidata não classificada. Zero deployments estavam em andamento/na fila na observação.

Coolify reportou `running:healthy` para staging, `container_present=true` e `health_check_enabled=false`. Nenhum endpoint foi chamado. Tags, imagens de rollback, SHA de deployment e digests estão distinguidos em [image-provenance](editorial-generations-phase-2-1a-12b4a-image-provenance.md). O digest ativo não foi comprovado.

## K–M. GitHub Actions, Git e divergências

Runs de CI de main `40488544210` e staging `40394870286`: builds backend/frontend e E2E concluídos, deploys `skipped`. Run G2 `39179762892`: build/push de imagem backend bem-sucedido no SHA `41dc470c567bae50b7ebcf0662d45d43863980c9`, sem prova de deployment. Os deployments Coolify concluídos de staging registram fff; o candidato main registra deployment falho em 22dca. Nenhum registro liga digest ativo a esses SHAs.

As refs Git remotas, ancestralidade e a matriz por área estão em [compatibility](editorial-generations-phase-2-1a-12b4a-compatibility.md). `main...staging = 1/3`; e5 tem 21 commits além de main e não contém três commits exclusivos de staging. A diferença de e5 contra main abrange 113 arquivos. Não foi feito merge, rebase ou cherry-pick.

## N–P. Confiança e baselines

- **Produção:** baseline implantado **NÃO COMPROVADO**.
- **Staging:** parcialmente evidenciado por status da plataforma e deployments concluídos; baseline de runtime/digest **NÃO COMPROVADO**.
- **Build:** o run G2 é evidência de build/push ligado ao commit `41dc470c...`; o digest não foi disponibilizado por metadados consultados.
- **Snapshot auditado:** e5bf3147... permanece linha de análise; não foi encontrado em registros Coolify consultados.

O veredito global é **BASELINE PARCIALMENTE COMPROVADO**, no sentido restrito de que há deployments de staging e estado atual reportado; isso não satisfaz comprovação de imagem em execução ou tráfego para qualquer ambiente.

## Q–R. ADR-008 e reconciliação futura

O ADR-008 permanece **Proposed** e a matriz continua **PENDING_APPROVAL**. Recomendação condicional: escolher uma linha dedicada após o owner confirmar o baseline de release/ambiente e a evidência de digest ativo; usar fff somente como SHA de deployment registrado em staging; manter e5 como snapshot de auditoria; reconciliar explicitamente os três commits exclusivos de staging, as mudanças de e5 e os contratos de schema/API/frontend antes de código.

Plano posterior: obter metadados sanitizados por serviço (digest de runtime, build/provenance, SHA e associação de rota/readiness); o owner identifica o recurso de produção; revisar compatibilidade nos SHAs confirmados; aprovar ADR-008 e uma linha técnica antes de qualquer implementação. Nada disso foi executado nesta fase.

## S. Riscos residuais

1. Sem digest ativo ou vínculo com roteamento, usuários podem receber uma revisão diferente da inferida pelo deployment history.
2. A aplicação main encontrada pode não ser produção e está `starting:unknown`; classificá-la incorretamente criaria baseline falso.
3. O G2 GHCR pode existir sem corresponder ao recurso Coolify; a tag não é identidade OCI imutável.
4. Staging API/frontend podem ser incompatíveis no runtime apesar de commits de deployment iguais, pois seus digests/artefatos não foram expostos.
5. Health check desabilitado limita a interpretação do status `running:healthy`.

Mitigação: baseline continua bloqueado; solicitar somente os metadados sanitizados faltantes ao responsável de infraestrutura.

## T–V. Evidências ausentes e segurança

Faltam identificação oficial do recurso de produção, imagem/digest ativo por serviço, attestation/provenance verificável do digest, vínculo com deployment e rota de tráfego, e readiness associado à revisão. O resumo desta fase não contém FQDNs, segredos, URIs, logs, payloads ou dados pessoais. Não houve acesso a DB, shell, Docker remoto, Coolify secrets ou dados curriculares.

## W–X. Arquivos e operações

Documentos criados exclusivamente em `docs/architecture/`:

- [runtime-inventory](editorial-generations-phase-2-1a-12b4a-runtime-inventory.md)
- [image-provenance](editorial-generations-phase-2-1a-12b4a-image-provenance.md)
- [baseline-evidence](editorial-generations-phase-2-1a-12b4a-baseline-evidence.md)
- [compatibility](editorial-generations-phase-2-1a-12b4a-compatibility.md)
- [adr008-review](editorial-generations-phase-2-1a-12b4a-adr008-review.md)
- este relatório

Operações remotas: consultas de leitura `git ls-remote`, GitHub Actions (jobs e metadados de artifact) e Coolify (aplicações, deployments, serviços e inventário de rollback). Escritas remotas: nenhuma. Ações de serviço: nenhuma. Localmente, foi criada uma worktree e foram versionados apenas estes documentos. Nenhum workflow foi iniciado.

## Y. Veredito

**BASELINE PARCIALMENTE COMPROVADO.** Há evidência parcial de staging, mas nenhum baseline de runtime completo com digest e tráfego foi comprovado; produção permanece desconhecida. O ADR-008 e a implementação continuam bloqueados até evidência autorizada e aprovação humana.
