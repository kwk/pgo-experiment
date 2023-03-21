#!/bin/bash

set -e

spec=$TMT_TREE/redhat-rpm-config.spec
dnf -y build-dep $spec
rpmbuild --define "_sourcedir $TMT_TREE" -ba $spec
