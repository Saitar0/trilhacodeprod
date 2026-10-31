# Fase 2.1A.12C.6 — Harness isolado de escritor editorial

## Objetivo e limites

Este experimento carrega e executa o símbolo real `update_block` de [`backend/services/blocks.py`](../../backend/services/blocks.py#L38-L45) somente nos testes, substituindo previamente todas as dependências importadas por fakes. O wrapper da Fase 12C.5 é conectado apenas ao callable de teste. Nenhuma rota, serviço ativo, banco, aplicação FastAPI, publicação ou infraestrutura é inicializada.

O resultado avalia transparência do wrapper em torno do fluxo de código exercitado. Não valida persistência MongoDB, autorização, CAS, fencing, runtime, segurança do escritor ou comportamento de produção.

## Escritor escolhido

O inventário da Fase 12C.4 classifica o serviço de blocos como W-05 e aponta CRUD/reordenação de `content_blocks`, incluindo atualizações sem revisão comum ou fencing ([inventário W-05](editorial-generations-phase-2-1a-12c4-writer-inventory.md)). Foi selecionado `update_block`, uma alteração limitada a um documento, sem publicação, restauração, importação em lote ou exclusão. É o menor candidato adequado encontrado; permanece um writer legado e seu uso em runtime não foi comprovado.

O corpo real, nas linhas 38–45, lê o bloco, valida status, altera `data["updated_at"]`, chama `content_blocks.update_one`, chama `audit` e retorna `content_blocks.find_one`. O `update_one` não usa revisão esperada. A função descarta o resultado da atualização. A auditoria ocorre depois da mutação. Se a auditoria falhar, a função pode propagar erro após a alteração já ter ocorrido; não há rollback nesse caminho. O harness testa essa ordem e não corrige nem mascara esse comportamento.

## Importação segura e fakes

Uma importação normal desse módulo não é apropriada para o teste: `blocks.py` importa `audit`, `database`, `integrity`, `serialization` e `services.common`; esses caminhos transitivos referenciam `database.py`, que instancia `AsyncMongoClient` no escopo do módulo. `integrity.py` também importa `database`. O harness não importa tais implementações. Antes de executar o arquivo real por `importlib`, fornece módulos sintéticos por uma função `__import__` restrita ao namespace de builtins daquele módulo. Ela intercepta somente os imports de topo necessários (`fastapi`, `audit`, `core_utils`, `database`, `integrity`, `serialization` e `services.common`); não altera `sys.modules`, não instala hook global e não altera o import de outros módulos.

O símbolo continua vindo do arquivo versionado real: o teste verifica `update_block.__code__.co_filename` contra `backend/services/blocks.py` e confirma que o global `db` aponta para a coleção fake. O fake da coleção implementa somente `update_one` e `find_one`; os helpers de documento, status, data, ObjectId e auditoria são stubs determinísticos. A auditoria fake registra ordem, sem escrever em `edit_history`. Nenhum cliente MongoDB é criado e nenhuma operação de rede ou disco de dados ocorre.

Limitações deliberadas dos fakes: não reproduzem semântica de MongoDB, conversão real de ObjectId, grants, autorização HTTP, validação real de `services.common`, escrita de auditoria, transações, concorrência de armazenamento, efeitos colaterais de `integrity` nem durabilidade. Os testes demonstram equivalência do wrapper no fluxo executado, não equivalência integral da aplicação.

## Contrato de evento utilizado

O contexto é construído apenas com valores fechados já catalogados: `block.mutate`, `service` e `legacy_service`, correspondentes ao W-05. Nenhuma identidade, argumento, retorno, campo editorial, valor de usuário, exceção ou mensagem é passado ao instrumentador. O schema da Fase 12C.5 permanece inalterado e rejeita campos extras.

Sem classificador, o retorno do writer produz `unknown`: o método não fornece um sinal suficiente de confirmação persistente, e o fato de retornar um documento não é promovido a sucesso. Um teste separado comprova que um classificador explicitamente fornecido controla a categoria do evento em dados sintéticos; isso não é uma recomendação de classificação para integração real. Exceções comuns emitem apenas `failed`; uma exceção de validação pode ser classificada como `rejected` somente pelo classificador explícito do teste. Cancelamento async permanece propagado e é classificado como `cancelled` pelo contrato existente.

## Matriz de cenários

| Cenários | Evidência exercitada |
|---|---|
| T01–T04 | Símbolo real, execução base, instrumentador nulo e passivo; estado, ordem e retorno equivalentes. |
| T05–T09, T17–T18 | Execução única, identidade do retorno/exceção, falha do coletor, ordem invariável e ausência de retry. |
| T10–T14 | Sentinela privada em entrada/retorno/exceção, ausência da sentinela em eventos/logs, schema e catálogo fechados. |
| T15–T16, T26–T27, T29 | Resultado `unknown` por padrão, buckets fechados, classificação explícita, rejeição explícita e falha do relógio. |
| T19–T21 | Pontos de entrada de rede bloqueados no teste, ausência estática do import do harness/observador nos pontos examinados e writer byte a byte inalterado durante a execução. |
| T22–T25, T28, T30 | Cancelamento, falha de fake, repetibilidade, falha de auditoria após escrita, ausência de rollback/retry e equivalência da mutação do argumento feita pelo próprio writer. |

Foram implementados 30 testes do harness, executados sem skips. Os testes independentes da Fase 12C.5 (36) e do protocolo em memória 12C.1 (18) também passaram na mesma execução combinada. O resultado foi 84/84 aprovados. Os testes comprovaram que a instrumentação não acrescenta ou reordena chamadas no fake, não repete o callable, preserva identidade de resultado e exceção e não incorpora dados sintéticos privados nos eventos.

## Falha parcial observada

O cenário de erro da auditoria mostra `update_one` seguido de falha em `audit`, sem chamada a `find_one`. O estado sintético permanece alterado nos quatro modos (sem instrumentação, nulo, passivo e coletor defeituoso). O evento passivo classifica apenas a chamada que falhou como `failed`; não indica rollback, nem distingue commit parcial. Essa limitação pertence ao escritor/contrato legado e confirma que observabilidade não é enforcement ou transação.

## Integração futura — não realizada

O harness importa o módulo observacional e carrega o writer somente no teste. Uma busca estática também verificou que os pontos examinados (`server.py`, `routes_content.py` e `services/blocks.py`) não importam o harness ou a instrumentação. Não foram adicionados imports ativos, hooks, configuração, middleware ou dependências ao runtime.

Qualquer integração futura exige autorização separada, baseline operacional e linha de release aprovados, cobertura de todos os writers relevantes, sinal de resultado semântico, política de privacidade, teste no ponto de integração real e gates aplicáveis. O evento `revision_protocol` não prova CAS/fencing; este harness declara `legacy_service` e não altera o writer.

## Limitações e gates

- A observação não impede bypasses e não demonstra CAS, fencing ou commit persistente.
- Ausência de eventos não prova ausência de writers.
- Escritores externos ou não versionados continuam desconhecidos.
- O coletor é efêmero e em memória; eventos podem ser perdidos.
- O comportamento de falha parcial do writer não é corrigido pelo wrapper.
- O runtime continua não comprovado; ADR-008 permanece bloqueado.
- Os estados históricos dos gates permanecem G1 `PARTIAL`, G2 `NOT_VERIFIED`, G3 `NOT_VERIFIED`, G4 `PARTIAL`, G5 `NOT_VERIFIED`, G6 `PARTIAL`, G7 `PARTIAL`, G8 `NOT_VERIFIED`, G9 `BLOCKED`, G10 `BLOCKED`.

PyMongo não está disponível no Python usado nesta execução. Por isso, testes offline do adaptador C2 não foram executados; não houve tentativa de instalar dependências, iniciar banco ou conectar a serviço. Esta limitação não afeta os testes de fakes e tampouco fornece evidência persistente.
