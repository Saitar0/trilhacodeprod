---
arquivo_id: "f5-17-1-04-modulos-package-scripts-01-teoria"
parent_key: "17.1"
tipo_arquivo: "theory"
assunto: "04_modulos_package_scripts"
ordem: 4
itens_origem: ["6. Módulos, package.json e scripts"]
---

### 6. Módulos, package.json e scripts
Node.js oferece dois formatos comuns de módulo: ECMAScript Modules (ESM) e CommonJS. A forma de interpretar arquivos .js depende do campo type do package.json mais próximo; extensões .mjs e .cjs também identificam os formatos explicitamente. import/export pertencem ao ESM; require/module.exports são o padrão CommonJS. Um projeto deve declarar e usar seu formato de maneira consistente, especialmente ao integrar dependências.

O package.json registra metadados, dependências e scripts de automação. Scripts como npm run padronizam comandos de desenvolvimento, verificação e execução. Confirme a versão de Node adotada e não inclua tokens ou credenciais em scripts versionados. [Node.js — Packages](https://nodejs.org/api/packages.html).

