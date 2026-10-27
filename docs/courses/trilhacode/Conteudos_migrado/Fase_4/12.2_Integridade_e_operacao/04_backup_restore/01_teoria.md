---
arquivo_id: "f4-12-2-04-backup-restore-01-teoria"
parent_key: "12.2"
tipo_arquivo: "theory"
assunto: "04_backup_restore"
ordem: 4
itens_origem: ["5. Diferencie migration de backup e ensaie restore"]
---

### 5. Diferencie migration de backup e ensaie restore
Migration transforma a estrutura/dados para uma versão do produto. Backup cria uma cópia recuperável do estado do banco segundo uma estratégia de retenção. Um dump guardado no mesmo disco do banco não cobre falha desse disco; uma cópia só é útil se puder ser lida e restaurada.

Defina o que precisa ser recuperado, com que perda máxima de dados e em quanto tempo. A estratégia depende do tamanho, frequência de mudanças, retenção e objetivos operacionais. Faça restaurações de teste em ambiente separado, confira tabelas, restrições e dados essenciais e registre duração e falhas. Não teste restauração sobre a única cópia válida nem confunda volume persistente de container com backup independente.

**Checklist operacional:**
- Transação cobre todas as mudanças que precisam confirmar juntas?
- Concorrência está protegida por condição atômica, lock ou controle de versão?
- A aplicação reconhece conflito/abort e repete a operação inteira apenas quando seguro?
- Migration foi aplicada em cópia ou ambiente de teste com dados representativos?
- O rollout mantém compatibilidade durante a mudança?
- Existe backup independente e um restore recente verificado?

