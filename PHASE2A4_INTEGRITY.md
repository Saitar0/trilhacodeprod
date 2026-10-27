# Trilha Code — Fase 2A.4: Integridade, concorrência e ciclo de vida

## 1. Escopo da auditoria

Foi lido `PHASE2A3_REFACTOR.md` e pesquisado o backend completo, incluindo routers, serviços, setup de índices, migrações, seed, importação, tarefas de gestão e fixtures. A auditoria não conectou ao banco de desenvolvimento ou de produção. Os únicos dados consultados durante a validação pertenciam ao banco `test_*` descartável criado pela fixture, em um MongoDB 7 temporário.

### Achados comprovados no código

| Evidência | Achado | Efeito |
| --- | --- | --- |
| `services/auth.py::register_user` | Consulta por email seguida de `insert_one`; o índice único de email existia, mas `DuplicateKeyError` não era traduzido. | Duas requisições simultâneas podiam transformar uma duplicidade normal em erro 500. |
| `services/taxonomy.py::create_taxonomy`, `create_tag` e `create_block_type` | Consulta de duplicidade seguida de inserção. Havia índice único de taxonomias e tipos de bloco, mas não de slug de tag; as gravações não tratavam disputa concorrente. | Uma duplicidade concorrente podia causar 500; tags podiam ser duplicadas no banco. |
| `services/progress.py::visit_node` | Fazia `find_one` e depois `insert_one` para criar progresso de nó. | Visitas simultâneas podiam disputar a criação do mesmo documento; já existia índice único que impedia duas linhas, mas uma requisição podia falhar. |
| `services/progress.py` e `learning.py` | `user_track_state` é atualizado com `upsert` por `(user_id, track_id)`, mas não tinha índice único correspondente. | Upserts simultâneos podiam produzir estados repetidos para o mesmo usuário e trilha. |
| `services/taxonomy.py::delete_tag` | Remove referências em nós e trilhas em escritas separadas. | Não é atômico. Uma falha entre as coleções pode deixar parte da limpeza pendente. |
| `services/submissions.py::submit_answer` e `grade_submission` | Atualiza submissão, progresso e evento em comandos separados. | Falha depois da mudança de status pode deixar progresso ou histórico de eventos incompleto. |
| `services/nodes.py::delete_node`, `services/tracks.py::delete_track` e duplicação de nós/trilhas | Cascatas e cópias gravam ou removem documentos em várias coleções sem transação. | Falha intermediária pode deixar dados parciais; não há garantia transacional comprovada. |
| `services/imports.py::_execute` | Importação grava trilha, tags, nós, blocos, relações e auditoria em etapas. Atualizações por `import_ref` e relações usam upsert, mas a sequência não é atômica. | Reexecução é parcialmente idempotente, mas uma interrupção pode deixar importação incompleta. |
| `backend/learning.py` | O arquivo combina router com operações MongoDB para notas e revisões, diferente dos routers delegados na Fase 2A.3. | Fronteira de camada inconsistente; risco arquitetural, sem falha de integridade isolada comprovada nesta etapa. |
| `migrations/__init__.py::migrate` | A trava usa lease de 15 minutos sem renovação; o marcador de cada migração só é inserido após `up()`. | Se uma migração exceder o lease, outra instância pode tentar obtê-lo. Não foi reproduzido; risco de duração longa. |
| `indexes.py::ensure_indexes` | A rotina removia o índice único antigo de tentativas de submissão antes de recriá-lo com outro nome. | A janela sem índice permitia corrida durante atualização do índice. A mudança abaixo mantém o índice equivalente e evita a remoção. |
| `services/tracks.py::create_track` e `services/imports.py::_execute` | Slug de trilha é usado para localizar trilhas, mas não há índice único. | Slugs duplicados podem tornar a associação de importação ambígua. Unicidade não foi presumida nem adicionada nesta fase. |

### Riscos sem falha reproduzida

- `authenticate_user` lê a contagem de tentativas e depois incrementa com `$inc` atômico. O incremento não perde atualizações, mas requisições simultâneas podem passar pelo limite antes de observarem a contagem atualizada.
- A criação de submissões usa índice único em `(user_id, block_id, attempt)` e captura colisão ao abrir uma tentativa. A atualização de reivindicação usa `find_one_and_update` condicional e é atômica por documento. A suíte não reproduz corrida entre dois corretores além da proteção condicional existente.
- Ordenação baseada em `count_documents` ou no último `order` pode atribuir posições repetidas sob concorrência. Não há restrição de unicidade de ordem, e a ordem não foi tratada como chave de integridade.
- `seed.py` usa upserts em taxonomias, tipos e tags; cadastro do usuário seed segue consulta seguida de inserção. Uma inicialização concorrente pode colidir no índice de email.

## 2. Correções implementadas

