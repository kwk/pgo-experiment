# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 3%{?dist}
Summary: A simple "Hello, World!" application.

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment
Source0: myapp.cpp
Source1: CMakeLists.txt

BuildRequires:	clang
BuildRequires:	cmake

%description
A simple "Hello, World!" application.

#-----------------------------------------------------------------------
# Generalize the naming and description of the profdata subpackage
#-----------------------------------------------------------------------
%package -n %{name}-%{toolchain}-profdata

Summary: %{toolchain} profile data from %{name} package

%description -n %{name}-%{toolchain}-profdata 
This package contains profiledata for %{toolchain} that was generated while
compiling %{name}. This can be used for doing Profile Guided Optimizations
(PGO) builds of %{toolchain}.

%files -n %{name}-%{toolchain}-profdata
/usr/lib/profraw/%{name}.%{toolchain}.profraw
#-----------------------------------------------------------------------

%build
#-----------------------------------------------------------------------
# We want the profile data to be written to a specific file that will later land
# in the sub-package "myapp-clang-profdata".
# See https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#running-the-instrumented-program
export LLVM_PROFILE_FILE="%{name}.%{toolchain}.profraw"
#-----------------------------------------------------------------------
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
#-----------------------------------------------------------------------
# Generalized
#-----------------------------------------------------------------------
mkdir -pv %{buildroot}/usr/lib/profraw
cp -v %{_builddir}/%{_vpath_builddir}/%{name}.%{toolchain}.profraw \
      %{buildroot}/usr/lib/profraw/%{name}.%{toolchain}.profraw
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
