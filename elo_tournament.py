#!/usr/bin/env python3
"""
ELO Tournament Script for MLE-bench

For each task (competition), runs a tournament between all agents where:
- Agent A vs Agent B fight for S_A * S_B rounds (cartesian product of seeds)
- Computes aggregate win rate and plays exactly ONE ELO game
- Computes ELO ratings for each agent on each task + grand tournament across all tasks

Usage:
    python elo_tournament.py --repo-url https://github.com/openai/mle-bench \\
                             --split low \\
                             --output-dir results/
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class AgentTaskResult:
    """Result for a specific agent on a specific task/competition."""

    agent_name: str
    task_name: str
    seed_id: str
    raw_score: float | None
    is_lower_better: bool
    higher_is_better_score: float | None
    submission_exists: bool
    valid_submission: bool

    @property
    def normalized_score(self) -> float | None:
        """Returns score normalized so higher is always better."""
        return self.higher_is_better_score


class ELORatingSystem:
    """ELO rating system for pairwise comparisons."""

    def __init__(self, k_factor: float = 32, initial_rating: float = 1500):
        self.k_factor = k_factor
        self.initial_rating = initial_rating

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A against player B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_ratings(
        self, rating_a: float, rating_b: float, actual_score_a: float
    ) -> Tuple[float, float]:
        """
        Update ratings after a match.
        actual_score_a: 1.0 if A won, 0.5 if draw, 0.0 if B won
        Returns: (new_rating_a, new_rating_b)
        """
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a

        new_rating_a = rating_a + self.k_factor * (actual_score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * ((1 - actual_score_a) - expected_b)

        return new_rating_a, new_rating_b


def ensure_repo_exists(repo_url: str, repo_dir: Path) -> Path:
    """Clone the repo if it doesn't exist."""
    if repo_dir.exists():
        print(f"Repository already exists at {repo_dir}")
        return repo_dir

    print(f"Cloning repository from {repo_url}...")
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Successfully cloned repository to {repo_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}")
        sys.exit(1)

    return repo_dir


def load_split(repo_dir: Path, split: str) -> List[str]:
    """Load competition IDs from a split file."""
    split_file = repo_dir / "experiments" / "splits" / f"{split}.txt"

    if not split_file.exists():
        print(f"Error: Split file not found: {split_file}")
        available = list((repo_dir / "experiments" / "splits").glob("*.txt"))
        print(f"Available splits: {[f.stem for f in available]}")
        sys.exit(1)

    with open(split_file, "r") as f:
        competitions = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(competitions)} competitions from split '{split}'")
    return competitions


