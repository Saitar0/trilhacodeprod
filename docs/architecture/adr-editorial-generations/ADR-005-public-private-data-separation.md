# ADR-005 — Separação de dados públicos e privados de avaliação

**Status:** Proposed
**Tipo:** decisão de segurança recomendada; não aprovada nem implementada.
**Baseline analisado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.

## 1. Contexto

O schema genérico de blocos permite campos extras (backend/schemas/content.py:116-145); o serializer genérico remove apenas alguns campos (backend/serialization.py:8-41). O caminho de quiz versionado mantém definição privada em activity_publications e tem public_activity com projeção específica (backend/services/activity_publications.py:155-169). A aplicação usa um cliente AsyncMongoClient compartilhado (backend/database.py:1-8); grants atuais do ambiente não foram consultados. Evidência no audit B.2, leitores e risco EG-03/EG-18; confiança alta quanto ao código e desconhecida quanto às grants instaladas.

## 2. Problema

Uma denylist não protege contra campos privados novos nem contra endpoint alternativo. Projeção em aplicação não impede que uma credencial pública leia diretamente documento de gabarito da mesma coleção.

## 3. Requisitos

- Resposta pública construída por allowlist explícita e versionada.
- Gabaritos, rubricas, respostas corretas e critérios privados inacessíveis ao reader público.
- Campos desconhecidos/tipos sem renderer conhecido falham fechados.
- Identidades MongoDB e armazenamento separados conforme capacidade real de grants.
- A avaliação acessa somente versão privada vinculada à tentativa.

## 4. Alternativas

| Opção | Prós | Contras |
|---|---|---|
| A. Filtrar no controller | Mudança pequena | Projeção inconsistente entre rotas; falta defesa contra leitura direta |
| B. DTO público allowlist | Contrato verificável; campos novos não vazam | Não limita acesso de credencial ao banco |
| C. Documentos/coleções público e privado separados | Isola gabaritos em nível de coleção | Duplicação ou sincronização; requer migração e controle de versão |
| D. Identidades MongoDB distintas | Menor privilégio no banco | Permissões Mongo são por coleção; separação de campos exige separar coleção/partição |
| E. Defesa em profundidade: C + D + B | Limita leitura direta e saída API | Maior complexidade de índices, builder, avaliação e operação |

## 5. Critérios de avaliação

Vazamento por API, comprometimento de credencial, campos extras, facilidade de auditoria, compatibilidade de DTO, custo de armazenamento e avaliações históricas.

## 6. Recommended Decision

Recomenda-se E. Manter conteúdo learner-safe em armazenamento separado da definição privada de avaliação; identidade pública não tem find na coleção/partição de definição; evaluator usa credencial de serviço mínima para obter definição da tentativa; API mapeia para DTO allowlist por schema/type. Campos desconhecidos, bloco desconhecido e falha de projeção devem retornar erro fechado, nunca serialização genérica. Permissões precisam ser comprovadas com usuários Mongo de teste antes de qualquer rollout.

## 7. Justificativa

MongoDB autoriza operações em nível de banco/coleção, não uma allowlist arbitrária de campos por documento; portanto, role por coleção só resolve o problema se os dados privados estiverem separados. A PoC demonstrou projeção por caminho experimental; não prova roles da aplicação real.

## 8. Consequências positivas

Reduz vazamento acidental por novos campos; reader público não pode consultar definição privada; cada rota pode ser auditada contra contrato.

## 9. Consequências negativas

Builder precisa produzir representações coerentes públicas/privadas; evaluator precisa resolver versão antiga; migração de atividade e compatibilidade são necessárias.

## 10. Riscos

Endpoint alternativo ou cache pode ignorar DTO; armazenamento duplicado pode divergir; credencial compartilhada atual limita isolamento. Alta severidade para gabarito exposto.

## 11. Impacto na migração

Inventariar endpoints públicos/admin/preview/export; separar armazenamento antes de habilitar reader novo; adicionar canários secretos e testes de role. Não alterar schemas nesta fase.

## 12. Compatibilidade

Preservar campos e IDs públicos existentes mediante mapper explícito. Alteração de payload deve ser aditiva ou versionada. DTO público não pode refletir automaticamente novos campos de bloco.

## 13. Estratégia de rollback

Desabilitar novas avaliações/publicações se a definição privada estiver indisponível. Servir somente projeção da última geração verificada ou indisponibilidade explícita; nunca relaxar a role nem enviar documento privado ao cliente.

## 14. Testes obrigatórios

Roles reais demonstram reader sem find em coleção privada; API projection fuzz com campos desconhecidos; gabarito canário ausente em catálogo/tree/node/search/preview/cache; evaluator de tentativa antiga usa definição pinada; campos extras negados; logs sem resposta correta.

## 15. Critérios de aceitação

Inventário de endpoints completo; identidade e grants revisados por segurança; todos os DTOs têm allowlist; testes de não exposição passam em MongoDB real descartável; nenhuma rota/worker bypass.

## 16. Decisões dependentes

ADR-002 (definição histórica), ADR-003 (schema/tipo), ADR-004 (retenção), ADR-006 (geração selada), ADR-008 (baseline).

## 17. Perguntas para aprovação humana

Qual serviço pode avaliar? Acesso privado por collection ou DB separado? Quais campos legacy são publicáveis? O preview administrativo pode usar DTO diferente? Qual protocolo para tipo desconhecido?

## 18. Approved Decision

Nenhuma. A separação e os privilégios propostos aguardam aprovação de segurança e backend.

## 19. Evidência e confiança

Confirmado: backend/schemas/content.py:116-145 tem extra allow; backend/services/activity_publications.py:155-169 define public projection; backend/database.py:1-8 tem cliente compartilhado. e5bf…; alta. Grants implantadas são não identificadas. Ausência de leak na rota de quiz testada não é garantia para todas as rotas.

## 20. Gate de segurança

Não ativar leitura por geração até prova de isolamento por coleção/identidade e varredura de todos os leitores/DTOs, inclusive cache e preview.
