# Fase 2.1A.12C.15 — Transição da matriz estática de permissões

## Problema

No código versionado, `backend/constants.py` define `PERMISSIONS` como matriz Python imutável em execução para `admin`, `editor` e `student`; [`permissions.py`](../../backend/permissions.py#L9-L19) resolve a permissão a partir do papel. Mudança dessa matriz ocorre por versão de código, não por documento que uma transação MongoDB possa ler e condicionar. O fato de `security.current_user` carregar o papel atual por request não ordena um commit que já começou contra um release com política anterior.

Política P6 ratificada: release isolado não prova revogação ordenada. Uma solução persistida também não é suficiente se algum writer ignorar a versão. A decisão arquitetural aprovada é coordenar política e writers; a implementação concreta segue proposta.

## Alternativas

| Opção | Mecanismo | Vantagens | Limites e riscos | Evidência exigida |
|---|---|---|---|---|
| A — Epoch persistido | Cada política possui `policy_epoch`; escritor lê/condiciona essa versão na mesma fronteira do commit; alteração incrementa epoch. | Comparação explícita; pode invalidar capabilities preparadas e produzir conflito em writer antigo. | Só funciona se todos writers consultam a fonte e incluem a checagem na confirmação; não corrige uma instância velha que não implementa protocolo; requer schema, índice e autoridade da política. | Teste concorrente com clientes independentes, transição/rollback e todos writers de escopo; baseline e grants DB autorizados. |
| B — Drenagem coordenada | Pausar entrada; drenar operações e instâncias da versão anterior; publicar versão; só reabrir quando versão uniforme e writers antigos bloqueados. | Não precisa confiar numa leitura transacional de uma matriz compilada. | Exige controle operacional confiável sobre HTTP, jobs, CLI, imports e retries; operação longa/indisponibilidade; invisibilidade de ferramentas externas impede garantia atual. | Rehearsal de drain, inventário de processo/instância, comprovação de nenhum writer antigo ativo, rollback ensaiado. |
| C — Híbrida (recomendada para desenho) | Epoch persistido para autorização na confirmação + drenagem/compatibilidade coordenada de releases; recusa de versão desconhecida; capability vincula epoch. | Defesa em profundidade; epoch torna stale explícito e drain cobre caminhos sem consumidor do epoch durante rollout. | Complexidade e dependência dos dois mecanismos; não remove necessidade de cobertura integral nem cria garantia contra writer externo. | Testes A, prova operacional de drain, corrida de release, falha parcial, rollback de versão sem rebaixar epochs/autorizações revogadas. |

## Recomendação

Recomenda-se **C como arquitetura alvo**, sujeita à decisão da autoridade IAM e à evidência ADR-008. A sequência de rollout deve operar em modo fechado: bloquear writer sem versão suportada; emitir capability somente para epoch conhecido; toda transação deve condicionar ao epoch efetivo. Durante mudança de matriz, primeiro publicar compatibilidade de readers/writers, depois estabelecer barreira/drain, avançar epoch e reabrir somente quando o baseline suportado estiver verificado.

Um incremento de epoch não deve reviver um grant, papel ou sessão revogados. Rollback de software pode retornar código compatível, mas não diminuir epoch nem reabilitar estado revogado. Correção de configuração é nova transição auditada.

## Relação com role, sessão e usuário

O epoch da matriz Python cobre somente a interpretação de `role → permission`. Ele não substitui:

* revogação/versão do grant de trilha;
* estado de `users` (ativo, papel, token version conforme fluxo existente);
* registro de `auth_sessions`;
* escopo global administrativo;
* CAS/fence editorial.

Para garantia forte, cada versão persistente que puder mudar acesso precisa ou participar condicionalmente da fronteira transacional ou ter uma transição coordenada que demonstre que operações da versão anterior terminaram antes da política efetiva mudar. Consultar a mesma fonte antes e depois não torna a operação linearizável.

## Política de compatibilidade e falha

* Epoch desconhecido/ausente, política não carregável ou mismatch: negar/indeterminado; não inferir permissão.
* Writer antigo sem suporte: não pode receber tráfego de mutação após cutover. Bloqueio precisa cobrir route, worker, import, restore, CLI, seed, migração e credencial de banco quando pertinente.
* Múltiplas instâncias: todas devem informar/validar a versão suportada; uma instância antiga impede reabertura.
* Capabilities emitidas no epoch anterior: ficam inválidas; o cliente prepara nova operação depois de autorização vigente, mantendo a mesma identidade idempotente quando se trata de replay/reconciliação e sem recriar mutação já confirmada.
* Falha de rollout: pausar nova entrada, reconciliar operações em resultado incerto, manter revogações e histórico; não desfazer transações confirmadas para simular downgrade.

## Pendências e critério de fechamento

Owner/IAM deve decidir autoridade e semântica da mudança de política; operações deve provar controle/drain de todos executores; segurança deve aprovar fail-closed e tratamento de capabilities; arquitetura deve provar CAS/fence + epoch em teste persistente com versão compatível. Nenhum critério é operacionalmente satisfeito nesta C15. A matriz de [prontidão](editorial-generations-phase-2-1a-12c15-readiness-gates.md) mantém isso como bloqueio.
