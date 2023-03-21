#!/bin/bash

set -ex

for f in %{build_cflags} %{build_cxxflags} %{build_fflags} %{build_ldflags}; do
  rpm --eval "$f" | grep -vP '\t'
done
