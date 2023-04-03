%global debug_package %{nil}

Name:       llvm-pgo-instrumentation-macros
Version:    0.0.1
Release:    1%{?dist}
Summary:    Provides and overrides RPM macros to use a PGO instrumented LLVM toolchain
License:    BSD
URL:        https://pagure.io/llvm-snapshot-builder
Source001:  macros.llvm-pgo-instrumentation
Source002:  pgo-background-merge.sh

BuildArch:  noarch
Requires:   inotify-tools

%global rrcdir /usr/lib/rpm/redhat

%description
Provides and overrides RPM macros to use a PGO instrumented LLVM toolchain.

%prep
# Not strictly necessary but allows working on file names instead
# of source numbers in install section
%setup -c -T
cp -p %{sources} .

%build

%install
mkdir -p %{buildroot}%{rrcdir}
install -p -m0644 -D macros.llvm-pgo-instrumentation %{buildroot}%{_rpmmacrodir}/macros.llvm-pgo-instrumentation
install -p -m 755 -t %{buildroot}%{rrcdir} pgo-background-merge.sh

%files
%dir %{rrcdir}
%{_rpmmacrodir}/macros.llvm-pgo-instrumentation
%{rrcdir}/pgo-background-merge.sh

%attr(0755,-,-) %{rrcdir}/pgo-background-merge.sh

%changelog
* Mon Apr 03 2023 Konrad Kleine <kkleine@redhat.com> - 0.0.1-1
- Initial Release
