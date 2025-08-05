#!/bin/bash

# Check if at least two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 TEST_INSTANCES_FOLDER ALGORITHM"
    exit 1
fi

# Extract the test instances folder
TEST_INSTANCES_FOLDER=$1
ALGORITHM=$2

echo "Evaluating algorithm: $ALGORITHM"

# Check if src/$ALGORITHM.rs exists
if [ -f "src/$ALGORITHM.rs" ]; then
    sed "s#\${BRANCH}#blank_slate#g" Cargo.toml.template > Cargo.toml
    sed "s#\${ALGORITHM}#$ALGORITHM#g" src/main.rs.template > src/main.rs
    echo "Using local algorithm in src/$ALGORITHM.rs"
    ALGORITHM=$ALGORITHM cargo run --release --features local -- "$TEST_INSTANCES_FOLDER"
else
    sed "s#\${BRANCH}#vector_search/$ALGORITHM#g" Cargo.toml.template > Cargo.toml
    sed "s#\${ALGORITHM}#$ALGORITHM#g" src/main.rs.template > src/main.rs
    echo "Using algorithm from github:"
    echo "https://github.com/tig-foundation/tig-monorepo/blob/vector_search/$ALGORITHM/tig-algorithms/src/vector_search/$ALGORITHM/benchmarker_outbound.rs" 
    ALGORITHM=$ALGORITHM cargo run --release -- "$TEST_INSTANCES_FOLDER"
fi