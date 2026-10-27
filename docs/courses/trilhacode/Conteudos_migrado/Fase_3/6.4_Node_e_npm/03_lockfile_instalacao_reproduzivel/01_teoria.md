---
arquivo_id: "f3-6-4-03-lockfile-instalacao-reproduzivel-01-teoria"
parent_key: "6.4"
tipo_arquivo: "theory"
assunto: "03_lockfile_instalacao_reproduzivel"
ordem: 3
itens_origem: ["Lockfile e instalação reproduzível"]
---

### Lockfile e instalação reproduzível
`package-lock.json` registra a árvore resolvida de dependências e deve ser versionado junto do `package.json`. `npm install` pode atualizar o lockfile para conciliá-lo com o manifesto. `npm ci` exige um lockfile compatível, falha se manifesto e lock divergirem e instala a árvore registrada; antes da instalação, remove o `node_modules` existente. Use-o em um projeto ou cópia descartável.

`node_modules` contém pacotes instalados localmente e costuma ser recriado a partir do manifesto e do lockfile, por isso geralmente fica fora do Git. Um clone limpo com `npm ci` permite verificar se as dependências registradas bastam para executar os scripts.

