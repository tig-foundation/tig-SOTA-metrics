# TIG SOTA Metrics for Quadratic Knapsack Problem

This crate provides tools to evaluate TIG's knapsack algorithms against academic test instances for the Quadratic Knapsack Problem (QKP).

## Resources

- Test instances are sourced from: [benchmark-instances-for-qkp](https://github.com/phil85/benchmark-instances-for-qkp)
- Optimal values for comparison can be found at: [results-for-qkp-benchmark-instances](https://github.com/phil85/results-for-qkp-benchmark-instances)

## Supported Instance Collections

Currently, the crate supports evaluation against the Standard-QKP collection. Future work includes adding support for additional academic instance collections such as:
- Large-QKP
- QKPGroupII
- QKPGroupIII
- And more

## Getting Started

### Downloading Test Instances

To download the Standard-QKP dataset:

```bash
cd data
python3 download_standard_qkp.py
```

### Evaluating Algorithms

The evaluation script supports testing an algorithm against a collection of instances.

```bash
# Usage
bash run.sh TEST_INSTANCES_FOLDER ALGORITHM

# Example
bash run.sh data/Standard-QKP new_quadkp_improved
```

## Output

The evaluation outputs the knapsack value found by the algorithm for each test instance. Example output:

```
instance: "jeu_200_100_3.txt", knapsack_value: no solution
instance: "jeu_200_100_4.txt", knapsack_value: 100838
instance: "jeu_200_100_5.txt", knapsack_value: invalid solution
instance: "jeu_200_100_6.txt", knapsack_value: 40090
```