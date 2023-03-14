#!/bin/bash

set -ex

# Build and install our customized redhat-rpm-config
cd /root
fedpkg clone --anonymous -b f37 redhat-rpm-config
cd redhat-rpm-config
git am /root/redhat-rpm-config.patch
fedpkg --release f37 local
sudo dnf install -y --disablerepo=* noarch/redhat-rpm-config-230-1.fc37.noarch.rpm

# Build the app and always enter bash for further inspection
cd /home/tester/myapp
su -c "make rpm" tester || true

bash