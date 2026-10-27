# Autenticação, confirmação e recuperação de conta

## Política de cadastro

O cadastro é público. Senhas novas devem ter ao menos 12 caracteres e até 72 bytes em UTF-8, limite compatível com o bcrypt usado pelo backend. O login continua aceitando senhas existentes menores para não bloquear contas legadas. Uma conta recém-criada não recebe cookies de sessão até confirmar o e-mail.

Contas anteriores sem `email_verified` continuam habilitadas. Somente `email_verified: false` bloqueia login, refresh e todas as rotas protegidas pelo `current_user`. Novas contas recebem explicitamente esse valor como falso.

O link de confirmação expira em 24 horas. O servidor guarda somente o SHA-256 do token aleatório; emissão de outro link substitui o anterior. O consumo é uma atualização atômica e remove hash e expiração, impedindo reutilização. Links expirados, usados ou inválidos recebem a mesma resposta de erro.

## Limites de abuso

Os limites usam buckets de tokens guardados na coleção `login_attempts`, reutilizando seu índice TTL existente; a reposição é gradual e não libera uma nova rajada quando o relógio cruza o início de um minuto ou hora. Cada alteração do contador é atômica no MongoDB, compartilhada entre instâncias, e usa o relógio do servidor Mongo. Identificadores de IP/e-mail usam HMAC com o segredo da aplicação e os documentos de contador usam `_id` hash, sem guardar IP ou e-mail em claro. O monitor TTL do MongoDB faz a limpeza depois de uma hora sem atividade.

| Ação | Limite |
| --- | --- |
| Cadastro | 20 por IP/hora e 3 por e-mail/hora |
| Login | capacidade inicial de 120 por IP; reposição de 120 por minuto; também há bloqueio por 5 falhas para o par IP/e-mail em 15 minutos |
| Reenvio de confirmação | 10 por IP/hora e 3 por e-mail/hora |
| Pedido de recuperação | 10 por IP/hora e 3 por e-mail/hora |
| Consumo de confirmação ou recuperação | capacidade de 60 por IP; reposição de 60 por minuto |
| Alteração de senha autenticada | capacidade de 30 por IP; reposição de 30 por hora |

Cadastro, reenvio e recuperação retornam mensagens genéricas para não revelar se um endereço está cadastrado. O envio ocorre após iniciar a resposta HTTP. O login também usa mensagem igual para senha incorreta e conta ainda não confirmada.

## Transporte de e-mail

O backend usa a biblioteca padrão do Python (`smtplib`), sem credenciais ou dependência de provedor embutidas. Produção exige `EMAIL_TRANSPORT=smtp`, host, remetente e TLS. Staging pode usar `local` para previews descartáveis; esse transporte grava mensagens em disco e não entrega e-mail. Defina `SMTP_STARTTLS=true` para um relay com STARTTLS (normalmente porta 587), ou `SMTP_SSL=true` para conexão TLS desde o início; não habilite os dois. `SMTP_USERNAME` e `SMTP_PASSWORD` são opcionais para relays sem autenticação, mas devem ser configurados juntos quando o relay exigir login. O remetente precisa estar autorizado pelo provedor.

Variáveis de runtime:

| Variável | Uso |
| --- | --- |
| `EMAIL_TRANSPORT` | `smtp` para entrega de e-mail e obrigatório em produção; `local` para desenvolvimento, teste descartável e preview de staging |
| `SMTP_HOST`, `SMTP_PORT` | Relay e porta SMTP |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | Credenciais do relay, armazenadas como segredo de runtime |
| `SMTP_FROM_EMAIL` | Endereço remetente validado pelo provedor |
| `SMTP_STARTTLS`, `SMTP_SSL` | Modo de criptografia SMTP; exatamente um deve ser habilitado |
| `LOCAL_EMAIL_DIR` | Diretório do transporte local; arquivos `.eml` recebem permissões restritas e contêm links ativos. Nunca use esse transporte em produção. |

Sem provedor, `EMAIL_TRANSPORT=local` grava mensagens `.eml` num diretório local de desenvolvimento/teste, sem enviar pela rede. Os testes usam um diretório temporário removido no teardown. Um servidor local de produção não substitui um relay operacional e monitorado: configure o provedor antes de abrir cadastro ao público. Falhas de envio não expõem detalhes do relay, destinatário ou token na resposta HTTP nem nos logs; o usuário pode pedir novo link dentro dos limites.

## Rotas

- `POST /api/auth/register`: cria conta pendente e solicita confirmação.
- `POST /api/auth/verify-email`: consome `{ "token": "..." }` uma única vez.
- `POST /api/auth/resend-verification`: solicita novo link por e-mail.
- `POST /api/auth/password-reset-request`: solicita link de recuperação; resposta genérica.
- `POST /api/auth/password-reset`: consome token de uma hora e troca a senha; revoga sessões existentes.
- `POST /api/auth/password`: exige sessão, senha atual e nova senha de pelo menos 12 caracteres; revoga as sessões existentes.

## Procedimento de entrega e recuperação

Antes de staging/produção, forneça os valores SMTP pelo gerenciador de segredos do ambiente, confirme conectividade de saída à porta TLS escolhida e valide remetente, recebimento, spam e bounce com uma caixa de teste autorizada. Não inclua senha SMTP ou tokens de teste em commits/logs.

Os limitadores reutilizam `login_attempts.last` e não exigem um novo índice nem mudança do manifesto G2. Em rollout, mantenha a etapa de índices já existente, aguarde health/ready e confirme os checks G2 vigentes. Para reversão de código, mantenha a configuração SMTP; registros hashados de limite expiram pelo índice TTL existente e são ignorados por versões antigas.

Uma senha redefinida revoga cookies antigos ao aumentar `token_version`; peça login novamente. Tokens expirados/consumidos podem ser substituídos por nova solicitação dentro dos limites. O procedimento de suporte não deve ler tokens ou senhas pelo banco; use reenvio/recuperação por e-mail.
