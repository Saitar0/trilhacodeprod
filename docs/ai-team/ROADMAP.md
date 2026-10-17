# Roadmap técnico

Atualizado em 17/10/2026 a partir de `main` (`27a98964`) e da leitura da CI, dos testes e da documentação do repositório. Prioridades descrevem oportunidades observadas, não bugs confirmados.

| Prioridade | Oportunidade e evidência | Impacto esperado | Esforço | Dependências | Risco | Critério verificável |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Validar a configuração dos arquivos Compose na CI. `.github/workflows/ci-deploy.yml` valida backend e frontend, mas não executa `docker compose config` para `compose.yaml` e `compose.qa.yaml`. | Detectar cedo erros de sintaxe/interpolação nos ambientes locais e de QA. | Baixo | Docker Compose disponível no runner e variáveis de exemplo documentadas. | Baixo; exige lidar com variáveis obrigatórias sem expor valores. | Um job de CI valida ambos os arquivos com valores fictícios e não inicializa containers nem bancos. |
| P2 | Adicionar cobertura E2E para fluxos de estudante e administração. A suíte de interface contém testes em `App.test.tsx`, `AuthContext.test.tsx` e `lib/api.test.ts`; não foi encontrado workflow/browser E2E. | Detectar regressões em navegação e fluxos completos que os testes unitários não cobrem. | Médio | Escolha de runner, ambiente de API e dados descartáveis. | Médio; evitar uso de credenciais ou banco compartilhado. | Fluxos críticos automatizados em ambiente descartável e executados na CI. |
| P2 | Acompanhar o tamanho dos bundles do frontend. `PHASE2R5_RELEASE_REVIEW.md` registra aviso do Vite para um chunk de ícones acima de 500 KB. | Reduzir ou evitar regressão no carregamento inicial. | Baixo a médio | Medição repetível do build e análise de importações. | Baixo; otimização pode alterar carregamento de ícones. | Definir um limite baseado em medição atual e demonstrar que o build o respeita sem quebrar telas. |

## Itens não selecionados nesta missão

Nenhum dos itens acima foi reproduzido como falha de runtime nesta auditoria. Não remover dependências, alterar o seed ou mudar lógica de produto sem uma verificação direcionada. O trabalho atual limita-se à documentação permanente da equipe.
