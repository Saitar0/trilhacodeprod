# Beta 8.1 — Integração experimental do IAM ativo

## Escopo

Esta prova conecta uma operação HTTP já existente (`PUT /api/blocks/{block_id}`) à autenticação ativa do FastAPI, à projeção experimental C12 de grants, à autoridade C8/C10 e às permissões MongoDB de identidades sintéticas. A composição com `beta8_1_editorial_runtime` é feita somente pelo harness descartável. `server.py` não constrói nem injeta essa capacidade.

O runtime comum retorna `503` para a edição protegida quando a capacidade não foi composta. Não há fallback para `services.blocks.update_block` com escrita direta. O serviço legado continua disponível como símbolo, mas a identidade comum do harness não pode escrever em `content_blocks`; a chamada direta foi negada pelo próprio MongoDB.

## Caminho exercitado

1. `POST /api/auth/login` executa a rota real e cria a sessão no MongoDB descartável.
2. O endpoint usa `require("content.write")` e `current_user` reais; identidade e sessão vêm do cookie JWT e das coleções reais `users` e `auth_sessions`.
3. A rota verifica o espelhamento experimental do principal e da sessão C12, além da permissão global já existente.
4. `services.blocks.update_block` resolve o bloco e sua trilha no servidor. `Beta8EditorialMutationBoundary` exige o grant `block.update`, estado `draft`, revisão esperada e fence.
5. A operação C8/C10 e seus participantes condicionais registram, na mesma transação, os fatos C12, a sessão/usuário ativos, o bloco, histórico e auditoria.
6. Resposta HTTP expõe somente o bloco permitido, ETag de revisão e sinal de replay; chaves e tokens não são retornados.

## Revogação e ponto de confirmação

A autorização inicial ocorre antes da preparação e é repetida no commit. A operação e a revogação atualizam condicionalmente os mesmos documentos C12 na fronteira transacional. A revogação é efetiva quando sua transação confirma. Se a operação concorrente perde a serialização/confirmação, retorna negação ou conflito e o bloco permanece sem alteração. O guard adicional condiciona `users` e `auth_sessions` ativos no mesmo cliente/transação C8/C10.

O teste HTTP usou uma barreira antes da confirmação: a operação autenticada parou depois da validação, o grant foi revogado e confirmado, e a escrita foi liberada. A resposta foi negada; revisão e conteúdo não avançaram. Isto valida a semântica no MongoDB 7 replica set sintético, não a configuração ou o IAM operacional.

## Resultados HTTP persistentes

Passaram: login real; anônimo 401; JWT expirado 401; sessão após logout 401; usuário desativado 401; ausência de capacidade 503; ausência de grant 403; grant de outra trilha 403; admin sem grant por recurso 403; atualização com grant válido 200; CAS/ETag; retry idêntico sem duplicar histórico/auditoria; revogação concorrente negada.

O erro de autorização é sanitizado e não revela o escopo da trilha. A auditoria de sucesso e o histórico foram verificados pelo provisionador isolado; a identidade de autoridade possui inserção, mas não leitura, nessas coleções.

## Limites

* A projeção C12 e os grants continuam sintéticos; não existe leitura/gravação do IAM operacional.
* A rota usa a autoridade experimental somente na composição de teste. O startup comum não foi habilitado.
* O role da autoridade precisa atualizar `content_blocks` para executar o participante. O MongoDB autoriza por coleção, não por função, documento ou protocolo; um processo com essa credencial ainda poderia escrever diretamente. Não há contenção de um processo de autoridade comprometido.
* Só a atualização de bloco foi integrada. Outras rotas de escrita editorial continuam fora desta prova e não são consideradas protegidas operacionalmente.

Veredito da Entrega A: **IAM INTEGRADO AOS GRANTS EDITORIAIS NO RUNTIME DE TESTE — ATIVAÇÃO OPERACIONAL PENDENTE**.
