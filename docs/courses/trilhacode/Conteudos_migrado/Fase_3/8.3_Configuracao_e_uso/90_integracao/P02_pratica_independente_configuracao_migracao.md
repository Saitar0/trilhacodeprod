---
arquivo_id: "f3-8-3-90-integracao-p02-pratica-independente-configuracao-migracao"
parent_key: "8.3"
tipo_arquivo: "practice"
assuntos: ["01_escopo_selecao_arquivos", "02_opcoes_runtime_build", "04_migracao_gradual"]
ordem: 2
itens_origem: ["P2"]
---

### 2. Independente — proponha uma configuração de migração
Considere um projeto com JavaScript em src/, um processo de build existente e arquivos gerados que não devem ficar junto às fontes. Escreva um plano de três etapas: delimite os arquivos abrangidos, decida onde ficam as saídas quando o compilador as emitir, use allowJs/checkJs adequadamente e explique como verificará que cada etapa preservou o comportamento.

Registre o runtime real — Node, navegador com bundler ou outro — e explique como ele orienta target, module e moduleResolution. Não há uma combinação universal para todos os ambientes.

**Dica:** desenhe primeiro as pastas fonte/saída; escolha depois um módulo de baixo risco e defina como observar o comportamento antes e depois.

