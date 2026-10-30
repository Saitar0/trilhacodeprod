# Beta 8 — Matriz de autorização por recurso

## Leitura do IAM atual

`backend/security.py::current_user` valida JWT de acesso, sessão ativa, usuário existente/ativo, versão do token e verificação de e-mail. `backend/permissions.py::require` compara permissões globais derivadas do papel em `backend/constants.py`. Essa fronteira não consulta os grants experimentais C11/C12.

| Ação | Ator e permissão efetivos no código-base | Recurso/escopo | Beta 8 | Estado |
|---|---|---|---|---|
| Ler trilha publicada | Sessão autenticada; `can_view_track` admite público publicado e certos papéis com `content.read` | Trilha; leitura ativa não usa grant experimental | Sem mudança; leitor ativo não foi conectado à prévia nem à promoção | Código inspecionado; HTTP operacional não executado |
| Ler draft/private | Usuário com permissão global pode alcançar alguns leitores administrativos; não há grant C12 nas dependências ativas | Trilha/bloco | A fatia Beta 8 só aceita bloco sintético em `draft`, resolvendo trilha no banco e exigindo grant C12 exato | Persistência experimental |
| Editar draft | Rotas/services existentes usam `content.write` global; escopo por recurso não está demonstrado na dependência ativa | Trilha/bloco | `block.update` exige principal ativo, sessão ativa, permissão e grant exato; C10 CAS/fence + C12 transacional | Persistência experimental |
| Revisar/aprovar conteúdo | Não foi demonstrada uma política operacional comum para revisão editorial | Revisão/trilha | Não implementado como fluxo geral; somente mutação sintética de bloco | NOT_VERIFIED operacional |
| Preparar importação | Importador ativo exige `content.write` e usa job/lease próprios; não há fence comum para todos os writers | Lote/trilha | Papel `beta8-preparer` escreve somente nas duas coleções sintéticas de staging e não altera bloco/head | Rejeição MongoDB persistente |
| Promover geração | Não há rota Beta 8; a promoção ativa permanece fora do escopo | Lote/trilha/revisão | `content.publish` + grant de trilha; só grava coleções `_beta8_experimental_*`, com CAS/fence/auditoria | Persistência sintética |
| Publicar/retirar publicação | Writers ativos separados e cobertura/runtime desconhecidos | Publicação/geração | Sem caminho de escrita nas coleções operacionais de publicação | Não executado; privilégio ausente no papel de autoridade de teste |
| Consultar gabarito/rubrica | Projeções da aprendizagem existentes; não alteradas nesta fase | Atividade/avaliação | Sem novo acesso público; harness não usa conteúdo curricular real | NOT_VERIFIED nesta fase |
| Corrigir submissão | Fluxo de aprendizagem Beta 7.1 usa concessão experimental por trilha; IAM operacional completo não integrado | Submissão/trilha | Sem alteração | Histórico de beta; não regressado aqui |
| Consultar auditoria | Funções e ACL de auditoria operacional sem verificação de deployment | Evento/ator | Writer de autoridade grava eventos append-only; role usado pelo serviço não tem `find` nos eventos B8 | Inserção persistente; leitura separada proposta |

## Regra experimental

Para o serviço Beta 8, tudo que não estiver descrito no contrato é negado. O ator é carregado pela autoridade sintética a partir de seus próprios registros; parâmetros de cliente não são fonte de papel ou escopo. O bloco determina o `track_id`, e a autorização confere a operação e grant daquele mesmo recurso. A regra vale apenas dentro do serviço desconectado e das identidades sintéticas.

## Limite

A matriz não descreve permissões efetivas de produção. Não foi acessada qualquer configuração operacional, usuário MongoDB real, secret store, instância staging/produção ou identidade implantada. A aplicação ativa continua com permissões globais por papel em sua camada HTTP, e C12 continua fora do IAM operacional.
