# Beta 8.4 — frontend e navegador

Nenhum arquivo de frontend foi alterado. As verificações de regressão executadas em `frontend/` foram:

* TypeScript typecheck: **PASS**.
* ESLint: **PASS**.
* Vitest: **9 arquivos, 29 testes aprovados**.
* Build: **PASS**; permanece o aviso existente de chunk principal acima de 500 kB (506,05 kB minificado).

## Playwright

**NOT_RUN.** A composição descartável Beta 8.4 contém API, autoridade e MongoDB, mas não provisiona frontend, identidade de prévia curricular nem o lote Beta 7.1/7.2 necessário para a jornada das dez unidades. Não foi usado serviço local, dado operacional ou outra worktree como substituto. Portanto, esta fase não declara regressão browser/E2E da jornada curricular real.

O comportamento da aplicação de aprendizagem não foi alterado nesta fase; os testes frontend existentes passaram, mas isso não equivale à jornada Playwright com a autoridade separada.
