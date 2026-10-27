# Homologação de gerações editoriais em MongoDB 7

Este harness exercita a PoC de gerações editoriais em um MongoDB 7 standalone efêmero. Ele não importa dados do currículo, não usa as configurações MongoDB da aplicação e não está conectado às rotas ou ponteiros reais de publicação.

## Execução local

No PowerShell, a partir da raiz do repositório:

    pwsh -File ops/editorial-generations/run-local.ps1

O script executa testes da barreira de contexto e verifica o Docker Engine antes de iniciar qualquer recurso. O preflight recusa overrides DOCKER_*, contextos remotos, qualquer pipe Windows diferente de `npipe:////./pipe/dockerDesktopLinuxEngine` e Engines que não reportem Linux. Cada execução recebe um nome Compose aleatório, usuário root e senha temporários, uma rede interna privada e um filesystem de dados em tmpfs. Não há porta publicada, volume persistente, socket Docker dentro do runner ou conexão ao MongoDB do host.

Se o Docker Engine estiver indisponível, a execução termina antes de iniciar containers. Não tente substituir o alvo por localhost:27017.

## O que o runner faz

1. Confere os marcadores e a identidade exclusiva desta execução.
2. Exige o host Compose mongo, porta 27017, MongoDB 7 e topologia standalone.
3. Recusa variáveis de conexão da aplicação e URI externa.
4. Cria um banco aleatório, confirma que ainda não existe e grava nele um marcador aleatório de propriedade.
5. Cria e verifica os índices PoC antes de criar usuários limitados.
6. Executa primeiro os testes de contrato com fake e depois os testes com conexões PyMongo Async independentes.
7. Remove somente o banco que ainda contém o marcador exato da execução.
8. O script local verifica novamente o contexto Docker e os labels Compose antes de remover containers, rede ou volumes do projeto exclusivo.

O banco não é removido se o marcador estiver ausente ou divergente. O Compose não declara volumes persistentes e remove apenas os recursos do nome de projeto aleatório.

## Identidades MongoDB

* poc_builder: find, insert e update somente nas coleções de gerações em construção e heads experimentais.
* poc_append: somente find e insert nas coleções de chunks e manifestos.
* poc_reader: somente find nas quatro coleções PoC.
* poc_fixture: privilégios limitados às quatro coleções do banco aleatório, usados exclusivamente para simular corrupção fora do protocolo.
* pocroot: identidade temporária de provisionamento, nunca passada aos processos de teste.

Todos os usuários temporários são criados dentro do banco aleatório e desaparecem com a remoção validada desse banco. As credenciais são geradas durante a execução e não são impressas.

A identidade `poc_builder` pode atualizar documentos de geração e head; portanto, as garantias de CAS e estado selado dependem do protocolo confiável da aplicação, e não de uma condição por documento imposta pelos grants do MongoDB. Esta é uma limitação explícita da PoC.

## Suíte coberta

A suíte real testa índices e unicidade, permissões negativas de update/replace/delete, aquisição concorrente, selagem concorrente, CAS do head, replay após perda da resposta, fencing após takeover, chunks atrasados, failpoints de preparação, recuperação, leitura pinada, corrupção simulada com identidade de fixture e projeção pública sem campos privados. Os clientes usam `tz_aware=True`, igual ao cliente canônico em `backend/database.py`; um caso integrado verifica que `lease_until` volta como UTC-aware antes de a PoC compará-lo.

Barreiras/eventos e um relógio controlado determinam os interleavings. O servidor é standalone; os testes demonstram CAS por documento e append-only por autorização MongoDB. Não demonstram atomicidade multidocumento, nem a segurança de leitores de produção.

## CI

O workflow separado editorial-generations-mongodb.yml tem somente workflow_dispatch, contents: read, checkout sem credenciais persistidas, timeout e cleanup delimitado por labels. Ele não consulta secrets do repositório e não contém deploy, publicação, SSH ou execução de código externo. Este workflow foi preparado, mas não foi executado nesta fase.

## Limites conhecidos

* O DTO da PoC continua usando filtros conservadores de campos; isso não substitui uma allowlist versionada por tipo de bloco.
* A suíte valida o protocolo experimental, não a integração futura com os escritores ou leitores atuais.
* A execução integrada só pode ser considerada concluída após os testes passarem contra um servidor MongoDB 7 descartável real.
