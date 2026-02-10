# MLE-bench ELO Tournament

ELO-based ranking system for MLE-bench agents with normalized tournaments.

## Features

- ✅ **Normalized tournaments**: Each agent pair plays exactly 1 game per task (aggregate win rate)
- ✅ **Higher-is-better normalization**: Handles both "lower is better" and "higher is better" metrics
- ✅ **Split support**: Run on any split (low, medium, high, systemcard, split75)
- ✅ **Auto-cloning**: Automatically clones MLE-bench repo if not present
- ✅ **Grand tournament**: Overall ELO rankings across all tasks
- ✅ **Per-task ELO**: Individual rankings for each competition

## Quick Start

### Run on a specific split

```bash
# Run on low (lite) split
python elo_tournament.py --split low --output-dir results/

# Run on medium split
python elo_tournament.py --split medium --output-dir results/

# Run on high split
python elo_tournament.py --split high --output-dir results/

# Run on systemcard (mle-b-30) split
python elo_tournament.py --split systemcard --output-dir results/

# Run on all 75 competitions
python elo_tournament.py --split split75 --output-dir results/
```

### Run on all splits

```bash
./run_all_splits.sh --output-dir results/
```

### Exclude specific agents

```bash
python elo_tournament.py --split low --exclude-agents extratime-gpt4o-aide --output-dir results/

# Or with the runner script
./run_all_splits.sh --output-dir results/ --exclude-agents "extratime-gpt4o-aide agent2"
```

### Use a different repo URL or directory

```bash
python elo_tournament.py --repo-url https://github.com/yourfork/mle-bench.git --repo-dir my-mle-bench --split low
```

## Output Files

For each split, three files are generated:

1. **`elo_grand_<split>.csv`** - Grand tournament rankings (overall ELO across all tasks)
2. **`elo_per_task_<split>.csv`** - Per-task ELO ratings for each agent
3. **`agent_task_results_<split>.csv`** - Raw normalized scores for all agent-task-seed combinations

## Available Splits

| Split | # Tasks | Description |
|-------|---------|-------------|
| `low` | 21 | Low complexity tasks (lite benchmark) |
| `medium` | 38 | Medium complexity tasks |
| `high` | 14 | High complexity tasks |
| `systemcard` | 29 | System card evaluation set (mle-b-30) |
| `split75` | 74 | All 75 competitions |

## Command Line Options

```
--repo-url URL          URL of the MLE-bench repository (default: https://github.com/openai/mle-bench.git)
--repo-dir DIR          Directory for the repository (default: mle-bench)
--split SPLIT           Split to use (default: split75)
--output-dir DIR        Output directory for results (default: results)
--k-factor FLOAT        ELO K-factor (default: 32)
--exclude-agents AGENTS Space-separated list of agents to exclude
```

## How It Works

### Normalized Tournament

For each pair of agents A and B on a task:
1. Compute all S_A × S_B seed matchups
2. Calculate aggregate win rate across all matchups
3. Play **exactly ONE** ELO game with that win rate as the outcome

This ensures fair comparison regardless of how many seeds each agent submitted.

### Grand Tournament

The grand tournament runs a single ELO competition across ALL tasks:
- For each agent pair, aggregate win rates across all tasks
- Play ONE ELO game with the overall aggregate win rate
- Produces a single global ranking

## Example Output

```
======================================================================
GRAND TOURNAMENT - Overall ELO Rankings (low)
======================================================================
 1. PiEvolve_24hrs                                     ELO: 1629.79
 2. PiEvolve_12hrs                                     ELO: 1598.80
 3. Famou-Agent-2.0                                    ELO: 1572.87
 4. deepseek-v3.2-speciale-ML-Master-2.0               ELO: 1545.19
 5. Leeroo                                             ELO: 1541.40
...
```

## Requirements

- Python 3.9+
- Git (for auto-cloning)
- No additional Python packages required (uses stdlib only)

## Notes

- The script will automatically clone the MLE-bench repo if it doesn't exist
- Git LFS files are automatically skipped (with warning)
- Agent names are extracted from `runs/run_group_experiments.csv` mapping
- Scores are normalized so higher is always better (negating "lower is better" metrics)
