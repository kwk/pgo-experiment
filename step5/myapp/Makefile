# Prepare variables
TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version myapp.spec | sed 's/.* //')
PACKAGE = myapp-$(VERSION)
FILES = LICENSE myapp.cpp \
		myapp.spec CMakeLists.txt

.PHONY: source, tarball, rpm, srpm, clean

source:
	mkdir -p $(TMP)/SOURCES
	mkdir -p $(TMP)/$(PACKAGE)
	cp -a $(FILES) $(TMP)/$(PACKAGE)
tarball: source
	cd $(TMP) && tar vcfj ../$(PACKAGE).tar.bz2 $(PACKAGE)
rpm: tarball
	fedpkg --release f37 --name myapp local -- --noclean
srpm: tarball
	fedpkg --release f37 --name myapp srpm
clean:
	rm -rf $(TMP) $(PACKAGE)*