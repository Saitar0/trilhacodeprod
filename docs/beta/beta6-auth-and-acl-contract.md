# Beta 6 — autenticação e autorização por recurso

## Autenticação

As rotas reutilizam `security.current_user` e `permissions.require`; não aceitam `user_id`, papel ou `is_admin` do corpo como identidade. O mecanismo existente valida o token/sessão e carrega o usuário; as mutações usam a permissão de progresso ou correção já definida. A autenticação deve ser verificada pela suíte HTTP, ainda não executada nesta fase por bloqueio do harness persistente.

## Regra experimental do avaliador

O acesso à fila, ao detalhe de submissão, ao claim e à correção exige:

1. permissão estática `submissions.grade` no papel resolvido pelo servidor;
2. registro `learning_review_scopes` em estado `active`, ligado ao mesmo usuário e à trilha, com a operação requerida (`submissions.read` ou `submissions.grade`).

Ausência de escopo nega a operação. Recurso fora de escopo não é distinguível de recurso inexistente no detalhe. A fixture de integração provisiona o escopo sintético; não há endpoint para conceder grants, e nenhum escopo é inferido do nome `admin` ou `editor`.

## Limites

Esta é uma ACL experimental fail-closed para a jornada isolada, não um grant IAM de produção. A coleção é acessada somente pelos serviços de aprendizagem alterados; seu schema, provisionamento, revogação, auditoria e corrida com a correção ainda carecem de decisão e validação operacional. O uso em qualquer ambiente persistente real permanece proibido sem aprovação IAM específica.

O proprietário da submissão pode ler apenas os próprios dados e atividades ainda visíveis. Rubrica e contexto de correção não são retornados ao aluno. Uma autorização nominal sem escopo não permite ler a fila nem corrigir. O frontend não é fronteira de segurança.

## CSRF e entrada

As rotas de escrita validam origem para cookies autenticados. Entrada de resposta e correção usa modelos estritos (`extra=forbid`) e limites de tamanho. `Idempotency-Key` identifica a intenção de envio. Tokens não são enviados em URLs.

## Testes

Testes unitários cobrem as projeções públicas/reservadas, ausência de campos internos e validação estrita. O cenário HTTP previsto cobre outro aluno, avaliador sem escopo e avaliador com escopo. Esse cenário ainda não foi executado por falha de provisionamento do MongoDB descartável; logo, autorização HTTP efetiva segue não verificada.
