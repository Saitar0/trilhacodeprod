# Beta 6 — arquitetura da primeira jornada de aprendizagem

## Escopo e estado

Implementação confinada à worktree Beta 6. O fluxo reutiliza `current_user`, JWT/sessão e permissões existentes; mantém as rotas de atividades e submissões no backend; e adapta projeções, escopo do avaliador e sincronização de progresso. A leitura curricular continua sob `get_node`/`can_view_node`. Nenhuma rota de importação, publicação ou promoção de staging foi conectada.

Fluxo pretendido: sessão autenticada → unidade legível → quiz versionado sem gabarito → tentativa avaliada pelo servidor → exercício manual enviado → avaliação por instrutor com escopo explícito da trilha → feedback e projeção idempotente de progresso.

As novas regras estão implementadas na branch, mas a prova HTTP/persistente está **NOT RUN**: a infraestrutura Beta 6 não conseguiu expor a porta de loopback exigida pelo verificador, e o harness abortou antes de abrir uma conexão MongoDB. Portanto, este documento não declara a jornada integrada validada.

## Fronteiras de autorização

* Rotas de mutação exigem usuário obtido por dependência real e permissão `progress.write` ou `submissions.grade`; cookie mutante também passa por validação de origem.
* A leitura de atividade usa o leitor e as verificações de visibilidade existentes.
* A fila, detalhe, claim e correção exigem permissão estática mais registro sintético ativo por `user_id`, `track_id` e operação em `learning_review_scopes`. Sem ambos, nega por padrão.
* O registro de escopo é somente uma política experimental provisionada no banco descartável. Não existe administração operacional de grants, nem se pretendeu substituir IAM.
* O cliente não define identidade, papel, gabarito, resultado de quiz, autor da submissão ou autoridade de correção.

## Consistência e histórico

Tentativas e correções usam revisão condicional do documento para evitar sobrescrita concorrente. Chaves de idempotência são vinculadas ao usuário e ao fingerprint do conteúdo. Uma chave reutilizada para outro payload dá conflito. Eventos e projeção de progresso usam IDs determinísticos e podem ser reconciliados por repetição; isso não é uma transação distribuída única, e o cenário persistente Beta 6 permanece não executado.

Submissões guardam versão derivada da atividade e contexto restrito de correção. Projeções do aluno usam allowlists fechadas e removem rubricas, respostas de referência, notas internas e campos futuros desconhecidos. Respostas de instrutor também são allowlisted. `get_node` mantém a projeção pública de avaliações e não libera campos privados.

## Interface

O leitor e componentes de atividades existentes são reutilizados. O formulário de exercício apresenta instruções públicas e preserva a chave de idempotência ao tentar novamente após erro de rede. O painel existente de correção consome os endpoints de submissões e apresenta critérios apenas após retorno autorizado do servidor. Typecheck, lint e testes de componentes passaram; nenhuma inspeção visual de navegador ou jornada com backend ativo foi concluída.

## Dependências para ativação futura

1. IAM aprovar grants por trilha e um ciclo de vida confiável para `learning_review_scopes`.
2. Resolver contenção de writers editoriais C8–C16; Beta 6 não toca conteúdo protegido.
3. Executar a suíte HTTP em MongoDB comprovadamente descartável e corrigir qualquer falha observada.
4. Validar o fluxo navegador/frontend contra backend e banco isolados.
5. Definir política pedagógica para critérios de domínio e liberação de explicações.
6. Homologar segurança, acessibilidade, mobile, logs, backups e rollback antes de qualquer ambiente de alunos.

Gates históricos continuam G1 PARTIAL, G2 NOT_VERIFIED, G3 NOT_VERIFIED, G4 PARTIAL, G5 NOT_VERIFIED, G6 PARTIAL, G7 PARTIAL, G8 NOT_VERIFIED, G9 BLOCKED e G10 BLOCKED. ADR-008 continua bloqueado.
