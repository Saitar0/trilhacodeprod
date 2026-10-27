---
arquivo_id: "f4-9-3-90-integracao-kp03-gabarito-pratica"
parent_key: "9.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_integridade_referencial_e_exclusao", "03_limites_constraints_e_evolucao_segura"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** Defina ativo como empréstimo sem devolução registrada (fim IS NULL) ou como intervalo [inicio, fim) sem sobreposição, conforme o domínio. Uma opção no PostgreSQL é uma exclusion constraint sobre exemplar_id e um intervalo de tempo, combinando igualdade de exemplar com sobreposição de intervalos, usando a extensão btree_gist quando necessária; outra estratégia é guardar empréstimo ativo em estrutura/estado apropriado e impor unicidade parcial por exemplar. Uma operação transacional com bloqueio adequado também pode serializar a verificação e a gravação, se todos os caminhos respeitarem o protocolo. Dois empréstimos encerrados em períodos distintos devem ser aceitos; empréstimos ativos de exemplares diferentes devem ser aceitos; dois períodos ativos sobrepostos para o mesmo exemplar devem ser rejeitados. O DDL exato depende da definição de intervalo e versão/configuração do PostgreSQL.

