---
arquivo_id: "f9-41-1-02-timeout-retry-circuit-breaker-01-teoria"
parent_key: "41.1"
tipo_arquivo: "theory"
assunto: "02_timeout_retry_circuit_breaker"
ordem: 2
itens_origem: ["### 2. Timeout, retry e circuit breaker"]
---


### 2. Timeout, retry e circuit breaker
- **Timeout:** limite por tentativa, compatível com o deadline total. Diferencie timeout de conexão e de resposta quando a plataforma permitir. Defina também cancelamento/propagação; cancelar a espera não cancela automaticamente o efeito remoto.
- **Retry:** use apenas para falhas que podem se resolver e operações repetíveis com segurança. Limite tentativas, use backoff exponencial com jitter, respeite `Retry-After` quando aplicável e não ultrapasse o deadline. Erro de validação ou autorização normalmente não melhora com repetição.
- **Amplificação:** retries em API, biblioteca, gateway e serviço podem multiplicar chamadas. Conte as tentativas de todas as camadas e imponha um orçamento. Sobrecarga pode produzir timeouts que disparam mais retries e agravam a falha.
- **Circuit breaker:** observa falhas recentes e interrompe chamadas provavelmente inúteis. No estado fechado, permite chamadas; aberto, falha rápido; semiaberto, deixa passar poucas tentativas para testar recuperação. Ele não substitui timeout, tratamento de erro ou retry bem dimensionado.
- **Bulkhead e fallback:** limites de concorrência isolam recursos para uma dependência não consumir todas as conexões ou threads. Fallback só é válido se o resultado alternativo respeitar a regra de negócio. Mostrar um dado desatualizado pode ser aceitável; afirmar que pagamento foi concluído sem confirmação não é.

Instrumente tentativas, timeout, latência, estado do breaker, saturação e resultado final. Um breaker aberto deve ser visível e ter procedimento para distinguir dependência indisponível de falha de configuração.

**Checagem:** uma operação que falha por cartão inválido deve ser repetida? Não; a falha é permanente até que os dados mudem.

