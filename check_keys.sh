#!/usr/bin/env bash
# Verify hackathon API keys work. Run: ./check_keys.sh
set -uo pipefail
cd "$(dirname "$0")"
set -a; source .env; set +a

echo "=== Novita ==="
if [ -z "${NOVITA_API_KEY:-}" ]; then
  echo "SKIP: NOVITA_API_KEY not set in .env"
else
  code=$(curl -s -o /tmp/novita.out -w "%{http_code}" -m 20 \
    -H "Authorization: Bearer $NOVITA_API_KEY" \
    https://api.novita.ai/openai/v1/models)
  echo "GET /openai/v1/models -> $code"
  if [ "$code" = "200" ]; then
    echo "first models:"; grep -o '"id":"[^"]*"' /tmp/novita.out | head -5
  else
    head -c 300 /tmp/novita.out; echo
  fi
fi

echo
echo "=== ActionLayer ==="
if [ -z "${ACTIONLAYER_API_KEY:-}" ]; then
  echo "SKIP: ACTIONLAYER_API_KEY not set in .env"
elif [ -z "${ACTIONLAYER_BASE_URL:-}" ]; then
  echo "SKIP: ACTIONLAYER_BASE_URL not set — fill it in from their docs, then re-run."
else
  for hdr in "Authorization: Bearer $ACTIONLAYER_API_KEY" "x-api-key: $ACTIONLAYER_API_KEY"; do
    code=$(curl -s -o /tmp/al.out -w "%{http_code}" -m 20 \
      -H "$hdr" "$ACTIONLAYER_BASE_URL/tasks")
    ct=$(head -c 20 /tmp/al.out)
    echo "GET \$BASE/tasks with '${hdr%%:*}' -> $code"
    [ "$code" = "200" ] && { echo "body:"; head -c 300 /tmp/al.out; echo; break; }
  done
fi
