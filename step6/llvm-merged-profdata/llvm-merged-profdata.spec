# Disable PGO data generation
%global _toolchain_profile_subpackages 0

Name: llvm-merged-profdata
Version: 1.0.0
Release: 1%{?dist}
Summary: Indexed Profile Optimized Data (PGO) file 

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment

# For llvm-profdata
BuildRequires: llvm

# List all *-clang-profdata packages here
BuildRequires: myapp-clang-profdata

%description
A merge of all raw profile data files into an index profile data file 

%build
# TODO(kwk): This is a place to tweak with 
cd %{_builddir}
llvm-profdata merge /usr/lib/profraw/* -output llvm-merged.profdata

%install
mkdir -pv %{buildroot}/usr/lib/profdata
cp -v %{_builddir}/llvm-merged.profdata \
      %{buildroot}/usr/lib/profdata/llvm-merged.profdata

%files
%license LICENSE
/usr/lib/profdata/llvm-merged.profdata

%changelog
* Tue Mar 14 2023 Konrad Kleine <kkleine@redhat.com> - 1.0.0-1
- Merging raw profiles
