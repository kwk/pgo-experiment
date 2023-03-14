# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
fas_user ?= ${USER}
copr_project ?= profile-data-collection

.PHONY: all
all: create-copr-project llvm-merged-profdata.copr_build_id

.PHONY: create-copr-project
create-copr-project:
	-copr create --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)
	copr modify --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)

.ONESHELL:
llvm-merged-profdata.copr_build_id:
	cd llvm-merged-profdata
	make srpm
	copr build --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) llvm-merged-profdata-1.0.0-1.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../llvm-merged-profdata.copr_build_id