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
export TMPDIR="%{_builddir}/raw-pgo-profdata"
mkdir -pv $TMPDIR
export LLVM_PROFILE_FILE="%t/myapp.clang.%m.%p.profraw"
# end::llvm_profile_file[]
# tag::start_background_merge[]
SHUTDOWN_FILE=%{_builddir}/raw-pgo-profdata/shutdown.txt
PID_FILE=/tmp/background-merge.pid
./pgo-background-merge.sh \
  -d $TMPDIR \
  -f /tmp/myapp.clang.background.merge \
  -p $PID_FILE \
  -x $SHUTDOWN_FILE &
# end::start_background_merge[]
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

#-----------------------------------------------------------------------
# tag::stop_background_merge[]
# Signal stop and wait for the PID file to be deleted to gracefully
# exit the background job.
echo '' > $SHUTDOWN_FILE;
[ -e $PID_FILE ] && inotifywait -e delete_self $PID_FILE || true;
# end::stop_background_merge[]
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
export TMPDIR="/tmp"
export LLVM_PROFILE_FILE="%t/llvm-profdata.clang.%m.%p.profraw"
llvm-profdata merge \
  --compress-all-sections \
  --sparse \
  /tmp/myapp.clang.background.merge \
  $(find %{_builddir}/raw-pgo-profdata -type f -name '*.profraw') \
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
