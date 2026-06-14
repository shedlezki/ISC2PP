# ISC2PP - Intermittent Strategic Cooperation of Two Selfish Agents on Graphs

This repository contains code for simulating and evaluating **ISC2PP: Intermittent Strategic Cooperation of Two Selfish Agents on Graphs**. The project studies two selfish agents that each have their own start and goal, but may benefit from travelling together over parts of the graph. Cooperation changes the travel delay at selected vertices, creating a game in which each agent can either follow an independent route or join a cooperation path when it is individually rational.

The implementation has two main layers:

1. Algorithm code for computing intermittent-cooperation paths, equilibria, social optima, and bargaining solutions.
2. Experiment scripts and analysis utilities for generating CSV results, normalizing them, summarizing them, and preparing chart data.

## Repository Structure

```text
src/
  isc2pp.py                 Core intermittent-cooperation path algorithms
  bargaining_solutions.py  Python wrapper around MATLAB bargaining routines
  evaluation_functions.py  Conventions for correlating on a selected ECJS
  main.py                  Experiment runner and CSV writer
  MATLAB/                  Nash, Kalai-Smorodinsky, Egalitarian, Utilitarian solvers
experiement_scripts/       Experiment and analysis scripts
  run_experiments.sh       Run batches of experiments across parameter ranges
  merge_and_group_csv.py   Merge experiment results and create parameter-wise grouped CSVs
  normalizeResults.py      Normalize raw experiment CSVs and create summaries
  analyze_results.sh       Full post-processing pipeline to analyze the results
  clear_analysis_outputs.sh
                           Clear generated analysis outputs
results/                   Generated experiment outputs
archive/                   Local restore target for Zenodo scenario pickles
charts.numbers             Chart-ready workbook for final figures
```

## Code Documentation

### Model

The graph is represented with `networkx`. Edges have a travel time `tau=1`. Nodes have two relevant travel delays:

- `tau_1`: travel delay when an agent traverses independently.
- `tau_2`: travel delay when agents cooperate.

A cooperation vertex is any node where `tau_1 > tau_2`. In the code this set is usually named `V_C`.

Each experiment has two agents:

- Agent 1: `s_1 -> g_1`
- Agent 2: `s_2 -> g_2`

The central question is which joint paths are stable, efficient, or fair when agents may coordinate on shared cooperation segments.

### `src/isc2pp.py`

`isc2pp.py` implements the main algorithms corresponding to the intermittent-cooperation path-planning procedures described in the paper.

Important path primitives:

- `shortest_paths(G, s, tau)` computes Dijkstra shortest paths from one source using either independent delays (`tau_1`) or cooperation delays (`tau_2`).
- `all_pairs_shortest_paths(G, tau)` computes all-pairs shortest paths under the selected node-delay regime.
- `shortest_independent_path(G, v_s, v_g)` returns the shortest path without cooperation.
- `shortest_cooperated_path(G, v_s, v_g)` returns the shortest path assuming cooperation delays at all cooperation nodes, without waiting for the other agent.

The equilibrium/cooperation logic is built around cooperation start and departure nodes:

- `all_nodes_shortest_non_cooperative_partial_paths(...)` computes shortest prefixes from a start node to possible cooperation nodes while respecting the condition under which neither agent would prefer to deviate earlier.
- `all_nodes_shortest_stable_partial_paths(...)` computes stable cooperative partial paths ending cooperation at a selected cooperation departure node.
- `optimal_stable_js_to_cooperation_ending_node(...)` chooses the best stable joint strategy for a fixed cooperation departure node.
- `map_optimal_ecjs(...)` maps all non-dominated equilibrium cooperation joint strategies. This is the main equilibrium enumeration entry point used by `main.py`.
- `best_response(...)` computes an agent's best response to the other agent's path, which is used to test whether the pair of shortest independent paths forms a pure Nash equilibrium.
- `social_welfare_optimal_path(...)` computes the joint path minimizing the sum of both agents' travel times.

The implementation stores each path as a dictionary:

```python
{"path": [...nodes...], "length": travel_time}
```

When one agent reaches a cooperation point earlier than the other, the code inserts `WAIT_<time>` into that path. This keeps the path representation explicit and allows later evaluation/simulation to account for synchronization.

### `src/evaluation_functions.py`

This file defines conventions that the agents can use to correlate on a selected **equilibrium cooperation joint strategy (ECJS)** from the feasible potential set. Each convention maps an ECJS to a scalar ranking value. Examples include:

- `Min-Max`: minimize the worse individual travel time.
- `Min-Sum`: minimize total travel time.
- `Max-Min-Surplus`: maximize the minimum improvement over the independent baseline.
- `Max-Min-Improvement`: maximize the minimum normalized improvement.
- Nash-value variants based on the product of agent surpluses.

