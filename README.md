# Overview

In this experiment I try to show the steps I take to generate PGO profile data from compiling unmodified RPM packages and feeding those profiles into a PGO optimized rebuild of LLVM.

## Non-goal

It is NOT a goal to get a perfectly tweaked PGO optimization build of LLVM. Instead we want to just show a way how to setup a pipeline in [Copr](https://copr.fedorainfracloud.org/) for further tweaking and experimentation.

# Resources

* For building LLVM with PGO: https://llvm.org/docs/HowToBuildWithPGO.html#building-clang-with-pgo
* PGO in general: https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization

# Understanding what PGO can do

> PGO (Profile-Guided Optimization) allows your compiler to better optimize code for how it actually runs. Users report that applying this to Clang and LLVM can decrease overall compile time by 20%.
([Source](https://llvm.org/docs/HowToBuildWithPGO.html#introduction))

> Profile information enables better optimization. For example, knowing that a branch is taken very frequently helps the compiler make better decisions when ordering basic blocks. Knowing that a function `foo` is called more frequently than another function `bar` helps the inliner. Optimization levels `-O2` and above are recommended for use of profile guided optimization. [...] [Be] careful to collect profiles by running your code with inputs that are representative of the typical behavior. Code that is not exercised in the profile will be optimized as if it is unimportant, and the compiler may make poor optimization choices for code that is disproportionately used while profiling.
([Source](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization))

For the [Fedora Linux](https://getfedora.org/) distribution we build a ton of packages with LLVM. The aforementioned *inputs* are these packages themselves. The programs to optimize are those under the LLVM umbrella (e.g. `clang`).

The question is: How can we tap in the RPM build pipeline using [Fedora Copr](https://copr.fedorainfracloud.org/) and build RPM packages without modifying their `*.spec` files manually?

I've created a 7 step experiment that shows how this can be achieved. For educational purposes I've written many of the steps using `Containerfile`s. This allows for a good level of isolation when you want to build the steps on your own. To run any of the steps on your own, you can run `make build-stepX` where $X \in \lbrace 0,1,2,...,6 \rbrace$. But make sure you first read the description for each step below. Sometimes a step really only serves a documentation purpose.

NOTE: The `Containerfile`s run as `root` to allow packages to be installed and have a `tester` account for regular user interaction. Afterall the resulting images are not meant for anything but demonstration purposes and MUST NOT be used in production sites. 

## Step 0

NOTE: This step mainly exists for documentation purposes. If you *do* build this step on your own, make sure to walk through the files where there's a reference to [kkleine/llvm-pgo-instrumented](https://copr.fedorainfracloud.org/coprs/kkleine/llvm-pgo-instrumented/) and change it to your project. I don't see a need to consider this part of this excersise.

In this step we're going to create PGO instrumented LLVM packages and host them
for later consumption on a Copr project. 

If you want to build this yourself, you need to have a valid Kerberos ticket. Try running:

```
$ kinit <FAS_USER>@FEDORAPROJECT.ORG
```

But rest assured, you don't need to run this on your own. The
[kkleine/llvm-pgo-instrumented](https://copr.fedorainfracloud.org/coprs/kkleine/llvm-pgo-instrumented/)
project is ready for you to consume in the next steps.

In this step, we're essentially following the [official documentation](https://llvm.org/docs/HowToBuildWithPGO.html#building-clang-with-pgo) for how to build a PGO instumented clang.

The resulting `clang` will generate profile data upon execution and we're trying to collect, bundle, and merge it for optimizing a rebuild of `clang` later. 

## Step 1

In this step we set the foundation for our experiment.

We have a simply "Hello, World!" application that we build and package as an RPM file.

The other steps build on this simple setup by first adding lines to the RPM spec file that we later want to generalize and finally auto-generate to come back to an unmodified spec file.

Let's have a look at the [specfile](step1/myapp/myapp.spec) first:

**step1/myapp/myapp.spec**

```rpm
# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 1%{?dist}
Summary: A simple "Hello, World!" application.

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment
Source0: myapp-%{version}.tar.bz2

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	git

%description
A simple "Hello, World!" application.

%prep
%autosetup -S git

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%check
test "`%{buildroot}/%{_bindir}/myapp`" = "Hello, World!"

%files
%license LICENSE
%{_bindir}/myapp

%changelog
* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Building step1
```

This is the most simple specfile I could come up with for a "Hello, World!" application built with `clang`.

The [application code](step1/myapp/myapp.cpp) itself is similarly short and throughout this experiment we're never changing this:

**step1/myapp/myapp.cpp**

```cxx
#include <iostream>

int main(int argc, char *argv[]) {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```

In order to build the RPM we use standard tools like `fedpkg` from a [`step1/myapp/Makefile](step1/myapp/Makefile):

**step1/myapp/Makefile**

```Makefile
# Prepare variables
TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version myapp.spec | sed 's/.* //')
PACKAGE = myapp-$(VERSION)
FILES = LICENSE myapp.cpp \
		myapp.spec CMakeLists.txt

.PHONY: source, tarball, rpm, srpm, clean

source:
	mkdir -p $(TMP)/SOURCES
	mkdir -p $(TMP)/$(PACKAGE)
	cp -a $(FILES) $(TMP)/$(PACKAGE)
tarball: source
	cd $(TMP) && tar vcfj ../$(PACKAGE).tar.bz2 $(PACKAGE)
rpm: tarball
	fedpkg --release f37 --name myapp local -- --noclean
srpm: tarball
	fedpkg --release f37 --name myapp srpm
clean:
	rm -rf $(TMP) $(PACKAGE)*
```

Within a [`Containerfile`](step1/Containerfile) we're calling `make rpm` to build the `myapp-1.0.0-1.fc37.x86_64.rpm` RPM:

**step1/Containerfile**

```Dockerfile
FROM fedora:37

LABEL author="Konrad Kleine <kkleine@redhat.com>"
LABEL description="A basic specfile-to-RPM process demo"

# Install packages to build and package "myapp"
RUN dnf install -y cmake fedora-packager clang git

WORKDIR /root
RUN useradd --create-home tester
COPY entrypoint.sh /root/entrypoint.sh
COPY ./myapp /home/tester/myapp
RUN chown -Rfv  tester:tester /home/tester/myapp

USER root
ENTRYPOINT [ "/root/entrypoint.sh" ]
```

Once the build is done, we stay in the container and you have to manually exit it (e.g. using `<ctrl>+<d>`). We do this to allow you to look around in the build directories etc.:

**step1/entrypoint.sh**

```
#!/bin/bash

set -ex

# Build the app and always enter bash for further inspection
cd /home/tester/myapp
su -c "make rpm" tester || true

bash
```

## Step 2

In this step we manually add a `myapp-clang-profdata` sub-package which contains PGO profile data from LLVM. This data is generated by executing a PGO instrumented `clang` from the Copr repo [kkleine/llvm-pgo-instrumented](https://copr.fedorainfracloud.org/coprs/kkleine/llvm-pgo-instrumented/) which we've built in step 0.

The only changes from step1 to step2 are in the the `Containerfile` were we add the PGO instrumented LLVM.

**diff -u step1/Containerfile step2/Containerfile**

```diff
--- step1/Containerfile	2023-03-14 15:20:18.947387020 +0100
+++ step2/Containerfile	2023-03-14 15:19:35.843191441 +0100
@@ -1,10 +1,19 @@
 FROM fedora:37
 
 LABEL author="Konrad Kleine <kkleine@redhat.com>"
-LABEL description="A basic specfile-to-RPM process demo"
+LABEL description="Manually generate sub-package with PGO data"
+
+# Install the PGO instrumented (not PGO optimized!) clang and llvm (for the
+# llvm-profdata tool).
+# https://llvm.org/docs/HowToBuildWithPGO.html#building-clang-with-pgo
+RUN dnf install -y 'dnf-command(copr)'
+RUN dnf copr enable -y kkleine/llvm-pgo-instrumented
+RUN sudo dnf install -y \
+    llvm \
+    clang
 
 # Install packages to build and package "myapp"
-RUN dnf install -y cmake fedora-packager git clang
+RUN dnf install -y cmake fedora-packager git
 
 WORKDIR /root
 RUN useradd --create-home tester
```

Also, we add the sub-package manually in [step2/myapp/myapp.spec](step2/myapp/myapp.spec).

**diff -u step1/myapp/myapp.spec step2/myapp/myapp.spec**

```diff
--- step1/myapp/myapp.spec	2023-03-13 17:37:14.721181295 +0100
+++ step2/myapp/myapp.spec	2023-03-13 17:29:14.422542629 +0100
@@ -3,7 +3,7 @@
 
 Name: myapp
 Version: 1.0.0
-Release: 1%{?dist}
+Release: 2%{?dist}
 Summary: A simple "Hello, World!" application.
 
 License: Apache-2.0
@@ -20,12 +20,41 @@
 %prep
 %autosetup -S git
 
+#-----------------------------------------------------------------------
+# We want to generalize and automate this sub-package creation
+#-----------------------------------------------------------------------
+%package -n myapp-clang-profdata
+
+Summary: clang profile data from myapp package
+
+%description -n myapp-clang-profdata 
+This package contains profiledata for clang that was generated while
+compiling myapp. This can be used for doing Profile Guided Optimizations
+(PGO) builds of clang.
+
+%files -n myapp-clang-profdata
+/usr/lib/profraw/myapp.clang.profraw
+#-----------------------------------------------------------------------
+
 %build
+#-----------------------------------------------------------------------
+# We want the profile data to be written to a specific file that will later land
+# in the sub-package "myapp-clang-profdata".
+# See https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
+export LLVM_PROFILE_FILE="myapp.clang.profraw"
+#-----------------------------------------------------------------------
 %cmake -DCMAKE_BUILD_TYPE=Release
 %cmake_build
 
 %install
 %cmake_install
+#-----------------------------------------------------------------------
+# Must be generatlized and automated as well.
+#-----------------------------------------------------------------------
+mkdir -pv %{buildroot}/usr/lib/profraw
+cp -v %{_builddir}/myapp-1.0.0/%{_vpath_builddir}/myapp.clang.profraw \
+      %{buildroot}/usr/lib/profraw/myapp.clang.profraw
+#-----------------------------------------------------------------------
 
 %check
 test "`%{buildroot}/%{_bindir}/myapp`" = "Hello, World!"
@@ -35,5 +64,9 @@
 %{_bindir}/myapp
 
 %changelog
+* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-2
+- Building step2
+- Manually added "myapp-clang-profdata" sub-package
+
 * Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
 - Building step1
```

Notice that the added `myapp-clang-profdata` sub-package requires this file `/usr/lib/profraw/myapp.clang.profraw`. It is a file that we have to create manually by invoking the PGO instrumented `clang`. By specifying `export LLVM_PROFILE_FILE="myapp.clang.profraw"` we instruct `clang` to create a raw profile file in the current directory where `clang` is called under the name `myapp.clang.profraw`. We then need to copy it from the build directory to the buildroot to be picked up by the `%files` section of the `myapp-clang-profdata` sub-package. In our example it happens like this:

```
cp -v /home/tester/myapp/myapp-1.0.0/redhat-linux-build/myapp.clang.profraw /home/tester/rpmbuild/BUILDROOT/myapp-1.0.0-2.fc37.x86_64/usr/lib/profraw/myapp.clang.profraw
```

Now, you may ask why we make the changes to the spec file at all when I promised that we get profile data from unmodified packages. The honest answer is that I didn't know how to do it when I started out this experiment and I found the manual way much more easy to follow along compared to presenting the solution right away. We make transparent what needs to be generalized and automated.

In the next step we're generalizing the manual addition of the sub-package before we remove it entirely from the spec file again.

## Step 3

In this step we generalize the `myapp-clang-profdata` sub-package from step 2 to
`%{name}-%{toolchain}-profdata`.

The only changes from step2 to step3 is in the `myapp/myapp.spec` file.

**diff -u step2/myapp/myapp.spec step3/myapp/myapp.spec**

```diff
--- step2/myapp/myapp.spec	2023-03-13 17:29:14.422542629 +0100
+++ step3/myapp/myapp.spec	2023-03-13 17:35:52.589931021 +0100
@@ -3,7 +3,7 @@
 
 Name: myapp
 Version: 1.0.0
-Release: 2%{?dist}
+Release: 3%{?dist}
 Summary: A simple "Hello, World!" application.
 
 License: Apache-2.0
@@ -21,19 +21,19 @@
 %autosetup -S git
 
 #-----------------------------------------------------------------------
-# We want to generalize and automate this sub-package creation
+# Generalize the naming and description of the profdata sub-package
 #-----------------------------------------------------------------------
-%package -n myapp-clang-profdata
+%package -n %{name}-%{toolchain}-profdata
 
-Summary: clang profile data from myapp package
+Summary: %{toolchain} profile data from %{name} package
 
-%description -n myapp-clang-profdata 
-This package contains profiledata for clang that was generated while
-compiling myapp. This can be used for doing Profile Guided Optimizations
-(PGO) builds of clang.
+%description -n %{name}-%{toolchain}-profdata 
+This package contains profiledata for %{toolchain} that was generated while
+compiling %{name}. This can be used for doing Profile Guided Optimizations
+(PGO) builds of %{toolchain}.
 
-%files -n myapp-clang-profdata
-/usr/lib/profraw/myapp.clang.profraw
+%files -n %{name}-%{toolchain}-profdata
+/usr/lib/profraw/%{name}.%{toolchain}.profraw
 #-----------------------------------------------------------------------
 
 %build
@@ -41,7 +41,7 @@
 # We want the profile data to be written to a specific file that will later land
 # in the sub-package "myapp-clang-profdata".
 # See https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
-export LLVM_PROFILE_FILE="myapp.clang.profraw"
+export LLVM_PROFILE_FILE="%{name}.%{toolchain}.profraw"
 #-----------------------------------------------------------------------
 %cmake -DCMAKE_BUILD_TYPE=Release
 %cmake_build
@@ -49,11 +49,11 @@
 %install
 %cmake_install
 #-----------------------------------------------------------------------
-# Must be generatlized and automated as well.
+# Generalized
 #-----------------------------------------------------------------------
 mkdir -pv %{buildroot}/usr/lib/profraw
-cp -v %{_builddir}/myapp-1.0.0/%{_vpath_builddir}/myapp.clang.profraw \
-      %{buildroot}/usr/lib/profraw/myapp.clang.profraw
+cp -v %{_builddir}/%{name}-%{version}/%{_vpath_builddir}/%{name}.%{toolchain}.profraw \
+      %{buildroot}/usr/lib/profraw/%{name}.%{toolchain}.profraw
 #-----------------------------------------------------------------------
 
 %check
@@ -64,6 +64,9 @@
 %{_bindir}/myapp
 
 %changelog
+* Tue Mar 7 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-3
+- Generalized the "myapp-clang-profdata" sub-package
+
 * Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-2
 - Building step2
 - Manually added "myapp-clang-profdata" sub-package
```

You should see that we've replaced all occurrences of `myapp` with the RPM specfile macro `%{name}` and the word `clang` with the `%{toolchain}` macro. That is essentially all we have to do now.


## Step 4

In this step we use the `myapp` directory from `step1` that doesn't contain any information about the sub-package at all. And yet we're still gonna get our sub-package with profile data. We do this by patching, compiling and installing another package that is always present on Fedora: `redhat-rpm-config`. This package is the home of many useful build-flags and macros but it also allows us to tap into the build process by:

1. Exporting the `LLVM_PROFILE_FILE` environment variable at the right place.
2. Getting our sub-package included.
3. Tapping in the post-`%install` step to copy the raw profile file to the buildroot location.


In order to build the `redhat-rpm-config` we first download it using `fedpkg clone`, apply our [`step4/redhat-rpm-config.patch`](step4/redhat-rpm-config.patch) patch on top of it and then build the package using `fedpkg local`. Then we can simply imstall the resulting RPM using `dnf`.

**diff -u step3/entrypoint.sh step4/entrypoint.sh**

```diff
--- step3/entrypoint.sh	2023-03-09 11:51:51.855001153 +0100
+++ step4/entrypoint.sh	2023-03-14 16:00:30.061111901 +0100
@@ -2,6 +2,14 @@
 
 set -ex
 
+# Build and install our customized redhat-rpm-config
+cd /root
+fedpkg clone --anonymous -b f37 redhat-rpm-config
+cd redhat-rpm-config
+git am /root/redhat-rpm-config.patch
+fedpkg --release f37 local
+sudo dnf install -y --disablerepo=* noarch/redhat-rpm-config-230-1.fc37.noarch.rpm
+
 # Build the app and always enter bash for further inspection
 cd /home/tester/myapp
 su -c "make rpm" tester || true
```

Here're are the changes to the [`step4/Containerfile`](step4/Containerfile):

**diff -u step3/Containerfile step4/Containerfile**

```diff
--- step3/Containerfile	2023-03-14 16:01:48.964250798 +0100
+++ step4/Containerfile	2023-03-14 16:01:34.382274707 +0100
@@ -21,5 +21,14 @@
 COPY ./myapp /home/tester/myapp
 RUN chown -Rfv  tester:tester /home/tester/myapp
 
+# Install packages required to build redhat-rpm-config
+RUN dnf install -y perl-generators
+# Copy the patches we need for a modified redhat-rpm-config package that we
+# smuggle into the container.
+COPY redhat-rpm-config.patch /root
+# Make git happy
+RUN git config --global user.email "you@example.com"
+RUN git config --global user.name "Your Name"
+
 USER root
 ENTRYPOINT [ "/root/entrypoint.sh" ]
```

NOTICE: There's no `step4/myapp` directory. This is because we copy it from step1 in the top-level [`Makefile`](Makefile). This is supposed to emphasize the point that we don't modify the spec file. 

## Step 5

NOTE: You don't need to run this step manually. It has already been run and the results are in the Copr project
[kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/).

Up until this point all of our experiments look promising but how can we use Copr to build packages and produce ´<PACKAGE>-clang-profdata` packages automatically for us? 

Copr will become the storage for our profile data sub-packages with all the rest of the regular packages.r will become the storage for our profile data sub-packages with all the rest of the regular packages.

After running this step using `make build-step5`, we're gonna have a project called:

[kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/)

In that project, there will be the patched `redhat-rpm-config` package and the
`myapp` package with the additional sub-package inside:

![profile-data-collection](profile-data-collection.png?raw=true "profile-data-collection")

Any package that will be built after `redhat-rpm-config` in the [kkleine/profile-data-collection](https://copr.fedorainfracloud.org/coprs/kkleine/profile-data-collection/) Copr project will automatically have a `<package>-clang-profdata` sub-package that we can download in a later step to merge and feed it in the final, optimized build of LLVM.

## Step 6

TBD

## Open questions:

* What happens to packages that don't use `%global toolchain clang`?
