---
arquivo_id: "f6-27-4-03-segredos-csp-dependencias-p03-pratica-md"
parent_key: "27.4"
tipo_arquivo: "practice"
assunto: "03_segredos_csp_dependencias"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Revisar bundle, CSP e dependências
**Contexto e objetivo:** identificar dados que se tornam públicos e entender o limite das ferramentas de segurança.

**Dados iniciais fictícios:** bundle contém `PUBLIC_MAP_KEY=demo-key-123`; `.env.example` inclui `DATABASE_PASSWORD=change-me`; relatório de auditoria aponta pacote direto com advisory e correção disponível.

**Instruções:** classifique cada valor como público, exemplo ou segredo real; decida onde deve viver e quais restrições são adequadas. Esboce uma CSP de princípio mínimo para app que carrega scripts próprios e uma origem de API declarada (não copie para produção sem validar dependências, nonce/hash e modo de deploy). Para o advisory, verifique dependência direta/transitiva, versão corrigida e risco de quebra; proponha atualização revisada e registro. Não introduza chaves reais nem atualize dependências de produção como parte do exercício.

**Entrega:** tabela de inventário/decisão, CSP comentada para ambiente local, registro de revisão do advisory e limites das verificações.

**Dica gradual:** bundle de cliente é observável pelo usuário; `.env.example` deve conter placeholders, não credenciais reutilizáveis. CSP é uma camada e pode bloquear scripts legítimos se mal configurada.

**Feedback e erro comum:** a chave de frontend é assumida pública e restringida conforme o serviço; senha fica apenas no servidor e o exemplo é claramente fictício; advisory tem correção revisada. Erro comum: considerar prefixo `PUBLIC_` um cofre ou “audit sem findings” uma certificação.

