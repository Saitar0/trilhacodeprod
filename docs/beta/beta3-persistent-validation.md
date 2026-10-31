# Beta 3 — validação persistente isolada

## Ambiente e limites

- MongoDB `7.0.43`, WiredTiger, standalone. Replica set não era necessário para observar o importador C16, que não usa transação global; esta prova não valida transações editoriais.
- Imagem digest `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`.
- Container `trilhacode-beta3-curriculum-mongo`, ID `056be0eae2bfb334b169ce6fd211eb206adda0c2f359b0da9072b1dd68ce064f`, identificado por label da Beta 3.
- Rede bridge exclusiva `trilhacode-beta3-curriculum-net`, ID `47d221ad445a8df12ecdc2d9c69c376a9b8793b2e51d3b576bb8137f5a4de8c3`, sem masquerade de saída.
- Única porta publicada: `127.0.0.1:27150`; diretórios Mongo em tmpfs; nenhum volume/bind mount, sem credenciais reais ou banco previamente selecionado.
- Bancos com nome aleatório `beta3_curriculum_fidelity_<token>` e marcador de propriedade. Harness confirma IDs/labels/configuração antes de conectar ou limpar.

O primeiro container usou uma rede Docker marcada `internal`; a publicação da porta não encaminhou conexão do host. O driver recusou `hello` antes de qualquer gravação. Após confirmar os IDs e a propriedade, removi somente o container/rede Beta 3 e recriei bridge sem NAT de saída, mantendo a porta em loopback. Os testes persistentes subsequentes passaram.

## Evidência

Seis testes chamaram `services.imports.run_import` real, depois dos metadados sintéticos mínimos de tipos de bloco/taxonomias. A prova também chamou `services.nodes.get_track_tree` e `get_node` reais para o ator staff sintético. O resultado persistido foi uma trilha privada/draft, um nó draft e 19 blocos draft na ordem 0–18. A leitura de estudante do serviço foi negada com 404. Nenhuma rota, publicação, frontend ou jornada de aluno foi chamada.

| Cenário persistente | Resultado observado |
|---|---|
| Dry-run, importação e repetição | Schema aceito; 8 teoria, 1 resumo, 5 quizzes, 3 exercícios, 2 referências; repetição manteve uma trilha, nó, 19 blocos e um histórico |
| Falha após quatro blocos de teoria | Estado parcial e job interrompido; mesma operação retomou sem duplicar |
| Falha após 14 blocos, já com os 5 quizzes | Quizzes permanecem; retry completou os exercícios/referências sem duplicá-los |
| Falha após 17 blocos, com três exercícios | Retry completou referências e auditoria sem duplicar |
| Falha de auditoria antes de persistir | Conteúdo já persistido, nenhum `edit_history`; retry criou uma única auditoria |
| Auditoria persistida e confirmação simuladamente perdida | Um evento persistiu antes da exceção; retry retomou e manteve a contagem em um |

As falhas foram injetadas em helpers com patch; não são falhas de rede naturais. O importador deixa estado parcial enquanto retoma. Isto demonstra a retomada por identidade estável na versão C16 e nos interleavings testados, não atomicidade, segurança contra concorrência de credenciais diretas nem equivalência operacional.

O bloco privado de quiz pode ser lido pelo staff sintético no draft. Helpers reais de projeção foram testados offline e excluem gabarito/feedback; o leitor de estudante não consegue abrir a trilha draft/privada. Não houve teste de projeção via endpoint publicado, porque a unidade não foi publicada.

## Limpeza

Cada teste removeu apenas seu banco aleatório após confirmar o marcador `phase` e `run_id`. A rede e o container exclusivos devem ser removidos após todas as verificações Beta 3, mediante nova inspeção de IDs, labels, ausência de mounts e ausência de bancos de teste. Nenhum container ou volume anterior foi reutilizado.
