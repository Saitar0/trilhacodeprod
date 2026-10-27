---
arquivo_id: "f7-32-2-90-integracao-p02-pratica-md"
parent_key: "32.2"
tipo_arquivo: "practice"
assuntos: ["03_saude_pos_deploy", "04_rollback_schema_dados"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Detecte falha e recupere a aplicação

**Desafio:** prove que um smoke check impede promoção e pratique a volta a uma versão conhecida.

**Passos:**
1. Defina um health check e um smoke check com endpoint, timeout e resposta esperada.
2. Implante primeiro uma versão conhecida como saudável e registre o identificador.
3. Em ambiente isolado, publique uma alteração de exercício que faça o smoke check falhar sem danificar dados compartilhados.
4. Confirme que o job fica falho e que a próxima promoção não continua automaticamente.
5. Reverta para o artefato anterior registrado, execute novamente health/smoke e anote tempo e passos de recuperação.
6. Documente também a alternativa de correção para frente e quem decidiria entre corrigir e reverter.

**Evidências:** critério do check; logs do caso saudável e falho; registro de bloqueio; identidade do artefato anterior; execução de recuperação e limitações.

**Verificação:** uma falha realista é detectada pelo check, o ambiente retorna à versão anterior e a recuperação é confirmada por uma verificação funcional.

**Aceite:** critério é objetivo; falha interrompe a promoção; rollback usa versão rastreada e é reproduzível; o ambiente fica saudável após a operação.

