# Beta 5 — contrato de conteúdo público, restrito e interno

## Modelo experimental

`backend/curriculum_contract/beta_protected_content.py` separa dados por campo em `STUDENT_PUBLIC`, `INSTRUCTOR_RESTRICTED` e `SYSTEM_INTERNAL`. Os modelos são estritos (`extra=forbid`) e imutáveis. Questão e exercício possuem dados públicos e dados reservados em objetos diferentes; projeções públicas são listas explícitas de campos e não serializam os objetos reservados.

Gabarito, resposta de referência, rubrica e explicação ficam fora da projeção de aluno. A divulgação de explicação após resposta/correção continua `PENDING_DECISION`; nenhum cronograma de liberação foi inventado. O acesso restrito sintético exige evidência de grant associada à mesma trilha e à operação `curriculum.read_restricted`. Nome de papel ou `admin` não é evidência de autorização. Esse contrato não se conecta ao IAM ativo e não representa uma ACL operacional.

`beta_staging_contract.py` aplica allowlists por tipo, rejeita chaves privadas recursivas (incluindo variações de caixa/camel case), valida o shape de alternativas e proíbe metadata genérica na projeção pública. O pacote guarda a versão completa somente em registros internos do namespace Beta 5. `inspect_batch` devolve apenas resumo técnico; não há rota, leitor operacional ou promoção.

## Projeto 3.5

Os 11 artefatos estão inventariados em `beta5-project-3-5-artifacts.json` apenas por identidade, tipo, ordem, IDs de origem e hashes. O contrato completo, incluindo conteúdo, etapas e rubrica, é mantido como registro exclusivamente interno do staging. Todos os 11 artefatos têm visibilidade pendente e a projeção de aluno fica vazia, inclusive brief e marcos. Checklists e rubricas também permanecem restritos no contrato de origem. Isso evita transformar uma classificação candidata em aprovação de publicação.

## Risco não resolvido

Os DTOs e as projeções experimentais demonstram separação estrutural. O backend atual ainda não foi comprovado como ACL para respostas/rubricas de instrutor, nem houve teste de resposta HTTP real nesta fase. Nenhum conteúdo de projeto foi publicado ou servido a alunos.
