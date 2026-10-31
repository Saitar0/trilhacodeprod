# Beta 3 — recuperação do ambiente de testes

## Ambiente Python isolado

Foi criado o venv exclusivo `C:\Users\Joao\.codex\tmp\trilhacode-beta3-venv`, com Python `3.11.9`. As dependências vieram de `backend/requirements-dev.txt` e `backend/requirements.txt` usando PyPI público; não houve alteração do Python global, requirements do projeto ou outro venv. Versões observadas: `httpx 0.28.1`, `pytest 9.1.1`, `pydantic 2.13.5`, `pymongo 4.18.2`, `ruff 0.17.3`, `mypy 2.4.0`.

`httpx==0.28.1` está declarado em `requirements-dev.txt`. O bloqueio Beta 2 era do ambiente Python anterior, não uma dependência ausente do manifesto atual.

## Coleta e execução

| Comando/escopo | Resultado |
|---|---|
| `python -m pytest --collect-only -q` no backend, com `MONGO_URL_TEST` somente em loopback | 131 testes coletados |
| Suíte padrão `backend/tests`, conectada somente ao MongoDB descartável Beta 3 | 130 passaram; 1 falhou por expectativa estática de quantidade de índices |
| `python -m pytest unit_tests -q` | 277 passaram, 36 skipped, 26 subtests passaram |
| `unit_tests/test_snapshot_safety.py` | 6 passaram |
| `unit_tests/test_beta_curriculum_fidelity.py` | 8 passaram |
| `integration_tests/test_beta_import_recovery.py` | 6 passaram em MongoDB 7 descartável |
| Ruff nos quatro arquivos Python Beta 3 | passou |
| Mypy no módulo Pydantic de fidelidade | passou; a invocação conjunta dos quatro arquivos encontrou nomes de módulo duplicados pelo `sys.path` de testes e não foi usada como aprovação |
| Compilação sintática | passou nos quatro arquivos Beta 3 |

Falha da suíte padrão: `tests/test_integrity_concurrency.py::test_preflight_compound_and_text_index_key_matching` espera `len(INDEXES)==38`, mas a definição versionada contém 40. Nenhum teste/código histórico foi alterado para mascarar a diferença.

Na primeira execução `unit_tests`, seis testes falharam por workflows e `ops/g2` ausentes no sparse-checkout. Materializei apenas `.github/workflows` e `ops/g2` para leitura estática. A repetição passou; nenhum workflow ou script foi executado e nenhum serviço externo acessado.

Uma tentativa de teste persistente antes de ajustar a rede Docker falhou na conexão do host, antes de inserir marcador ou dados. A rede `internal` impediu o encaminhamento de porta neste host. A rede exclusiva foi então substituída por bridge sem masquerade, mantendo a publicação loopback e sem egress NAT; as seis provas persistentes passaram.

## Regressões e limites

A suíte offline `unit_tests` inclui contratos das fases C1–C16, Beta 1/2, snapshots, atividades e gerações presentes neste checkout. Os 36 skips permanecem skips; não se declara execução deles. Testes persistentes de outras fases não foram chamados nem seus recursos reutilizados. A suíte backend padrão teve um caso falho relatado acima.

Mypy inicialmente identificou um literal de tipo de relação inferido como `str`; o módulo experimental foi corrigido com mapa explícito e a análise direcionada passou. Os resultados desta tabela não afirmam aprovação de endpoint, frontend, publicação ou runtime operacional.