`main.py` applies these correlation conventions to the potential ECJS set and records both total welfare and the individual travel time from each selected ECJS.

### `src/bargaining_solutions.py`

`bargaining_solutions.py` bridges Python experiments with MATLAB bargaining solvers.

`MATLABBargainingSolutions` starts a MATLAB engine and calls:

```text
src/MATLAB/findSolutions.m
```

The MATLAB layer computes four bargaining solutions over the feasible equilibrium points:

- Nash bargaining solution [Nash 1950](#references)
- Kalai-Smorodinsky bargaining solution [Kalai and Smorodinsky 1975](#references)
- Egalitarian bargaining solution
- Utilitarian solution

The Python wrapper converts Python lists to `matlab.double`, calls MATLAB, then converts MATLAB arrays back into rounded Python lists. If there is only one feasible PNE, the wrapper returns that PNE for all bargaining solutions.

In `findSolutions.m`, points are converted into surplus space relative to the independent shortest-path baseline. The disagreement point is derived from the independent paths and the evaluated `SIP|SIP` outcome. Before returning the results the bargaining surpluses are converted back into path times.


## Experiments and Analysis

This section documents the batch experiments and the analysis pipeline used to generate the raw CSVs, normalized summaries, and chart-ready tables. The common workflow is:

- generate raw CSV results with the experiment runner (`main.py`)
- merge and group CSVs into analysis bins
- normalize raw results to per-experiment ratios and produce `summary` / `variance` / `standard_deviation` tables
- produce final figures from the summary (the provided `charts.numbers` file contains chart-ready tables)

Practical notes on artifacts and metadata:

- the experiment outputs live under `results/experiments/` and are grouped into four experiment folders: `density`, `magnitude`, `length`, and `seperation`
- within each experiment folder, `data/` contains raw `expN.csv` files and `descriptions/` contains matching `expN.txt` files recording the exact script parameters
- scenario pickles are loaded from `archive/` when replaying runs. In a fresh clone this folder is empty. Download the reproducibility archive from Zenodo to restore the referenced `archive/<eid>.pkl` files

### Reproducing the full pipeline

1. Run the batch experiment script(s) in `experiement_scripts/` to generate raw CSVs. The main example is `experiement_scripts/run_experiments.sh`, which runs the density, magnitude, length, and separation experiment groups in sequence and writes CSVs and descriptions into a `results` subtree. Example invocation (from repository root):

```bash
bash experiement_scripts/run_experiments.sh
```

The script calls `src/main.py` repeatedly. Each `src/main.py` invocation writes one (or more) CSV rows into a directory structure under `results/experiments/<sweep>/data/` and writes a matching description file into `results/experiments/<sweep>/descriptions/`.

### The main experiment runner: `src/main.py`

`src/main.py` is the core experiment driver used by the batch scripts. It generates graphs via the simulator's MAPF benchmark provider [Stern et al. 2019](#references), runs the ISC2PP analysis for each generated scenario, optionally stores pickled scenario archives, and writes CSV rows describing the scenario outcomes.

#### Command-line parameters

The script exposes the following command-line options (short and long forms):

- `-m`, `--map` (string, default: `empty-8-8`): map name passed to the simulator's MAPF benchmark provider.
- `-s`, `--scenario` (string): optional scenario name used by the MAPF benchmark provider.
- `-d`, `--density` (float, default: `0.5`): cooperation density parameter used by the graph generator.
- `-mt`, `--magnitude` (int, default: `10`): cooperation magnitude parameter controlling delay improvement at cooperation nodes.
- `-e`, `--extent` (int, default: `15`): extent parameter (used as a proxy for path-length distribution).
- `-se`, `--seperation` (int, default: `4`): separation parameter (used as a proxy for shortest-path divergence / SPD).
- `-i`, `--iterations` (int, default: `1`): how many scenario instances to generate per invocation; each iteration produces two CSV rows (one per agent perspective).
- `-o`, `--output` (string, default: `results`): base output path (the script writes to `../results/<output>.csv`).
- `-de`, `--description` (string): path/stem used to write a small `.txt` description file alongside outputs; if omitted the `--output` value is used.
- `-v`, `--visualization` (flag): if present, the final scenario (or loaded pickle) is shown in the GUI after running.
- `-l`, `--load` (string): load a single archived experiment pickle by `eid` (loads `../archive/<eid>.pkl`) instead of generating new scenarios.
- `-r`, `--rerun` (string): re-run experiments for each `eid` listed in an existing CSV; the script expects a CSV file base name (it appends `.csv` internally).
- `-si`, `--size` (string): optional map-size label passed to the simulator's MAPF benchmark provider.

#### Behavior notes

- When run normally (no `--load`), `src/main.py` calls `mapf_benchmark_provider.get_graph_with_timeout(...)`, using maps and scenarios from the MAPF benchmark format, to obtain a graph, node positions, and grid. It then invokes the ISC2PP analysis (`isc2pp.py`) to enumerate feasible equilibrium cooperation joint strategies, compute shortest independent/cooperated paths, best responses, social-welfare optima, and bargaining solutions via the MATLAB wrapper.
- For each iteration the script writes two CSV rows (one per agent perspective) into `../results/<output>.csv` and writes a small description file under `../results/<description>.txt` containing the `args` and runtime metadata.
- When `--load <eid>` is used, the script loads `../archive/<eid>.pkl`, extracts the saved `graph`, `grid`, `pos`, `paths`, and `args`, and optionally visualizes the scenario.
- When `--rerun <name>` is used, the script reads ` <name>.csv` from the results folder, extracts `EID` values and replays the archived pickles for those EIDs (so rerun requires that `archive/<eid>.pkl` files exist for the listed EIDs).
- The script saves per-scenario pickles under `../archive/` using the generated `eid` as the filename; these pickles contain the graph, solver outputs and the `args` object, allowing later inspection or replay.

#### Output format

- The CSV header includes: `eid`, `path_time_div`, `is_sp_pne`, `Potential`, `SIP1`, `SIP2`, `SCP1`, `SCP2`, `SIP1|SIP2`, `Individual Time In Optimal Social Welfare`, `Optimal Social Welfare`, evaluator-specific columns (one pair per evaluator: total and individual time), bargaining solution columns (total and individual time for each of `Nash`, `Kalai_Smorodinsky`, `Egalitarian`, `Utilitarian`), and `PoA`, `PoS`.
- Each raw CSV row contains the realized numeric times and structured `Potential` field (a Python-list representation). Downstream analysis scripts expect these column names and formats.

Change parameters by calling `src/main.py` directly or by modifying the helper scripts in `experiement_scripts/` which already encapsulate common parameter ranges and iteration counts.

#### Files to check after running experiment batches:

- `results/experiments/<sweep>/data/expN.csv` : raw per-iteration CSVs
- `results/experiments/<sweep>/descriptions/expN.txt` : the parameters used for that CSV
- `archive/` or `archive/<subpath>/` : pickled experiment objects that can be reloaded by `src/main.py`

Notes on `run_experiments.sh` behavior:

- It creates the standard `results/experiments/<sweep>/{data,descriptions}` folders and runs multiple parameter loops (density, magnitude, length, seperation).
- Each call to `src/main.py` is done from the `experiement_scripts` helper; modify the script to change ranges, steps, or the `--iterations` value used for each CSV.

### Merge and grouping (binning)

When you want grouped analyses (for example: group by SPD, or by rounded path-length bins) use `experiement_scripts/merge_and_group_csv.py`.

#### Purpose:

- merge many per-exp CSV files into a single `merged_data.csv` for convenience;
- split rows into grouped files under `by_<parameter>/` (either exact values or numeric ranges/buckets).

#### Typical usage examples (run from the appropriate `results/experiments/<sweep>` folder):

```bash
python3 experiement_scripts/merge_and_group_csv.py --path=. --parameter=path_time_div --group_range=10 --bucket-mode=one-based
python3 experiement_scripts/merge_and_group_csv.py --path=. --parameter=MAGNITUDE --no-bucket --parameter-source=description
```

#### Important options:

- `--parameter`: the column (or description field) to group by
- `--group_range`: numeric bucket size (omit with `--no-bucket` to write one file per exact value)
- `--parameter-source`: where to read the grouping parameter from; possible values are `column` or `description`
- `--add-sip-columns`: convenience option that adds `AVG SIP`, `MAX SIP`, `MIN SIP` derived from `SIP1` and `SIP2`

After running, grouped files are written to `by_<parameter>/` (or `by_<parameter>(<bucket>)`) under the same `--path`

### Normalization: `normalizeResults.py`

#### Purpose:

- convert raw CSV rows into per-experiment normalized metrics (ratios) so results are comparable across scales
- produce three analysis artifacts per grouping: `summary.csv`, `variance.csv`, and `standard_deviation.csv`
- write a per-experiment normalized CSV file per input CSV (named `<exp>_normalized.csv`)

#### Typical command (from a grouped folder's parent):

```bash
python3 experiement_scripts/normalizeResults.py \
  --path results/experiments/magnitude \
  --data-folder=by_magnitude \
  --parameter=magnitude \
  --comparison-source=filename \
  --label=non-filtered
```

#### Key behavior:

- when `--comparison-source=description` the script parses the numeric parameter from `descriptions/expN.txt` files. When `filename` it uses the CSV filename stem as the comparison value
- it writes normalized per-experiment CSVs into `<path>/<label>/normalized<suffix>/` and writes `summary<suffix>.csv`, `variance<suffix>.csv`, and `standard_deviation<suffix>.csv` into `<path>/<label>/`;
- normalization converts individual-time columns by dividing by `SIP1` and social-welfare totals by the `Optimal Social Welfare` so that summary numbers are unitless ratios appropriate for plotting

#### Filtering:

- use `--filter-multiple-pne` to produce summaries that only include rows whose `Potential` field contains multiple feasible PNEs (this is often used to focus on scenarios with richer equilibrium sets)

### Full analysis driver: `experiement_scripts/analyze_results.sh`

#### Purpose:

- run the canonical sequence of merge, normalize, filter, and summarize steps for every sweep used in the paper
- generate `summary_*.csv` and `standard_deviation_*.csv` files that feed the plotting/figure generation step

#### What it does:

- for each sweep (density, magnitude, path length, SPD) it runs `merge_and_group_csv.py` with the appropriate parameter settings and then runs `normalizeResults.py` twice: once for the full (non-filtered) data and once with `--filter-multiple-pne` to produce the filtered summaries used in some plots
- outputs live under the same `results/experiments/<sweep>/` subtree in labeled folders (for example `results/experiments/density/non-filtered/summary.csv` and `results/experiments/density/filtered/summary.csv`)

#### How to run it:

```bash
bash experiement_scripts/analyze_results.sh --path results/experiments
```

The `--path` option is optional; if omitted, the script defaults to this repository's `results/experiments` folder.

This script is the reproducible analysis pipeline used to create the summary tables that are later turned into figures.

### Clearing generated analysis outputs: `experiement_scripts/clear_analysis_outputs.sh`

Use this script when you want to remove generated analysis files before re-running `analyze_results.sh`.

It clears the derived outputs under each experiment folder (`density`, `magnitude`, `length`, and `seperation`):

- `filtered*`
- `non-filtered*`
- `by_*`
- `merged_data.csv`

It does not remove the raw experiment CSVs in `data/`, the parameter records in `descriptions/`, or archived scenario pickles in `archive/`.

```bash
bash experiement_scripts/clear_analysis_outputs.sh --path results/experiments
```

The `--path` option is optional; if omitted, the script defaults to this repository's `results/experiments` folder.

### charts.numbers and final figure data

`charts.numbers` is a spreadsheets file kept in the repository that contains chart-ready tables (the summary rows and standard-deviation columns used to draw error bars). After `analyze_results.sh` finishes, the relevant summary and standard-deviation CSVs can be copied or exported into `charts.numbers` to re-generate the final figures used in the paper. In short:

- `summary*.csv` provides the point estimates for plotted series
- `standard_deviation*.csv` provides the uncertainty level
- `charts.numbers` collects those into named sheets for each figure

### Archive and pickled scenarios

During `src/main.py` execution each generated scenario (graph + solved equilibrium information + extra metadata) is saved as a pickle under `archive/` or `archive/<archive-subpath>/` when the `--archive-subpath` option is given. The archive lets you:

- reload a scenario with `src/main.py --load <eid>` for debugging or replaying the simulation
- re-run analysis on a fixed set of scenario pickles without regenerating graphs

The archived scenario pickles used for reproducibility are available on Zenodo:

```text
https://zenodo.org/records/20691446
```

The Zenodo record contains the packaged `archive/<eid>.pkl` files, a checksum, and a small README explaining how to restore the archive locally.

### Quick experiment checklist

1. Record the exact `run_experiments.sh` invocation and the `experiement_scripts/*` versions used.
2. Run `experiement_scripts/analyze_results.sh` to merge, group, normalize, and summarize the produced CSVs.
3. Use the generated `summary*.csv` and `standard_deviation*.csv` files as inputs for plotting or for copying into `charts.numbers`.
4. Download the reproducibility archive from Zenodo when you need to reload the referenced scenario pickles.

## Dependencies

Core Python dependencies include:

- Python 3
- `networkx`
- `matplotlib`
- MATLAB Engine for Python
- [`iscpp-simulator`](https://github.com/shedlezki/ISCPP-Simulator)

The bargaining solution pipeline requires MATLAB and the MATLAB Engine API to be available to Python.

## References

- Kalai, E., and Smorodinsky, M. (1975). "Other solutions to Nash's bargaining problem." *Econometrica*, 43(3), 513-518.
- Nash, J. F. (1950). "The Bargaining Problem." *Econometrica*, 18(2), 155-162.
- Shedlezki, I., and Agmon, N. (2026). *Intermittent Cooperation Multiagent Path Planning Simulation*. MIT License.
- Stern, R., Sturtevant, N. R., Felner, A., Koenig, S., Ma, H., Walker, T. T., Li, J., Atzmon, D., Cohen, L., Kumar, T. K. S., Boyarski, E., and Bartak, R. (2019). "Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks." *Proceedings of the International Symposium on Combinatorial Search*, 10(1), 151-158.