- Cadastro captura colisão no índice único de email e mantém a resposta HTTP 400 já usada para email existente.
- Criação e atualização de taxonomias e tipos de bloco, e criação de tags, traduzem colisões de índice para as respostas HTTP 400 existentes.
- Progresso de visita passou a ser criado por `update_one(..., upsert=True, $setOnInsert)`, tornando a criação do registro de nó idempotente e atômica por documento.
- Exclusão de tag limpa as referências em nós e trilhas antes de remover a tag. Se uma etapa falhar, a tag permanece disponível e a operação pode ser repetida; não há promessa de atomicidade entre coleções.
- Importação de tags passou a usar upsert por slug e recuperar o documento persistido, evitando falha quando uma importação concorrente cria o mesmo slug.
- A rotina de índices agora inspeciona duplicatas antes dos índices únicos novos ou reconfigurados. Em caso de duplicatas, interrompe a criação com valores, contagens e amostras de IDs. Não apaga nem altera registros.
- A atualização do índice de tentativas deixou de remover o índice único equivalente antes da criação. `create_index` idempotente preserva a proteção existente e evita a janela sem índice.
- `server.py` migrou de `@app.on_event` para `lifespan`: verifica migrações antes do `yield`, mantém o aviso em desenvolvimento e a falha em produção, e fecha o cliente Mongo no encerramento.
- Não foram introduzidas transações: a configuração disponível não comprova que produção usa replica set ou outro deployment compatível. A migração Motor → PyMongo Async não foi feita.

## 3. Índices e verificação de dados

Índices únicos adicionados:

- `tags.slug` (`one_tag_slug`), após inspeção agregada de duplicatas.
- `user_track_state(user_id, track_id)` (`one_user_track_state`), após inspeção agregada de duplicatas.

Índice de tentativas em `submissions(user_id, block_id, attempt)` continua único. Agora a rotina verifica duplicatas antes de assegurar o índice e não remove o índice anterior para renomeá-lo.

A checagem de duplicatas foi exercitada com uma coleção simulada e a criação é interrompida quando encontra valores repetidos. Não foi feita inspeção de dados reais de desenvolvimento ou produção, pois a validação desta fase foi restrita ao MongoDB temporário. Antes de executar `ensure-indexes` em ambiente com dados existentes, a rotina fará a inspeção. Se detectar duplicatas, o operador deve revisar os IDs e resolver manualmente conforme a regra de negócio; esta fase não escolhe registros vencedores nem altera dados.

## 4. Garantias de atomicidade e idempotência

- Índices únicos dão garantia de unicidade para email, taxonomia, tipo de bloco, tag, progresso e tentativa de submissão, desde que os índices estejam instalados.
- A criação/atualização de um documento por `update_one` ou `find_one_and_update` é atômica por documento no MongoDB. Isso não torna atômicas escritas em coleções diferentes.
- Visita mantém no máximo um registro de progresso por chave e não sobrescreve o progresso existente ao visitar novamente. Eventos de visita continuam sendo registrados por chamada, conforme o comportamento anterior.
- Exclusão de tag pode ser repetida. A limpeza parcial pode remover referências antes da falha, mas a tag não é removida até as duas atualizações terminarem.
- Notas, revisões pendentes, blocos de versão e trabalhos de restauração já tinham índices únicos ou condicionais definidos em `indexes.py`; foram mantidos.

## 5. Testes e verificações

Foram adicionados testes para cadastro concorrente, criação concorrente de tag, visitas concorrentes, resposta HTTP de duplicidade, falha intermediária e repetição segura da exclusão de tag, preflight de índice e ciclo de vida FastAPI.

Executado com Python 3.11 e MongoDB 7 em contêiner descartável na porta 27023. O fixture gerou um banco `test_*` aleatório e o descartou ao finalizar.

- Ruff: passou.
- Compilação: 56 arquivos Python compilados.
- Suíte completa: **61 passaram**, 1 aviso de depreciação do `python_multipart` via Starlette.
- `git diff --check`: sem erro de whitespace; permanecem avisos do Git sobre conversão LF/CRLF em arquivos do worktree.

## 6. Possíveis regressões

- O novo preflight pode impedir `ensure-indexes` quando encontrar duplicatas antigas. Isso é intencional para evitar apagar ou escolher dados automaticamente; exige resolução manual antes de prosseguir.
- O índice de slug de tag rejeitará tags que tenham o mesmo slug, inclusive quando nomes diferem apenas por espaços e caixa conforme a normalização existente.
- A limpeza de tag agora prefere deixar uma tag existente com referências parcialmente removidas em caso de falha, em vez de apagar a tag e deixar referências órfãs. A operação é recuperável por repetição, mas continua sem transação.
- O teste de ciclo de vida exercita a ordem de verificação/encerramento diretamente. O `ASGITransport` usado pelos testes existentes não inicia lifespan automaticamente.

## 7. Pendências para a próxima fase

- Avaliar migração das rotas de notas e revisões de `learning.py` para serviço dedicado.
- Definir política para falhas entre submissão, progresso e evento; opções incluem reconciliação idempotente ou transactional outbox. Avaliar implantação de produção antes de considerar transações.
- Avaliar lease renovável para migrações e execução concorrente de migrações que ultrapassem 15 minutos.
- Decidir se slug de trilha deve ser único; antes de qualquer índice, revisar duplicatas no ambiente-alvo e documentar correção manual.
- Revisar limites concorrentes do lockout de autenticação e atribuição de ordem quando houver requisito estrito.
- Adicionar testes de falha intermediária para cascatas de nós/trilhas, submissão/correção e restauração de versões.

Não houve push, deploy ou alteração de dados fora do banco descartável.
