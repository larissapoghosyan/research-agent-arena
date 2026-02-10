#!/usr/bin/env python3
"""
Generate MLE-bench ELO Leaderboard

Creates a comprehensive leaderboard table showing ELO ratings across all splits.

Usage:
    python generate_leaderboard.py --results-dir results/ --output LEADERBOARD.md
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional


def load_elo_ratings(results_dir: Path, split: str) -> Dict[str, float]:
    """Load ELO ratings for a specific split."""
    elo_file = results_dir / f"elo_grand_{split}.csv"

    if not elo_file.exists():
        print(f"Warning: {elo_file} not found")
        return {}

    ratings = {}
    with open(elo_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            agent = row['agent_name']
            elo = float(row['elo_rating'])
            ratings[agent] = elo

    return ratings


def generate_leaderboard(results_dir: Path, output_file: Path):
    """Generate leaderboard markdown table."""

    # Define splits and their display names
    splits = {
        'low': 'Low (Lite)',
        'medium': 'Medium',
        'high': 'High',
        'systemcard': 'MLE-B-30',
        'split75': 'All',
    }

    # Load ELO ratings for each split
    print("Loading ELO ratings from splits...")
    split_ratings = {}
    for split_key, split_name in splits.items():
        ratings = load_elo_ratings(results_dir, split_key)
        split_ratings[split_key] = ratings
        print(f"  {split_name}: {len(ratings)} agents")

    # Get all unique agents
    all_agents = set()
    for ratings in split_ratings.values():
        all_agents.update(ratings.keys())

    print(f"\nTotal unique agents: {len(all_agents)}")

    # Build leaderboard data
    leaderboard = []
    for agent in all_agents:
        row = {'agent_name': agent}
        for split_key in splits.keys():
            elo = split_ratings[split_key].get(agent)
            row[split_key] = elo
        leaderboard.append(row)

    # Sort by 'all' (split75) descending, with fallback to other splits if not available
    def sort_key(row):
        # Try split75 first (All)
        if row['split75'] is not None:
            return row['split75']
        # Fallback to other splits in order of preference
        for split_key in ['systemcard', 'medium', 'high', 'low']:
            if row[split_key] is not None:
                return row[split_key]
        # If no splits have data, put at the end
        return -float('inf')

    leaderboard.sort(key=sort_key, reverse=True)

    # Generate markdown table
    print(f"\nGenerating leaderboard markdown...")

    with open(output_file, 'w') as f:
        # Header
        f.write("# MLE-bench ELO Leaderboard\n\n")
        f.write("ELO ratings across all MLE-bench splits. Sorted by overall performance (All split).\n\n")

        # Metadata
        f.write("## Methodology\n\n")
        f.write("- **Normalized Tournament**: Each agent pair plays exactly 1 game per task (aggregate win rate)\n")
        f.write("- **Higher-is-Better**: All scores normalized so higher is always better\n")
        f.write("- **Grand Tournament**: Overall ELO computed across all tasks in the split\n")
        f.write("- **Initial Rating**: 1500 (standard ELO)\n")
        f.write("- **K-Factor**: 32\n\n")

        # Split info
        f.write("## Splits\n\n")
        f.write("| Split | # Tasks | Description |\n")
        f.write("|-------|---------|-------------|\n")
        f.write("| **Low (Lite)** | 21 | Low complexity tasks (~158GB) |\n")
        f.write("| **Medium** | 38 | Medium complexity tasks |\n")
        f.write("| **High** | 14 | High complexity tasks |\n")
        f.write("| **MLE-B-30** | 29 | System card evaluation set |\n")
        f.write("| **All** | 74 | All 75 competitions |\n\n")

        # Rankings table
        f.write("## Rankings\n\n")
        f.write("| Rank | Agent | Low (Lite) | Medium | High | MLE-B-30 | All |\n")
        f.write("|------|-------|------------|--------|------|----------|-----|\n")

        for rank, row in enumerate(leaderboard, 1):
            agent = row['agent_name']

            # Format ELO ratings
            elos = []
            for split_key in ['low', 'medium', 'high', 'systemcard', 'split75']:
                elo = row[split_key]
                if elo is None:
                    elos.append("-")
                else:
                    elos.append(f"{elo:.1f}")

            # Add medal emoji for top 3 in "All" category
            if rank == 1:
                agent_display = f"🥇 {agent}"
            elif rank == 2:
                agent_display = f"🥈 {agent}"
            elif rank == 3:
                agent_display = f"🥉 {agent}"
            else:
                agent_display = agent

            f.write(f"| {rank} | {agent_display} | {elos[0]} | {elos[1]} | {elos[2]} | {elos[3]} | {elos[4]} |\n")

        # Statistics
        f.write("\n## Statistics\n\n")

        # Top 3 per split
        f.write("### Top 3 per Split\n\n")
        for split_key, split_name in splits.items():
            ratings = split_ratings[split_key]
            if not ratings:
                continue

            top_3 = sorted(ratings.items(), key=lambda x: x[1], reverse=True)[:3]
            f.write(f"**{split_name}:**\n")
            for i, (agent, elo) in enumerate(top_3, 1):
                medal = ["🥇", "🥈", "🥉"][i-1]
                f.write(f"{medal} {agent}: {elo:.2f}\n")
            f.write("\n")

        # Consistency analysis (agents in top 10 across all splits)
        f.write("### Most Consistent Agents\n\n")
        f.write("Agents appearing in top 10 across multiple splits:\n\n")

        consistency = defaultdict(list)
        for split_key, split_name in splits.items():
            ratings = split_ratings[split_key]
            if not ratings:
                continue

            top_10 = sorted(ratings.items(), key=lambda x: x[1], reverse=True)[:10]
            for agent, elo in top_10:
                consistency[agent].append(split_name)

        # Sort by number of appearances
        consistent_agents = sorted(consistency.items(), key=lambda x: len(x[1]), reverse=True)

        for agent, appears_in in consistent_agents[:15]:
            count = len(appears_in)
            splits_str = ", ".join(appears_in)
            f.write(f"- **{agent}**: {count}/5 splits ({splits_str})\n")

        # Footer
        f.write("\n---\n\n")
        f.write("*Generated using normalized ELO tournament system*\n")
        f.write("*Higher ELO = Better performance*\n")

    print(f"✓ Leaderboard saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MLE-bench ELO Leaderboard"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Directory containing ELO results",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="LEADERBOARD.md",
        help="Output markdown file",
    )

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_file = Path(args.output)

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print(f"Please run the tournaments first using ./run_all_splits.sh")
        return 1

    generate_leaderboard(results_dir, output_file)

    print("\n" + "="*70)
    print("Leaderboard generated successfully!")
    print("="*70)
    print(f"Output: {output_file}")
    print(f"\nView with: cat {output_file}")

    return 0


if __name__ == "__main__":
    exit(main())
