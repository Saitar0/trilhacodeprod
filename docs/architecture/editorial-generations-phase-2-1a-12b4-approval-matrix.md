# Fase 2.1A.12B.4 — matriz de aprovação humana

Todos os estados abaixo são PENDING_APPROVAL. As recomendações técnicas não representam decisão de produto, segurança ou operação aprovada.

| Ordem | ADR | Decisão / pergunta | Recomendação | Alternativas | Categoria e impacto | Status |
|---:|---|---|---|---|---|---|
| 1 | ADR-008 | Qual ambiente/versão serve de baseline e qual linha receberá a implementação? | Obter digest e proveniência por ambiente; selecionar uma linha de integração reconciliada a partir do release baseline aprovado | main; staging; snapshot e5; linha específica reconciliada | Operacional e técnica; bloqueia qualquer runtime | PENDING_APPROVAL |
| 2 | ADR-001 | Como coordenar todos os escritores e tratar revisão obsoleta? | Revisão monotônica por trilha, snapshot privado coerente, CAS e conflito explícito; fencing para operação longa quando necessário | Serialização total; lease/fencing comum; snapshot por revisão; híbrida | Técnica e produto editorial; bloqueia construção confiável | PENDING_APPROVAL |
| 3 | ADR-005 | Como impedir acesso público a gabaritos e campos internos? | Defesa em profundidade: armazenamento/identidade segregados, reader mínimo e DTO allowlist | Filtragem no controller; DTO isolado; segregação combinada | Segurança; bloqueia leitor/avaliador | PENDING_APPROVAL |
| 4 | ADR-003 | Quais taxonomias e metadados são imutáveis na geração? | Congelar ou versionar o que altera significado, ordem, renderização ou validação; classificar campo por campo | Copiar tudo; referências globais; catálogo versionado; híbrida | Produto, frontend e técnica; bloqueia escopo do snapshot | PENDING_APPROVAL |
| 5 | ADR-002 | Quando fixar geração para sessão/tentativa e como tratar republicação? | Fixação validada pelo servidor para sessão; tentativa continua ligada à publicação/geração original | Última geração sempre; pin por request; pin por tentativa; híbrida sessão + tentativa | Produto/pedagógica e técnica; bloqueia leitura e progresso versionados | PENDING_APPROVAL |
| 6 | ADR-004 | Quais referências e obrigações impedem retenção/exclusão? | Retenção por referência e obrigação; sem prazo até aprovação de produto/privacidade | Ilimitada; janela fixa; por curso; híbrida | Privacidade, jurídica e produto; bloqueia GC/backfill destrutivo | PENDING_APPROVAL |
| 7 | ADR-006 | Qual é a unidade segura de publicação e restauração? | Construir, validar e selar candidato imutável; selecionar por CAS; leitor pinado e sem fallback live | Atualização in-place; snapshot legado; geração e head; coexistência gradual | Técnica e operacional; depende obrigatoriamente de ADR-001 | PENDING_APPROVAL |
| 8 | ADR-007 | Qual ordem, escopo, donos e critério de cutover? | Fases pequenas, flags inicialmente off, escritores antes dos leitores, zero bypass antes do cutover | Big-bang; shadow write por rota; rollout gradual controlado | Operacional e produto; bloqueia rollout | PENDING_APPROVAL |

## Ordem e dependências

1. ADR-008 define baseline, ambiente alvo e linha que pode receber mudanças.
2. ADR-001 define a coerência da origem; ADR-006 depende dessa garantia.
3. ADR-005 e ADR-003 definem a fronteira de dados públicos/privados e o conteúdo congelado.
4. ADR-002 e ADR-004 definem a duração das referências de alunos e avaliação; ADR-004 depende de inventário completo dessas referências.
5. ADR-006 formaliza seleção/restore sobre os contratos anteriores.
6. ADR-007 aprova rollout, ownership, flags, coortes e cutover depois das decisões de domínio e segurança.

## Questões para os responsáveis

### Produto e pedagogia

- Por quanto tempo o aluno deve permanecer na geração da sessão?
- Pode concluir uma tentativa antiga após republicação?
- O que ocorre após restore e após retirada urgente?
- Como preservar progresso sem geração e histórico de notas?
- Qual é a experiência para atividade removida ou link antigo?

### Segurança, privacidade e dados

- Quais papéis podem ler definições privadas de avaliação?
- Quais campos são pessoais e quais são conteúdo pedagógico?
- Quais dados podem ser definitivamente excluídos e quem autoriza?
- Qual revisão jurídica/privacidade é necessária antes de retenção/GC?

### Engenharia e operação

- Qual ambiente recebe primeiro a integração?
- Qual linha é a linha oficial de desenvolvimento e release?
- Quem controla todas as rotas, importações, scripts e manutenção?
- Qual procedimento formal autoriza cutover e interrompe publicação?
- Como o operador entrega evidência sanitizada de imagem em execução?

As respostas não devem ser preenchidas por inferência de código ou pelo resultado da PoC.
