# Beta 1 — auditoria executiva

Inspeção em 2026-10-29. Base analisada: C16, sem fetch, banco, serviço, importação, publicação ou endpoint externo. É um retrato estático/local, não certificação operacional.

## Veredito

**AUDITORIA DA BETA PARCIAL — INTEGRAÇÕES E VALIDAÇÕES PENDENTES.** A árvore C16 contém uma aplicação de aprendizagem com autenticação/sessão, catálogo/leitor, publicação e versões, quiz objetivo versionado com tentativas persistidas, progresso, submissão de exercícios e correção manual. Há telas administrativas e um pacote de curso estruturado.

A jornada ponta a ponta não foi executada. O pacote C16 está todo em `draft` e importa teoria/resumo/notas, não quizzes interativos. O conteúdo segmentado e o contrato tipado encontrados na worktree `migracao-estrutura` não estão integrados; a worktree também tem mudanças locais. C8–C16 fornecem provas editoriais experimentais, mas C16 demonstra bypass por credencial MongoDB de escrita direta. A versão operacional não foi verificada; ADR-008 permanece bloqueado.

## Retrato da plataforma

| Domínio | Estado na C16 | Evidência | Consequência |
|---|---|---|---|
| Backend FastAPI | `IMPLEMENTED_IN_INSPECTED_CODE` | Rotas/serviços e testes no repositório | Presença não prova runtime atual |
| Autenticação | `IMPLEMENTED_IN_INSPECTED_CODE` | JWT, sessão, verificação de email, reset | E2E e homologação pendentes |
| Leitor/catálogo | `IMPLEMENTED_IN_INSPECTED_CODE` | React chama `/tracks`, `/tree`, `/progress` | Visual/mobile e jornada `NOT_VERIFIED` |
| Quiz objetivo | `IMPLEMENTED_IN_INSPECTED_CODE` | Publicação imutável, tentativas e avaliação | O bundle C16 não traz blocos quiz |
| Exercícios escritos | `IMPLEMENTED_IN_INSPECTED_CODE` | Submissão, histórico e correção humana | Não há executor de código |
| Progresso | `IMPLEMENTED_IN_INSPECTED_CODE` | Serviço e endpoints | Regressões selecionadas, sem E2E nesta fase |
| Curso C16 | `PARTIALLY_IMPLEMENTED` | 10 fases, 53 módulos, 131 unidades, 1.691 blocos todos draft | Conteúdo não publicado/não disponível ao aluno |
| Migração curricular | `IMPLEMENTED_ON_ISOLATED_BRANCH` | Worktree migratória, conteúdo segmentado e novo contrato | Precisa revisão/reconciliação, não importar |
| Tutor IA | `NOT_FOUND` no produto inspecionado | Dependências presentes, sem serviço/rota/tela encontrados | Adiar |
| Laboratório executável | `NOT_FOUND` | Bloco de código permite copiar; sem sandbox no produto | Não executar código de aluno |
| XP/RPG/pagamentos/Pioneiros | `NOT_FOUND` no produto inspecionado | Sem rotas/modelos/telas encontradas | Não confundir dependência Stripe com pagamentos |
| Segurança editorial | `EXPERIMENTAL_ONLY` | C8–C16 e testes isolados | Não prova enforcement global |
| Infra operacional | `NOT_VERIFIED` | Apenas configuração versionada | ADR-008 bloqueado |

`NOT_FOUND` é limitado às áreas de produto inspecionadas. Níveis e distinções de evidência estão no relatório final.

## Curso no snapshot C16

O diretório versionado contém 159 Markdown e um JSON. O bundle registra 10 fases, 53 módulos, 131 unidades, 194 nós, 1.691 blocos e 50 relações; todos os blocos são `draft`. Tipos: 1.567 `theory_text`, 123 `summary`, 1 `instructor_note`; sem quiz/exercício estruturado. Um scan encontrou quatro ocorrências de links relativos quebrados e nenhum Markdown sem H1. É análise estrutural, não avaliação pedagógica humana.

O conteúdo segmentado em worktrees tem outro estado Git; não deve ser tratado como integrado ou canônico sem decisão do owner.

## Escopo recomendado aos Pioneiros

Beta A reforçada: convites manuais; gratuita, sem cartão/cobrança; uma fase completa somente após transformação, revisão e importação validada; leitura, quiz objetivo versionado, entrega de exercícios com correção manual, progresso, suporte e feedback. 20–50 participantes é cenário de planejamento, não decisão aprovada. Não ampliar para segunda fase antes de a primeira passar critérios de completude e suporte.

Adiar execução de código, tutor IA, pagamentos, certificados, comunidade e gamificação avançada. O benefício planejado de 60 dias Premium pós-lançamento não requer assinatura durante a beta.

## Bloqueios P0

* Decidir base canônica e reconciliar branches sem sobrescrever worktrees sujas.
* Escolher fonte curricular; compatibilizar conteúdo revisado com o importador e validá-lo em ambiente apropriado.
* Testar jornada E2E e mobile/visual antes de convidar participantes.
* Aprovar operação, privacidade/retenção, suporte, backups e restore.
* Satisfazer baseline e controles de segurança antes de persistir dados de alunos.
* Conter writers editoriais ou congelar conteúdo publicado com controles comprováveis; C16 demonstrou bypass direto.

## Documentos

[Git](beta1-git-integration-inventory.md) · [Backend](beta1-backend-feature-inventory.md) · [Frontend](beta1-frontend-feature-inventory.md) · [Curso](beta1-course-revision-audit.md) · [Compatibilidade](beta1-course-platform-compatibility.md) · [Jornada](beta1-student-journey.md) · [Segurança](beta1-security-and-infrastructure.md) · [Pioneiros](beta1-pioneers-scope.md) · [Backlog](beta1-prioritized-backlog.md) · [Roadmap](beta1-roadmap-and-estimates.md) · [Relatório](beta1-final-report.md)

Nenhuma funcionalidade foi implementada, nenhum conteúdo foi alterado e este documento não autoriza integração ou lançamento.

Matriz estruturada filtrável: [beta1-feature-inventory.json](beta1-feature-inventory.json).
