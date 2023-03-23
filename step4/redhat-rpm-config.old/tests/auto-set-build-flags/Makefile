.phony: all

all: hello-c hello-cpp

clean:
	rm -Rf *.o hello-c hello-cpp

hello-c: main-c.o hello-c.o

hello-cpp: main-cpp.o hello-cpp.o
	$(CXX) $(LDFLAGS) -o $@ $^
