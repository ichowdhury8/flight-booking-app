#!/usr/bin/env bash
#
# Build the frontend, commit the output, and push — as one atomic step.
#
# static/ is committed to git so Render's build command can stay Python-only
# and never depend on Node being present in its image (PLAN.md R3). The risk
# that creates is a stale static/ being deployed against newer source, so
# build-add-commit-push lives here rather than in anyone's muscle memory (R9).
#
#   ./deploy.sh "Optional commit message"

set -euo pipefail

cd "$(dirname "$0")"

MESSAGE="${1:-Rebuild frontend and deploy}"

echo "==> Building frontend"
(cd frontend && npm run build)

if [[ ! -f static/index.html ]]; then
  echo "!! static/index.html missing after build — aborting." >&2
  exit 1
fi

echo "==> Staging"
git add -A

if git diff --cached --quiet; then
  echo "==> Nothing to commit; working tree already matches HEAD."
else
  git commit -m "$MESSAGE"
fi

echo "==> Pushing to origin/$(git branch --show-current)"
git push origin "$(git branch --show-current)"

echo
echo "==> Pushed. Render will redeploy from the blueprint."
echo "    Watch: https://dashboard.render.com"
echo "    Live:  https://flight-booking-app-zr2v.onrender.com"
