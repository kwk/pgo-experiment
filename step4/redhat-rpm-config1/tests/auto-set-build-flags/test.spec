%bcond_without auto_set_build_flags

%if %{without auto_set_build_flags}
%undefine _auto_set_build_flags
%endif

Name: test
Version: 1
Release: 1
Summary: Test package for checking %%set_build_flag usage
License: MIT

BuildRequires: gcc gcc-c++ make
BuildRequires: annobin-annocheck

Source0: Makefile
Source1: main-c.c
Source2: hello-c.c
Source3: main-cpp.cpp
Source4: hello-cpp.cpp

%global build_and_check \
	make \
	%{!?with_auto_set_build_flags:!} annocheck hello-c hello-cpp \
	make clean

%description
Test package for checking %%set_build_flag usage

%prep

%build
%build_and_check

%check 
%build_and_check

%install
%build_and_check
