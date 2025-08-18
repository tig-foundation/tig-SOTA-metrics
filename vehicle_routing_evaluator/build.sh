#!/bin/bash

# Check if at least two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 ALGORITHM"
    exit 1
fi

ALGORITHM=$1

echo "Building evaluator for algorithm: $ALGORITHM"

# Check if src/$ALGORITHM.rs exists
if [ -f "src/$ALGORITHM.rs" ]; then
    sed "s#\${BRANCH}#blank_slate#g" Cargo.toml.template > Cargo.toml
    sed "s#\${ALGORITHM}#$ALGORITHM#g" src/main.rs.template > src/main.rs
    echo "Using local algorithm in src/$ALGORITHM.rs"
    ALGORITHM=$ALGORITHM cargo build --release --features local
else
    sed "s#\${BRANCH}#vehicle_routing/$ALGORITHM#g" Cargo.toml.template > Cargo.toml
    sed "s#\${ALGORITHM}#$ALGORITHM#g" src/main.rs.template > src/main.rs
    echo "Using algorithm from github:"
    echo "https://github.com/tig-foundation/tig-monorepo/blob/vehicle_routing/$ALGORITHM/tig-algorithms/src/vehicle_routing/$ALGORITHM/benchmarker_outbound.rs" 
    ALGORITHM=$ALGORITHM cargo build --release
fi