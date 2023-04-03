#!/bin/bash

set -x

# Build the app and always enter bash for further inspection
cd /home/tester/myapp
su -c "make rpm" tester || true

bash
