#!/bin/bash
#
# Update the MLE-bench ELO Leaderboard
#
# Usage:
#   ./update_leaderboard.sh [results_dir] [output_file]
#
# Examples:
#   ./update_leaderboard.sh                      # Use defaults
#   ./update_leaderboard.sh results/             # Custom results dir
#   ./update_leaderboard.sh results/ LEADERBOARD.md  # Full custom
#

RESULTS_DIR=${1:-"results"}
OUTPUT_FILE=${2:-"LEADERBOARD.md"}

echo "=========================================="
echo "Updating MLE-bench ELO Leaderboard"
echo "=========================================="
echo "Results directory: $RESULTS_DIR"
echo "Output file: $OUTPUT_FILE"
echo ""

# Check if results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "Error: Results directory not found: $RESULTS_DIR"
    echo ""
    echo "Please run tournaments first:"
    echo "  ./run_all_splits.sh --output-dir $RESULTS_DIR"
    echo ""
    exit 1
fi

# Count available splits
SPLITS=0
for split in low medium high systemcard split75; do
    if [ -f "$RESULTS_DIR/elo_grand_${split}.csv" ]; then
        SPLITS=$((SPLITS + 1))
    fi
done

echo "Found $SPLITS/5 completed splits"
echo ""

if [ $SPLITS -eq 0 ]; then
    echo "Error: No tournament results found in $RESULTS_DIR"
    echo ""
    echo "Please run tournaments first:"
    echo "  ./run_all_splits.sh --output-dir $RESULTS_DIR"
    echo ""
    exit 1
fi

# Generate leaderboard
python generate_leaderboard.py --results-dir "$RESULTS_DIR" --output "$OUTPUT_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Leaderboard updated successfully!"
    echo "=========================================="
    echo ""
    echo "View with:"
    echo "  cat $OUTPUT_FILE"
    echo "  less $OUTPUT_FILE"
    echo ""
    echo "Preview top 10:"
    echo ""

    # Show top 10 from the markdown table
    grep "^| [0-9]" "$OUTPUT_FILE" | head -11 | tail -10

    echo ""
else
    echo ""
    echo "Error: Failed to generate leaderboard"
    exit 1
fi
