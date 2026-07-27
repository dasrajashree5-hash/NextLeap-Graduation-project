#!/bin/sh
# Populate a fresh deployment with demo data: reviews -> analysis -> insights -> research.
#
#   ./scripts/seed_demo.sh                       # http://127.0.0.1:8000
#   ./scripts/seed_demo.sh https://api.host      # deployed backend
#
# Steps 3-5 call Groq, so GROQ_API_KEY must be set on the target service.
# Tunable: REVIEW_LIMIT, ANALYZE_LIMIT, SKIP_TRANSLATION, REVIEWS_CSV.

set -e

BASE_URL="${1:-${BASE_URL:-http://127.0.0.1:8000}}"
BASE_URL="${BASE_URL%/}"

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REVIEWS_CSV="${REVIEWS_CSV:-$SCRIPT_DIR/../data/sample_blinkit_reviews.csv}"

REVIEW_LIMIT="${REVIEW_LIMIT:-500}"
ANALYZE_LIMIT="${ANALYZE_LIMIT:-200}"
SKIP_TRANSLATION="${SKIP_TRANSLATION:-true}"

BODY_FILE=$(mktemp)
trap 'rm -f "$BODY_FILE"' EXIT

if [ ! -f "$REVIEWS_CSV" ]; then
  echo "Sample reviews not found: $REVIEWS_CSV" >&2
  exit 1
fi

step() {
  echo ""
  echo "==> $1"
}

# Prints the response body; on a non-2xx the status is surfaced instead of a bare curl code.
call() {
  label=$1
  shift
  status=$(curl -sS -o "$BODY_FILE" -w '%{http_code}' "$@")
  cat "$BODY_FILE"
  echo ""
  case "$status" in
    2*) ;;
    *)
      echo "$label failed with HTTP $status — check the service logs for the traceback." >&2
      exit 1
      ;;
  esac
}

post_json() {
  call "$1" -X POST "$BASE_URL$2" -H "Content-Type: application/json" -d "$3"
}

step "Checking $BASE_URL"
call "health check" "$BASE_URL/api/health"

# Steps 3-5 return an opaque 500 without a key, so fail early with a readable reason.
if grep -q '"groq":{"status":"not_configured"' "$BODY_FILE"; then
  echo "" >&2
  echo "GROQ_API_KEY is not set on this service — steps 3-5 would fail." >&2
  echo "Set it (Railway: service -> Variables) and re-run." >&2
  exit 1
fi

step "1/6 Uploading sample reviews"
call "review upload" -X POST "$BASE_URL/api/reviews/upload" \
  -F format=csv \
  -F source_name="Blinkit sample" \
  -F "file=@$REVIEWS_CSV"

step "2/6 Preprocessing and embedding"
post_json "preprocess" "/api/pipeline/preprocess" \
  "{\"limit\": $REVIEW_LIMIT, \"skip_translation\": $SKIP_TRANSLATION}"

step "3/6 Analyzing reviews (Groq)"
post_json "analyze" "/api/pipeline/analyze" \
  "{\"limit\": $ANALYZE_LIMIT, \"force\": false}"

# Needs hdbscan + umap-learn from requirements.txt; a bare venv install will 500 here.
step "4/6 Clustering into themes"
post_json "cluster" "/api/pipeline/cluster" '{"force": false}'

step "5/6 Generating insights"
post_json "insights" "/api/pipeline/insights" '{"replace": true}'

step "6/6 Seeding research repository"
call "research seed" -X POST "$BASE_URL/api/research/seed?code=true"
call "triangulate" -X POST "$BASE_URL/api/research/triangulate"
call "opportunities" -X POST "$BASE_URL/api/research/opportunities"

step "Done — current status"
call "analysis status" "$BASE_URL/api/pipeline/analysis-status"
