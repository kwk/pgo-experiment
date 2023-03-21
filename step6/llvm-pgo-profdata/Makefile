# Prepare variables
TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version llvm-pgo-profdata.spec | sed 's/.* //')
PACKAGE = llvm-pgo-profdata-$(VERSION)
FILES = LICENSE \
		llvm-pgo-profdata.spec

.PHONY: source, tarball, rpm, srpm, clean

source:
	mkdir -p $(TMP)/SOURCES
	mkdir -p $(TMP)/$(PACKAGE)
	cp -a $(FILES) $(TMP)/$(PACKAGE)
tarball: source
	cd $(TMP) && tar vcfj ../$(PACKAGE).tar.bz2 $(PACKAGE)
rpm: tarball
	fedpkg --release f37 --name llvm-pgo-profdata local -- --noclean
srpm: tarball
	fedpkg --release f37 --name llvm-pgo-profdata srpm
clean:
	rm -rf $(TMP) $(PACKAGE)*