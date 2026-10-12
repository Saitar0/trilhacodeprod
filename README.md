# Trilha Code

Aplicação full-stack para gestão de trilhas de aprendizagem, conteúdo, progresso, autenticação e submissões, com backend em FastAPI e frontend em React + TypeScript.

## Visão geral

Este projeto combina:

- Backend em Python com FastAPI
- Banco de dados MongoDB
- Frontend em React + CRA/CRACO + Tailwind
- Autenticação por JWT
- Estrutura de conteúdos, trilhas, progresso e avaliações

## Stack

- Python 3.11+
- FastAPI
- MongoDB Community Edition
- Node.js 18+
- React 19
- TypeScript
- Tailwind CSS

## Estrutura do repositório

- `backend/` — API, rotas, modelos e bootstrap do sistema
- `frontend/` — interface web em React
- `run_local.ps1` — script para iniciar backend e frontend localmente
- `mongo-data/` — dados locais do MongoDB
- `tests/` — testes e scripts de validação

## Pré-requisitos

Antes de iniciar, confirme que o ambiente local possui:

1. Python 3.11 ou superior
2. Node.js 18 ou superior
3. npm
4. MongoDB Community Edition instalado e acessível via comando `mongod`
5. Git

## Configuração rápida

### 1) Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2) Configure as variáveis de ambiente

Copie os arquivos de exemplo para os arquivos reais antes de rodar a aplicação:

```powershell
Copy-Item .\backend\.env.example .\backend\.env
Copy-Item .\frontend\.env.example .\frontend\.env
```

Se estiver no Linux/macOS:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

> Os arquivos `.env` são locais e não devem entrar no Git. O repositório já contém um `.gitignore` seguro para isso.

### 3) Crie o ambiente virtual do backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Inicie o MongoDB

Em um terminal separado:

```powershell
mongod --dbpath "C:\caminho\para\o\repositorio\mongo-data"
```

Exemplo:

```powershell
mongod --dbpath "C:\Users\Joao\Documents\trilhacodeprod\mongo-data"
```

### 5) Inicie o backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 6) Instale e rode o frontend

```powershell
cd frontend
npm install --legacy-peer-deps
npm start
```

Se o projeto já estiver com dependências instaladas, o script abaixo também funciona:

```powershell
cd ..
.\run_local.ps1
```

## Acesso local

Depois de levantar os serviços:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger da API: http://localhost:8000/docs

## Credenciais padrão

As credenciais padrões do ambiente local estão no arquivo `backend/.env` e geralmente são:

- Admin: `admin@trilhacode.dev` / `Admin@123`
- Editor: `editor@trilhacode.dev` / `Editor@123`
- Aluno: `aluno@trilhacode.dev` / `Aluno@123`

> Em produção ou em um repositório compartilhado, troque essas credenciais antes do deploy.

## Scripts úteis

### Windows PowerShell

```powershell
# Inicia tudo em um único passo
.\run_local.ps1
```

## Troubleshooting

### MongoDB não encontrado

Verifique se o binário do MongoDB está no PATH. Se não estiver, instale o MongoDB Community Edition e rode:

```powershell
mongod --dbpath "C:\Users\Joao\Documents\trilhacodeprod\mongo-data"
```

### Erro ao instalar dependências do frontend

Este projeto usa uma stack mais antiga com CRA/CRACO. Se ocorrer problema de peer dependency, use:

```powershell
npm install --legacy-peer-deps
```

Em algumas máquinas também foi necessário instalar explicitamente:

```powershell
npm install @babel/traverse@7.28.0 --legacy-peer-deps --save-dev
```

### Port conflicts

Se a porta 3000 ou 8000 estiver em uso por outro processo, termine o processo conflitante antes de reiniciar:

```powershell
Get-Process node,uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 404/500 na API

Verifique:

- se o MongoDB está rodando
- se o backend foi iniciado com `uvicorn server:app --reload --host 0.0.0.0 --port 8000`
- se o arquivo `.env` foi criado corretamente

## Contribuição

1. Faça o fork do projeto
2. Crie uma branch para sua feature
3. Faça commits claros
4. Abra um Pull Request

## Licença

Adicione uma licença antes de publicar publicamente no GitHub, como MIT, Apache 2.0 ou GPL, conforme a necessidade do projeto.

## Observações finais

Este README foi preparado para facilitar a execução local e o envio para o GitHub com um processo de setup simples e seguro. Para manter o repositório limpo e seguro, mantenha os arquivos de ambiente fora do controle de versão e apenas publique exemplos em `.env.example`.
