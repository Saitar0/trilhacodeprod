# Trilha Code — Fase 2A.1: Modularização de `core.py`

## 1. Responsabilidades identificadas

Antes da mudança, `backend/core.py` reunia estas responsabilidades:

- Cliente MongoDB Motor compartilhado e seleção do banco.
- Hash de senhas, criação/validação de JWT e resolução do usuário autenticado.
- Matriz de permissões por papel, dependência `require()` e classificação de staff.
- Conversão de valores para `ObjectId` e serialização dos documentos para a API.
- Relógio UTC e constantes de estado, papel e hierarquia.
- Registro de ações na coleção `edit_history`.

O mapa de dependências consultado foi `PROJECT_AUDIT.md` (seções 4 e 12) e o
mapa de conexões do roadmap. A auditoria do repositório descreve o backend como
monólito modular, sem camada formal de repositórios, com Motor centralizado em
`core.py` e regras compartilhadas entre `core.py`, `learning.py` e `integrity.py`.

Foram encontrados 28 arquivos Python consumidores diretos de `core.py`, entre
rotas, serviços, schemas, inicialização, migrações e testes. Não foram
encontrados monkeypatches de `core` nem substituições dinâmicas desses objetos.
As fixtures, porém, importavam `client` e `db`, fechavam o cliente e removiam
apenas um banco cujo nome gerado começa com `test_`.

Não há ciclo de imports partindo de `core.py`. O grafo de domínio também não
apresenta ciclo entre os módulos extraídos: `permissions` depende de `security`,
que depende de `database`, `constants`, `core_utils` e `serialization`; `audit`
depende apenas de `database` e `core_utils`. Os módulos novos não importam
rotas, serviços, `learning` ou `integrity`.

## 2. Arquitetura anterior e nova

Antes, todos os consumidores apontavam para um único módulo que implementava
conexão, segurança, permissões, serialização, constantes, datas e auditoria.

Agora, a implementação está distribuída nestes módulos:

| Módulo | Responsabilidade |
| --- | --- |
| `backend/database.py` | Singleton Motor `client` e banco `db` |
| `backend/security.py` | Senhas, JWT e usuário autenticado |
| `backend/permissions.py` | Checagem de permissão e dependências FastAPI |
| `backend/serialization.py` | ObjectId e serialização de documentos |
| `backend/constants.py` | Papéis, permissões, estados e hierarquia |
| `backend/core_utils.py` | Horário UTC |
| `backend/audit.py` | Escrita do histórico de edição |
| `backend/core.py` | Fachada temporária que reexporta os nomes existentes |

`database.py` instancia o cliente uma única vez. `core.client` e
`database.client` são o mesmo objeto; a seleção de banco e o fechamento no
shutdown continuam ligados a essa instância. Motor e o formato de persistência
permanecem inalterados.

## 3. Arquivos criados e alterados

Criados:

- `backend/audit.py`
- `backend/constants.py`
- `backend/core_utils.py`
- `backend/database.py`
- `backend/permissions.py`
- `backend/security.py`
- `backend/serialization.py`
- `backend/tests/test_core_modules.py`
- `PHASE2A1_REFACTOR.md`

Alterados: `backend/core.py`, consumidores em rotas, serviços, schemas,
migrações, inicialização e seed, além de `backend/tests/conftest.py`. Em
`integrity.py` e `learning.py` foram alterados somente os imports necessários.
Nenhuma regra dessas áreas foi modificada. `PHASE2A1_REFACTOR.md` foi adicionado
na raiz.

## 4. Imports migrados e compatibilidade

Os consumidores passaram a importar cada nome do módulo da sua responsabilidade.
Não há mais imports de implementação com `from core import ...`; o teste de
identidade importa explicitamente a fachada `core`.

