#!/usr/bin/env bash
# ReplicaLab training entrypoint for Northflank GPU jobs.
#
# Usage:
#   MODE=train ./scripts/train.sh          # full training (scientist + lab manager)
#   MODE=scientist ./scripts/train.sh      # scientist GRPO only
#   MODE=lab-manager ./scripts/train.sh    # lab manager SFT only
#   MODE=eval ./scripts/train.sh           # baseline evaluation only
#   MODE=server ./scripts/train.sh         # just run server (default)
#
# The script starts the ReplicaLab server in the background (needed for
# rollout evaluation), then runs the requested training flow.

set -euo pipefail

MODE="${MODE:-server}"
SEED_COUNT="${SEED_COUNT:-8}"
MAX_STEPS="${MAX_STEPS:-300}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen3-8B}"
PERSIST_ROOT="${REPLICALAB_PERSIST_ROOT:-/app/outputs/training}"
BASE_URL="http://localhost:7860"

echo "=========================================="
echo " ReplicaLab Training Pipeline"
echo "=========================================="
echo " Mode:        $MODE"
echo " Model:       $MODEL_NAME"
echo " Seeds:       $SEED_COUNT"
echo " Max steps:   $MAX_STEPS"
echo " Persist:     $PERSIST_ROOT"
echo " Server URL:  $BASE_URL"
echo "=========================================="

# ── Start server in background (needed for eval rollouts) ──────────────
start_server() {
    echo "[train.sh] Starting ReplicaLab server on port 7860..."
    uvicorn server.app:app --host 0.0.0.0 --port 7860 &
    SERVER_PID=$!
    echo "[train.sh] Server PID: $SERVER_PID"

    # Wait for server to be ready
    for i in $(seq 1 30); do
        if curl -sf http://localhost:7860/health > /dev/null 2>&1; then
            echo "[train.sh] Server is ready."
            return 0
        fi
        sleep 1
    done
    echo "[train.sh] WARNING: Server did not become ready in 30s, continuing anyway."
}

# ── Scientist GRPO training ───────────────────────────────────────────
run_scientist_train() {
    echo ""
    echo "=== Phase 1: Scientist GRPO Training ==="
    echo ""

    # Preview first (no GPU needed)
    python -m replicalab.training.cli scientist-preview \
        --persist-root "$PERSIST_ROOT" \
        --model-name "$MODEL_NAME" \
        --seed-count "$SEED_COUNT"

    # Full training
    python -m replicalab.training.cli scientist-train \
        --persist-root "$PERSIST_ROOT" \
        --model-name "$MODEL_NAME" \
        --seed-count "$SEED_COUNT" \
        --max-steps "$MAX_STEPS"

    echo "[train.sh] Scientist GRPO training complete."
}

# ── Lab Manager SFT training ─────────────────────────────────────────
run_lab_manager_train() {
    echo ""
    echo "=== Phase 2: Lab Manager SFT Training ==="
    echo ""

    # Preview first
    python -m replicalab.training.cli lab-manager-preview \
        --persist-root "$PERSIST_ROOT" \
        --model-name "$MODEL_NAME" \
        --seed-count "$SEED_COUNT"

    # Full training
    python -m replicalab.training.cli lab-manager-train \
        --persist-root "$PERSIST_ROOT" \
        --model-name "$MODEL_NAME" \
        --seed-count "$SEED_COUNT"

    echo "[train.sh] Lab Manager SFT training complete."
}

# ── Baseline evaluation ──────────────────────────────────────────────
run_eval() {
    echo ""
    echo "=== Baseline Evaluation ==="
    echo ""

    python -m replicalab.training.cli baseline-eval \
        --persist-root "$PERSIST_ROOT" \
        --base-url "$BASE_URL" \
        --seed-count "$SEED_COUNT"

    echo "[train.sh] Evaluation complete."
}

# ── Mode dispatch ────────────────────────────────────────────────────

case "$MODE" in
    server)
        echo "[train.sh] Server-only mode."
        exec uvicorn server.app:app --host 0.0.0.0 --port 7860
        ;;

    train)
        start_server
        run_scientist_train
        run_lab_manager_train
        run_eval
        echo ""
        echo "=========================================="
        echo " All training complete!"
        echo " Artifacts saved to: $PERSIST_ROOT"
        echo "=========================================="
        # Keep container alive so artifacts can be retrieved
        echo "[train.sh] Training done. Keeping container alive..."
        wait $SERVER_PID
        ;;

    scientist)
        run_scientist_train
        ;;

    lab-manager)
        run_lab_manager_train
        ;;

    eval)
        start_server
        run_eval
        wait $SERVER_PID
        ;;

    *)
        echo "Unknown MODE: $MODE"
        echo "Valid modes: server, train, scientist, lab-manager, eval"
        exit 1
        ;;
esac
