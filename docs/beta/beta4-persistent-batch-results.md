# Beta 4 — resultados persistentes

## Ambiente descartável

- MongoDB `7.0.43`, WiredTiger, modo standalone (o writer de importação não depende de transações MongoDB).
- Cliente PyMongo Async (`AsyncMongoClient`).
- Container `trilhacode-beta4-first-phase-mongo`, rede exclusiva `trilhacode-beta4-first-phase-net`, dados em tmpfs, imagem digest fixado pelo harness.
- Porta local `127.0.0.1:29164`; sem volume e sem credenciais reais.
- Cada teste cria banco aleatório com prefixo `beta4_first_phase_` e marcador de propriedade. Na inspeção final foram encontrados dois bancos com esse prefixo e marcadores Beta 4 válidos; ambos foram removidos explicitamente após nova conferência, antes do container. Portanto, a limpeza por fixture não é considerada comprovada por si só.
- Esta prova usa somente o banco descartável descrito acima. A ressalva separada da execução do teste histórico de índices na porta 27017 está registrada em [análise da divergência](beta4-index-divergence-analysis.md).

## Resultado

Dois testes persistentes passaram usando `services.imports.run_import`, `services.nodes.get_track_tree` e `get_node` reais, ligados somente ao banco de teste:

1. Dry-run completo sem gravar trilha, nó ou bloco; importação privada/draft; 44 nós, 161 blocos, 21 relações e uma entrada de histórico editorial. Entre os blocos: 44 quizzes e 26 exercícios. O leitor real devolveu árvore e detalhe ordenados; estudante sintético recebeu 404. A projeção real `_student_block` removeu gabarito/feedback. Replay sequencial preservou contagens e uma única entrada de histórico.
2. Falha injetada na 61.ª preparação de bloco deixou 60 blocos parciais, estado da trilha/job `interrupted`; a repetição do mesmo payload retomou a importação até 44 nós/161 blocos/21 relações, sem duplicação e com uma entrada de histórico.

As unidades foram persistidas como árvore hierárquica na mesma trilha de teste. `get_track_tree` contou 44 nós/161 blocos; `get_node` leu a unidade 1.1 e seus cinco tópicos com oito blocos teóricos e cinco quizzes. O teste de visibilidade permaneceu em draft/private e não publicou conteúdo.

## O que esta prova não valida

Não houve replica set porque a sequência real exercitada não exige transação. A recuperação é retomada pelo job e payload idênticos, não rollback atômico: o estado parcial existiu e foi observável. Não foram executadas falha natural, perda de resposta após confirmação, concorrência entre imports, falha de auditoria, rota HTTP, frontend, publicação ou leitura autenticada de aluno em conteúdo publicado. A prova não contorna o risco C16 de credenciais de banco com escrita direta. A verificação final conferiu o marcador dos dois bancos restantes, removeu somente esses bancos próprios e confirmou a ausência do container/rede Beta 4.
