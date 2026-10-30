# Homologação de segurança MongoDB — atividades 14F.1

## Decisão

**PARCIAL — persistência em banco e RBAC de coleção não homologados.** O ambiente descartável exigido não pôde ser iniciado ou comprovado. Não usar o serviço MongoDB preexistente: identidade não confirmada.

## Evidência de ambiente

- Projeto/branch/HEAD: `migracao-estrutura` / `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Docker CLI 29.8.2 e Compose v5.6.0 disponíveis; Engine indisponível no pipe local.
- Serviço Docker Desktop parado; inicialização negada por falta de permissão.
- `mongod`/`mongosh` ausentes; serviço MongoDB automático preexistente não consultado.
- Nenhuma URI explícita de teste. Nenhum banco/cluster foi contatado.
- Python 3.13.15, PyMongo 4.17.0 e Pydantic 2.13.5.

## Avaliação por controle

| Controle | Evidência | Resultado |
|---|---|---|
| Separação física público/privado | Coleções distintas, projeções explícitas e modelos de resposta separados | Implementado no repositório; não testado contra permissões Mongo |
| Acesso de aluno a gabaritos | Repositório não está conectado a endpoint de aluno; leitura privada exige `submissions.grade` no serviço | Nenhum endpoint novo; ACL do banco segue pendente |
| Credencial pública restrita | Nenhum role/user Mongo foi criado | Não homologado; bloqueador para afirmar isolamento no servidor |
| Atomicidade das quatro gravações | Público, privado, evento e head compartilham transação/sessão | Confirmado por inspeção; sem comprovação no servidor |
| Imutabilidade de versões e CAS | Versões são insert-only; revisões exigem versão-base atual | Lógica e fake cobertos; corrida real pendente |
| Integridade do head | Antes de revisão, valida head, par, hashes e evento; falha fechado | Regressão fake aprovada; servidor real pendente |
| Rollback | Testes opt-in preparados para falha após escrita e antes do head | Não executados |
| Índices e unicidade | Seis índices declarados no método `ensure_indexes()` | Nenhum índice real criado/verificado |
| Reexecução/idempotência | Mesmo hash retorna versão existente; commit incerto tem erro próprio para reconciliação | Fake aprovado; replay após persistência Mongo não executado |
| Política dos quizzes | Nenhuma rota ou serviço operacional foi conectado; sem mudança de tentativas, nota ou progresso | Sem regressão unitária relevante; não houve mudança operacional |
| Importação/publicação | Não executadas | Confirmado pelo escopo da execução |

## Testes executados

- Persistência e regressões unitárias: **99 aprovados, 4 ignorados**.
- Os quatro ignorados são testes opt-in MongoDB que exigem URI explícita de replica set descartável.
- Ruff, formato, mypy focal, compilação Python e `git diff --check`: aprovados.
- Nenhum teste com banco foi executado. Não apresentar os testes fake como prova de transação, concorrência, rollback, índice ou RBAC real.

## Limitações

Mesmo quando executado, o teste planejado usa replica set de um membro: isso valida transações no topology de teste, mas não eleição, failover nem disponibilidade distribuída de produção. A camada atual separa as coleções, porém o isolamento por role Mongo ainda precisa ser configurado e demonstrado com credenciais restritas, sem usar credencial administrativa como prova.

## Integridade curricular e Git

- SHA-256 do pacote curricular confirmado: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- Nenhuma árvore curricular ou JSON foi modificada nesta etapa.
- Nenhuma operação de importação, publicação, migração ou conexão com banco foi executada.
- Nenhum commit foi criado.

## Gate antes de integração

Não conectar a persistência a frontend, endpoints ou importador até que um ambiente de replica set descartável, iniciado para o teste e identificado por URI explícita, permita executar os testes de rollback, concorrência, índice e recuperação. Em seguida, testar credenciais distintas e confirmar no servidor que o principal público não lê a coleção privada. Produção e failover continuam fora desta homologação.
