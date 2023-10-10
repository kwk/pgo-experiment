# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 1%{?dist}
Summary: A simple "Hello, World!" application.

License: Apache-2.0
URL: https://github.com/kwk/hello-world
Source0: myapp-%{version}.tar.bz2

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	git

%description
A simple "Hello, World!" application.

%prep
%autosetup -S git

%build
env
TMPDIR=%{_builddir}/raw-pgo-profdata2
export TMPDIR
mkdir -pv $TMPDIR
LLVM_PROFILE_FILE=%t/%{name}.llvm.%m.%p.profraw
export LLVM_PROFILE_FILE
env
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build
llvm-profdata merge \
    --compress-all-sections \
    --sparse \
    $(find /root/myapp/raw-pgo-profdata -type f -name '*.profraw') \
    -o %{name}.llvm.profdata --text

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
