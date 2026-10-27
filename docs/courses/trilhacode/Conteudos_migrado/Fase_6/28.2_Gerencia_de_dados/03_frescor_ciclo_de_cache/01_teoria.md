---
arquivo_id: "f6-28-2-03-frescor-ciclo-de-cache-01-teoria-md"
parent_key: "28.2"
tipo_arquivo: "theory"
assunto: "03_frescor_ciclo_de_cache"
ordem: 3
itens_origem: ["## Microtópico 3 — Entenda frescor e ciclo de vida do cache"]
---

## Microtópico 3 — Entenda frescor e ciclo de vida do cache
Cache diminui buscas repetidas e pode manter a interface útil enquanto novos dados chegam. **Frescor** e **permanência no cache** são decisões distintas: `staleTime` define por quanto tempo uma resposta é considerada fresca para fins de revalidação; o tempo de coleta de consultas inativas governa por quanto tempo dados sem observadores permanecem guardados. Dados obsoletos ainda podem ser exibidos, mas podem motivar uma nova busca conforme as opções da consulta e eventos configurados.

Não existe um único prazo certo para todos os dados. Uma lista que muda com frequência pode precisar ser revalidada mais cedo que uma tabela de referência quase imutável. Configure o comportamento com base no custo de dados desatualizados, frequência de mudança e custo da rede. Se a tela precisa atualizar periodicamente, polling é uma política separada e deve ser avaliado conscientemente. Leia os padrões da biblioteca adotada, porque revalidação em montagem, foco da janela, reconexão e tentativas podem explicar buscas que parecem inesperadas.

Invalidar uma família de consultas marca o dado como precisando de atualização e permite que a biblioteca reconcilie as consultas relevantes com o servidor. A invalidação não é sinônimo de apagar todos os dados nem garante que toda consulta futura desapareça; entenda o filtro de chave usado e o comportamento da versão instalada.

