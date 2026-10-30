# Beta 8.1 — Evidências ainda necessárias para ADR-008

ADR-008 continua **BLOCKED**. A Beta 8.1 não acessou infraestrutura operacional e não modifica os gates históricos.

| Evidência | Estado local | Necessário em etapa operacional autorizada |
|---|---|---|
| Identidade efetiva de cada runtime/job/writer | `UNKNOWN` | Inventário observado de processos, contas e credenciais em uso |
| Grants operacionais e proprietário da decisão | `NOT_VERIFIED` | Fonte IAM oficial, delegação, escopo, expiração e revogação comprovados |
| Privilégios Mongo efetivos | `NOT_VERIFIED` | Leitura autorizada de roles/usuários existentes, sem alterar contas |
| Contenção dos 17 writers | `PARTIAL` | Classificar call graph e impedir credenciais antigas de contornar a autoridade |
| Isolamento de autoridade | `PROPOSED` | Processo/credencial de authority separado; não compartilhar segredo com escritores comuns |
| Revogação durante operação | `EXPERIMENTALLY_VERIFIED` | Confirmar mesma semântica/epoch e topologia de transação no IAM operacional |
| Replica set/transações | `EXPERIMENTALLY_VERIFIED` em MongoDB local | Verificar topologia, write concern, failover e timeouts operacionais |
| Backup e recuperação | `NOT_VERIFIED` | Procedimentos, RPO/RTO, restore ensaiado e retenção de auditoria |
| Observabilidade e resposta a incidente | `NOT_VERIFIED` | Logs, alertas, trilha de auditoria, rotação/revogação e runbooks aprovados |
| Leitores e gerações imutáveis | `NOT_VERIFIED` | Compatibilidade de runtime, pinning de geração e rollback |
| Rubrica do projeto 3.5 | `PROPOSED` | Decisão pedagógica humana explícita; não autorizar aprovação real antes dela |
| Publicação curricular | `BLOCKED` | ADR-008, autorização editorial e pedagógica, contenção global e rollout/rollback aprovado |

Os estados experimentais não autorizam promoção de gates. Para avançar, primeiro deve existir uma etapa de descoberta/planejamento operacional somente leitura com responsável, escopo e autorização explícitos; depois, uma implantação controlada de menor privilégio e verificação do cutover sem publicar currículo.
