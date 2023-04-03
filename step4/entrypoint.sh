#!/bin/bash

set -x

# tag::build_patched_redhat_rpm_config[]
# Build and install our customized redhat-rpm-config
cd /root/redhat-rpm-config
fedpkg --release f37 local
sudo dnf install -y --disablerepo=* noarch/redhat-rpm-config-230-1.fc37.noarch.rpm
# end::build_patched_redhat_rpm_config[]

# tag::build_llvm_pgo_instrumentation_macros[]
# Build and install our customized redhat-rpm-config
cd /root/llvm-pgo-instrumentation-macros
fedpkg --release f37 local
sudo dnf install -y --disablerepo=* noarch/llvm-pgo-instrumentation-macros-0.0.1-1.fc37.noarch.rpm
# end::build_llvm_pgo_instrumentation_macros[]

# Build the app and always enter bash for further inspection
cd /home/tester/myapp
su -c "make rpm" tester || true

bash