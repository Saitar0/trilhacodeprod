# Fase 2.1A.12B.4 — relatório de baseline e preparação das aprovações

## Resultado executivo

As referências públicas atuais de main e staging foram confirmadas e comparadas com o snapshot técnico e5bf3147…. Foram examinados workflows, documentação de deploy e metadados públicos de runs. Há evidência de builds associados a SHAs, inclusive um build/push de imagem de backend em 41dc470…, mas não há digest da imagem atualmente em execução nem registro verificável de implantação por ambiente.

Conclusão: **BASELINE IMPLANTADO NÃO COMPROVADO**. A recomendação é manter e5 como referência da auditoria, não tratá-lo como produção, e escolher a futura linha de implementação por decisão ADR-008 depois de reconciliar a imagem implantada, main, staging e as alterações do snapshot.

## Git e isolamento

- Worktree: C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12b4-baseline-adr-approval\trilhacodeprod.
- Branch: codex/fase2-1a-12b4-baseline-adr-approval.
- Base: 45fa5c5ff81982f7b784753e31a1dda0ce56cf5f.
- Pai da base: 4805e3caab18f183c37375d23af1b2e12a425d1b.
- Snapshot de código: e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.
- Remote configurado: https://github.com/Saitar0/trilhacodeprod.git.
- A worktree foi criada sem checkout inicial; sparse-checkout foi definido antes da materialização.
- docs/courses/trilhacode/ e docs/migracao/ não foram materializados.

## Evidências e limites

Detalhes em [evidências de baseline](editorial-generations-phase-2-1a-12b4-baseline-evidence.md). Em síntese:

- GitHub API consultada em 2026-10-28: main=22dca64556338a8fa9aaa89ce627a4f4af72317d, staging=fff85218fd71b164dc7465ca72d22b4a53232f49, default branch main.
- CI em main (run 40488544210, push, checks E2E concluídos) teve deploy-staging e deploy-production ignorados.
- CI em staging (run 40394870286, push) também teve deploys ignorados.
- A configuração versionada em DEPLOY.md descreve produção por main, staging por staging e webhook manual; não prova a configuração efetiva atual do Coolify.
- Run 39179762892 confirma build/push GHCR de backend para SHA 41dc470…; check-run não expôs digest na resposta consultada, e não foi feita consulta a registry privado.
- Run 38979959967 é build local no runner em SHA 17b3bf1…; workflow declara que não publicou nem implantou.
- A PoC aprovada no run 40686021030 comprova o protocolo isolado em MongoDB 7.0.45 descartável. Não comprova integração nem deploy da aplicação.
- Nenhum endpoint privado, Coolify, SSH, Docker de produção ou banco foi acessado. Não houve acesso a dados de alunos.

Evidência necessária: digest imutável atualmente em execução para API e frontend por ambiente, metadados que associem o digest ao SHA/run de build e registro de deploy/saúde. Obter via responsável de infraestrutura e autorização separada.

## Compatibilidade e recomendação

Consulte [compatibilidade de branches](editorial-generations-phase-2-1a-12b4-branch-compatibility.md). O diff main...staging contém um commit exclusivo de main e três de staging; merge-base 9b79751278496e51134a6ab8d495706bb2c700a7. main é ancestral do snapshot local e5; snapshot tem 21 commits além de main. Em comparação com staging, há três commits exclusivos de staging e 22 do snapshot.

O diff main/staging nas áreas comparadas mostrou backend/settings.py e .github/workflows/foundation-validation.yml. Em settings, main exige validação SMTP em staging mesmo com transporte local; staging dispensa essa validação para o transporte local. O snapshot e5 difere amplamente: serviços e schemas de atividades, importação, progresso, submissões, sessões, publicação imutável, PoC e frontend. Isso impede tratar e5 como simples extensão operacional sem reconciliar interfaces e dados.

Recomendação condicional: Opção D, linha de integração isolada derivada do baseline de release que o owner aprovar, com portabilidade seletiva e testes de compatibilidade; e5 permanece a linha de referência da auditoria/PoC. A linha release pretendida descrita em DEPLOY.md é main para produção, mas a imagem efetivamente implantada e a operação atual não foram comprovadas.

