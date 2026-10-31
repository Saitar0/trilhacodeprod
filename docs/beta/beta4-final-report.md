# Beta 4 — relatório final

## A. Resultado executivo

Dez unidades da Fase 1 revisada foram descobertas, tipadas e convertidas em um único payload experimental. A prova persistente usou `run_import` e os leitores reais de serviço em MongoDB 7 descartável, mantendo tudo draft/private. Testes demonstraram leitura, replay sequencial e retomada após falha sintética parcial. O resultado é parcial: campos importantes e o projeto 3.5 não têm destino operacional seguro; não houve HTTP, frontend, publicação ou fluxo de aprendizagem.

**Veredito: PRIMEIRA FASE PARCIALMENTE VALIDADA — ADAPTAÇÕES E INTEGRAÇÃO PENDENTES.** Nenhum resultado autoriza publicação, integração ou deploy.

## B. Git e isolamento

Base `68cd396f6c12dda8b464208c130fb03dc40a6870`; branch `codex/beta4-first-phase-curriculum-validation`; worktree `C:\Users\Joao\.codex\worktrees\trilhacode-beta4-first-phase\trilhacodeprod`. A base contém os artefatos Beta 3. Só novos módulos/testes experimentais e documentos `docs/beta/beta4-*` foram criados. O commit local foi gravado, sem merge, cherry-pick, push ou deploy; a verificação final confirmou a worktree limpa.

## C. Fonte e inventário

Fonte segmentada: worktree `migracao-estrutura`, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`; 221 arquivos rastreados no recorte e sem diferenças Git nesse caminho. A worktree tem alterações de terceiros em outros diretórios; elas não foram tocadas. A classificação da fonte é `rascunho`. O hash monolítico 1.1 coincide com a referência Beta 3 autorizada (`db6e3ae5...`). O inventário: 3 módulos derivados dos IDs, 10 unidades, 30 tópicos, 42 segmentos, 30 arquivos de quiz/44 questões, 26 exercícios, 11 artefatos de projeto, 39 referências, 30 relações extraídas e 21 relações internas no payload.

## D–L. Conversão e fidelidade

O conversor Beta 4 reutiliza modelos Pydantic estritos Beta 3. Preserva ordem e conteúdo Markdown por tópico/segmento, IDs estáveis, título, objetivo, resumo, questões, alternativas, respostas/explicações em blocos draft, exercícios manuais, proveniência e hashes. A unidade 1.1 mantém 5 tópicos/8 segmentos, 5 questões e 3 exercícios. A unidade 3.4 tem 4 questões/2 exercícios. A 3.5 contém 11 materiais de projeto e nenhum quiz/exercício convencional; esses materiais não são importados.

Critérios de conclusão, respostas/rubricas manuais, checklists, descrição de referências, marcos do projeto e parte das relações permanecem no contrato/intermediário ou foram deliberadamente excluídos do payload com `REQUIRES_ADAPTER`. Relações internas são não enforced. O manifest não contém corpos privados. Todos os itens foram convertidos com avisos, não como integração pronta.

## M–R. Determinismo, persistência e recuperação

IDs são derivados de IDs de origem; o manifesto canônico não inclui horário de execução. Duas conversões produziram mesmo payload/hash no teste. Hash bruto e hash de LF agora são calculados separadamente para cada artefato. O manifesto agregado em `docs/beta/beta4-first-phase-manifest.json` declara 10 unidades, 3 módulos, 161 blocos e hash de payload `0c0ba5e5db5c0d18d03383657cd87d17ea599547e3cc261c61a1186e5d84410f`; SHA do manifesto canônico `7228f727a21ea38493456edd5cbcb63c8299349242be35555672cef854a6f191`.

MongoDB 7.0.43, WiredTiger standalone descartável. `run_import` real persistiu 44 nós, 161 blocos, 21 relações e uma entrada de histórico. `get_track_tree` e `get_node` reais leram a árvore; uma leitura de estudante sintético foi negada em draft/private e a projeção `_student_block` retirou campos de solução. Replay sequencial não duplicou dados. Falha injetada na 61.ª preparação deixou 60 blocos e job/trilha interrompidos; repetição retomou o mesmo lote sem duplicação. O writer não possui transação global, portanto houve estado parcial real dentro do banco de teste.

## S–U. Privacidade, índices e verificações

Gabaritos de quiz foram mantidos em blocos draft no banco descartável e não apareceram em manifestos. As respostas de exercícios/rubricas não foram persistidas. ACL de publicação e de instrutor não está demonstrada. A divergência de índices 38/40 é explicada pelos dois índices `track_publications` adicionados no commit `2574bf1b...`; nada operacional foi alterado.

Resultados novos: 6 testes unitários de conversor e 2 testes persistentes aprovados. Regressões offline Beta 2/Beta 3, snapshots, formato de importação e progresso: 53 aprovadas. Ruff nos quatro módulos experimentais: aprovado. MyPy do conversor: aprovado com `--disable-error-code=import-untyped` para PyYAML sem stubs e `--explicit-package-bases`. Uma checagem de MyPy que também seguiu imports do harness expôs 37 diagnósticos em 13 módulos operacionais existentes; nenhum deles foi alterado. Compilação sintática passou. A asserção histórica de índices falhou (espera 38, lista 40); seu fixture usou a porta 27017, conforme ressalva no documento de índices. Nenhuma suíte completa do backend foi inferida desses resultados.

## V–AC. Segurança, prontidão e próximo passo

Não houve acesso intencional a staging/produção, credenciais reais, dados reais de aluno, conteúdo curricular alterado, IAM ou writers ativos, nem deploy. Houve uma exceção de isolamento: a execução da asserção histórica de índices inicializou o fixture versionado que aponta ao padrão `localhost:27017`, criou um banco sintético `test_*`, aplicou migrações e semeou dados/rotas de teste, incluindo a publicação de trilha sintética. O teardown não reportou erro, mas a identidade do servidor e a limpeza não foram verificadas fora do fixture; nenhum novo teste com ele será executado. Na limpeza Beta 4, dois bancos temporários próprios ainda estavam presentes; seus marcadores foram verificados e os bancos foram removidos antes do container/rede, cuja identidade e configuração foram conferidas. Os estados históricos ficam inalterados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED; ADR-008 BLOCKED.

Próximo incremento recomendado: desenhar e aprovar contratos de backend/ACL para critérios, projetos e material de correção, depois implementar staging/promover sob o enforcement C8–C16 e cobrir HTTP/aluno/E2E. A integração não deve começar enquanto os escritores diretos puderem contornar a autoridade editorial ou as respostas privadas não tiverem proteção comprovada.

## Artefatos

Ver [inventário](beta4-first-phase-inventory.md), [matriz](beta4-curriculum-conversion-matrix.md), [contrato de lote](beta4-batch-import-contract.md), [fidelidade](beta4-content-fidelity-report.md), [validação de avaliações](beta4-quiz-and-exercise-validation.md), [resultados persistentes](beta4-persistent-batch-results.md), [recuperação](beta4-import-recovery-results.md), [índices](beta4-index-divergence-analysis.md), [prontidão](beta4-integration-readiness.md) e [manifesto JSON](beta4-first-phase-manifest.json).
