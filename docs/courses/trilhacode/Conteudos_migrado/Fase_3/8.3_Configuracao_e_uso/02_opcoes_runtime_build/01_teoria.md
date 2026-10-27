---
arquivo_id: "f3-8-3-02-opcoes-runtime-build-01-teoria"
parent_key: "8.3"
tipo_arquivo: "theory"
assunto: "02_opcoes_runtime_build"
ordem: 2
itens_origem: ["2. Opções de acordo com runtime e build"]
---

### 2. Opções de acordo com runtime e build
As opções devem refletir onde o JavaScript vai rodar e quem resolve os módulos. target escolhe o nível de JavaScript emitido; module descreve o formato de módulos esperado no resultado; moduleResolution define como o TypeScript encontra imports; rootDir e outDir organizam fontes e saídas. Não copie opções de Node para navegador ou bundler sem verificar se representam o mesmo ambiente.

Uma saída separada evita misturar arquivos gerados às fontes:

```text
projeto/
  src/
    index.ts
  dist/       # saída gerada
  tsconfig.json
```

strict ativa verificações mais rigorosas, incluindo noImplicitAny e strictNullChecks. Entenda quais diagnósticos essas opções habilitam antes de desligá-las ao primeiro erro.

**Erro comum:** escolher module e moduleResolution isoladamente. As opções precisam combinar com runtime e ferramentas que executam ou empacotam o código.

