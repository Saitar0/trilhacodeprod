import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "ops/g2/trilhacode-g2-preflight-run"
MANIFEST_PATH = REPO_ROOT / "ops/g2/preflight-manifest-v1.json"


def _runner_tools():
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    flock = shutil.which("flock")
    if os.name != "posix" or not bash or not jq or not flock:
        pytest.skip("G2 runner harness requires POSIX bash, jq, and flock (provided on Ubuntu CI)")
    return bash, jq, flock


def _fake_docker(path: Path) -> None:
    path.write_text(r'''#!/usr/bin/env bash
set -eu
state="$G2_TEST_STATE"
id='0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
mode="$G2_TEST_MODE"
case "$1" in
  network)
    if [[ "$mode" == network_failure ]]; then exit 1; fi
    cat <<JSON
[{"Name":"trilhacode-g2-preflight-internal","Internal":true,"Containers":{"$id":{"Name":"/test-mongo","IPv4Address":"172.22.0.2/24","Aliases":["mongo"]}}}]
JSON
    ;;
  image) [[ "$mode" == image_failure ]] && exit 1 || exit 0 ;;
  inspect)
    shift
    if [[ "$1" == -f ]]; then
      format="$2"; target="$3"
      case "$format" in
        '{{.Id}}') printf '%s\n' "$id" ;;
        '{{.State.Running}}') printf 'true\n' ;;
        '{{index .Config.Labels "com.trilhacode.g2-run"}}') [[ -f "$state" ]] || exit 1; sed -n '2p' "$state" ;;
        *) exit 1 ;;
      esac
    else
      [[ -f "$state" ]] && exit 0 || exit 1
    fi
    ;;
  ps)
    if [[ -f "$state" ]]; then printf '%s\n' "$id"; fi
    exit 0
    ;;
  rm)
    [[ "$mode" == cleanup_failure ]] && exit 1
    rm -f "$state"
    ;;
  run)
    while (($#)); do
      case "$1" in
        --name) name="$2"; shift 2 ;;
        --label) label="$2"; shift 2 ;;
        --cidfile) cidfile="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    printf '%s\n%s\n%s\n' "$name" "${label#*=}" "$id" > "$state"
    if [[ "$mode" != signal_before_cidfile ]]; then printf '%s\n' "$id" > "$cidfile"; fi
    if [[ "$mode" == canary ]]; then printf '%s\n' 'private-canary-value' >&2; exit 1; fi
    if [[ "$mode" == signal_wait ]]; then sleep 60; exit 0; fi
    if [[ "$mode" == signal_before_cidfile ]]; then sleep 60; exit 0; fi
    printf '%s' "$G2_TEST_OUTPUT"
    exit "$G2_TEST_RUN_RC"
    ;;
  *) exit 125 ;;
esac
''')
    path.chmod(0o755)


def _fake_flock(path: Path, real_flock: str) -> None:
    path.write_text(
        "#!/usr/bin/env bash\n"
        "[[ \"${G2_TEST_MODE:-}\" == lock_failure ]] && exit 1\n"
        f"exec '{real_flock}' \"$@\"\n"
    )
    path.chmod(0o755)


