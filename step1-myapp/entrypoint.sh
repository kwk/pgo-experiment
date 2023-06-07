#!/bin/bash

set -x

cd /root/myapp
make rpm || true

bash