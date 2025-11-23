# Copilot instructions

## Architecture overview
- `core/base_solver.py` defines `BaseSolver`; each solver in `core/sat_solver.py`, `core/subset_sum.py`, and `core/traveling_salesman.py` inherits from it and must implement `solve`, `get_complexity_class`, and `get_algorithm_name`.
- Domain data is generated in `generators/*.py`; every generator returns a `ProblemInstance` (see `core/data_models.py`) whose `.data` field holds the domain class (`SATInstance`, `SubsetSumInstance`, `TSPInstance`) and whose `metadata` records things like `generation_method` and known witnesses.

## Data flow & integration
- Tests (`tests/test_sat_solver.py`, `tests/test_subset_sum.py`, `tests/test_traveling_salesman.py`) instantiate a generator with a fixed `seed`, pull its `.data`, feed it to the solver, and then call the relevant `verify_*` utility function or compare outputs from brute-force vs. optimized solvers.
- Solver results are consumed via specific keys (`satisfiable`, `assignment`, `assignments_tried`, `solution_found`, `subsets_tried`, `tour_found`, `best_distance`, etc.), so any new solver/feature must expose the same metrics that unit tests (and future automation) expect.

## Benchmarks & stability
- Use `benchmarks/timeout_manager.py` whenever a new solver or batch run might hang; the module exposes `default_timeout_manager`, `execute_with_timeout`, and `safe_execute` that choose signal-based timeouts on Unix and thread-based on Windows.

## Testing & verification
- Run `python -m unittest discover tests` to exercise everything; the suite depends only on the standard library, so no `pip install` step is required and there is no `requirements.txt` or `pyproject.toml` in this repo.
- When you add a problem type or algorithm, mirror the pattern from existing tests: create deterministic instances via `generate_*` functions (often seeding with `42` or `123`) and assert both the success flag and any metadata-driven witness values (e.g., `problem.metadata['solution_subset']`).

## Documentation & frontend
- The `docs/` folder is a static site: open `docs/index.html` in a browser to preview. There is no Node/`npm run dev` script (the failed `npm run dev` attempt indicates this), so editing means updating `docs/index.html`, `docs/styles.css`, or `docs/script.remade.js` manually.
- `docs/script.remade.js` wires every interactive exhibit (SAT toggles, Subset Sum scale, reduction conveyor, scaling wall, approximation corner, FPT playground) and assumes the current DOM structure; keep any additions in sync with the markup in `docs/index.html`.

## Conventions to follow
- Be explicit about input types. Every solver currently raises a `TypeError` when the `problem_instance` is not the expected class (e.g., `core/sat_solver.py` checks `isinstance(problem_instance, SATInstance)`).
- Document modules with docstrings (see how `core/subset_sum.py` and `generators/subset_generator.py` describe each helper) so future maintainers understand the mathematical context.
- Preserve generator metadata fields like `generation_method`, `satisfying_assignment`, and `solution_subset`; downstream tests and data displays rely on them to describe the instance.
- When returning solutions, include both the data artifact and counters (assignments tried, subsets tried, tours evaluated) because the tests and any future benchmarks analyze those values directly.

## Common pitfalls
- Do not add build tooling; this repo is pure Python + static HTML/JS, so ignore tools such as `npm run dev` (it fails because no `package.json` or script exists).
- Seeds matter. Many tests rely on deterministic outputs (`seed=42`, `seed=123`, etc.), so keep `seed` parameters available on new generator helpers and pass them through when running automated checks.

If anything here is unclear or missing (architecture nuances, test workflows, or critical files), please let me know so I can clarify or expand the instructions.