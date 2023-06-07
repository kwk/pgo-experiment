#!/usr/bin/bash

set -x

# Source the python environment with required packages
source ~/mysandbox/bin/activate

function configure_build_run {
    # Configure the test suite
    cmake \
        -DCMAKE_GENERATOR=Ninja \
        -DCMAKE_C_COMPILER=/usr/bin/clang \
        -DCMAKE_CXX_COMPILER=/usr/bin/clang++ \
        -C~/test-suite/cmake/caches/O3.cmake \
        ~/test-suite

    # Build the test-suite
    ninja -j30

    # Run the tests with lit:
    lit -j1 -v -o results.json . || true
}

# Install and enable the repository that provides the PGO LLVM Toolchain
# See https://llvm.org/docs/HowToBuildWithPGO.html#building-clang-with-pgo
dnf copr enable -y kkleine/llvm-pgo-optimized
dnf install -y \
    clang-16.0.2-2.fc39 \
    clang-libs-16.0.2-2.fc39 \
    clang-resource-filesystem-16.0.2-2.fc39 \
    llvm-16.0.2-2.fc39 \
    llvm-libs-16.0.2-2.fc39

mkdir -pv ~/pgo
cd ~/pgo

configure_build_run

# Build with regular clang
dnf copr disable -y kkleine/llvm-pgo-optimized
dnf upgrade -y clang clang-libs clang-resource-filesystem llvm llvm-libs
mkdir -pv ~/rawhide
cd ~/rawhide

configure_build_run

/root/test-suite/utils/compare.py \
    --metric exec_time \
    --metric compile_time \
    --metric link_time \
    --lhs-name 16.0.3 \
    --rhs-name 16.0.2-pgo \
    ~/rawhide/results.json vs ~/pgo/results.json > ~/results-1.txt || true

bash
