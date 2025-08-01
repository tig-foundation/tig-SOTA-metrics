# TIG SOTA Metrics for Vector Search

This directory provides tools to evaluate TIG's vector search algorithms against academic test instances, specifically the SIFT dataset, and the Fashion-MNIST dataset. 

## Benchmark Sets

### SIFT

SIFT is a dataset of Scale-Invariant Feature Transform descriptors. Original source: [INRIA TEXMEX Corpus](ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz):
- Dimensions: 128
- Base vectors: 1,000,000
- Query vectors: 10,000

### Fashion-MNIST

The Fashion-MNIST is dataset of clothing item images encoded as vectors. Original source: [HuggingFace Dataset](https://huggingface.co/datasets/open-vdb/fashion-mnist-784-euclidean):
- Dimensions: 784
- Base vectors: 60,000
- Query vectors: 10,000

## Evaluating Algorithms

<a href="https://colab.research.google.com/github/tig-foundation/tig-SOTA-metrics/blob/vs-rework/vector_search_evaluator/quick_start.ipynb" target="_blank">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>