## Decisões arquiteturais

Os oito ADRs originais estão presentes e todos permanecem Proposed. Nenhum foi alterado ou aprovado nesta fase. Fichas e estados em [matriz de aprovação](editorial-generations-phase-2-1a-12b4-approval-matrix.md) e [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md); todos os oito estão PENDING_APPROVAL.

- ADR-008: baseline e compatibilidade — decisão inicial bloqueante.
- ADR-001: revisão monotônica, writers, fencing e conflitos.
- ADR-005: leitor público, papéis e projeção allowlist.
- ADR-003: taxonomias/metadados congelados ou versionados.
- ADR-002: pin de sessão, versão de atividade e progresso.
- ADR-004: retenção, referências e exclusão; sem prazo inventado.
- ADR-006: geração selada, seleção CAS, leitor fixado e restore; depende de ADR-001.
- ADR-007: migração gradual, flags off, writers antes de readers e zero bypass.

## Gates e primeira fase

Os gates continuam bloqueados ou pendentes; propostas não contam como aprovação. Ver [gates de implementação](editorial-generations-phase-2-1a-12b4-implementation-gates.md). A menor fase futura sugerida é resolver baseline primeiro e, somente após ADR-008 e revisão de privacidade, adicionar instrumentação passiva sem alterar payload ou comportamento. Não se recomenda começar por migração, publicação ou troca de leitor.

## Operações e validação

Operações realizadas: leitura Git local; ls-remote de branches; consultas públicas GitHub REST para metadados de repositório, branches, workflows, runs, jobs e check-runs; leitura estática de arquivos versionados. Nenhuma escrita remota, execução de workflow, deploy, alteração de infraestrutura, conexão a banco ou operação Docker ocorreu.

As verificações finais de documentação e commit estão reportadas na resposta da fase. O executor independente foi consultado apenas por API pública: HEAD 701b314230af3a87765a08671e1b69fd7b9864ac, transporte desabilitado.

**Veredito:** **DECISÕES PREPARADAS — BASELINE IMPLANTADO PENDENTE**.

**Próxima ação mínima:** obter evidência sanitizada de digest em execução e sua proveniência por ambiente, e aprovar ADR-008 antes de qualquer alteração de runtime.

## Índice do relatório obrigatório A–Y

### A. Resumo executivo

Referências Git confirmadas; build de backend associado a um SHA encontrado; baseline implantado sem comprovação de nível 1. As oito decisões estão preparadas, não aprovadas.

### B. Git e isolamento

Worktree, branch, base, parent, remote e ausência de materialização dos caminhos protegidos constam em “Git e isolamento” acima. O commit documental B3 não alterou a árvore de código do snapshot.

### C. Evidências de implantação

Fontes públicas e versionadas, horários, runs, limites e níveis de confiança: [evidências de baseline](editorial-generations-phase-2-1a-12b4-baseline-evidence.md).

### D. Baseline implantado

Não comprovado para produção nem staging. Não há SHA/digest de API e frontend ligados a container efetivamente servido.

### E. Lacunas de rastreabilidade

Faltam digest em execução por aplicação/ambiente, proveniência digest→SHA, registro de deploy e confirmação de saúde/readiness. Evidência a solicitar sem tokens nem dados pessoais: [evidências de baseline](editorial-generations-phase-2-1a-12b4-baseline-evidence.md).

### F. Compatibilidade de branches

SHAs, merge-bases, commits exclusivos, diferenças por área e trade-offs: [compatibilidade](editorial-generations-phase-2-1a-12b4-branch-compatibility.md).

### G. Baseline de implementação

Recomendação condicional pela opção D: após o owner selecionar release baseline com evidência, criar linha de integração isolada e reconciliar mudanças escolhidas; usar e5 como referência de auditoria, não como origem automática de release.

### H. ADR-008

Decisão inicial bloqueante: identificar SHA/digest implantado e selecionar linha reconciliada. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-008--baseline-e-compatibilidade).

### I. ADR-001

Proposta de revisão monotônica, snapshot coerente e conflito explícito; todos os escritores precisam respeitar o mecanismo. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-001--revisao-e-concorrencia-editorial).

### J. ADR-005

