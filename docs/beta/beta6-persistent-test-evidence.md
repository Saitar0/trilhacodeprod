# Beta 6 — evidência de testes persistentes

## Política e procedimento

Os testes de `backend/tests/` permanecem opt-in, sem fallback `MONGO_URL_TEST` ou `localhost:27017`. O provisionador Beta 6 usa identificadores e credenciais por execução, labels de ownership, banco exclusivo, tmpfs, imagem MongoDB 7.0.43 e rede Docker `--internal`; a identidade/port binding/owner são verificados antes de criar o cliente Mongo. A rede interna é requisito Beta 6. A coleta dos testes persistentes exige exatamente um opt-in da fase.

O runner `backend/test_support/run_beta6_pytest.py` abre o harness, passa o alvo gerado ao pytest filho e só remove contêiner/rede com labels, IDs e token da execução conferidos. Não houve tentativa de conectar ao antigo endereço localhost:27017, nenhuma investigação nem limpeza retroativa.

## Resultado desta fase

O Docker Desktop não publicou `NetworkSettings.Ports` para a porta solicitada, apesar do `HostConfig.PortBindings` conter o binding loopback reservado. O verificador exigiu ambos e parou antes de construir o cliente Mongo. O harness removeu somente os recursos Beta 6 identificados e próprios da tentativa. A listagem posterior de recursos deve ser confirmada antes do commit.

Resultado: **persistência, teste HTTP Beta 6 e E2E = NOT RUN/BLOCKED**, não falha funcional da aplicação. A política de isolamento e o encerramento por ausência da prova foram preservados. Não reduzir o requisito de rede interna, não usar porta 27017 e não alterar o fixture para contornar o bloqueio.

## Cobertura efetivamente executada

* Contratos unitários de política de banco Beta 5/Beta 6 e projeções Beta 6: status final a registrar após executar com venv exclusivo.
* Compilação sintática Python: aprovada após as mudanças atuais.
* Frontend: typecheck, 29 testes em 9 arquivos e lint aprovados; build de produção já foi executado durante esta fase, com aviso de chunk de entrada acima de 500 kB.
* Integração Mongo/HTTP, autenticação ponta a ponta, persistência, leitor no banco, recuperação e E2E browser: não executados.

Os resultados dos testes offline não demonstram ACL operacional, nem conexão real de browser com API.
