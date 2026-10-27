---
arquivo_id: "f5-24-4-m03-criterios-de-aceite"
parent_key: "24.4"
tipo_arquivo: "acceptance_criteria"
ordem: 3
itens_origem: ["M3"]
titulo_marco: "Marco 3 — Implementação da propriedade difícil do tipo"
---

**Aceite por tipo:**
| Tipo | Demonstração obrigatória |
|---|---|
| T1 | Mesma chave repetida não duplica o efeito; concorrência respeita estoque disponível; pagamento é explicitamente simulado. |
| T2 | Dois usuários autenticados em tenants distintos; leitura e escrita cruzadas são negadas por autorização por objeto. |
| T3 | Dois clientes conectados observam o evento; conexão protegida e reconexão/estado após desconexão são demonstrados. |
| T4 | Busca/ordem/paginação obedecem ao contrato; limites e casos de página vazia/última página são verificados. |
| T5 | Job pode ser consultado por estado; sucesso/falha e limites do arquivo são demonstrados sem carregar arquivo inteiro na memória. |

