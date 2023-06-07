# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
fas_user ?= ${USER}
copr_project ?= profile-data-collection

.PHONY: all
all: create-copr-project myapp

# tag::create_copr_project[]
.PHONY: create-copr-project
create-copr-project:
	-copr create --chroot fedora-rawhide-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)
	copr modify --chroot fedora-rawhide-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)
	copr edit-chroot --packages llvm-pgo-instrumentation-macros $(fas_user)/profile-data-collection/fedora-rawhide-x86_64
# end::create_copr_project[]

# We copy the myapp directory from step1 to have an unmodified spec file
.PHONY: myapp
.ONESHELL:
myapp:
	-rm -rf ./myapp
	cp -rfv ../step1-myapp/myapp .
	cd myapp
	make srpm
	copr build --timeout 108000 --nowait --chroot fedora-rawhide-x86_64 $(fas_user)/$(copr_project) myapp-1.0.0-1.fc37.src.rpm

# tag::build_from_disgit[]
# Build an arbitrary package from dist-git
distgit-%:
	$(eval package:=$(subst distgit-,,$@))
	-copr add-package-distgit \
		--name $(package) \
		--distgit fedora \
		--commit rawhide \
		$(fas_user)/$(copr_project)
	copr edit-package-distgit \
		--name $(package) \
		--distgit fedora \
		--commit rawhide \
		$(fas_user)/$(copr_project)
	# copr edit-chroot --rpmbuild-with clang $(fas_user)/profile-data-collection/fedora-rawhide-x86_64
	copr build-package \
		--name $(package) \
		--timeout 1728000 \
		--nowait \
		--chroot fedora-rawhide-x86_64 \
		$(fas_user)/$(copr_project)
# end::build_from_disgit[]
