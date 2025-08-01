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

# Replace ${ALGORITHM} in Cargo.toml.template and save to Cargo.toml
sed "s/\${ALGORITHM}/$ALGORITHM/g" Cargo.toml.template > Cargo.toml

# Replace ${ALGORITHM} in src/main.rs.template and save to src/main.rs
sed "s/\${ALGORITHM}/$ALGORITHM/g" src/main.rs.template > src/main.rs

# Check if src/$ALGORITHM.rs exists
if [ -f "src/$ALGORITHM.rs" ]; then
    echo "Using local algorithm in src/$ALGORITHM.rs"
    cargo run --release --features local -- "$TEST_INSTANCES_FOLDER"
else
    echo "Using algorithm from github:"
    echo "https://github.com/tig-foundation/tig-monorepo/blob/vehicle_routing/$ALGORITHM/tig-algorithms/src/vehicle_routing/$ALGORITHM/benchmarker_outbound.cu" 
    cargo run --release -- "$TEST_INSTANCES_FOLDER"
fi