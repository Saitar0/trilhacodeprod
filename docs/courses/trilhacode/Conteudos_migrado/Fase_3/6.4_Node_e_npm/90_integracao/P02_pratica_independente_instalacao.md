---
arquivo_id: "f3-6-4-90-integracao-p02-pratica-independente-instalacao"
parent_key: "6.4"
tipo_arquivo: "practice"
assuntos: ["02_manifesto_dependencias", "03_lockfile_instalacao_reproduzivel", "04_scripts_ferramentas_qualidade"]
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — investigue uma instalação não reproduzível
Um projeto clonado contém `package.json` e `package-lock.json`, mas não `node_modules`. O manifesto foi editado sem atualizar o lock e `npm ci` falha.

Entregue uma sequência curta que explique por que o clone não precisa versionar `node_modules`, por que `npm ci` falhou, quando `npm install` deve reconciliar manifesto e lock e como testar em uma cópia limpa sem apagar dependências locais importantes. Inclua como analisar uma vulnerabilidade transitiva do `npm audit` sem aplicar uma correção automática às cegas.

**Dicas graduais:** (1) compare manifesto e lock; (2) `npm ci` não atualiza o lock e remove a instalação existente; (3) leia pacote, caminho transitivo, severidade e correção sugerida antes de decidir.

