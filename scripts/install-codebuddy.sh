#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${HOME}/.codebuddy/skills"

mkdir -p "${DEST}"

for skill in ctx-recall ctx-compact ctx-jobs; do
  mkdir -p "${DEST}/${skill}"
  ln -sfn "${ROOT}/skills/${skill}/SKILL.md" "${DEST}/${skill}/SKILL.md"
done

echo "Installed ctx skills into ${DEST}."
echo "Restart CodeBuddy before using /ctx-recall, /ctx-compact, or /ctx-jobs."
