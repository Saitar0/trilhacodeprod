---
arquivo_id: "f4-10-2-03-prontidao-operacao-diagnostico-01-teoria"
parent_key: "10.2"
tipo_arquivo: "theory"
assunto: "03_prontidao_operacao_diagnostico"
ordem: 3
itens_origem: ["4. Separe ordem de inicialização e prontidão", "5. Opere e diagnostique o projeto"]
---

### 4. Separe ordem de inicialização e prontidão
`depends_on` controla a ordem de criação/inicialização, mas sua forma curta não espera que a aplicação dependente esteja pronta para aceitar conexões. Um serviço pode estar iniciado e ainda estar inicializando o banco. Configure um healthcheck para verificar uma condição útil e, quando apropriado, use a condição `service_healthy` na dependência.

```yaml
  api:
    build: .
    environment:
      DATABASE_HOST: db
      DATABASE_PORT: "5432"
    depends_on:
      db:
        condition: service_healthy
```

Mesmo com healthcheck, a aplicação deve tratar interrupções e reconectar: o banco pode reiniciar depois da inicialização da API, e uma atualização pode recriar um container. Uma verificação de saúde indica uma condição definida; não prova que toda consulta futura terá sucesso.

**Erro comum:** usar `depends_on` curto como garantia de que o banco já aceita consultas.

### 5. Opere e diagnostique o projeto
Comandos usuais:

```sh
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs -f db
docker compose exec db psql -U estudo -d estudo
docker compose down
```

`up --build` constrói serviços que têm configuração de build e inicia o conjunto; `-d` executa em segundo plano. `ps` mostra estado e saúde reportada; `logs` ajuda a localizar falhas de inicialização; `exec` executa um comando em um container em execução. Antes de apagar dados, identifique o projeto, os volumes associados e o conteúdo que será removido.

Compose organiza ambientes locais e cenários simples. Ele não oferece automaticamente alta disponibilidade, backups, gestão completa de segredos, monitoramento ou estratégia de produção. Documente pré-requisitos, portas, serviços opcionais, dados descartáveis e o procedimento de limpeza.

**Checklist de revisão:**
- O arquivo descreve apenas serviços necessários ao cenário?
- Os serviços usam nomes DNS e portas internas para comunicação entre containers?
- Só as portas necessárias estão publicadas para o host?
- Os volumes têm caminho correto e política de descarte clara?
- Dependências estão prontas antes de a aplicação tentar usá-las?
- Logs e estado permitem diagnosticar falhas?
- Nenhum segredo real está versionado?

