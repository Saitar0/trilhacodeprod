from pathlib import Path


def test_g2_workflow_remains_manual_fixed_command_and_main_only():
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github/workflows/g2-staging-preflight.yml").read_text()
    assert "  workflow_dispatch:" in workflow
    assert "    if: github.ref == 'refs/heads/main'" in workflow
    assert "permissions: {}" in workflow
    assert "StrictHostKeyChecking=yes" in workflow
    assert "'trilhacode-g2-preflight'" in workflow
    assert "workflow_run:" not in workflow
    assert "push:" not in workflow
    assert "pull_request:" not in workflow


def test_g2_workflow_never_dispatches_or_runs_preflight_in_pr_validation():
    root = Path(__file__).resolve().parents[2]
    ci = (root / ".github/workflows/ci-deploy.yml").read_text()
    assert "g2-staging-preflight.yml" not in ci
    assert "trilhacode-g2-preflight" not in ci
