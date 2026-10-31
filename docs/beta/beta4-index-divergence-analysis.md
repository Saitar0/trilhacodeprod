# Beta 4 — divergência de índices 38/40

## Evidências

`backend/indexes.py` declara 40 índices. O teste histórico `tests/test_integrity_concurrency.py::test_preflight_compound_and_text_index_key_matching` ainda espera 38. A mensagem e coleta reportadas pela Beta 3 identificaram essa expectativa antiga; nenhuma alteração foi feita em `indexes.py` ou no teste.

O commit local `2574bf1b98482b58746c5e7a42b4df0fe07bec93` (`feat(learning): prepare immutable publication read models`) acrescentou à definição dois índices para `track_publications`:

1. `one_track_publication_operation`, índice único em `(track_id, operation_id)` para identidade de operação.
2. `track_publication_recovery_lookup`, índice `(state, lease_until)` para recuperação por estado/lease.

O mesmo commit introduziu o serviço e os testes de publicação imutável. A definição versionada e os testes de `backend/unit_tests/test_immutable_publications.py` referenciam os dois nomes. A diferença é explicada por essas duas entradas, não por uma alteração no harness Beta 4.

## Conclusão e ação futura

A expectativa 38 ficou desatualizada após a expansão intencional para 40. A Beta 4 não alterou o teste nem a lista operacional. Antes da próxima mudança de código, a manutenção deverá confirmar que a suíte histórica deve esperar 40 e revisar se a comparação de índices deve validar nomes/opções em vez de contar uma lista global. A execução dessa suíte completa não foi usada como prova da importação curricular.

## Execução do teste histórico e ressalva de isolamento

O teste-alvo foi executado e falhou exatamente na asserção `40 == 38`. Sua fixture autouse `backend/tests/conftest.py` usa `MONGO_URL_TEST` ou, se ausente, `mongodb://localhost:27017`, cria um banco aleatório `test_*` e aplica migrações. A saída também registra usuários de teste sintéticos e chamadas pela aplicação de teste para login, criação de trilha/nós/relação e publicação de uma trilha sintética antes da asserção. O teardown não reportou erro; o código fecha o cliente e chama `drop_database`, mas a limpeza não foi verificada de forma independente. Esse teste tocou a porta 27017 durante a Beta 4, contrariando a restrição de isolamento; nenhum teste com esse fixture será repetido. O incidente está reportado explicitamente: não é possível atestar a identidade do servidor nem afirmar que fosse operacional, e seu estado posterior não foi consultado.
