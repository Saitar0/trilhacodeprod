# Beta 8.4 — reinício real da autoridade e reconciliação

## Prova de processo

O controlador PowerShell pausa o verifier persistente, revalida projeto/run/role labels, ID, rede interna, ausência de portas públicas e mounts inesperados, então envia SIGKILL somente ao contêiner próprio da autoridade. Ele observa o contêiner parado, reinicia o mesmo ID e exige PID diferente e endpoint de saúde restabelecido. O socket Docker não é montado nos serviços. API, autoridade e MongoDB usam contêineres próprios, identidades MongoDB distintas, credenciais sintéticas e rede interna exclusiva.

## Interrupções executadas

* `before_commit`: interrupção real na barreira anterior ao commit; retry após restart não depende de estado em memória.
* `after_commit`: interrupção depois da confirmação MongoDB e antes de a resposta RPC chegar; retry devolve/reconcilia o resultado persistido sem repetir a mutação.
* `staging_after_commit`: interrupção após transição sintética durável do staging; o bridge consulta o estado persistido e o retry idempotente não cria outra geração.

Após recuperar essa primeira geração, o teste realizou uma edição HTTP real de rascunho e promoveu um segundo lote sintético. O ponteiro experimental avançou exatamente uma unidade em sua própria sequência CAS, enquanto o contrato da nova geração registrou a revisão editorial atual como `parent_revision` e a revisão editorial seguinte como `revision`. A geração anterior permaneceu presente. Isso cobre o caso em que uma edição de conteúdo ocorre entre duas transições de geração e impede que os dois contadores de revisão sejam confundidos.

Na execução final, os três reinícios produziram PIDs novos. O harness verificou revisão, estado da operação, evento de auditoria, geração sintética vencedora e ausência de duplicações. A reconciliação usa MongoDB descartável; não usa a resposta HTTP como fonte da verdade. As falhas antes/depois do commit foram posicionadas por barreira controlada; não representam uma queda aleatória de rede ou uma falha natural de host.

## Limites

Não foram exercitadas todas as instruções possíveis de desligamento, partição de rede, eleição de replica set, corrupção ou failover de armazenamento. O restart conserva o MongoDB descartável e a identidade do contêiner; não testa backup/restore. Nenhuma geração curricular operacional foi criada.

## Veredito

**REINÍCIO REAL E RECUPERAÇÃO DA AUTORIDADE VALIDADOS NO ESCOPO EXPERIMENTAL** para os pontos de falha listados.
