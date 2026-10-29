# Fase 2.1A.12C.13 — Ondas futuras de integração editorial

**Planejamento apenas:** nenhuma onda está autorizada ou executada nesta fase. As etapas abaixo pressupõem uma nova autorização por incremento e o fechamento dos bloqueios especificados. Não são cronograma nem aprovação de cutover.

## Princípios de ordenação

1. Primeiro decidir a fonte de autoridade e a semântica de revogação; não há valor em integrar writers a um contrato IAM sem dono, grants, administração e auditoria decididos.
2. Comprovar o baseline e os esquemas/roles/topologia do runtime autorizado pelo processo ADR-008 antes de planejar migração real. Os testes sintéticos C8–C12 não fornecem esse baseline.
3. Cobrir caminhos que disputam as mesmas coleções de conteúdo. Não é seguro colocar `update_block` sob CAS enquanto import, restore, clone, delete ou seed ainda puderem gravar o mesmo escopo sem coordenação.
4. Tratar revisão editorial, geração imutável e head público como authorities separadas. Escritores de snapshot/publicação e leitores vêm depois de consistência dos fontes.
5. Não permitir fallback a writer legado depois que revisão/fence novos forem confirmados. Pausar escrita ou corrigir com nova revisão é mais seguro que reabrir um bypass.

## Bloqueios gerais de entrada

Nenhuma alteração operacional pode começar até haver decisão humana registrada para:

* autoridade de grants por trilha e de catálogo global; poderes de conceder, delegar, revogar e recuperar acesso;
* política explícita de escopo global, sem `admin` implícito; revisão/versionamento de permissões globais;
* ordenação das mudanças de usuário/papel, sessão, grants e escopo administrativo com commit; fonte que possa participar dessa fronteira;
* ownership editorial, limites de delegação, expiração/retention e auditoria de governança;
* semântica de delete e preservação de tentativas/progresso; ACL/retention de edit_history, recibos, histórico e dados privados;
* revisão esperada e chave idempotente/contrato HTTP, conflitos e replays;
* identidade do runtime, drivers, Mongo topology/concerns, database roles, indexes e implantação por procedimento ADR-008;
* classificação completa dos writers que compartilham cada coleção e plano de bloqueio de bypass;
* rollback ensaiado que não apague auditoria/revisões e não reabra writers antigos.

## Ondas propostas

