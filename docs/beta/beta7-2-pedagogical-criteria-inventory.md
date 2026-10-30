# Beta 7.2 — inventário dos critérios pedagógicos

## Proveniência

Leitura somente leitura da fonte aprovada para experimento isolado: revisão `147dc68b81169f66b0ba3802fa2f26e5130923a3`, classificação editorial `rascunho`. O manifesto Beta 4 confirma os hashes abaixo. A fonte não foi alterada. Integridade para experimentação não é aprovação para publicação.

| Unidade | Artefato | SHA-256 | Estado do critério |
|---|---|---|---|
| 1.1 | `f1-1-1-02-criterio-de-conclusao` | `ca2d8f1ee3f7395be9b08ab00e4532d9ec9be85587600cc201b60dbbf21375b7` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 1.2 | `f1-1-2-02-criterio-de-conclusao` | `937e6f58fb27335218eb74b61aff62e143d5adb710979b7bcb6f282a694564a5` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 2.1 | `f1-2-1-02-criterio-de-conclusao` | `a9fcd20e8bf545b9978f4480e5150d12f9cd5da49397b33b8fd434ef9f7cf964` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 2.2 | `f1-2-2-02-criterio-de-conclusao` | `d7ec7f52bab60541b2b8928e817d278faf862e5e8c230fdc09a0237dea71c661` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 2.3 | `f1-2-3-02-criterio-de-conclusao` | `44d99c1bb9bc673483f5e7cfcd139906a5c274bf8087f4048f22ef585c9aecf9` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 3.1 | `f1-3-1-02-criterio-de-conclusao` | `61780d4a241fa47192bbf44405c7c3aea7e39c0d8f23d14f2d440d83d018c812` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 3.2 | `f1-3-2-02-criterio-de-conclusao` | `e08fdd7b53e89afb1ec55d8cb72768540be7c35b5d3a1d2d9074a8797cc43c5b` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 3.3 | `f1-3-3-02-criterio-de-conclusao` | `5f8d17f7b9fa4fd824f55f4cb3f6fd1f7c701db6372283a6b3ea1f68dd42d850` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 3.4 | `f1-3-4-02-criterio-de-conclusao` | `1cf745659735a1a6dd4097037075a10ebbd570b572c25a207f4b8c5e24ac7733` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |
| 3.5 | `f1-3-5-02-criterio-de-conclusao` | `41f5e5208f6ca816d5553d3df8141e814222c61d78a7b938a1f73f46ea7b4366` | `SOURCE_DEFINED_BUT_AMBIGUOUS` |

Os textos originais definem alvos de aprendizagem: explicar a arquitetura web e descrever o percurso navegador/DNS/HTTP (1.1); recriar e explicar o ambiente (1.2); operar terminal com segurança (2.1); interpretar permissões/processos/logs sem expor segredos (2.2); autenticar via chave SSH e proteger a chave privada (2.3); explicar estados e operações de Git (3.1); escolher merge/rebase/cherry-pick e lidar com conflitos (3.2); percorrer o fluxo GitHub e responder a exposição de credenciais (3.3); manter um repositório de estudo legível e utilizável (3.4); e compreender a ideia, preparar o ambiente pela documentação, navegar pelo repositório, manter histórico legível e não versionar credenciais/dados pessoais (3.5).

Esses enunciados são preservados. A fonte não define uma rubrica estruturada para cada unidade, evidências mínimas padronizadas, condições computáveis de satisfação nem regra para agregar aprovação. Por isso, sua presença não é convertida em aprovação automática. O código usa a classificação ambígua para bloquear conclusão até que o responsável pedagógico defina a política.

## Projeto 3.5

Há 11 materiais de projeto (brief, quatro marcos, uma rubrica, cinco checklists) e um artefato separado de teoria contextual. A rubrica define descritores 0–4 por marco: evidências completas/verificação aprovada; entrega aprovada com lacuna menor; artefato sem evidência ou verificação importante; entrega incompleta/difícil de usar; sem evidência avaliável. Também diz que marcos 3 e 4 não são aceitos enquanto houver credencial real ou dado pessoal versionado.

O texto não determina a regra de agregação dos quatro marcos, se todos os checklists são obrigatórios, como resolver uma “lacuna menor” no resultado final, nem se uma nota 3 em cada marco basta para concluir o projeto/fase. A implementação não preenche essas lacunas.

