# Beta 8 — Resultados de regressão

## Executado

* 74 testes offline passaram: contratos Beta 8, protocolo C8 em memória, inventário/contrato C13/C16, adapter Mongo offline, PoC de gerações e testes C12 que carregam a implementação real de `security.py` com coleções sintéticas.
* 11/11 testes do módulo `test_beta8_security_contracts.py` passaram na execução isolada.
* O harness persistente Beta 8 passou em MongoDB 7 descartável, inclusive privilégios do servidor, revogação após autorização de requisição, CAS/fencing, retries, duas operações concorrentes e promoção sintética concorrente.
* Ruff passou nos cinco módulos/testes Beta 8.
* MyPy passou individualmente nos quatro módulos de contrato/serviço/harness.
* `py_compile` passou nos cinco arquivos Python Beta 8.
* Parser PowerShell e `docker compose config --quiet` passaram com valores sintéticos.

## Não executado

* Suíte pytest completa do backend: não executada; não foi inspecionada em sua totalidade nesta fase e pode conter fixtures persistentes legadas.
* HTTP: nenhum endpoint foi adicionado ou conectado à autoridade Beta 8; não há fluxo HTTP Beta 8 a declarar validado.
* Regressões persistentes históricas C8–C16: não executadas em seus harnesses próprios. A prova B8 foi escrita para consumir MongoDB descartável próprio, mas os harnesses históricos não foram invocados.
* Regressões do frontend e da jornada de aprendizagem: não executadas; nenhum frontend foi alterado.
* MyPy de todo o backend: não executado; somente os quatro módulos novos foram verificados.

## Resultado da preparação

Uma primeira tentativa fechou antes das escritas porque o MongoDB rejeitou as permissões do keyfile montado. A tentativa seguinte revelou expectativas do harness sobre credenciais/coleções, e uma execução completa revelou a forma `sha256:` dos IDs de imagem. As correções ficaram limitadas ao harness Beta 8; cada limpeza foi restringida a labels/IDs exatos e verificou a propriedade. A última execução repetiu os cenários e removeu seus recursos.
