# Frontend Trilha Code

Interface React 19 com TypeScript e Vite. O servidor de desenvolvimento fica na porta 3000; `VITE_BACKEND_URL` indica a URL da API que o navegador consegue acessar.

## Desenvolvimento

```sh
npm ci
npm start
```

Copie `.env.example` para `.env.local` e ajuste `VITE_BACKEND_URL` se a API não estiver em `http://localhost:8000`.

## Verificações

```sh
npm run typecheck
npm run lint
npm test
npm run build
```

O bundle de produção é gerado em `dist/`. `frontend/Dockerfile.prod` instala as dependências com `npm ci`, compila a aplicação e serve o conteúdo com Nginx.

## Variáveis

- `VITE_BACKEND_URL`: URL base da API, necessária para a imagem de produção e incorporada durante o build.
- `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT` e `VITE_SENTRY_RELEASE`: configuração opcional do Sentry no navegador.

No Coolify, cadastre essas configurações como variáveis de build. Consulte o [guia de deploy](../DEPLOY.md) para os ambientes de staging e produção.
