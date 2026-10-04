#!/usr/bin/env bash
# Build the Lambda bundle and ship it.
#
#   deploy/aws/deploy.sh            build + upload code
#   deploy/aws/deploy.sh --build    build only (deploy/aws/build/bundle.zip)
#
# A zip rather than a container image: no Docker needed to build it. Dependencies
# are fetched as Linux arm64 wheels, so this works from a Mac. The one-off
# infrastructure (role, function, URL, CloudFront, DNS) is described in README.md.
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
FUNCTION="${FUNCTION:-napkin-chain}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/deploy/aws/build"
PKG="$BUILD/pkg"

rm -rf "$BUILD"
mkdir -p "$PKG"

echo "==> frontend"
(cd "$ROOT/frontend" && npm ci --silent && npm run build --silent)
mkdir -p "$PKG/frontend"
cp -R "$ROOT/frontend/dist" "$PKG/frontend/dist"

echo "==> backend dependencies (linux arm64, cp313)"
# Everything above the "# dev / test" marker is a runtime dependency.
sed '/^# dev \/ test/,$d' "$ROOT/backend/requirements.txt" > "$BUILD/requirements.txt"
python3 -m pip install --quiet --disable-pip-version-check \
  --requirement "$BUILD/requirements.txt" \
  --target "$PKG" \
  --platform manylinux2014_aarch64 --implementation cp --python-version 3.13 \
  --only-binary=:all:

echo "==> backend app"
rsync -a --exclude '__pycache__' "$ROOT/backend/app" "$PKG/"
cp "$ROOT/deploy/aws/run.sh" "$PKG/run.sh"
chmod 755 "$PKG/run.sh"

find "$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} +
(cd "$PKG" && zip -qr9 "$BUILD/bundle.zip" .)
echo "    $(du -h "$BUILD/bundle.zip" | cut -f1) bundle.zip"

[[ "${1:-}" == "--build" ]] && exit 0

echo "==> upload to $FUNCTION ($REGION)"
aws lambda update-function-code --region "$REGION" --function-name "$FUNCTION" \
  --zip-file "fileb://$BUILD/bundle.zip" --architectures arm64 \
  --query 'LastModified' --output text
aws lambda wait function-updated-v2 --region "$REGION" --function-name "$FUNCTION"
echo "==> done"
