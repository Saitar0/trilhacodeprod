# Beta 5 — política fail-closed para MongoDB de testes

## Ocorrência anterior e limite desta fase

A Beta 4 registrou um fixture persistente que podia recorrer a `localhost:27017` quando `MONGO_URL_TEST` não era informado. O servidor então alcançado não teve sua identidade comprovada e a limpeza não foi verificada independentemente. Não há evidência suficiente para afirmar dano, nem para afirmar que o banco era descartável. A Beta 5 não se conectou a essa porta, não investigou o estado posterior e não executou limpeza retroativa.

## Política aplicada

Os testes persistentes de `backend/tests/` exigem `--beta5-isolated-mongo`. Sem a opção, o hook de coleta encerra antes de importar os módulos de teste ou a aplicação. `MONGO_URL_TEST` não é usado como fallback. Se o opt-in for informado, o `pytest_sessionstart` valida URI e identidade Docker antes de importar `database`, `server`, migrações ou seeds. A URI operacional `MONGO_URL` só é substituída depois dessa validação.

O alvo precisa reunir todas as condições abaixo:

* URI explícita `mongodb://` em `127.0.0.1`, porta efêmera não igual a 27017, banco `beta5_<UUID>` e parâmetros únicos limitados a `authSource=admin` e `directConnection=true`.
* Usuário derivado do UUID da execução e senha exclusiva gerada pelo harness.
* IDs Docker completos do contêiner e da rede, labels Beta 5 com UUID e token de propriedade aleatório correspondente.
* Imagem local `mongo:7.0.43`, servidor MongoDB 7, WiredTiger e topologia standalone.
* Uma bridge de nome derivado da execução, contendo somente o contêiner Beta 5; binding de porta exclusivamente no loopback.
* Nenhum mount persistente; `/data/db` e `/data/configdb` são tmpfs.
* Banco inexistente antes do primeiro uso ou marcador `_beta5_test_owner` correspondente a UUID, token, contêiner, rede e nome do banco.

O harness provisiona rede, contêiner, credenciais e banco. Não lê arquivos `.env`, não imprime URI/credenciais, e revalida propriedade antes de remover os recursos. O fixture legado também valida o marcador antes da limpeza e preserva esse marcador para a verificação final do harness. Os helpers de alvo não abrem conexão durante importação.

O serviço experimental de staging exige nome de banco ligado ao UUID e confere o marcador/token antes de criar índices ou gravar. Isso é uma defesa adicional do staging Beta 5, não substitui a validação Docker do harness.

## Provas executadas

Testes offline rejeitam URI ausente/vazia/malformada, localhost e porta 27017, banco não exclusivo, credenciais que não derivam do UUID, parâmetros extras, IDs incompletos, labels divergentes, credenciais incompatíveis, binding não loopback, volumes persistentes, rede compartilhada e marcador ausente/divergente. Doubles verificam que a fábrica do cliente não é chamada antes da validação.

`pytest tests --collect-only -q` sem opt-in encerrou com erro de uso esperado: módulos persistentes bloqueados antes da importação. Não ocorreu conexão MongoDB nessa prova.

O harness Beta 5 provisionou MongoDB 7 descartável e verificou URI, Docker, versão, WiredTiger, marcador e armazenamento temporário antes da prova persistente; ao final, verificou novamente propriedade e removeu apenas os recursos daquela execução.

## Limites residuais

A rede Docker é dedicada e sem compartilhamento, mas não é declarada `--internal`: Docker Desktop rejeitou publicação loopback ao combinar rede interna e porta publicada. O serviço escuta somente no binding loopback e a URI é validada contra o inspect; não foi demonstrado bloqueio de saída de rede do contêiner. O harness não protege comandos manuais que contornem pytest, nem substitui ACL de banco de produção. Nenhuma instância preexistente foi inspecionada ou removida.
