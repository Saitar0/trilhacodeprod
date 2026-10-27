---
arquivo_id: "f6-29-2-03-flakiness-e-evidencia-01-teoria-md"
parent_key: "29.2"
tipo_arquivo: "theory"
assunto: "03_flakiness_e_evidencia"
ordem: 3
itens_origem: ["## Microtópico 4 — Reduza flakiness e registre o limite da evidência"]
---

## Microtópico 4 — Reduza flakiness e registre o limite da evidência
Um teste é flaky quando passa ou falha dependendo de tempo, ordem ou estado externo sem que o produto tenha mudado. Use fixtures isoladas, dados exclusivos, assertions com espera automática e ações ancoradas em elementos acessíveis. Evite pausas fixas como `sleep` para “dar tempo”: espere a condição que importa, como a mensagem aparecer ou a URL mudar.

Cada teste deve preparar seu próprio contexto e não depender de outro teste ter criado uma sessão ou registro. Em Playwright, páginas e contextos de teste são isolados por padrão. Ao usar backend compartilhado, a base de dados ainda pode ser fonte de interferência; crie identificadores exclusivos, limpe recursos e mantenha a execução segura em paralelo.

Ao relatar um teste, registre a fronteira atravessada e as substituições: quais componentes executaram, quais serviços foram simulados, qual backend foi real, quais dados foram preparados e qual contrato ficou sem verificação. Essa descrição evita interpretar um fluxo de navegador com rede mockada como validação do backend.

