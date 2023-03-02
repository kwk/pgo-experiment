# See https://docs.fedoraproject.org/en-US/packaging-guidelines/#_compiler_macros
%global toolchain clang

Name: myapp
Version: 1.0.0
Release: 1%{?dist}
Summary: A simple "Hello, World!" application.

License: Apache-2.0
URL: https://github.com/kwk/pgo-experiment
Source0: myapp.cpp
Source1: CMakeLists.txt

BuildRequires:	clang
BuildRequires:	cmake

%description
A simple "Hello, World!" application.

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

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
