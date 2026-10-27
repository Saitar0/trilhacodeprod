---
arquivo_id: "f7-36-2-90-integracao-p03-pratica-md"
parent_key: "36.2"
tipo_arquivo: "practice"
assuntos: ["02_pipeline_identidade_gates", "03_custo_recuperacao_encerramento"]
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Faça rollback controlado e encerre o laboratório

**Desafio:** provar que a equipe consegue interromper uma versão problemática e remover o ambiente temporário sem apagar evidência necessária.

**Passos:**
1. Registre a última versão saudável e a implantação atual; provoque uma falha segura apenas em staging e capture sinais de health/smoke check.
2. Reverta a aplicação ao artefato anterior conhecido ou documente a correção para frente; verifique serviço e infraestrutura sem aplicar destroy como “rollback”.
3. Analise se a mudança Terraform afetou dados/schema; identifique o plano de recuperação e quais backups/state precisam permanecer.
4. Gere e revise plano de destroy para o ambiente temporário; liste recursos que não serão removidos automaticamente e dados a reter.
5. Em conta autorizada, aplique destroy apenas em dev/staging de exercício; confirme state, console por região, dependências e billing depois da atualização. Se não houver sandbox, entregue plano sem executar.
6. Remova ou proteja state, plano salvo, outputs e artefatos conforme a política de retenção e registre o encerramento.

**Evidências:** registro da versão/rollback; smoke check posterior; plano de destroy revisado; inventário antes/depois; destino de state/backups; verificação de custos pendentes ou declaração de que será verificada após atualização.

**Verificação:** recuperação da aplicação foi confirmada; recursos persistentes não foram presumidos removidos; dados necessários não foram apagados; limites temporais de billing estão declarados.

**Aceite:** rollback e destroy são decisões separadas; limpeza é limitada ao ambiente autorizado; state e dados têm destino explícito; nenhuma ausência de cobrança imediata é tratada como prova de custo zero.

