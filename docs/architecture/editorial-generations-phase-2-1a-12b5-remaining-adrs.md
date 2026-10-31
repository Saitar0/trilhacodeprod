# Fase 2.1A.12B.5 — revisão dos ADRs restantes

**Escopo:** ADR-002, ADR-003, ADR-004, ADR-007 e ADR-008.
**Natureza:** análise e propostas para decisão humana.
**Estados dos ADRs originais:** todos continuam `Proposed`; os estados desta revisão são apenas triagem da decisão, não aprovação.

Referências principais: [auditoria da arquitetura B.2](./editorial-generations-phase-2-1a-12b2-audit.md), [contratos B.3](./editorial-generations-phase-2-1a-12b3-contracts.md), [invariantes B.3](./editorial-generations-phase-2-1a-12b3-invariants.md), [matriz de decisão B.3](./editorial-generations-phase-2-1a-12b3-decisions.md), [evidências de baseline B.4B](./editorial-generations-phase-2-1a-12b4b-runtime-evidence.md) e [gates do ADR-008 B.4B](./editorial-generations-phase-2-1a-12b4b-adr008-gates.md). A base técnica examinada é `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`; as conclusões de deployment são as registradas em `ccc5ade1fc92f4532a820d0ade41c50555d19ffa`, sem nova consulta à infraestrutura nesta fase.

## ADR-002 — sessões de aprendizagem vinculadas à geração

**Status original:** Proposed.
**Triagem para aprovação:** REQUIRES_CLARIFICATION.
**Decisão recomendada:** o servidor fixa uma geração validada ao abrir uma sessão de estudo; cada tentativa fixa também a identidade/versionamento da atividade e é avaliada contra a definição privada dessa mesma geração.

### Evidência e problema

A auditoria B.2 encontrou tentativas de quiz que podem registrar `published_version_id`, mas não identificou identidade de geração propagada uniformemente por navegação, leituras, submissões, progresso e outros fluxos. Os contratos públicos e o comportamento de continuação precisam ser compatíveis com clientes existentes. A evidência está limitada ao snapshot técnico B.2 e não demonstra qual contrato está implantado. Ver [inventário de leitores e progresso B.2](./editorial-generations-phase-2-1a-12b2-audit.md) e [contratos de sessão B.3](./editorial-generations-phase-2-1a-12b3-contracts.md).

### Proposta conceitual

1. `open_session` autentica o aluno, autoriza a trilha e resolve no servidor o head/geração selecionável. O cliente não escolhe uma geração arbitrária; um identificador recebido do cliente é apenas uma referência opaca de sessão e deve ser validado contra usuário, escopo e estado.
2. A sessão guarda `track_id`, `generation_id`, identidade do usuário, estado e metadados mínimos de retomada. A validade/expiração é política de produto e privacidade ainda pendente; não se propõe TTL.
3. Cada tentativa registra `generation_id`, `activity_id`, identidade da definição privada e versão do esquema de avaliação. A submissão é idempotente por chave de tentativa/submissão. A avaliação usa a definição fixada, nunca o head atual.
4. O progresso mantém referências suficientes para interpretar tentativas e concluir retomada, sem copiar gabaritos ou armazenar dados pessoais no snapshot pedagógico.
5. Sessão expirada ou geração indisponível não migra silenciosamente para o head novo. A resposta deve ser explícita e segura; a política de retomada, extensão ou bloqueio precisa ser aprovada.
6. Uma retirada urgente pode revogar acesso futuro à geração, mas não deve alterar retroativamente uma nota já calculada. O comportamento para sessão ativa/tentativa incompleta é decisão de produto e segurança.

### Contratos conceituais

| Operação proposta | Pós-condição essencial | Falha/retry |
|---|---|---|
| Abrir sessão | Geração validada pelo servidor e vinculada ao usuário/trilha | Repetição com idempotency key retorna a mesma sessão ou resultado documentado |
| Ler conteúdo fixado | Todas as chamadas da sessão consultam a mesma geração | Geração ausente/corrompida falha fechado; sem fallback ao legado |
| Iniciar tentativa | Tentativa fixa geração, atividade e versão privada | Retry não cria tentativa duplicada |
| Enviar resposta/avaliar | Uma definição privada imutável determina o resultado | Head atual não altera a avaliação; resposta duplicada é idempotente |
| Retomar progresso | Servidor valida vínculo e disponibilidade das referências | Referência órfã vai para estado explícito de recuperação, não para conteúdo atual |
| Encerrar sessão | Fecha o estado de navegação sem apagar histórico de tentativa | Retry não destrói resultado persistido |

