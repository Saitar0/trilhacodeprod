# Beta 8.1 — Evidência de testes, isolamento e regressões

## Harness persistente

Executado pelo script `ops/beta8-1-security/run-local.ps1` no Docker Desktop local (`desktop-linux`, Engine Linux 29.8.2). A validação ocorreu antes de conectar ou gravar: MongoDB 7.0.43 pinado, replica set `rsB8`, imagem por digest, identificadores Docker e labels de execução, rede bridge interna exclusiva, nenhum port mapping, nenhum volume persistente, diretórios de dados em tmpfs e keyfile temporário readonly. API/HTTP roda como processo de harness isolado na mesma rede. As únicas credenciais são geradas para aquela execução.

O gate bloqueia overrides de contexto Docker, URI/identidade divergente e propriedade não comprovada. O cleanup re-inspeciona IDs e labels, número de participantes, volumes e imagem temporária; remove apenas recursos daquela execução. A última execução confirmou remoção do contêiner, rede e imagem; inspeção por label retornou zero recursos Beta 8.1. Nenhum localhost MongoDB, banco preexistente, staging ou produção foi acessado.

## Resultado da última execução

* Pytest offline no harness: **4 passed**.
* Prova persistente histórica Beta 8: **PASS** para gate/role, authority, promoção sintética e concorrência/revogação.
* Prova HTTP e persistente Beta 8.1: **PASS** para login ativo; atualização por route real; grant de recurso; negativas anônimo, token expirado, logout/revogação de sessão, usuário desativado, grant ausente, grant de outra trilha e admin sem grant; ausência de capability 503; Mongo negou escrita direta comum; CAS/ETag; replay idempotente; conflito/negação após revogação concorrente; histórico/auditoria; serviço real Beta 5 staging + autoridade experimental; preparador impedido de promover.
* Testes Playwright/frontend: não executados; esta entrega não alterou frontend e a prova concentrou-se na fronteira HTTP/Mongo.
* Suítes históricas completas C8–C16/Beta 5–7.2: não executadas em bloco. O harness executou a regressão persistente Beta 8 usada como base, além dos quatro testes Beta 8.1.
* Pytest no Python global da estação: não disponível. Ruff e Mypy foram executados em diretórios temporários fora do repositório, sem instalação global.
* Compilação sintática Python, `git diff --check` e validações JSON: resultados finais registrados no relatório depois da revisão.

Ruff 0.17.3 passou em todos os arquivos Python alterados. Mypy 2.4.1 passou nos cinco módulos de rota/serviço alterados (`--ignore-missing-imports --follow-imports=silent --python-version 3.11`): `Success: no issues found in 5 source files`. As instalações temporárias foram removidas.

## Falhas de integração encontradas e corrigidas

1. Windows PowerShell 5.1 não oferece `RandomNumberGenerator.GetBytes(int)` nem `Convert.ToHexString`; o runner passou a obter bytes por instância criptográfica compatível e zerá-los no cleanup.
2. PowerShell desembrulhava o único objeto JSON de `docker inspect`; as verificações de identidade/cleanup agora materializam arrays antes de validar cardinalidade.
3. O nome de banco inicialmente excedia limites/regex dos contratos C10/C12; foi limitado e alinhado ao prefixo estrito esperado.
4. A fixture de login usava `.invalid`, rejeitado corretamente pelo validador de e-mail; passou a usar endereço sintético de domínio de exemplo.
5. A rota mapeava `EditorialMutationDenied` como erro genérico 500; agora retorna 403 sanitizado e bloco não encontrado retorna 404.
6. A autoridade possui auditoria/history write-only; as asserções passaram a consultar as coleções com o provisionador isolado, sem ampliar privilégios do writer.

## Classificação

| Componente | Estado | Evidência |
|---|---|---|
| Contratos/offline do adapter | `OFFLINE_VERIFIED` | 4 testes unitários |
| Gate e negações MongoDB | `PERSISTENCE_VERIFIED` | Mongo descartável, roles autenticados |
| Login e rota existente | `HTTP_VERIFIED` | ASGI HTTP, rota real e dependências reais |
| Grant/CAS/fencing/auditoria/replay | `PERSISTENCE_VERIFIED` | C8/C10/C12 e coleções persistidas |
| Revogação concorrente | `PERSISTENCE_VERIFIED` | barreira controlada, revogação antes do commit |
| Serviço Beta 5 staging → autoridade | `PERSISTENCE_VERIFIED` | banco de staging e identidade preparadora separados |
| Contenção global dos writers | `NOT_VERIFIED` | somente PUT update e roles sintéticos |
| Segurança operacional IAM/credenciais | `BLOCKED` | nenhuma consulta permitida a ambiente operacional |

Veredito da Entrega D: **VALIDAÇÃO INTEGRADA PARCIAL — REGRESSÕES OU GARANTIAS PENDENTES**.
