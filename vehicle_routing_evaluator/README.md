# TIG SOTA Metrics for the Vehicle Routing Problem with Time Windows

This crate provides tools to evaluate TIG's vehicle routing algorithms against standard academic benchmark instances for the Vehicle Routing Problem with Time Windows (VRPTW). It measures algorithmic performance compared to known optimal or best-known solutions (BKS).

To ensure accuracy and consistency with known optimal solutions, all coordinates, travel times, distances, and time windows are scaled by a factor of 10. This scaling maintains the one-decimal precision and allows precise integer arithmetic during comparisons. This follows convention taken by [CVRPLIB](http://vrp.galgos.inf.puc-rio.br/index.php/en/plotted-instances?data=C101).

## Resources

- Test instances and best-known values are sourced from: [CVRPLIB](http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/)

## Supported Instance Collections

Currently, this evaluation toolkit supports one widely recognized benchmark set:
- **Homberger–Gehring Instances**: Extended benchmarks with larger-scale problems ranging from 200 to 1000 customers.


## Getting Started

<a href="https://colab.research.google.com/github/tig-foundation/tig-SOTA-metrics/blob/vr-rework/vehicle_routing_evaluator/quick_start.ipynb" target="_blank">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
