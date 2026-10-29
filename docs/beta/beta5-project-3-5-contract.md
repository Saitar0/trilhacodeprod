# Beta 5 — contrato experimental do projeto 3.5

## Inventário real

O manifesto Beta 4 e a conversão Beta 5 identificam 11 materiais associados ao projeto 3.5: um brief, quatro marcos M01–M04, uma rubrica comum e cinco checklists (quatro por marco e um checklist final). O inventário em `beta5-project-3-5-artifacts.json` lista para cada um ID, tipo, caminho, hash, ordem e IDs de origem, sem copiar corpos. A fonte permanece em estado `rascunho` na revisão `migration@147dc68:tracked-clean-first-phase-files`.

## Contrato

`beta_project_contract.py` representa projeto, artefatos, etapas, instruções, entregáveis, rubrica, critério e evidência de submissão. IDs e referências são validados; cada etapa aponta para artefato existente e ordem contínua. Respostas ou arquivos de aluno não foram criados. A rubrica é restrita. Brief/marcos são candidatos a material do aluno, mas ficam com visibilidade `PENDING_OWNER_REVIEW` e sem projeção pública até decisão explícita.

O contrato experimental não executa código, não avalia projetos, não recebe submissões e não adiciona modelos operacionais. Os critérios textuais do projeto requerem decisão humana. O backend não demonstrou uma representação segura de marcos, rubricas e evidências de submissão; é necessário adaptador e ACL antes da integração.
