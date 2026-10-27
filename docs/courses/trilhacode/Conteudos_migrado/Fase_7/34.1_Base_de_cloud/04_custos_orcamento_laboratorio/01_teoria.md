---
arquivo_id: "f7-34-1-04-custos-orcamento-laboratorio-01-teoria-md"
parent_key: "34.1"
tipo_arquivo: "theory"
assunto: "04_custos_orcamento_laboratorio"
ordem: 4
itens_origem: ["### Microtópico 4 — Custo, orçamento e encerramento do laboratório"]
---

### Microtópico 4 — Custo, orçamento e encerramento do laboratório

Custo pode incluir horas de compute, armazenamento e snapshots, banco, balanceador, endereços IPv4 públicos, NAT Gateway, tráfego entre zonas/regiões e para a internet, logs, DNS, suporte e impostos. Serviço “pequeno” mantido ligado por dias ou um componente de rede esquecido pode superar a estimativa inicial. Registre região, tamanho, quantidade, duração, armazenamento, tráfego e hipóteses; use a AWS Pricing Calculator para obter uma estimativa, não uma fatura garantida.

AWS Budgets pode enviar alertas e também pode ser configurado para executar ações específicas, como aplicar política ou agir sobre certos recursos compatíveis. Não assuma que um budget genérico desliga tudo ou limita cobrança: dados de uso/custo têm atraso, alertas podem chegar depois do gasto e a ação depende de configuração, serviço e permissão. Confira a atualização documentada, leia as condições atuais da conta e use limite de serviço/ação específica quando adequado.

As ofertas de Free Tier e os planos de cadastro mudam. Em outubro de 2026, novas contas têm planos/ créditos com elegibilidade e duração próprios; contas existentes ou criadas antes da mudança podem ver condições diferentes. Não prometa “AWS grátis” sem consultar a tela de billing e a página vigente para aquela conta, região e serviço. Créditos não cobrem necessariamente todo serviço, uso ou duração.

Ao concluir um laboratório, liste os recursos criados por região e dependências; apague recursos de compute, load balancer, NAT, banco, volumes, snapshots, endereços e logs conforme apropriado. Confirme o estado final no console e examine Billing/Cost Explorer depois, pois custos e dados podem atualizar com atraso. Não apague backups/dados que precisam ser preservados; identifique a decisão e retenção antes de remover. Sem conta AWS autorizada, produza diagrama e estimativa sem provisionar.

