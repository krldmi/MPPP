include ../def.mk

SHELL=/bin/sh

SOURCE_DIRS=init.d

all:
	@for i in $(SOURCE_DIRS) ; \
	do \
		echo "--------Compiling directory $$i----------"; \
		TDIR=`pwd` ; \
		cd $$i; \
		$(MAKE); \
		cd $$TDIR; \
	done;

clean:
	@\rm -f *~ core
	@for i in $(SOURCE_DIRS) ; \
	do \
		echo "--------Cleaning directory $$i----------"; \
		TDIR=`pwd`; \
		cd $$i; \
		$(MAKE) clean; \
		cd $$TDIR; \
	done;

distclean:
	@\rm -f *~ core config.* a.out
	@\rm -f setup.env
	@for i in $(SOURCE_DIRS) ; \
	do \
		echo "-----Distcleaning directory $$i-------"; \
		TDIR=`pwd`; \
		cd $$i; \
		$(MAKE) distclean; \
		cd $$TDIR; \
	done
	@\rm -f def.mk

install:
	@for i in $(SOURCE_DIRS) ; \
	do \
		echo "--------Installing from directory $$i-------"; \
		TDIR=`pwd`; \
		cd $$i; \
		$(MAKE) install; \
		cd $$TDIR; \
	done
