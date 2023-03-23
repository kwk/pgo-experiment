Name: brp-llvm-compile-lto-elf-test-lib
Version: 1
Release: 1
Summary: Library package for testing brp-llvm-compile-lto-elf
License: MIT

BuildRequires: clang binutils
Source0: %{name}.c
Source1: %{name}.h

# FIXME: I'm not sure why this doesn't work
%undefine _package_note_file

%global toolchain clang

%description
%{summary}

%build

clang ${CFLAGS} -c %{SOURCE0} -o lib.o
ar cr %{name}.a lib.o
ranlib %{name}.a

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}

%{__install} -p -m 644 -t %{buildroot}%{_libdir} %{name}.a
%{__install} -p -m 644 -t %{buildroot}%{_includedir} %{SOURCE1}

%files
%{_libdir}/%{name}.a
%{_includedir}/%{name}.h
