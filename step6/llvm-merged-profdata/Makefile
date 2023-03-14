# Prepare variables
TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version llvm-merged-profdata.spec | sed 's/.* //')
PACKAGE = llvm-merged-profdata-$(VERSION)
FILES = LICENSE \
		llvm-merged-profdata.spec

.PHONY: source, tarball, rpm, srpm, clean

source:
	mkdir -p $(TMP)/SOURCES
	mkdir -p $(TMP)/$(PACKAGE)
	cp -a $(FILES) $(TMP)/$(PACKAGE)
tarball: source
	cd $(TMP) && tar vcfj ../$(PACKAGE).tar.bz2 $(PACKAGE)
rpm: tarball
	fedpkg --release f37 --name llvm-merged-profdata local -- --noclean
srpm: tarball
	fedpkg --release f37 --name llvm-merged-profdata srpm
clean:
	rm -rf $(TMP) $(PACKAGE)*