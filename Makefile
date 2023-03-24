build-step0:
	$(MAKE) -C step0 all

# tag::build_step_4[]
build-step4:
	rm -rf step4/myapp
	cp -rf step1/myapp step4/myapp
	podman build -t pgo-experiment-step4 ./step4
	podman run -it --rm pgo-experiment-step4
# end::build_step_4[]

build-step5:
	$(MAKE) -C step5 all

build-step6:
	$(MAKE) -C step6 all

build-step7:
	$(MAKE) -C step7 all

build-step%:
	$(eval step:=$(subst build-,,$@))
	podman build -t pgo-experiment-$(step) ./$(step)
	podman run -it --rm pgo-experiment-$(step)

.PHONY: docs
docs:
	asciidoctor README.in.adoc --doctype article -o index.html
	asciidoctor README.in.adoc --doctype article --backend docbook -o README.xml
	pandoc --from=docbook --to=asciidoc -o README.adoc.tmp README.xml
	echo "include::preamble.adoc[]" > README.adoc
	cat README.adoc.tmp >> README.adoc

.PHONY: update-submodules
update-submodules:
	git fetch --recurse-submodules
	git submodule foreach 'git reset --hard origin/pgo-experiment' 