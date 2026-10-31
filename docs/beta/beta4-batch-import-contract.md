# Beta 4 — contrato experimental de conversão em lote

## Pipeline

`Descoberta → parsing seguro → validação Pydantic estrita → normalização determinística → validação de IDs/relações → payload C16 → dry-run do importador → persistência descartável → leitores reais de serviço`.

O módulo `backend/curriculum_contract/experimental_beta_first_phase_converter.py` reutiliza os value objects estritos da Beta 3; não cria IAM ou autoridade editorial concorrente. Ele lê somente os arquivos Markdown da fonte segmentada, verifica o SHA-256 monolítico autorizado de 1.1, rejeita chaves YAML duplicadas, IDs duplicados, quiz/gabarito divergentes, referências inválidas e tipos desconhecidos. A construção completa e as referências do lote são validadas antes de se chamar o writer.

IDs de destino são derivados do ID curricular estável, item de origem e posição. JSON canônico ordenado produz `payload_sha256` e `canonical_manifest_sha256`; nenhuma data de execução entra nesses campos. Uma alteração de qualquer byte de origem altera o hash agregado da unidade.

## Estados

| Estado | Significado |
|---|---|
| `CONVERSION_SUCCESS` | Parsing concluído sem destinos pendentes. |
| `CONVERSION_SUCCESS_WITH_WARNINGS` | Contrato convertido, com campos fora do destino atual. É o estado observado nas dez unidades. |
| `CONVERSION_BLOCKED` | Tipo/campo incompatível ou validação estrutural impede payload seguro. |
| `PERSISTENCE_NOT_TESTED` | Nenhum writer persistente foi chamado. |
| `PERSISTENCE_SUCCESS` | Somente para a prova descartável concluída e conferida. |
| `PERSISTENCE_FAILED` | Falha persistente ou invariantes de verificação divergentes. |

“Success with warnings” não é autorização para publicar. O lote atual ainda omite materiais cujo destino/ACL não está demonstrado. A primeira fase toda gerou 10 unidades, 44 nós, 161 blocos e 21 relações internas no payload; o manifesto lista 30 relações de origem, incluindo relações externas não persistidas.

## Identidade e recuperação

O serviço real deriva `operation_id` do payload e identifica o job pela trilha/operação; dry-run executa validação e plano sem gravar. A prova repetiu o payload serialmente e observou replay idempotente sem duplicar nós, blocos, relações ou auditoria. O lock de job permite retomar o mesmo payload após falha simulada, mas isso não é prova de idempotência concorrente nem de transação global.

## Segurança e limites

O payload define trilha e nós como `private`/`draft`. Os gabaritos de quiz ficam somente em blocos draft no banco descartável; respostas de exercícios, rubricas e projetos não são persistidos. A prova chamou funções de serviço diretamente com ator sintético; não exercitou rota, JWT, sessão, autorização por grant, publicação ou aluno autenticado. Não integra o conversor ao startup nem às rotas.

Manifesto agregado: 30 tópicos, 42 segmentos, 30 arquivos de quiz, 44 questões, 26 exercícios, 11 artefatos de projeto, 39 referências, 30 relações de origem e 161 blocos. Nenhum corpo privado aparece no JSON.