| Onda | Escopo, writers e dependências | Critérios de entrada | Testes/saída verificável | Bloqueios e rollback |
|---|---|---|---|---|
| **0 — Decisões e governança** | Sem código operacional. Delibera a proposta C13: fonte de autoridade, roles, operação, escopo administrativo, delegação, auditoria e revogação. Depende do responsável do projeto/autoridade IAM e de decisões de privacidade. | Inventários C4/C13 aceitos como versão do repositório; donos de decisões nomeados. | Registro de decisões inclui grantor, revogador, recuperação, approver, epochs, audit, API, retention e política de admin global; critérios de revogação sem ambiguidade. | Bloquear se “quem concede” ou o scope global estiver indefinido. Rollback não aplicável; manter nenhuma alteração operacional. |
| **1 — Baseline e compatibilidade operacional** | Verifica runtime autorizado, origem da imagem/digest, rota, readiness, linha de código, versão Python/PyMongo, topologia, URI, permissões Mongo e schemas. Não repetir descoberta por Coolify/GHCR fora do processo autorizado ADR-008. | O fluxo administrativo ADR-008 autorizado fornece evidências verificáveis e acesso de leitura estritamente aprovado; nenhum dado de aluno copiado. | Relatório de compatibilidade operacional, validação dos índices/transactions/roles, matriz de bancos/coleções e plano de acesso de teste. Não muda dados. | Sem baseline ou sem permissão necessária: bloqueia todas as ondas de writer. Recuperação: não iniciar implantação. |
| **2 — Modelo e ciclo de vida de grants** | Especifica schema, unicidade, epochs, estado, auditoria de grant, política global e vínculo com os atuais `users`, `auth_sessions` e matriz de permissões. Decide se grant está na autoridade transacional editorial ou sob coordenador com garantia equivalente. | Onda 0 fechada; Onda 1 confirma que a fonte escolhida pode ser mantida e consultada com os controles definidos. | Testes de concessão, subset de delegação, autoconcessão negada, mudança/revogação e recuperação; auditoria e índices em ambiente descartável representativo; fail closed em falha de consulta. | Bloquear duplicidade de fontes grant, falha de auditoria obrigatória, falta de ordenação com revogação ou grantador sem separação de deveres. Rollback: não conceder grants reais; retenção/epoch só adiante. |
| **3 — Fronteira autenticada e contrato HTTP** | Traduz JWT/sessão/papel atuais e grant confiável em capability server-side. Define `If-Match`/revisão esperada, `Idempotency-Key`, erros HTTP, replay externo, `null`, ACL e recibo mínimo. Ainda sem ativar writer novo. | Onda 2 aprovada; API decision record define compatibilidade de clientes e operação de leitura. | Testes de token/sessão/papel/grant (incluindo revogação concorrente), recurso resolvido no servidor, chave conflitante, `412/409` conforme decisão, payload nulo/ausente, sem exposição do bloco em replay não autorizado. | Bloquear qualquer capability originada do request, track_id não validado, erro interno exposto ou cliente antigo capaz de overwrite silencioso. Rollback: endpoint experimental não publicado; não habilitar cliente. |
| **4 — Inventário de writers por coleção e contenção do piloto** | Cobre todas as entradas que podem tocar os mesmos tracks/nodes/blocks/relations, incluindo CRUD, duplicações, import, restore, seed, CLI, workers e publication. É pré-condição do piloto, não integração gradual writer-a-writer com bypass aberto. | C3/C13 inventory reconciliado com runtime e operadores; operação de piloto e collections do escopo selecionadas; forma de suspender todos bypasses disponíveis. | Testes de busca/registro de imports e entrypoints, testes de corrida contra cada escritor do escopo e prova de que writers não migrados são bloqueados ou não podem apontar para o escopo. | Se um importador, restore, script, usuário Mongo ou serviço desconhecido pode gravar mesmo collection, não há piloto seguro. Rollback: read-only/pausa de edição, nunca writer legado sem fence. |
| **5 — Escrita de conteúdo controlada por trilha** | Integra uma família pequena, começando por update de bloco apenas se W-07 **e todos os demais escritores capazes de alterar o mesmo bloco** (delete, reorder, import, restore, duplicate, seed) forem coordenados ou bloqueados. Mantém protocolo C8/C10 como autoridade única; compartilha audit, CAS, fence, recibo e conteúdo no commit requerido. | Ondas 0–4 concluídas para o escopo e risco de `content_blocks`/`edit_history` decidido; compatibilidade schema/API aprovada. | MongoDB/topologia alvo de teste aprovada: sucesso, CAS, fence, grant/session revogados, audit fail, idempotência/replay, null/patch, concorrência multiprocesso, import/restore bloqueados e rollback testado. | Qualquer writer compartilhado sem controle, inconsistência audit/bloco ou dúvida de resultado ambíguo bloqueia ampliar. Rollback: suspender escritas e reconciliar receipts; correção é nova revisão, não replay via versão antiga. |
| **6 — Estrutura e relações** | Migrar track/node/relation create/update/reorder, duplicação com escopos origem/destino, depois exclusões somente com política de aluno. Depende da Onda 5 e das regras hierárquicas/ciclos. | Família de bloco estável; estratégia de revisão da estrutura e implicação sobre bloqueios/leitores definida. | CAS em reorder e árvore, ciclo/ref checks no mesmo commit, duplicação idempotente, persistência de tentativas em delete, auditoria e referências sem órfãos. | Exclusão bloqueada se progresso/tentativas ou relações não tiverem política. Rollback: pausar family, preservar histórico e corrigir por nova revisão. |
| **7 — Catálogo e importação** | Separa taxonomias/tags/block_types como autoridade global/catálogo versionado; migra import depois de bloquear escrita sequencial fora do protocolo. Depende de ondas 2, 5 e 6 e da semântica de catalog impact sobre gerações. | Modelo de catálogo e escopo aprovado; importação inclui job id, origem/destino, operação e todos os escritores que podem concorrer. | Cenários de falha por batch, crash/resume, duplicate key, idempotência, isolamento entre tracks e aplicação atômica/recoverable de catálogo. | `delete_tag` transversal e import parcial são blockers até schema/geração impact definidos. Rollback: marcar import não concluído, restaurar por intent versionado; nunca usar lock lease como único fence. |
| **8 — Snapshot, restore e publicação** | Cobre W-04, W-11, W-12, candidatos W-15 e todas as referências `activity_publications`. Segue ADR-005/006: gerar snapshot coerente, armazenar immutable generation e trocar head por CAS próprio; restore cria nova revisão/generation e não reescreve histórico confirmado. | Writers de fonte cobertos; formato de generation, reader pinning, ACL de snapshots e política emergencial de retirada definidos; ADR-008 liberado. | Simulação de corte/leitor fixado, falhas pré/pós-head, geração incompleta inacessível, tentativa antiga mantida, rollback via head aprovado sem apagar geração/audit. | Não publicar quando algum leitor ainda usa coleções mutáveis ou pode observar mistura. Rollback de head não autoriza apagar auditoria/revisões nem reverter revogação. |
| **9 — Expansão, auditoria de cobertura e cutover** | Aumenta o escopo somente após provar todos os writers/consumidores daquele scope; inclui serviço automatizado/CLI controlados e observabilidade passiva apenas como sinal auxiliar. | Onda 8 aprovada para primeiros tracks; observabilidade, alertas, plano de suporte/recuperação e SLOs decididos. | Testes de carga moderados, caos seguro no ambiente autorizado, reconciliação de commits, confirmação de writers bloqueados, ensaio de rollback e auditoria independente. | Qualquer bypass desconhecido, drift do runtime, shadow writer, grants não ordenáveis ou sinais sem auditoria bloqueia expansão. Rollback: maintenance/read-only e forward fix; nunca reabrir writer que não verifica revision/fence. |

