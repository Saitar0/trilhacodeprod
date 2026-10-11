# Auth Testing Playbook

1. MongoDB: `db.users.find({role:"admin"})` — password_hash starts with `$2b$`; unique index on users.email.
2. API:
```
curl -c cookies.txt -X POST $URL/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@trilhacode.dev","password":"Admin@123"}'
curl -b cookies.txt $URL/api/auth/me
```
Login returns user object and sets access_token + refresh_token cookies. 5 failed logins => 15 min lockout (429).