def load_run_group_mapping(csv_path: Path) -> Dict[str, str]:
    """Load mapping from run_group to experiment_id (agent name)."""
    run_group_to_agent = {}

    if not csv_path.exists():
        print(f"Warning: {csv_path} not found, will use directory-based agent extraction")
        return {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_group = row['run_group'].strip()
            experiment_id = row['experiment_id'].strip()
            run_group_to_agent[run_group] = experiment_id

    return run_group_to_agent


def extract_agent_name_from_path(report_path: Path, run_group_mapping: Dict[str, str]) -> str | None:
    """Extract agent name from the run group directory name using CSV mapping."""
    # Check if this is in an "hourly" subdirectory
    if report_path.parent.name == "hourly":
        # Go up one more level to get the actual run group
        run_group = report_path.parent.parent.name
    else:
        run_group = report_path.parent.name

    # First try the CSV mapping
    if run_group in run_group_mapping:
        return run_group_mapping[run_group]

    # Fallback: Try to extract agent name from run group
    # Common patterns: "agent_group1", "2024-09-16T19-44-41-UTC_run-group_mlagentbench"
    if "_group" in run_group:
        agent_name = run_group.split("_group")[0]
    elif "_run-group_" in run_group:
        agent_name = run_group.split("_run-group_")[1]
    else:
        # For timestamp-based directories, return None to skip
        return None

    return agent_name


def load_grading_reports(
    runs_dir: Path, run_group_csv: Path, exclude_agents: List[str] = None, filter_competitions: List[str] = None
) -> List[AgentTaskResult]:
    """Load all grading reports from the runs directory."""
    results = []

    # Load run group to agent mapping
    run_group_mapping = load_run_group_mapping(run_group_csv)
    print(f"Loaded {len(run_group_mapping)} run group mappings")

    # Find all grading report JSON files
    report_files = list(runs_dir.glob("**/grading_report*.json"))

    print(f"Found {len(report_files)} grading report files")

    for i, report_path in enumerate(report_files):
        if i % 10 == 0:
            print(f"Loading grading reports... {i}/{len(report_files)}")
        try:
            with open(report_path, "r") as f:
                content = f.read()

                # Skip Git LFS pointer files
                if content.startswith("version https://git-lfs"):
                    print(f"Skipping LFS file: {report_path}")
                    continue

                grading_report = json.loads(content)

            agent_name = extract_agent_name_from_path(report_path, run_group_mapping)

            # Skip if we couldn't extract a valid agent name
            if agent_name is None:
                continue

            # Skip excluded agents
            if exclude_agents and agent_name in exclude_agents:
                continue

            # Use the report filename or parent directory as seed identifier
            seed_id = report_path.stem  # filename without extension

            # Extract competition reports
            competition_reports = grading_report.get("competition_reports", [])

            for comp_report in competition_reports:
                task_name = comp_report["competition_id"]

                # Filter by competitions if specified
                if filter_competitions and task_name not in filter_competitions:
                    continue

                raw_score = comp_report.get("score")
                is_lower_better = comp_report.get("is_lower_better", False)

                # Compute higher-is-better score
                if raw_score is not None:
                    if is_lower_better:
                        higher_is_better_score = -raw_score
                    else:
                        higher_is_better_score = raw_score
                else:
                    higher_is_better_score = None

                results.append(
                    AgentTaskResult(
                        agent_name=agent_name,
                        task_name=task_name,
                        seed_id=seed_id,
                        raw_score=raw_score,
                        is_lower_better=is_lower_better,
                        higher_is_better_score=higher_is_better_score,
                        submission_exists=comp_report.get("submission_exists", False),
                        valid_submission=comp_report.get("valid_submission", False),
                    )
                )

        except json.JSONDecodeError as e:
            print(f"Error parsing {report_path}: {e}")
        except Exception as e:
            print(f"Error processing {report_path}: {e}")

    return results


def run_tournament_for_task(
    task_name: str, results: List[AgentTaskResult]
) -> Dict[str, float]:
    """
    Run ELO tournament for a specific task.

    For each pair of agents A and B:
    - Compute all S_A * S_B pairwise seed matchups
    - Calculate the aggregate win rate for A across all matchups
    - Play exactly ONE ELO game with that win rate as the outcome

    This ensures each pair plays exactly one game, regardless of seed count.

    Returns: dict mapping agent_name to final ELO rating
    """
    elo_system = ELORatingSystem()

    # Group results by agent
    agent_results: Dict[str, List[AgentTaskResult]] = defaultdict(list)
    for result in results:
        if result.task_name == task_name:
            agent_results[result.agent_name].append(result)

    # Initialize ratings
    ratings = {agent: elo_system.initial_rating for agent in agent_results.keys()}

    # Get all unique agent pairs
    agents = sorted(agent_results.keys())

    # Run tournament: all agents vs all agents
    for i, agent_a in enumerate(agents):
        for agent_b in agents[i + 1 :]:  # Only play each pair once
            results_a = agent_results[agent_a]
            results_b = agent_results[agent_b]

            # Compute aggregate win rate across all S_A * S_B matchups
            wins_a = 0.0
            total_valid_matchups = 0

            for result_a in results_a:
                for result_b in results_b:
                    # Skip if either has no valid score
                    if (
                        result_a.normalized_score is None
                        or result_b.normalized_score is None
                    ):
                        continue

                    total_valid_matchups += 1

                    # Determine outcome (higher normalized score wins)
                    if result_a.normalized_score > result_b.normalized_score:
                        wins_a += 1.0  # A wins
                    elif result_a.normalized_score < result_b.normalized_score:
                        wins_a += 0.0  # B wins
                    else:
                        wins_a += 0.5  # Draw

            # Skip if no valid matchups
            if total_valid_matchups == 0:
                continue

            # Compute aggregate score for A (win rate)
            aggregate_score_a = wins_a / total_valid_matchups

            # Play exactly ONE ELO game with the aggregate score
            new_rating_a, new_rating_b = elo_system.update_ratings(
                ratings[agent_a], ratings[agent_b], aggregate_score_a
            )
            ratings[agent_a] = new_rating_a
            ratings[agent_b] = new_rating_b

    return ratings


def run_grand_tournament(all_results: List[AgentTaskResult]) -> Dict[str, float]:
    """
    Run a single grand tournament across ALL tasks.

    For each pair of agents:
    - Aggregate win rate across ALL tasks and ALL seeds
    - Play exactly ONE ELO game with that aggregate win rate

    Returns: dict mapping agent_name to final ELO rating
    """
    elo_system = ELORatingSystem()

    # Group results by agent
    agent_results: Dict[str, List[AgentTaskResult]] = defaultdict(list)
    for result in all_results:
        agent_results[result.agent_name].append(result)

    # Initialize ratings
    ratings = {agent: elo_system.initial_rating for agent in agent_results.keys()}

    # Get all unique agent pairs
    agents = sorted(agent_results.keys())

    num_tasks = len(set(r.task_name for r in all_results))
    print(f"\nRunning GRAND TOURNAMENT across all {num_tasks} tasks...")
    print(f"Agents competing: {len(agents)}")

    # Run tournament: all agents vs all agents (across ALL tasks)
    total_comparisons = 0
    for i, agent_a in enumerate(agents):
        for agent_b in agents[i + 1:]:  # Only play each pair once
            results_a = agent_results[agent_a]
            results_b = agent_results[agent_b]

            # Compute aggregate win rate across ALL tasks and ALL seeds
            wins_a = 0.0
            total_valid_matchups = 0

            for result_a in results_a:
                for result_b in results_b:
                    # Only compare if both are on the same task
                    if result_a.task_name != result_b.task_name:
                        continue

                    # Skip if either has no valid score
                    if (
                        result_a.normalized_score is None
                        or result_b.normalized_score is None
                    ):
                        continue

                    total_valid_matchups += 1

                    # Determine outcome (higher normalized score wins)
                    if result_a.normalized_score > result_b.normalized_score:
                        wins_a += 1.0  # A wins
                    elif result_a.normalized_score < result_b.normalized_score:
                        wins_a += 0.0  # B wins
                    else:
                        wins_a += 0.5  # Draw

            # Skip if no valid matchups
            if total_valid_matchups == 0:
                continue

            # Compute aggregate score for A (win rate)
            aggregate_score_a = wins_a / total_valid_matchups

            # Play exactly ONE ELO game with the aggregate score
            new_rating_a, new_rating_b = elo_system.update_ratings(
                ratings[agent_a], ratings[agent_b], aggregate_score_a
            )
            ratings[agent_a] = new_rating_a
            ratings[agent_b] = new_rating_b

            total_comparisons += total_valid_matchups

    print(f"Total pairwise comparisons: {total_comparisons:,}")
    return ratings


def run_all_tournaments(
    all_results: List[AgentTaskResult],
) -> Dict[str, Dict[str, float]]:
    """
    Run tournaments for all tasks.

    Returns: dict mapping task_name -> dict(agent_name -> elo_rating)
    """
    # Group results by task
    tasks = set(result.task_name for result in all_results)

    elo_ratings = {}

    tasks_list = sorted(tasks)
    for i, task in enumerate(tasks_list):
        print(f"Running tournament for task {i+1}/{len(tasks_list)}: {task}")
        task_results = [r for r in all_results if r.task_name == task]
        ratings = run_tournament_for_task(task, task_results)
        elo_ratings[task] = ratings

    return elo_ratings


def save_results_table(all_results: List[AgentTaskResult], output_path: Path) -> None:
    """Save results table to CSV."""
    with open(output_path, 'w', newline='') as f:
        fieldnames = [
            "agent_name", "task_name", "seed_id", "raw_score",
            "is_lower_better", "higher_is_better_score",
            "submission_exists", "valid_submission"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in all_results:
            writer.writerow({
                "agent_name": result.agent_name,
                "task_name": result.task_name,
                "seed_id": result.seed_id,
                "raw_score": result.raw_score,
                "is_lower_better": result.is_lower_better,
                "higher_is_better_score": result.higher_is_better_score,
                "submission_exists": result.submission_exists,
                "valid_submission": result.valid_submission,
            })


def save_elo_table(elo_ratings: Dict[str, Dict[str, float]], output_path: Path) -> None:
    """Save ELO ratings table to CSV."""
    with open(output_path, 'w', newline='') as f:
        fieldnames = ["task_name", "agent_name", "elo_rating"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for task_name, ratings in elo_ratings.items():
            for agent_name, elo_rating in ratings.items():
                writer.writerow({
                    "task_name": task_name,
                    "agent_name": agent_name,
                    "elo_rating": elo_rating,
                })


def main():
    parser = argparse.ArgumentParser(
        description="Run ELO tournament for MLE-bench agents"
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        default="https://github.com/openai/mle-bench.git",
        help="URL of the MLE-bench repository",
    )
    parser.add_argument(
        "--repo-dir",
        type=str,
        default="mle-bench",
        help="Directory for the MLE-bench repository",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="split75",
        help="Split to use (low, medium, high, systemcard, split75)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for results",
    )
    parser.add_argument(
        "--k-factor",
        type=float,
        default=32,
        help="ELO K-factor (default: 32)",
    )
    parser.add_argument(
        "--exclude-agents",
        type=str,
        nargs="*",
        default=[],
        help="List of agent names to exclude from analysis",
    )

    args = parser.parse_args()

    # Ensure repo exists
    repo_dir = Path(args.repo_dir)
    ensure_repo_exists(args.repo_url, repo_dir)

    # Load split
    competitions = load_split(repo_dir, args.split)

    # Set up paths
    runs_dir = repo_dir / "runs"
    run_group_csv = runs_dir / "run_group_experiments.csv"
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not runs_dir.exists():
        print(f"Error: runs directory not found: {runs_dir}")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"ELO Tournament Configuration")
    print(f"{'='*70}")
    print(f"Repository: {repo_dir}")
    print(f"Split: {args.split} ({len(competitions)} competitions)")
    print(f"Output directory: {output_dir}")
    print(f"Excluded agents: {args.exclude_agents or 'None'}")
    print(f"{'='*70}\n")

    print("Loading grading reports...")
    all_results = load_grading_reports(runs_dir, run_group_csv, args.exclude_agents, competitions)

    print(f"\nLoaded {len(all_results)} agent-task-seed results")
    print(f"Unique agents: {len(set(r.agent_name for r in all_results))}")
    print(f"Unique tasks: {len(set(r.task_name for r in all_results))}")

    # Create results table
    print("\nSaving results table...")
    results_csv = output_dir / f"agent_task_results_{args.split}.csv"
    save_results_table(all_results, results_csv)
    print(f"Saved results to {results_csv}")

    # Run per-task tournaments
    print("\nRunning ELO tournaments for each task...")
    elo_ratings = run_all_tournaments(all_results)

    # Save per-task ELO table
    print("\nSaving per-task ELO ratings table...")
    elo_csv = output_dir / f"elo_per_task_{args.split}.csv"
    save_elo_table(elo_ratings, elo_csv)
    print(f"Saved per-task ELO ratings to {elo_csv}")

    # Run grand tournament
    grand_ratings = run_grand_tournament(all_results)

    # Save grand tournament results
    print("\nSaving grand tournament ELO ratings...")
    grand_csv = output_dir / f"elo_grand_{args.split}.csv"
    with open(grand_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["agent_name", "elo_rating"])
        writer.writeheader()
        for agent_name, elo_rating in sorted(grand_ratings.items(), key=lambda x: x[1], reverse=True):
            writer.writerow({
                "agent_name": agent_name,
                "elo_rating": elo_rating,
            })
    print(f"Saved grand tournament ELO ratings to {grand_csv}")

    # Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    print("\n" + "=" * 70)
    print(f"GRAND TOURNAMENT - Overall ELO Rankings ({args.split})")
    print("=" * 70)
    sorted_grand = sorted(grand_ratings.items(), key=lambda x: x[1], reverse=True)
    for i, (agent, elo) in enumerate(sorted_grand, 1):
        print(f"{i:2d}. {agent:50s} ELO: {elo:.2f}")

    print("\n" + "=" * 70)
    print("PER-TASK AVERAGE - Top 10 Agents by Average ELO")
    print("=" * 70)

    # Compute average ELO per agent across all tasks
    agent_elos = defaultdict(list)
    for task_name, ratings in elo_ratings.items():
        for agent_name, elo in ratings.items():
            agent_elos[agent_name].append(elo)

    avg_elo_by_agent = {
        agent: sum(elos) / len(elos)
        for agent, elos in agent_elos.items()
    }

    sorted_agents = sorted(avg_elo_by_agent.items(), key=lambda x: x[1], reverse=True)
    for i, (agent, elo) in enumerate(sorted_agents[:10], 1):
        print(f"{i:2d}. {agent:50s} ELO: {elo:.2f}")

    # Compute ELO variance per task
    task_elo_variance = {}
    for task_name, ratings in elo_ratings.items():
        elos = list(ratings.values())
        if len(elos) > 1:
            mean_elo = sum(elos) / len(elos)
            variance = sum((e - mean_elo) ** 2 for e in elos) / len(elos)
            task_elo_variance[task_name] = variance ** 0.5  # std dev
        else:
            task_elo_variance[task_name] = 0.0

    print("\n" + "=" * 70)
    print("Top 10 Most Competitive Tasks (highest ELO variance):")
    print("=" * 70)
    sorted_tasks = sorted(task_elo_variance.items(), key=lambda x: x[1], reverse=True)
    for i, (task, std) in enumerate(sorted_tasks[:10], 1):
        print(f"{i:2d}. {task:50s} ELO Std: {std:.2f}")


if __name__ == "__main__":
    main()
