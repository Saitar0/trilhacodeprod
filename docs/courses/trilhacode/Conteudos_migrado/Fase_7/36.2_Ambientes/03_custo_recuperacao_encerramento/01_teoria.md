---
arquivo_id: "f7-36-2-03-custo-recuperacao-encerramento-01-teoria-md"
parent_key: "36.2"
tipo_arquivo: "theory"
assunto: "03_custo_recuperacao_encerramento"
ordem: 3
itens_origem: ["### Microtópico 4 — Custo, recuperação e encerramento do ciclo"]
---

### Microtópico 4 — Custo, recuperação e encerramento do ciclo

Dev e staging podem diferir em tamanho e disponibilidade para reduzir custo, mas essas diferenças reduzem o que o teste comprova. Registre quais componentes, carga, rede e integrações não são representativos. Tag por projeto/ambiente e estimativa de custo ajudam atribuição; budget e alertas complementam monitoramento, mas não garantem interrupção de cobrança. Nat, banco, balanceador, logs, volumes, snapshots, IPs e transferência podem continuar gerando custo após parar a aplicação.

O laboratório tem lifecycle explícito: provisionar o mínimo permitido → verificar deploy → coletar evidência → revisar destroy → remover recursos temporários → confirmar state/backend, recursos remanescentes e billing após atualização. Não destrua estado remoto antes de usar o Terraform para remover os recursos sob sua gestão. Preserve state/outputs e backups exigidos até confirmar limpeza; então aplique retenção/remoção segura. Recursos importados/manuais, políticas e alguns artefatos podem não ser apagados junto com o recurso principal.

Mantenha um runbook de interrupção: interromper promoções se checks falharem, coletar logs sanitizados, restaurar versão anterior de aplicação se adequado, verificar infraestrutura e decidir se precisa corrigir para frente. Para mudanças de banco e dados, rollback de código ou infra não devolve automaticamente os dados. Restauração precisa de backup testado e permissão apropriada.

