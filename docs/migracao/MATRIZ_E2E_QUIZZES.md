# Matriz E2E — quizzes

Os testes abaixo executam frontend, backend, autenticação e persistência em ambiente local descartável. Os mocks de rede limitam-se a falhas controladas e a simular a resposta perdida; os fluxos de negócio usam HTTP real.

| Cenário | Evidência / spec | Resultado |
|---|---|---|
| Login e acesso ao tópico | `quiz-api-real.spec.ts`, ciclo principal | Aprovado |
| Carregamento e renderização das questões | Resposta pública real com 10 questões | Aprovado |
| Gabarito e explicações ocultos no payload público | Allowlist de campos protegidos no corpo HTTP | Aprovado |
| Acesso sem autenticação | GET público via cliente anônimo | 401 |
| Revisão antes do limite | GET de revisão antes de tentativas | 403 |
| Cliente tenta enviar nota/aprovação | POST com `passed`, `score_percent` e número de tentativa | 422 |
| Primeira tentativa e limiar | 7 de 10 respostas corretas | 70%, aprovado, duas restantes; sem revisão |
| Segunda tentativa e melhor nota | 9 de 10; resposta da conexão descartada após gravação | 90%; histórico registra uma vez |
| Retry com chave igual após resposta perdida | Reabertura da aba e repetição de corpo/chave | Mesmo ID da tentativa, sem duplicação |
| Retry após reinício do backend | Probe de API separado, usando corpo/chave salvos pelo teste para a tentativa 2 | Mesmo ID; histórico continua em três |
| Terceira tentativa | 6 de 10 | Não aprovado; melhor nota continua 90%; revisão liberada somente então |
| Gabarito e explicações após o limite | Revisão autenticada após terceira tentativa | Aprovado |
| Quarta tentativa | Nova chave depois do esgotamento | 409; histórico permanece com três |
| Histórico entre usuários | Admin consulta histórico do quiz do estudante | Total zero para admin |
| Clique/submissão duplicada | Dois eventos `submit` enquanto tentativa está pendente | Um POST observado |
| Falha anterior à gravação e reload | POST abortado antes de chegar à API, depois reenviado | Mesma chave, uma tentativa registrada |
| Sessão expirada | Cookie removido e requisição retomada | API 401; interface informa sessão expirada |
| API indisponível | GET abortado no navegador | Erro recuperável; nenhuma correção local alternativa |
| Rate limit de leitura | Burst concorrente de 30 GET reais | 429 e `Retry-After`; botão bloqueado durante espera |
| Rate limit de publicação | Burst concorrente de publicações reais | 429 e `Retry-After` |
| Versão alterada | Nova publicação com conteúdo diferente | Nova versão e contador 0/3 |
| Republicação sem mudança | Publicação do mesmo snapshot | Reutiliza a mesma versão |
| Flag ligada | Build Vite `e2e_on` | Valor incorporado `"true"`; fluxo API usado |
| Flag desligada | Build Vite `e2e_off` | Valor `"false"`; nenhuma chamada `/api/quizzes/` |
| Flag ausente | Build Vite `e2e_absent` | Valor incorporado `void 0`; padrão desativado |

## Cenários não comprovados

- A interface não demonstrou recuperação automática da chave pendente depois de fechar a aba; o `sessionStorage` não oferece essa durabilidade. Após reabrir, o teste confirmou o histórico persistido; o replay pós-reinício foi uma chamada de API com o artefato salvo pelo teste.
- Não foi injetado timeout cronometrado de socket; foram simulados abort antes da gravação e perda da resposta após a gravação.
- O E2E não disparou submissões concorrentes para competir pelas três vagas. Esse cenário continua exigindo prova integrada antes de ativação; a suíte cobriu o limite sequencial, clique duplicado e bursts de outras rotas.

## Limites da evidência

- MongoDB 9.0.2 local em replica set de um membro. Não comprova a topologia de produção ou failover multi-membro.
- A simulação de rede aborta uma requisição/resposta no navegador; não injeta falhas físicas no armazenamento.
- A tela sob flag desligada continua no renderer legado, cujo payload de conteúdo não contém `correct_index`. A integração não mantém correção local insegura como fallback, mas o quiz legado fica funcionalmente incapaz de confirmar a resposta correta.
- A pontuação imediata agregada pode ser inferida em um quiz de uma questão. Não foi modificada.
- As compilações de produção foram gravadas em pasta temporária, fora de `frontend/dist`; a flag não foi configurada em ambiente de usuário.
- Não foi executado E2E contra ambiente de produção nem banco compartilhado.
