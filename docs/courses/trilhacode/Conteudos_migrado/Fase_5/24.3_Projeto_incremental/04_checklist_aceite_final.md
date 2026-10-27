---
arquivo_id: "f5-24-3-04-checklist-aceite-final"
parent_key: "24.3"
tipo_arquivo: "checklist"
ordem: 0
itens_origem: ["checklist_final"]
---

## Checklist de aceite final
- [ ] README permite iniciar, migrar e testar o projeto em ambiente local.
- [ ] API documenta operação, autenticação, respostas e erros principais.
- [ ] Autorização deriva da identidade autenticada e é testada para negação.
- [ ] PostgreSQL pode ser criado do zero com migrations versionadas.
- [ ] Testes cobrem serviço, rota, validação, persistência e acesso negado.
- [ ] Cache tem decisão registrada e, se usado, política testável de expiração/invalidação.
- [ ] Dockerfile e Compose executam os serviços necessários sem embutir segredos.
- [ ] Seeds e exemplos usam dados sintéticos; nenhum teste acessa produção.

