---
arquivo_id: "f7-32-2-04-rollback-schema-dados-01-teoria-md"
parent_key: "32.2"
tipo_arquivo: "theory"
assunto: "04_rollback_schema_dados"
ordem: 4
itens_origem: ["### Microtópico 4 — Faça rollback sem confundir aplicação e dados"]
---

### Microtópico 4 — Faça rollback sem confundir aplicação e dados

Rollback da aplicação normalmente significa voltar a servir uma versão anterior conhecida, seja redeployando seu artefato, seja mudando o tráfego para uma versão ainda disponível. A estratégia precisa dizer qual versão é válida, como identificá-la, quem pode disparar a reversão, quais sinais a acionam e como confirmar recuperação. Um rollback não é reproduzível se depende de encontrar manualmente arquivos ou reconstruir a versão antiga sem rastreabilidade.

Aplicação e banco têm ciclos diferentes. Voltar o código não restaura automaticamente linhas alteradas nem desfaz uma migração. Uma coluna removida, formato de dados alterado ou escrita feita apenas pelo novo código pode tornar a versão antiga incompatível. Planeje migrações compatíveis com as versões que coexistirão: um padrão comum é expandir (adicionar estrutura compatível), migrar/levar leituras e escritas para o novo formato, e só depois remover o formato antigo em outra mudança. A ordem e a reversibilidade dependem do banco e do tráfego.

Antes de mudanças destrutivas, faça backup testado e defina recuperação de dados, dono da decisão e impacto aceitável. Backup sem teste de restauração não comprova que recuperação funciona. Quando o rollback de dados não é seguro, prefira correção para frente ou procedimento de recuperação explícito, em vez de prometer reversão automática.

Exemplo conceitual de jobs: adapte scripts, artefatos e referência das Actions à aplicação. As tags ilustrativas devem ser substituídas por referências verificadas conforme a política do repositório; o job de produção foi omitido para manter o exercício em staging.

```yaml
name: Deploy staging
on:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - name: Build e validação
        run: npm ci && npm run lint && npm run build
      - name: Guardar o artefato desta versão
        uses: actions/upload-artifact@v4
        with:
          name: web-${{ github.sha }}
          path: dist/
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    concurrency:
      group: deploy-staging
      cancel-in-progress: false
    steps:
      - name: Baixar o artefato do commit
        uses: actions/download-artifact@v5
        with:
          name: web-${{ github.sha }}
          path: dist/
      - name: Implantar em staging
        run: ./scripts/deploy-staging.sh dist/
      - name: Verificar saúde
        run: ./scripts/smoke-staging.sh
```

O exemplo supõe que scripts de deploy e smoke existem, que `dist/` é a saída correta e que as Actions escolhidas são compatíveis. Não contém credenciais: o script deve receber autenticação por mecanismo configurado com privilégio mínimo, de preferência OIDC quando suportado e corretamente restrito. O exercício deve comprovar que o nome identifica o artefato da mesma execução; um nome sozinho não é atestado de integridade.