Esses nomes não são endpoints atuais. Não há proposta de alterar payload público nesta fase.

### Alternativas e trade-offs

| Alternativa | Benefício | Custo/risco |
|---|---|---|
| Sempre seguir a geração mais nova | Simples para catálogo | Pode misturar conteúdo e atividade numa sessão já iniciada |
| Pin por requisição | Implementação mais curta | Não estabiliza navegação nem submissões entre chamadas |
| Pin por sessão e tentativa (recomendação) | Coerência pedagógica e avaliação reproduzível | Exige sessão no servidor, retenção e compatibilidade de cliente |
| Pin somente por tentativa | Protege a nota, mas não toda a experiência de leitura | Aluno pode ver material B e responder uma tentativa A |

### Perguntas humanas e critérios de aceitação

Produto deve decidir duração/renovação de sessão, conclusão de atividades antigas após republicação, links para gerações antigas, comportamento para geração retirada urgentemente e experiência de erro. Segurança/privacidade deve definir escopo e expiração de identificadores. Aceitação futura exige testes de A→B durante sessão, submissão tardia contra A, restauração como nova geração C, retomada após muitas publicações, revogação, autorização cruzada entre usuários e cliente tentando selecionar geração não autorizada.

**Dependências:** ADR-006 para geração fixada e ausência de fallback; ADR-004 para retenção; ADR-005 para acesso ao conteúdo público e definição privada; ADR-003 para identidade/versionamento semântico de atividade. Não há GC seguro até haver inventário aprovado das referências criadas por esses contratos.

## ADR-003 — taxonomias e metadados versionados

**Status original:** Proposed.
**Triagem para aprovação:** REQUIRES_CLARIFICATION.
**Decisão recomendada:** congelar na geração toda referência que altere significado, ordenação ou apresentação pública; versionar identidade/esquema quando a semântica puder mudar; permitir consulta dinâmica apenas para dados explicitamente não semânticos.

### Evidência, limites e classificação proposta

O snapshot B.2 identifica coleções/serviços relacionados a tags, taxonomias e tipos de bloco; não comprova que todos os campos conceituais abaixo existam no mesmo schema, nem sua semântica de produto. Dificuldade, competências e objetivos pedagógicos devem ser confirmados no inventário vigente antes de implementação. A matriz abaixo é uma classificação de trabalho, não descrição completa do schema.

| Dado/área observada ou candidata | Classe proposta | Motivo/limite |
|---|---|---|
| Identidade de trilha, módulo, nó, atividade | Congelado na geração | Referências e progresso precisam resolver o mesmo objeto lógico |
| Título, descrição, slug e ordem públicos | Congelado na geração | Alteram apresentação, navegação ou seleção do aluno |
| Hierarquia de módulos/nós e relações | Congelada na geração | Uma mudança intermediária pode criar árvore mista |
| Tipo de bloco/exercício e versão do schema | Referência versionada ou congelada | Renderer/evaluator histórico precisa interpretar o formato original |
| Conteúdo de bloco, alternativas e configuração pedagógica | Congelado; privado/público conforme classificação do ADR-005 | Mudança afeta o material apresentado e/ou avaliação |
| Tags e categorias de navegação | Congeladas ou referenciadas por versão | Alteram busca, filtros ou agrupamento; produto/frontend deve confirmar |
| Taxonomias com significado pedagógico | Referência versionada/congelada | Renomeação ou reclassificação não pode reinterpretar histórico |
| Rótulos puramente visuais, sem efeito de ordenação/semântica | Dinâmica somente após comprovação | Atualização dinâmica pode ser permitida se não mudar conteúdo, acesso ou interpretação |
| Campos administrativos, autoria e estado de workflow | Fora da projeção pública; snapshot apenas se necessário para auditoria | Não assumir exposição ou imutabilidade por conveniência |
| Dificuldade, competência, objetivo curricular | Pendente de validação de existência e semântica | Não inferir de nomes ou de uso parcial no frontend |

