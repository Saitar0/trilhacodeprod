# Conclusão da segurança do frontend

Data: 16/10/2026

## Resumo

A auditoria inicial retornou 13 vulnerabilidades: 2 críticas, 5 altas, 4 moderadas e 2 baixas. Foram corrigidas com atualizações controladas do Vitest, ESLint/AJV e migração do Tailwind CSS para a major 4. A auditoria final não encontrou vulnerabilidades. O code splitting continuou presente no build.

## Dependências atualizadas

| Dependência | Antes | Depois | Motivo |
|---|---:|---:|---|
| `vitest` | 3.2.7 | 4.1.11 | Corrigir os avisos críticos relacionados ao Vitest/Tinypool e o aviso do `@vitest/mocker` |
| `@eslint/js` | 9.23.0 | 9.39.5 | Alinhar a configuração com o ESLint atualizado |
| `eslint` | 9.23.0 | 9.39.5 | Corrigir o aviso em `@eslint/plugin-kit` (resolvido para 0.4.1) |
| `ajv` | 8.17.1 | 8.20.0 | Corrigir ReDoS ao usar a opção `$data` |
| `tailwindcss` | 3.4.17 | 4.3.3 | Corrigir os avisos altos de Braces/Micromatch e transitivos PostCSS no ramo Tailwind 3 |
| `@tailwindcss/postcss` | — | 4.3.3 | Usar o plugin PostCSS separado requerido pelo Tailwind 4 |

`vite` permaneceu na major 6 (lockfile: 6.4.4), `typescript` permaneceu em 5.4.5 e `postcss` em 8.5.28. Os demais avisos resolvidos desapareceram da árvore final ao atualizar as dependências acima.

## Vulnerabilidades e exposição

A auditoria inicial reportou:

- **Críticas (2):** `tinypool` (RCE por prototype pollution) e cadeia do Vitest; corrigidas com Vitest 4.1.11.
- **Altas (5):** `braces`, `chokidar`, `fast-glob`, `micromatch` e Tailwind CSS 3; corrigidas na migração para Tailwind 4.3.3.
- **Moderadas (4):** `@vitest/mocker`, `ajv`, `postcss-nested` e `postcss-selector-parser`; corrigidas com Vitest 4.1.11, AJV 8.20.0 e Tailwind 4.3.3.
- **Baixas (2):** ESLint e `@eslint/plugin-kit`; corrigidas com ESLint 9.39.5 / `@eslint/plugin-kit` 0.4.1.

Vitest, ESLint, Tailwind e PostCSS são ferramentas de teste, lint ou compilação e não foram importadas no código de aplicação. AJV consta em `dependencies`, mas a busca no código `src` não encontrou uso. A auditoria final registrou **0 vulnerabilidades**.

## Mudanças major e compatibilidade

- Vitest 3 → 4.1.11. Compatível com a versão Vite 6 usada pelo projeto e com Node 20 configurado no CI. A API de teste existente continuou executando.
- Tailwind CSS 3 → 4.3.3. `src/index.css` passou a importar Tailwind e carregar explicitamente a configuração JavaScript existente; `postcss.config.js` usa `@tailwindcss/postcss`.
- TypeScript, ESLint, Vite e Vitest passaram por typecheck, lint, build e testes locais.
- O Tailwind 4 requer navegadores modernos (Safari 16.4+, Chrome 111+, Firefox 128+). Se o público do Trilha Code precisar de navegadores mais antigos, há risco de incompatibilidade visual/funcional.
- O CSS compilado aumentou de aproximadamente 69 KB para 88 KB. O build passou e manteve chunks separados para páginas e componentes. Não foi feita comparação visual no navegador; diferenças de defaults do Tailwind 4 ainda precisam de validação visual humana.

## Arquivos alterados

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/postcss.config.js`
- `frontend/src/index.css`
- `FRONTEND_SECURITY_COMPLETION.md` (este relatório)

Não alterei o workflow do CI. Ele segue usando Node 20, `npm ci`, typecheck, lint, Vitest, build e `npm audit --audit-level=high`.

## Verificações

| Verificação | Resultado |
|---|---|
| Auditoria inicial `npm audit --json` | 13 vulnerabilidades (2 críticas, 5 altas, 4 moderadas, 2 baixas) |
| Análise `npm ls` | Identificadas as cadeias afetadas; depois das atualizações, versões seguras confirmadas para Vitest, ESLint, `@eslint/plugin-kit`, AJV e Tailwind |
| `npm run typecheck` | **Passou** |
| `npm run lint` | **Passou** |
| `npm test` | **Passou:** 2 arquivos, 4 testes |
| `npm run build` | **Passou**, com aviso existente de chunks maiores que 500 KB; code splitting preservado |
| `npm audit --audit-level=high` | **Passou:** 0 vulnerabilidades |
| Instalação limpa `npm ci` | **Não confirmada localmente:** a instalação no Windows ficou sem progresso por mais de dois minutos e foi interrompida. O lockfile foi gerado pelo npm, mas a instalação limpa deve ser confirmada no CI Linux antes de deploy. |

Na primeira execução local dos testes, o Vitest foi bloqueado por `EPERM` ao renomear cache temporário no sandbox Windows. A repetição fora da pasta temporária restrita passou integralmente; o CI Linux não usa esse sandbox do Windows.

## Rollback

As quatro alterações funcionais do frontend estão limitadas aos arquivos listados acima. Como esses arquivos estavam sem alterações locais antes desta tarefa, o rollback pode ser feito com `git restore frontend/package.json frontend/package-lock.json frontend/postcss.config.js frontend/src/index.css`. O relatório pode ser mantido para histórico ou removido separadamente.

## Estado de CI e deploy

Nenhum push nem deploy foi realizado. A configuração do workflow permanece intacta e o teste de auditoria que ela executa passou localmente. A instalação limpa não foi concluída neste Windows; portanto, aguarde o CI executar `npm ci` e todas as etapas do job frontend antes de promover qualquer deploy.
