# Relatório de recuperação da validação da fundação

## A. Resumo executivo

A fundação foi validada no commit `7aa01383e9b36b67d9109ab5060cec051a2133dc`, sem deploy, produção ou infraestrutura operacional. O PR #38 permanece aberto para integração manual.

## B. Git

- Base: `main` em `22dca64556338a8fa9aaa89ce627a4f4af72317d`.
- Branch: `codex/foundation-ci-e2e-recovery`.
- PR: https://github.com/Saitar0/trilhacodeprod/pull/38
- Commit validado: `7aa01383e9b36b67d9109ab5060cec051a2133dc`.

## C. Coordenação

O diagnóstico foi separado entre Docker/G2 e Playwright; uma revisão independente verificou escopo, cobertura, segurança e compatibilidade antes da execução final.

## D–E. Docker/G2

O workflow apontava para um teste ausente. O contrato histórico foi restaurado e o Compose foi alinhado ao isolamento por `--project-name`: portas parametrizadas, redes e volumes sem nomes globais fixos e ausência de `container_name`. O teste também trata explicitamente a ausência local do plugin Compose.

## F–G. Playwright E2E

A causa primária era o Vite sem `VITE_BACKEND_URL`, fazendo o frontend chamar a própria porta `5173` em vez da API descartável. O workflow passou a iniciar o frontend com a URL da API; login, navegação administrativa, confirmação de e-mail, progresso e submissão passaram sem skips, mocks ou aumento artificial de timeout.

## H. Segurança

Foram usados somente MongoDB 7, usuários e senhas sintéticos, diretório de e-mails de teste, serviços locais e recursos Docker efêmeros. Nenhum secret operacional, staging, Coolify, GHCR ou produção foi acessado.

## I–J. Testes e GitHub Actions

Run final: https://github.com/Saitar0/trilhacodeprod/actions/runs/41079604265

Backend/MongoDB, Frontend/Node 20, Docker/G2, Playwright E2E e resumo de homologação concluíram com `success`. O PyMongo foi atualizado para `4.18.3` para eliminar a vulnerabilidade reportada no CI anterior. Deploys staging e produção permaneceram `skipped`.

## K. Regressões

`git diff --check`, parse YAML e compilação Python passaram. A suíte final do workflow passou integralmente. O teste local específico não foi executado porque este host não possui `pytest`; a execução equivalente no CI passou.

## L. PR

PR #38 está aberta, limpa para merge e não foi integrada automaticamente.

## M. Limitações

Esta validação não comprova integração das branches Beta 1–9, migração curricular, C14–C16, writers editoriais, staging, deploy ou identidade operacional do baseline. O ADR-008 permanece bloqueado.

## N–O. Roadmap e próximo incremento

Manter as frentes Beta, curricular e editorial isoladas. O próximo incremento deve ser uma decisão explícita sobre baseline curricular e integração segura, não Beta 10.

## P. Veredito

**FUNDAÇÃO DA TRILHA CODE VALIDADA NO COMMIT DE CORREÇÃO — INTEGRAÇÃO E DEPLOY NÃO AUTORIZADOS**
