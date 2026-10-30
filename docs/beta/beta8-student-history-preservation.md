# Beta 8 — Preservação do histórico de aprendizagem

O participante experimental de edição escreve somente no bloco sintético `draft`, revisão C8/C10 e auditoria. O fluxo de promoção escreve somente gerações/head/auditoria Beta 8. O usuário Mongo de autoridade não recebeu privilégios em `progress`, `activity_attempts`, `submissions`, nem em `tracks` ou coleções de publicação. O runtime e o preparador tampouco recebem esses privilégios.

O harness verificou, pelo provisionador do banco descartável, que as coleções operacionais `tracks`, `nodes`, `relations`, `activity_publications`, `track_publications`, `progress`, `activity_attempts` e `submissions` não foram criadas. A promoção preservou uma geração experimental anterior e a concorrência não alterou dados de aprendizagem.

Isso prova a ausência de acesso/efeito nesses dados para a fatia sintética testada. Não prova que W-02/W-06/W-11 operacionais preservam histórico: esses writers continuam bloqueados no plano de integração. Também não é teste sobre aluno ou dado real; nenhum foi utilizado.
