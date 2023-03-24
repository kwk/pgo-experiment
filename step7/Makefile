# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
fas_user ?= ${USER}
copr_project ?= llvm-pgo-optimized

.PHONY: all
all: clean create-copr-project llvm.copr_build_id clang.copr_build_id lld.copr_build_id

.PHONY: clean
clean:
	-rm -f *.copr_build_id

# tag::create_copr_project[]
.PHONY: create-copr-project
create-copr-project:
	-copr create --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/profile-data-collection $(copr_project)
	copr  modify --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/profile-data-collection $(copr_project)
	copr edit-chroot --rpmbuild-with pgo_optimized_build $(copr_project)/fedora-37-x86_64
# end::create_copr_project[]

.ONESHELL:
llvm.copr_build_id:
	cd llvm
	fedpkg --release f37 srpm
	copr build --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) llvm-15.0.7-3.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../llvm.copr_build_id

.ONESHELL:
clang.copr_build_id: llvm.copr_build_id
	cd clang
	fedpkg --release f37 srpm
	copr build --after-build-id $(shell cat llvm.copr_build_id) --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) clang-15.0.7-3.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../clang.copr_build_id

.ONESHELL:
lld.copr_build_id: llvm.copr_build_id
	cd lld
	fedpkg --release f37 srpm
	copr build --after-build-id $(shell cat llvm.copr_build_id) --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) lld-15.0.7-3.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../lld.copr_build_id
