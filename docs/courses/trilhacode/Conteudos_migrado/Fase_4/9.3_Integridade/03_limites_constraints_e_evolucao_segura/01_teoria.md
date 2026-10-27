---
arquivo_id: "f4-9-3-03-limites-constraints-e-evolucao-segura-01-teoria"
parent_key: "9.3"
tipo_arquivo: "theory"
assunto: "03_limites_constraints_e_evolucao_segura"
ordem: 3
itens_origem: ["4. Saiba onde a regra deve ser aplicada", "5. Verifique falhas e evolua o esquema com segurança"]
---

### 4. Saiba onde a regra deve ser aplicada
CHECK é indicado para condições da própria linha, como preço não negativo ou data_final >= data_inicial. No PostgreSQL, CHECK não deve consultar outra linha nem outra tabela: a validação não se mantém confiável diante de alterações posteriores. Para regras entre tabelas, prefira FK, UNIQUE, exclusion constraint quando aplicável, ou uma operação transacional cuidadosamente protegida. Triggers podem atender casos específicos, mas adicionam comportamento que deve ser documentado e testado.

Uma regra como “não pode haver dois empréstimos ativos do mesmo exemplar” envolve várias linhas e o intervalo/estado dos empréstimos. Uma UNIQUE comum sobre exemplar_id não atende ao histórico, pois impediria todos os empréstimos futuros. A modelagem e o mecanismo precisam expressar precisamente o que significa “ativo”; no PostgreSQL, uma exclusão por intervalo ou uma estratégia com estado e unicidade parcial podem ser adequadas conforme os requisitos.

Constraints adiáveis podem ser verificadas no fim da transação em vez de após cada instrução, quando o tipo de constraint e o SGBD permitem. Isso ajuda em certas operações que mudam referências em etapas, mas não deve ser usado sem necessidade.

**Erro comum:** implementar uma regra que depende de outras linhas com um CHECK que só observa a linha atual.

### 5. Verifique falhas e evolua o esquema com segurança
Demonstre cada regra com pelo menos um caso válido e um caso inválido. Leia o erro do SGBD para identificar tabela, constraint e linha, quando informadas. A aplicação pode traduzir uma violação conhecida em mensagem clara, mas não deve esconder falhas inesperadas nem afirmar que uma gravação ocorreu quando a transação foi revertida.

Adicionar uma constraint a uma tabela existente pode falhar se dados antigos a violarem. Uma migração responsável identifica e corrige os registros, aplica a regra em uma ordem segura e verifica o resultado. Em tabelas grandes, considere o impacto operacional e os recursos de validação incremental disponíveis no SGBD; detalhes dependem do mecanismo e da versão.

**Checklist de revisão:**
- A regra está escrita de forma observável e sem ambiguidade?
- A constraint escolhida cobre exatamente seu escopo?
- NULL tem significado definido para cada coluna?
- A ação de exclusão respeita o ciclo de vida dos dados?
- Há exemplos válidos e tentativas que provam as rejeições esperadas?
- Uma migração foi planejada para dados já existentes?

