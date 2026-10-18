from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci-deploy.yml"


def test_coolify_deploy_webhooks_are_not_retried_automatically():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for job_name, next_job in (("deploy-staging", "deploy-production"),
                               ("deploy-production", None)):
        section = workflow.split(f"  {job_name}:", 1)[1]
        if next_job:
            section = section.split(f"  {next_job}:", 1)[0]
        assert "curl --fail --silent --show-error" in section
        assert "--retry" not in section
