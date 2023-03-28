# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 3%{?dist}
Summary: A simple "Hello, World!" application.

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment
Source0: myapp-%{version}.tar.bz2

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	git
BuildRequires:	llvm

%description
A simple "Hello, World!" application.

%prep
%autosetup -S git

#-----------------------------------------------------------------------
# Generalize the naming and description of the profdata subpackage
#-----------------------------------------------------------------------
# tag::generalize_add_package[]
%package -n %{name}-%{toolchain}-raw-pgo-profdata

Summary: Indexed PGO profile data from %{name} package

%description -n %{name}-%{toolchain}-raw-pgo-profdata 
This package contains profiledata for %{toolchain} that was generated while
compiling %{name}. This can be used for doing Profile Guided Optimizations
(PGO) builds of %{toolchain}.

%files -n %{name}-%{toolchain}-raw-pgo-profdata
%{_libdir}/%{toolchain}-pgo-profdata/%{name}/%{name}.%{toolchain}.profdata
# end::generalize_add_package[]
#-----------------------------------------------------------------------

%build
#-----------------------------------------------------------------------
# We want the profile data to be written to specific files that will
# later land in the sub-package "myapp-clang-raw-pgo-profdata". See
# https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
# tag::llvm_profile_file[]
export TMPDIR="%{_builddir}/raw-pgo-profdata"
mkdir -pv $TMPDIR
export LLVM_PROFILE_FILE="%t/%{name}.%{toolchain}.%m.%p.profraw"
# end::llvm_profile_file[]
# tag::start_background_merge[]
./pgo-background-merge.sh \
  -d $TMPDIR \
  -f /tmp//%{name}.%{toolchain}.background.merge \
  -p /tmp/background-merge.pid &
# end::start_background_merge[]
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

#-----------------------------------------------------------------------
# tag::stop_background_merge[]
# Terminate online merge and wait for it to finish.
kill -s TERM $(cat /tmp/background-merge.pid)
while true; do [ ! -e /tmp/background-merge.pid ] && break; sleep 5; done;\
# end::stop_background_merge[]
#-----------------------------------------------------------------------

%install
%cmake_install
#-----------------------------------------------------------------------
# Generalized
#-----------------------------------------------------------------------
# tag::merge_profiles[]
# llvm-profdata itself is instrumented and wants to write profile data itself,
# hence we need to specify an LLVM_PROFILE_FILE. Otherwise it tries to write
# to a non existing location coming from when llvm-profdata was built.  
mkdir -pv %{buildroot}%{_libdir}/clang-pgo-profdata/myapp
export TMPDIR="/tmp"
export LLVM_PROFILE_FILE="%t/llvm-profdata.clang.%m.%p.profraw"
llvm-profdata merge \
  --compress-all-sections \
  --sparse \
  /tmp/%{name}.%{toolchain}.background.merge \
  $(find %{_builddir}/raw-pgo-profdata -type f) \
  -o %{buildroot}%{_libdir}/%{toolchain}-pgo-profdata/%{name}/%{name}.%{toolchain}.profdata
# end::merge_profiles[]

#-----------------------------------------------------------------------

%check
test "`%{buildroot}/%{_bindir}/myapp`" = "Hello, World!"

%files
%license LICENSE
%{_bindir}/myapp

%changelog
* Tue Mar 7 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-3
- Generalized the "myapp-clang-profdata" subpackage

* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-2
- Building step2
- Manually added "myapp-clang-profdata" subpackage

* Wed Mar 1 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Building step1
