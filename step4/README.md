# Step 4

In this step we use the `myapp` directory from `step1` that doesn't contain any
information about the sub-package at all.

And yet we're still gonna get our sub-package with profile data. We do this by
patching, compiling and installing another package that is always present on
Fedora: `redhat-rpm-config`. This package is the home of many useful macros like
but it also allows us to tap into the build process by:

1. exporting the `LLVM_PROFILE_FILE` environment variable
2. getting our sub-package included
3. tapping in the post-`%install` step

This time around, we're actually exporting the sub-package
`myapp-clang-profdata` because we're gonna need it to feed back into the
re-compilation of LLVM to produce a profile-optimized LLVM.