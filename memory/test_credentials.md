# Test Credentials — Trilha Code

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| admin   | admin@trilhacode.dev   | Admin@123  |
| editor  | editor@trilhacode.dev  | Editor@123 |
| student | aluno@trilhacode.dev   | Aluno@123  |

Seeded on backend startup from backend/.env (ADMIN_*, EDITOR_*, STUDENT_*).

Auth endpoints: POST /api/auth/register, POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me, POST /api/auth/refresh
Auth uses httpOnly cookies (access_token 15min, refresh_token 7d); Bearer header also accepted.
