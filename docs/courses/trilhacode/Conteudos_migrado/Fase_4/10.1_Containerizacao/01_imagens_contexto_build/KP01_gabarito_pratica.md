---
arquivo_id: "f4-10-1-01-imagens-contexto-build-kp01-gabarito-pratica"
parent_key: "10.1"
tipo_arquivo: "answer_key_pratica"
assunto: "01_imagens_contexto_build"
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["node", "consulta.js"]
```
Exemplo de .dockerignore:
```
node_modules
.git
.env
*.log
```
Construa na raiz do projeto com `docker build -t consulta:dev .`. O ponto indica que a raiz do projeto é o contexto. Manter os manifestos antes do restante do código evita reinstalar dependências quando só o código muda.

