# Matriz de progresso compartilhado — Etapa 14H.1

## Fatos observados

- [TESTADO] O bundle tem 406 identidades de bloco canônico, 1.001 colocações, 284 assuntos consumidores e 1.001 valores progress_scope: undecided.
- [IMPLEMENTADO] O contrato intermediário distingue block_ref de SharedPlacement.ref e mantém subject_ref, ordem, proveniência e escopo.
- [IMPLEMENTADO] O progresso operacional de conteúdo existente é indexado pelo usuário e pelos IDs internos de nó/bloco (user_id, node_id, block_id), não por placement_ref.
- [IMPLEMENTADO] O serviço operacional de tentativas de quiz usa escopo de usuário, quiz_id e version_id. A identidade do quiz compartilhado não é atualmente contextualizada pela colocação.
- [NÃO IMPLEMENTADO] Não existe reconciliação de progresso legado para IDs curriculares canônicos/colocações neste adaptador.
- Nenhuma leitura ao MongoDB foi realizada nesta etapa.

## Alternativas — comparação técnica

| Dimensão | A. Global por bloco canônico | B. Independente por colocação | C. Híbrido por escopo explícito |
| --- | --- | --- | --- |
| Identidade de progresso proposta | (user, block_ref) | (user, placement_ref) | (user, block_ref) ou (user, placement_ref) conforme um escopo explícito e aprovado |
| Índice/ unicidade propostos | Único por usuário e bloco | Único por usuário e colocação | Chave depende do escopo; precisa prevenir colisões entre os dois formatos |
| Histórico existente (user,node,block) | Exigiria escolher uma identidade canônica e mesclar usos contextuais; risco de conclusão cruzada | Exigiria mapear cada registro ao tópico/colocação correspondente; ambiguidades continuam sem resolução automática | Exigiria classificar cada colocação e mapear cada registro; maior complexidade |
| Quizzes compartilhados e tentativas | Um quiz/versão canônica tende a compartilhar o limite e histórico em todos os usos se mantiver a chave atual (user,quiz,version) | Progresso por colocação não separa tentativas sozinho; a identidade/idempotência das tentativas precisaria incluir colocação ou uma política de quiz explicitamente compartilhado | Tentativas precisariam seguir regra explícita por escopo; com 1.001 escopos indefinidos, o sistema deve bloquear uso contextual |
| Mudança de conteúdo/versão | Atualização canônica afeta todos os contextos; histórico deve conservar hash/versão anterior | Conteúdo continua canônico único, mas cada histórico de colocação precisa registrar versão/hash | A política por escopo e versão precisa ser definida por colocação; nenhuma versão de conteúdo foi inferida nesta etapa |
| Remoção/realocação de colocação | Progresso do bloco permanece mesmo que aquele contexto desapareça | Histórico da colocação precisa permanecer arquivado, sem apagar eventos | Tratamento depende do escopo; mudança não pode mesclar nem apagar automaticamente |
| Reconciliação sem perda | Pode fundir estados de contextos distintos; precisa regra para conflitos de estado/data | Mantém separação contextual, mas dados antigos sem colocação inequívoca ficam pendentes | Pode preservar casos explícitos, mas requer decisão, migração e relatório item a item |
| Compatibilidade com sistemas atuais | Requer mapear block_ref curricular a IDs internos | Requer suporte a placement_ref além de node/block internos | Requer suporte a ambas as chaves e armazenamento do escopo da decisão |
| Efeito percebido pelo aluno | Concluir uma vez pode refletir em outros assuntos onde o mesmo conteúdo aparece | O aluno pode precisar concluir a mesma atividade em contextos diferentes | Experiência varia de acordo com configuração explícita de cada colocação |

As chaves e efeitos na tabela são comparações de arquitetura, não comportamento implementado.

## Decisões

- [PROPOSTA — não aprovada] Documentos anteriores recomendam a alternativa B (progresso por colocação) para evitar que conclusão em um contexto satisfaça outro.
- [PENDENTE] Aprovação humana é necessária para A, B ou C, incluindo efeitos sobre tentativas de quizzes e histórico.
- [PENDENTE] As 1.001 scopes permanecem undecided. Esta etapa não preenche, converte, normaliza ou usa esse campo para operar progresso.
- [PENDENTE] A compatibilidade com progresso legado depende de snapshot autorizado, inventário de IDs internos e regra de reconciliação aprovada.
- [PENDENTE] Atualizações de conteúdo, versões históricas e remoção de colocações precisam de política explícita antes de persistência operacional.

## Gate para implementação futura

Antes de qualquer backfill/persistência: aprovar a política; definir se tentativas de quiz são por quiz/versão ou colocação; mapear IDs curriculares a IDs internos; definir preservação de eventos, conflitos e versões; criar plano reversível; testar em banco descartável. Nenhum desses passos faz parte da 14H.1.
