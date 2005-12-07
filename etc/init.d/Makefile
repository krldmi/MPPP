include ../../def.mk

INSTALL_FILES=nwcsaf_msg_pp_start.sh

all: ;

clean:
	@\rm -f core *~

distclean:
	@\rm -f core *~

install:
	@for i in $(INSTALL_FILES) ; \
	do \
		$(HLHDF_INSTALL_BIN) -f -o -m755 -C $$i $(MSGPP_INSTALL_PATH)/etc/init.d/$$i; \
	done
