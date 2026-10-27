---
arquivo_id: "f4-10-1-01-imagens-contexto-build-01-teoria"
parent_key: "10.1"
tipo_arquivo: "theory"
assunto: "01_imagens_contexto_build"
ordem: 1
itens_origem: ["1. Diferencie imagem, container e processo", "2. Construa imagens com contexto controlado"]
---

## Teoria

### 1. Diferencie imagem, container e processo
Imagem é um artefato construído em camadas que reúne arquivos e metadados para iniciar uma aplicação. Container é uma instância em execução criada a partir da imagem, com configuração própria de processo, rede e armazenamento. Ele compartilha o kernel do sistema hospedeiro e não é uma máquina virtual completa.

A imagem pode ser referenciada por tag, como `postgres:18`, ou por digest. Tags são nomes convenientes e podem apontar para conteúdo atualizado; um digest identifica um conteúdo específico. Para aprender, tags explícitas ajudam a reconhecer a versão principal. Para builds que precisam de repetibilidade rigorosa, registre e revise o digest de forma deliberada.

O container tem uma camada gravável própria. Arquivos criados ali podem desaparecer quando ele é removido. Não trate essa camada como armazenamento persistente.

**Erro comum:** supor que remover e recriar um container preserva tudo o que foi gravado dentro dele.

### 2. Construa imagens com contexto controlado
O Dockerfile descreve como montar a imagem: imagem base, diretório de trabalho, dependências, arquivos copiados e comando de inicialização. O contexto é o conjunto de arquivos disponibilizado ao builder; o argumento final do comando de build costuma ser `.`, o diretório atual. COPY só alcança arquivos presentes nesse contexto.

Exemplo de aplicação Node.js:

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["node", "consulta.js"]
```

Esse exemplo exige `package.json`, `package-lock.json` e `consulta.js` dentro do contexto. Copiar primeiro os arquivos de dependências permite aproveitar o cache de `npm ci` quando apenas o código da aplicação muda. `npm ci` é apropriado quando o projeto mantém um lockfile coerente com package.json.

Use `.dockerignore` para excluir arquivos que não precisam ser enviados ao builder, como `node_modules`, `.git`, arquivos locais de ambiente e artefatos temporários. Segredos não devem ser copiados para a imagem nem enviados no contexto. A imagem precisa receber configuração em tempo de execução por um mecanismo adequado ao ambiente.

**Erro comum:** executar o build na pasta errada ou enviar o repositório inteiro, inclusive credenciais e arquivos locais.

