# Fase 2.1A.12B.3 — matriz de decisões para aprovação humana

**Todos os estados abaixo:** PENDING_APPROVAL.
Criar ADR não aprova política, não concede autorização de implementação e não significa que a decisão esteja implementada.

## 1. Decisões propostas

| Ordem | ADR | Pergunta que exige decisão | Recomendação técnica | Alternativas principais | Risco em aberto | Status |
|---:|---|---|---|---|---|---|
| 1 | ADR-008 | Qual SHA/digest implantado e qual ambiente é o primeiro alvo? | Bloquear código até owner apresentar SHA + image digest e baseline de release | main, staging, snapshot e5 ou baseline por ambiente comprovado | Implementar contra API/schema não implantado | PENDING_APPROVAL |
| 2 | ADR-001 | Como todos os writers formam estado coerente e resolvem conflito? | Revisão monotônica + snapshot privado; lease/fence para operações longas; stale command retorna conflito | serialização total, lease compartilhado, snapshot versionado, híbrida | Bypass de writer e lost update | PENDING_APPROVAL |
| 3 | ADR-005 | Onde ficam definições privadas e quem pode lê-las? | Separar storage/coleções e identidades; reader público + DTO allowlist | Filtrar no controller; DTO apenas; grants isoladas | Vazamento de gabarito ou campo novo | PENDING_APPROVAL |
| 4 | ADR-003 | Quais campos/taxonomias congelam por geração? | Versionar tudo que afeta sentido, renderização, ordem, validação ou navegação | Copiar toda taxonomia; referência global; versão global; híbrida | Experiência mutável sem publicação e duplicação | PENDING_APPROVAL |
| 5 | ADR-002 | Quando aluno fixa e perde geração? Qual versão avalia tentativa/progresso? | Pin de sessão pelo servidor + pin independente da tentativa | Latest always; por request; só tentativa; híbrida | Conteúdo e nota referirem versões diferentes | PENDING_APPROVAL |
| 6 | ADR-004 | Que referências e obrigações impedem exclusão? | Retenção por referência e obrigação, grace period a decidir; sem prazo arbitrário | ilimitada; janela fixa; por curso; híbrida | Perda de histórico ou retenção excessiva | PENDING_APPROVAL |
| 7 | ADR-006 | Unidade de publicação, restore e resposta em corrupção? | Candidate completo + seal + CAS único; leitor pinado; sem fallback live | in-place, snapshot legado, geração com head, coexistência gradual | Exposição parcial e rollback inseguro | PENDING_APPROVAL |
| 8 | ADR-007 | Ordem, coorte, owners e gates do rollout? | Fases independentes; flags off; writers antes de readers; cutover só com zero bypass | big-bang; shadow write por rota; gradual controlado | Estado híbrido e efeito público inesperado | PENDING_APPROVAL |

## 2. Ordem recomendada de aprovação

1. **Baseline (ADR-008)**: bloqueia interpretar todos os contratos e escolher arquivos de código.
2. **Consistência editorial (ADR-001)**: define revisão e conflito que tornam a origem de geração confiável.
3. **Segurança público/privado (ADR-005)** e **taxonomias (ADR-003)**: definem schema congelado e projeção antes do builder/reader.
4. **Sessão/progresso (ADR-002)** e **retenção (ADR-004)**: resolvem referências históricas antes de backfill e leitura versionada.
5. **Publicação atômica (ADR-006)**: depende dos anteriores.
6. **Migração gradual (ADR-007)**: sequência e rollout finais incorporam os gates aprovados.

A ordem não significa aceite implícito. Cada ADR deve receber decisão humana registrada e dono por papel (produto, backend, segurança, operação e privacidade quando aplicável). Se uma recomendação for rejeitada, registrar alternativa, trade-off e novos testes antes de liberar implementação.

## 3. Perguntas de aprovação por domínio

### Produto e experiência pedagógica

- Sessões continuam na geração anterior após republicação? Qual aviso permite migração voluntária?
- Qual janela permite tentativa aberta e submissão tardia?
- Em retirada urgente, sessão é revogada imediatamente ou há exceção pedagógica?
- Como progresso legado sem versão deve ser retomado?
- Restore deve parecer nova publicação ou retroceder explicitamente a experiência?

### Backend e dados

- Revisão é por trilha inteira ou agregado menor? Como taxonomias globais entram no revision token?
- Quem pode escrever metadata e manter revision monotônica em scripts/seeds?
- Qual erro externo representa conflito sem quebrar clientes?
- Quais schemas de bloco/evaluator antigos precisam permanecer suportados?

### Segurança, privacidade e operações

- Quais credenciais/coleções separam public reader, evaluator, builder, selector e maintenance?
- Quais referências são retenção obrigatória? Requer avaliação jurídica/privacidade?
- Quem aciona flags e quem autoriza corte/retirada?
- Qual estado operacional é preferível após corrupção: geração anterior ou indisponibilidade?

## 4. Evidência experimental e limites

O run da PoC 40686021030 (MongoDB 7.0.45 standalone; 15/15 integração, 26/26 unitários e 7/7 guardas) fornece evidência sobre o protocolo isolado. Não aprova nenhuma linha desta matriz nem comprova integração, grants, semântica de produto ou deploy da aplicação real.