### Identidades que não devem ser confundidas

* **Identidade estável:** ID que relaciona progresso, conteúdo e referências.
* **Rótulo de apresentação:** texto traduzível/alterável; mudança de rótulo não deve trocar identidade.
* **Versão de schema:** formato necessário para desserializar/renderizar dados.
* **Versão semântica:** significado e regras de avaliação/navegação; pode exigir conteúdo e renderer históricos.
* **Migração:** transformação explicitamente validada entre versões; não é reescrita silenciosa do passado.

### Alternativas e trade-offs

| Alternativa | Benefício | Custo/risco |
|---|---|---|
| Copiar todas as taxonomias em cada geração | Imutabilidade simples de explicar | Duplicação, tamanho e manutenção |
| Referências globais dinâmicas | Menor armazenamento | Muda conteúdo publicado sem nova seleção |
| Catálogo global com versões imutáveis (recomendação) | Reuso sem perda de semântica | Precisa lifecycle/versionamento e compatibilidade de renderer |
| Separar metadados administrativos e pedagógicos | Limita snapshot ao que importa | Exige classificação campo a campo e revisão de produto |

**Questões humanas:** quais categorias/tags influenciam descoberta; quais tipos de bloco são contratos públicos; se rótulos e ordenação podem mudar sem republicação; como apresentar versões antigas no frontend. **Critérios de aceitação:** inventário de campo/coleção com dono; classes congelada/versionada/dinâmica/admin; teste que altera cada dependência durante construção e prova que o resultado ou rejeita a mudança ou fixa uma versão; teste de renderer/evaluator histórico.

**Dependências:** ADR-001 deve incluir revisão/identidade das dependências globais usadas na candidata, pois um contador por trilha não detecta mudança em taxonomia global; ADR-005 classifica visibilidade; ADR-006 consome refs imutáveis; ADR-002 usa identidade semântica da atividade; ADR-004 retém versões ainda referenciadas.

## ADR-004 — retenção e exclusão

**Status original:** Proposed.
**Triagem para aprovação:** BLOCKED_BY_EVIDENCE.
**Decisão recomendada:** retenção baseada em referências ativas e obrigações aprovadas, começando por nenhuma coleta de lixo até inventariar referências e política de privacidade/negócio. Nenhum prazo é proposto como aprovado.

### Referências que precisam integrar o inventário

Head ativo; sessão e retomada; tentativas e resultados; submissões, notas, revisões e progresso; recibos/idempotência e replay; histórico/restore; auditoria; investigação de segurança; hold legal/privacidade; jobs ainda em execução e candidatos não selecionados. A existência e formato de cada referência devem ser confirmados no baseline escolhido antes de codificar GC.

### Política conceitual segura

1. Uma geração ativa, referenciada por qualquer sessão/tentativa/histórico protegido ou sujeita a hold não é elegível à remoção.
2. O conteúdo pedagógico imutável deve ser separado, quando possível, de identificadores pessoais e respostas de aluno; apagar/anonymizar a identidade não deve inutilizar definições necessárias para uma avaliação histórica legítima, salvo decisão de privacidade em contrário.
3. Exclusão solicitada passa por classificação: dado pessoal, conteúdo educacional, avaliação, obrigação de auditoria ou artefato órfão. Uma tombstone e bloqueio de seleção podem preceder remoção física, sem representar cumprimento legal automático.
4. Só depois de catálogo completo de referências, janela de expiração aprovada, corrida de GC com novas referências protegida por fencing/CAS, e plano de recuperação, poderá ser especificada remoção física.
5. Recibos de publicação expiram conforme regra explícita; resposta perdida não autoriza republicação quando o receipt já expirou. A operação deve parar/reconciliar de forma segura.

### Alternativas e trade-offs

Retenção ilimitada protege histórico, mas tem custo e conflito de privacidade. Prazo fixo é operacionalmente simples, mas não deve ser inventado sem base legal/produto. Retenção por referência evita remoção em uso, mas depende de grafo completo. Política por curso oferece controle, porém aumenta complexidade. A recomendação híbrida precisa de avaliação jurídica/privacidade e dono operacional antes de GC.

