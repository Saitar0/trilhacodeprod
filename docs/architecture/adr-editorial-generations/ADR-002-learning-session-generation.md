# ADR-002 — Geração fixada para sessão de estudo e progresso

**Status:** Proposed
**Tipo:** recomendação de produto/backend; não implementada e não aprovada.
**Baseline analisado:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636.

## 1. Contexto

Tentativas de quiz registram published_version_id e activity_revision; progresso genérico é chaveado por user/node/block e não por geração. O frontend consulta árvore, detalhe e progresso por chaves sem geração. Evidência: audit B.2 seções 3 e 4; e5bf…; backend/services/activities.py:130-190, backend/services/progress.py:152-379, frontend/src/hooks/useData.ts:19-40; alta. A existência de versão por tentativa é confirmada no código; uma semântica única de sessão não foi identificada.

## 2. Problema

Após publicação/restauração, o estudante pode continuar vendo conteúdo de uma identidade e iniciar/submeter atividade avaliada contra outra. Uma requisição pinada não basta para navegação em múltiplas requisições.

## 3. Requisitos

- Fixar geração sem confiar cegamente em um ID escolhido pelo cliente.
- Preservar a versão de atividade original em tentativas e avaliações.
- Compatibilizar progresso legado e conteúdo removido sem apagar histórico.
- Definir revogação urgente, expiração e retomada de sessão.

## 4. Alternativas

| Opção | Benefício | Limite |
|---|---|---|
| A. Sempre seguir geração mais nova | Simples, aluno vê conteúdo atual | Pode trocar conteúdo no meio de sessão/tentativa |
| B. Pin só por requisição | Leitura internamente consistente | Navegação tree/node/quiz pode trocar geração entre chamadas |
| C. Pin por sessão de estudo | Consistência entre navegação; UX previsível | Requer sessão persistida, expiração, revogação e retenção |
| D. Pin somente por tentativa | Preserva avaliação de quiz | Não resolve conteúdo geral, navegação ou cache |
| E. Híbrida: sessão + tentativa | Sessão mantém leitura; tentativa registra a identidade exata do avaliador | Requer política para reabrir, trocar e encerrar sessões |

## 5. Critérios de avaliação

Coerência pedagógica, autenticidade de identidade, compatibilidade com progresso existente, privacidade, custo de retenção, resposta a retirada urgente e suporte a múltiplos clientes.

## 6. Recommended Decision

Recomenda-se E, condicionado à aprovação do produto: uma sessão é criada/resolvida pelo servidor e fixa uma geração para a trilha; cada tentativa fixa também o identificador imutável da atividade/definição usada para avaliação. O servidor vincula session_id a usuário, trilha, geração, estado e validade; o cliente recebe token opaco/autenticado ou referência não autoritativa. Submissão é avaliada contra a definição privada fixada, nunca contra o head corrente.

## 7. Justificativa

O caminho de quiz versionado existente é um precedente limitado: a tentativa já persiste versão, enquanto o restante do nó/trilha pode mudar. O cache atual não inclui generation ID. A sessão híbrida fecha a lacuna sem afirmar que o progresso atual já preserva esse vínculo.

## 8. Consequências positivas

Navegação, quiz e avaliação podem permanecer coerentes durante republicação; histórico pode ser explicado e reavaliado de forma reproduzível.

## 9. Consequências negativas

Mais estado persistido, gestão de validade, referências que afetam retenção e UX explícita para geração retirada.

## 10. Riscos

Pin excessivamente longo mantém conteúdo retirado acessível; pin curto demais interrompe estudo. Token manipulável pode permitir acesso a conteúdo fora da coorte. Compatibilidade de progresso antigo é incerta.

## 11. Impacto na migração

Introduzir sessão após reader por geração estar estável. Tentativas novas passam a guardar generation_id e activity_definition_id/version; progresso legado deve ser associado apenas quando comprovável, sem inferir geração. Retomar progresso sem referência pode iniciar sessão corrente com aviso ou permanecer legado, decisão de produto.

## 12. Compatibilidade

Preservar endpoints e IDs atuais inicialmente; acrescentar campo/token aditivo somente após API review. Não tratar client-supplied generation_id como autorização. Mudanças incompatíveis em quiz/submission exigem versão de contrato.

## 13. Estratégia de rollback

Parar abertura de sessões novas e tentativas novas se houver falha; manter resolução de tentativas existentes pela versão gravada. Após cutover, não recalcular respostas contra conteúdo vivo. Conteúdo retirado urgentemente requer revogação de sessões/gerações e mensagem indisponível, não troca silenciosa.

## 14. Testes obrigatórios

- Abrir sessão em A, publicar B, navegar árvore/nó/quiz e confirmar A.
- Submeter tentativa de A depois de B e avaliar com definição privada de A.
- Token de outra pessoa/trilha ou token alterado é negado.
- Retomar sessão e idempotência de tentativa.
- Sessão revogada e geração indisponível falham de modo explícito.
- Progresso legado órfão e links diretos têm comportamento aprovado.

## 15. Critérios de aceitação

Uma geração resolvida por sessão; tentativas invariavelmente ligadas à definição avaliada; cliente não escolhe geração arbitrária; histórico fica explicável; comportamento de expiração/revogação aprovado; sem regressão de contrato de quiz.

## 16. Decisões dependentes

ADR-004 (retenção), ADR-005 (identidades), ADR-006 (head), contrato frontend/progresso e política de retirada urgente.

## 17. Perguntas para aprovação humana

1. Quando a sessão fixa a geração e por quanto tempo é retomável?
2. Republicação mantém sessões existentes ou oferece troca explícita?
3. Em retirada de segurança, sessão antiga é revogada imediatamente?
4. Como vincular progresso sem geração histórica comprovável?
5. Links diretos para nós removidos retornam 404, tombstone ou aviso de versão?
6. Notas/notas de atividade podem ser recalculadas? Recomendação: preservar resultado histórico e evaluator identity.

## 18. Cenários pedagógicos propostos, pendentes

| Cenário | Resultado recomendado | Decisão de produto necessária |
|---|---|---|
| Aluno inicia A; professor publica B | Sessão continua A; nova sessão obtém B | Duração e UX de “versão nova disponível” |
| Resposta de quiz A enviada após B | Avaliar contra definição privada A | Janela para tentativa aberta e submissão tardia |
| Restore de versão anterior | Criar geração nova derivada da fonte antiga; sessões existentes mantêm o pin salvo revogação | Significado pedagógico do restore |
| Retirada urgente de A | Revogar A e interromper com estado seguro/indisponível; não mudar conteúdo silenciosamente | Autoridade e SLA para revogação |
| Retorno após várias publicações | Retomar geração fixada se retida; caso contrário, migração/aviso explícito | Janela de retenção e tratamento do progresso |

## 19. Approved Decision

Nenhuma. Sessão, validade, revogação e progress mapping aguardam aprovação humana.

## 20. Evidência e confiança

Confirmado no código: attempt version em backend/services/activities.py:130-190; progresso por IDs em backend/services/progress.py:152-379; cache sem geração em frontend/src/hooks/useData.ts:19-40 e staleTime em frontend/src/index.tsx:41. Base e5bf…; confiança alta. Homologação da PoC não valida a integração desses endpoints.
