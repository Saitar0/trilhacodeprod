# Trilha Code — Diagnóstico do ambiente de desenvolvimento

Data da verificação: 16/10/2026  
Escopo: diagnóstico somente leitura. Nenhum serviço foi iniciado, dependência instalada, banco acessado, nem configuração ou dado alterado.

## Resumo

Há três bloqueios independentes:

1. **Rede/DNS:** os três hosts solicitados falham na resolução de nome. `npm audit` retorna `ENOTFOUND registry.npmjs.org`; HTTPS nem chega à etapa TLS. Não há proxy configurado nas variáveis desta sessão ou no npm. A causa subjacente (DNS do Windows, VPN/rede/firewall ou restrição do terminal) ainda precisa ser identificada.
2. **Docker:** Docker Desktop/CLI e os contextos estão presentes, mas a conexão aos named pipes do engine é negada. Os contextos `desktop-linux` e `default` falham com `permission denied`; não é evidência de contexto incorreto. O estado do Desktop e a integração WSL não puderam ser confirmados porque a consulta de processos/serviços do Windows foi bloqueada.
3. **Python:** o `.venv` é estruturalmente funcional, porém usa Python 3.13.15, não 3.11; `pip-audit` não está instalado. A instalação isolada de `requirements-dev.txt` não pode ser validada sem Python 3.11 e acesso ao PyPI.

## 1. Docker

| Comando | Resultado observado |
|---|---|
| `docker version` | Cliente 29.8.2/API 1.56 disponível. A seção Server retorna `permission denied while trying to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`. |
| `docker info` | Mostra informações do cliente/plugins e termina com o mesmo `permission denied` ao consultar o engine. |
| `docker context ls` | Contexto atual `desktop-linux` aponta para `npipe:////./pipe/dockerDesktopLinuxEngine`; `default` aponta para `npipe:////./pipe/docker_engine`. |
| `docker ps` | Falha com `permission denied` no pipe `dockerDesktopLinuxEngine`. |
| `docker --context default ps` | Também falha com `permission denied`, agora no pipe `docker_engine`. |

O caminho do pipe do Desktop existe, mas isso não prova que o daemon está saudável. A consulta de processos não listou processos Docker e a consulta do serviço retornou: `Cannot open Service Control Manager on computer '.'. This operation might require other privileges.` Por essa restrição, não é possível distinguir com certeza Docker Desktop desligado de engine ativo inacessível ao usuário/sessão. A falha nos dois contextos indica que trocar de contexto não resolve o problema observado. Não foi confirmada uma causa de permissões específica; o erro de acesso ao pipe é confirmado.

O comando de listagem WSL não forneceu um inventário utilizável nesta sessão (erro de acesso CIM). Assim, integração WSL/Linux engine permanece hipótese, não causa confirmada.

**Correções recomendadas:**

1. No Windows, abrir Docker Desktop pelo menu Iniciar e aguardar o estado “Running”. Em Settings, confirmar que o Linux engine está habilitado e, em Resources > WSL Integration, habilitar a distribuição usada pelo projeto, se aplicável.
2. Em um terminal PowerShell novo, executar `wsl --status`, `wsl --list --verbose` e repetir `docker context ls`, `docker version` e `docker ps`.
3. Se continuar `permission denied` com o Desktop em execução, reiniciar o Docker Desktop pela interface e abrir um novo terminal. Se persistir, pedir ao administrador do Windows para revisar a permissão de acesso do usuário ao Docker Desktop/named pipe. Não fazer reset, prune, reinstalação ou remoção de volumes.

**Risco/precaução:** o `compose.yaml` do projeto define `mongo:7` com o volume persistente nomeado `mongo_data`. Não usar `docker compose up` como atalho para obter Mongo descartável sem revisar a persistência; o serviço Compose também inicia a aplicação. O diagnóstico não executou comandos que alterem containers ou volumes.

## 2. MongoDB

- Porta local 27017: nenhuma conexão TCP aceita em `127.0.0.1:27017`; `Test-NetConnection` retornou `TcpTestSucceeded: False`. Nenhum processo `mongod`, `mongosh` ou `mongo` foi listado.
- Container MongoDB: **não determinável**, porque o daemon Docker não permite listar containers. `docker ps` foi negado antes de retornar uma lista.
- Configuração do projeto: `compose.yaml` oferece MongoDB 7 e o CI declara MongoDB 7 como serviço temporário. A configuração Compose usa volume nomeado `mongo_data` e não publica a porta Mongo no host. A suíte backend usa `MONGO_URL_TEST` (padrão `mongodb://localhost:27017`) e cria um banco `test_<uuid>`; o fixture recusa nomes fora de `test_` e remove somente o banco temporário daquela execução.
- Mongo descartável em porta alternativa: tecnicamente seguro após recuperar Docker, usando porta loopback livre, por exemplo 27117, sem volume nomeado e com container removível. **Não foi iniciado.** Primeiro confirmar que 27117 não está em uso. Essa abordagem não toca o banco persistido do Compose nem bancos locais em 27017.

Comandos sugeridos, somente depois de Docker funcionar e de confirmar a porta alternativa livre:

```powershell
Test-NetConnection 127.0.0.1 -Port 27117
docker run --rm --name trilhacode-mongo-test -p 127.0.0.1:27117:27017 mongo:7
```

Em outro terminal, executar os testes apontando explicitamente para a porta alternativa:

```powershell
$env:MONGO_URL_TEST = 'mongodb://127.0.0.1:27117'
Set-Location backend
python -m pytest
```

O container usa sua camada temporária, não um volume de dados. Ao encerrá-lo, os dados desse container serão descartados. Não executar a parte de inicialização nesta etapa; estes comandos são uma recomendação futura.

