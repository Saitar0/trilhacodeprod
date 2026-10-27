---
arquivo_id: "f4-10-2-02-dados-volumes-configuracao-segura-01-teoria"
parent_key: "10.2"
tipo_arquivo: "theory"
assunto: "02_dados_volumes_configuracao_segura"
ordem: 2
itens_origem: ["3. Preserve dados e trate configurações com cuidado"]
---

### 3. Preserve dados e trate configurações com cuidado
Volumes nomeados mantêm dados além da recriação dos containers. Declare-os no nível superior e associe cada volume ao caminho de dados adequado à imagem. `docker compose down` remove containers e rede do projeto, mas preserva volumes nomeados por padrão. `docker compose down --volumes` remove também os volumes gerenciados pelo projeto e pode apagar os dados locais.

Variáveis de ambiente permitem parametrizar nomes de banco, portas e configurações. Um arquivo `.env` pode alimentar interpolação do Compose, mas não deve ser tratado automaticamente como cofre de segredos: não versione credenciais reais. Para recursos sensíveis, use mecanismo de secrets compatível com o ambiente e conceda acesso somente ao serviço que precisa deles. Valores de exemplo neste curso são locais e descartáveis.

Exemplo didático de desenvolvimento para PostgreSQL 18+, Redis e MongoDB:

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_DB: estudo
      POSTGRES_USER: estudo
      POSTGRES_PASSWORD: dev-only
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s

  cache:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

  documentdb:
    image: mongo:8
    profiles: ["document"]
    ports:
      - "127.0.0.1:27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  postgres_data:
  redis_data:
  mongo_data:
```

Este exemplo usa credencial descartável, sem autenticação configurada para MongoDB, e destina-se somente a uma máquina de estudo. O serviço MongoDB só entra no modelo quando o perfil `document` é ativado, por exemplo com `docker compose --profile document up`. Se a aplicação não usa algum serviço, não o mantenha ativo sem necessidade. Para outras versões de PostgreSQL, confira o caminho de volume documentado pela tag.

**Erro comum:** acreditar que publicar portas ou colocar uma senha de exemplo no YAML torna a configuração apropriada para produção.

