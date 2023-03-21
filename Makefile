build-step0:
	$(MAKE) -C step0 all

# tag::build_step_4[]
build-step4:
	rm -rf step4/myapp
	cp -rf step1/myapp step4/myapp
	podman build -t pgo-experiment-step4 ./step4
	-podman rm -f pgo-experiment-step4
	podman run -it --name pgo-experiment-step4 pgo-experiment-step4
	podman cp pgo-experiment-step4:/home/tester/myapp/x86_64/myapp-clang-profdata-1.0.0-1.fc37.x86_64.rpm step4/myapp-clang-profdata-1.0.0-1.fc37.x86_64.rpm
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
	# sudo dnf install asciidoctor
	# gem install pygments.rb
	asciidoctor --safe README.in.adoc --doctype article -o index.html