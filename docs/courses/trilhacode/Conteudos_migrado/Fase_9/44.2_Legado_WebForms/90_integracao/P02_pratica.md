---
arquivo_id: "f9-44-2-90-integracao-p02-pratica"
parent_key: "44.2"
tipo_arquivo: "practice"
assuntos: ["02_controles_viewstate_codebehind", "03_manutencao_suporte_modernizacao"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Avalie um legado e proponha próximo passo
**Contexto:** um sistema de estoque tem `Inventory.aspx.cs` com validação, regra de reserva e consultas SQL; a página mantém dados no ViewState. O sistema roda em Windows Server e depende de um controle de terceiros sem versão registrada.

**Instruções:** faça um inventário do que precisa ser confirmado antes de decidir “manter”, “corrigir” ou “modernizar”: suporte do Framework/Windows, dependências, dados/estado, lógica de domínio, segurança e observabilidade. Proponha uma primeira fatia para separar uma regra de negócio ou endpoint, indique métrica de sucesso, forma de testar e como reverter durante coexistência com ASP.NET Core.

**Entrega:** checklist priorizado e plano de uma página com uma hipótese, uma fatia pequena, critérios de aceite e retorno.

**Dica gradual:** começar por uma nova interface não resolve dependência de banco compartilhado ou autenticação; identifique primeiro a fonte da verdade e as regras envolvidas.

