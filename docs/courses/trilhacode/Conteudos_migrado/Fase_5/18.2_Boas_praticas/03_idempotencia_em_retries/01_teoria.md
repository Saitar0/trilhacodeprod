---
arquivo_id: "f5-18-2-03-idempotencia-em-retries-01-teoria"
parent_key: "18.2"
tipo_arquivo: "theory"
assunto: "03_idempotencia_em_retries"
ordem: 3
itens_origem: ["4. Idempotência em escritas sujeitas a retry"]
---

### 4. Idempotência em escritas sujeitas a retry
Uma conexão pode cair depois que o servidor concluiu uma operação, mas antes que o cliente receba a resposta. O cliente então não sabe se deve tentar novamente. Para um POST que não é idempotente por definição, a aplicação pode adotar uma chave de idempotência: um identificador gerado pelo cliente para reconhecer retries da mesma intenção. Esse cabeçalho e suas regras são uma convenção implementada pelo serviço; não presuma que toda API aplica o mesmo comportamento.

Defina o escopo da chave, por exemplo por cliente autenticado e operação; calcule ou guarde uma impressão digital dos parâmetros; e persista chave, estado e resultado de forma coordenada com o efeito. Mesma chave e mesmo payload repetidos devem retornar o resultado acordado sem repetir o efeito. Mesma chave com payload diferente deve ser recusada de modo documentado, por exemplo como conflito. Duas requisições concorrentes com a mesma chave precisam ser serializadas ou coordenadas por restrição/controle atômico. Defina retenção e limpeza: após expirar e apagar a chave, um retry tardio pode executar novamente.

Uma transação do banco pode coordenar o registro da chave e um efeito no mesmo banco; ela não torna atômico, por si só, um efeito externo como cobrança em outro serviço. Nesse caso, use idempotência também na dependência externa ou um fluxo durável apropriado. Stripe documenta uma implementação própria como exemplo, não um padrão universal. [Stripe — Idempotent requests](https://docs.stripe.com/api/idempotent_requests).

