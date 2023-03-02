# Overview

In this experiment I try to show the steps I take to generate PGO profile data
from compiling unmodified RPM packages and feeding those profiles into a rebuild
of LLVM to get an LLVM that PGO optimized.

# Resources

* For building LLVM with PGO: https://llvm.org/docs/HowToBuildWithPGO.html#building-clang-with-pgo
* PGO in general: https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization

# Understanding what PGO can do

> PGO (Profile-Guided Optimization) allows your compiler to better optimize code
> for how it actually runs. Users report that applying this to Clang and LLVM
> can decrease overall compile time by 20%.
([Source](https://llvm.org/docs/HowToBuildWithPGO.html#introduction))

> Profile information enables better optimization. For example, knowing that a
> branch is taken very frequently helps the compiler make better decisions when
> ordering basic blocks. Knowing that a function `foo` is called more frequently
> than another function `bar` helps the inliner. Optimization levels `-O2` and
> above are recommended for use of profile guided optimization.
>
> [...] be careful to collect profiles by running your code with inputs that are
> representative of the typical behavior. Code that is not exercised in the
> profile will be optimized as if it is unimportant, and the compiler may make
> poor optimization choices for code that is disproportionately used while
> profiling.
([Source](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization))

As the [Fedora Linux](https://getfedora.org/) distribution we build a ton of
packages with LLVM. The aforementioned *inputs* are these packages themselves.
The programs to optimize are those under the LLVM umbrella (e.g. `clang`).

The question is: How can we tap in the RPM build pipeline using [Fedora
Copr](https://copr.fedorainfracloud.org/) and build RPM packages without
modifying their `*.spec` files manually?

I've created a 5 step experiment that shows how this can be achieved:

* [Step 0](step0/README.md)
* [Step 1](step1/README.md)
* [Step 2](step2/README.md)
* [Step 3](step3/README.md)
* [Step 4](step4/README.md)
* [Step 5](step5/README.md)