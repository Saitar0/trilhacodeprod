# Beta 3 — conclusão, conexões e referências

## Critério de conclusão

A fonte declara um critério textual de conclusão para a unidade. O conversor o preserva literalmente em `CompletionCriterion.source_text`, marca `interpretation=unstructured_text`, mantém `automated_rule=None` e requer política humana antes de automatizar. A prova não adiciona percentual, nota de corte ou equivalência entre entrega e domínio.

O backend possui progresso e submissões, mas esta unidade não mapeia o texto a uma regra validada que combine leitura, quiz respondido/aprovado, exercício enviado/corrigido ou domínio. O destino operacional é `REQUIRES_ADAPTER`. Progresso observado e domínio pedagógico continuam conceitos distintos.

## Conexões curriculares

Foram preservadas três linhas de conexão do texto: uma `Complementar` para a unidade 1.2 e duas `Relacionado` para unidades 7.3 e 18.1. `CurricularRelation` retém tipo, caminho, âncora, rótulo e linha original. Não há resolução para IDs de nós no piloto; `target_node_ref=None` e `enforced=False`. Menção ou relação conceitual não é convertida em pré-requisito obrigatório.

O importador C16 exige refs de origem/destino existentes no próprio payload e tipo de relação presente na taxonomia. Como os destinos estão fora do escopo da unidade-piloto, nenhuma relação C16 foi enviada. Uma fase completa deve resolver referências contra manifestos aprovados, validar tipos, detectar ciclos e distinguir associação conceitual de requisito de matrícula.

## Referências

As duas referências da unidade mantêm título, descrição, URL, ordem e trecho Markdown original no contrato intermediário. O backend atual aceita `reference.data.citation` e `url`; descrição não tem campo demonstrado. O payload guarda título e URL, e a descrição permanece classificada `REQUIRES_ADAPTER` no manifesto.

Não foram consultadas URLs externas. Integrar descrições exige adaptar o schema/leitor com decisão de ACL e renderização; não truncar ou concatenar descrição em `citation` para ocultar incompatibilidade.
