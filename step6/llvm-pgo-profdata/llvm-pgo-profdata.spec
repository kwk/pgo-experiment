# Disable PGO data generation
%global _toolchain_profile_subpackages %{nil}
# Disable debuginfo packages because we don't have any ;)
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Debuginfo/#_useless_or_incomplete_debuginfo_packages_due_to_other_reasons
%global debug_package %{nil}

%global toolchain clang

Name: llvm-pgo-profdata
Version: 1.0.0
Release: 1%{?dist}
Summary: Indexed Profile Optimized Data (PGO) file 

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment
Source0: %{name}-%{version}.tar.bz2

# For llvm-profdata
BuildRequires: llvm
BuildRequires: git

# List all *-clang-raw-pgo-profdata packages here
BuildRequires: myapp-clang-pgo-profdata
BuildRequires: retsnoop-clang-pgo-profdata

%description
A merge of all PGO profile data files into a single file

%prep
%autosetup -S git

%build
# TODO(kwk): This is a place to tweak 
cd %{_builddir}
llvm-profdata merge \
      %{_libdir}/%{toolchain}-pgo-profdata/myapp/* \
      %{_libdir}/%{toolchain}-pgo-profdata/retsnoop/* \
      -output llvm-pgo.profdata

%install
mkdir -pv %{buildroot}%{_libdir}/%{toolchain}-pgo-profdata
cp -v %{_builddir}/llvm-pgo.profdata \
      %{buildroot}%{_libdir}/%{toolchain}-pgo-profdata/llvm-pgo.profdata

%files
%license LICENSE
%{_libdir}/%{toolchain}-pgo-profdata/llvm-pgo.profdata

%changelog
* Tue Mar 14 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Merging raw profiles