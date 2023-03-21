#!/bin/bash -ex

# we diff most of the dependencies against our list in requires.txt
# generally, a new dependency is bad, for exceptional cases, we can add it to the list together with the change
# we intentionally grep out:
#  -srpm-macros and -rpm-macros
#  rpmlib(...)
#  conditional dependencies (they contain if)
# at the end, we strip the versions with cut
diff -u <(cat $(dirname $0)/requires.txt | sort | uniq) \
        <(rpm -q --requires redhat-rpm-config | grep -Ev -- '-s?rpm-macros(\s|$)|^rpmlib\(|\sif\s' | cut -d' ' -f1 | sort | uniq)
