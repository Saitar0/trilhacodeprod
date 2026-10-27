---
arquivo_id: "f3-7-2-02-carregamento-diagnostico-01-teoria"
parent_key: "7.2"
tipo_arquivo: "theory"
assunto: "02_carregamento_diagnostico"
ordem: 2
itens_origem: ["3. Carregamento e diagnóstico no navegador"]
---

### 3. Carregamento e diagnóstico no navegador
O HTML carrega o ponto de entrada como módulo:

```html
<script type="module" src="./app.js"></script>
```

O navegador resolve as dependências importadas pelo ponto de entrada. Módulos são deferidos automaticamente até que o documento seja analisado e usam modo estrito. Durante o desenvolvimento, sirva a página por um servidor local compatível: abrir o HTML diretamente com `file://` pode impedir o carregamento por restrições do navegador.

Ao diagnosticar uma falha, confira: (1) se o script tem `type="module"`; (2) se o caminho é relativo ao arquivo que contém aquele import; (3) se o nome importado existe entre as exportações; (4) se o servidor encontrou e serviu os arquivos corretamente.

**Erro comum:** calcular o caminho do import a partir do HTML. O caminho é resolvido em relação ao módulo que declara o import.

