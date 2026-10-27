---
arquivo_id: "f4-12-2-03-migrations-rollout-01-teoria"
parent_key: "12.2"
tipo_arquivo: "theory"
assunto: "03_migrations_rollout"
ordem: 3
itens_origem: ["4. Evolua schema com migrations planejadas"]
---

### 4. Evolua schema com migrations planejadas
Migration é uma alteração versionada e ordenada do schema e, quando necessário, dos dados. Uma ferramenta ou fluxo de migrations registra quais versões foram aplicadas para que ambientes diferentes avancem de forma controlada. Mantenha migrations aplicadas como histórico; correções normalmente entram em uma nova migration, não pela edição silenciosa de uma versão já distribuída.

Planeje impacto em dados existentes, duração, locks e compatibilidade com as versões da aplicação. Uma mudança em etapas — expandir schema, atualizar código para usar a estrutura nova, migrar os dados e só depois remover a estrutura antiga — permite implantações graduais. Adicionar uma coluna obrigatória sem valor para linhas antigas, por exemplo, exige estratégia de preenchimento e validação.

Rollback não é sempre uma inversão simples: remover coluna ou transformar dados pode perder informação. Alguns comandos do PostgreSQL têm restrições transacionais, portanto a execução deve seguir as orientações da ferramenta e do comando. Em sistemas em uso, combine plano de reversão ou correção, verificação e janela operacional.

**Erro comum:** aplicar migration diretamente em dados reais sem conferir compatibilidade, duração, bloqueios e caminho de recuperação.

