#!/bin/bash
#
# Run ELO tournaments on all MLE-bench splits
#
# Usage:
#   ./run_all_splits.sh [--repo-url URL] [--output-dir DIR]
#

set -e

# Default values
REPO_URL="https://github.com/openai/mle-bench.git"
REPO_DIR="mle-bench"
OUTPUT_DIR="results"
EXCLUDE_AGENTS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo-url)
            REPO_URL="$2"
            shift 2
            ;;
        --repo-dir)
            REPO_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --exclude-agents)
            EXCLUDE_AGENTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--repo-url URL] [--repo-dir DIR] [--output-dir DIR] [--exclude-agents 'agent1 agent2']"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Running ELO Tournaments on All Splits"
echo "=========================================="
echo "Repository URL: $REPO_URL"
echo "Repository Dir: $REPO_DIR"
echo "Output Dir: $OUTPUT_DIR"
echo "Exclude Agents: ${EXCLUDE_AGENTS:-None}"
echo "=========================================="
echo ""

# Define splits to run
SPLITS=("low" "medium" "high" "systemcard" "split75")

# Run tournament for each split
for SPLIT in "${SPLITS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Running tournament for split: $SPLIT"
    echo "=========================================="

    if [ -n "$EXCLUDE_AGENTS" ]; then
        python elo_tournament.py \
            --repo-url "$REPO_URL" \
            --repo-dir "$REPO_DIR" \
            --split "$SPLIT" \
            --output-dir "$OUTPUT_DIR" \
            --exclude-agents $EXCLUDE_AGENTS
    else
        python elo_tournament.py \
            --repo-url "$REPO_URL" \
            --repo-dir "$REPO_DIR" \
            --split "$SPLIT" \
            --output-dir "$OUTPUT_DIR"
    fi

    echo ""
    echo "✓ Completed tournament for split: $SPLIT"
    echo ""
done

echo ""
echo "=========================================="
echo "All tournaments completed!"
echo "=========================================="
echo "Results saved in: $OUTPUT_DIR/"
echo ""
echo "Output files:"
for SPLIT in "${SPLITS[@]}"; do
    echo "  - elo_grand_${SPLIT}.csv"
    echo "  - elo_per_task_${SPLIT}.csv"
    echo "  - agent_task_results_${SPLIT}.csv"
done
echo ""

# Generate summary comparison
echo "Generating summary comparison..."
python << 'EOF'
import csv
from pathlib import Path
import sys

output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results")
splits = ["low", "medium", "high", "systemcard", "split75"]

print("\n" + "=" * 80)
print("SUMMARY: Top 5 Agents Across All Splits")
print("=" * 80)
print()

# Load grand tournament results for each split
split_results = {}
for split in splits:
    grand_csv = output_dir / f"elo_grand_{split}.csv"
    if not grand_csv.exists():
        continue

    with open(grand_csv, 'r') as f:
        reader = csv.DictReader(f)
        rankings = [(row['agent_name'], float(row['elo_rating'])) for row in reader]
    split_results[split] = rankings

# Print top 5 for each split
for split in splits:
    if split not in split_results:
        continue

    print(f"{split.upper():15s}", end="")

print()
print("-" * 80)

# Print top 5 agents side by side
for rank in range(5):
    for split in splits:
        if split not in split_results:
            print(f"{'':15s}", end="")
            continue

        if rank < len(split_results[split]):
            agent, elo = split_results[split][rank]
            # Truncate agent name if too long
            agent_short = agent[:12] + "..." if len(agent) > 15 else agent
            print(f"{rank+1}. {agent_short:11s}", end=" ")
        else:
            print(f"{'':15s}", end="")
    print()

print()
print("=" * 80)
EOF

echo ""
echo "Done! Check $OUTPUT_DIR/ for all results."
