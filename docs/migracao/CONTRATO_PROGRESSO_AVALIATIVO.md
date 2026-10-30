# Contrato de progresso e pré-requisitos avaliativos

## Estado

Implementado na etapa 13C.3, ainda não ativado operacionalmente. A feature flag do renderer de quizzes continua desativada por padrão. Nenhuma das 55 relações do contrato curricular foi convertida automaticamente.

## Semântica

| Tipo | Fonte autoritativa | Significado |
|---|---|---|
| `content_completed` | Registro de progresso genérico do próprio usuário, com `status=completed` | O aluno marcou o conteúdo como concluído segundo o fluxo de leitura existente. É uma declaração de progresso, não uma prova de aprendizagem. |
| `quiz_passed` | Resultado persistido pelo serviço de quizzes para o próprio usuário e a versão ativa publicada | O servidor registrou aprovação a partir de tentativa corrigida no servidor. Exige `passed=true` e melhor nota decimal igual ou superior a 70%. |
| ausente / `null` | Semântica anterior da relação | Mantém o comportamento legado de conclusão de conteúdo, incluindo o tratamento histórico de destino ausente. Não recebe interpretação avaliativa automática. |

O endpoint genérico de progresso não cria nem altera `quiz_progress`; campos de `data` enviados pelo cliente, inclusive `passed` e `score`, não satisfazem `quiz_passed`.

## Regras de avaliação

- Só relações `type=prerequisite` com `enforced=true` participam do bloqueio.
- Relações com tipo explícito são avaliadas separadamente e, em conjunto, operam como AND: todo pré-requisito obrigatório precisa estar satisfeito.
- `content_completed` consulta a conclusão de conteúdo já usada pela plataforma.
- `quiz_passed` exige um quiz no mesmo escopo curricular, uma versão ativa publicada e o resultado persistido daquele usuário para aquela versão.
- Notas são lidas como Decimal/Decimal128; não há arredondamento antes da comparação com 70%.
- Conteúdo, quiz ou versão não publicados, inexistentes ou não verificáveis resultam em estado `unavailable` e mantêm o bloqueio.
- Erros da consulta ao banco não liberam o conteúdo. A falha sobe à API; a interface protegida também falha fechada.
- Trocar a versão ativa invalida a aprovação da versão anterior para fins de desbloqueio, sem apagar seu histórico.
- Não há leitura de `passed`, nota ou data do endpoint genérico de progresso para conceder aprovação.

## Contratos de API afetados

As entradas de relação aceitam opcionalmente `prerequisite_kind: content_completed | quiz_passed`. O campo só é válido em relações `prerequisite`. Ausência ou `null` preserva o legado. Nenhuma conversão em lote foi executada.

A resposta de progresso da trilha inclui `prerequisite_states`, com `target_id`, `prerequisite_kind` (`legacy`, `content_completed`, `quiz_passed` ou `unavailable`) e `status` (`satisfied`, `pending` ou `unavailable`). Os bloqueios incluem `pending_requirements` para manter a explicação da causa.

## Experiência do aluno

A interface apresenta estados distintos de leitura concluída/pendente e quiz aprovado/ainda não aprovado, além de conteúdo bloqueado/liberado. Se a trilha exigir pré-requisitos e a avaliação do servidor estiver carregando, falhar ou não trouxer estados, estudantes não recebem o conteúdo protegido e recebem uma mensagem acessível com opção de tentar novamente. Equipe mantém o acesso de pré-visualização existente.

Após um resultado autoritativo de quiz, a interface invalida a consulta de progresso para refletir o estado atualizado. A interface não calcula nota ou aprovação e não escreve aprovação no endpoint genérico.

## Limites e pendências

- A conclusão de leitura continua autodeclarada como no sistema legado; não demonstra que o conteúdo foi aprendido.
- A semântica das relações antigas permanece pendente. A ausência de tipo não é convertida em `quiz_passed`.
- Com a feature flag de quizzes desligada, um pré-requisito avaliativo tipado continua bloqueando até a API/fluxo de quiz estar habilitado. Não associar novas relações tipadas em ambientes de aluno antes da ativação homologada do fluxo.
- Esta alteração não muda o importador, o contrato intermediário, o JSON curricular, as regras de desbloqueio globais ou o histórico de leitura.
- A política de ativação e a futura representação no importador exigem homologação posterior.

## Testes

A cobertura específica confirma leitura declarada, aprovação em 69,99%/70%, melhor nota persistida, usuário e versão corretos, versão publicada, rejeição de falsa aprovação via progresso, semântica legada e combinação AND de leitura + quiz. A interface tem testes de rótulos distintos, falha fechada, e um E2E com frontend e API reais em banco descartável.