## Compatibilidade e rollback transversal

API atual aceita clientes sem revisão esperada ou chave idempotente. Tornar esses campos obrigatórios é mudança de contrato: precisa de plano de cliente, período de compatibilidade delimitado e regra fail-closed ao final. Se uma chamada antiga puder gravar sem CAS depois de existir revisão editorial, não há coexistência segura para aquele escopo.

Rollback deve separar quatro objetos: código/rota; grants/epochs; conteúdo e revisão já confirmados; geração/head publicado. Uma implantação pode ser revertida por pausa de escrita e restauração controlada de código enquanto mantém grants revogados, recibos e histórico. Conteúdo confirmado não deve ser apagado para imitar estado anterior; correção é nova revisão sob autoridade corrente. Head público, se houver, só pode retornar para geração previamente validada por protocolo explícito e sem expor tentativas de aluno. Feature flag sozinha não ordena commits e não impede client antigo.

Antes de qualquer onda, validar: (a) comunicação do modo de manutenção, (b) bloqueio de clients/CLI/workers/legacy process, (c) reconcile por operação, (d) procedimento para commit indeterminado, (e) cópia/restauração autorizada sem usar dados reais em testes, (f) decisão de seguir adiante ou manter escrita pausada. Não chamar rollback de uma transação já confirmada de exclusão/revogação.

## Critérios verificáveis de bloqueio para primeira integração

Manter bloqueado quando houver qualquer item:

* Fonte de grants, responsável de concessão, política admin global ou gestão de delegação pendente.
* Usuário/papel/sessão/grant que influencia autorização não pode ser ordenado com a confirmação conforme a garantia desejada.
* Escritor versionado, CLI ou integração runtime capaz de mutar as mesmas entidades sem CAS/fence/audit; inventário externo não resolvido.
* Auditoria ou recibo sem ACL/retention/minimização aprovada.
* Publicação, quiz, restore, import ou leitor capaz de observar estado parcial ou generation misturada.
* Compatibilidade de API e clientes antigos não definida; replay e null sem semântica.
* topology/runtime, roles e índices reais sem baseline ADR-008.
* Testes de concorrência/falha/rollback relevantes ausentes ou executados somente em fake.
* Plano de rollback exige reabrir uma escrita antiga que ignora revisão/fencing.

## Próximo incremento técnico recomendado

Uma deliberação documentada, pelo responsável e autoridade IAM designada, sobre **fonte primária de grants por trilha, quem pode conceder/revogar e qual estado global (papel/permissão/sessão) precisa ser ordenado com commit**. É o menor passo que fecha decisões bloqueantes de arquitetura; não toca runtime nem repete inventário genérico. Depois dela, uma fase autorizada poderá especificar o schema de grant e testar compatibilidade com o baseline ADR-008.
