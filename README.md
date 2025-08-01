# TIG SOTA Metrics

A repository of tools to evaluate The Innovation Game (TIG) algorithms against state-of-the-art (SOTA) test instances.

## Available Evaluators

* 3-SAT Boolean Satisfiability (`satisfiability_evaluator`)
  * [Evaluator Documentation](./satisfiability_evaluator/README.md)
  * [Challenge Description](https://tig.foundation/challenges/satisfiability)
  * [Challenge Code](https://github.com/tig-foundation/tig-monorepo/blob/main/tig-challenges/src/satisfiability.rs)  

* Vehicle Routing With Timing Windows Problem (`vehicle_routing_evaluator`)
  * [Evaluator Documentation](./vehicle_routing_evaluator/README.md)
  * [Challenge Description](https://tig.foundation/challenges/vehicle-routing)
  * [Challenge Code](https://github.com/tig-foundation/tig-monorepo/blob/main/tig-challenges/src/vehicle_routing.rs)

* Quadratic Knapsack Problem (`knapsack_evaluator`)
  * [Evaluator Documentation](./knapsack_evaluator/README.md)
  * [Challenge Description](https://tig.foundation/challenges/knapsack)
  * [Challenge Code](https://github.com/tig-foundation/tig-monorepo/blob/main/tig-challenges/src/knapsack.rs)

* Vector Search (`vector_search`)
  * [Evaluator Documentation](./vector_search_evaluator/README.md)
  * [Challenge Description](https://tig.foundation/challenges/vector_search)
  * [Challenge Code](https://github.com/tig-foundation/tig-monorepo/blob/main/tig-challenges/src/vector_search.rs)

## Coming Soon

We are actively developing additional evaluators for all of TIG's challenges:

- **Hypergraph Partitioning**