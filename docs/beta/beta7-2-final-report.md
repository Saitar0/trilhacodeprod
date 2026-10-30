# Trilha Code — Beta 7.2: relatório final

## A. Resultado executivo

Foram entregues contratos versionados de rubrica, registro imutável de avaliação, revisão/reenvio do projeto 3.5 e agregação fail-closed de conclusão. A rubrica real da fonte continua `PROPOSED`; portanto, a avaliação real pode registrar feedback e pedir revisão, mas não aprovar nem concluir a primeira fase. A mecânica técnica de aprovação/conclusão foi testada apenas com rubrica explicitamente sintética.

**Veredito:** AVALIAÇÃO PEDAGÓGICA VERSIONADA VALIDADA TECNICAMENTE — APROVAÇÃO DA RUBRICA REAL PENDENTE.

## B–C. Git, isolamento e fonte

Base exata `2202905adf5e3d274a960fd4284b1c7d4964a707`; worktree e branch Beta 7.2 isoladas; nenhuma outra worktree ou checkout foi alterado. Fonte: worktree de migração, revisão `147dc68b81169f66b0ba3802fa2f26e5130923a3`, arquivos curriculares do escopo limpos, estado editorial `rascunho`. Os hashes do manifesto Beta 4 foram conferidos antes da cópia de leitura; o conversor confirmou a fonte-piloto 1.1 e o manifesto canônico. O material original não foi modificado.

## D–G. Projeto, critérios e decisões pedagógicas

O projeto prepara uma base segura, reproduzível e compreensível para um repositório mantido ao longo do curso; não pede a arquitetura nem as funções finais do produto nesta fase. Os quatro marcos tratam de: problema/escopo; repositório e setup reproduzível; histórico/configuração segura; publicação/conferência remota. A fonte nomeia brief e issue, README/setup, árvore e commits, `.gitignore`, clone limpo, repositório remoto, issue atualizada e README final.

A rubrica fonte traz descritores 0–4 para cada marco e proíbe aceitar os marcos 3–4 quando credencial real ou dado pessoal estiver versionado. Não define agregação dos quatro resultados, obrigatoriedade dos cinco checklists, resolução de “lacuna menor”, pacote mínimo de evidências por avaliador nem protocolo de comprovação/recuperação para a condição de segredo. Os critérios textuais das unidades tampouco fornecem limiares computáveis de domínio. A matriz e as perguntas para decisão humana constam em [inventário pedagógico](beta7-2-pedagogical-criteria-inventory.md) e [decisões pendentes](beta7-2-pedagogical-decisions-required.md).

## H–I. Rubrica e versionamento

`VersionedRubric` registra projeto, rubrica, versão, estado editorial, proveniência/hash, critérios, descritores, restrições fonte, regra e registro explícito de aprovação. Estados: `DRAFT`, `PROPOSED`, `PEDAGOGICALLY_APPROVED`, `RETIRED`. Validar Pydantic prova coerência estrutural, não aprovação pedagógica. A fonte foi materializada como `PROPOSED`, sem regra ativa e sem aprovador inventado. A avaliação guarda versão e hash da rubrica; versões posteriores não alteram registros anteriores. A restrição dos marcos 3–4 fica tipada como condição impeditiva ligada aos marcos, sem inventar seu método de verificação.

## J–P. Entrega, revisão, avaliação, autorização, concorrência e histórico

Entrega usa identidade da sessão, versão do projeto, chave idempotente e cadeia `previous_submission_id`; reenvios preservam a tentativa anterior. O avaliador requer permissão `submissions.grade`, grant sintético ativo para o lote e sessão válida. Aluno vê apenas o próprio estado/feedback; rubrica e fila são restritas. A API rejeita tentativa de aprovação com rubrica `PROPOSED` (`409`), mas permite feedback e pedido de revisão.

Decisão, evento de auditoria, CAS da submissão e revisão/fence do grant são gravados na mesma transação MongoDB. Retry idêntico retorna o recibo existente; mesma chave com payload diferente recebe `409`. Na prova concorrente com dois avaliadores sintéticos, exatamente uma decisão foi confirmada; a outra recebeu conflito; permaneceu um evento e revisão 1. Uma segunda versão sintética foi inserida e o evento anterior manteve sua versão/hash. Isso valida o mecanismo na fixture, não IAM operacional nem todas as condições de corrida possíveis.

## Q–T. Privacidade e conclusão

`STUDENT_PUBLIC`, `INSTRUCTOR_RESTRICTED` e `SYSTEM_INTERNAL` permanecem separados. O aluno não recebe rubrica, evidências restritas ou critérios da avaliação de terceiros. A projeção de histórico do aluno limita-se a suas decisões/feedback.

O cálculo determinístico de unidade/módulo/fase aceita apenas requisitos definidos, obrigatoriedade explícita e resultado aprovado para a versão exata. Política vazia, versão obsoleta, critério ambíguo/proposto/não verificado e rubrica ausente bloqueiam conclusão. A fase precisa conter a unidade 3.5 e sua rubrica-fonte; enviar ou abrir uma atividade nunca conclui domínio. Todos os critérios fonte da primeira fase continuam bloqueados por falta de protocolo pedagógico aprovado.

## U–X. Fixture, projeto real, frontend, HTTP e persistência