**Evidência bloqueante:** a auditoria B.2 não demonstra grafo completo entre progresso, sessões, tentativas, avaliações, receipts e gerações; as decisões de política e prazos não foram aprovadas. **Perguntas humanas:** quais dados podem ser removidos, autoridade para aprovar, requisitos de anonimização, preservação histórica, janela de receipts e restauração após exclusão acidental. **Critérios de aceitação:** matriz completa de referência→dono→prazo aprovado; simulação de referência concorrente com GC; auditoria de exclusão; restauração testada; revisão jurídica/privacidade documentada.

**Dependências:** ADR-002 fornece referências de sessão/tentativa; ADR-005 separa PII e conteúdo privado; ADR-006 define gerações/restauração/receipts; ADR-007 deve manter GC desativado durante migração.

## ADR-007 — migração gradual e coexistência

**Status original:** Proposed.
**Triagem para aprovação:** PENDING_APPROVAL para a sequência e os princípios; nenhuma etapa está autorizada a executar.
**Decisão recomendada:** migrar por escopo delimitado, com flags independentes inicialmente desabilitadas, sem dual-write público implícito, sem selecionar ponteiro durante backfill e sem fallback a coleções mutáveis após cutover.

### Sequência proposta e gates

| Etapa | Resultado | Gate antes de avançar |
|---|---|---|
| 0. Baseline e decisões | Baseline/runtime e ADRs essenciais determinados | ADR-008 evidência operacional suficiente; decisões de produto/segurança aprovadas |
| 1. Instrumentação passiva | Métricas dos escritores/leitores legados por escopo | Nenhum payload sensível; cobertura observável e owner definido |
| 2. Revisão/fencing | Todos os comandos no escopo compartilham autoridade de revisão | Matriz de escritores fechada; conflitos e retry testados |
| 3. Armazenamento privado e roles | Coleções/identidades para conteúdo e definição privada | ADR-005 aprovado; grants mínimos verificados em ambiente descartável |
| 4. Backfill isolado | Gerações candidatas validadas, sem ativação | Idempotência, integridade, retomada, contagem e comparação aprovadas |
| 5. Shadow comparison | Comparação sem efeito em resposta pública | Divergência explicada e abaixo do gate aprovado; nenhuma escrita duplicada pública |
| 6. Leitores administrativos e compatibilidade | Preview/editor usam contratos versionados em escopo controlado | Autorização, projeções, rollback e testes de API aprovados |
| 7. Leitura de aluno em coorte delimitada | Sessão fixa geração, sem caminho legado misto | ADR-002 aprovado; cache/progresso/avaliação compatíveis |
| 8. Seleção/publicação atômica | Head muda por CAS e leitor usa somente geração | ADRs 001/003/005/006 aprovados; zero writer bypass no escopo |
| 9. Restore e operações | Restauração cria geração nova sob mesma validação | Restore, replay e retenção testados |
| 10. Desativação do legado | Nenhum caminho de leitura/escrita contorna o protocolo | Evidência de tráfego/código, observabilidade e aprovação de cutover |

O backfill nunca seleciona o ponteiro. Uma construção sombra pode gravar exclusivamente em namespace privado, com identidade de operação e fencing; não deve atualizar documentos legados ou produzir efeito público. “Dual write” entre stores mutáveis não é presumido seguro: se for inevitável, requer outbox/recuperação e semântica de leitura explícitas, decisão adicional e testes de falha. Recomendação é evitar essa fase e manter escopos não migrados no legado até que a troca seja completa e segura.

### Rollback e flags

Flags separadas: construir candidato, comparar sombra, leitura versionada, seleção de head, restauração e coorte. Todas começam off. Alterar uma flag exige owner, pré-condições, métrica e autorização registrada. Após seleção pública, rollback de código/flag não deve reabrir leitor legado; manter reader de gerações e última geração válida, ou interromper publicação e retornar indisponibilidade controlada. Restore de conteúdo é nova geração, não edição do passado.

**Critérios de aceitação:** cada etapa tem escopo, observabilidade, owner, teste e reversão; nenhuma ativação depende somente de porcentagem de tempo; zero writer bypass antes do cutover; backfill não muda head; diferenças são explicadas; parada preserva conteúdo válido.

