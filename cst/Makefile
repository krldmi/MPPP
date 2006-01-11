include ../def.mk

INSTALL_FILES=C0429_1999_S0700_0900.LAT \
	C0429_1999_S0700_0900.LON \
	C0429_1999_S0700_0900.SAT_AZI \
	C0429_1999_S0700_0900.SAT_ZEN \
	msg_coverage_CEuro.euro.hdf msg_coverage_CEuro.mesanX.hdf \
	msg_coverage_CEuro.nswe.hdf msg_coverage_CEuro.scan.hdf msg_coverage_CEuro.sswe.hdf \
	msg_coverage_CEuro.euro4.hdf


all: ;

clean:
	@\rm -f core *.pyc *~

distclean:
	@\rm -f core *.pyc *~

install:
	@for i in $(INSTALL_FILES) ; \
	do \
		$(HLHDF_INSTALL_BIN) -f -o -m644 -C $$i $(MSGPP_INSTALL_PATH)/cst/$$i; \
	done
