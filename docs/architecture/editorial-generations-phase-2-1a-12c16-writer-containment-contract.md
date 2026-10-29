# C16 — Contrato experimental de contenção entre escritores editoriais

## Resultado e limite da prova

A prova persistente C16 validou que participantes **cooperativos** de famílias distintas podem compartilhar a autoridade de revisão C8/C10: cada comando preparado usa a revisão da trilha, e a transação confirma CAS, mutações do participante, auditoria, histórico e recibo em conjunto. Em nove corridas com dois clientes independentes, um comando confirmou e o outro recebeu conflito; não houve efeitos parciais do perdedor.

A prova também demonstrou o limite decisivo: uma identidade MongoDB com `readWrite` sobre o banco pode alterar `content_blocks` diretamente, sem atualizar revisão, fence, auditoria, histórico ou recibo. A aprovação do caso cooperativo **não** contém esse bypass.

Os participantes C16 são modelos sintéticos de formato de efeito. Nenhum dos writers operacionais foi chamado ou alterado. Os 17 itens C13 continuam com `runtime=NOT_VERIFIED` na matriz versionada. Esta evidência não valida produção, IAM implantado ou a totalidade do inventário dinâmico.

## Autoridade comum

O harness reutiliza `AsyncEditorialRevisionAdapter` de C10, que implementa a forma transacional do protocolo C8. Não introduz revisão por coleção, por bloco ou por família.

Para cada família cooperativa:

1. Resolver a trilha no lado confiável; os exemplos C16 recebem um `track_id` sintético fixo.
2. Preparar a intenção no adaptador C10, incluindo identidade estável de operação, revisão esperada e fence corrente.
3. No commit, abrir a transação C10 e verificar novamente credencial, preparação, revisão e fence.
4. Executar o participante específico dentro da mesma sessão MongoDB.
5. Gravar evento funcional sintético de auditoria; o participante não pode omiti-lo.
6. Gravar histórico e recibo C8/C10 e confirmar a transação.
7. Em conflito, falha de participante ou falha de auditoria, abortar a unidade toda. Replay consulta o recibo persistido e não invoca outra mutação.

Publicação, importação, restauração e exclusão mantêm participantes próprios; não são reduzidas a um patch de bloco. A validação da trilha, autorização IAM e resolução de referências dos writers reais permanecem fora do modelo C16.

## Modelos e fidelidade

| Família C16 | Referência C13 | Mutação sintética na transação | Fidelidade declarada |
|---|---|---|---|
| Edição de bloco | W-07 | Atualiza bloco sintético | Apenas formato do efeito; não chama `update_block` |
| Publicação | W-04 | Lê blocos, cria snapshot/version, registro de publicação e ativa estado sintético | Efeito multicoleta simplificado; não usa serviço real nem contrato de gerações |
| Importação | W-10 | Insere nó, bloco e relação | Lote mínimo; não reproduz job, lease, parser ou retomada |
| Restauração | W-11 | Remove e reinsere bloco sintético | Substituição mínima; não reproduz batches, restore job ou resume |
| Exclusão | W-02/W-06 | Remove conteúdo/relações e, intencionalmente, progresso/tentativas sintéticos | Contraexemplo de política: atomicidade não torna essa exclusão correta |
| Duplicação | W-03/W-06 | Cria trilha, nó e bloco sintéticos | Formato mínimo; não chama `duplicate_track`/`duplicate_node` |
| Reordenação | W-01/W-05/W-07 | Atualiza ordenação de nó sintético | Formato mínimo; não reproduz regras de ordenação real |
| Seed | W-13 | Upsert de bloco sintético estável | Demonstra participante cooperativo futuro, não executa `run_seed` |

W-08, W-09, W-14, W-15, W-16 e W-17 não têm participante persistente C16: foram mantidos no inventário e suas dependências precisam de tratamento específico. W-14 não é automaticamente uma mutação editorial; precisa classificar efeito por migração antes do cutover. W-15 segue sem lifecycle/call graph comprovados; W-17 permanece em namespace de PoC.

## Resultados persistentes

| Cenário | Resultado observado | Evidência/limite |
|---|---|---|
| Edição × edição | Um commit, um conflito, revisão final 1, uma auditoria, um histórico e um efeito | MongoDB C16; clientes e sessões independentes; participante sintético |
| Edição × publicação | Um commit e um conflito; sem publicação parcial do perdedor | MongoDB C16; publicação sintética |
| Edição × importação | Um commit e um conflito; sem nó importado parcial do perdedor | MongoDB C16; importação sintética |
| Edição × restauração | Um commit e um conflito | MongoDB C16; restauração sintética |
| Publicação × restauração | Um commit e um conflito | MongoDB C16; estados compostos sintéticos |
| Importação × publicação | Um commit e um conflito | MongoDB C16; sem job/lease real |
| Exclusão × edição | Um commit e um conflito | MongoDB C16; política de retenção de aluno não aprovada por atomicidade |
| Duplicação × reordenação | Um commit e um conflito sob a revisão da trilha de origem | MongoDB C16; sem duplicação/reordenação real |
| Seed × edição | Um commit e um conflito | MongoDB C16; upsert de seed sintético |
| Falha depois da primeira mutação de importação/restauração/exclusão | Revisão e todas as coleções voltaram ao estado inicial | Erro injetado dentro da transação; não é falha de rede |
| Falha depois de criar snapshot e antes de ativar publicação | Nenhum snapshot/publicação ficou confirmado | Erro injetado; não demonstra consistência do snapshot real |
| Falha antes da auditoria | Bloco, revisão, histórico, efeito e recibo não confirmaram | Auditoria sintética obrigatória no mesmo participante |
| Retry após falha e replay após sucesso | A intenção preparada confirmou uma vez; replay não duplicou efeitos/auditoria | Mesmo recibo C8/C10 e contagens persistidas |
| Revisão de snapshot desatualizada | Rejeitada antes da preparação | Validação sintética de revisão fonte |
| Fence obsoleto | Commit rejeitado sem mutação | Fence C8/C10 avançado na mesma autoridade |
| Exclusão de estado de aluno sintético | Conteúdo, progresso e tentativa foram apagados juntos | Demonstra atomicidade; também demonstra que a transação não decide a política pedagógica |