Uma política de rubrica e evidências totalmente sintéticas demonstrou avaliação aprovada e conclusão técnica. Ela não está associada ao projeto 3.5 real e não altera o progresso curricular. A entrega real recebeu feedback/pedido de revisão e foi reenviada; a tentativa anterior permaneceu no histórico. Nenhuma aprovação real foi concedida.

Resultados da execução isolada:

* MongoDB 7 descartável em replica set, rede interna, credenciais/IDs exclusivos, sem portas publicadas e sem mounts persistentes; ownership gate antes de qualquer seed/escrita.
* Execução final do harness: run ID `308f3ab6653745e792274c042c34efdb`; banco `beta7_1_308f3ab6653745e792274c042c34efdb`; contexto Docker `desktop-linux`; container Mongo `da3ec4b5f6934ea35918a2a52521f240e8e0eb8ec4f1318598bdb975bf56e215`, runner `00442bf6a0a36c8e7b01a108b5c22b49c61438e61d0d6acc95e451599c8a676f`, rede interna `f5b8cdba22c9cda511c2263b8ed1a614135a4ee1837913137744add85d02e36b`. O harness Beta 7.1 foi reutilizado, mas provisionou identidades próprias para esta execução; após finalizar, a consulta por esse run ID encontrou zero containers e zero redes. Nenhuma credencial foi registrada.
* Conversão/preparação: 3 módulos, 10 unidades, 30 tópicos, 42 segmentos, 44 questões, 26 exercícios, 39 referências, 30 relações e 11 materiais do projeto; 161 blocos e 21 relações persistidas. Estado original `draft/private`; zero registros de publicação.
* Offline no runner com fonte montada: 13 testes aprovados. HTTP: 10 unidades/3 módulos, projeções protegidas, reader operacional privado `404`, pedido real de revisão persistido.
* Playwright: uma jornada real percorreu as dez unidades, validou os quatro critérios M01–M04 da rubrica restrita com evidências e hashes dos respectivos marcos, tentou aprovação (bloqueada), solicitou revisão, reenviou, verificou linhagem/histórico após recarga e confirmou negativa a avaliador sem escopo.
* Prova persistente Beta 7.2: aprovação e conclusão apenas sintéticas; retry idempotente, payload divergente `409`, versão nova sem reescrita histórica e disputa simultânea 1 confirmação/1 conflito.

TypeScript, ESLint, 29 testes Vitest e build passaram. O chunk principal ficou em 506,07 kB sem compressão, mantendo o aviso prévio acima de 500 kB. O histórico da tentativa HTTP e do Playwright compartilhou a fixture; o E2E passou a derivar o número da nova tentativa do histórico existente, sem limpar registros para forçar o número 2.

## Y–AA. Testes e regressões

Ruff passou nos arquivos Python alterados; MyPy passou direcionado em cinco módulos; compilação sintática e `git diff --check` passaram. Regressões exercitadas: testes Beta 7.1 HTTP, leitor privado, fluxo persistente de revisão, prova de concorrência revogação/CAS, E2E das dez unidades e suíte frontend. A suíte histórica completa do backend não foi repetida; outros testes persistentes históricos não foram executados sem inspeção específica de seus efeitos. A execução final não teve falhas. Duas expectativas do E2E foram corrigidas durante a validação: uma mensagem textual e o número de tentativa, que deve considerar o registro criado pelo teste HTTP anterior.

## AB–AE. Segurança editorial, gates, arquivos e limitações

Sem promoção de staging, publicação, writer editorial, rota operacional, IAM global, banco real, conteúdo fonte, certificado ou deploy. Rotas Beta 7.2 existem apenas na composição test-only montada após o gate Docker. C8–C16 e ADR-008 permanecem dependências bloqueadas; grants continuam sintéticos. Nenhuma matriz histórica de gates foi alterada: G1 PARTIAL, G2 NOT_VERIFIED, G3 NOT_VERIFIED, G4 PARTIAL, G5 NOT_VERIFIED, G6 PARTIAL, G7 PARTIAL, G8 NOT_VERIFIED, G9 BLOCKED, G10 BLOCKED.

Arquivos novos: três contratos curriculares; schema e serviço isolado de avaliação; router e harness de prova; dois testes offline; oito documentos beta. Arquivos Beta 7.1 alterados para ligação experimental: serviço de prévia, seed, composição de teste, harness e tela/E2E. Nenhuma fonte curricular original foi modificada.

Limitações: falta aprovação pedagógica humana da rubrica; não há regra de agregação final aprovada nem evidências mínimas por marco; ausência de integração com IAM global/C8–C16; não foi validada a retenção operacional ou consumo por leitores reais fora do ambiente de prévia. A fixture sintética não cobre a avaliação curricular real.

## AF–AI. Próximo passo e veredito

Solicitar ao responsável pedagógico uma decisão rastreável sobre obrigatoriedade dos quatro marcos/checklists, regra de composição dos níveis 0–4, evidências por marco, tratamento de lacunas e condição de credenciais/dados pessoais. Só então criar nova versão da rubrica com aprovação explícita; preservar a versão atual proposta e os registros anteriores. Em paralelo, a integração operacional depende de resolver C8–C16/ADR-008 antes de qualquer promoção.

**Conclusão técnica:** o mecanismo de avaliação versionada, revisão, histórico, bloqueio de aprovação, idempotência, concorrência e projeção de conclusão está validado tecnicamente no escopo isolado. **Conclusão pedagógica real da primeira fase:** pendente; o sistema corretamente não declara domínio nem conclusão.
