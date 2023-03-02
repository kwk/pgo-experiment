build-step0:
	cd step0 && $(MAKE) all

build-step4:
	rm -rf step4/myapp
	cp -rf step1/myapp step4/myapp
	podman build -t pgo-experiment-step4 ./step4
	-podman rm -f pgo-experiment-step4
	podman run -it --name pgo-experiment-step4 pgo-experiment-step4
	podman cp pgo-experiment-step4:/home/tester/myapp/x86_64/myapp-clang-profdata-1.0.0-1.fc37.x86_64.rpm step4/myapp-clang-profdata-1.0.0-1.fc37.x86_64.rpm

build-step%:
	$(eval step:=$(subst build-,,$@))
	podman build -t pgo-experiment-$(step) ./$(step)
	podman run -it --rm pgo-experiment-$(step)