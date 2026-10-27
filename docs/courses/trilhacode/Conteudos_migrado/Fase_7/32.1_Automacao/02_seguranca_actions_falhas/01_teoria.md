---
arquivo_id: "f7-32-1-02-seguranca-actions-falhas-01-teoria-md"
parent_key: "32.1"
tipo_arquivo: "theory"
assunto: "02_seguranca_actions_falhas"
ordem: 2
itens_origem: ["### Microtópico 3 — Permissões, secrets e dependências de Actions", "### Microtópico 4 — Leitura de falhas e limites da análise estática"]
---

### Microtópico 3 — Permissões, secrets e dependências de Actions

Defina `permissions` explicitamente e conceda somente o necessário. Um workflow que apenas lê o código geralmente precisa de `contents: read`; não habilite `write-all` por conveniência. Jobs de publicação ou implantação devem ser isolados e receber permissões adicionais somente quando forem executar essa tarefa.

Segredos devem ficar no armazenamento de secrets do GitHub, ser disponibilizados somente para o job que precisa deles e nunca ser escritos no YAML, em fixtures ou nos logs. Pull requests de forks normalmente não recebem secrets; não desenhe o fluxo supondo que eles estarão presentes. Para publicar em um serviço compatível, prefira credenciais curtas por OIDC quando essa integração estiver corretamente configurada.

Uma Action é código executado no runner. Revise quem a mantém, permissões solicitadas, versão e alterações. Tags como `@v7` são mais legíveis e facilitam atualizações, mas podem apontar para uma nova revisão; fixar o SHA completo é a opção imutável. Quando a equipe adotar SHA, registre a versão legível em comentário, use uma origem confiável e atualize o SHA por processo revisado. Não copie um SHA sem verificar que corresponde à release pretendida.

### Microtópico 4 — Leitura de falhas e limites da análise estática

CI deve dizer qual requisito falhou e preservar informação suficiente para corrigir o problema. Separe lint, build e testes em steps identificáveis, mantenha a saída do comando e evite mascarar falhas com `continue-on-error` em um gate obrigatório. Se o comando retorna código diferente de zero, o step e o job falham, a menos que a configuração altere essa regra.

Ferramentas de análise estática, como SonarQube, podem encontrar padrões suspeitos, duplicação e problemas de manutenção. Elas complementam testes e revisão; um score não prova correção, segurança ou qualidade total. Defina o que o gate mede, como tratar falsos positivos e quem mantém o limiar. Evite adicionar ferramenta ou threshold sem uma decisão de equipe e uma forma de interpretar o resultado.

Exemplo ilustrativo para projeto npm com scripts `lint`, `build` e `test:ci` já definidos. As referências de versão mostram o formato; em repositórios com exigência de Actions imutáveis, substitua cada tag por SHA completo verificado e documente a versão correspondente.

```yaml
name: CI
on:
  pull_request:
permissions:
  contents: read
concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
jobs:
  quality:
    name: quality
    runs-on: ubuntu-latest
    steps:
      - name: Baixar o código
        uses: actions/checkout@v7
      - name: Preparar Node.js
        uses: actions/setup-node@v7
        with:
          node-version: '24'
          cache: npm
      - name: Instalar dependências do lockfile
        run: npm ci
      - name: Verificar estilo e erros estáticos
        run: npm run lint
      - name: Gerar build
        run: npm run build
      - name: Executar testes de CI
        run: npm run test:ci
```

Adapte `node-version` à versão suportada pelo projeto e confirme que os scripts existem no `package.json`. Se não houver `test:ci`, crie um script explícito e documentado; não suponha que opções como `--run` funcionam com qualquer runner de testes. O exemplo usa uma única job para produzir um check obrigatório previsível. Separar em jobs pode acelerar feedback, desde que os checks requeridos e dependências estejam configurados com clareza.

