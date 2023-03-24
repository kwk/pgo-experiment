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

.PHONY: update-submodules
update-submodules:
	git fetch --recurse-submodules
	git submodule foreach 'git reset --hard origin/pgo-experiment'

# This step might look counter intuitive at first but it has a reason.
# I make heavy use of a the asciidoc include directive to keep the document
# as close to the truth as possible.
# Sometimes I include complete files and sometimes just tagged regions or
# in the worst case, just lines by line number. Unfortunately github doesn't
# allow includes at all. That's why I convert my asciidoc document
# to docbook only to convert it back to asciidoc but this time with
# materialized include files.
#
# See:
#   * https://docs.asciidoctor.org/asciidoc/latest/directives/include/.
#   * https://docs.asciidoctor.org/asciidoc/latest/directives/include-tagged-regions/
#   * https://docs.asciidoctor.org/asciidoc/latest/directives/include-lines/
# 
# The index.html will be rendered on https://kwk.github.io/pgo-experiment/
# The README.adoc will be rendered as the README on https://github.com/kwk/pgo-experiment#readme
.PHONY: docs
docs:
	asciidoctor README.in.adoc --doctype article -o index.html
	asciidoctor README.in.adoc --doctype article --backend docbook -o README.xml
	pandoc --from=docbook --to=asciidoc -o README.adoc.tmp README.xml
	cat preamble.adoc > README.adoc
	cat README.adoc.tmp >> README.adoc
