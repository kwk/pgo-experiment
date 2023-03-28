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
LLVM_PROFILE_FILE="%t/myapp.clang.%m.%p.profraw"
export LLVM_PROFILE_FILE
# end::llvm_profile_file[]
# tag::start_background_merge[]
./background-merge.sh $TMPDIR /tmp/myapp.clang.background.merge &
# end::start_background_merge[]
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

#-----------------------------------------------------------------------
# tag::wait_for_background_merge[]
# Terminate online merge and wait for it to finish.
MERGE_PID=$(cat /tmp/background-merge.pid)
kill -s TERM $MERGE_PID
wait $MERGE_PID || true
# end::wait_for_background_merge[]
#-----------------------------------------------------------------------

%install
%cmake_install

#-----------------------------------------------------------------------
# Must be generatlized and automated as well.
#-----------------------------------------------------------------------
# tag::merge_profiles[]
# llvm-profdata itself is instrumented and wants to write profile data itself,
# hence we need to specify an LLVM_PROFILE_FILE. Otherwise it tries to write
# to a non existing location coming from when llvm-profdata was built.
mkdir -pv %{buildroot}/usr/lib64/clang-pgo-profdata/myapp
LLVM_PROFILE_FILE="llvm-profdata.clang.%m.%p.profraw" \
llvm-profdata merge \
  --compress-all-sections \
  --sparse \
  /tmp/myapp.clang.background.merge \
  $(find %{_builddir}/raw-pgo-profdata -type f) \
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
