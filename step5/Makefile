# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
fas_user ?= ${USER}
copr_project ?= profile-data-collection

.PHONY: all
all: create-copr-project redhat-rpm-config.copr_build_id myapp.copr_build_id

.PHONY: create-copr-project
create-copr-project:
	-copr create --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)
	copr modify --chroot fedora-37-x86_64 --unlisted-on-hp on --repo copr://$(fas_user)/llvm-pgo-instrumented $(copr_project)

redhat-rpm-config.patch: ../step4/redhat-rpm-config.patch
	-cp -fv ../step4/redhat-rpm-config.patch .

.PHONY: clean
clean:
	rm -fv *.copr_build_id

# We delete any redhat-rpm-config package first because we don't want to apply
# an older version of it when building a new. This can cause weird results.
.ONESHELL:
redhat-rpm-config.copr_build_id: redhat-rpm-config.patch
	[[ ! -d redhat-rpm-config ]] && fedpkg clone --anonymous -b f37 redhat-rpm-config
	cd redhat-rpm-config
	git reset --hard origin/f37
	git am ../redhat-rpm-config.patch
	fedpkg srpm
	-copr delete-package --name redhat-rpm-config $(copr_project)
	copr build --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) redhat-rpm-config-230-1.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../redhat-rpm-config.copr_build_id

# We copy the myapp directory from step1 to have an unmodified spec file
.ONESHELL:
myapp.copr_build_id: redhat-rpm-config.copr_build_id
	-rm -rf myapp
	cp -rfv ../step1/myapp .
	cd myapp
	make srpm
	copr build --after-build-id $(shell cat redhat-rpm-config.copr_build_id) --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project) myapp-1.0.0-1.fc37.src.rpm | tee build.log
	grep -Po 'Created builds: \K(\d+)' build.log > ../myapp.copr_build_id

# Just for fun build chromium
.PHONY: chromium
chromium:
	-copr add-package-scm --name chromium --clone-url https://src.fedoraproject.org/rpms/chromium.git --commit f37 $(fas_user)/$(copr_project)
	copr edit-package-scm --name chromium --clone-url https://src.fedoraproject.org/rpms/chromium.git --commit f37 $(fas_user)/$(copr_project)	
	copr build-package --name chromium --timeout 108000 --nowait --chroot fedora-37-x86_64 $(fas_user)/$(copr_project)