Proposta de defesa em profundidade: storage/identidade segregados, reader mínimo e DTO allowlist. Grants do ambiente real não foram consultadas. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-005--separacao-de-dados-publicos-e-privados).

### K. ADR-003

Classificação de campos que alteram sentido, apresentação, ordenação ou validação é pendente de produto/frontend; nenhuma taxonomia foi classificada como decisão aprovada. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-003--taxonomias-e-metadados).

### L. ADR-002

Recomendação de geração fixada pelo servidor para sessão e definição original fixada por tentativa; expiração, conclusão tardia e revogação dependem de decisão de produto. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-002--geracao-de-sessao-e-progresso).

### M. ADR-004

Retenção baseada em referências/obrigações é proposta; não foi fixado prazo. GC e exclusão definitiva permanecem bloqueados até política de produto, privacidade e inventário de referências. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-004--retencao-e-exclusao).

### N. ADR-006

Proposta: construir, validar e selar antes de selecionar por CAS; leitores pinados; restore como nova geração; sem fallback live inseguro. Depende de ADR-001. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-006--publicacao-e-restauracao-atomicas).

### O. ADR-007

Proposta de migração gradual com flags off, escritores antes de readers e zero bypass antes do cutover. Ficha: [decision briefs](editorial-generations-phase-2-1a-12b4-decision-briefs.md#adr-007--migracao-gradual-e-coexistencia).

### P. Matriz de aprovação

Oito linhas, todas PENDING_APPROVAL, com ordem de dependências e categoria: [matriz de aprovação](editorial-generations-phase-2-1a-12b4-approval-matrix.md).

### Q. Perguntas humanas

Produto/pedagogia: duração de sessão, tentativa antiga, restore, retirada urgente, progresso legado e histórico de nota. Segurança/privacidade: papéis para gabaritos, campos pessoais, exclusão e autoridade de retenção. Operação: ambiente inicial, linha oficial, evidência de runtime e procedimento de cutover. A lista objetiva está na matriz.

### R. Gates de implementação

Baseline, reconciliação, inventários, decisões, rollback, observabilidade e autorização específica estão pendentes/bloqueados: [gates](editorial-generations-phase-2-1a-12b4-implementation-gates.md).

### S. Primeira fase executável proposta

Após aprovação do ADR-008: reconciliação isolada do baseline e instrumentação passiva sanitizada. Sem alterar payload, autorização, ordem de escrita, persistência ou resposta pública; não é autorizada nesta fase.

### T. Arquivos produzidos

Seis documentos listados na seção [arquivos locais](#arquivos-locais).

### U. Validações

Validado: escopo dos seis Markdown, links relativos, oito ADRs ainda Proposed, oito linhas PENDING_APPROVAL, ausência de padrões de segredo, diff check e árvore de código. Não foram executados testes de aplicação, Docker, MongoDB ou Actions, conforme escopo.

### V. Segurança

Sem credenciais, segredos, URI autenticada ou dados de aluno nos novos documentos. Os caminhos editoriais protegidos não foram materializados. Nenhuma infraestrutura privada foi acessada.

### W. Operações remotas

Somente consultas públicas Git/GitHub de leitura. Nenhum push, PR, merge, rebase, workflow, deploy, acesso a Coolify, MongoDB ou Docker ocorreu.

### X. Próxima autorização

Obter via responsável de infraestrutura os metadados sanitizados de digest e SHA em execução, por ambiente; em seguida, aprovar ADR-008 e decidir a linha de desenvolvimento. Acesso privado necessita autorização separada.

### Y. Veredito

**DECISÕES PREPARADAS — BASELINE IMPLANTADO PENDENTE**.

## Arquivos locais

1. [Evidências de baseline](editorial-generations-phase-2-1a-12b4-baseline-evidence.md).
2. [Compatibilidade entre branches](editorial-generations-phase-2-1a-12b4-branch-compatibility.md).
3. [Matriz de aprovação](editorial-generations-phase-2-1a-12b4-approval-matrix.md).
4. [Fichas resumidas dos ADRs](editorial-generations-phase-2-1a-12b4-decision-briefs.md).
5. [Gates e fase futura](editorial-generations-phase-2-1a-12b4-implementation-gates.md).
6. Este relatório.
