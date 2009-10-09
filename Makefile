include ./def.mk

SHELL=/bin/sh

SOURCE_DIRS=src lib data etc

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
	@\rm -f def.mk setup.env

install:
	@for i in $(SOURCE_DIRS) ; \
	do \
		echo "--------Installing from directory $$i-------"; \
		TDIR=`pwd`; \
		cd $$i; \
		$(MAKE) install; \
		cd $$TDIR; \
	done
	@$(HLHDF_INSTALL_BIN) -f -o -m620 -C def.mk $(MSGPP_INSTALL_PATH)/mkf/def.mk
	@\touch marker.tmp
	@$(HLHDF_INSTALL_BIN) -c -o -m644 -C marker.tmp $(MSGPP_INSTALL_PATH)/log/marker.tmp
	@\rm -f $(MSGPP_INSTALL_PATH)/log/marker.tmp
	@\rm -f marker.tmp
