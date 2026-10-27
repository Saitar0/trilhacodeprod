---
arquivo_id: "f7-32-2-04-rollback-schema-dados-p03-pratica-md"
parent_key: "32.2"
tipo_arquivo: "practice"
assunto: "04_rollback_schema_dados"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Planeje compatibilidade e restauração

**Desafio:** mostre como uma mudança de schema e dados convive com deploy e rollback.

**Passos:**
1. Escolha uma alteração fictícia ou de banco isolado, como trocar uma coluna de nome ou formato.
2. Desenhe estados do banco e versões da aplicação antes, durante e depois da transição.
3. Identifique em cada passo qual versão consegue ler e escrever; proponha expansão compatível, migração de dados e remoção posterior, quando aplicável.
4. Marque quais operações não são reversíveis automaticamente e proponha correção para frente, backup/restauração ou procedimento manual seguro.
5. Faça uma restauração de ensaio se o ambiente permitir; sem execução, registre como proposta e indique que ainda não foi comprovada.
6. Registre sinais de decisão, responsáveis e condição para parar ou reverter a implantação.

**Evidências:** sequência de migração; matriz versão × schema; plano de rollback/forward fix; registro de backup e restauração de ensaio ou lacuna explícita; critérios de decisão.

**Verificação:** a versão anterior continua compatível durante os passos em que rollback é prometido; os dados necessários não dependem de uma operação destrutiva já executada.

**Aceite:** compatibilidade e limites são explícitos; nenhuma reversão de dados é alegada sem mecanismo; backup tem restauração ensaiada ou permanece identificado como risco não verificado.

