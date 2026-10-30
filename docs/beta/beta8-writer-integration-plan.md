# Beta 8 — Plano de contenção e migração gradual dos writers

## Reconciliação

A lista C13 versionada foi reconciliada com o commit Beta 8: os 17 caminhos e símbolos continuam localizáveis. W-01–W-16 são funções/serviços classificados no inventário anterior; W-17 é a classe `EditorialGenerationsPoC`. Todos mantêm `runtime=NOT_VERIFIED`. A matriz detalhada está em `beta8-editorial-writer-inventory.md`.

## Ondas propostas

| Onda | Writers | Pré-condições |
|---|---|---|
| 0 — conter credenciais | W-01–W-17 | Identificar cada processo/credencial por evidência operacional autorizada; retirar escrita editorial de runtimes comuns; bloquear cutover enquanto identidade não for mapeada |
| 1 — mutações atômicas por trilha | W-01, W-05, W-07, W-08 | Resolução servidor-side de trilha, grant por recurso, revisão/fence comum, auditoria na transação e testes de conflitos |
| 2 — operações compostas | W-03, W-06 duplicação, W-10 | Contrato de lote, idempotência, referências, checkpoint/recovery e exclusão de writes concorrentes |
| 3 — catálogo global e snapshots | W-09, W-12, W-15 | Autoridade global separada, revisão do catálogo, consistência do snapshot e leitores compatíveis |
| 4 — operações de alto impacto | W-02, W-06 exclusão, W-04, W-11 | Política de retenção aprovada, preservação de tentativas/progresso, gerações imutáveis, recuperação e rollback ensaiados |
| 5 — comandos e serviços indiretos | W-13, W-14, W-16, W-17 | Seed/migração com alvo explícito; auditoria transacional; PoC permanece isolada; call graph e comando de cada migração classificados |

## Decisões de contenção

* Não migrar em massa nem alterar os writers ativos nesta fase.
* Desabilitar/retirar privilégios de um writer legado só após mapear sua identidade e provar que nenhum processo depende dela.
* Separar credencial de leitor, runtime/aprendizagem, preparador, autoridade editorial e auditoria, com grants MongoDB mínimos por coleção.
* MongoDB não oferece ACL por documento; autoridade precisa ser fronteira de processo/credencial confiável, não somente uma classe Python compartilhada.
* W-02/W-06 exclusão e W-11 restauração ficam bloqueados até política de retenção e prova de não remoção de dados do aluno.
* W-04 publicação e W-10 importação ficam bloqueados até autoridade, geração e leitores compatíveis; o importador Beta 2–7 não é essa autoridade.

## Evidência necessária por writer

Para sair de `NOT_VERIFIED`, cada item precisa de identidade de serviço real identificada, privilégios efetivos observados por leitura autorizada, chamada HTTP/job/CLI real em ambiente controlado, teste de bypass com identidade antiga, CAS/fence/idempotência/auditoria e comportamento de recovery. A prova Beta 8 cobre uma mutação sintética e não altera o status C13 dos demais.
