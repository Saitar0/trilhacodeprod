---
arquivo_id: "f6-27-2-03-retry-seguro-01-teoria-md"
parent_key: "27.2"
tipo_arquivo: "theory"
assunto: "03_retry_seguro"
ordem: 3
itens_origem: ["## Microtópico 3 — Faça novas tentativas com segurança"]
---

## Microtópico 3 — Faça novas tentativas com segurança
Retry é útil para falhas transitórias, como uma interrupção breve de rede ou uma resposta temporária do servidor. Repetir indefinidamente pode aumentar a carga, atrasar a recuperação e confundir a pessoa. Defina limite e intervalo, ofereça uma tentativa manual quando apropriado e cancele ou invalide tentativas quando a tela ou a intenção mudar. Backoff progressivo reduz pressão sobre um serviço que ainda está recuperando; jitter pode evitar que muitos clientes repitam simultaneamente.

Também classifique a operação. Métodos idempotentes podem ser repetidos sem alterar o efeito final além da primeira execução, sob o contrato HTTP correspondente. Uma leitura `GET` costuma ser candidata a retry. Uma criação ou pagamento via `POST` pode duplicar efeitos se o servidor não fornecer uma garantia de idempotência. Não automatize a repetição de uma escrita não idempotente só porque a resposta demorou: primeiro defina como descobrir se a operação foi concluída. Um contrato com chave de idempotência pode permitir repetição segura quando cliente e servidor implementam a mesma regra.

Retry automático e botão “Tentar novamente” devem refletir a mesma política de segurança. Enquanto a operação estiver em curso, evite disparar várias cópias por cliques repetidos; desabilite ou torne a ação idempotente no cliente e, principalmente para gravações, proteja também no servidor.

