#!/usr/bin/env bash
# ActionLayer CLI helper.
#
# Exists because the MCP tool `actionlayer_get_action_ticket` (and
# GET /v1/actions/tickets/{id}) do NOT surface info_request — you see
# "blocked" with null everywhere and never learn what it's asking.
# GET /tasks/{id} does. This script always uses /tasks/{id}.
#
#   ./al.sh fire <url> "<short instruction>"     -> ticket_id
#   ./al.sh task "<goal>" [target_url]           -> ticket_id
#   ./al.sh watch <ticket_id>                    -> poll until terminal or blocked
#   ./al.sh get <ticket_id>                      -> one-shot state dump
#   ./al.sh reply <ticket_id> <key> "<value>"    -> answer an info_request question
#
# Keep instructions SHORT — they truncate around 500 chars.
set -uo pipefail
cd "$(dirname "$0")"
set -a; source .env; set +a
: "${ACTIONLAYER_API_KEY:?missing in .env}"
API="${ACTIONLAYER_API_URL:-https://api.actionlayer.io}"
H="Authorization: Bearer $ACTIONLAYER_API_KEY"

# lenient JSON: goal strings contain raw newlines, strict parsing dies
PY='import json,sys; d=json.loads(sys.stdin.read(), strict=False)'

show() {
  python3 -c "$PY
print('state      :', d.get('state'))
print('reason     :', d.get('reason'))
r = d.get('result')
if r: print('result     :', json.dumps(r, indent=2)[:3000])
e = d.get('error')
if e: print('error      :', e)
ir = d.get('info_request')
if ir and ir.get('questions'):
    print()
    print('>>> BLOCKED — it is asking you:')
    for q in ir['questions']:
        print('    [%s] %s' % (q['key'], q['label']))
    if ir.get('amount_usd'):
        print('    PAYMENT: \$%s  status=%s' % (ir['amount_usd'], ir.get('payment_status')))
    print()
    print('    reply with:  ./al.sh reply %s <key> \"your answer\"' % d.get('id'))
"
}

case "${1:-}" in
  fire)
    url="${2:?usage: al.sh fire <url> \"<instruction>\"}"; inst="${3:?need instruction}"
    n=${#inst}; [ "$n" -gt 480 ] && echo "!! instruction is $n chars — truncates ~500. Shorten it." >&2
    curl -s -m 60 -H "$H" -H 'Content-Type: application/json' \
      -d "$(python3 -c 'import json,sys; print(json.dumps({"inputs":{"url":sys.argv[1],"instruction":sys.argv[2]}}))' "$url" "$inst")" \
      "$API/v1/actions/direct.browser_action" \
    | python3 -c "$PY
print('ticket:', (d.get('payload') or {}).get('ticket_id'))
print('outcome:', d.get('outcome'))"
    ;;
  task)
    goal="${2:?usage: al.sh task \"<goal>\" [target_url]}"; turl="${3:-}"
    body=$(python3 -c 'import json,sys
b={"goal":sys.argv[1]}
if len(sys.argv)>2 and sys.argv[2]: b["target_url"]=sys.argv[2]
print(json.dumps(b))' "$goal" "$turl")
    curl -s -m 60 -H "$H" -H 'Content-Type: application/json' \
      -H "Idempotency-Key: al-$(python3 -c 'import uuid;print(uuid.uuid4())')" \
      -d "$body" "$API/tasks" | python3 -c "$PY
print('ticket:', d.get('id')); print('state:', d.get('state'))"
    ;;
  get)
    curl -s -m 30 -H "$H" "$API/tasks/${2:?need ticket_id}" | show
    ;;
  watch)
    t="${2:?need ticket_id}"; start=$(date +%s)
    while :; do
      body=$(curl -s -m 30 -H "$H" "$API/tasks/$t")
      st=$(printf '%s' "$body" | python3 -c "$PY
print(d.get('state'))" 2>/dev/null)
      el=$(( $(date +%s) - start ))
      printf '\r  %s  %ds elapsed   ' "$st" "$el"
      if [ "$st" != "pending" ] && [ -n "$st" ]; then
        echo; echo "────────────────────────────────"; printf '%s' "$body" | show; exit 0
      fi
      /bin/sleep 15
    done
    ;;
  reply)
    t="${2:?need ticket_id}"; k="${3:?need question key}"; v="${4:?need value}"
    curl -s -m 30 -H "$H" -H 'Content-Type: application/json' \
      -d "$(python3 -c 'import json,sys; print(json.dumps({"sensitive":False,"info":{sys.argv[1]:sys.argv[2]}}))' "$k" "$v")" \
      "$API/tasks/$t/reply" | python3 -c "$PY
print('state:', d.get('state'))"
    echo "now: ./al.sh watch $t"
    ;;
  *)
    sed -n '3,17p' "$0" | sed 's/^# \{0,1\}//'
    ;;
esac