`core.py` segue reexportando os contratos antes utilizados, inclusive `client`,
`db`, tokens, autenticação, autorização, serialização, datas, constantes e
auditoria. A fixture usa agora os mesmos objetos via `database.py` e
`security.py`; o ciclo de vida de criação/encerramento segue no cliente
compartilhado. Não foram alteradas rotas, payloads ou matriz de permissões.

## 5. Testes e verificações

Executado com Python **3.11.9** do ambiente `backend/.venv311`:

- Compilação de 52 arquivos Python: **passou**.
- `pip check`: **passou**, sem dependências quebradas.
- `tests/test_core_modules.py`, sem carregar a fixture global do Mongo:
  **5 passaram**. Cobertura: identidade do cliente/banco, JWT, senhas,
  autorização dos três papéis, conversão de ObjectId e serialização.
- `ruff check`: **não passou**. Restam duas correções de import/compatibilidade
  em `backend/core.py` e `backend/routes_submissions.py`. A tentativa de gravar
  esses dois arquivos foi recusada pelo Windows por estarem abertos por uma
  seção mapeada. Os outros arquivos foram organizados com isort.
- Os **47 testes de backend** não foram executados. `MONGO_URL_TEST` não está
  configurado e o Docker daemon não está acessível. A fixture de integração faz
  `ping` e remove o banco descartável no encerramento; por isso a suíte não foi
  apontada para o Mongo padrão nem para dados existentes.

### Execução externa no PowerShell

Com Docker Desktop ativo, estes comandos usam um container Mongo descartável e
uma porta própria. Execute a partir da raiz do repositório:

```powershell
Set-Location .\backend
$mongoContainer = 'trilhacode-phase2a1-mongo'
docker run --rm -d --name $mongoContainer -p 27018:27017 mongo:7
try {
    $env:MONGO_URL_TEST = 'mongodb://127.0.0.1:27018'
    .\.venv311\Scripts\python.exe -m ruff check . --exclude .venv,.venv311,.pytest_cache,.ruff_cache
    .\.venv311\Scripts\python.exe -m pip check
    .\.venv311\Scripts\python.exe -c "from pathlib import Path; import py_compile; files=[p for p in Path('.').rglob('*.py') if not any(part in {'.venv','.venv311','.pytest_cache','.ruff_cache','__pycache__'} for part in p.parts)]; [py_compile.compile(str(p), doraise=True) for p in files]; print(f'Compiled {len(files)} Python files')"
    .\.venv311\Scripts\python.exe -m pytest -q
} finally {
    docker stop $mongoContainer | Out-Null
    Remove-Item Env:MONGO_URL_TEST -ErrorAction SilentlyContinue
}
```

O container não reutiliza `mongo-data/`. A fixture cria um banco aleatório com
prefixo `test_` e remove somente esse banco.

## 6. Riscos e possíveis regressões

- Chamadas antigas `from core import nome` continuam disponíveis. Código que
  substitua dinamicamente `core.db` para afetar dependentes deixaria de alterar
  as referências importadas em cada módulo; a auditoria não encontrou esse
  padrão no projeto.
- O cliente Motor inicia ao importar `database.py`, como ocorria quando
  `core.py` era importado. O singleton e o encerramento continuam preservados.
- A verificação de integração ainda precisa rodar contra o container Mongo
  descartável antes de considerar a etapa totalmente homologada.
- O `ruff check` requer revisão após liberar os dois arquivos que o Windows
  manteve mapeados. O achado em `core.py` refere-se a uma reexportação privada
  mantida para compatibilidade; o achado em `routes_submissions.py` é somente
  organização de imports.

## 7. Pendências para a Fase 2A.2

- Executar `ruff check` após liberar `core.py` e `routes_submissions.py` e
  corrigir os dois achados.
- Rodar os 47 testes originais com o container descartável e registrar o
  resultado integral.
- Decidir quando retirar a fachada `core.py`, após confirmar que não há
  consumidores externos ao repositório.
- Avaliar, em etapa própria, injeção explícita do cliente/banco nos pontos de
  inicialização e teste, sem alterar o ciclo de vida nesta fase.
