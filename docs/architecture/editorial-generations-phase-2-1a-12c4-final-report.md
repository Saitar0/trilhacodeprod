# Fase 2.1A.12C.4 — Relatório final

## A. Resumo executivo

Foram rastreados **12 grupos de caminhos da aplicação/administrativos**, mais a PoC isolada (W-13), incluindo CRUD/reordenação/duplicação/exclusão, publicação, relações, taxonomias, import, restore, snapshots, comandos de startup e preparação imutável isolada. Foram encontrados bypasses diretos demonstráveis: a maioria dos serviços grava coleções sem revisão editorial comum ou fencing; import/restore usam leases/markers que não aparecem como precondição de todas as escritas; e `publish_track` grava efeitos em múltiplas coleções antes do CAS final de `tracks.version`.

O adaptador validado na Fase 12C.3 permanece isolado e não substitui esses caminhos. O plano recomenda uma autoridade única de comandos e cobertura/isolamento de todos os writers antes de qualquer cutover; dual-write divergente e fallback para leitores legados não são seguros. O inventário não prova quais caminhos estão ativos no deployment. **G1 fica PARTIAL; G2 e os demais gates não são promovidos. ADR-008 permanece bloqueado.**

## B. Git e isolamento

- Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c4-editorial-writer-readiness\trilhacodeprod`
- Branch: `codex/fase2-1a-12c4-editorial-writer-readiness`
- Base exata: `afe84afc964bbb0fec3c4466b1b27a451ff2b65a`
- Alterações previstas: apenas os três Markdown da Fase 12C.4.
- Checkout original com alterações preexistentes não foi tocado; nenhuma outra worktree foi alterada.

## C. Escopo analisado

Foram lidos entrypoints e serviços de conteúdo, taxonomia, importação, versões/restauração, integridade, auditoria, seed, manage e configurações versionadas de inicialização, além do adaptador C1/C2 e relatórios C3. A análise permaneceu estática. Não foram executados endpoints, jobs, scripts, MongoDB, Docker ou fluxos editoriais; não houve consultas à infraestrutura.

## D–G. Escritores, bypasses e controles

O inventário documentado em [writer-inventory](editorial-generations-phase-2-1a-12c4-writer-inventory.md) contém W-01–W-13, agrupados por serviço. Os principais achados confirmados no código são:

1. CRUD/reorder/duplicate/delete de track, node, block e relation opera diretamente nas coleções vivas sem revisão monotônica/fence comum.
2. `publish_track` persiste publicações de atividades e snapshot/version antes do CAS final do documento `tracks`; status de nodes/blocks também pode ser alterado antes desse CAS.
3. Importação usa job, lease e `_import_state`, mas as mutações de nodes/blocos/relações não usam uma authority/fence comum por write.
4. Restore substitui nodes/blocks/relations por delete e insert em lotes; o owner da lease não é precondição por mutação da estrutura restaurada.
5. Snapshot atual compara contagens antes/depois, insuficiente para detectar mudança de conteúdo com cardinalidade preservada.
6. Taxonomia global e exclusão de tag mudam dados compartilhados sem revisão de catálogo/trilhas comum.
7. O adaptador não está conectado a routers/serviços examinados. A PoC e o preparador de publicação imutável não são evidência de integração ativa.

Rotas têm controles de permissão em nível de aplicação; esses controles não equivalem a fencing persistente, CAS ou roles Mongo. Algumas rotas descartam o ator e serviços de taxonomia/reordenação não registram identidade de autor nos trechos examinados. Não foram inspecionados grants de ambiente real.

## H. Compatibilidade com o adaptador

Há incompatibilidade de fronteira: as operações legadas são assíncronas e gravam diretamente diversas coleções; o adaptador C2 é síncrono e mantém seu próprio estado, recibos e histórico no namespace de teste. Não existe envelope comum para operações compostas, mapeamento de autenticação para capability, fence compartilhado, compatibilidade de tamanho para importação (rota aceita até 32 MiB; adaptador tem limite próprio inferior/configurável), nem demonstração de comportamento no runtime. `tracks.version` não deve ser confundido com revisão editorial.

## I–J. Segurança, publicação e restauração

Permissões de rota ajudam na autorização do usuário, mas não cercam todas as escritas no armazenamento. As mutações de publicação/restauração não podem ser tornadas seguras apenas adicionando um CAS de revisão: geração imutável, separação público/privado, validação e CAS de head são obrigações distintas do ADR-006 e dependem de revisão coerente (ADR-001) e proteção de dados privados (ADR-005).

Restauração atualmente reconstrói coleções mutáveis; publicação atual tem CAS final limitado a `tracks.version`. Nenhum dos mecanismos equivale à seleção atômica de um head de geração completa. Quizzes são transformados em documentos de publicação durante publish, mas não há base para aprovar publicação independente por geração.

## K–L. Riscos e plano futuro

Riscos maiores: bypass em CRUD/import/restore/publicação, estado parcial em operações multi-coleção, exclusões com efeitos sobre progresso e taxonomias globais, e incompletude operacional fora do repositório. O [plano de prontidão](editorial-generations-phase-2-1a-12c4-integration-readiness.md) define incrementos, dependências, testes e recuperação.

Primeiro passo futuro sugerido: instrumentação passiva de todos os entrypoints, sem payload ou efeito editorial, após baseline e autorização próprios. Se não for possível cobrir todos os caminhos e validar privacidade da telemetria, interromper; observabilidade parcial não autoriza migração de writer.

## M. Gates e ADR-008

Estados históricos preservados: G1 `PARTIAL`, G2 `NOT_VERIFIED`, G3 `NOT_VERIFIED`, G4 `PARTIAL`, G5 `NOT_VERIFIED`, G6 `PARTIAL`, G7 `PARTIAL`, G8 `NOT_VERIFIED`, G9 `BLOCKED`, G10 `BLOCKED`. O inventário adiciona evidência documental, não prova proteção ou execução real.

ADR-008 continua bloqueado por ausência de serviço de produção identificado, digest ativo, proveniência runtime→imagem→build→commit, rota/tráfego/readiness e linha de release aprovada. Não houve nova consulta ao Coolify, GHCR, bancos ou outros ambientes. Referência sanitizada: [pedido ao administrador em 12B.4B](editorial-generations-phase-2-1a-12b4b-admin-evidence-request.md).

## N–Q. Arquivos e validações

Arquivos desta fase:

- [Inventário de escritores](editorial-generations-phase-2-1a-12c4-writer-inventory.md)
- [Prontidão e plano de integração](editorial-generations-phase-2-1a-12c4-integration-readiness.md)
- [Relatório final](editorial-generations-phase-2-1a-12c4-final-report.md)

Validações: somente três arquivos Markdown novos em `docs/architecture/`; referências de código, links relativos e anchors de linha revisados; `git diff --check` passou; nenhum código, teste, configuração, ADR ou matriz histórica foi alterado; os diretórios protegidos não foram materializados; varredura documental não identificou credenciais ou dados pessoais. Nenhum teste de aplicação foi executado por instrução de escopo. A checagem de imports não encontrou uso do adaptador nos routers/serviços editoriais; os hits em `immutable_publications.py` referem-se apenas ao texto do bloqueio `editorial_revision_protocol_required`.

## R. Limitações

- Código examinado é somente o snapshot `afe84afc964bbb0fec3c4466b1b27a451ff2b65a`.
- A implantação e a linha de release não foram identificadas nesta fase.
- Chamadas externas, jobs operacionais, scripts não versionados, invocação real do compose e completude da lista de escritores não são comprováveis pela inspeção local.
- Riscos classificados refletem capacidade/impacto observado no código, não frequência real em produção.

## S. Veredito

**ESCRITORES IN-REPO MAPEADOS COM LIMITAÇÃO DE COBERTURA OPERACIONAL — PLANO PREPARADO; IMPLEMENTAÇÃO NÃO AUTORIZADA**
