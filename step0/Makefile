# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
fas_user ?= ${USER}
copr_project ?= llvm-pgo-instrumented

.PHONY: all
all: create-copr-project llvm.copr_build_id clang.copr_build_id lld.copr_build_id

.PHONY: create-copr-project
create-copr-project:
	-copr create --chroot fedora-37-x86_64 --unlisted-on-hp on $(copr_project)

.ONESHELL:
llvm.copr_build_id:
	[[ ! -d llvm ]] && fedpkg clone --anonymous -b f37 llvm
	cd llvm
	git reset --hard 624d3135f736b8020cf0fdd9f02924142eb14aa4
	git am ../llvm.patch
	fedpkg srpm
	copr build --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) llvm-15.0.7-2.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../llvm.copr_build_id

.ONESHELL:
clang.copr_build_id: llvm.copr_build_id
	[[ ! -d clang ]] && fedpkg clone --anonymous -b f37 clang
	cd clang
	git reset --hard 44be8b6afe9a394ca1c02a3a0640c06992417d91
	git am ../clang.patch
	fedpkg srpm
	copr build --after-build-id $(shell cat llvm.copr_build_id) --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) clang-15.0.7-2.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../clang.copr_build_id

.ONESHELL:
lld.copr_build_id: llvm.copr_build_id
	[[ ! -d lld ]] && fedpkg clone --anonymous -b f37 lld
	cd lld
	git reset --hard 034235cdf6cafa8a7ca317206fdf10da7542db6d
	git am ../lld.patch
	fedpkg srpm
	copr build --after-build-id $(shell cat llvm.copr_build_id) --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) lld-15.0.7-2.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../lld.copr_build_id
