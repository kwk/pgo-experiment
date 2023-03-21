#!/bin/bash

set -ex

dnf -y build-dep test.spec
rpmbuild --define '_sourcedir .' --define '_builddir .' -bi test.spec
rpmbuild --without auto_set_build_flags --define '_sourcedir .' --define '_builddir .' -bi test.spec
