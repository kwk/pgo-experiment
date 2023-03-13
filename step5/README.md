# Step 5

NOTE: You don't need to run this step manually. It has already been run and the
results are in the Copr project
[kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/).

In step 5 we essentially do the same thing as already done in step 4. But this
time we do it on Copr. Copr will become the storage for our profile data
sub-packages with all the rest of the regular packages.

After running this step, we're gonna have a project called:

[kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/)

In that project, there will be the patched `redhat-rpm-config` package and the
`myapp` package with the additional sub-package inside.

Any package that will be built after `redhat-rpm-config` in the
[kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/)
Copr project will automatically have a `<package>-clang-profdata` subpackage
that we can download in a later step to merge and feed it in the final,
optimized build of LLVM.