| Artefato | Tipo | SHA-256 |
|---|---|---|
| `f1-3-5-00-brief-projeto` | brief | `d381f5d17f0b4a5d1773348cbd9b87a068821ba434b6af280d86997137b3479c` |
| `f1-3-5-marco-01-escopo` | marco | `2541ab7ef86bec2e02f065fceb3fe8a581f6135aa5e03722f1120ac124663c0d` |
| `f1-3-5-marco-02-repositorio-setup` | marco | `69ed88657b0b19796058b8c8d6816f6800965abd17d860ca3b4fcd3a6e3ac5f9` |
| `f1-3-5-marco-03-historico-seguro` | marco | `2df7903a472803d96a5a357a5fef5b1497bdb6bc20e233d79edc7b1a5fb942d8` |
| `f1-3-5-marco-04-publicacao-remota` | marco | `b922364218f2952c3c7785f70d53799ecd4d1267e302ef8cfac48e0613387e55` |
| `f1-3-5-rubrica-comum-marcos-0-4` | rubrica | `a1e1b7609fc7b12b56aebde687c2e858aea5d6c599567722ec10637c1c57fcd5` |
| `f1-3-5-checklist-marco-01-aceite` | checklist | `f956838abee9af4e11228eec7b61103e8e97cf6b31477f9d2547944476f23401` |
| `f1-3-5-checklist-marco-02-aceite` | checklist | `93044f19dfc0f10e505a7b2460ee5fe6c5e4abef582c051d9fe14dd2bbd582f3` |
| `f1-3-5-checklist-marco-03-aceite` | checklist | `9523a19dedf6eb9865feae3102b956b15f75492eafab4f324bffa3cf47d575f7` |
| `f1-3-5-checklist-marco-04-aceite` | checklist | `71e0484831e537369d2ccc1892f754e7fa3bc1821e12e9555d39fd9a0f1e69c0` |
| `f1-3-5-checklist-revisao-final` | checklist | `78022069a1a5b5bdcc49d0488d838b47b5701ef0c193dbafabed7fc57e5034a3` |

O artefato de teoria contextual `f1-3-5-teoria-contexto` (SHA-256 `91a28118da504e93b58f57627b4eb28ac80f10062a4ccd9df574cf25a2d08c70`) não é contado como material do projeto.

## Competências e entregáveis que a fonte explicita

| Marco | Competência/objetivo preservado da fonte | Entregáveis e evidências que a fonte nomeia |
|---|---|---|
| 1 — problema e escopo | Delimitar problema, usuário, necessidade inicial, escopo e justificativa de aprendizagem; comunicar o primeiro resultado. | `projetos/trilho-a/brief.md` versionado e issue em inglês simples; leitura por outra pessoa (ou releitura após um dia quando individual). |
| 2 — repositório e setup | Organizar um repositório de estudo e tornar a entrada/instalação reproduzível por documentação. | Repositório; `README.md`; `setup/README.md`; árvore útil; requisitos, passos desde fontes oficiais e verificação observável das ferramentas; commits descritivos; clone limpo usado na conferência. |
| 3 — histórico e segurança | Manter histórico legível e configuração compartilhável segura; inspecionar alterações antes de gravar. | `.gitignore`; histórico recente; estado limpo após commits; justificativa para não compartilhar dotfiles, se aplicável; arquivo fictício ignorado e não rastreado; revisão de arquivos preparados e commitados. A fonte manda interromper a entrega e iniciar resposta a incidente se credencial real tiver sido commitada. |
| 4 — publicação remota | Publicar o repositório sem material sensível, atualizar issue/README e verificar o clone remoto. | Repositório GitHub acessível; issue atualizada; commits; README final; clone limpo que confirma branch, arquivos e setup. |

O brief escolhe entre gestor de tarefas, loja virtual ou base de conhecimento e admite uma troca da escolha até o fim da Fase 4 com justificativa. A revisão final lista os quatro marcos, README, setup, histórico/issues, `.gitignore` e escopo. Isso comprova que a fonte menciona esses itens; **não** determina, por si só, se cada item ou checklist é condição obrigatória e não compensável para a aprovação final.

O brief do projeto também delimita o produto pedagógico desta fase: manter um mesmo repositório ao longo do curso e preparar uma base segura, reproduzível e compreensível; não construir agora arquitetura ou funcionalidades finais. O critério de conclusão existente diz que outra pessoa deve compreender a ideia, preparar o ambiente pela documentação, navegar pelo repositório, encontrar histórico legível e não encontrar credenciais/dados pessoais versionados. Esse texto é requisito-fonte, mas não define um método objetivo de comprovar “compreender” ou a decisão final de aprovação.

## Classificação de formalização

Os textos por unidade e os quatro marcos são `SOURCE_DEFINED_BUT_AMBIGUOUS` para conclusão automática: seus alvos e evidências textuais são preservados, mas não existe protocolo estruturado de suficiência nem composição de uma decisão de domínio. Os descritores 0–4 são `SOURCE_DEFINED`; a aplicação deles a cada marco está no artefato de rubrica, porém o sistema de passagem geral permanece `PROPOSED_REQUIRES_APPROVAL`. Os cinco checklists são preservados como materiais fonte e não recebem `required=true` por inferência. A regra de não aceitação dos marcos 3 e 4 com credencial real/dado pessoal versionado é uma restrição explícita da fonte; a evidência e o processo de remediação ainda exigem definição operacional/pedagógica.
