#!/bin/bash
#
# Quick wrapper for running ELO tournament on a single split
#
# Usage:
#   ./run_elo.sh low                    # Run on low split
#   ./run_elo.sh medium results/        # Run on medium split with custom output dir
#   ./run_elo.sh high results/ agent1   # Exclude agent1
#

SPLIT=${1:-"low"}
OUTPUT_DIR=${2:-"results"}
EXCLUDE_AGENTS=${3:-""}

echo "Running ELO tournament on split: $SPLIT"
echo "Output directory: $OUTPUT_DIR"
echo ""

if [ -n "$EXCLUDE_AGENTS" ]; then
    python elo_tournament.py --split "$SPLIT" --output-dir "$OUTPUT_DIR" --exclude-agents "$EXCLUDE_AGENTS"
else
    python elo_tournament.py --split "$SPLIT" --output-dir "$OUTPUT_DIR"
fi

echo ""
echo "✓ Done! Results saved in $OUTPUT_DIR/"
echo ""
echo "Output files:"
echo "  - elo_grand_${SPLIT}.csv         (Grand tournament rankings)"
echo "  - elo_per_task_${SPLIT}.csv      (Per-task ELO ratings)"
echo "  - agent_task_results_${SPLIT}.csv (Raw scores)"
echo ""
echo "View grand tournament:"
echo "  cat $OUTPUT_DIR/elo_grand_${SPLIT}.csv | column -t -s,"