Os testes usam barreira assíncrona, sem `sleep` para sincronizar as corridas. Os casos de falha de participante são injeções determinísticas, não falhas naturais do servidor.

## Contrato requerido para uma operação composta futura

Cada família que afete estado versionado de uma trilha deve fornecer ao contrato C8/C10 um participante transacional que:

* use o mesmo `track_id` e a mesma revisão monotônica;
* inclua a escrita da família e toda a auditoria funcional obrigatória na mesma sessão;
* crie snapshots vinculados à revisão fonte e só ative publicação depois que seu conteúdo estiver completo;
* torne lotes importados/restaurados totalmente atômicos ou explicitamente recuperáveis, com fence que rejeite workers antigos;
* use identidade idempotente estável e reconcilie recibo antes de repetir;
* não apague progresso/tentativas sem contrato próprio de preservação, exclusão ou retenção;
* aplique autorização IAM/grant por trilha separadamente de CAS e fence.

Uma operação global como taxonomia pode afetar várias trilhas; precisa de autoridade/escopo global e protocolo apropriado, não de autoridade improvisada por bloco.

## Caso B — writer não cooperativo e contenção

Com o usuário sintético `readWrite` usado pelo participante C10, um segundo cliente atualizou `content_blocks` diretamente antes do commit C10 e novamente depois dele. A escrita posterior foi persistida enquanto revisão, histórico C8/C10 e auditoria continuaram nos valores anteriores. Logo, a revisão do protocolo não serializa comandos que não escrevem a autoridade compartilhada.

Um papel MongoDB sintético restrito à coleção `content_blocks` também conseguiu alterar um bloco diretamente e não conseguiu atualizar a coleção sintética de revisão C8. Isso protege o estado de autoridade contra esse usuário, mas **não** impede a mutação sem CAS do conteúdo. Um usuário somente leitura não pode fazer a mutação. A prova de grants é por coleção, não por documento, e não foi aplicada a usuários ou coleções operacionais.

Consequências:

* Uma checagem na aplicação ou uma convenção de chamada é apenas cooperação, não contenção global.
* A prevenção exige que identidades antigas não tenham capacidade de escrita efetiva nas coleções protegidas, ou que as chamadas antigas sejam bloqueadas/desativadas; a estratégia exata depende de topologia, processos e privilégios reais, não verificados aqui.
* Segregar identidade de serviço e restringir privilégios de banco é uma defesa adicional, mas não substitui auditoria e política. Se um único usuário `readWrite` for compartilhado por novos e antigos writers, o bypass persiste.
* Um change stream, reconciliação ou observabilidade pode detectar algumas divergências, mas não evita confirmação irregular.

## Ambiente e privacidade

MongoDB 7.0.43, replica set de nó único `rsC16`, WiredTiger, sessões habilitadas, um banco aleatório por teste com marcador C16, usuário de aplicação sintético `readWrite` apenas naquele banco e coleções sintéticas. O contêiner não publicou porta; o runner Python 3.11 ligou-se à rede Docker bridge interna dedicada. `/data/db` e `/data/configdb` eram tmpfs, sem volume. Nenhum serviço fora da rede foi consultado.

Não foram usados dados reais. O valor editorial C16 é sintético e foi escrito somente em coleções descartáveis. O recibo/histórico C8 recebe a intenção metadata-only criada pelo harness; o conteúdo sintético pertence apenas ao documento de teste que representa o bloco/snapshot. Isso não altera o adaptador C8 genérico, que aceita payload mais amplo.

## Limitações

1. Modelos sintéticos não provam que os writers reais possam ser colocados na mesma transação, nem que seu call graph, efeitos externos ou contratos HTTP sejam compatíveis.
2. A prova usa um replica set de nó único; não valida failover multinó, topologia implantada, latency ou transações em serviços separados.
3. As credenciais `readWrite` e custom role foram criadas apenas no banco C16; privilégios reais, usuários compartilhados e grants da aplicação são desconhecidos.
4. IAM C11/C12 não foi repetido nesta prova de concorrência. A corrida de revisão não prova autorização por trilha.
5. Não foi executada falha natural de rede, commit ambíguo de driver ou lease expirado do importador/restore.
6. A política para exclusão de progresso e tentativas, publicação de gerações, retenção e readers segue pendente.
7. O inventário C13 é versionado e possui 17 entradas verificáveis no código; não é prova de exaustividade dinâmica de jobs, shells operacionais ou runtime.

**Conclusão:** a contenção cooperativa C8/C10 foi demonstrada no escopo sintético. O bypass direto também foi demonstrado. Escritores não cooperativos ainda impedem qualquer afirmação de contenção global e mantêm bloqueada a integração operacional.
