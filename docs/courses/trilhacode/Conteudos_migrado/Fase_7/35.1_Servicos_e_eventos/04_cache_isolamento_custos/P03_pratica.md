---
arquivo_id: "f7-35-1-04-cache-isolamento-custos-p03-pratica-md"
parent_key: "35.1"
tipo_arquivo: "practice"
assunto: "04_cache_isolamento_custos"
ordem: 3
itens_origem: ["P03"]
---

### Atividade 3 — Decida se precisa de cache

**Desafio:** modele uma leitura frequente de catálogo ou perfil com e sem ElastiCache.

**Passos:**
1. Identifique fonte de verdade, taxa de leitura/escrita, tolerância a dado antigo e objetivo de latência.
2. Se cache ajudar, escolha cache-aside ou outra estratégia, defina chave com tenant/escopo, TTL e evento/ação de invalidação.
3. Simule cache miss, dado desatualizado e indisponibilidade do cache; determine quando ler do banco, falhar ou degradar.
4. Estime o custo comparando cache com chamadas ao banco, incluindo modalidade/engine, região, capacidade, tráfego e manutenção.
5. Registre a decisão de não usar cache se o benefício não justificar complexidade, custo e risco de staleness.

**Evidências:** sequência de leitura/escrita; contrato de chave/TTL/invalidação; análise de cenários de falha e isolamento entre tenants; estimativa com hipóteses.

**Verificação:** cache pode ser reconstruído; dados de tenants não colidem; comportamento sem cache é definido; o tipo de engine e os recursos necessários existem na modalidade/região escolhida.

**Aceite:** fonte durável está clara; política trata staleness e falhas; escolha de cache (ou não adoção) se apoia em requisitos e custo verificáveis.

