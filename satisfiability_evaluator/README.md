# TIG SOTA Metrics for Boolean Satisfiability Challenge

This crate provides tools to evaluate TIG's SAT algorithms against academic benchmark instances of the 3-SAT problem, where each clause in the CNF formula has at most three literals.

## Resources

- SAT Competition instances are sourced from: [Global-Benchmark-Database](https://benchmark-database.de/)[^1]
- Uniform random 3-SAT instances are sourced from: [SATLIB - Benchmark Problems](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)


## Supported Benchmark Sets
- SAT Competition (2018–2024): 3-CNF instances from the main track, used in SAT Competitions between 2018 and 2024.

- Uniform Random 3-SAT: Randomly generated 3-SAT formulas from SATLIB Benchmark series.

- *Future Work:* Support for additional 3-SAT instances and CNF variants (e.g., mixed clause lengths).

## Getting Started

### Downloading Test Instances

To download the 3-SAT instances:

```bash
cd data
# Download main-track 3-SAT instances (2018-2024)
python3 download_2018-2024_3-SAT_instances.py

# Download SATLIB uniform random 3-SAT instances
python3 download_uf_3-SAT_instances.py
```

### Evaluating Algorithms

Use the provided script to evaluate your SAT algorithm against a benchmark set:

```bash
# Usage
bash run.sh TEST_INSTANCES_FOLDER ALGORITHM

# Example
bash run.sh data/2024-2018_3-SAT better_sat
```

## Output

The evaluation outputs whether the SAT solver found a satisfiable solution for each test instance. Example output:

```
instance: "072785fd927ff0fd180ce8b9cc00078f.cnf", result: sat, time:   14 ms
instance: "0a27eb7c16c1e69ff4d087d217ac89cb.cnf", result: no solution
instance: "0fa9521ff633b27be11525a7b0f7d8b6.cnf", result: no solution
instance: "12b4a08e412a3bffb513ca65639c7c69.cnf", result: sat, time:  387 ms
instance: "12d79233413fe38d99a604487d2c3515.cnf", result: sat, time:  106 ms
```
- **sat:** A satisfying assignment was found.
- **no solution:** The solver did not find a solution within the provided time or fuel constraints.
- **invalid solution:** The solver returned an assignment that violates one or more clauses.


[^1]: Markus Iser and Christoph Jabs. Global Benchmark Database. In 27th International Conference on Theory and Applications of Satisfiability Testing (SAT 2024). Leibniz International Proceedings in Informatics (LIPIcs), Volume 305, pp. 18:1-18:10, Schloss Dagstuhl – Leibniz-Zentrum für Informatik (2024) https://doi.org/10.4230/LIPIcs.SAT.2024.18