**Dependências:** ADR-001, ADR-005 e ADR-008 antes de alterar runtime; ADR-002/003/004 antes de ativar leitor/GC; ADR-006 antes de seleção. O roadmap da auditoria anterior usa identificadores de fase que se sobrepõem à numeração usada neste ciclo; consultar a [matriz de dependências](./editorial-generations-phase-2-1a-12b5-dependency-matrix.md) em vez de inferir correspondência por número. Essa colisão de governança não altera código nem autoriza trabalho.

## ADR-008 — baseline e compatibilidade

**Status original:** Proposed.
**Triagem para aprovação:** BLOCKED_BY_EVIDENCE.
**Decisão recomendada:** manter desenvolvimento de integração bloqueado até identificar baseline técnico escolhido e reconciliar compatibilidade; manter a identidade implantada explicitamente não comprovada conforme B.4B. As evidências não foram atualizadas por consulta operacional nesta fase.

### Evidências preservadas e lacunas

* Snapshot de auditoria: `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`; é referência técnica, não runtime comprovado.
* Referências Git anteriormente observadas: `main` `22dca64556338a8fa9aaa89ce627a4f4af72317d`; `staging` `fff85218fd71b164dc7465ca72d22b4a53232f49`.
* Staging possuía deployments históricos associados ao SHA de staging, sem digest de runtime, container ativo, rota efetiva ou tráfego comprovados.
* Recurso chamado `trilhacode` no projeto `general` não foi comprovado como produção; último deployment relatado falhou. Healthchecks reportados desabilitados.
* Build G2/Actions run `39179762892` relaciona build ao commit `41dc470c567bae50b7ebcf0662d45d43863980c9`, mas não vincula imagem executada nem ambiente ativo.
* B.4B produziu matriz, pedido sanitizado ao administrador e relatório de baseline parcial em commit `ccc5ade1fc92f4532a820d0ade41c50555d19ffa`.

Não se deve repetir Coolify/GHCR nesta fase ou converter histórico em evidência atual. Falta evidência operacional autorizada que associe produção/staging → serviço ativo → digest OCI ativo → build/proveniência → commit, além de identificar a linha que será realmente validada e liberada.

### Alternativas de baseline

| Opção | Vantagem | Risco/condição |
|---|---|---|
| `main` | Pode refletir linha de release, se comprovado | Referência Git não prova deploy nem contratos efetivos |
| `staging` | Tem histórico de deployment | Digest/artefato ativo e roteamento não comprovados |
| Snapshot `e5bf...` | Auditoria profunda disponível | Diverge de commits exclusivos de staging e não é runtime |
| Branch de integração reconciliada (recomendação condicional) | Permite revisar compatibilidade sem escolher por recência | Só após inventário de diffs, baseline escolhido, compatibilidade e aprovação humana |

**Critério de aceitação:** confirmar commits e artefatos efetivos onde necessário, decidir linha de desenvolvimento e release com responsável, fazer matriz de schemas/import/progresso/quiz/frontend/jobs, definir testes comparativos e obter aprovação explícita. A decisão sobre branch não precisa afirmar qual revisão está em produção se essa informação for impossível, mas deve registrar o risco e seu tratamento antes de qualquer mudança de runtime.

**Dependências:** gate paralelo obrigatório para qualquer fase de runtime. O ADR-008 não impede revisão conceitual dos outros ADRs, mas bloqueia seleção de destino, integração, migração, rollout e release até evidências/risco e aprovação serem tratados. Não marca implementação como liberada.

## Síntese de prontidão

| ADR | Estado desta revisão | Motivo principal |
|---|---|---|
| 002 | REQUIRES_CLARIFICATION | Semântica de sessão, atividade antiga, retirada urgente e progresso são decisões de produto |
| 003 | REQUIRES_CLARIFICATION | Classificação campo a campo e dependências globais não concluídas |
| 004 | BLOCKED_BY_EVIDENCE | Grafo de referências e política de privacidade/legal incompletos; GC vedado |
| 007 | PENDING_APPROVAL | Princípios e sequência revisáveis; não autorizam execução |
| 008 | BLOCKED_BY_EVIDENCE | Runtime/digest/proveniência/produção não comprovados |

As fichas executivas de decisão estão no [pacote de aprovação](./editorial-generations-phase-2-1a-12b5-approval-packet.md). Nenhum dos estados acima altera o `Proposed` original.
