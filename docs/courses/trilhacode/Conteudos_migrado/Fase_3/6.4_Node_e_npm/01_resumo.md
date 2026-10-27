---
arquivo_id: "f3-6-4-01-resumo"
parent_key: "6.4"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Node executa JavaScript fora do navegador.
- `package.json` descreve projeto, scripts e dependências.
- `dependencies` servem ao runtime; `devDependencies`, às ferramentas de desenvolvimento.
- Versione `package-lock.json`; exclua `node_modules` do Git; `npm ci` remove a pasta de dependências existente antes de recriá-la.
- CommonJS e ESM são sistemas de módulos diferentes, influenciados pela extensão e pelo campo `type`.
- `npm run` executa scripts declarados no projeto.
- ESLint analisa código segundo regras configuradas; Prettier formata; `npm audit` relata vulnerabilidades conhecidas, sem certificar segurança.

