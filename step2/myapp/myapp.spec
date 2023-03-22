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
# tag::manually_add_package[]
%package -n myapp-clang-pgo-profdata

Summary: Indexed PGO profile data from myapp package

%description -n myapp-clang-pgo-profdata 
This package contains profiledata for clang that was generated while
compiling myapp. This can be used for doing Profile Guided Optimizations
(PGO) builds of clang.

%files -n myapp-clang-pgo-profdata
/usr/lib64/clang-pgo-profdata/myapp/myapp.clang.profdata
# end::manually_add_package[]
#-----------------------------------------------------------------------

%build
# tag::llvm_profile_file[]
#-----------------------------------------------------------------------
# We want the profile data to be written to specific files that will
# later land in the sub-package "myapp-clang-raw-pgo-profdata". See
# https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
TMPDIR="%{_builddir}/raw-pgo-profdata"
export TMPDIR
mkdir -pv $TMPDIR
LLVM_PROFILE_FILE="%t/myapp.clang.%m.profraw"
export LLVM_PROFILE_FILE
# end::llvm_profile_file[]
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
#-----------------------------------------------------------------------
# Must be generatlized and automated as well.
#-----------------------------------------------------------------------
# tag::find_profiles[]
mkdir -pv %{buildroot}/usr/lib64/clang-pgo-profdata/myapp
find %{_builddir}/raw-pgo-profdata \
  -type f \
  -name "myapp.clang.*.profraw" \
  > %{_builddir}/pgo-profiles

# end::find_profiles[]

# tag::merge_profiles[]
llvm-profdata merge \
  --enable-name-compression \
  -sparse $(cat %{_builddir}/pgo-profiles) \
  -o %{buildroot}/usr/lib64/clang-pgo-profdata/myapp/myapp.clang.profdata
# end::merge_profiles[]
#-----------------------------------------------------------------------

%check
test "`%{buildroot}/%{_bindir}/myapp`" = "Hello, World!"

%files
%license LICENSE
%{_bindir}/myapp

%changelog
* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-2
- Building step2
- Manually added "myapp-clang-raw-pgo-profdata" subpackage

* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Building step1
