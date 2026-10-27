---
arquivo_id: "f6-28-3-03-persistencia-reset-identidade-01-teoria-md"
parent_key: "28.3"
tipo_arquivo: "theory"
assunto: "03_persistencia_reset_identidade"
ordem: 3
itens_origem: ["## Microtópico 4 — Defina quando preservar, redefinir e revisar"]
---

## Microtópico 4 — Defina quando preservar, redefinir e revisar
O lugar onde um componente aparece na árvore de renderização influencia a preservação do estado em React. Ao trocar de registro ou contexto, decida se o formulário deve preservar o rascunho ou começar limpo. Uma chave de componente pode sinalizar que uma nova identidade deve iniciar um estado novo; use-a deliberadamente, pois também pode redefinir campos e interações que a pessoa esperava preservar.

Persistência exige uma decisão adicional: guardar em memória, URL, armazenamento local ou servidor. Cada opção tem efeitos diferentes sobre recarga, compartilhamento, privacidade, expiração e logout. Preferências visuais não têm o mesmo risco que tokens de autenticação ou dados pessoais. Não use armazenamento do navegador como proteção para segredos.

Organização é revisável. Quando novos consumidores surgem, um estado local pode precisar ser elevado. Quando uma feature deixa de ser usada por outras áreas, um estado global pode voltar para perto do componente. Registre o requisito que motivou a decisão e um sinal concreto que levaria a revisá-la, como duplicação de estado, atualizações manuais espalhadas ou consumidores que nunca usam o valor.