@pytest.fixture
def runner_harness(tmp_path):
    bash, jq, real_flock = _runner_tools()
    env_file = tmp_path / "preflight.env"
    env_file.write_text(
        "ENV=staging\nDB_NAME=trilhacode_staging\n"
        "MONGO_URL=mongodb://reader:dummy@mongo:27017/trilhacode_staging\n"
        "G2_MONGO_EXPECTED_HOST=mongo\nG2_MONGO_EXPECTED_PORT=27017\n"
        "G2_MONGO_EXPECTED_CONTAINER_ID=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n"
    )
    env_file.chmod(0o600)
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(MANIFEST_PATH.read_bytes())
    manifest.chmod(0o600)
    docker = tmp_path / "docker"
    _fake_docker(docker)
    flock = tmp_path / "flock"
    _fake_flock(flock, real_flock)
    lock_dir = tmp_path / "lockdir"
    lock_dir.mkdir(mode=0o700)
    timeout = tmp_path / "timeout"
    timeout.write_text("#!/usr/bin/env bash\nshift 3\nexec \"$@\"\n")
    timeout.chmod(0o755)
    runner = tmp_path / "runner.sh"
    source = RUNNER.read_text()
    source = source.replace("readonly MONGO_CONTAINER='3jo4k9aes1iqn4qlqqeyyh4y'", "readonly MONGO_CONTAINER='test-mongo'")
    source = source.replace("readonly ENV_FILE='/etc/trilhacode-g2/preflight.env'", f"readonly ENV_FILE='{env_file}'")
    source = source.replace("readonly MANIFEST='/etc/trilhacode-g2/preflight-manifest-v1.json'", f"readonly MANIFEST='{manifest}'")
    source = source.replace("readonly DOCKER='/usr/bin/docker'", f"readonly DOCKER='{docker}'")
    source = source.replace("readonly TIMEOUT='/usr/bin/timeout'", f"readonly TIMEOUT='{timeout}'")
    source = source.replace("readonly JQ='/usr/bin/jq'", f"readonly JQ='{jq}'")
    source = source.replace("readonly FLOCK='/usr/bin/flock'", f"readonly FLOCK='{flock}'")
    source = source.replace("readonly LOCK_DIR='/run/trilhacode-g2-preflight'", f"readonly LOCK_DIR='{lock_dir}'")
    source = source.replace("readonly LOCK_FILE='/run/trilhacode-g2-preflight/runner.lock'", f"readonly LOCK_FILE='{lock_dir / 'runner.lock'}'")
    source = source.replace(
        '[[ -d /run && ! -L /run && "$(stat -c \'%u:%a\' /run)" == \'0:755\' ]] || emit_failure LOCK_UNAVAILABLE 69',
        '[[ -d /run ]] || emit_failure LOCK_UNAVAILABLE 69',
    )
    source = source.replace("== '0:700'", f"== '{os.getuid()}:700'")
    source = source.replace("== '0:600'", f"== '{os.getuid()}:600'")
    source = source.replace('[[ "$(id -u)" == 0 ]]', '[[ 0 == 0 ]]')
    runner.write_text(source)
    runner.chmod(0o700)

    state_path = tmp_path / "container-state"

    def invoke(mode="success", output=None, run_rc=0):
        env = os.environ.copy()
        env.update({
            "G2_TEST_MODE": mode,
            "G2_TEST_STATE": str(state_path),
            "G2_TEST_OUTPUT": output if output is not None else json.dumps({
                "schema_version": 1,
                "result": "COMPLETE",
                "checks": [{"id": check_id, "status": "AUSENTE" if check_id.startswith("index/") else "OK"}
                           for check_id in json.loads(manifest.read_text())["checks"]],
            }),
            "G2_TEST_RUN_RC": str(run_rc),
        })
        return subprocess.run([bash, str(runner)], capture_output=True, text=True, env=env)

    def start(mode):
        env = os.environ.copy()
        manifest_data = json.loads(manifest.read_text())
        env.update({
            "G2_TEST_MODE": mode,
            "G2_TEST_STATE": str(state_path),
            "G2_TEST_OUTPUT": json.dumps({
                "schema_version": 1,
                "result": "COMPLETE",
                "checks": [{"id": check_id, "status": "AUSENTE" if check_id.startswith("index/") else "OK"}
                           for check_id in manifest_data["checks"]],
            }),
            "G2_TEST_RUN_RC": "0",
        })
        return subprocess.Popen([bash, str(runner)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=env, start_new_session=True)

    invoke.state_path = state_path
    invoke.start = start
    return invoke


def test_complete_manifest_report_passes_and_cleans_container(runner_harness):
    result = runner_harness()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AUSENTE=" in result.stdout
    assert "COMPLETE" in result.stdout
    assert "private-canary" not in result.stdout + result.stderr
    assert not runner_harness.state_path.exists()


@pytest.mark.parametrize("output,run_rc", [
    ("", 0),
    ('{"schema_version":1,"result":"COMPLETE","checks":[]}', 0),
    ('{"schema_version":1,"result":"COMPLETE","checks":[]}\n{}', 0),
    ('{"schema_version":1,"result":"COMPLETE","checks":[', 0),
])
def test_empty_partial_or_malformed_output_never_passes(runner_harness, output, run_rc):
    result = runner_harness(output=output, run_rc=run_rc)
    assert result.returncode != 0
    assert "PASSED" not in result.stdout


@pytest.mark.parametrize("mode,category", [
    ("lock_failure", "ALREADY_RUNNING"),
    ("network_failure", "NETWORK_ISOLATION"),
    ("image_failure", "IMAGE_UNAVAILABLE"),
    ("cleanup_failure", "CLEANUP_FAILED"),
])
def test_runner_fails_closed_for_host_and_cleanup_errors(runner_harness, mode, category):
    result = runner_harness(mode=mode)
    assert result.returncode != 0
    assert category in result.stdout


def test_timeout_is_distinct_and_cleanup_occurs(runner_harness):
    result = runner_harness(mode="success", run_rc=124)
    assert result.returncode == 124
    assert "TIMEOUT" in result.stdout
    assert not runner_harness.state_path.exists()


def test_termination_signal_cleans_its_container_before_exit(runner_harness):
    import signal
    import time

    process = runner_harness.start("signal_wait")
    for _ in range(100):
        if runner_harness.state_path.exists():
            break
        time.sleep(0.05)
    assert runner_harness.state_path.exists()
    os.killpg(process.pid, signal.SIGTERM)
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 143
    assert "INTERRUPTED" in stdout
    assert "CLEANUP_FAILED" not in stdout
    assert not runner_harness.state_path.exists()


def test_concurrent_invocation_is_rejected_while_lock_is_held(runner_harness):
    import signal
    import time

    first = runner_harness.start("signal_wait")
    for _ in range(100):
        if runner_harness.state_path.exists():
            break
        time.sleep(0.05)
    assert runner_harness.state_path.exists()
    second = runner_harness()
    assert second.returncode == 75
    assert "ALREADY_RUNNING" in second.stdout
    os.killpg(first.pid, signal.SIGTERM)
    first.communicate(timeout=10)
    assert not runner_harness.state_path.exists()


def test_signal_before_cidfile_still_cleans_only_labelled_invocation(runner_harness):
    import signal
    import time

    process = runner_harness.start("signal_before_cidfile")
    for _ in range(100):
        if runner_harness.state_path.exists():
            break
        time.sleep(0.05)
    assert runner_harness.state_path.exists()
    os.killpg(process.pid, signal.SIGHUP)
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 129
    assert "INTERRUPTED" in stdout
    assert "CLEANUP_FAILED" not in stdout
    assert not runner_harness.state_path.exists()


@pytest.mark.parametrize("run_rc,expected", [(137, "PROCESS_KILLED"), (124, "TIMEOUT")])
def test_kill_and_timeout_are_distinct(runner_harness, run_rc, expected):
    result = runner_harness(run_rc=run_rc)
    assert result.returncode == run_rc
    assert expected in result.stdout


@pytest.mark.parametrize("category,code", [("DB_AUTH", 41), ("DB_CONNECTION", 42), ("URI_INVALID", 40)])
def test_backend_failure_categories_are_preserved(runner_harness, category, code):
    output = json.dumps({"schema_version": 1, "result": "ERROR", "category": category})
    result = runner_harness(output=output, run_rc=code)
    assert result.returncode == code
    assert category in result.stdout


@pytest.mark.parametrize("status", ["CONFLITO", "DUPLICATAS"])
def test_semantically_rejected_report_fails_after_full_validation(runner_harness, status):
    manifest = json.loads(MANIFEST_PATH.read_text())
    checks = [{"id": check_id, "status": "AUSENTE" if check_id.startswith("index/") else "OK"}
              for check_id in manifest["checks"]]
    checks[0]["status"] = status
    output = json.dumps({"schema_version": 1, "result": "COMPLETE", "checks": checks})
    result = runner_harness(output=output, run_rc=43)
    assert result.returncode == 43
    assert "PREFLIGHT_REJECTED" in result.stdout


def test_raw_backend_canary_is_never_published(runner_harness):
    result = runner_harness(mode="canary", run_rc=1)
    assert result.returncode != 0
    assert "private-canary-value" not in result.stdout + result.stderr
