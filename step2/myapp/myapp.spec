# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 2%{?dist}
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

#-----------------------------------------------------------------------
# We want to generalize and automate this sub-package creation
#-----------------------------------------------------------------------
%package -n myapp-clang-profdata

Summary: clang profile data from myapp package

%description -n myapp-clang-profdata 
This package contains profiledata for clang that was generated while
compiling myapp. This can be used for doing Profile Guided Optimizations
(PGO) builds of clang.

%files -n myapp-clang-profdata
/usr/lib/profraw/myapp.clang.profraw
#-----------------------------------------------------------------------

%build
#-----------------------------------------------------------------------
# We want the profile data to be written to a specific file that will later land
# in the sub-package "myapp-clang-profdata".
# See https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
export LLVM_PROFILE_FILE="myapp.clang.profraw"
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
#-----------------------------------------------------------------------
# Must be generatlized and automated as well.
#-----------------------------------------------------------------------
mkdir -pv %{buildroot}/usr/lib/profraw
cp -v %{_builddir}/myapp-1.0.0/%{_vpath_builddir}/myapp.clang.profraw \
      %{buildroot}/usr/lib/profraw/myapp.clang.profraw
#-----------------------------------------------------------------------

%check
test "`%{buildroot}/%{_bindir}/myapp`" = "Hello, World!"

%files
%license LICENSE
%{_bindir}/myapp

%changelog
* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-2
- Building step2
- Manually added "myapp-clang-profdata" subpackage

* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Building step1
