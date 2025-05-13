# TIG SOTA Metrics for the Vehicle Routing Problem with Time Windows

This crate provides tools to evaluate TIG's vehicle routing algorithms against standard academic benchmark instances for the Vehicle Routing Problem with Time Windows (VRPTW). It measures algorithmic performance compared to known optimal or best-known solutions (BKS).

To ensure accuracy and consistency with known optimal solutions, all coordinates, travel times, distances, and time windows are scaled by a factor of 10. This scaling maintains the one-decimal precision and allows precise integer arithmetic during comparisons. This follows convention taken by [CVRPLIB](http://vrp.galgos.inf.puc-rio.br/index.php/en/plotted-instances?data=C101).

## Resources

- Test instances and best-known values are sourced from: [CVRPLIB](http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/)

## Supported Instance Collections

Currently, this evaluation toolkit supports two widely recognized benchmark sets:
- **Solomon Instances**: Classic benchmark problems with varying customer distribution patterns and tightness of time windows.
- **Homberger–Gehring Instances**: Extended benchmarks with larger-scale problems ranging from 200 to 1000 customers.


## Getting Started

### Downloading Test Instances

Run the python scripts in the data/ folder to download test instances. For example: 

```bash
cd data
python3 download_solomon_instances.py
```

### Evaluating Algorithms

The evaluation script supports testing a vehicle routing algorithm against the benchmark data using the provided script.

```bash
# Usage
bash run.sh TEST_INSTANCES_FOLDER ALGORITHM

# Example
bash run.sh data/Solomon enhanced_solomon
```

## Output

The evaluation script outputs detailed metrics for each test instance:
- **instance**: Instance name.
- **distance**: Total distance of all routes (one-decimal precision).
- **NV**: Total number of vehicles used.
- **BKS NV**: Number of vehicles used in the BKS.
- **gap**: Percentage gap from the BKS, or
- **improvement**: Percentage improvement over the BKS (if applicable).

Example output:
```
instance: C103  distance:  1087.4       NV: 11  BKS NV: 10      gap: 31.6%      time:  446 µs
instance: C101  distance:   852.4       NV: 10  BKS NV: 10      gap:  3.0%      time:  387 µs
instance: RC201 distance:  1843.1       NV:  5  BKS NV:  9      gap: 46.1%      time:  906 µs
```
- **invalid solution:** The solver returned routes that violate one or more constraints.
- **no solution:** The solver did not find a solution within the provided time or fuel constraints.
