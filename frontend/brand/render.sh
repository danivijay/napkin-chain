#!/usr/bin/env bash
# Re-render the share image and PNG app icons into public/ with headless Chrome.
set -euo pipefail

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PUBLIC="$HERE/../public"

shot() { # <html> <out.png> <width> <height>
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=5000 --window-size="$3,$4" --screenshot="$2" "file://$HERE/$1" 2>/dev/null
}

shot og-image.html "$PUBLIC/og-image.png" 1200 630
# Headless Chrome will not shrink a window below ~500px, so render the icon
# once at 512 and scale it down.
shot icon.html "$PUBLIC/icon-512.png" 512 512
sips -z 192 192 "$PUBLIC/icon-512.png" --out "$PUBLIC/icon-192.png" >/dev/null
sips -z 180 180 "$PUBLIC/icon-512.png" --out "$PUBLIC/apple-touch-icon.png" >/dev/null
ls -la "$PUBLIC"/*.png
