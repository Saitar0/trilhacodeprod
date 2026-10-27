---
arquivo_id: "f3-6-4-04-scripts-ferramentas-qualidade-01-teoria"
parent_key: "6.4"
tipo_arquivo: "theory"
assunto: "04_scripts_ferramentas_qualidade"
ordem: 4
itens_origem: ["Scripts e ferramentas de qualidade"]
---

### Scripts e ferramentas de qualidade
O campo `scripts` do `package.json` dá nomes a comandos do projeto. `npm run nome` executa um script declarado; `npm start` é uma forma abreviada convencional para o script `start`. Scripts registram como iniciar e verificar o projeto, em vez de depender de comandos memorizados.

**ESLint** analisa padrões configurados e aponta problemas ou inconsistências; **Prettier** formata código segundo regras definidas. Têm funções diferentes e podem ser usados juntos. Registre ferramentas locais em `devDependencies` e chame as versões instaladas pelo projeto. `npm audit` envia ao registry configurado informações sobre dependências para obter um relatório de vulnerabilidades conhecidas. O resultado depende dos avisos disponíveis e da árvore consultada: relatório sem avisos não prova que o aplicativo é seguro.

