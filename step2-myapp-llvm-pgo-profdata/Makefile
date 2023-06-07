.PHONY: all
all:
	rm -rf ./myapp
	cp -rf ../step1-myapp/myapp ./myapp
	podman build -t pgo-experiment-step2-myapp-llvm-pgo-profdata .
	podman run -it --rm pgo-experiment-step2-myapp-llvm-pgo-profdata