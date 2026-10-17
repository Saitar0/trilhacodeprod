#!/bin/bash
# Explicitly run as root ONCE after review: ./install-g2-host.sh /root/g2-actions.pub
# Deliberately does NOT create a MongoDB user, pull images, or run preflight.
set -Eeuo pipefail
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
[[ "$(id -u)" == 0 && $# == 1 && "$1" == /* ]] || { echo 'Usage as root: install-g2-host.sh /absolute/path/to/dedicated-public-key' >&2; exit 64; }
readonly PUB="$1"
readonly TARGET_USER='trilhacode-g2'
readonly KEYFILE='/home/trilhacode-g2/.ssh/authorized_keys'
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly GUARD='/usr/local/sbin/trilhacode-g2-preflight-guard'
readonly RUNNER='/usr/local/sbin/trilhacode-g2-preflight-run'
readonly SUDOERS='/etc/sudoers.d/trilhacode-g2'

[[ -f "$PUB" && ! -L "$PUB" ]] || { echo 'Public key missing' >&2; exit 78; }
[[ -f "$SCRIPT_DIR/trilhacode-g2-preflight-guard" && -f "$SCRIPT_DIR/trilhacode-g2-preflight-run" ]] || { echo 'Executor source missing' >&2; exit 78; }
/usr/bin/id "$TARGET_USER" >/dev/null || { echo 'Dedicated user missing' >&2; exit 78; }
groups="$(id -nG "$TARGET_USER")"
[[ " $groups " == " $TARGET_USER " ]] || { echo 'Unexpected extra groups on G2 account' >&2; exit 78; }
[[ -f "$KEYFILE" && ! -s "$KEYFILE" && ! -L "$KEYFILE" ]] || { echo 'authorized_keys must exist and be empty' >&2; exit 78; }
for f in "$GUARD" "$RUNNER" "$SUDOERS"; do
  [[ ! -e "$f" && ! -L "$f" ]] || { echo "Refusing to overwrite $f" >&2; exit 78; }
done
[[ "$(/usr/bin/wc -l < "$PUB")" == 1 ]] || { echo 'Public key must contain one line' >&2; exit 78; }
read -r key_type key_blob key_comment < "$PUB"
[[ "$key_type" == 'ssh-ed25519' && "$key_blob" =~ ^[A-Za-z0-9+/]+={0,2}$ ]] || { echo 'Expected a plain Ed25519 public key' >&2; exit 78; }
/usr/bin/ssh-keygen -l -f "$PUB" >/dev/null || { echo 'Invalid public key' >&2; exit 78; }
/usr/sbin/visudo -c >/dev/null || { echo 'Current sudoers invalid' >&2; exit 78; }
/usr/sbin/sshd -t || { echo 'Current SSH configuration invalid' >&2; exit 78; }
[[ -d '/home/trilhacode-g2/.ssh' ]] || { echo 'SSH home missing' >&2; exit 78; }
[[ "$(stat -c '%U:%a' '/home/trilhacode-g2/.ssh')" == 'trilhacode-g2:700' ]] || { echo 'SSH dir permissions unexpected' >&2; exit 78; }

# Stage sudoers and validate before modifying any active policy.
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
printf 'trilhacode-g2 ALL=(root) NOPASSWD: %s\n' "$RUNNER" > "$tmp"
/usr/sbin/visudo -cf "$tmp" >/dev/null || { echo 'Generated sudo policy failed validation' >&2; exit 78; }

install -o root -g root -m 0755 "$SCRIPT_DIR/trilhacode-g2-preflight-guard" "$GUARD"
install -o root -g root -m 0700 "$SCRIPT_DIR/trilhacode-g2-preflight-run" "$RUNNER"
# Install the forced-command key before granting its narrowly scoped sudo right.
# If the final policy install fails, the key has no privileged operation.
# Only allow the exact remote request, no scp/sftp/TTY/forwarding.
printf 'restrict,command="%s" %s %s\n' "$GUARD" "$key_type" "$key_blob" > "$KEYFILE"
chown trilhacode-g2:trilhacode-g2 "$KEYFILE"
chmod 0600 "$KEYFILE"
install -o root -g root -m 0440 "$tmp" "$SUDOERS"
/usr/sbin/visudo -c >/dev/null
echo 'G2 host guard installed. Preflight not executed. Image/readonly Mongo/env/GitHub secrets still require separate provisioning.'
