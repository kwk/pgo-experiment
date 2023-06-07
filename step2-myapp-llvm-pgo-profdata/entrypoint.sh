#!/bin/bash

# set -x

# Build the app and always enter bash for further inspection
cd /root/myapp
make rpm || true

bash