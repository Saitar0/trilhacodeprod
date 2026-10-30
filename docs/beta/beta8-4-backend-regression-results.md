# Beta 8.4 — regressões backend

## Testes offline seguros

Executados no estágio de build da imagem, sem rede, em processos pytest separados para preservar o contrato de importação inerte:

* `test_beta8_1_runtime_security.py`: **4 passed**.
* 13 arquivos direcionados de RPC, B8.4, writers, contratos, IAM, protocolo C8, privacidade/aprendizagem, progresso, sessões, política de banco, prévia e isolamento: **94 passed, 4 skipped**.
* Total: **98 passed, 4 skipped**. Os testes que dependiam das fontes curriculares Beta 4/Beta 5 não montadas em modo somente leitura permanecem `NOT_VERIFIED`; nenhum skip foi promovido a evidência funcional.

O conjunto não representa a suíte completa do backend. Suítes persistentes históricas sem gate fail-closed não foram executadas contra destinos desconhecidos.

## Testes persistentes e HTTP

`ops/beta8-4-security/run-local.ps1` terminou com sucesso e removeu recursos próprios. Além do harness persistente da Beta 8.3, os marcadores B8.4 passaram para ataques de RPC, revogação pré-commit em W-07 PUT/POST e W-05 PUT, interleaving de grant e commit em transação, reinícios reais `before_commit`/`after_commit` e recuperação de staging após restart.

Verificações observadas:

* API/autoridade em contêineres e PIDs diferentes; usuários Mongo diferentes.
* Escrita editorial direta pela identidade API negada pelo próprio MongoDB.
* W-07 PUT, W-07 POST e W-05 PUT; CAS concorrente, replay, revogação, autorização e auditoria.
* Staging Beta 5 via bridge, retry, concorrência, integridade e geração persistida.
* Três reinícios reais da autoridade com PID diferente e reconciliação durável.
* Edição editorial entre duas transições sintéticas: revisão do conteúdo e sequência CAS do ponteiro avançaram independentemente; pai/revisão da geração foram conferidos contra a revisão editorial.
* Propriedade e cleanup Docker verificados pelo run id; nenhuma porta publicada ou volume de dados persistente.

## Ferramentas

* Ruff nos arquivos Python alterados/selecionados: **PASS**.
* MyPy direcionado aos seis módulos/arquivos de protocolo, serviços, servidor e integração: **Success, no issues found**.
* `py_compile` nos módulos/testes alterados: **PASS**.
* `git diff --check`: **PASS**.
* Compose/guard de Docker: **PASS** no harness.
* Testes históricos completos C8–C16/Beta 5–8.3: **NOT_RUN** como conjunto completo; apenas os arquivos seguros acima e a integração real B8.3/B8.4 foram executados.
