---
arquivo_id: "f3-6-4-90-integracao-p03-pratica-transferencia-projeto-node"
parent_key: "6.4"
tipo_arquivo: "practice"
assuntos: ["01_node_execucao_modulos", "02_manifesto_dependencias", "03_lockfile_instalacao_reproduzivel", "04_scripts_ferramentas_qualidade"]
ordem: 3
itens_origem: ["P3"]
---

### 3. Transferência — monte um pequeno projeto Node/npm
Crie um projeto com `npm init`, um `dados.json` fictício e um programa Node que leia o arquivo local e imprima um resumo. Declare explicitamente o formato de módulos. Configure scripts para iniciar o programa e executar ESLint e Prettier como ferramentas locais de desenvolvimento. Configure `.gitignore` para `node_modules`; versione manifesto e lockfile.

Use este dado inicial em `dados.json`:

```json
{
  "eventos": [
    { "titulo": "Aula aberta", "publicado": true },
    { "titulo": "Rascunho", "publicado": false }
  ]
}
```

No arquivo de entrada ESM, use a estrutura abaixo e complete o resumo:

```js
import { readFileSync } from "node:fs";

const caminho = new URL("../dados.json", import.meta.url);
try {
  const dados = JSON.parse(readFileSync(caminho, "utf8"));
  // TODO: imprimir quantos eventos estão publicados
} catch (erro) {
  console.error(`Não foi possível ler os dados: ${erro.message}`);
  process.exitCode = 1;
}
```

Com o JSON inicial, a saída esperada é `Eventos publicados: 1`. Altere temporariamente o JSON para um formato inválido e confirme a mensagem e o código de saída. Depois restaure o arquivo válido.

Organize o projeto com `src/index.js` como entrada e `dados.json` na raiz; o caminho relativo do exemplo já considera essa estrutura.

Instale e configure as ferramentas seguindo a documentação oficial atual. Execute `npm audit` e registre como interpretou o relatório. Em uma cópia limpa, use `npm ci` e execute os scripts documentados. **Atenção:** `npm ci` remove `node_modules` existente na pasta onde é executado; use a cópia limpa ou confirme que a pasta é descartável.


**Entregue:** árvore de arquivos, scripts do manifesto, leitor JSON completo, `.gitignore`, lockfile e nota sobre o audit. Demonstre JSON válido e inválido conforme o cenário acima. Não é necessário publicar o projeto.


**Dicas graduais:** (1) complete o contador com `dados.eventos.filter((evento) => evento.publicado).length`; (2) converta o texto com `JSON.parse` e preserve o tratamento de erro; (3) instale ferramentas com `--save-dev` e chame-as por scripts npm; (4) valide em cópia limpa com `npm ci`.

