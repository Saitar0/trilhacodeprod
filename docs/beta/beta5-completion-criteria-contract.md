# Beta 5 — critérios de conclusão

`beta_completion_criteria.py` modela cada regra com texto original, unidade, tipo, modo de avaliação, atividade opcional, evidência exigida, dependências, exigência de revisão humana e proveniência. Tipos distinguem leitura, resposta/aprovação de quiz, envio/correção de exercício, projeto avaliado, domínio e conclusão. O limiar automatizado é explicitamente `None`.

Texto curricular ambíguo permanece `UNSTRUCTURED` / `DECISION_REQUIRED` e requer decisão humana. Enviar exercício não implica aprovação; resposta de quiz não implica domínio; completar leitura não implica conclusão automática. A Beta 5 preserva o texto, não define percentuais e não altera serviço operacional de progresso.

O conversor Beta 4 entrega critérios textuais sem semântica automática. O staging os conserva como registros próprios e inclui o artefato/ hash de origem no manifesto sem expor corpos privados. Falta decisão pedagógica por critério e adaptação do contrato de progresso antes de representar conclusão de aluno.
