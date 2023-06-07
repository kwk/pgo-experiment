# Disable PGO data generation
# tag::disable_pgo_data_generation[]
%global __llvm_pgo_subpackage %{nil}
# end::disable_pgo_data_generation[]
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
# tag::build_requires[]
BuildRequires: myapp-llvm-pgo-profdata
BuildRequires: retsnoop-llvm-pgo-profdata
# end::build_requires[]

%description
A merge of all PGO profile data files into a single file

%prep
%autosetup -S git

%build
cd %{_builddir}
# tag::merge_profiles[]
llvm-profdata merge \
      --compress-all-sections \
      --sparse \
      %{_libdir}/llvm-pgo-profdata/myapp/* \
      %{_libdir}/llvm-pgo-profdata/retsnoop/* \
      -output llvm-pgo.profdata
# end::merge_profiles[]

%install
mkdir -pv %{buildroot}%{_libdir}/llvm-pgo-profdata
cp -v %{_builddir}/llvm-pgo.profdata \
      %{buildroot}%{_libdir}/llvm-pgo-profdata/llvm-pgo.profdata

# tag::installed_profile_data[]
%files
%license LICENSE
%{_libdir}/llvm-pgo-profdata/llvm-pgo.profdata
# end::installed_profile_data[]

%changelog
* Mon May 08 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Merging raw profiles