## 3. DNS, registries e proxy

| Destino | Resolução/HTTPS observados |
|---|---|
| `registry.npmjs.org` | `curl`: `(6) Could not resolve host`. `npm audit --json`: `getaddrinfo ENOTFOUND registry.npmjs.org`; endpoint de auditoria não foi alcançado. |
| `pypi.org` | `curl`: `(6) Could not resolve host`. |
| `github.com` | `curl`: `(6) Could not resolve host`. |

As consultas DNS via `Resolve-DnsName` retornaram `Acesso negado` nesta sessão. O `Test-NetConnection` não conseguiu resolver os destinos e, portanto, não testou efetivamente TCP/443. As falhas acontecem antes de conexão TLS: não há evidência de erro de certificado/TLS nem resposta HTTP de firewall/registry. A indisponibilidade de rede/DNS para este terminal é confirmada; a origem da falha não é.

Proxy: não havia variáveis de ambiente de proxy (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`) na sessão; `npm config get proxy` e `npm config get https-proxy` retornaram `null`. Não foi encontrado `.vscode/settings.json` no workspace nem configuração `http.proxy` nas configurações de usuário que estavam acessíveis. Isso não exclui política de proxy da VPN/rede ou configuração do Windows fora do escopo acessível. Assim, não há evidência de que o terminal esteja herdando um proxy inadequado.

**Correções recomendadas:**

1. No Windows, confirmar conexão de rede e VPN corporativa (se exigida) e pedir à equipe de rede que valide DNS para os três domínios. Se a rede exigir proxy, obter a URL/credenciais do proxy com o administrador; não inventar valores nem gravar credenciais em arquivos do projeto.
2. Abrir um PowerShell novo fora do VS Code e comparar `Resolve-DnsName registry.npmjs.org`, `Resolve-DnsName pypi.org`, `Resolve-DnsName github.com` e `curl.exe -I https://registry.npmjs.org/`. Repetir no terminal integrado. Se só falhar dentro do VS Code, revisar Settings > Proxy e reiniciar o VS Code após corrigir a origem.
3. Com DNS recuperado, verificar `npm ping` e `npm audit --json` no diretório `frontend`; para pip, verificar acesso a `https://pypi.org/simple/` antes de instalar ferramentas.

**Interpretação por camada:** DNS falha; proxy inadequado não foi evidenciado; firewall não pode ser separado de DNS/rede com as conexões atuais; TLS não foi iniciado; indisponibilidade do registry não foi demonstrada (o hostname sequer resolveu).

## 4. Python

- Python encontrado: Python 3.13.15 (64-bit) em `python`; `py -0p` não lista instalações gerenciadas e `py -3.11 --version` retorna `No installed Python found!`.
- `.venv`: encontrado em `backend/.venv`. `pyvenv.cfg` aponta para Python 3.13.15 e `backend/.venv/Scripts/python.exe` inicia e importa pip 26.2.1. É um ambiente isolado funcional, mas não corresponde à matriz de produção.
- `pip-audit`: ausente no Python global e no `.venv`; `python -m pip_audit --version` retorna `No module named pip_audit`.
- Produção: `backend/Dockerfile.prod` usa `python:3.11-slim`. A versão instalada local não valida compatibilidade de runtime Python 3.11.
- Dependências: `requirements-dev.txt` inclui `-r requirements.txt` e `pip-audit>=2.9,<3`. Não foi feita instalação seca nem real: Python 3.11 falta e o acesso ao PyPI falha por DNS. Portanto, compatibilidade/resolução de todos os pins (incluindo a dependência via URL direta no requirements) permanece sem validação.

**Correção recomendada:** instalar Python 3.11 pelo instalador oficial do Windows (marcar a opção de launcher `py`, se oferecida), abrir novo PowerShell e confirmar `py -3.11 --version`. Criar um ambiente paralelo para preservar o `.venv` 3.13 atual e instalar nele, após corrigir DNS:

```powershell
py -3.11 -m venv backend\.venv311
backend\.venv311\Scripts\python.exe -m pip install --upgrade pip
backend\.venv311\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
backend\.venv311\Scripts\python.exe -m pip_audit --version
backend\.venv311\Scripts\python.exe -m pip_audit -r backend\requirements.prod.txt -f json
```

A instalação usa a árvore de desenvolvimento em ambiente isolado e requer rede para PyPI e para a URL direta listada em `requirements.txt`. Se houver falha de resolução, registrar a mensagem sem alterar os pins.

## 5. Ordem de prioridade e intervenção Windows

1. **Resolver rede/DNS no Windows/terminal.** É o bloqueio comum que impede a auditoria npm e a instalação do `pip-audit`/requirements. Confirmar se fora do VS Code também falha; escalar ao administrador de rede se persistir.
2. **Restabelecer acesso ao Docker Desktop.** Abrir e aguardar Docker Desktop, conferir Linux engine/WSL Integration e revisar permissões do usuário se o named pipe continuar negando acesso. É necessária intervenção na interface/serviços do Windows, não no código do projeto.
3. **Instalar Python 3.11 lado a lado e criar `.venv311`.** Não remover o Python 3.13 ou o `.venv` existente; validar os requisitos só depois de recuperar a rede.
4. **Só então auditar e validar:** `npm audit --json`; `pip-audit` em requirements de produção; MongoDB 7 temporário na porta alternativa; testes backend apontando para `MONGO_URL_TEST`.

Não foram confirmados proxy incorreto, bloqueio TLS, indisponibilidade do registry, contexto Docker errado, Mongo em container existente, nem falha de compatibilidade de dependência. São questões ainda não decidíveis enquanto os acessos necessários estiverem bloqueados.
